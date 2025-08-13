#!/usr/bin/env python3
"""
Script para inicializar o banco de dados do sistema CRC-ES
"""

import os
import sys
from datetime import datetime

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importa todos os modelos para garantir que as tabelas sejam criadas
from src.models.user import db, User, Role, Permission, user_roles
from src.models.campaign import Campaign, CampaignMessage
from src.models.template import EmailTemplate, WhatsAppTemplate
from src.models.audit import AuditLog, SystemHealth
from src.main import create_app

def init_database():
    """Inicializa o banco de dados com tabelas e dados iniciais"""
    app = create_app()
    
    with app.app_context():
        print("Criando tabelas do banco de dados...")
        
        # Remove todas as tabelas existentes
        db.drop_all()
        
        # Cria todas as tabelas
        db.create_all()
        
        print("Tabelas criadas com sucesso!")
        
        # Cria permissões básicas
        permissions = [
            'view_dashboard',
            'create_campaigns', 
            'manage_templates',
            'manage_users',
            'view_audit_logs',
            'system_admin'
        ]
        
        print("Criando permissões...")
        for perm_name in permissions:
            if not Permission.query.filter_by(name=perm_name).first():
                permission = Permission(name=perm_name)
                db.session.add(permission)
        
        # Cria roles básicos
        roles_data = [
            {
                'name': 'admin',
                'description': 'Administrador do sistema',
                'permissions': permissions  # Admin tem todas as permissões
            },
            {
                'name': 'operator',
                'description': 'Operador de campanhas',
                'permissions': ['view_dashboard', 'create_campaigns', 'manage_templates']
            },
            {
                'name': 'viewer',
                'description': 'Visualizador apenas',
                'permissions': ['view_dashboard']
            }
        ]
        
        print("Criando roles...")
        for role_data in roles_data:
            if not Role.query.filter_by(name=role_data['name']).first():
                role = Role(
                    name=role_data['name'],
                    description=role_data['description']
                )
                
                # Adiciona permissões ao role
                for perm_name in role_data['permissions']:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        role.permissions.append(permission)
                
                db.session.add(role)
        
        db.session.commit()
        
        # Cria usuário admin padrão
        print("Criando usuário admin...")
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@crces.org.br',
                is_active=True,
                is_verified=True
            )
            admin_user.set_password('admin123')  # Senha padrão - deve ser alterada
            
            # Adiciona role de admin
            admin_role = Role.query.filter_by(name='admin').first()
            if admin_role:
                admin_user.roles.append(admin_role)
            
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"Usuário admin criado com ID: {admin_user.id}")
        else:
            print("Usuário admin já existe")
        
        # Cria templates de exemplo
        print("Criando templates de exemplo...")
        
        # Template de email para cobrança
        try:
            email_template = EmailTemplate(
                name='Cobrança Mensalidade',
                description='Template para cobrança de mensalidades em aberto',
                subject='CRC-ES - Mensalidade em Aberto - {{nome_contador}}',
                html_content='''
                <html>
                <body>
                    <h2>Prezado(a) {{nome_contador}},</h2>
                    
                    <p>Informamos que existe(m) mensalidade(s) em aberto em seu nome no CRC-ES:</p>
                    
                    <ul>
                        <li><strong>Valor:</strong> R$ {{valor_total}}</li>
                        <li><strong>Vencimento:</strong> {{data_vencimento}}</li>
                        <li><strong>Registro:</strong> {{numero_registro}}</li>
                    </ul>
                    
                    <p>Para regularizar sua situação, efetue o pagamento através do boleto em anexo.</p>
                    
                    <p>Em caso de dúvidas, entre em contato conosco.</p>
                    
                    <p>Atenciosamente,<br>
                    <strong>CRC-ES - Conselho Regional de Contabilidade do Espírito Santo</strong></p>
                </body>
                </html>
                ''',
                text_content='Prezado(a) {{nome_contador}}, informamos que existe(m) mensalidade(s) em aberto...',
                created_by=admin_user.id
            )
            email_template.set_available_variables([
                'nome_contador', 'valor_total', 'data_vencimento', 'numero_registro'
            ])
            db.session.add(email_template)
        except Exception as e:
            print(f"Erro ao criar template de email: {e}")
        
        # Template de WhatsApp para cobrança
        try:
            whatsapp_template = WhatsAppTemplate(
                name='Cobrança WhatsApp',
                description='Template para cobrança via WhatsApp',
                message_content='''🏛️ *CRC-ES - Mensalidade em Aberto*

Olá {{nome_contador}}!

Identificamos mensalidade(s) em aberto em seu registro:

💰 *Valor:* R$ {{valor_total}}
📅 *Vencimento:* {{data_vencimento}}
📋 *Registro:* {{numero_registro}}

📎 Boleto em anexo para pagamento.

Em caso de dúvidas, entre em contato conosco.

*CRC-ES*''',
                has_attachment=True,
                attachment_type='document',
                attachment_caption='Boleto para pagamento',
                created_by=admin_user.id
            )
            whatsapp_template.set_available_variables([
                'nome_contador', 'valor_total', 'data_vencimento', 'numero_registro'
            ])
            db.session.add(whatsapp_template)
        except Exception as e:
            print(f"Erro ao criar template de WhatsApp: {e}")
        
        db.session.commit()
        
        print("Templates de exemplo criados!")
        
        # Registra log de inicialização
        try:
            AuditLog.log_action(
                user_id=admin_user.id,
                username=admin_user.username,
                action_type='SYSTEM_INIT',
                resource_type='Database',
                resource_id='system',
                new_values={'initialized': True},
                ip_address='127.0.0.1',
                user_agent='System',
                endpoint='init_db',
                method='SCRIPT',
                success=True
            )
        except Exception as e:
            print(f"Erro ao criar log de auditoria: {e}")
        
        print("✅ Banco de dados inicializado com sucesso!")
        print("\n📋 Informações de acesso:")
        print("   Usuário: admin")
        print("   Senha: admin123")
        print("   ⚠️  IMPORTANTE: Altere a senha padrão após o primeiro login!")

if __name__ == '__main__':
    init_database()

