"""
Serviço de envio de emails baseado no script original ENVIO BOLETO EMAIL.py
"""
import os
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from flask import current_app
from ..models.config import SystemConfig
from ..models.audit import AuditLog, ActionType

try:
    import win32com.client as win32
    OUTLOOK_AVAILABLE = True
except ImportError:
    OUTLOOK_AVAILABLE = False
    print("win32com não disponível - usando SMTP")

class EmailService:
    """Serviço de envio de emails"""
    
    def __init__(self):
        self.smtp_server = None
        self.smtp_port = None
        self.smtp_username = None
        self.smtp_password = None
        self.email_from = None
        self._load_config()
    
    def _load_config(self):
        """Carrega configurações de email"""
        self.smtp_server = SystemConfig.get_value('smtp_server', 'smtp.gmail.com')
        self.smtp_port = int(SystemConfig.get_value('smtp_port', '587'))
        self.smtp_username = SystemConfig.get_value('smtp_username', '')
        self.smtp_password = SystemConfig.get_value('smtp_password', '')
        self.email_from = SystemConfig.get_value('email_from', 'atendimento@crc-es.org.br')
    
    def send_email_outlook(self, to_email, subject, html_body, attachment_path=None):
        """
        Envia email via Outlook (baseado no script original)
        """
        if not OUTLOOK_AVAILABLE:
            return False, "Outlook não disponível"
        
        try:
            # Integração com Outlook como no script original
            outlook = win32.Dispatch('outlook.application')
            email = outlook.CreateItem(0)
            
            email.To = to_email
            email.Subject = subject
            email.HTMLBody = html_body
            
            # Anexar arquivo se fornecido
            if attachment_path and os.path.exists(attachment_path):
                email.Attachments.Add(attachment_path)
            
            email.Send()
            time.sleep(3)  # Delay como no script original
            
            return True, "Email enviado via Outlook"
            
        except Exception as e:
            return False, f"Erro Outlook: {e}"
    
    def send_email_smtp(self, to_email, subject, html_body, attachment_path=None):
        """
        Envia email via SMTP
        """
        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Adicionar corpo HTML
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Anexar arquivo se fornecido
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    attachment = MIMEApplication(f.read())
                    attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=os.path.basename(attachment_path)
                    )
                    msg.attach(attachment)
            
            # Enviar via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True, "Email enviado via SMTP"
            
        except Exception as e:
            return False, f"Erro SMTP: {e}"
    
    def send_email(self, to_email, subject, html_body, attachment_path=None, use_outlook=True):
        """
        Envia email (tenta Outlook primeiro, depois SMTP)
        """
        if use_outlook and OUTLOOK_AVAILABLE:
            success, message = self.send_email_outlook(to_email, subject, html_body, attachment_path)
            if success:
                return success, message
        
        # Fallback para SMTP
        return self.send_email_smtp(to_email, subject, html_body, attachment_path)
    
    def send_anuidade_email(self, contact_data, boleto_path=None, user_id=None):
        """
        Envia email de anuidade (baseado no template original)
        """
        try:
            nome = contact_data.get('nome', 'Profissional')
            email = contact_data.get('email')
            registro = contact_data.get('registro', '')
            
            if not email:
                return False, "Email não informado"
            
            # Template HTML baseado no script original
            html_body = f"""
            <p>Prezado(a) {nome}, bom dia.</p>
            
            <p>Através do boleto abaixo você poderá realizar o pagamento integral da anuidade de 2024 com vencimento para até o dia 31/03/2024.</p>
            
            <p>Estando em dia com o Conselho, você garante os seguintes benefícios:</p>
            
            <p>- Emissão gratuita de Certificado Digital do tipo A1, com validade de 1 ano;</p>
            <p>- Acesso à credencial do Sesc ES com condições especiais;</p>
            <p>- Descontos e benefícios em instituições de ensino parceiras;</p>
            <p>- Parceria com Administradoras de planos de saúde (ass. Médica e Hospitalar) e planos odontológicos com tabela de preços diferenciada;</p>
            <p>- Capacitações gratuitas;</p>
            <p>- Acesso gratuito ao Espaço Compartilhado do Profissional da Contabilidade (Co-Working);</p>
            
            <p>Caso queira efetuar o parcelamento, acesse o portal do CRCES, e clique no banner exclusivo para anuidade de 2024.</p>
            
            <p>Para tirar suas dúvidas, entre em contato pelo Whatsapp no número (27) 3232-1600 (SOMENTE MENSAGENS), e-mail: atendimento@crc-es.org.br ou pelos telefones de contato (27) 3232-1607 / 1611 / 1626/ 1641.</p>
            
            <p><strong>A SENHA DE ABERTURA DO ARQUIVO SÃO OS 3 PRIMEIROS DIGITOS DO SEU CPF.</strong></p>
            
            <p>Atenciosamente</p>
            <p>ENVIADO AUTOMATICAMENTE</p>
            """
            
            subject = 'ANUIDADE DE 2024 - CRCES'
            
            # Preparar caminho do boleto
            attachment_path = None
            if boleto_path:
                attachment_path = boleto_path
            elif registro:
                # Formato do arquivo como no script original
                boletos_folder = SystemConfig.get_value('boletos_folder', 'boletos')
                filename = registro.replace('-', '').replace('/', '') + '.pdf'
                attachment_path = os.path.join(boletos_folder, filename)
            
            # Enviar email
            success, message = self.send_email(email, subject, html_body, attachment_path)
            
            # Log da ação
            if user_id:
                AuditLog.log_action(
                    user_id=user_id,
                    action=ActionType.SEND_EMAIL,
                    resource_type='contact',
                    resource_id=registro,
                    description=f"Email de anuidade enviado para {nome} ({email})",
                    details={'success': success, 'message': message},
                    success=success,
                    error_message=message if not success else None
                )
            
            return success, message
            
        except Exception as e:
            error_msg = f"Erro ao enviar email: {e}"
            
            # Log do erro
            if user_id:
                AuditLog.log_action(
                    user_id=user_id,
                    action=ActionType.SEND_EMAIL,
                    resource_type='contact',
                    resource_id=contact_data.get('registro', ''),
                    description=f"Erro ao enviar email para {contact_data.get('nome', '')}",
                    success=False,
                    error_message=error_msg
                )
            
            return False, error_msg
    
    def send_bulk_emails(self, contacts_list, template_data, user_id=None):
        """
        Envia emails em lote
        """
        results = {
            'total': len(contacts_list),
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        for contact in contacts_list:
            try:
                success, message = self.send_anuidade_email(contact, user_id=user_id)
                
                if success:
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'contact': contact.get('nome', ''),
                        'email': contact.get('email', ''),
                        'error': message
                    })
                
                # Delay entre envios
                time.sleep(2)
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'contact': contact.get('nome', ''),
                    'email': contact.get('email', ''),
                    'error': str(e)
                })
        
        return results
    
    def test_connection(self):
        """Testa conexão de email"""
        try:
            if OUTLOOK_AVAILABLE:
                outlook = win32.Dispatch('outlook.application')
                return True, "Outlook disponível"
        except:
            pass
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
            return True, "SMTP conectado"
        except Exception as e:
            return False, f"Erro SMTP: {e}"

