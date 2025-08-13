import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
from typing import List, Dict, Optional
import os
from pathlib import Path
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailService:
    """Serviço para envio de emails SMTP"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
        self.from_name = os.getenv('FROM_NAME', 'CRC-ES')
        self.use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        
    def test_connection(self) -> bool:
        """Testa a conexão SMTP"""
        try:
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                
                server.login(self.smtp_username, self.smtp_password)
                logger.info("Conexão SMTP testada com sucesso")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao testar conexão SMTP: {e}")
            return False
    
    def send_email(self, to_email: str, subject: str, html_content: str, 
                   text_content: str = None, attachments: List[str] = None,
                   to_name: str = None) -> Dict:
        """
        Envia um email
        
        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            html_content: Conteúdo HTML do email
            text_content: Conteúdo texto alternativo
            attachments: Lista de caminhos para anexos
            to_name: Nome do destinatário
        """
        try:
            # Cria mensagem
            message = MIMEMultipart('alternative')
            message['From'] = formataddr((self.from_name, self.from_email))
            message['To'] = formataddr((to_name or to_email, to_email))
            message['Subject'] = subject
            
            # Adiciona conteúdo texto se fornecido
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                message.attach(text_part)
            
            # Adiciona conteúdo HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            message.attach(html_part)
            
            # Adiciona anexos se fornecidos
            if attachments:
                for attachment_path in attachments:
                    if os.path.exists(attachment_path):
                        self._add_attachment(message, attachment_path)
                    else:
                        logger.warning(f"Anexo não encontrado: {attachment_path}")
            
            # Envia email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
            
            logger.info(f"Email enviado com sucesso para {to_email}")
            return {
                'success': True,
                'message_id': message['Message-ID'],
                'to_email': to_email
            }
            
        except Exception as e:
            logger.error(f"Erro ao enviar email para {to_email}: {e}")
            return {
                'success': False,
                'error': str(e),
                'to_email': to_email
            }
    
    def _add_attachment(self, message: MIMEMultipart, file_path: str):
        """Adiciona anexo à mensagem"""
        try:
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            
            filename = Path(file_path).name
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            
            message.attach(part)
            
        except Exception as e:
            logger.error(f"Erro ao adicionar anexo {file_path}: {e}")
    
    def send_bulk_emails(self, recipients: List[Dict], subject_template: str, 
                        html_template: str, text_template: str = None,
                        attachments: List[str] = None, delay: int = 1) -> List[Dict]:
        """
        Envia emails em massa
        
        Args:
            recipients: Lista de destinatários com dados
            subject_template: Template do assunto com variáveis
            html_template: Template HTML com variáveis
            text_template: Template texto com variáveis
            attachments: Lista de anexos
            delay: Delay entre envios em segundos
        """
        results = []
        
        for i, recipient in enumerate(recipients):
            try:
                # Substitui variáveis nos templates
                subject = self.replace_variables(subject_template, recipient)
                html_content = self.replace_variables(html_template, recipient)
                text_content = self.replace_variables(text_template, recipient) if text_template else None
                
                # Envia email
                result = self.send_email(
                    to_email=recipient['email'],
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    attachments=attachments,
                    to_name=recipient.get('name')
                )
                
                result['recipient'] = recipient
                result['index'] = i
                results.append(result)
                
                # Log do resultado
                if result['success']:
                    logger.info(f"Email enviado para {recipient['email']}")
                else:
                    logger.error(f"Falha ao enviar email para {recipient['email']}: {result['error']}")
                
                # Delay entre envios
                if i < len(recipients) - 1:
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Erro ao processar destinatário {recipient}: {e}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'recipient': recipient,
                    'index': i
                })
        
        return results
    
    def replace_variables(self, template: str, recipient: Dict, global_vars: Dict = None) -> str:
        """Substitui variáveis no template"""
        if not template:
            return ""
            
        content = template
        
        # Substitui variáveis do destinatário
        for key, value in recipient.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        
        # Substitui variáveis globais
        if global_vars:
            for key, value in global_vars.items():
                placeholder = f"{{{{{key}}}}}"
                content = content.replace(placeholder, str(value))
        
        return content
    
    def validate_email(self, email: str) -> bool:
        """Valida formato de email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def create_html_template(self, title: str, content: str, footer: str = None) -> str:
        """Cria template HTML básico"""
        footer = footer or "CRC-ES - Conselho Regional de Contabilidade do Espírito Santo"
        
        return f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #2c5aa0;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border: 1px solid #ddd;
                }}
                .footer {{
                    background-color: #333;
                    color: white;
                    padding: 15px;
                    text-align: center;
                    font-size: 12px;
                    border-radius: 0 0 5px 5px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #2c5aa0;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
                .highlight {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>CRC-ES</h1>
                <p>Conselho Regional de Contabilidade do Espírito Santo</p>
            </div>
            <div class="content">
                {content}
            </div>
            <div class="footer">
                {footer}
            </div>
        </body>
        </html>
        """
    
    def create_cobranca_template(self, nome: str, valor: str, vencimento: str, registro: str) -> str:
        """Cria template específico para cobrança"""
        content = f"""
        <h2>Prezado(a) {nome},</h2>
        
        <p>Informamos que existe(m) mensalidade(s) em aberto em seu nome no CRC-ES:</p>
        
        <div class="highlight">
            <ul>
                <li><strong>Valor:</strong> R$ {valor}</li>
                <li><strong>Vencimento:</strong> {vencimento}</li>
                <li><strong>Registro:</strong> {registro}</li>
            </ul>
        </div>
        
        <p>Para regularizar sua situação, efetue o pagamento através do boleto em anexo.</p>
        
        <p>Em caso de dúvidas, entre em contato conosco através dos canais oficiais.</p>
        
        <p>Atenciosamente,<br>
        <strong>Equipe CRC-ES</strong></p>
        """
        
        return self.create_html_template("Mensalidade em Aberto", content)

