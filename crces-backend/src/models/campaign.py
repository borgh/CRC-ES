from datetime import datetime
from enum import Enum
import json
from .user import db

class CampaignType(Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    BOTH = "both"

class CampaignStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class MessageStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    BOUNCED = "bounced"

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Tipo e status da campanha
    type = db.Column(db.Enum(CampaignType), nullable=False)
    status = db.Column(db.Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    
    # Critérios de seleção (JSON)
    selection_criteria = db.Column(db.Text, nullable=True)  # JSON string
    
    # Templates utilizados (removidas FKs temporariamente)
    email_template_id = db.Column(db.Integer, nullable=True)
    whatsapp_template_id = db.Column(db.Integer, nullable=True)
    
    # Datas e controle
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    scheduled_at = db.Column(db.DateTime, nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Usuário que criou a campanha (removida FK temporariamente)
    created_by = db.Column(db.Integer, nullable=True)
    
    # Estatísticas
    total_recipients = db.Column(db.Integer, default=0)
    emails_sent = db.Column(db.Integer, default=0)
    emails_delivered = db.Column(db.Integer, default=0)
    emails_opened = db.Column(db.Integer, default=0)
    emails_clicked = db.Column(db.Integer, default=0)
    emails_bounced = db.Column(db.Integer, default=0)
    whatsapp_sent = db.Column(db.Integer, default=0)
    whatsapp_delivered = db.Column(db.Integer, default=0)
    whatsapp_read = db.Column(db.Integer, default=0)
    whatsapp_failed = db.Column(db.Integer, default=0)
    
    # Relacionamentos (removidos temporariamente)
    # email_template = db.relationship('EmailTemplate', backref='campaigns')
    # whatsapp_template = db.relationship('WhatsAppTemplate', backref='campaigns')
    # messages = db.relationship('CampaignMessage', backref='campaign', lazy=True, cascade='all, delete-orphan')

    def get_selection_criteria(self):
        """Retorna os critérios de seleção como dicionário"""
        if self.selection_criteria:
            return json.loads(self.selection_criteria)
        return {}

    def set_selection_criteria(self, criteria):
        """Define os critérios de seleção"""
        self.selection_criteria = json.dumps(criteria)

    def update_statistics(self):
        """Atualiza as estatísticas da campanha baseado nas mensagens"""
        email_stats = db.session.query(
            db.func.count(CampaignMessage.id).label('total'),
            db.func.sum(db.case([(CampaignMessage.email_status == MessageStatus.SENT, 1)], else_=0)).label('sent'),
            db.func.sum(db.case([(CampaignMessage.email_status == MessageStatus.DELIVERED, 1)], else_=0)).label('delivered'),
            db.func.sum(db.case([(CampaignMessage.email_opened == True, 1)], else_=0)).label('opened'),
            db.func.sum(db.case([(CampaignMessage.email_clicked == True, 1)], else_=0)).label('clicked'),
            db.func.sum(db.case([(CampaignMessage.email_status == MessageStatus.BOUNCED, 1)], else_=0)).label('bounced')
        ).filter(
            CampaignMessage.campaign_id == self.id,
            CampaignMessage.email_sent_at.isnot(None)
        ).first()

        whatsapp_stats = db.session.query(
            db.func.count(CampaignMessage.id).label('total'),
            db.func.sum(db.case([(CampaignMessage.whatsapp_status == MessageStatus.SENT, 1)], else_=0)).label('sent'),
            db.func.sum(db.case([(CampaignMessage.whatsapp_status == MessageStatus.DELIVERED, 1)], else_=0)).label('delivered'),
            db.func.sum(db.case([(CampaignMessage.whatsapp_status == MessageStatus.READ, 1)], else_=0)).label('read'),
            db.func.sum(db.case([(CampaignMessage.whatsapp_status == MessageStatus.FAILED, 1)], else_=0)).label('failed')
        ).filter(
            CampaignMessage.campaign_id == self.id,
            CampaignMessage.whatsapp_sent_at.isnot(None)
        ).first()

        if email_stats:
            self.emails_sent = email_stats.sent or 0
            self.emails_delivered = email_stats.delivered or 0
            self.emails_opened = email_stats.opened or 0
            self.emails_clicked = email_stats.clicked or 0
            self.emails_bounced = email_stats.bounced or 0

        if whatsapp_stats:
            self.whatsapp_sent = whatsapp_stats.sent or 0
            self.whatsapp_delivered = whatsapp_stats.delivered or 0
            self.whatsapp_read = whatsapp_stats.read or 0
            self.whatsapp_failed = whatsapp_stats.failed or 0

        db.session.commit()

    def to_dict(self, include_messages=False):
        """Converte a campanha para dicionário"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type.value,
            'status': self.status.value,
            'selection_criteria': self.get_selection_criteria(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_by': self.created_by,
            'statistics': {
                'total_recipients': self.total_recipients,
                'email': {
                    'sent': self.emails_sent,
                    'delivered': self.emails_delivered,
                    'opened': self.emails_opened,
                    'clicked': self.emails_clicked,
                    'bounced': self.emails_bounced
                },
                'whatsapp': {
                    'sent': self.whatsapp_sent,
                    'delivered': self.whatsapp_delivered,
                    'read': self.whatsapp_read,
                    'failed': self.whatsapp_failed
                }
            }
        }
        
        if include_messages:
            data['messages'] = [msg.to_dict() for msg in self.messages]
        
        return data

    def __repr__(self):
        return f'<Campaign {self.name}>'


class CampaignMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, nullable=False)  # Removida FK temporariamente
    
    # Dados do destinatário
    recipient_name = db.Column(db.String(200), nullable=False)
    recipient_email = db.Column(db.String(120), nullable=True)
    recipient_phone = db.Column(db.String(20), nullable=True)
    recipient_registry = db.Column(db.String(50), nullable=False)  # Num. Registro do CRC
    
    # Status e dados do email
    email_status = db.Column(db.Enum(MessageStatus), nullable=True)
    email_sent_at = db.Column(db.DateTime, nullable=True)
    email_delivered_at = db.Column(db.DateTime, nullable=True)
    email_opened = db.Column(db.Boolean, default=False)
    email_opened_at = db.Column(db.DateTime, nullable=True)
    email_clicked = db.Column(db.Boolean, default=False)
    email_clicked_at = db.Column(db.DateTime, nullable=True)
    email_error_message = db.Column(db.Text, nullable=True)
    
    # Status e dados do WhatsApp
    whatsapp_status = db.Column(db.Enum(MessageStatus), nullable=True)
    whatsapp_sent_at = db.Column(db.DateTime, nullable=True)
    whatsapp_delivered_at = db.Column(db.DateTime, nullable=True)
    whatsapp_read_at = db.Column(db.DateTime, nullable=True)
    whatsapp_error_message = db.Column(db.Text, nullable=True)
    
    # Dados adicionais (JSON)
    additional_data = db.Column(db.Text, nullable=True)  # JSON string para dados extras
    
    # Controle
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_additional_data(self):
        """Retorna dados adicionais como dicionário"""
        if self.additional_data:
            return json.loads(self.additional_data)
        return {}

    def set_additional_data(self, data):
        """Define dados adicionais"""
        self.additional_data = json.dumps(data)

    def to_dict(self):
        """Converte a mensagem para dicionário"""
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'recipient_name': self.recipient_name,
            'recipient_email': self.recipient_email,
            'recipient_phone': self.recipient_phone,
            'recipient_registry': self.recipient_registry,
            'email': {
                'status': self.email_status.value if self.email_status else None,
                'sent_at': self.email_sent_at.isoformat() if self.email_sent_at else None,
                'delivered_at': self.email_delivered_at.isoformat() if self.email_delivered_at else None,
                'opened': self.email_opened,
                'opened_at': self.email_opened_at.isoformat() if self.email_opened_at else None,
                'clicked': self.email_clicked,
                'clicked_at': self.email_clicked_at.isoformat() if self.email_clicked_at else None,
                'error_message': self.email_error_message
            },
            'whatsapp': {
                'status': self.whatsapp_status.value if self.whatsapp_status else None,
                'sent_at': self.whatsapp_sent_at.isoformat() if self.whatsapp_sent_at else None,
                'delivered_at': self.whatsapp_delivered_at.isoformat() if self.whatsapp_delivered_at else None,
                'read_at': self.whatsapp_read_at.isoformat() if self.whatsapp_read_at else None,
                'error_message': self.whatsapp_error_message
            },
            'additional_data': self.get_additional_data(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<CampaignMessage {self.recipient_name} - Campaign {self.campaign_id}>'

