"""
Modelo de campanhas de envio
"""
from datetime import datetime
from enum import Enum
from ..config.database import db

class CampaignType(Enum):
    EMAIL = 'email'
    WHATSAPP = 'whatsapp'
    BOTH = 'both'

class CampaignStatus(Enum):
    DRAFT = 'draft'
    SCHEDULED = 'scheduled'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

class Campaign(db.Model):
    """Campanhas de envio de mensagens"""
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.Enum(CampaignType), nullable=False)
    status = db.Column(db.Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    
    # Templates
    email_template_id = db.Column(db.Integer, db.ForeignKey('templates.id'))
    whatsapp_template_id = db.Column(db.Integer, db.ForeignKey('templates.id'))
    
    # Filtros de destinatários
    target_filter = db.Column(db.JSON)  # Critérios de filtro
    recipient_count = db.Column(db.Integer, default=0)
    
    # Agendamento
    scheduled_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Estatísticas
    sent_count = db.Column(db.Integer, default=0)
    delivered_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    
    # Metadados
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    email_template = db.relationship('Template', foreign_keys=[email_template_id])
    whatsapp_template = db.relationship('Template', foreign_keys=[whatsapp_template_id])
    creator = db.relationship('User', backref='campaigns')
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type.value if self.type else None,
            'status': self.status.value if self.status else None,
            'email_template_id': self.email_template_id,
            'whatsapp_template_id': self.whatsapp_template_id,
            'target_filter': self.target_filter,
            'recipient_count': self.recipient_count,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'sent_count': self.sent_count,
            'delivered_count': self.delivered_count,
            'failed_count': self.failed_count,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_success_rate(self):
        """Calcula taxa de sucesso"""
        if self.sent_count == 0:
            return 0
        return (self.delivered_count / self.sent_count) * 100
    
    def __repr__(self):
        return f'<Campaign {self.name}>'

