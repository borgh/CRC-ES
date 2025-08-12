"""
Rotas de templates do sistema CRC-ES
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.database import Template, db, AuditLog
from datetime import datetime
import json

templates_bp = Blueprint('templates', __name__)

@templates_bp.route('/', methods=['GET'])
@jwt_required()
def get_templates():
    """Listar templates"""
    try:
        template_type = request.args.get('type')  # Filtrar por tipo
        
        query = Template.query.filter_by(active=True)
        
        if template_type:
            query = query.filter_by(type=template_type)
        
        templates = query.order_by(Template.created_at.desc()).all()
        
        return jsonify({
            'templates': [template.to_dict() for template in templates]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@templates_bp.route('/', methods=['POST'])
@jwt_required()
def create_template():
    """Criar novo template"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        name = data.get('name')
        template_type = data.get('type')  # 'email' ou 'whatsapp'
        subject = data.get('subject', '')  # Para emails
        content = data.get('content')
        variables = data.get('variables', [])
        
        if not name or not template_type or not content:
            return jsonify({'error': 'Nome, tipo e conteúdo são obrigatórios'}), 400
        
        if template_type not in ['email', 'whatsapp']:
            return jsonify({'error': 'Tipo deve ser email ou whatsapp'}), 400
        
        # Criar template
        template = Template(
            name=name,
            type=template_type,
            subject=subject,
            content=content,
            variables=json.dumps(variables) if variables else None,
            created_by=user_id
        )
        
        db.session.add(template)
        db.session.commit()
        
        # Log da criação
        audit_log = AuditLog(
            user_id=user_id,
            action='template_created',
            resource='template',
            resource_id=template.id,
            details=f'Template criado: {name}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Template criado com sucesso',
            'template': template.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@templates_bp.route('/<int:template_id>', methods=['GET'])
@jwt_required()
def get_template(template_id):
    """Obter template específico"""
    try:
        template = Template.query.get(template_id)
        
        if not template:
            return jsonify({'error': 'Template não encontrado'}), 404
        
        return jsonify({'template': template.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@templates_bp.route('/<int:template_id>', methods=['PUT'])
@jwt_required()
def update_template(template_id):
    """Atualizar template"""
    try:
        user_id = get_jwt_identity()
        template = Template.query.get(template_id)
        
        if not template:
            return jsonify({'error': 'Template não encontrado'}), 404
        
        data = request.get_json()
        
        # Atualizar campos
        if 'name' in data:
            template.name = data['name']
        if 'subject' in data:
            template.subject = data['subject']
        if 'content' in data:
            template.content = data['content']
        if 'variables' in data:
            template.variables = json.dumps(data['variables'])
        if 'active' in data:
            template.active = data['active']
        
        template.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log da atualização
        audit_log = AuditLog(
            user_id=user_id,
            action='template_updated',
            resource='template',
            resource_id=template.id,
            details=f'Template atualizado: {template.name}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Template atualizado com sucesso',
            'template': template.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@templates_bp.route('/<int:template_id>', methods=['DELETE'])
@jwt_required()
def delete_template(template_id):
    """Deletar template (soft delete)"""
    try:
        user_id = get_jwt_identity()
        template = Template.query.get(template_id)
        
        if not template:
            return jsonify({'error': 'Template não encontrado'}), 404
        
        template_name = template.name
        
        # Soft delete
        template.active = False
        db.session.commit()
        
        # Log da exclusão
        audit_log = AuditLog(
            user_id=user_id,
            action='template_deleted',
            resource='template',
            resource_id=template_id,
            details=f'Template deletado: {template_name}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({'message': 'Template deletado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@templates_bp.route('/default', methods=['GET'])
@jwt_required()
def get_default_templates():
    """Obter templates padrão do sistema"""
    try:
        default_templates = {
            'email': {
                'anuidade': {
                    'name': 'Anuidade CRC-ES',
                    'subject': 'ANUIDADE DE {year} - CRCES',
                    'content': '''
                    <p>Prezado(a) {nome}, bom dia.</p>
                    
                    <p>Através do boleto abaixo você poderá realizar o pagamento integral da anuidade de {year}.</p>
                    
                    <p>Estando em dia com o Conselho, você garante os seguintes benefícios:</p>
                    <ul>
                        <li>Emissão gratuita de Certificado Digital do tipo A1, com validade de 1 ano;</li>
                        <li>Acesso à credencial do Sesc ES com condições especiais;</li>
                        <li>Descontos e benefícios em instituições de ensino parceiras;</li>
                        <li>Capacitações gratuitas;</li>
                    </ul>
                    
                    <p><strong>A SENHA DE ABERTURA DO ARQUIVO SÃO OS 3 PRIMEIROS DÍGITOS DO SEU CPF.</strong></p>
                    
                    <p>Atenciosamente<br>CRC-ES</p>
                    ''',
                    'variables': ['nome', 'year', 'registro']
                }
            },
            'whatsapp': {
                'anuidade': {
                    'name': 'Anuidade WhatsApp',
                    'content': 'Prezado {nome}, segue boleto da anuidade de {year}. A senha para abertura do arquivo são os 3 primeiros dígitos do seu CPF.',
                    'variables': ['nome', 'year']
                }
            }
        }
        
        return jsonify({'default_templates': default_templates}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

