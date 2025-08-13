from datetime import datetime
import json
from .user import db

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Informações do usuário
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    username = db.Column(db.String(80), nullable=True)  # Backup caso user seja deletado
    
    # Informações da ação
    action_type = db.Column(db.String(100), nullable=False)  # 'CREATE', 'UPDATE', 'DELETE', 'LOGIN', etc.
    resource_type = db.Column(db.String(100), nullable=False)  # 'User', 'Campaign', 'Template', etc.
    resource_id = db.Column(db.String(100), nullable=True)  # ID do recurso afetado
    
    # Detalhes da mudança
    old_values = db.Column(db.Text, nullable=True)  # JSON dos valores antigos
    new_values = db.Column(db.Text, nullable=True)  # JSON dos valores novos
    
    # Informações da requisição
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 ou IPv6
    user_agent = db.Column(db.Text, nullable=True)
    endpoint = db.Column(db.String(200), nullable=True)  # Endpoint da API chamado
    method = db.Column(db.String(10), nullable=True)  # GET, POST, PUT, DELETE
    
    # Resultado da ação
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # Dados adicionais
    additional_data = db.Column(db.Text, nullable=True)  # JSON para dados extras
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_old_values(self):
        """Retorna os valores antigos como dicionário"""
        if self.old_values:
            return json.loads(self.old_values)
        return {}

    def set_old_values(self, values):
        """Define os valores antigos"""
        if values:
            self.old_values = json.dumps(values, default=str)

    def get_new_values(self):
        """Retorna os valores novos como dicionário"""
        if self.new_values:
            return json.loads(self.new_values)
        return {}

    def set_new_values(self, values):
        """Define os valores novos"""
        if values:
            self.new_values = json.dumps(values, default=str)

    def get_additional_data(self):
        """Retorna dados adicionais como dicionário"""
        if self.additional_data:
            return json.loads(self.additional_data)
        return {}

    def set_additional_data(self, data):
        """Define dados adicionais"""
        if data:
            self.additional_data = json.dumps(data, default=str)

    def to_dict(self):
        """Converte o log para dicionário"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'action_type': self.action_type,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'old_values': self.get_old_values(),
            'new_values': self.get_new_values(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'endpoint': self.endpoint,
            'method': self.method,
            'success': self.success,
            'error_message': self.error_message,
            'additional_data': self.get_additional_data(),
            'created_at': self.created_at.isoformat()
        }

    @staticmethod
    def log_action(user_id=None, username=None, action_type=None, resource_type=None, 
                   resource_id=None, old_values=None, new_values=None, ip_address=None, 
                   user_agent=None, endpoint=None, method=None, success=True, 
                   error_message=None, additional_data=None):
        """Método estático para criar um log de auditoria"""
        log = AuditLog(
            user_id=user_id,
            username=username,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            success=success,
            error_message=error_message
        )
        
        log.set_old_values(old_values)
        log.set_new_values(new_values)
        log.set_additional_data(additional_data)
        
        db.session.add(log)
        db.session.commit()
        
        return log

    def __repr__(self):
        return f'<AuditLog {self.action_type} {self.resource_type} by {self.username}>'


class SystemHealth(db.Model):
    """Modelo para monitoramento da saúde do sistema"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Métricas de sistema
    cpu_usage = db.Column(db.Float, nullable=True)  # Percentual de uso da CPU
    memory_usage = db.Column(db.Float, nullable=True)  # Percentual de uso da memória
    disk_usage = db.Column(db.Float, nullable=True)  # Percentual de uso do disco
    
    # Métricas de banco de dados
    db_connections = db.Column(db.Integer, nullable=True)  # Número de conexões ativas
    db_response_time = db.Column(db.Float, nullable=True)  # Tempo de resposta em ms
    
    # Métricas de API
    api_response_time = db.Column(db.Float, nullable=True)  # Tempo médio de resposta
    api_error_rate = db.Column(db.Float, nullable=True)  # Taxa de erro das APIs
    
    # Métricas de envio
    emails_in_queue = db.Column(db.Integer, default=0)  # Emails na fila
    whatsapp_in_queue = db.Column(db.Integer, default=0)  # WhatsApp na fila
    failed_sends_last_hour = db.Column(db.Integer, default=0)  # Envios falhados na última hora
    
    # Status geral
    overall_status = db.Column(db.String(20), default='healthy')  # 'healthy', 'warning', 'critical'
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Converte as métricas para dicionário"""
        return {
            'id': self.id,
            'system': {
                'cpu_usage': self.cpu_usage,
                'memory_usage': self.memory_usage,
                'disk_usage': self.disk_usage
            },
            'database': {
                'connections': self.db_connections,
                'response_time': self.db_response_time
            },
            'api': {
                'response_time': self.api_response_time,
                'error_rate': self.api_error_rate
            },
            'messaging': {
                'emails_in_queue': self.emails_in_queue,
                'whatsapp_in_queue': self.whatsapp_in_queue,
                'failed_sends_last_hour': self.failed_sends_last_hour
            },
            'overall_status': self.overall_status,
            'created_at': self.created_at.isoformat()
        }

    @staticmethod
    def record_metrics(**kwargs):
        """Método estático para registrar métricas do sistema"""
        health = SystemHealth(**kwargs)
        db.session.add(health)
        db.session.commit()
        return health

    def __repr__(self):
        return f'<SystemHealth {self.overall_status} at {self.created_at}>'

