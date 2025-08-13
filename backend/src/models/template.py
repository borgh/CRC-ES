"""
Modelo de templates de mensagens
"""
from datetime import datetime
from enum import Enum
from ..config.database import db

class TemplateType(Enum):
    EMAIL = 'email'
    WHATSAPP = 'whatsapp'

class Template(db.Model):
    """Templates de mensagens"""
    __tablename__ = 'templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.Enum(TemplateType), nullable=False)
    subject = db.Column(db.String(255))  # Para emails
    content = db.Column(db.Text, nullable=False)
    variables = db.Column(db.JSON)  # Variáveis disponíveis
    is_active = db.Column(db.Boolean, default=True)
    
    # Metadados
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    creator = db.relationship('User', backref='templates')
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.value if self.type else None,
            'subject': self.subject,
            'content': self.content,
            'variables': self.variables,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def render(self, variables_dict):
        """Renderiza template com variáveis"""
        content = self.content
        subject = self.subject or ''
        
        for key, value in variables_dict.items():
            placeholder = '{' + key + '}'
            content = content.replace(placeholder, str(value))
            subject = subject.replace(placeholder, str(value))
        
        return {
            'subject': subject,
            'content': content
        }
    
    @classmethod
    def get_default_variables(cls):
        """Retorna variáveis padrão disponíveis"""
        return [
            'nome',
            'registro',
            'email',
            'telefone',
            'ddd',
            'data_vencimento',
            'valor',
            'codigo_debito',
            'parcela'
        ]
    
    def __repr__(self):
        return f'<Template {self.name}>'

