"""Machine Learning service for price prediction and anomaly detection."""

import logging
from typing import Dict, List, Optional
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta
import pandas as pd

from src.database.connection import get_db

logger = logging.getLogger(__name__)


class MLService:
    """Service for machine learning operations on licitacao data."""
    
    def __init__(self):
        """Initialize ML service."""
        pass
    
    def prever_preco(self, descricao: str, meses: int = 3) -> Dict:
        """
        Predict future price using linear regression on historical data.
        
        Args:
            descricao: Item description
            meses: Number of months to predict
            
        Returns:
            Dict with predictions and statistics
        """
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Get historical prices for similar items
            cursor.execute("""
                SELECT 
                    i.data_resultado::date as data,
                    i.valor_unitario
                FROM itens i
                WHERE i.descricao ILIKE %s
                    AND i.valor_unitario > 0
                    AND i.data_resultado >= NOW() - INTERVAL '24 months'
                ORDER BY i.data_resultado
            """, (f'%{descricao}%',))
            
            rows = cursor.fetchall()
            cursor.close()
            
            if len(rows) < 5:
                return {
                    'success': False,
                    'message': 'Dados insuficientes para previsão (mínimo 5 registros)',
                    'count': len(rows)
                }
            
            # Prepare data
            dates = [row[0] for row in rows]
            prices = [float(row[1]) for row in rows]
            
            # Convert dates to numeric (days since first date)
            base_date = min(dates)
            X = np.array([(d - base_date).days for d in dates]).reshape(-1, 1)
            y = np.array(prices)
            
            # Train model
            model = LinearRegression()
            model.fit(X, y)
            
            # Make predictions
            last_date = max(dates)
            future_dates = []
            future_X = []
            
            for i in range(1, meses + 1):
                future_date = last_date + timedelta(days=30 * i)
                future_dates.append(future_date)
                future_X.append([(future_date - base_date).days])
            
            predictions = model.predict(np.array(future_X))
            
            # Calculate statistics
            mean_price = np.mean(prices)
            std_price = np.std(prices)
            
            return {
                'success': True,
                'historico': {
                    'media': float(mean_price),
                    'mediana': float(np.median(prices)),
                    'min': float(np.min(prices)),
                    'max': float(np.max(prices)),
                    'desvio_padrao': float(std_price),
                    'count': len(prices)
                },
                'previsoes': [
                    {
                        'data': future_dates[i].isoformat(),
                        'valor_previsto': float(predictions[i]),
                        'intervalo_confianca': {
                            'min': float(predictions[i] - 1.96 * std_price),
                            'max': float(predictions[i] + 1.96 * std_price)
                        }
                    }
                    for i in range(len(predictions))
                ],
                'tendencia': 'subindo' if model.coef_[0] > 0 else 'descendo' if model.coef_[0] < 0 else 'estável'
            }
            
        except Exception as e:
            logger.error(f"Error predicting price: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def detectar_outliers_ml(self, descricao: str, contamination: float = 0.1) -> List[Dict]:
        """
        Detect price outliers using Isolation Forest algorithm.
        
        Args:
            descricao: Item description
            contamination: Expected proportion of outliers
            
        Returns:
            List of detected outliers
        """
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Get item prices
            cursor.execute("""
                SELECT 
                    i.id,
                    i.descricao,
                    i.valor_unitario,
                    i.quantidade,
                    l.numero_compra,
                    m.nome as municipio,
                    i.data_resultado
                FROM itens i
                JOIN licitacoes l ON i.licitacao_id = l.id
                JOIN municipios m ON l.municipio_id = m.id
                WHERE i.descricao ILIKE %s
                    AND i.valor_unitario > 0
                    AND i.data_resultado >= NOW() - INTERVAL '12 months'
            """, (f'%{descricao}%',))
            
            rows = cursor.fetchall()
            cursor.close()
            
            if len(rows) < 10:
                return []
            
            # Prepare features
            prices = np.array([float(row[2]) for row in rows]).reshape(-1, 1)
            
            # Train Isolation Forest
            model = IsolationForest(contamination=contamination, random_state=42)
            predictions = model.fit_predict(prices)
            
            # Get outliers
            outliers = []
            for i, pred in enumerate(predictions):
                if pred == -1:  # Outlier
                    row = rows[i]
                    outliers.append({
                        'id': row[0],
                        'descricao': row[1],
                        'valor_unitario': float(row[2]),
                        'quantidade': row[3],
                        'licitacao_numero': row[4],
                        'municipio': row[5],
                        'data': row[6].isoformat() if row[6] else None
                    })
            
            return outliers
            
        except Exception as e:
            logger.error(f"Error detecting outliers: {e}")
            return []
    
    def classificar_risco_licitacao(self, licitacao_id: int) -> Dict:
        """
        Calculate risk score for a licitacao using multiple factors.
        
        Args:
            licitacao_id: Licitacao ID
            
        Returns:
            Dict with risk score and factors
        """
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Get licitacao data
            cursor.execute("""
                SELECT 
                    l.valor_total_estimado,
                    l.modalidade,
                    COUNT(DISTINCT r.fornecedor_id) as num_participantes,
                    COUNT(DISTINCT a.id) as num_anomalias
                FROM licitacoes l
                LEFT JOIN resultados r ON r.licitacao_id = l.id
                LEFT JOIN anomalias a ON a.licitacao_id = l.id
                WHERE l.id = %s
                GROUP BY l.id, l.valor_total_estimado, l.modalidade
            """, (licitacao_id,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                return {'success': False, 'message': 'Licitação não encontrada'}
            
            valor = float(row[0]) if row[0] else 0
            modalidade = row[1]
            num_participantes = row[2] or 0
            num_anomalias = row[3] or 0
            
            # Calculate risk factors
            risk_score = 0
            factors = []
            
            # Factor 1: High value (>1M = higher risk)
            if valor > 1000000:
                risk_score += 25
                factors.append({'fator': 'Valor Alto', 'peso': 25, 'descricao': 'Licitação acima de R$ 1 milhão'})
            
            # Factor 2: Low participation
            if num_participantes < 3:
                risk_score += 20
                factors.append({'fator': 'Baixa Participação', 'peso': 20, 'descricao': f'Apenas {num_participantes} participante(s)'})
            
            # Factor 3: Anomalies detected
            if num_anomalias > 0:
                peso = min(num_anomalias * 15, 40)
                risk_score += peso
                factors.append({'fator': 'Anomalias Detectadas', 'peso': peso, 'descricao': f'{num_anomalias} anomalia(s) encontrada(s)'})
            
            # Factor 4: Dispensa/Inexigibilidade (higher risk modalities)
            if modalidade in ['Dispensa de Licitação', 'Inexigibilidade']:
                risk_score += 15
                factors.append({'fator': 'Modalidade de Risco', 'peso': 15, 'descricao': f'Modalidade: {modalidade}'})
            
            # Normalize to 0-100
            risk_score = min(risk_score, 100)
            
            # Classify risk level
            if risk_score >= 70:
                nivel = 'alto'
            elif risk_score >= 40:
                nivel = 'médio'
            else:
                nivel = 'baixo'
            
            return {
                'success': True,
                'score': risk_score,
                'nivel': nivel,
                'fatores': factors
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk: {e}")
            return {
                'success': False,
                'message': str(e)
            }


# Global instance
ml_service = MLService()
