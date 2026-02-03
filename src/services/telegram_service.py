"""Telegram service for sending bot notifications."""

import logging
from typing import Dict, Optional
from telegram import Bot
from telegram.error import TelegramError

from config.settings import settings

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for sending Telegram notifications."""
    
    def __init__(self):
        """Initialize Telegram bot."""
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.bot = None
        
        if self.bot_token:
            try:
                self.bot = Bot(token=self.bot_token)
                logger.info("Telegram bot initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Telegram bot: {e}")
    
    async def send_message(self, chat_id: str, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send a message to a Telegram chat.
        
        Args:
            chat_id: Telegram chat ID or username
            message: Message text (supports HTML or Markdown)
            parse_mode: Parse mode for formatting (HTML or Markdown)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.bot:
            logger.warning("Telegram bot not configured, skipping message")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info(f"Telegram message sent to {chat_id}")
            return True
            
        except TelegramError as e:
            logger.error(f"Error sending Telegram message to {chat_id}: {e}")
            return False
    
    async def send_alerta_licitacao(self, chat_id: str, licitacao: Dict) -> bool:
        """
        Send alert about new licitacao.
        
        Args:
            chat_id: Telegram chat ID
            licitacao: Licitacao data
            
        Returns:
            True if sent successfully
        """
        message = f"""
🔔 <b>Nova Licitação Detectada</b>

📋 <b>Número:</b> {licitacao.get('numero_compra', 'N/A')}
📍 <b>Município:</b> {licitacao.get('municipio_nome', 'N/A')}
💰 <b>Valor:</b> R$ {licitacao.get('valor_total_estimado', 0):,.2f}
📅 <b>Abertura:</b> {licitacao.get('data_abertura_proposta', 'N/A')}
🏷️ <b>Modalidade:</b> {licitacao.get('modalidade', 'N/A')}

📝 <b>Objeto:</b>
{licitacao.get('objeto', 'N/A')[:200]}...

🔗 <a href="{settings.FRONTEND_URL}/licitacoes/{licitacao.get('id', '')}">Ver Detalhes</a>
"""
        
        return await self.send_message(chat_id, message.strip())
    
    async def send_alerta_anomalia(self, chat_id: str, anomalia: Dict) -> bool:
        """
        Send alert about detected anomaly.
        
        Args:
            chat_id: Telegram chat ID
            anomalia: Anomaly data
            
        Returns:
            True if sent successfully
        """
        severity_emoji = {
            'crítica': '🔴',
            'alta': '🟠',
            'média': '🟡',
            'baixa': '🟢'
        }
        
        emoji = severity_emoji.get(anomalia.get('severidade', 'média').lower(), '⚠️')
        
        message = f"""
{emoji} <b>Anomalia Detectada</b>

🏷️ <b>Tipo:</b> {anomalia.get('tipo', 'N/A')}
📊 <b>Severidade:</b> {anomalia.get('severidade', 'N/A')}
📋 <b>Licitação:</b> {anomalia.get('licitacao_numero', 'N/A')}

📝 <b>Descrição:</b>
{anomalia.get('descricao', 'N/A')}

🔗 <a href="{settings.FRONTEND_URL}/anomalias/{anomalia.get('id', '')}">Ver Detalhes</a>
"""
        
        return await self.send_message(chat_id, message.strip())
    
    async def send_relatorio_pronto(self, chat_id: str, relatorio: Dict) -> bool:
        """
        Send notification about ready report.
        
        Args:
            chat_id: Telegram chat ID
            relatorio: Report data
            
        Returns:
            True if sent successfully
        """
        message = f"""
📊 <b>Relatório Disponível</b>

📋 <b>Tipo:</b> {relatorio.get('tipo', 'N/A')}
📄 <b>Formato:</b> {relatorio.get('formato', 'PDF')}
📅 <b>Gerado em:</b> {relatorio.get('created_at', 'N/A')}

⬇️ <a href="{settings.FRONTEND_URL}/api/v1/relatorios/download/{relatorio.get('id', '')}">Download</a>
"""
        
        return await self.send_message(chat_id, message.strip())


# Global instance
telegram_service = TelegramService()
