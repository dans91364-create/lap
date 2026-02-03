"""Email service for sending notifications."""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

from config.settings import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails using SMTP."""
    
    def __init__(self):
        """Initialize email service with SMTP configuration."""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_from = settings.SMTP_FROM
        
        # Setup Jinja2 environment for templates
        templates_dir = Path(__file__).parent.parent.parent / "templates" / "email"
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def send_email(
        self,
        to: str,
        subject: str,
        template: str,
        context: Dict,
        html: Optional[str] = None
    ) -> bool:
        """
        Send email using template or raw HTML.
        
        Args:
            to: Recipient email address
            subject: Email subject
            template: Template name (without .html extension)
            context: Template context variables
            html: Raw HTML content (overrides template)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured, skipping email")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_from
            msg['To'] = to
            
            # Render HTML content
            if html:
                html_content = html
            else:
                try:
                    template_obj = self.jinja_env.get_template(f"{template}.html")
                    html_content = template_obj.render(context)
                except Exception as e:
                    logger.error(f"Error rendering template {template}: {e}")
                    html_content = f"<p>{context.get('message', 'Email notification')}</p>"
            
            # Attach HTML part
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {to}: {e}")
            return False
    
    def send_alerta_licitacao(self, to: str, licitacao: Dict) -> bool:
        """
        Send alert about new licitacao.
        
        Args:
            to: Recipient email
            licitacao: Licitacao data
            
        Returns:
            True if sent successfully
        """
        subject = f"Nova Licitação: {licitacao.get('objeto', 'N/A')[:50]}"
        
        context = {
            'numero': licitacao.get('numero_compra', 'N/A'),
            'objeto': licitacao.get('objeto', 'N/A'),
            'municipio': licitacao.get('municipio_nome', 'N/A'),
            'valor': licitacao.get('valor_total_estimado', 0),
            'data_abertura': licitacao.get('data_abertura_proposta', 'N/A'),
            'modalidade': licitacao.get('modalidade', 'N/A'),
            'url': f"{settings.FRONTEND_URL}/licitacoes/{licitacao.get('id', '')}"
        }
        
        return self.send_email(to, subject, 'alerta_licitacao', context)
    
    def send_alerta_anomalia(self, to: str, anomalia: Dict) -> bool:
        """
        Send alert about detected anomaly.
        
        Args:
            to: Recipient email
            anomalia: Anomaly data
            
        Returns:
            True if sent successfully
        """
        subject = f"Anomalia Detectada: {anomalia.get('tipo', 'N/A')}"
        
        context = {
            'tipo': anomalia.get('tipo', 'N/A'),
            'descricao': anomalia.get('descricao', 'N/A'),
            'severidade': anomalia.get('severidade', 'média'),
            'licitacao_numero': anomalia.get('licitacao_numero', 'N/A'),
            'url': f"{settings.FRONTEND_URL}/anomalias/{anomalia.get('id', '')}"
        }
        
        return self.send_email(to, subject, 'alerta_anomalia', context)
    
    def send_relatorio(self, to: str, relatorio: Dict) -> bool:
        """
        Send report notification.
        
        Args:
            to: Recipient email
            relatorio: Report data
            
        Returns:
            True if sent successfully
        """
        subject = f"Relatório Disponível: {relatorio.get('tipo', 'N/A')}"
        
        context = {
            'tipo': relatorio.get('tipo', 'N/A'),
            'formato': relatorio.get('formato', 'PDF'),
            'data': relatorio.get('created_at', 'N/A'),
            'download_url': f"{settings.FRONTEND_URL}/api/v1/relatorios/download/{relatorio.get('id', '')}"
        }
        
        return self.send_email(to, subject, 'relatorio', context)


# Global instance
email_service = EmailService()
