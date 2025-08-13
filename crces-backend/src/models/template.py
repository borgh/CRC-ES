from datetime import datetime
import json
import re
from .user import db

class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Conteúdo do template
    subject = db.Column(db.String(500), nullable=False)
    html_content = db.Column(db.Text, nullable=False)
    text_content = db.Column(db.Text, nullable=True)  # Versão texto alternativa
    
    # Variáveis disponíveis (JSON)
    available_variables = db.Column(db.Text, nullable=True)  # JSON array
    
    # Controle de versão
    version = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)  # Removido FK temporariamente
    
    # Relacionamentos (removidos para evitar referências circulares)
    # created_by_user = db.relationship('User', backref='email_templates')

    def get_available_variables(self):
        """Retorna as variáveis disponíveis como lista"""
        if self.available_variables:
            return json.loads(self.available_variables)
        return []

    def set_available_variables(self, variables):
        """Define as variáveis disponíveis"""
        self.available_variables = json.dumps(variables)

    def extract_variables_from_content(self):
        """Extrai automaticamente as variáveis do conteúdo do template"""
        # Busca por padrões como {{variable}} ou {variable}
        pattern = r'\{\{?\s*(\w+)\s*\}?\}'
        
        variables = set()
        
        # Busca no subject
        variables.update(re.findall(pattern, self.subject))
        
        # Busca no HTML content
        variables.update(re.findall(pattern, self.html_content))
        
        # Busca no text content se existir
        if self.text_content:
            variables.update(re.findall(pattern, self.text_content))
        
        return list(variables)

    def render(self, variables=None):
        """Renderiza o template com as variáveis fornecidas"""
        if variables is None:
            variables = {}
        
        rendered_subject = self.subject
        rendered_html = self.html_content
        rendered_text = self.text_content
        
        # Substitui variáveis no formato {{variable}} e {variable}
        for var_name, var_value in variables.items():
            # Converte valor para string se não for
            str_value = str(var_value) if var_value is not None else ''
            
            # Substitui ambos os formatos
            rendered_subject = rendered_subject.replace(f'{{{{{var_name}}}}}', str_value)
            rendered_subject = rendered_subject.replace(f'{{{var_name}}}', str_value)
            
            rendered_html = rendered_html.replace(f'{{{{{var_name}}}}}', str_value)
            rendered_html = rendered_html.replace(f'{{{var_name}}}', str_value)
            
            if rendered_text:
                rendered_text = rendered_text.replace(f'{{{{{var_name}}}}}', str_value)
                rendered_text = rendered_text.replace(f'{{{var_name}}}', str_value)
        
        return {
            'subject': rendered_subject,
            'html_content': rendered_html,
            'text_content': rendered_text
        }

    def validate_template(self):
        """Valida se o template está correto"""
        errors = []
        
        if not self.subject.strip():
            errors.append("Subject não pode estar vazio")
        
        if not self.html_content.strip():
            errors.append("Conteúdo HTML não pode estar vazio")
        
        # Verifica se todas as variáveis no template estão na lista de disponíveis
        used_variables = self.extract_variables_from_content()
        available_variables = self.get_available_variables()
        
        for var in used_variables:
            if var not in available_variables:
                errors.append(f"Variável '{var}' não está na lista de variáveis disponíveis")
        
        return errors

    def clone(self, new_name=None, created_by=None):
        """Cria uma cópia do template"""
        clone = EmailTemplate(
            name=new_name or f"{self.name} (Cópia)",
            description=self.description,
            subject=self.subject,
            html_content=self.html_content,
            text_content=self.text_content,
            available_variables=self.available_variables,
            created_by=created_by or self.created_by
        )
        return clone

    def to_dict(self, include_content=True):
        """Converte o template para dicionário"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'is_active': self.is_active,
            'available_variables': self.get_available_variables(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by
        }
        
        if include_content:
            data.update({
                'subject': self.subject,
                'html_content': self.html_content,
                'text_content': self.text_content
            })
        
        return data

    def __repr__(self):
        return f'<EmailTemplate {self.name}>'


class WhatsAppTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Conteúdo do template
    message_content = db.Column(db.Text, nullable=False)
    
    # Configurações de anexo
    has_attachment = db.Column(db.Boolean, default=False)
    attachment_type = db.Column(db.String(50), nullable=True)  # 'document', 'image', 'video', 'audio'
    attachment_caption = db.Column(db.String(1000), nullable=True)
    
    # Variáveis disponíveis (JSON)
    available_variables = db.Column(db.Text, nullable=True)  # JSON array
    
    # Controle de versão
    version = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)  # Removido FK temporariamente
    
    # Relacionamentos (removidos para evitar referências circulares)
    # created_by_user = db.relationship('User', backref='whatsapp_templates')

    def get_available_variables(self):
        """Retorna as variáveis disponíveis como lista"""
        if self.available_variables:
            return json.loads(self.available_variables)
        return []

    def set_available_variables(self, variables):
        """Define as variáveis disponíveis"""
        self.available_variables = json.dumps(variables)

    def extract_variables_from_content(self):
        """Extrai automaticamente as variáveis do conteúdo do template"""
        # Busca por padrões como {{variable}} ou {variable}
        pattern = r'\{\{?\s*(\w+)\s*\}?\}'
        
        variables = set()
        
        # Busca no message content
        variables.update(re.findall(pattern, self.message_content))
        
        # Busca no attachment caption se existir
        if self.attachment_caption:
            variables.update(re.findall(pattern, self.attachment_caption))
        
        return list(variables)

    def render(self, variables=None):
        """Renderiza o template com as variáveis fornecidas"""
        if variables is None:
            variables = {}
        
        rendered_message = self.message_content
        rendered_caption = self.attachment_caption
        
        # Substitui variáveis no formato {{variable}} e {variable}
        for var_name, var_value in variables.items():
            # Converte valor para string se não for
            str_value = str(var_value) if var_value is not None else ''
            
            # Substitui ambos os formatos
            rendered_message = rendered_message.replace(f'{{{{{var_name}}}}}', str_value)
            rendered_message = rendered_message.replace(f'{{{var_name}}}', str_value)
            
            if rendered_caption:
                rendered_caption = rendered_caption.replace(f'{{{{{var_name}}}}}', str_value)
                rendered_caption = rendered_caption.replace(f'{{{var_name}}}', str_value)
        
        return {
            'message_content': rendered_message,
            'attachment_caption': rendered_caption,
            'has_attachment': self.has_attachment,
            'attachment_type': self.attachment_type
        }

    def validate_template(self):
        """Valida se o template está correto"""
        errors = []
        
        if not self.message_content.strip():
            errors.append("Conteúdo da mensagem não pode estar vazio")
        
        # Verifica limite de caracteres do WhatsApp (4096 caracteres)
        if len(self.message_content) > 4096:
            errors.append("Mensagem excede o limite de 4096 caracteres do WhatsApp")
        
        # Verifica se todas as variáveis no template estão na lista de disponíveis
        used_variables = self.extract_variables_from_content()
        available_variables = self.get_available_variables()
        
        for var in used_variables:
            if var not in available_variables:
                errors.append(f"Variável '{var}' não está na lista de variáveis disponíveis")
        
        # Validações específicas de anexo
        if self.has_attachment:
            if not self.attachment_type:
                errors.append("Tipo de anexo deve ser especificado quando has_attachment é True")
            elif self.attachment_type not in ['document', 'image', 'video', 'audio']:
                errors.append("Tipo de anexo deve ser: document, image, video ou audio")
        
        return errors

    def clone(self, new_name=None, created_by=None):
        """Cria uma cópia do template"""
        clone = WhatsAppTemplate(
            name=new_name or f"{self.name} (Cópia)",
            description=self.description,
            message_content=self.message_content,
            has_attachment=self.has_attachment,
            attachment_type=self.attachment_type,
            attachment_caption=self.attachment_caption,
            available_variables=self.available_variables,
            created_by=created_by or self.created_by
        )
        return clone

    def to_dict(self, include_content=True):
        """Converte o template para dicionário"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'is_active': self.is_active,
            'has_attachment': self.has_attachment,
            'attachment_type': self.attachment_type,
            'available_variables': self.get_available_variables(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by
        }
        
        if include_content:
            data.update({
                'message_content': self.message_content,
                'attachment_caption': self.attachment_caption
            })
        
        return data

    def __repr__(self):
        return f'<WhatsAppTemplate {self.name}>'

