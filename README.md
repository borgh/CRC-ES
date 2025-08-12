# Sistema CRC-ES - Envio de Mensagens em Massa

Sistema web completo para envio em massa de mensagens de cobrança via WhatsApp e email para o CRC-ES (Conselho Regional de Contabilidade do Espírito Santo).

## 🚀 Funcionalidades

### ✅ Funcionalidades Implementadas

- **Autenticação e Autorização**
  - Login seguro com JWT
  - Controle de acesso baseado em roles (Admin, Supervisor, Operador)
  - Rate limiting para prevenir ataques
  - Auditoria completa de ações

- **Envio de Mensagens**
  - Envio individual via WhatsApp
  - Envio individual via Email
  - Envio em massa via WhatsApp (até 1000 destinatários)
  - Envio em massa via Email (até 1000 destinatários)
  - Templates personalizáveis
  - Anexos em emails
  - Validação de números de telefone e emails

- **Gerenciamento de Campanhas**
  - Criação e gerenciamento de campanhas
  - Acompanhamento de status em tempo real
  - Estatísticas detalhadas de entrega
  - Histórico completo de envios

- **Interface Web**
  - Dashboard com estatísticas
  - Interface responsiva e moderna
  - Tema claro/escuro
  - Navegação intuitiva

- **Segurança**
  - Criptografia de senhas com salt
  - Rate limiting por IP
  - Validação rigorosa de entrada
  - Logs de auditoria
  - Bloqueio automático por tentativas falhadas

## 🏗️ Arquitetura

### Backend (Flask)
- **Framework**: Flask com SQLAlchemy
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Autenticação**: JWT com refresh tokens
- **APIs**: RESTful com validação de entrada
- **Serviços**: WhatsApp (Evolution API), Email (SMTP)

### Frontend (React)
- **Framework**: React 18 com Vite
- **UI**: Componentes modernos com Tailwind CSS
- **Estado**: Context API para autenticação
- **Roteamento**: React Router
- **Gráficos**: Recharts para visualizações

## 📋 Pré-requisitos

- Python 3.11+
- Node.js 18+
- Evolution API (para WhatsApp)
- Servidor SMTP (para emails)

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone <repository-url>
cd crces-system
```

### 2. Configuração do Backend

```bash
cd crces-backend

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\\Scripts\\activate  # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Inicialize o banco de dados
python src/main.py
```

### 3. Configuração do Frontend

```bash
cd crces-frontend

# Instale dependências
pnpm install
# ou
npm install

# Configure variáveis de ambiente
cp .env.example .env
# Edite VITE_API_URL se necessário

# Inicie o servidor de desenvolvimento
pnpm dev
# ou
npm run dev
```

## ⚙️ Configuração

### Configuração de Email

1. Configure um servidor SMTP (Gmail, Outlook, etc.)
2. Para Gmail, use senhas de aplicativo
3. Atualize as variáveis no `.env`:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-aplicativo
```

### Configuração do WhatsApp

1. Instale e configure a Evolution API
2. Crie uma instância
3. Atualize as variáveis no `.env`:

```env
WHATSAPP_API_URL=http://localhost:8080
WHATSAPP_API_KEY=sua-api-key
WHATSAPP_INSTANCE=nome-da-instancia
```

## 🚀 Uso

### Acesso Inicial

1. Acesse `http://localhost:5173`
2. Use as credenciais padrão:
   - **Usuário**: admin
   - **Senha**: admin123
3. **IMPORTANTE**: Altere a senha padrão imediatamente

### Criando Campanhas

1. Acesse "Campanhas" no menu
2. Clique em "Nova Campanha"
3. Escolha o tipo (Email ou WhatsApp)
4. Configure destinatários e mensagem
5. Agende ou envie imediatamente

### Templates

1. Acesse "Templates" no menu
2. Crie templates reutilizáveis
3. Use variáveis como `{{nome}}`, `{{valor}}`, etc.
4. Templates suportam HTML para emails

### Exemplo de Template de Cobrança

```html
<h2>Prezado(a) {{nome}},</h2>

<p>Informamos que existe(m) mensalidade(s) em aberto:</p>

<ul>
  <li><strong>Valor:</strong> R$ {{valor}}</li>
  <li><strong>Vencimento:</strong> {{vencimento}}</li>
  <li><strong>Registro:</strong> {{registro}}</li>
</ul>

<p>Para regularizar sua situação, efetue o pagamento através do boleto em anexo.</p>

<p>Atenciosamente,<br>
<strong>Equipe CRC-ES</strong></p>
```

## 📊 Monitoramento

### Dashboard
- Estatísticas em tempo real
- Gráficos de performance
- Status das campanhas
- Taxa de entrega

### Logs de Auditoria
- Todas as ações são registradas
- Rastreamento por usuário e IP
- Histórico completo de operações

## 🔒 Segurança

### Medidas Implementadas

- **Rate Limiting**: Previne spam e ataques
- **Validação de Entrada**: Sanitização de dados
- **Autenticação JWT**: Tokens seguros
- **Criptografia**: Senhas com hash + salt
- **Auditoria**: Log completo de ações
- **Bloqueio Automático**: Por tentativas falhadas

### Roles e Permissões

- **Admin**: Acesso total ao sistema
- **Supervisor**: Gerencia campanhas e usuários
- **Operador**: Envia mensagens individuais
- **Visualizador**: Apenas consulta

## 🐛 Solução de Problemas

### Backend não inicia
```bash
# Verifique se o ambiente virtual está ativo
source venv/bin/activate

# Verifique dependências
pip install -r requirements.txt

# Verifique logs
tail -f logs/crces.log
```

### Frontend não conecta
```bash
# Verifique se o backend está rodando
curl http://localhost:5000/api/health

# Verifique variáveis de ambiente
cat .env
```

### WhatsApp não funciona
1. Verifique se a Evolution API está rodando
2. Teste a conexão: `GET /api/messaging/test-connections`
3. Verifique se a instância está conectada

### Emails não são enviados
1. Teste configurações SMTP
2. Verifique se não está sendo bloqueado por firewall
3. Para Gmail, use senhas de aplicativo

## 📝 API Endpoints

### Autenticação
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `POST /api/auth/refresh` - Renovar token

### Mensagens
- `POST /api/messaging/send-email` - Enviar email individual
- `POST /api/messaging/send-whatsapp` - Enviar WhatsApp individual
- `POST /api/messaging/send-bulk-email` - Enviar emails em massa
- `POST /api/messaging/send-bulk-whatsapp` - Enviar WhatsApp em massa

### Campanhas
- `GET /api/campaigns` - Listar campanhas
- `POST /api/campaigns` - Criar campanha
- `GET /api/campaigns/:id` - Detalhes da campanha

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte técnico, entre em contato:
- Email: suporte@crces.org.br
- Telefone: (27) 3xxx-xxxx

## 🔄 Atualizações

### Versão 1.0.0
- Sistema completo implementado
- Funcionalidades de envio em massa
- Interface web responsiva
- Segurança robusta
- Auditoria completa

---

**Desenvolvido para o CRC-ES - Conselho Regional de Contabilidade do Espírito Santo**

