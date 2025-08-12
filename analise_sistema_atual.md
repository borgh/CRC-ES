# Análise do Sistema Atual - CRC-ES

## Estrutura dos Arquivos Encontrados

### BOT_WPP (Sistema de WhatsApp)
- ANIVERSARIO.py
- ANUIDADE_EXERCICIO.py
- ATIVOS_DEVEDORES.py
- BAIXADOS_DEVEDORES.py
- BOLETO_ANUIDADE.py
- BOLETO_PARCELA.py
- LEMBRETE_VENCIMENTO.py

### DEV/CODIGOS (Scripts de Desenvolvimento)
- Aniversario.py
- ANUIDADE2024.py
- ANUIDADE2024PJ.py
- BI.py
- ENVIO BOLETO EMAIL.py
- ENVIO BOLETO WHATSAPP.py
- LEMBRETE_VENCIMENTO.py
- E outros scripts auxiliares

## Análise Detalhada dos Scripts Principais




### Funcionalidades Identificadas

#### 1. Envio de Email (ENVIO BOLETO EMAIL.py)
- **Conexão com SQL Server**: SERVERSQL\CRCES, database SCF
- **Integração com Outlook**: Usa win32com.client para envio
- **Query SQL**: Busca registros com débitos de anuidade (código 23%)
- **Anexos**: Boletos em PDF com senha (3 primeiros dígitos do CPF)
- **Template de Email**: HTML formatado com informações sobre benefícios
- **Controle de Envio**: Loop com tratamento de exceções e delay de 3 segundos

#### 2. Envio de WhatsApp (ENVIO BOLETO WHATSAPP.py)
- **Selenium WebDriver**: Automação do WhatsApp Web
- **Dados de Entrada**: Excel com destinatários (CRCES_WPP.xlsx)
- **Anexos**: Mesma estrutura de PDFs com senha
- **Template de Mensagem**: Texto personalizado com nome do destinatário
- **Controle de Envio**: Loop com tratamento de exceções e delays

#### 3. Sistema BOT_WPP
- **BOLETO_ANUIDADE.py**: Busca registro por telefone e retorna JSON
- **LEMBRETE_VENCIMENTO.py**: Gera lista de devedores para lembrete
- **Outros scripts**: ANIVERSARIO, ATIVOS_DEVEDORES, BAIXADOS_DEVEDORES, etc.

### Estrutura do Banco de Dados
- **Servidor**: SERVERSQL\CRCES
- **Database**: SCF
- **Tabelas principais**:
  - SCDA01: Dados dos registrados
  - SCDA71: Telefones dos registrados
  - SFNA01: Dados financeiros/débitos

### Pontos de Melhoria Identificados
1. **Segurança**: Credenciais hardcoded no código
2. **Interface**: Scripts executados manualmente
3. **Logs**: Falta de sistema de auditoria
4. **Escalabilidade**: Dependência de ferramentas desktop (Outlook, Chrome)
5. **Manutenibilidade**: Código duplicado entre scripts
6. **Configuração**: Caminhos de arquivos hardcoded

### Funcionalidades a Manter
1. Conexão com SQL Server existente
2. Envio de emails com anexos
3. Envio via WhatsApp com anexos
4. Templates de mensagens personalizadas
5. Sistema de senhas para PDFs
6. Controle de envios em lote

