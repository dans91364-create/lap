"""Service for intelligent alerts."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models import AlertaConfiguracao, AlertaDisparado, Licitacao


class AlertaService:
    """Service for intelligent alerts."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def criar_alerta(self, config_data: Dict[str, Any]) -> AlertaConfiguracao:
        """Create alert configuration."""
        config = AlertaConfiguracao(
            nome=config_data.get('nome'),
            ativo=config_data.get('ativo', True),
            tipo=config_data.get('tipo'),
            palavras_chave=config_data.get('palavras_chave'),
            municipios=config_data.get('municipios'),
            modalidades=config_data.get('modalidades'),
            valor_minimo=config_data.get('valor_minimo'),
            valor_maximo=config_data.get('valor_maximo'),
            canal_notificacao=config_data.get('canal_notificacao'),
            destinatario=config_data.get('destinatario')
        )
        
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        
        return config
    
    def verificar_alertas(self, licitacao: Licitacao) -> List[AlertaDisparado]:
        """Check if bidding triggers any configured alerts."""
        alertas_disparados = []
        
        # Get active alert configurations
        configs = self.db.query(AlertaConfiguracao).filter(
            AlertaConfiguracao.ativo == True
        ).all()
        
        for config in configs:
            deve_disparar = self._verificar_criterios(licitacao, config)
            
            if deve_disparar:
                # Check if already triggered
                ja_disparado = self.db.query(AlertaDisparado).filter(
                    and_(
                        AlertaDisparado.configuracao_id == config.id,
                        AlertaDisparado.licitacao_id == licitacao.id
                    )
                ).first()
                
                if not ja_disparado:
                    mensagem = self._gerar_mensagem(licitacao, config)
                    
                    alerta = AlertaDisparado(
                        configuracao_id=config.id,
                        licitacao_id=licitacao.id,
                        mensagem=mensagem,
                        enviado=False
                    )
                    
                    self.db.add(alerta)
                    alertas_disparados.append(alerta)
        
        self.db.commit()
        
        return alertas_disparados
    
    def _verificar_criterios(self, licitacao: Licitacao, config: AlertaConfiguracao) -> bool:
        """Check if bidding matches alert criteria."""
        # Check keywords
        if config.palavras_chave:
            objeto_lower = (licitacao.objeto_compra or '').lower()
            if not any(palavra.lower() in objeto_lower for palavra in config.palavras_chave):
                return False
        
        # Check municipalities
        if config.municipios:
            if licitacao.municipio_id not in config.municipios:
                return False
        
        # Check modalities
        if config.modalidades:
            if licitacao.modalidade_nome not in config.modalidades:
                return False
        
        # Check value range
        valor = licitacao.valor_total_estimado or 0
        if config.valor_minimo and valor < config.valor_minimo:
            return False
        if config.valor_maximo and valor > config.valor_maximo:
            return False
        
        return True
    
    def _gerar_mensagem(self, licitacao: Licitacao, config: AlertaConfiguracao) -> str:
        """Generate alert message."""
        mensagem = f"🔔 Alerta: {config.nome}\n\n"
        mensagem += f"Licitação: {licitacao.numero_compra}\n"
        mensagem += f"Objeto: {licitacao.objeto_compra}\n"
        mensagem += f"Modalidade: {licitacao.modalidade_nome}\n"
        
        if licitacao.valor_total_estimado:
            mensagem += f"Valor: R$ {licitacao.valor_total_estimado:,.2f}\n"
        
        if licitacao.data_abertura_proposta:
            mensagem += f"Abertura: {licitacao.data_abertura_proposta.strftime('%d/%m/%Y %H:%M')}\n"
        
        return mensagem
    
    def enviar_notificacao_email(self, alerta: AlertaDisparado) -> bool:
        """Send notification by email."""
        # TODO: Implement email sending
        try:
            # Implementation would use SMTP settings from config
            # For now, just mark as sent
            alerta.enviado = True
            alerta.enviado_em = datetime.now()
            self.db.commit()
            return True
        except Exception as e:
            alerta.erro = str(e)
            self.db.commit()
            return False
    
    def enviar_notificacao_telegram(self, alerta: AlertaDisparado) -> bool:
        """Send notification by Telegram."""
        # TODO: Implement Telegram sending
        try:
            # Implementation would use Telegram Bot API
            # For now, just mark as sent
            alerta.enviado = True
            alerta.enviado_em = datetime.now()
            self.db.commit()
            return True
        except Exception as e:
            alerta.erro = str(e)
            self.db.commit()
            return False
    
    def executar_verificacao_periodica(self):
        """Job to check alerts periodically."""
        # Get recent biddings not yet checked
        alertas_pendentes = self.db.query(AlertaDisparado).filter(
            AlertaDisparado.enviado == False
        ).all()
        
        for alerta in alertas_pendentes:
            config = alerta.configuracao
            
            if config.canal_notificacao == 'email':
                self.enviar_notificacao_email(alerta)
            elif config.canal_notificacao == 'telegram':
                self.enviar_notificacao_telegram(alerta)
