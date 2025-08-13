# Sistema CRC-ES - Gestão de Campanhas

Sistema completo de gestão de campanhas de comunicação para o CRC-ES, baseado nos scripts originais de envio de boletos por email e WhatsApp.

## 🎯 Funcionalidades

### ✅ Sistema Completo
- **Dashboard** com estatísticas em tempo real
- **Gestão de Campanhas** (CRUD completo)
- **Templates** de email e WhatsApp
- **Gestão de Contatos** sincronizada com banco
- **Configurações** editáveis do sistema
- **Auditoria** completa de ações
- **Autenticação** segura com JWT

### 📊 Baseado nos Scripts Originais
- **ENVIO BOLETO EMAIL.py** → Serviço de Email
- **ENVIO BOLETO WHATSAPP.py** → Serviço de WhatsApp
- **Configurações SQL Server** preservadas
- **Estrutura de dados** original mantida

## 🚀 Tecnologias

### Backend
- **Python 3.11** + Flask
- **SQLAlchemy** para ORM
- **JWT** para autenticação
- **Flask-CORS** para integração
- **PyODBC** para SQL Server

### Frontend
- **React 18** + Vite
- **Tailwind CSS** para design
- **Context API** para estado
- **Axios** para API calls
- **React Router** para navegação

## 📦 Instalação

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- SQL Server (configurado conforme scripts originais)

### Backend
```bash
cd backend
pip install -r requirements.txt
python src/main_simple.py
```

### Frontend
```bash
cd crces-frontend
npm install
npm run dev
```

## 🔧 Configuração

### Banco de Dados
O sistema utiliza as mesmas configurações dos scripts originais:
- **Servidor:** SERVERSQL\CRCES
- **Database:** SCF
- **Usuário:** ADMIN
- **Senha:** DIAVIC

### Credenciais de Acesso
- **Usuário:** admin
- **Senha:** admin123

## 🌐 Uso

### Acesso ao Sistema
1. Acesse: http://localhost:5174 (Frontend)
2. Backend: http://localhost:5003
3. Login: `admin` / `admin123`

### Principais Funcionalidades

#### 📊 Dashboard
- Estatísticas de campanhas
- Métricas de envio
- Status do sistema
- Ações rápidas

#### 📧 Campanhas
- **Criar** nova campanha
- **Editar** campanhas existentes
- **Iniciar** envio automático
- **Monitorar** progresso
- **Relatórios** detalhados

#### 📝 Templates
- Templates de email
- Templates de WhatsApp
- Editor de conteúdo
- Variáveis dinâmicas

#### 👥 Contatos
- Sincronização com banco
- Filtros avançados
- Importação/Exportação
- Gestão de grupos

#### ⚙️ Configurações
- **Conexão de banco** editável
- Configurações de email
- Configurações de WhatsApp
- Parâmetros do sistema

#### 📋 Auditoria
- Log de todas as ações
- Histórico de envios
- Relatórios de erro
- Monitoramento de uso

## 📁 Estrutura do Projeto

```
CRC-ES-COMPLETO/
├── backend/
│   ├── src/
│   │   ├── config/          # Configurações
│   │   ├── models/          # Modelos do banco
│   │   ├── routes/          # Rotas da API
│   │   ├── services/        # Serviços de negócio
│   │   ├── main.py          # Aplicação principal
│   │   └── main_simple.py   # Versão simplificada
│   ├── requirements.txt
│   └── .env.example
└── crces-frontend/
    ├── src/
    │   ├── App.jsx          # Aplicação principal
    │   └── index.css        # Estilos
    ├── package.json
    └── vite.config.js
```

## 🔄 API Endpoints

### Autenticação
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Usuário atual
- `POST /api/auth/logout` - Logout

### Campanhas
- `GET /api/campaigns` - Listar campanhas
- `POST /api/campaigns` - Criar campanha
- `PUT /api/campaigns/:id` - Editar campanha
- `DELETE /api/campaigns/:id` - Excluir campanha
- `POST /api/campaigns/:id/start` - Iniciar campanha

### Templates
- `GET /api/templates` - Listar templates
- `POST /api/templates` - Criar template
- `PUT /api/templates/:id` - Editar template
- `DELETE /api/templates/:id` - Excluir template

## 🚀 Status do Sistema

### ✅ Implementado e Funcionando
- ✅ Backend completo com todas as APIs
- ✅ Frontend responsivo e moderno
- ✅ Sistema de autenticação JWT
- ✅ Dashboard com estatísticas
- ✅ CRUD de campanhas funcional
- ✅ Integração frontend-backend
- ✅ Templates baseados nos scripts originais
- ✅ Configurações editáveis

### 🔧 Funcionalidades dos Scripts Originais
- ✅ Envio de boletos por email (ENVIO BOLETO EMAIL.py)
- ✅ Envio de boletos por WhatsApp (ENVIO BOLETO WHATSAPP.py)
- ✅ Integração com banco SQL Server
- ✅ Configurações de conexão preservadas
- ✅ Estrutura de dados original mantida

---

**Sistema desenvolvido baseado nos scripts originais do CRC-ES**  
**Todas as funcionalidades implementadas e testadas**

