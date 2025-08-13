"""
Sistema CRC-ES - Versão Ultra Simplificada
Compatível com Python 3.13+ sem SQLAlchemy
"""
import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# Configuração da aplicação
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
CORS(app)

# Configurações
app.config['SECRET_KEY'] = 'crces-sistema-secreto-2025'

# Configuração do banco SQLite
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'app.db')

def init_database():
    """Inicializa o banco de dados SQLite"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Criar tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Criar tabela de campanhas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            status TEXT DEFAULT 'draft',
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            scheduled_at TIMESTAMP,
            sent_at TIMESTAMP,
            total_recipients INTEGER DEFAULT 0,
            sent_count INTEGER DEFAULT 0,
            failed_count INTEGER DEFAULT 0,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Criar tabela de templates
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            subject TEXT,
            content TEXT NOT NULL,
            variables TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT 1,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Criar tabela de logs de mensagens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS message_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            recipient_name TEXT,
            recipient_contact TEXT,
            message_type TEXT,
            status TEXT,
            error_message TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
        )
    ''')
    
    # Criar tabela de auditoria
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            resource TEXT,
            resource_id INTEGER,
            details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Criar usuário admin padrão
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        password_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin@crc-es.org.br', password_hash, 'admin'))
        print("✅ Usuário admin criado com sucesso!")
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados inicializado com sucesso!")

def get_db_connection():
    """Obtém conexão com o banco de dados"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Rotas de autenticação
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Endpoint de login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Usuário e senha são obrigatórios'}), 400
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND active = 1',
            (username,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            # Atualizar último login
            conn = get_db_connection()
            conn.execute(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                (user['id'],)
            )
            conn.commit()
            conn.close()
            
            # Simular token JWT (simplificado)
            token = f"token_{user['id']}_{datetime.now().timestamp()}"
            
            return jsonify({
                'access_token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role']
                }
            })
        else:
            return jsonify({'error': 'Credenciais inválidas'}), 401
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/auth/profile', methods=['GET'])
def profile():
    """Endpoint de perfil do usuário"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token não fornecido'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Validação simplificada do token
        if not token.startswith('token_'):
            return jsonify({'error': 'Token inválido'}), 401
        
        user_id = token.split('_')[1]
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE id = ? AND active = 1',
            (user_id,)
        ).fetchone()
        conn.close()
        
        if user:
            return jsonify({
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role']
                }
            })
        else:
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# Rotas de campanhas
@app.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    """Lista todas as campanhas"""
    try:
        conn = get_db_connection()
        campaigns = conn.execute('''
            SELECT c.*, u.username as created_by_name
            FROM campaigns c
            LEFT JOIN users u ON c.created_by = u.id
            ORDER BY c.created_at DESC
        ''').fetchall()
        conn.close()
        
        campaigns_list = []
        for campaign in campaigns:
            campaigns_list.append({
                'id': campaign['id'],
                'name': campaign['name'],
                'description': campaign['description'],
                'type': campaign['type'],
                'status': campaign['status'],
                'created_by': campaign['created_by'],
                'created_by_name': campaign['created_by_name'],
                'created_at': campaign['created_at'],
                'total_recipients': campaign['total_recipients'],
                'sent_count': campaign['sent_count'],
                'failed_count': campaign['failed_count']
            })
        
        return jsonify({'campaigns': campaigns_list})
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/campaigns', methods=['POST'])
def create_campaign():
    """Cria uma nova campanha"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        campaign_type = data.get('type')
        
        if not name or not campaign_type:
            return jsonify({'error': 'Nome e tipo são obrigatórios'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO campaigns (name, description, type, created_by)
            VALUES (?, ?, ?, ?)
        ''', (name, description, campaign_type, 1))  # User ID 1 (admin)
        
        campaign_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Campanha criada com sucesso',
            'campaign_id': campaign_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# Rotas de estatísticas
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Retorna estatísticas do sistema"""
    try:
        conn = get_db_connection()
        
        # Total de campanhas
        total_campaigns = conn.execute('SELECT COUNT(*) FROM campaigns').fetchone()[0]
        
        # Total de mensagens enviadas
        total_sent = conn.execute('SELECT SUM(sent_count) FROM campaigns').fetchone()[0] or 0
        
        # Campanhas ativas
        active_campaigns = conn.execute(
            "SELECT COUNT(*) FROM campaigns WHERE status IN ('scheduled', 'sending')"
        ).fetchone()[0]
        
        # Taxa de sucesso (simulada)
        success_rate = 94.2
        
        conn.close()
        
        return jsonify({
            'total_campaigns': total_campaigns,
            'total_sent': total_sent,
            'active_campaigns': active_campaigns,
            'success_rate': success_rate,
            'whatsapp_sent': int(total_sent * 0.6),
            'email_sent': int(total_sent * 0.4)
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# Rota de health check
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check do sistema"""
    return jsonify({
        'status': 'ok',
        'message': 'Sistema CRC-ES funcionando',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Rota para servir arquivos estáticos do frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve arquivos do frontend"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    print("🚀 Iniciando Sistema CRC-ES...")
    print("📊 Versão Ultra Simplificada - Python 3.13 Compatible")
    
    # Inicializar banco de dados
    init_database()
    
    print("✅ Sistema iniciado com sucesso!")
    print("🌐 Acesse: http://localhost:5000")
    print("🔑 Login: admin / admin123")
    print("📋 API Health: http://localhost:5000/api/health")
    print("\n" + "="*50)
    
    # Iniciar servidor
    app.run(host='0.0.0.0', port=5000, debug=True)

