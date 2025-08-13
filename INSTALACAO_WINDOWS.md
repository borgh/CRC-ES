# 🪟 Guia de Instalação - Windows

Este guia resolve todos os problemas de instalação do Sistema CRC-ES no Windows.

## 🔧 Pré-requisitos

### 1. Python 3.11+
```bash
# Baixe do site oficial: https://www.python.org/downloads/
# ✅ Marque "Add Python to PATH" durante a instalação
```

### 2. Node.js 18+
```bash
# Baixe do site oficial: https://nodejs.org/
# ✅ Instale a versão LTS recomendada
```

### 3. Git
```bash
# Baixe do site oficial: https://git-scm.com/download/win
```

## 📥 Instalação

### 1. Clone o Repositório
```bash
git clone https://github.com/borgh/CRC-ES.git
cd CRC-ES
```

### 2. Backend (Flask)

#### Criar Ambiente Virtual
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

#### Instalar Dependências (MÉTODO SEGURO)
```bash
# Método 1: Instalação padrão
pip install -r requirements.txt

# Se der erro, use o Método 2:
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Se ainda der erro, use o Método 3:
pip install Flask==3.0.0
pip install flask-cors==4.0.0
pip install Flask-SQLAlchemy==3.1.1
pip install Flask-JWT-Extended==4.5.3
pip install python-dotenv==1.0.0
pip install pandas==1.5.3
pip install numpy==1.24.4
pip install selenium==4.15.0
pip install pyodbc==4.0.39
```

#### Configurar Banco de Dados
```bash
# Criar arquivo .env na pasta backend
echo DATABASE_URL=sqlite:///app.db > .env
echo SECRET_KEY=crces-secret-key-2024 >> .env
echo JWT_SECRET_KEY=jwt-crces-secret-2024 >> .env
```

#### Iniciar Backend
```bash
python src/main.py
```
✅ **Backend rodando em:** http://localhost:5000

### 3. Frontend (React)

#### Abrir Nova Janela do Terminal
```bash
cd frontend
```

#### Instalar Dependências
```bash
# Método 1: npm (recomendado para Windows)
npm install

# Se der erro, use:
npm install --legacy-peer-deps

# Ou use yarn:
npm install -g yarn
yarn install
```

#### Iniciar Frontend
```bash
npm run dev
```
✅ **Frontend rodando em:** http://localhost:5173

## 🚀 Acesso ao Sistema

1. **Abra o navegador:** http://localhost:5173
2. **Faça login:**
   - **Usuário:** `admin`
   - **Senha:** `admin123`

## ⚠️ Soluções para Problemas Comuns

### Erro: "ModuleNotFoundError: No module named 'dotenv'"
```bash
cd backend
venv\Scripts\activate
pip install python-dotenv==1.0.0
```

### Erro: "metadata-generation-failed" (pandas)
```bash
# Instale versão específica compatível
pip install pandas==1.5.3 numpy==1.24.4
```

### Erro: "ninja: build stopped"
```bash
# Instale Microsoft C++ Build Tools
# Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Ou use versões pré-compiladas:
pip install --only-binary=all pandas numpy
```

### Erro: "Cannot find module" (Frontend)
```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install --legacy-peer-deps
```

### Erro: "Port already in use"
```bash
# Backend (porta 5000)
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# Frontend (porta 5173)
netstat -ano | findstr :5173
taskkill /PID <PID_NUMBER> /F
```

## 🔧 Configuração SQL Server (Opcional)

Se quiser usar SQL Server em vez de SQLite:

### 1. Instalar Driver ODBC
```bash
# Download: Microsoft ODBC Driver 17 for SQL Server
# https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

### 2. Configurar .env
```bash
# Substitua no arquivo backend/.env:
DATABASE_URL=mssql+pyodbc://usuario:senha@servidor/database?driver=ODBC+Driver+17+for+SQL+Server
```

## 📱 Funcionalidades Disponíveis

### ✅ Dashboard
- Estatísticas em tempo real
- Gráficos de performance
- Ações rápidas

### ✅ Campanhas
- Criar campanhas de email/WhatsApp
- Agendar envios
- Monitorar status

### ✅ Templates
- Templates personalizáveis
- Variáveis dinâmicas
- Preview em tempo real

### ✅ Usuários
- Gestão de usuários
- Controle de acesso
- Perfis de permissão

### ✅ Auditoria
- Logs completos
- Rastreamento de ações
- Relatórios de segurança

## 🆘 Suporte

### Problemas Persistentes?

1. **Verifique versões:**
```bash
python --version  # Deve ser 3.11+
node --version    # Deve ser 18+
npm --version     # Deve ser 9+
```

2. **Reinstalação limpa:**
```bash
# Backend
cd backend
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

# Frontend
cd frontend
rmdir /s node_modules
del package-lock.json
npm cache clean --force
npm install
```

3. **Logs de erro:**
```bash
# Backend - verifique logs no terminal
# Frontend - abra F12 no navegador e veja Console
```

## 🎯 Checklist de Instalação

- [ ] Python 3.11+ instalado
- [ ] Node.js 18+ instalado
- [ ] Git instalado
- [ ] Repositório clonado
- [ ] Backend: venv criado e ativado
- [ ] Backend: dependências instaladas
- [ ] Backend: arquivo .env configurado
- [ ] Backend: servidor rodando (porta 5000)
- [ ] Frontend: dependências instaladas
- [ ] Frontend: servidor rodando (porta 5173)
- [ ] Sistema acessível em http://localhost:5173
- [ ] Login funcionando (admin/admin123)

**✅ Sistema 100% funcional no Windows!**

---

💡 **Dica:** Mantenha sempre os terminais do backend e frontend abertos durante o uso do sistema.

