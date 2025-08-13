"""
Serviço de envio WhatsApp baseado no script original ENVIO BOLETO WHATSAPP.py
"""
import os
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from ..models.config import SystemConfig
from ..models.audit import AuditLog, ActionType

class WhatsAppService:
    """Serviço de envio WhatsApp baseado no script original"""
    
    def __init__(self):
        self.driver = None
        self.profile_path = None
        self.boletos_folder = None
        self._load_config()
    
    def _load_config(self):
        """Carrega configurações do WhatsApp"""
        self.profile_path = SystemConfig.get_value(
            'whatsapp_profile_path', 
            'C:\\\\Users\\\\wmariano\\\\AppData\\\\Local\\\\Google\\\\Chrome\\\\User Data'
        )
        self.boletos_folder = SystemConfig.get_value(
            'boletos_folder',
            'C:\\\\Users\\\\wmariano\\\\Downloads\\\\ANEXOS'
        )
    
    def init_driver(self):
        """Inicializa driver do Chrome (baseado no script original)"""
        try:
            service = Service(ChromeDriverManager().install())
            options = Options()
            
            # Configurações do script original
            options.add_argument(f"user-data-dir={self.profile_path}")
            # options.add_argument("--incognito")  # Comentado como no original
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.delete_all_cookies()
            self.driver.get('https://web.whatsapp.com/')
            
            time.sleep(2)
            return True, "Driver inicializado"
            
        except Exception as e:
            return False, f"Erro ao inicializar driver: {e}"
    
    def close_driver(self):
        """Fecha driver"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except:
                pass
    
    def send_message_with_attachment(self, phone_number, message, attachment_path=None):
        """
        Envia mensagem WhatsApp com anexo (baseado no script original)
        """
        try:
            if not self.driver:
                success, msg = self.init_driver()
                if not success:
                    return False, msg
            
            # Formatar número (como no script original)
            if not phone_number.startswith('55'):
                phone_number = '55' + phone_number
            
            # URL do WhatsApp Web com mensagem
            encoded_message = urllib.parse.quote(message)
            link = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"
            
            self.driver.get(link)
            time.sleep(5)
            
            # Clicar no botão de enviar mensagem
            try:
                send_button = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[2]/button'))
                )
                send_button.click()
            except:
                return False, "Erro ao encontrar botão de enviar"
            
            # Se há anexo, enviar arquivo
            if attachment_path and os.path.exists(attachment_path):
                try:
                    # Clicar no botão de anexo
                    attach_button = self.driver.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/div')
                    attach_button.click()
                    
                    # Selecionar arquivo
                    file_input = self.driver.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/span/div/div/ul/li[4]/button/input')
                    file_input.send_keys(attachment_path)
                    
                    # Enviar arquivo
                    send_file_button = WebDriverWait(self.driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/div/div[2]/div[2]/div/div'))
                    )
                    send_file_button.click()
                    
                    time.sleep(5)
                    
                except Exception as e:
                    return False, f"Erro ao enviar anexo: {e}"
            
            # Aguardar processamento
            time.sleep(10)
            
            return True, "Mensagem enviada com sucesso"
            
        except Exception as e:
            return False, f"Erro ao enviar mensagem: {e}"
    
    def send_boleto_whatsapp(self, contact_data, user_id=None):
        """
        Envia boleto via WhatsApp (baseado no template original)
        """
        try:
            nome = contact_data.get('nome', 'Profissional')
            telefone = contact_data.get('telefone_completo')
            registro = contact_data.get('registro', '')
            
            if not telefone:
                return False, "Telefone não informado"
            
            # Mensagem baseada no script original
            message = f"Prezado {nome}, segue boleto da anuidade de 2024. A senha para abertura do arquivo são os 3 primeiros digitos do seu CPF. Aproveite o desconto para pagamento à vista."
            
            # Preparar caminho do boleto
            attachment_path = None
            if registro:
                # Formato do arquivo como no script original
                filename = registro.replace('-', '').replace('/', '') + '.pdf'
                attachment_path = os.path.join(self.boletos_folder, filename)
            
            # Enviar mensagem
            success, message_result = self.send_message_with_attachment(
                telefone, message, attachment_path
            )
            
            # Log da ação
            if user_id:
                AuditLog.log_action(
                    user_id=user_id,
                    action=ActionType.SEND_WHATSAPP,
                    resource_type='contact',
                    resource_id=registro,
                    description=f"WhatsApp enviado para {nome} ({telefone})",
                    details={'success': success, 'message': message_result},
                    success=success,
                    error_message=message_result if not success else None
                )
            
            return success, message_result
            
        except Exception as e:
            error_msg = f"Erro ao enviar WhatsApp: {e}"
            
            # Log do erro
            if user_id:
                AuditLog.log_action(
                    user_id=user_id,
                    action=ActionType.SEND_WHATSAPP,
                    resource_type='contact',
                    resource_id=contact_data.get('registro', ''),
                    description=f"Erro ao enviar WhatsApp para {contact_data.get('nome', '')}",
                    success=False,
                    error_message=error_msg
                )
            
            return False, error_msg
    
    def send_bulk_whatsapp(self, contacts_list, user_id=None):
        """
        Envia WhatsApp em lote (baseado no script original)
        """
        results = {
            'total': len(contacts_list),
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        # Inicializar driver uma vez
        success, msg = self.init_driver()
        if not success:
            return {
                'total': len(contacts_list),
                'sent': 0,
                'failed': len(contacts_list),
                'errors': [{'error': msg}]
            }
        
        try:
            for i, contact in enumerate(contacts_list):
                try:
                    success, message = self.send_boleto_whatsapp(contact, user_id=user_id)
                    
                    if success:
                        results['sent'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append({
                            'contact': contact.get('nome', ''),
                            'telefone': contact.get('telefone_completo', ''),
                            'error': message
                        })
                    
                    # Delay entre envios (como no script original)
                    time.sleep(10)
                    
                    print(f"Processado {i+1}/{len(contacts_list)}")
                    
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({
                        'contact': contact.get('nome', ''),
                        'telefone': contact.get('telefone_completo', ''),
                        'error': str(e)
                    })
                    
                    # Continuar mesmo com erro (como no script original)
                    continue
        
        finally:
            # Fechar driver
            self.close_driver()
        
        return results
    
    def get_devedores_list(self, db_config):
        """
        Obtém lista de devedores (baseado no script LEMBRETE_VENCIMENTO.py)
        """
        try:
            # Query baseada no script original
            query = """
            SET DATEFORMAT DMY 
            SELECT a2.[Nome], a2.[Num. Registro], a1.[DDD], a1.[Telefone] 
            FROM SCDA71 a1, SCDA01 a2  
            WHERE 
            ((a2.[Num. Registro]=a1.[Num. Registro] AND a1.[Telefone Ativo]='SIM' AND a1.[Tipo Telefone]='3' AND a1.DDD<>'') 
            OR 
            (a2.[Num. Registro]=a1.[Num. Registro] AND a1.[Telefone Ativo]='SIM' AND a1.[Telefone] LIKE '9%' AND a1.DDD<>'')) 
            AND a2.[Num. Registro] IN (
                SELECT DISTINCT [Num. Registro] FROM SFNA01 
                WHERE [Parcela]<>'0' AND [Data Vencimento] < GETDATE()
            )
            ORDER BY a1.[Num. Registro]
            """
            
            df = db_config.execute_query(query)
            
            if df.empty:
                return []
            
            # Processar dados como no script original
            devedores = []
            for _, row in df.iterrows():
                # Limpar dados
                ddd = str(row['DDD']).replace(' ', '') if pd.notna(row['DDD']) else ''
                telefone = str(row['Telefone']).replace('-', '') if pd.notna(row['Telefone']) else ''
                
                # Lógica do script original para adicionar 9
                if ddd and int(ddd) <= 29:
                    if len(telefone) <= 8:
                        telefone = '9' + telefone
                
                # Número completo
                telefone_completo = f"55{ddd}{telefone}"
                
                devedores.append({
                    'nome': row['Nome'],
                    'registro': row['Num. Registro'],
                    'ddd': ddd,
                    'telefone': telefone,
                    'telefone_completo': telefone_completo
                })
            
            return devedores
            
        except Exception as e:
            print(f"Erro ao obter devedores: {e}")
            return []
    
    def test_connection(self):
        """Testa conexão WhatsApp Web"""
        try:
            success, msg = self.init_driver()
            if success:
                self.close_driver()
                return True, "WhatsApp Web acessível"
            return False, msg
        except Exception as e:
            return False, f"Erro: {e}"

