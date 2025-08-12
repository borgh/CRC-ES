"""
Serviço de envio via WhatsApp baseado no script original do CRC-ES
Adaptado do arquivo 'ENVIO BOLETO WHATSAPP.py'
"""
import os
import time
import urllib.parse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from src.models.database import DatabaseConfig, MessageLog, db

class WhatsAppService:
    """Serviço de envio via WhatsApp"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def setup_driver(self):
        """Configura o driver do Chrome para WhatsApp Web"""
        try:
            service = Service(ChromeDriverManager().install())
            options = Options()
            
            # Configurações do Chrome (baseadas no script original)
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            # Para manter sessão do WhatsApp (se possível)
            user_data_dir = "/tmp/chrome_user_data"
            options.add_argument(f"--user-data-dir={user_data_dir}")
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 30)
            
            # Acessar WhatsApp Web
            self.driver.get('https://web.whatsapp.com/')
            
            return True
            
        except Exception as e:
            print(f"Erro ao configurar driver: {e}")
            return False
    
    def wait_for_whatsapp_login(self, timeout=60):
        """Aguarda login no WhatsApp Web"""
        try:
            print("Aguardando login no WhatsApp Web...")
            print("Escaneie o QR Code para continuar...")
            
            # Aguarda até que a página principal carregue (indicando login)
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="chat-list"]'))
            )
            
            print("Login realizado com sucesso!")
            return True
            
        except Exception as e:
            print(f"Timeout no login do WhatsApp: {e}")
            return False
    
    def get_whatsapp_recipients(self):
        """
        Busca destinatários do WhatsApp no banco original
        Baseado na estrutura do script original
        """
        query = """
        SELECT DISTINCT 
            a1.Nome as Nome_x,
            a1.[Num. Registro] as Registro,
            a1.Telefone as Telefone_Completo
        FROM SCDA01 a1, SFNA01 a2
        WHERE a1.[Num. Registro] = a2.[Num. Registro] 
        AND a2.[Codigo Debito] LIKE '25%' 
        AND a2.Parcela = '0'
        AND a1.Telefone IS NOT NULL
        AND a1.Telefone != ''
        """
        
        try:
            results = DatabaseConfig.execute_original_query(query)
            return results if results else []
        except Exception as e:
            print(f"Erro ao buscar destinatários WhatsApp: {e}")
            return []
    
    def format_phone_number(self, phone):
        """Formata número de telefone para WhatsApp"""
        if not phone:
            return None
        
        # Remove caracteres especiais
        phone = ''.join(filter(str.isdigit, str(phone)))
        
        # Adiciona código do país se necessário
        if len(phone) == 11 and phone.startswith('27'):
            phone = '55' + phone
        elif len(phone) == 10:
            phone = '5527' + phone
        elif len(phone) == 8:
            phone = '552732' + phone
        
        return phone
    
    def send_whatsapp_message(self, recipient_data, attachment_path=None):
        """
        Envia mensagem via WhatsApp baseada no template original
        """
        try:
            nome = recipient_data.get('Nome_x', '')
            telefone = self.format_phone_number(recipient_data.get('Telefone_Completo', ''))
            
            if not telefone:
                return False, "Número de telefone inválido"
            
            # Mensagem baseada no script original
            texto = f"Prezado {nome}, segue boleto da anuidade de 2025. A senha para abertura do arquivo são os 3 primeiros dígitos do seu CPF. Aproveite o desconto para pagamento à vista em janeiro."
            
            # Codificar texto para URL
            texto_encoded = urllib.parse.quote(texto)
            
            # Criar link do WhatsApp
            link = f"https://web.whatsapp.com/send?phone={telefone}&text={texto_encoded}"
            
            # Navegar para o link
            self.driver.get(link)
            time.sleep(5)
            
            # Aguardar e clicar no botão de enviar mensagem
            send_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="compose-btn-send"]'))
            )
            send_button.click()
            
            # Se há anexo, enviar arquivo
            if attachment_path and os.path.exists(attachment_path):
                time.sleep(2)
                
                # Clicar no botão de anexo
                attach_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@title="Anexar"]'))
                )
                attach_button.click()
                
                # Selecionar documento
                document_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//input[@accept="*"]'))
                )
                document_button.send_keys(attachment_path)
                
                # Aguardar upload e enviar
                time.sleep(3)
                send_file_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//span[@data-testid="send"]'))
                )
                send_file_button.click()
            
            time.sleep(3)
            return True, "Mensagem enviada com sucesso"
            
        except Exception as e:
            return False, f"Erro ao enviar mensagem: {str(e)}"
    
    def send_bulk_whatsapp(self, campaign_id, recipients=None):
        """
        Envia mensagens em massa via WhatsApp
        """
        if not recipients:
            recipients = self.get_whatsapp_recipients()
        
        if not self.setup_driver():
            return {'error': 'Falha ao configurar driver'}
        
        if not self.wait_for_whatsapp_login():
            return {'error': 'Falha no login do WhatsApp'}
        
        sent_count = 0
        failed_count = 0
        
        for i, recipient in enumerate(recipients, 1):
            try:
                # Preparar caminho do anexo
                registro = recipient.get('Registro', '').replace('-', '').replace('/', '')
                attachment_path = f"/uploads/boletos/{registro}.pdf"
                
                # Enviar mensagem
                success, message = self.send_whatsapp_message(recipient, attachment_path)
                
                # Log da mensagem
                log_entry = MessageLog(
                    campaign_id=campaign_id,
                    recipient_name=recipient.get('Nome_x', ''),
                    recipient_contact=recipient.get('Telefone_Completo', ''),
                    message_type='whatsapp',
                    status='sent' if success else 'failed',
                    error_message=None if success else message
                )
                db.session.add(log_entry)
                
                if success:
                    sent_count += 1
                    print(f"WhatsApp {i} enviado para {recipient.get('Nome_x', '')}")
                else:
                    failed_count += 1
                    print(f"Falha no WhatsApp {i} para {recipient.get('Nome_x', '')}: {message}")
                
                # Delay entre envios (como no script original)
                time.sleep(10)
                
            except Exception as e:
                failed_count += 1
                print(f"Erro no WhatsApp {i}: {str(e)}")
                
                # Log do erro
                log_entry = MessageLog(
                    campaign_id=campaign_id,
                    recipient_name=recipient.get('Nome_x', ''),
                    recipient_contact=recipient.get('Telefone_Completo', ''),
                    message_type='whatsapp',
                    status='failed',
                    error_message=str(e)
                )
                db.session.add(log_entry)
        
        # Fechar driver
        if self.driver:
            self.driver.quit()
        
        # Salvar logs
        db.session.commit()
        
        return {
            'total': len(recipients),
            'sent': sent_count,
            'failed': failed_count
        }
    
    def close_driver(self):
        """Fecha o driver do navegador"""
        if self.driver:
            self.driver.quit()
            self.driver = None

