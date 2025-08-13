"""
Rotas de contatos baseadas nas tabelas originais
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models.contact import Contact
from ..models.audit import AuditLog, ActionType
from ..services.auth_service import AuthService
from ..config.database import db_config, db
import pandas as pd

contacts_bp = Blueprint('contacts', __name__)

@contacts_bp.route('/', methods=['GET'])
@jwt_required()
def get_contacts():
    """Lista todos os contatos"""
    try:
        # Parâmetros de filtro
        search = request.args.get('search', '')
        has_email = request.args.get('has_email', '').lower() == 'true'
        has_phone = request.args.get('has_phone', '').lower() == 'true'
        has_debts = request.args.get('has_debts', '').lower() == 'true'
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Query base
        query = Contact.query
        
        # Aplicar filtros
        if search:
            query = query.filter(
                db.or_(
                    Contact.nome.ilike(f'%{search}%'),
                    Contact.registro.ilike(f'%{search}%'),
                    Contact.email.ilike(f'%{search}%')
                )
            )
        
        if has_email:
            query = query.filter(Contact.email.isnot(None))
        
        if has_phone:
            query = query.filter(Contact.telefone_completo.isnot(None))
        
        if has_debts:
            query = query.filter(Contact.tem_debitos == True)
        
        # Ordenar por nome
        query = query.order_by(Contact.nome)
        
        # Paginação
        contacts = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'contacts': [contact.to_dict() for contact in contacts.items],
                'total': contacts.total,
                'pages': contacts.pages,
                'current_page': page,
                'per_page': per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@contacts_bp.route('/<int:contact_id>', methods=['GET'])
@jwt_required()
def get_contact(contact_id):
    """Obtém contato específico"""
    try:
        contact = Contact.query.get(contact_id)
        
        if not contact:
            return jsonify({
                'success': False,
                'message': 'Contato não encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': contact.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@contacts_bp.route('/sync', methods=['POST'])
@jwt_required()
def sync_contacts():
    """Sincroniza contatos do SQL Server original"""
    try:
        current_user_id = get_jwt_identity()
        current_user_data = AuthService.get_current_user(current_user_id)
        
        if not current_user_data or not current_user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        # Sincronizar contatos
        sync_count, message = Contact.sync_from_sql_server(db_config)
        
        # Log da sincronização
        AuditLog.log_action(
            user_id=current_user_id,
            action=ActionType.SYNC_DATA,
            resource_type='contact',
            description=f"Sincronização de contatos: {message}",
            details={'sync_count': sync_count},
            success=sync_count > 0
        )
        
        return jsonify({
            'success': sync_count > 0,
            'message': message,
            'data': {'sync_count': sync_count}
        }), 200 if sync_count > 0 else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@contacts_bp.route('/devedores', methods=['GET'])
@jwt_required()
def get_devedores():
    """Obtém lista de devedores (baseado no script LEMBRETE_VENCIMENTO.py)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Query baseada no script original
        query = """
        SET DATEFORMAT DMY 
        SELECT a2.[Nome], a2.[Num. Registro], a1.[DDD], a1.[Telefone] 
        FROM SCDA71 a1, SCDA01 a2  
        WHERE 
        ((a2.[Num. Registro]=a1.[Num. Registro] AND a1.[Telefone Ativo]='SIM' AND a1.[Tipo Telefone]='3' AND a1.DDD<>'') 
        OR 
        (a2.[Num. Registro]=a1.[Num. Registro] AND a1.[Telefone Ativo]='SIM' AND a1.[Telefone] LIKE '9%' AND a1.DDD<>'')) 
        AND a2.[Num. Registro] IN (
            SELECT DISTINCT [Num. Registro] FROM SFNA01 
            WHERE [Parcela]<>'0' AND [Data Vencimento] < GETDATE()
        )
        ORDER BY a1.[Num. Registro]
        """
        
        try:
            df = db_config.execute_query(query)
            
            if df.empty:
                return jsonify({
                    'success': True,
                    'data': [],
                    'message': 'Nenhum devedor encontrado'
                }), 200
            
            # Processar dados como no script original
            devedores = []
            for _, row in df.iterrows():
                # Limpar dados
                ddd = str(row['DDD']).replace(' ', '') if pd.notna(row['DDD']) else ''
                telefone = str(row['Telefone']).replace('-', '') if pd.notna(row['Telefone']) else ''
                
                # Lógica do script original para adicionar 9
                if ddd and len(ddd) <= 2:
                    try:
                        if int(ddd) <= 29 and len(telefone) <= 8:
                            telefone = '9' + telefone
                    except:
                        pass
                
                # Número completo
                telefone_completo = f"55{ddd}{telefone}" if ddd and telefone else None
                
                devedores.append({
                    'nome': row['Nome'],
                    'registro': row['Num. Registro'],
                    'ddd': ddd,
                    'telefone': telefone,
                    'telefone_completo': telefone_completo
                })
            
            # Log da consulta
            AuditLog.log_action(
                user_id=current_user_id,
                action=ActionType.SYNC_DATA,
                resource_type='devedores',
                description=f"Consulta de devedores: {len(devedores)} encontrados",
                details={'count': len(devedores)},
                success=True
            )
            
            return jsonify({
                'success': True,
                'data': devedores,
                'message': f'{len(devedores)} devedores encontrados'
            }), 200
            
        except Exception as e:
            # Fallback para dados locais
            devedores_locais = Contact.query.filter_by(tem_debitos=True).all()
            
            return jsonify({
                'success': True,
                'data': [contact.to_dict() for contact in devedores_locais],
                'message': f'{len(devedores_locais)} devedores encontrados (dados locais)',
                'fallback': True
            }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@contacts_bp.route('/anuidade', methods=['GET'])
@jwt_required()
def get_anuidade_contacts():
    """Obtém contatos para envio de anuidade (baseado no script ENVIO BOLETO EMAIL.py)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Query baseada no script original
        query = """
        SET DATEFORMAT DMY 
        SELECT DISTINCT a1.Nome, a1.[Num. Registro], a1.[E-Mail] 
        FROM SCDA01 a1, SFNA01 a2
        WHERE a1.[Num. Registro]=a2.[Num. Registro] 
        AND a2.[Codigo Debito] LIKE '24%' 
        AND a2.Parcela ='0'
        """
        
        try:
            df = db_config.execute_query(query)
            
            if df.empty:
                return jsonify({
                    'success': True,
                    'data': [],
                    'message': 'Nenhum contato de anuidade encontrado'
                }), 200
            
            # Processar dados
            contatos = []
            for _, row in df.iterrows():
                if pd.notna(row['E-Mail']) and row['E-Mail'].strip():
                    contatos.append({
                        'nome': row['Nome'],
                        'registro': row['Num. Registro'],
                        'email': row['E-Mail']
                    })
            
            # Log da consulta
            AuditLog.log_action(
                user_id=current_user_id,
                action=ActionType.SYNC_DATA,
                resource_type='anuidade_contacts',
                description=f"Consulta de contatos anuidade: {len(contatos)} encontrados",
                details={'count': len(contatos)},
                success=True
            )
            
            return jsonify({
                'success': True,
                'data': contatos,
                'message': f'{len(contatos)} contatos de anuidade encontrados'
            }), 200
            
        except Exception as e:
            # Fallback para dados locais
            contatos_locais = Contact.query.filter(
                Contact.email.isnot(None),
                Contact.email != ''
            ).all()
            
            return jsonify({
                'success': True,
                'data': [contact.to_dict() for contact in contatos_locais],
                'message': f'{len(contatos_locais)} contatos encontrados (dados locais)',
                'fallback': True
            }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@contacts_bp.route('/search-by-phone', methods=['POST'])
@jwt_required()
def search_by_phone():
    """Busca contato por telefone (baseado no script BOLETO_ANUIDADE.py)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        phone = data.get('phone', '').replace('@c.us', '')
        
        if not phone:
            return jsonify({
                'success': False,
                'message': 'Telefone é obrigatório'
            }), 400
        
        # Processar telefone como no script original
        if len(phone) == 13:
            ddd = phone[2:4]
            telefone1 = phone[5:]
            telefone2 = telefone1[:4] + '-' + telefone1[4:]
        elif len(phone) == 12:
            ddd = phone[2:4]
            telefone1 = phone[4:]
            telefone2 = telefone1[:4] + '-' + telefone1[4:]
        else:
            return jsonify({
                'success': False,
                'message': 'Formato de telefone inválido'
            }), 400
        
        # Query baseada no script original
        query = f"""
        SELECT [Num. Registro] FROM SCDA71
        WHERE SCDA71.[DDD]='{ddd}' 
        AND (SCDA71.[Telefone] LIKE '%{phone}' OR SCDA71.[Telefone] LIKE '%{telefone2}') 
        AND SCDA71.[Telefone Ativo]='SIM'
        """
        
        try:
            df = db_config.execute_query(query)
            
            if df.empty:
                return jsonify({
                    'success': False,
                    'message': 'Contato não encontrado'
                }), 404
            
            registro = df['Num. Registro'].iloc[0]
            
            # Processar registro como no script original
            registro_limpo = registro.replace('/', '').replace('-', '')
            
            # Log da busca
            AuditLog.log_action(
                user_id=current_user_id,
                action=ActionType.SYNC_DATA,
                resource_type='phone_search',
                description=f"Busca por telefone: {phone}",
                details={'phone': phone, 'registro': registro},
                success=True
            )
            
            return jsonify({
                'success': True,
                'data': {
                    'registro': registro,
                    'registro_limpo': registro_limpo
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro na consulta: {e}'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@contacts_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_contacts_stats():
    """Obtém estatísticas dos contatos"""
    try:
        stats = {
            'total': Contact.query.count(),
            'with_email': Contact.query.filter(Contact.email.isnot(None)).count(),
            'with_phone': Contact.query.filter(Contact.telefone_completo.isnot(None)).count(),
            'with_debts': Contact.query.filter_by(tem_debitos=True).count(),
            'active_phones': Contact.query.filter_by(telefone_ativo=True).count(),
            'last_sync': None
        }
        
        # Data da última sincronização
        last_sync_contact = Contact.query.filter(
            Contact.last_sync.isnot(None)
        ).order_by(Contact.last_sync.desc()).first()
        
        if last_sync_contact:
            stats['last_sync'] = last_sync_contact.last_sync.isoformat()
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

