"""
Rotas de templates de mensagens
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models.template import Template, TemplateType
from ..models.audit import AuditLog, ActionType
from ..services.auth_service import AuthService
from ..config.database import db

templates_bp = Blueprint('templates', __name__)

@templates_bp.route('/', methods=['GET'])
@jwt_required()
def get_templates():
    """Lista todos os templates"""
    try:
        # Parâmetros de filtro
        type_filter = request.args.get('type')
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Query base
        query = Template.query
        
        # Aplicar filtros
        if type_filter:
            query = query.filter(Template.type == TemplateType(type_filter))
        
        if active_only:
            query = query.filter(Template.is_active == True)
        
        # Ordenar por data de criação
        query = query.order_by(Template.created_at.desc())
        
        # Paginação
        templates = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'templates': [template.to_dict() for template in templates.items],
                'total': templates.total,
                'pages': templates.pages,
                'current_page': page,
                'per_page': per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@templates_bp.route('/', methods=['POST'])
@jwt_required()
def create_template():
    """Cria novo template"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['name', 'type', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Campo {field} é obrigatório'
                }), 400
        
        # Criar template
        template = Template(
            name=data['name'],
            type=TemplateType(data['type']),
            subject=data.get('subject', ''),
            content=data['content'],
            variables=data.get('variables', Template.get_default_variables()),
            is_active=data.get('is_active', True),
            created_by=current_user_id
        )
        
        db.session.add(template)
        db.session.commit()
        
        # Log da criação
        AuditLog.log_action(
            user_id=current_user_id,
            action=ActionType.CREATE,
            resource_type='template',
            resource_id=str(template.id),
            description=f"Template criado: {template.name}",
            details=data,
            success=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Template criado com sucesso',
            'data': template.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@templates_bp.route('/<int:template_id>', methods=['GET'])
@jwt_required()
def get_template(template_id):
    """Obtém template específico"""
    try:
        template = Template.query.get(template_id)
        
        if not template:
            return jsonify({
                'success': False,
                'message': 'Template não encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': template.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@templates_bp.route('/<int:template_id>', methods=['PUT'])
@jwt_required()
def update_template(template_id):
    """Atualiza template"""
    try:
        current_user_id = get_jwt_identity()
        template = Template.query.get(template_id)
        
        if not template:
            return jsonify({
                'success': False,
                'message': 'Template não encontrado'
            }), 404
        
        data = request.get_json()
        
        # Atualizar campos
        if 'name' in data:
            template.name = data['name']
        if 'subject' in data:
            template.subject = data['subject']
        if 'content' in data:
            template.content = data['content']
        if 'variables' in data:
            template.variables = data['variables']
        if 'is_active' in data:
            template.is_active = data['is_active']
        
        template.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log da atualização
        AuditLog.log_action(
            user_id=current_user_id,
            action=ActionType.UPDATE,
            resource_type='template',
            resource_id=str(template.id),
            description=f"Template atualizado: {template.name}",
            details=data,
            success=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Template atualizado com sucesso',
            'data': template.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@templates_bp.route('/<int:template_id>', methods=['DELETE'])
@jwt_required()
def delete_template(template_id):
    """Exclui template"""
    try:
        current_user_id = get_jwt_identity()
        template = Template.query.get(template_id)
        
        if not template:
            return jsonify({
                'success': False,
                'message': 'Template não encontrado'
            }), 404
        
        template_name = template.name
        
        db.session.delete(template)
        db.session.commit()
        
        # Log da exclusão
        AuditLog.log_action(
            user_id=current_user_id,
            action=ActionType.DELETE,
            resource_type='template',
            resource_id=str(template_id),
            description=f"Template excluído: {template_name}",
            success=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Template excluído com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@templates_bp.route('/<int:template_id>/preview', methods=['POST'])
@jwt_required()
def preview_template(template_id):
    """Visualiza template com dados de exemplo"""
    try:
        template = Template.query.get(template_id)
        
        if not template:
            return jsonify({
                'success': False,
                'message': 'Template não encontrado'
            }), 404
        
        # Dados de exemplo para preview
        sample_data = request.get_json() or {
            'nome': 'João Silva',
            'registro': 'RJ-123456/O',
            'email': 'joao@exemplo.com',
            'telefone': '21987654321',
            'ddd': '21',
            'data_vencimento': '31/03/2024',
            'valor': 'R$ 450,00',
            'codigo_debito': '2301',
            'parcela': '0'
        }
        
        # Renderizar template
        rendered = template.render(sample_data)
        
        return jsonify({
            'success': True,
            'data': {
                'template': template.to_dict(),
                'rendered': rendered,
                'sample_data': sample_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@templates_bp.route('/variables', methods=['GET'])
@jwt_required()
def get_available_variables():
    """Obtém variáveis disponíveis para templates"""
    try:
        variables = Template.get_default_variables()
        
        # Descrições das variáveis
        variable_descriptions = {
            'nome': 'Nome completo do profissional',
            'registro': 'Número de registro no CRC (ex: RJ-123456/O)',
            'email': 'Endereço de email',
            'telefone': 'Número de telefone completo',
            'ddd': 'Código DDD',
            'data_vencimento': 'Data de vencimento do débito',
            'valor': 'Valor do débito',
            'codigo_debito': 'Código do tipo de débito',
            'parcela': 'Número da parcela (0 = à vista)'
        }
        
        variables_with_desc = [
            {
                'name': var,
                'placeholder': '{' + var + '}',
                'description': variable_descriptions.get(var, 'Variável do sistema')
            }
            for var in variables
        ]
        
        return jsonify({
            'success': True,
            'data': variables_with_desc
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@templates_bp.route('/defaults', methods=['POST'])
@jwt_required()
def create_default_templates():
    """Cria templates padrão do sistema"""
    try:
        current_user_id = get_jwt_identity()
        
        # Template de email de anuidade (baseado no script original)
        email_template = Template(
            name='Anuidade 2024 - Email',
            type=TemplateType.EMAIL,
            subject='ANUIDADE DE 2024 - CRCES',
            content="""<p>Prezado(a) {nome}, bom dia.</p>

<p>Através do boleto abaixo você poderá realizar o pagamento integral da anuidade de 2024 com vencimento para até o dia 31/03/2024.</p>

<p>Estando em dia com o Conselho, você garante os seguintes benefícios:</p>

<p>- Emissão gratuita de Certificado Digital do tipo A1, com validade de 1 ano;</p>
<p>- Acesso à credencial do Sesc ES com condições especiais;</p>
<p>- Descontos e benefícios em instituições de ensino parceiras;</p>
<p>- Parceria com Administradoras de planos de saúde (ass. Médica e Hospitalar) e planos odontológicos com tabela de preços diferenciada;</p>
<p>- Capacitações gratuitas;</p>
<p>- Acesso gratuito ao Espaço Compartilhado do Profissional da Contabilidade (Co-Working);</p>

<p>Caso queira efetuar o parcelamento, acesse o portal do CRCES, e clique no banner exclusivo para anuidade de 2024.</p>

<p>Para tirar suas dúvidas, entre em contato pelo Whatsapp no número (27) 3232-1600 (SOMENTE MENSAGENS), e-mail: atendimento@crc-es.org.br ou pelos telefones de contato (27) 3232-1607 / 1611 / 1626/ 1641.</p>

<p><strong>A SENHA DE ABERTURA DO ARQUIVO SÃO OS 3 PRIMEIROS DIGITOS DO SEU CPF.</strong></p>

<p>Atenciosamente</p>
<p>ENVIADO AUTOMATICAMENTE</p>""",
            variables=Template.get_default_variables(),
            created_by=current_user_id
        )
        
        # Template de WhatsApp de anuidade (baseado no script original)
        whatsapp_template = Template(
            name='Anuidade 2024 - WhatsApp',
            type=TemplateType.WHATSAPP,
            content='Prezado {nome}, segue boleto da anuidade de 2024. A senha para abertura do arquivo são os 3 primeiros digitos do seu CPF. Aproveite o desconto para pagamento à vista.',
            variables=Template.get_default_variables(),
            created_by=current_user_id
        )
        
        # Template de lembrete de vencimento
        lembrete_template = Template(
            name='Lembrete de Vencimento - WhatsApp',
            type=TemplateType.WHATSAPP,
            content='Prezado {nome}, lembramos que você possui débitos em aberto no CRC-ES. Para regularizar sua situação, entre em contato conosco pelo telefone (27) 3232-1600 ou acesse nosso portal.',
            variables=Template.get_default_variables(),
            created_by=current_user_id
        )
        
        templates_to_create = [email_template, whatsapp_template, lembrete_template]
        created_templates = []
        
        for template in templates_to_create:
            # Verificar se já existe
            existing = Template.query.filter_by(name=template.name).first()
            if not existing:
                db.session.add(template)
                created_templates.append(template)
        
        db.session.commit()
        
        # Log da criação
        if created_templates:
            AuditLog.log_action(
                user_id=current_user_id,
                action=ActionType.CREATE,
                resource_type='template',
                description=f"Templates padrão criados: {len(created_templates)}",
                details={'templates': [t.name for t in created_templates]},
                success=True
            )
        
        return jsonify({
            'success': True,
            'message': f'{len(created_templates)} templates padrão criados',
            'data': [t.to_dict() for t in created_templates]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

