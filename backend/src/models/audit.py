"""
Modelo de auditoria e logs do sistema
"""
from datetime import datetime
from enum import Enum
from ..config.database import db

class ActionType(Enum):
    LOGIN = 'login'
    LOGOUT = 'logout'
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    SEND_EMAIL = 'send_email'
    SEND_WHATSAPP = 'send_whatsapp'
    SYNC_DATA = 'sync_data'
    CONFIG_CHANGE = 'config_change'
    CAMPAIGN_START = 'campaign_start'
    CAMPAIGN_COMPLETE = 'campaign_complete'

class AuditLog(db.Model):
    """Logs de auditoria do sistema"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.Enum(ActionType), nullable=False)
    resource_type = db.Column(db.String(50))  # campaign, template, config, etc.
    resource_id = db.Column(db.String(50))
    description = db.Column(db.Text)
    details = db.Column(db.JSON)  # Dados adicionais
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='audit_logs')
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Sistema',
            'action': self.action.value if self.action else None,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'description': self.description,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'success': self.success,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def log_action(cls, user_id, action, resource_type=None, resource_id=None, 
                   description=None, details=None, ip_address=None, user_agent=None,
                   success=True, error_message=None):
        """Registra uma ação no log"""
        try:
            log = cls(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                description=description,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                error_message=error_message
            )
            db.session.add(log)
            db.session.commit()
            return log
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao registrar log: {e}")
            return None
    
    def __repr__(self):
        return f'<AuditLog {self.action.value} by {self.user_id}>'

