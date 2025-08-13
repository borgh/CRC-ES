"""
Rotas de auditoria e logs do sistema
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from ..models.audit import AuditLog, ActionType
from ..services.auth_service import AuthService

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/', methods=['GET'])
@jwt_required()
def get_audit_logs():
    """Lista logs de auditoria"""
    try:
        current_user_id = get_jwt_identity()
        current_user_data = AuthService.get_current_user(current_user_id)
        
        if not current_user_data or not current_user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        # Parâmetros de filtro
        action = request.args.get('action')
        resource_type = request.args.get('resource_type')
        user_id = request.args.get('user_id')
        success_only = request.args.get('success_only', '').lower() == 'true'
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Query base
        query = AuditLog.query
        
        # Aplicar filtros
        if action:
            try:
                query = query.filter(AuditLog.action == ActionType(action))
            except ValueError:
                pass
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        if user_id:
            query = query.filter(AuditLog.user_id == int(user_id))
        
        if success_only:
            query = query.filter(AuditLog.success == True)
        
        if date_from:
            try:
                date_from_obj = datetime.fromisoformat(date_from)
                query = query.filter(AuditLog.created_at >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.fromisoformat(date_to)
                query = query.filter(AuditLog.created_at <= date_to_obj)
            except ValueError:
                pass
        
        # Ordenar por data (mais recente primeiro)
        query = query.order_by(AuditLog.created_at.desc())
        
        # Paginação
        logs = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'logs': [log.to_dict() for log in logs.items],
                'total': logs.total,
                'pages': logs.pages,
                'current_page': page,
                'per_page': per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@audit_bp.route('/<int:log_id>', methods=['GET'])
@jwt_required()
def get_audit_log(log_id):
    """Obtém log específico"""
    try:
        current_user_id = get_jwt_identity()
        current_user_data = AuthService.get_current_user(current_user_id)
        
        if not current_user_data or not current_user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        log = AuditLog.query.get(log_id)
        
        if not log:
            return jsonify({
                'success': False,
                'message': 'Log não encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': log.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@audit_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_audit_stats():
    """Obtém estatísticas de auditoria"""
    try:
        current_user_id = get_jwt_identity()
        current_user_data = AuthService.get_current_user(current_user_id)
        
        if not current_user_data or not current_user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        # Período para estatísticas (últimos 30 dias)
        date_from = datetime.utcnow() - timedelta(days=30)
        
        # Estatísticas gerais
        total_logs = AuditLog.query.count()
        recent_logs = AuditLog.query.filter(AuditLog.created_at >= date_from).count()
        success_logs = AuditLog.query.filter(AuditLog.success == True).count()
        failed_logs = AuditLog.query.filter(AuditLog.success == False).count()
        
        # Ações mais comuns
        from sqlalchemy import func
        top_actions = db.session.query(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.created_at >= date_from
        ).group_by(
            AuditLog.action
        ).order_by(
            func.count(AuditLog.id).desc()
        ).limit(10).all()
        
        # Usuários mais ativos
        top_users = db.session.query(
            AuditLog.user_id,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.created_at >= date_from,
            AuditLog.user_id.isnot(None)
        ).group_by(
            AuditLog.user_id
        ).order_by(
            func.count(AuditLog.id).desc()
        ).limit(10).all()
        
        # Recursos mais acessados
        top_resources = db.session.query(
            AuditLog.resource_type,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.created_at >= date_from,
            AuditLog.resource_type.isnot(None)
        ).group_by(
            AuditLog.resource_type
        ).order_by(
            func.count(AuditLog.id).desc()
        ).limit(10).all()
        
        # Atividade por dia (últimos 7 dias)
        daily_activity = []
        for i in range(7):
            day_start = (datetime.utcnow() - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            count = AuditLog.query.filter(
                AuditLog.created_at >= day_start,
                AuditLog.created_at < day_end
            ).count()
            
            daily_activity.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'count': count
            })
        
        daily_activity.reverse()  # Ordem cronológica
        
        stats = {
            'total_logs': total_logs,
            'recent_logs': recent_logs,
            'success_logs': success_logs,
            'failed_logs': failed_logs,
            'success_rate': round((success_logs / total_logs * 100) if total_logs > 0 else 0, 2),
            'top_actions': [
                {
                    'action': action.value if action else 'unknown',
                    'count': count
                }
                for action, count in top_actions
            ],
            'top_users': [
                {
                    'user_id': user_id,
                    'count': count
                }
                for user_id, count in top_users
            ],
            'top_resources': [
                {
                    'resource_type': resource_type,
                    'count': count
                }
                for resource_type, count in top_resources
            ],
            'daily_activity': daily_activity
        }
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@audit_bp.route('/actions', methods=['GET'])
@jwt_required()
def get_available_actions():
    """Obtém lista de ações disponíveis para filtro"""
    try:
        current_user_id = get_jwt_identity()
        current_user_data = AuthService.get_current_user(current_user_id)
        
        if not current_user_data or not current_user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        actions = [
            {
                'value': action.value,
                'label': action.value.replace('_', ' ').title()
            }
            for action in ActionType
        ]
        
        return jsonify({
            'success': True,
            'data': actions
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@audit_bp.route('/export', methods=['POST'])
@jwt_required()
def export_audit_logs():
    """Exporta logs de auditoria"""
    try:
        current_user_id = get_jwt_identity()
        current_user_data = AuthService.get_current_user(current_user_id)
        
        if not current_user_data or not current_user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        data = request.get_json()
        
        # Filtros para exportação
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        actions = data.get('actions', [])
        
        # Query base
        query = AuditLog.query
        
        # Aplicar filtros
        if date_from:
            try:
                date_from_obj = datetime.fromisoformat(date_from)
                query = query.filter(AuditLog.created_at >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.fromisoformat(date_to)
                query = query.filter(AuditLog.created_at <= date_to_obj)
            except ValueError:
                pass
        
        if actions:
            try:
                action_enums = [ActionType(action) for action in actions]
                query = query.filter(AuditLog.action.in_(action_enums))
            except ValueError:
                pass
        
        # Ordenar por data
        query = query.order_by(AuditLog.created_at.desc())
        
        # Limitar a 10000 registros para evitar sobrecarga
        logs = query.limit(10000).all()
        
        # Preparar dados para exportação
        export_data = []
        for log in logs:
            export_data.append({
                'id': log.id,
                'usuario': log.user.username if log.user else 'Sistema',
                'acao': log.action.value if log.action else '',
                'recurso': log.resource_type or '',
                'recurso_id': log.resource_id or '',
                'descricao': log.description or '',
                'sucesso': 'Sim' if log.success else 'Não',
                'erro': log.error_message or '',
                'ip': log.ip_address or '',
                'data_hora': log.created_at.isoformat() if log.created_at else ''
            })
        
        # Log da exportação
        AuditLog.log_action(
            user_id=current_user_id,
            action=ActionType.SYNC_DATA,
            resource_type='audit_export',
            description=f"Exportação de logs de auditoria: {len(export_data)} registros",
            details={'count': len(export_data), 'filters': data},
            success=True
        )
        
        return jsonify({
            'success': True,
            'data': export_data,
            'message': f'{len(export_data)} registros exportados'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

