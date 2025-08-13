import requests
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Serviço para envio de mensagens via WhatsApp usando Evolution API"""
    
    def __init__(self):
        self.api_url = os.getenv('WHATSAPP_API_URL', 'http://localhost:8080')
        self.api_key = os.getenv('WHATSAPP_API_KEY', '')
        self.instance_name = os.getenv('WHATSAPP_INSTANCE', 'crces-instance')
        self.session = requests.Session()
        
        # Headers padrão
        self.session.headers.update({
            'Content-Type': 'application/json',
            'apikey': self.api_key
        })
    
    def check_connection(self) -> bool:
        """Verifica se a conexão com a API está funcionando"""
        try:
            response = self.session.get(f"{self.api_url}/instance/connectionState/{self.instance_name}")
            if response.status_code == 200:
                data = response.json()
                return data.get('instance', {}).get('state') == 'open'
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar conexão WhatsApp: {e}")
            return False
    
    def format_phone_number(self, phone: str) -> str:
        """Formata número de telefone para o padrão WhatsApp"""
        # Remove caracteres não numéricos
        phone = ''.join(filter(str.isdigit, phone))
        
        # Adiciona código do país se não tiver
        if len(phone) == 11 and phone.startswith('0'):
            phone = '55' + phone[1:]  # Remove 0 e adiciona 55
        elif len(phone) == 10:
            phone = '55' + phone
        elif not phone.startswith('55'):
            phone = '55' + phone
        
        return phone + '@s.whatsapp.net'
    
    def send_text_message(self, phone: str, message: str) -> Dict:
        """Envia mensagem de texto"""
        try:
            formatted_phone = self.format_phone_number(phone)
            
            payload = {
                "number": formatted_phone,
                "text": message
            }
            
            response = self.session.post(
                f"{self.api_url}/message/sendText/{self.instance_name}",
                json=payload
            )
            
            if response.status_code == 201:
                return {
                    'success': True,
                    'message_id': response.json().get('key', {}).get('id'),
                    'data': response.json()
                }
            else:
                logger.error(f"Erro ao enviar mensagem: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem WhatsApp: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_document(self, phone: str, document_path: str, caption: str = "") -> Dict:
        """Envia documento (PDF, DOC, etc.)"""
        try:
            formatted_phone = self.format_phone_number(phone)
            
            if not os.path.exists(document_path):
                return {
                    'success': False,
                    'error': 'Arquivo não encontrado'
                }
            
            # Lê o arquivo e converte para base64
            import base64
            with open(document_path, 'rb') as file:
                file_data = base64.b64encode(file.read()).decode('utf-8')
            
            file_name = Path(document_path).name
            
            payload = {
                "number": formatted_phone,
                "media": file_data,
                "fileName": file_name,
                "caption": caption
            }
            
            response = self.session.post(
                f"{self.api_url}/message/sendMedia/{self.instance_name}",
                json=payload
            )
            
            if response.status_code == 201:
                return {
                    'success': True,
                    'message_id': response.json().get('key', {}).get('id'),
                    'data': response.json()
                }
            else:
                logger.error(f"Erro ao enviar documento: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Erro ao enviar documento WhatsApp: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_bulk_messages(self, recipients: List[Dict], template: str, variables: Dict = None, delay: int = 2) -> List[Dict]:
        """
        Envia mensagens em massa
        
        Args:
            recipients: Lista de destinatários com dados
            template: Template da mensagem com variáveis
            variables: Variáveis globais para substituição
            delay: Delay entre envios em segundos
        """
        results = []
        
        for i, recipient in enumerate(recipients):
            try:
                # Substitui variáveis no template
                message = self.replace_variables(template, recipient, variables)
                
                # Envia mensagem
                result = self.send_text_message(recipient['phone'], message)
                result['recipient'] = recipient
                result['index'] = i
                
                results.append(result)
                
                # Log do resultado
                if result['success']:
                    logger.info(f"Mensagem enviada para {recipient['phone']}: {result['message_id']}")
                else:
                    logger.error(f"Falha ao enviar para {recipient['phone']}: {result['error']}")
                
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
    
    def send_bulk_documents(self, recipients: List[Dict], document_path: str, caption_template: str = "", delay: int = 3) -> List[Dict]:
        """Envia documentos em massa"""
        results = []
        
        for i, recipient in enumerate(recipients):
            try:
                # Substitui variáveis na legenda
                caption = self.replace_variables(caption_template, recipient) if caption_template else ""
                
                # Envia documento
                result = self.send_document(recipient['phone'], document_path, caption)
                result['recipient'] = recipient
                result['index'] = i
                
                results.append(result)
                
                # Log do resultado
                if result['success']:
                    logger.info(f"Documento enviado para {recipient['phone']}: {result['message_id']}")
                else:
                    logger.error(f"Falha ao enviar documento para {recipient['phone']}: {result['error']}")
                
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
        message = template
        
        # Substitui variáveis do destinatário
        for key, value in recipient.items():
            placeholder = f"{{{{{key}}}}}"
            message = message.replace(placeholder, str(value))
        
        # Substitui variáveis globais
        if global_vars:
            for key, value in global_vars.items():
                placeholder = f"{{{{{key}}}}}"
                message = message.replace(placeholder, str(value))
        
        return message
    
    def get_message_status(self, message_id: str) -> Dict:
        """Verifica status de uma mensagem"""
        try:
            response = self.session.get(
                f"{self.api_url}/chat/findMessages/{self.instance_name}",
                params={'id': message_id}
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Erro ao verificar status da mensagem: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_phone_number(self, phone: str) -> bool:
        """Valida se um número de telefone é válido"""
        try:
            formatted_phone = self.format_phone_number(phone)
            
            response = self.session.get(
                f"{self.api_url}/chat/whatsappNumbers/{self.instance_name}",
                params={'numbers': [formatted_phone]}
            )
            
            if response.status_code == 200:
                data = response.json()
                return len(data) > 0 and data[0].get('exists', False)
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao validar número: {e}")
            return False

