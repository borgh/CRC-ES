# 🚀 Guia de Instalação - CRC-ES

## ⚠️ **PROBLEMA RESOLVIDO**

Se você estava enfrentando erros de dependências como:
```
npm error ERESOLVE unable to resolve dependency tree
npm error peer date-fns@"^2.28.0 || ^3.0.0" from react-day-picker@8.10.1
```

**✅ SOLUÇÃO:** O `package.json` foi corrigido com versões compatíveis!

---

## 📋 **Pré-requisitos**

### ✅ **Node.js e npm**
- **Node.js:** 18.0.0 ou superior
- **npm:** 9.0.0 ou superior

### 🔍 **Verificar Versões:**
```bash
node --version  # Deve ser >= 18.0.0
npm --version   # Deve ser >= 9.0.0
```

### 📥 **Instalar Node.js (se necessário):**
- **Windows/Mac:** https://nodejs.org/
- **Linux:** 
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

---

## 🛠️ **Instalação Passo a Passo**

### 1️⃣ **Clone o Repositório**
```bash
git clone https://github.com/borgh/CRC-ES.git
cd CRC-ES
```

### 2️⃣ **Limpe Cache (se necessário)**
```bash
# Limpar cache do npm
npm cache clean --force

# Remover node_modules se existir
rm -rf node_modules
rm -f package-lock.json
```

### 3️⃣ **Instale as Dependências**
```bash
npm install
```

### 4️⃣ **Execute o Projeto**
```bash
npm run dev
```

### 5️⃣ **Acesse o Sistema**
- **URL:** http://localhost:5173
- **Usuário:** admin
- **Senha:** admin123

---

## 🔧 **Comandos Disponíveis**

```bash
# Desenvolvimento
npm run dev          # Inicia servidor de desenvolvimento

# Build
npm run build        # Gera build de produção
npm run preview      # Preview do build

# Linting
npm run lint         # Verifica código
```

---

## ❌ **Solucionando Problemas**

### **Erro: ERESOLVE unable to resolve dependency tree**
```bash
# Solução 1: Instalar com --legacy-peer-deps
npm install --legacy-peer-deps

# Solução 2: Usar --force (não recomendado)
npm install --force

# Solução 3: Limpar tudo e reinstalar
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### **Erro: Node.js version incompatible**
```bash
# Verificar versão
node --version

# Atualizar Node.js para versão 18+
# Windows/Mac: Baixar do site oficial
# Linux: Usar nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

### **Erro: Port 5173 already in use**
```bash
# Matar processo na porta
npx kill-port 5173

# Ou usar porta diferente
npm run dev -- --port 3000
```

### **Erro: Permission denied**
```bash
# Linux/Mac: Dar permissões
sudo chown -R $(whoami) ~/.npm
sudo chown -R $(whoami) node_modules

# Windows: Executar como Administrador
```

---

## 🌐 **Alternativa: Usar Sistema Online**

Se ainda tiver problemas com a instalação local:

### ✅ **Sistema 100% Funcional Online:**
**🔗 https://gwmrepid.manus.space**

**Credenciais:**
- Usuário: `admin`
- Senha: `admin123`

---

## 📱 **Testando a Instalação**

### ✅ **Verificações:**
1. **Servidor iniciou:** Veja mensagem "Local: http://localhost:5173"
2. **Página carrega:** Interface de login aparece
3. **Login funciona:** Use admin/admin123
4. **Dashboard aparece:** Estatísticas e gráficos carregam

### ✅ **Funcionalidades para Testar:**
- [x] Login/Logout
- [x] Dashboard com gráficos
- [x] Navegação entre páginas
- [x] Campanhas (lista e detalhes)
- [x] Templates (Email e WhatsApp)
- [x] Usuários (lista)
- [x] Auditoria (logs)

---

## 🔄 **Atualizações**

### **Para atualizar o projeto:**
```bash
git pull origin main
npm install  # Instalar novas dependências
npm run dev  # Reiniciar servidor
```

---

## 📞 **Suporte**

### **Se ainda tiver problemas:**

1. **Verifique os logs:** Console do navegador (F12)
2. **Teste online:** https://gwmrepid.manus.space
3. **Issues GitHub:** https://github.com/borgh/CRC-ES/issues
4. **Documentação:** Leia todos os arquivos .md do projeto

---

## ✅ **Instalação Bem-sucedida**

Quando tudo estiver funcionando, você verá:

```
  VITE v5.2.0  ready in 1234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**🎉 Parabéns! O sistema CRC-ES está rodando localmente!**

---

<div align="center">

**🏛️ Sistema CRC-ES - Instalação Simplificada**

*Qualquer dúvida, use o sistema online como alternativa*

</div>

