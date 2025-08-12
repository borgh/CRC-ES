# Contribuindo para o Sistema CRC-ES

Obrigado por considerar contribuir para o Sistema CRC-ES! Este documento fornece diretrizes para contribuições.

## 🤝 Como Contribuir

### 1. Fork do Projeto
- Faça um fork do repositório
- Clone seu fork localmente
- Configure o repositório upstream

```bash
git clone https://github.com/seu-usuario/CRC-ES.git
cd CRC-ES
git remote add upstream https://github.com/borgh/CRC-ES.git
```

### 2. Criando uma Branch
- Crie uma branch para sua feature/correção
- Use nomes descritivos

```bash
git checkout -b feature/nova-funcionalidade
# ou
git checkout -b fix/correcao-bug
```

### 3. Fazendo Alterações
- Mantenha o código limpo e bem documentado
- Siga os padrões de código existentes
- Adicione comentários quando necessário
- Teste suas alterações

### 4. Commit das Alterações
- Use mensagens de commit claras e descritivas
- Siga o padrão de commits convencionais

```bash
git commit -m "feat: adiciona nova funcionalidade de templates"
git commit -m "fix: corrige erro no envio de emails"
git commit -m "docs: atualiza documentação da API"
```

### 5. Push e Pull Request
- Faça push da sua branch
- Abra um Pull Request com descrição detalhada

```bash
git push origin feature/nova-funcionalidade
```

## 📋 Padrões de Código

### Backend (Python/Flask)
- Use PEP 8 para formatação
- Docstrings para funções e classes
- Type hints quando possível
- Testes unitários para novas funcionalidades

### Frontend (React/JavaScript)
- Use ESLint e Prettier
- Componentes funcionais com hooks
- Nomes de componentes em PascalCase
- Props tipadas com PropTypes ou TypeScript

## 🧪 Testes

### Backend
```bash
cd crces-backend
python -m pytest tests/
```

### Frontend
```bash
cd crces-frontend
npm test
```

## 📝 Documentação

- Atualize o README.md se necessário
- Documente novas APIs no código
- Adicione exemplos de uso
- Mantenha a documentação atualizada

## 🐛 Reportando Bugs

### Antes de Reportar
- Verifique se o bug já foi reportado
- Teste na versão mais recente
- Colete informações do ambiente

### Template de Bug Report
```markdown
**Descrição do Bug**
Descrição clara e concisa do bug.

**Passos para Reproduzir**
1. Vá para '...'
2. Clique em '....'
3. Role para baixo até '....'
4. Veja o erro

**Comportamento Esperado**
Descrição do que deveria acontecer.

**Screenshots**
Se aplicável, adicione screenshots.

**Ambiente:**
- OS: [e.g. Ubuntu 20.04]
- Browser: [e.g. Chrome 91]
- Versão: [e.g. 1.0.0]
```

## 💡 Sugerindo Melhorias

### Template de Feature Request
```markdown
**A melhoria está relacionada a um problema?**
Descrição clara do problema.

**Descreva a solução desejada**
Descrição clara da solução.

**Descreva alternativas consideradas**
Outras soluções consideradas.

**Contexto adicional**
Qualquer contexto adicional.
```

## 🔒 Segurança

- Nunca commite credenciais ou tokens
- Use variáveis de ambiente para configurações sensíveis
- Reporte vulnerabilidades de segurança privadamente

## 📞 Contato

- Issues: Use o sistema de issues do GitHub
- Email: suporte@crces.org.br
- Discussões: Use as discussões do GitHub

## 🎯 Prioridades de Desenvolvimento

### Alta Prioridade
- Correções de segurança
- Bugs críticos
- Performance

### Média Prioridade
- Novas funcionalidades
- Melhorias de UX
- Documentação

### Baixa Prioridade
- Refatoração
- Otimizações menores
- Funcionalidades experimentais

## ✅ Checklist do Pull Request

- [ ] Código testado localmente
- [ ] Testes passando
- [ ] Documentação atualizada
- [ ] Mensagens de commit claras
- [ ] Sem conflitos com main
- [ ] Revisão de código própria feita

## 🏆 Reconhecimento

Todos os contribuidores serão reconhecidos no README.md e releases.

---

**Obrigado por contribuir para o Sistema CRC-ES!** 🚀

