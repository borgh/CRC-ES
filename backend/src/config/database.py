"""
Configuração de banco de dados baseada nos scripts originais
"""
import os
import sqlite3
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
import pandas as pd

try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False
    print("pyodbc não disponível - usando SQLite para desenvolvimento")

db = SQLAlchemy()

class DatabaseConfig:
    """Configurações de banco de dados originais do CRC-ES"""
    
    # Configurações originais dos scripts
    DEFAULT_SERVER = 'SERVERSQL\\CRCES'
    DEFAULT_DATABASE = 'SCF'
    DEFAULT_USERNAME = 'ADMIN'
    DEFAULT_PASSWORD = 'DIAVIC'
    DEFAULT_DRIVER = 'SQL Server'
    
    def __init__(self):
        self.server = os.getenv('DB_SERVER', self.DEFAULT_SERVER)
        self.database = os.getenv('DB_DATABASE', self.DEFAULT_DATABASE)
        self.username = os.getenv('DB_USERNAME', self.DEFAULT_USERNAME)
        self.password = os.getenv('DB_PASSWORD', self.DEFAULT_PASSWORD)
        self.driver = os.getenv('DB_DRIVER', self.DEFAULT_DRIVER)
    
    def get_sql_server_connection_string(self):
        """Retorna string de conexão SQL Server original"""
        return f"DRIVER={{{self.driver}}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}"
    
    def get_sqlalchemy_uri(self):
        """Retorna URI SQLAlchemy para SQL Server"""
        if PYODBC_AVAILABLE:
            return f"mssql+pyodbc://{self.username}:{self.password}@{self.server}/{self.database}?driver=SQL+Server"
        else:
            # Fallback para SQLite em desenvolvimento
            return "sqlite:///crces_dev.db"
    
    def get_connection(self):
        """Retorna conexão pyodbc original dos scripts"""
        if PYODBC_AVAILABLE:
            try:
                return pyodbc.connect(self.get_sql_server_connection_string())
            except Exception as e:
                print(f"Erro ao conectar SQL Server: {e}")
                return None
        return None
    
    def execute_query(self, query, params=None):
        """Executa query usando pandas (como nos scripts originais)"""
        if PYODBC_AVAILABLE:
            try:
                conn = self.get_connection()
                if conn:
                    df = pd.read_sql(query, conn, params=params)
                    conn.close()
                    return df
            except Exception as e:
                print(f"Erro ao executar query: {e}")
        
        # Fallback para SQLite
        return self._execute_sqlite_query(query, params)
    
    def _execute_sqlite_query(self, query, params=None):
        """Executa query no SQLite (desenvolvimento)"""
        try:
            conn = sqlite3.connect('crces_dev.db')
            df = pd.read_sql(query, conn, params=params)
            conn.close()
            return df
        except Exception as e:
            print(f"Erro SQLite: {e}")
            return pd.DataFrame()

# Instância global
db_config = DatabaseConfig()

def init_database(app):
    """Inicializa banco de dados"""
    app.config['SQLALCHEMY_DATABASE_URI'] = db_config.get_sqlalchemy_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()
        
        # Criar dados iniciais
        create_initial_data()

def create_initial_data():
    """Cria dados iniciais do sistema"""
    from ..models.user import User
    from ..models.config import SystemConfig
    
    # Criar usuário admin se não existir
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@crc-es.org.br',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
    
    # Criar configurações padrão
    configs = [
        ('db_server', db_config.server, 'Servidor SQL Server'),
        ('db_database', db_config.database, 'Nome do Banco de Dados'),
        ('db_username', db_config.username, 'Usuário do Banco'),
        ('db_password', db_config.password, 'Senha do Banco'),
        ('smtp_server', 'smtp.gmail.com', 'Servidor SMTP'),
        ('smtp_port', '587', 'Porta SMTP'),
        ('email_from', 'atendimento@crc-es.org.br', 'Email Remetente'),
        ('whatsapp_profile_path', 'C:\\\\Users\\\\wmariano\\\\AppData\\\\Local\\\\Google\\\\Chrome\\\\User Data', 'Perfil Chrome WhatsApp'),
        ('boletos_folder', 'C:\\\\Users\\\\wmariano\\\\Downloads\\\\ANEXOS', 'Pasta de Boletos'),
    ]
    
    for key, value, description in configs:
        config = SystemConfig.query.filter_by(key=key).first()
        if not config:
            config = SystemConfig(
                key=key,
                value=value,
                description=description
            )
            db.session.add(config)
    
    try:
        db.session.commit()
        print("✅ Dados iniciais criados com sucesso!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao criar dados iniciais: {e}")

def test_connection():
    """Testa conexão com banco original"""
    try:
        conn = db_config.get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            return True, "Conexão SQL Server OK"
    except Exception as e:
        return False, f"Erro: {e}"
    
    return False, "pyodbc não disponível - usando SQLite"

