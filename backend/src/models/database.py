"""
Configuração do banco de dados para o sistema CRC-ES
Suporte para SQL Server (produção) e SQLite (desenvolvimento)
"""
import os
import pyodbc
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class DatabaseConfig:
    """Configuração de conexão com banco de dados"""
    
    @staticmethod
    def get_sql_server_connection():
        """Conexão com SQL Server original do CRC-ES"""
        server = os.getenv('DB_SERVER', 'SERVERSQL\\CRCES')
        database = os.getenv('DB_DATABASE', 'SCF')
        username = os.getenv('DB_USERNAME', 'ADMIN')
        password = os.getenv('DB_PASSWORD', 'DIAVIC')
        driver = os.getenv('DB_DRIVER', 'SQL Server')
        
        connection_string = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        
        try:
            connection = pyodbc.connect(connection_string)
            return connection
        except Exception as e:
            print(f"Erro ao conectar com SQL Server: {e}")
            return None
    
    @staticmethod
    def execute_original_query(query):
        """Executa query no banco original do CRC-ES"""
        connection = DatabaseConfig.get_sql_server_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(query)
                
                # Se é SELECT, retorna dados
                if query.strip().upper().startswith('SELECT'):
                    columns = [column[0] for column in cursor.description]
                    results = []
                    for row in cursor.fetchall():
                        results.append(dict(zip(columns, row)))
                    return results
                else:
                    # Para INSERT, UPDATE, DELETE
                    connection.commit()
                    return True
                    
            except Exception as e:
                print(f"Erro ao executar query: {e}")
                return None
            finally:
                connection.close()
        return None

# Modelos SQLAlchemy para desenvolvimento
class User(db.Model):
    """Modelo de usuário do sistema"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Campaign(db.Model):
    """Modelo de campanha de mensagens"""
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(20), nullable=False)  # 'email' ou 'whatsapp'
    status = db.Column(db.String(20), default='draft')  # 'draft', 'scheduled', 'sending', 'completed', 'failed'
    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scheduled_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    total_recipients = db.Column(db.Integer, default=0)
    sent_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'status': self.status,
            'template_id': self.template_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'total_recipients': self.total_recipients,
            'sent_count': self.sent_count,
            'failed_count': self.failed_count
        }

class Template(db.Model):
    """Modelo de template de mensagem"""
    __tablename__ = 'templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'email' ou 'whatsapp'
    subject = db.Column(db.String(500))  # Para emails
    content = db.Column(db.Text, nullable=False)
    variables = db.Column(db.Text)  # JSON com variáveis disponíveis
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'subject': self.subject,
            'content': self.content,
            'variables': self.variables,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'active': self.active
        }

class MessageLog(db.Model):
    """Log de mensagens enviadas"""
    __tablename__ = 'message_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'))
    recipient_name = db.Column(db.String(200))
    recipient_contact = db.Column(db.String(200))  # email ou telefone
    message_type = db.Column(db.String(20))  # 'email' ou 'whatsapp'
    status = db.Column(db.String(20))  # 'sent', 'failed', 'pending'
    error_message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'recipient_name': self.recipient_name,
            'recipient_contact': self.recipient_contact,
            'message_type': self.message_type,
            'status': self.status,
            'error_message': self.error_message,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }

class AuditLog(db.Model):
    """Log de auditoria do sistema"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    resource = db.Column(db.String(100))
    resource_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource': self.resource,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

def init_database(app):
    """Inicializa o banco de dados"""
    db.init_app(app)
    
    with app.app_context():
        # Cria todas as tabelas
        db.create_all()
        
        # Cria usuário admin padrão se não existir
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            from werkzeug.security import generate_password_hash
            admin_user = User(
                username='admin',
                email='admin@crc-es.org.br',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Usuário admin criado com sucesso!")

