# 🚀 Sistema CRC-ES - Mensagens em Massa

Sistema completo para envio de mensagens em massa via WhatsApp e Email para o Conselho Regional de Contabilidade do Espírito Santo (CRC-ES).

## ✨ Funcionalidades

### 📧 **Envio de Emails**
- Envio em massa de emails com boletos anexados
- Templates personalizáveis com variáveis dinâmicas
- Configuração SMTP flexível
- Rastreamento de entrega e status

### 📱 **Envio via WhatsApp**
- Integração com WhatsApp Web via Selenium
- Envio automatizado de mensagens e documentos
- Validação de números de telefone
- Controle de velocidade de envio

### 🎯 **Campanhas**
- Criação e gerenciamento de campanhas
- Agendamento de envios
- Relatórios detalhados de performance
- Histórico completo de envios

### 👥 **Gestão de Usuários**
- Sistema de autenticação JWT
- Controle de acesso por perfis
- Auditoria completa de ações
- Logs de segurança

### 🗄️ **Banco de Dados**
- Integração com SQL Server (configuração original)
- Suporte a SQLite para desenvolvimento
- Modelos de dados otimizados
- Backup automático

## 🏗️ Arquitetura

```
CRC-ES/
├── backend/          # API Flask
│   ├── src/
│   │   ├── models/   # Modelos de dados
│   │   ├── routes/   # Endpoints da API
│   │   └── services/ # Serviços de negócio
│   └── requirements.txt
├── frontend/         # Interface React
│   ├── src/
│   │   ├── components/
│   │   └── pages/
│   └── package.json
└── README.md
```

## 🚀 Instalação

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- SQL Server ou SQLite

### Backend (Flask)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
python src/main.py
```

### Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

## ⚙️ Configuração

### Variáveis de Ambiente (.env)
```env
# Banco de dados
DATABASE_URL=sqlite:///app.db
# ou para SQL Server:
# DATABASE_URL=mssql+pyodbc://user:pass@server/database?driver=ODBC+Driver+17+for+SQL+Server

# JWT
SECRET_KEY=sua-chave-secreta
JWT_SECRET_KEY=jwt-chave-secreta

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app

# WhatsApp
WHATSAPP_DELAY=2
WHATSAPP_MAX_RETRIES=3
```

## 📊 Funcionalidades Originais Implementadas

### Scripts Originais Analisados:
- ✅ **ENVIO BOLETO EMAIL.py** - Integrado no serviço de email
- ✅ **ENVIO BOLETO WHATSAPP.py** - Integrado no serviço WhatsApp
- ✅ **BOLETO_ANUIDADE.py** - Lógica de anuidade implementada
- ✅ **LEMBRETE_VENCIMENTO.py** - Sistema de lembretes

### Melhorias Implementadas:
- 🔐 **Segurança**: Autenticação JWT, auditoria completa
- 🎨 **Interface**: Dashboard moderno e responsivo
- 📈 **Relatórios**: Estatísticas em tempo real
- 🔄 **API REST**: Endpoints organizados e documentados
- 🛡️ **Validação**: Validação de dados e tratamento de erros

## 🎯 Uso do Sistema

### 1. Login
- Usuário: `admin`
- Senha: `admin123`

### 2. Dashboard
- Visualização de estatísticas
- Ações rápidas para campanhas
- Monitoramento em tempo real

### 3. Campanhas
- Criar nova campanha
- Selecionar tipo (Email/WhatsApp)
- Escolher template
- Definir destinatários
- Agendar ou enviar imediatamente

### 4. Templates
- Templates para email com HTML
- Templates para WhatsApp
- Variáveis dinâmicas: `{nome}`, `{year}`, `{registro}`

## 🔧 Desenvolvimento

### Estrutura do Backend
```python
# Modelos principais
- User: Usuários do sistema
- Campaign: Campanhas de envio
- Template: Templates de mensagens
- MessageLog: Logs de envio
- AuditLog: Auditoria de ações
```

### Endpoints da API
```
POST /api/auth/login          # Login
GET  /api/campaigns           # Listar campanhas
POST /api/campaigns           # Criar campanha
POST /api/messaging/send      # Enviar mensagens
GET  /api/audit/logs          # Logs de auditoria
```

## 📱 Interface do Usuário

- **Design Responsivo**: Funciona em desktop e mobile
- **Componentes Modernos**: Usando shadcn/ui e Tailwind CSS
- **Navegação Intuitiva**: Sidebar com menu organizado
- **Feedback Visual**: Alertas e notificações em tempo real

## 🔒 Segurança

- **Autenticação JWT**: Tokens seguros com expiração
- **Auditoria Completa**: Todos os logs são registrados
- **Validação de Dados**: Sanitização de inputs
- **Rate Limiting**: Proteção contra spam
- **CORS Configurado**: Acesso controlado

## 📈 Monitoramento

- **Logs Detalhados**: Rastreamento completo de envios
- **Estatísticas**: Métricas de performance
- **Relatórios**: Exportação de dados
- **Alertas**: Notificações de falhas

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

Para suporte técnico ou dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação da API
- Verifique os logs de auditoria

---

**Desenvolvido com ❤️ para o CRC-ES**

*Sistema completo baseado nos scripts originais, com melhorias em segurança, interface e funcionalidades.*

