import hashlib
import secrets
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import re
import os
from functools import wraps
from flask import request, jsonify, g
import jwt
from werkzeug.security import check_password_hash

logger = logging.getLogger(__name__)

class SecurityService:
    """Serviço de segurança com rate limiting, validação e auditoria"""
    
    def __init__(self):
        self.rate_limits = {}  # {ip: {endpoint: [timestamps]}}
        self.failed_attempts = {}  # {ip: {count, last_attempt}}
        self.blocked_ips = set()
        self.jwt_secret = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
        
        # Configurações de rate limiting
        self.rate_limit_config = {
            'login': {'requests': 5, 'window': 300},  # 5 tentativas em 5 minutos
            'api': {'requests': 100, 'window': 60},   # 100 requests por minuto
            'bulk_send': {'requests': 3, 'window': 3600},  # 3 envios em massa por hora
        }
        
        # Configurações de bloqueio
        self.max_failed_attempts = 5
        self.block_duration = 1800  # 30 minutos
    
    def rate_limit(self, endpoint_type: str = 'api'):
        """Decorator para rate limiting"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                client_ip = self.get_client_ip()
                
                if self.is_rate_limited(client_ip, endpoint_type):
                    logger.warning(f"Rate limit excedido para IP {client_ip} no endpoint {endpoint_type}")
                    return jsonify({
                        'error': 'Rate limit excedido. Tente novamente mais tarde.',
                        'retry_after': self.get_retry_after(client_ip, endpoint_type)
                    }), 429
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def is_rate_limited(self, ip: str, endpoint_type: str) -> bool:
        """Verifica se o IP está sendo rate limited"""
        if ip in self.blocked_ips:
            return True
        
        config = self.rate_limit_config.get(endpoint_type, self.rate_limit_config['api'])
        current_time = time.time()
        
        # Inicializa estrutura se não existir
        if ip not in self.rate_limits:
            self.rate_limits[ip] = {}
        
        if endpoint_type not in self.rate_limits[ip]:
            self.rate_limits[ip][endpoint_type] = []
        
        # Remove timestamps antigos
        window_start = current_time - config['window']
        self.rate_limits[ip][endpoint_type] = [
            ts for ts in self.rate_limits[ip][endpoint_type] 
            if ts > window_start
        ]
        
        # Verifica se excedeu o limite
        if len(self.rate_limits[ip][endpoint_type]) >= config['requests']:
            return True
        
        # Adiciona timestamp atual
        self.rate_limits[ip][endpoint_type].append(current_time)
        return False
    
    def get_retry_after(self, ip: str, endpoint_type: str) -> int:
        """Retorna tempo em segundos para próxima tentativa"""
        config = self.rate_limit_config.get(endpoint_type, self.rate_limit_config['api'])
        
        if ip in self.rate_limits and endpoint_type in self.rate_limits[ip]:
            oldest_request = min(self.rate_limits[ip][endpoint_type])
            return int(config['window'] - (time.time() - oldest_request))
        
        return 0
    
    def record_failed_attempt(self, ip: str):
        """Registra tentativa de login falhada"""
        current_time = time.time()
        
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = {'count': 0, 'last_attempt': current_time}
        
        self.failed_attempts[ip]['count'] += 1
        self.failed_attempts[ip]['last_attempt'] = current_time
        
        # Bloqueia IP se excedeu tentativas
        if self.failed_attempts[ip]['count'] >= self.max_failed_attempts:
            self.blocked_ips.add(ip)
            logger.warning(f"IP {ip} bloqueado por excesso de tentativas de login")
    
    def clear_failed_attempts(self, ip: str):
        """Limpa tentativas falhadas após login bem-sucedido"""
        if ip in self.failed_attempts:
            del self.failed_attempts[ip]
        
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
    
    def cleanup_expired_blocks(self):
        """Remove bloqueios expirados"""
        current_time = time.time()
        expired_ips = []
        
        for ip in list(self.failed_attempts.keys()):
            if current_time - self.failed_attempts[ip]['last_attempt'] > self.block_duration:
                expired_ips.append(ip)
        
        for ip in expired_ips:
            if ip in self.failed_attempts:
                del self.failed_attempts[ip]
            if ip in self.blocked_ips:
                self.blocked_ips.remove(ip)
    
    def get_client_ip(self) -> str:
        """Obtém IP do cliente considerando proxies"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr or '127.0.0.1'
    
    def validate_input(self, data: Dict, rules: Dict) -> Dict:
        """
        Valida entrada de dados
        
        Args:
            data: Dados a serem validados
            rules: Regras de validação
        
        Returns:
            Dict com 'valid' (bool) e 'errors' (list)
        """
        errors = []
        
        for field, rule in rules.items():
            value = data.get(field)
            
            # Campo obrigatório
            if rule.get('required', False) and not value:
                errors.append(f"Campo '{field}' é obrigatório")
                continue
            
            if value is None:
                continue
            
            # Tipo de dados
            if 'type' in rule:
                if rule['type'] == 'email' and not self.is_valid_email(value):
                    errors.append(f"Campo '{field}' deve ser um email válido")
                elif rule['type'] == 'phone' and not self.is_valid_phone(value):
                    errors.append(f"Campo '{field}' deve ser um telefone válido")
                elif rule['type'] == 'string' and not isinstance(value, str):
                    errors.append(f"Campo '{field}' deve ser uma string")
                elif rule['type'] == 'int' and not isinstance(value, int):
                    errors.append(f"Campo '{field}' deve ser um número inteiro")
            
            # Comprimento mínimo/máximo
            if isinstance(value, str):
                if 'min_length' in rule and len(value) < rule['min_length']:
                    errors.append(f"Campo '{field}' deve ter pelo menos {rule['min_length']} caracteres")
                if 'max_length' in rule and len(value) > rule['max_length']:
                    errors.append(f"Campo '{field}' deve ter no máximo {rule['max_length']} caracteres")
            
            # Padrão regex
            if 'pattern' in rule and isinstance(value, str):
                if not re.match(rule['pattern'], value):
                    errors.append(f"Campo '{field}' não atende ao padrão exigido")
            
            # Valores permitidos
            if 'allowed_values' in rule and value not in rule['allowed_values']:
                errors.append(f"Campo '{field}' deve ser um dos valores: {rule['allowed_values']}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def is_valid_email(self, email: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def is_valid_phone(self, phone: str) -> bool:
        """Valida formato de telefone brasileiro"""
        # Remove caracteres não numéricos
        clean_phone = re.sub(r'\D', '', phone)
        
        # Verifica se tem 10 ou 11 dígitos (com ou sem código do país)
        if len(clean_phone) in [10, 11]:  # Celular/fixo
            return True
        elif len(clean_phone) in [12, 13] and clean_phone.startswith('55'):  # Com código do país
            return True
        
        return False
    
    def sanitize_input(self, text: str) -> str:
        """Sanitiza entrada de texto"""
        if not isinstance(text, str):
            return str(text)
        
        # Remove caracteres perigosos
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        # Remove espaços extras
        text = ' '.join(text.split())
        
        return text.strip()
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Gera token seguro"""
        return secrets.token_urlsafe(length)
    
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """Gera hash seguro da senha"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Usa PBKDF2 com SHA-256
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100k iterações
        )
        
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verifica senha contra hash"""
        try:
            computed_hash, _ = self.hash_password(password, salt)
            return secrets.compare_digest(computed_hash, password_hash)
        except Exception:
            return False
    
    def generate_jwt_token(self, user_data: Dict, expires_in: int = 3600) -> str:
        """Gera token JWT"""
        payload = {
            'user_id': user_data['id'],
            'username': user_data['username'],
            'role': user_data.get('role', 'user'),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verifica e decodifica token JWT"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token JWT expirado")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Token JWT inválido")
            return None
    
    def require_auth(self, f):
        """Decorator para exigir autenticação"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            
            # Verifica header Authorization
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    token = auth_header.split(' ')[1]  # Bearer <token>
                except IndexError:
                    return jsonify({'error': 'Token malformado'}), 401
            
            if not token:
                return jsonify({'error': 'Token de acesso necessário'}), 401
            
            # Verifica token
            payload = self.verify_jwt_token(token)
            if not payload:
                return jsonify({'error': 'Token inválido ou expirado'}), 401
            
            # Adiciona dados do usuário ao contexto
            g.current_user = payload
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def require_role(self, required_role: str):
        """Decorator para exigir role específica"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not hasattr(g, 'current_user'):
                    return jsonify({'error': 'Usuário não autenticado'}), 401
                
                user_role = g.current_user.get('role', 'user')
                
                # Hierarquia de roles: admin > supervisor > operator > user
                role_hierarchy = {
                    'user': 0,
                    'operator': 1,
                    'supervisor': 2,
                    'admin': 3
                }
                
                user_level = role_hierarchy.get(user_role, 0)
                required_level = role_hierarchy.get(required_role, 0)
                
                if user_level < required_level:
                    return jsonify({'error': 'Permissão insuficiente'}), 403
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def log_security_event(self, event_type: str, details: Dict):
        """Registra evento de segurança"""
        logger.warning(f"SECURITY EVENT - {event_type}: {details}")
        
        # Aqui poderia integrar com sistema de auditoria
        # Por exemplo, salvar no banco de dados ou enviar alerta

