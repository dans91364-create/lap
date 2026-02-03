"""Webhook service for sending notifications to external URLs."""

import logging
from typing import Dict, Optional
import httpx

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for sending webhook notifications."""
    
    def __init__(self):
        """Initialize webhook service."""
        self.timeout = 30
    
    async def send_webhook(
        self,
        url: str,
        payload: Dict,
        headers: Optional[Dict] = None,
        method: str = "POST"
    ) -> bool:
        """
        Send webhook to external URL.
        
        Args:
            url: Webhook URL
            payload: Data to send
            headers: Optional HTTP headers
            method: HTTP method (POST, PUT, etc.)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not url:
            logger.warning("Webhook URL not provided, skipping")
            return False
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "POST":
                    response = await client.post(url, json=payload, headers=headers)
                elif method.upper() == "PUT":
                    response = await client.put(url, json=payload, headers=headers)
                else:
                    response = await client.request(method, url, json=payload, headers=headers)
                
                response.raise_for_status()
                logger.info(f"Webhook sent successfully to {url}")
                return True
                
        except httpx.HTTPError as e:
            logger.error(f"Error sending webhook to {url}: {e}")
            return False
    
    async def send_alerta_licitacao(self, url: str, licitacao: Dict) -> bool:
        """
        Send licitacao alert to webhook.
        
        Args:
            url: Webhook URL
            licitacao: Licitacao data
            
        Returns:
            True if sent successfully
        """
        payload = {
            "event": "nova_licitacao",
            "data": {
                "id": licitacao.get('id'),
                "numero": licitacao.get('numero_compra'),
                "objeto": licitacao.get('objeto'),
                "municipio": licitacao.get('municipio_nome'),
                "valor": licitacao.get('valor_total_estimado'),
                "data_abertura": licitacao.get('data_abertura_proposta'),
                "modalidade": licitacao.get('modalidade')
            }
        }
        
        return await self.send_webhook(url, payload)
    
    async def send_alerta_anomalia(self, url: str, anomalia: Dict) -> bool:
        """
        Send anomaly alert to webhook.
        
        Args:
            url: Webhook URL
            anomalia: Anomaly data
            
        Returns:
            True if sent successfully
        """
        payload = {
            "event": "anomalia_detectada",
            "data": {
                "id": anomalia.get('id'),
                "tipo": anomalia.get('tipo'),
                "severidade": anomalia.get('severidade'),
                "descricao": anomalia.get('descricao'),
                "licitacao_id": anomalia.get('licitacao_id'),
                "licitacao_numero": anomalia.get('licitacao_numero')
            }
        }
        
        return await self.send_webhook(url, payload)


# Global instance
webhook_service = WebhookService()
