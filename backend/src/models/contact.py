"""
Modelo de contatos baseado nas tabelas originais
"""
from datetime import datetime
from ..config.database import db

class Contact(db.Model):
    """Contatos baseados nas tabelas SCDA01 e SCDA71"""
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Dados da SCDA01
    registro = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    
    # Dados da SCDA71
    ddd = db.Column(db.String(3))
    telefone = db.Column(db.String(20))
    telefone_completo = db.Column(db.String(25))  # 55 + DDD + Telefone
    telefone_ativo = db.Column(db.Boolean, default=True)
    tipo_telefone = db.Column(db.String(10))
    
    # Dados financeiros (SFNA01)
    tem_debitos = db.Column(db.Boolean, default=False)
    ultima_atualizacao_financeira = db.Column(db.DateTime)
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync = db.Column(db.DateTime)  # Última sincronização com SQL Server
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'registro': self.registro,
            'nome': self.nome,
            'email': self.email,
            'ddd': self.ddd,
            'telefone': self.telefone,
            'telefone_completo': self.telefone_completo,
            'telefone_ativo': self.telefone_ativo,
            'tipo_telefone': self.tipo_telefone,
            'tem_debitos': self.tem_debitos,
            'ultima_atualizacao_financeira': self.ultima_atualizacao_financeira.isoformat() if self.ultima_atualizacao_financeira else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None
        }
    
    @classmethod
    def sync_from_sql_server(cls, db_config):
        """Sincroniza contatos do SQL Server original"""
        try:
            # Query baseada nos scripts originais
            query = """
            SELECT DISTINCT 
                a1.[Num. Registro] as registro,
                a1.[Nome] as nome,
                a1.[E-Mail] as email,
                a2.[DDD] as ddd,
                a2.[Telefone] as telefone,
                a2.[Telefone Ativo] as telefone_ativo,
                a2.[Tipo Telefone] as tipo_telefone
            FROM SCDA01 a1
            LEFT JOIN SCDA71 a2 ON a1.[Num. Registro] = a2.[Num. Registro]
            WHERE a1.[Nome] IS NOT NULL
            """
            
            df = db_config.execute_query(query)
            
            if df.empty:
                return 0, "Nenhum contato encontrado"
            
            sync_count = 0
            for _, row in df.iterrows():
                # Processar telefone como nos scripts originais
                telefone_completo = None
                if pd.notna(row['ddd']) and pd.notna(row['telefone']):
                    ddd = str(row['ddd']).replace(' ', '').replace('-', '')
                    telefone = str(row['telefone']).replace(' ', '').replace('-', '')
                    
                    # Lógica dos scripts originais
                    if len(ddd) <= 2 and int(ddd) <= 29:
                        if len(telefone) <= 8:
                            telefone = '9' + telefone
                    
                    telefone_completo = f"55{ddd}{telefone}"
                
                # Buscar ou criar contato
                contact = cls.query.filter_by(registro=row['registro']).first()
                if not contact:
                    contact = cls(registro=row['registro'])
                    db.session.add(contact)
                
                # Atualizar dados
                contact.nome = row['nome']
                contact.email = row['email'] if pd.notna(row['email']) else None
                contact.ddd = ddd if 'ddd' in locals() else None
                contact.telefone = telefone if 'telefone' in locals() else None
                contact.telefone_completo = telefone_completo
                contact.telefone_ativo = row['telefone_ativo'] == 'SIM' if pd.notna(row['telefone_ativo']) else False
                contact.tipo_telefone = row['tipo_telefone'] if pd.notna(row['tipo_telefone']) else None
                contact.last_sync = datetime.utcnow()
                
                sync_count += 1
            
            db.session.commit()
            return sync_count, f"Sincronizados {sync_count} contatos"
            
        except Exception as e:
            db.session.rollback()
            return 0, f"Erro na sincronização: {e}"
    
    def __repr__(self):
        return f'<Contact {self.registro} - {self.nome}>'

