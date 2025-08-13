"""
Modelo de configurações do sistema
"""
from datetime import datetime
from ..config.database import db

class SystemConfig(db.Model):
    """Configurações editáveis do sistema"""
    __tablename__ = 'system_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255))
    category = db.Column(db.String(50), default='general')
    is_encrypted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value if not self.is_encrypted else '***',
            'description': self.description,
            'category': self.category,
            'is_encrypted': self.is_encrypted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_value(cls, key, default=None):
        """Obtém valor de configuração"""
        config = cls.query.filter_by(key=key).first()
        return config.value if config else default
    
    @classmethod
    def set_value(cls, key, value, description=None, category='general', user_id=None):
        """Define valor de configuração"""
        config = cls.query.filter_by(key=key).first()
        if config:
            config.value = value
            config.updated_by = user_id
            config.updated_at = datetime.utcnow()
        else:
            config = cls(
                key=key,
                value=value,
                description=description,
                category=category,
                updated_by=user_id
            )
            db.session.add(config)
        
        db.session.commit()
        return config
    
    def __repr__(self):
        return f'<SystemConfig {self.key}>'

