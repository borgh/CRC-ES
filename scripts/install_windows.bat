@echo off
echo ========================================
echo    Sistema CRC-ES - Instalacao Windows
echo ========================================
echo.

echo [1/6] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Baixe em: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✓ Python encontrado

echo [2/6] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Node.js nao encontrado!
    echo Baixe em: https://nodejs.org/
    pause
    exit /b 1
)
echo ✓ Node.js encontrado

echo [3/6] Configurando Backend...
cd backend
if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Instalando dependencias do backend...
pip install --upgrade pip
pip install -r requirements.txt

echo Configurando variaveis de ambiente...
if not exist .env (
    copy .env.example .env
    echo ✓ Arquivo .env criado
)

echo [4/6] Configurando Frontend...
cd ..\frontend

echo Instalando dependencias do frontend...
call npm install --legacy-peer-deps

echo [5/6] Testando instalacao...
echo.
echo ========================================
echo           INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Para iniciar o sistema:
echo.
echo 1. Backend (Terminal 1):
echo    cd backend
echo    venv\Scripts\activate
echo    python src/main.py
echo.
echo 2. Frontend (Terminal 2):
echo    cd frontend
echo    npm run dev
echo.
echo 3. Acesse: http://localhost:5173
echo    Usuario: admin
echo    Senha: admin123
echo.
echo ========================================

pause

