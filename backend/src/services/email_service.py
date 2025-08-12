"""
Serviço de envio de emails baseado no script original do CRC-ES
Adaptado do arquivo 'ENVIO BOLETO EMAIL.py'
"""
import os
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from src.models.database import DatabaseConfig, MessageLog, db
from datetime import datetime

class EmailService:
    """Serviço de envio de emails"""
    
    def __init__(self):
        self.smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', 587))
        self.username = os.getenv('EMAIL_USERNAME', 'atendimento@crc-es.org.br')
        self.password = os.getenv('EMAIL_PASSWORD', '')
    
    def get_anuidade_recipients(self, year='2025'):
        """
        Busca destinatários da anuidade no banco original
        Baseado na query original do script
        """
        query = f"""
        SET DATEFORMAT DMY 
        SELECT DISTINCT 
            a1.Nome, 
            a1.[Num. Registro], 
            a1.[E-Mail] 
        FROM SCDA01 a1, SFNA01 a2
        WHERE a1.[Num. Registro] = a2.[Num. Registro] 
        AND a2.[Codigo Debito] LIKE '{year[2:]}%' 
        AND a2.Parcela = '0'
        """
        
        try:
            results = DatabaseConfig.execute_original_query(query)
            return results if results else []
        except Exception as e:
            print(f"Erro ao buscar destinatários: {e}")
            return []
    
    def send_anuidade_email(self, recipient_data, year='2025', attachment_path=None):
        """
        Envia email de anuidade baseado no template original
        """
        try:
            # Configurar email
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = recipient_data.get('E-Mail', '')
            msg['Subject'] = f'ANUIDADE DE {year} - CRCES'
            
            # Template original adaptado
            html_body = f"""
            <html>
            <body>
                <p>Prezado(a) {recipient_data.get('Nome', '')}, bom dia.</p>
                
                <p>Através do boleto abaixo você poderá realizar o pagamento integral da anuidade de {year} com vencimento para até o dia 31/03/{year}.</p>
                
                <p>Estando em dia com o Conselho, você garante os seguintes benefícios:</p>
                <ul>
                    <li>Emissão gratuita de Certificado Digital do tipo A1, com validade de 1 ano;</li>
                    <li>Acesso à credencial do Sesc ES com condições especiais;</li>
                    <li>Descontos e benefícios em instituições de ensino parceiras;</li>
                    <li>Parceria com Administradoras de planos de saúde (ass. Médica e Hospitalar) e planos odontológicos com tabela de preços diferenciada;</li>
                    <li>Capacitações gratuitas;</li>
                    <li>Acesso gratuito ao Espaço Compartilhado do Profissional da Contabilidade (Co-Working);</li>
                </ul>
                
                <p>Caso queira efetuar o parcelamento, acesse o portal do CRCES, e clique no banner exclusivo para anuidade de {year}.</p>
                
                <p>Para tirar suas dúvidas, entre em contato pelo Whatsapp no número (27) 3232-1600 (SOMENTE MENSAGENS), e-mail: atendimento@crc-es.org.br ou pelos telefones de contato (27) 3232-1607 / 1611 / 1626/ 1641.</p>
                
                <p><strong>A SENHA DE ABERTURA DO ARQUIVO SÃO OS 3 PRIMEIROS DÍGITOS DO SEU CPF.</strong></p>
                
                <p>Atenciosamente</p>
                <p><em>ENVIADO AUTOMATICAMENTE</em></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # Anexar arquivo se fornecido
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(attachment_path)}'
                    )
                    msg.attach(part)
            
            # Enviar email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            
            text = msg.as_string()
            server.sendmail(self.username, recipient_data.get('E-Mail', ''), text)
            server.quit()
            
            return True, "Email enviado com sucesso"
            
        except Exception as e:
            return False, f"Erro ao enviar email: {str(e)}"
    
    def send_bulk_emails(self, campaign_id, recipients=None, year='2025'):
        """
        Envia emails em massa
        """
        if not recipients:
            recipients = self.get_anuidade_recipients(year)
        
        sent_count = 0
        failed_count = 0
        
        for i, recipient in enumerate(recipients, 1):
            try:
                # Preparar caminho do anexo baseado no registro
                registro = recipient.get('Num. Registro', '').replace('-', '').replace('/', '')
                attachment_path = f"/uploads/boletos/{registro}.pdf"
                
                # Enviar email
                success, message = self.send_anuidade_email(recipient, year, attachment_path)
                
                # Log da mensagem
                log_entry = MessageLog(
                    campaign_id=campaign_id,
                    recipient_name=recipient.get('Nome', ''),
                    recipient_contact=recipient.get('E-Mail', ''),
                    message_type='email',
                    status='sent' if success else 'failed',
                    error_message=None if success else message
                )
                db.session.add(log_entry)
                
                if success:
                    sent_count += 1
                    print(f"Email {i} enviado para {recipient.get('Nome', '')}")
                else:
                    failed_count += 1
                    print(f"Falha no email {i} para {recipient.get('Nome', '')}: {message}")
                
                # Delay entre envios (como no script original)
                time.sleep(3)
                
            except Exception as e:
                failed_count += 1
                print(f"Erro no email {i}: {str(e)}")
                
                # Log do erro
                log_entry = MessageLog(
                    campaign_id=campaign_id,
                    recipient_name=recipient.get('Nome', ''),
                    recipient_contact=recipient.get('E-Mail', ''),
                    message_type='email',
                    status='failed',
                    error_message=str(e)
                )
                db.session.add(log_entry)
        
        # Salvar logs
        db.session.commit()
        
        return {
            'total': len(recipients),
            'sent': sent_count,
            'failed': failed_count
        }
    
    def send_custom_email(self, to_email, subject, content, attachment_path=None):
        """
        Envia email personalizado
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(content, 'html', 'utf-8'))
            
            # Anexar arquivo se fornecido
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(attachment_path)}'
                    )
                    msg.attach(part)
            
            # Enviar
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            
            text = msg.as_string()
            server.sendmail(self.username, to_email, text)
            server.quit()
            
            return True, "Email enviado com sucesso"
            
        except Exception as e:
            return False, f"Erro ao enviar email: {str(e)}"

