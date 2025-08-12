# Arquitetura do Sistema Web CRC-ES
## Sistema de Envio em Massa de Mensagens de Cobrança

**Autor**: Manus AI  
**Data**: 12 de Agosto de 2025  
**Versão**: 1.0

---

## 1. Visão Geral do Sistema

O sistema web para o Conselho Regional de Contabilidade do Espírito Santo (CRC-ES) será uma aplicação moderna e segura para automatizar o envio em massa de mensagens de cobrança via WhatsApp e email. O sistema substituirá os scripts Python manuais existentes por uma interface web intuitiva, proporcionando maior controle, auditoria e segurança nas operações de cobrança.

### 1.1 Objetivos Principais

O sistema tem como objetivo principal modernizar e centralizar o processo de cobrança de mensalidades do CRC-ES, oferecendo uma interface web amigável que permita aos usuários autorizados enviar mensagens personalizadas em massa para os contadores associados. A solução deve manter a compatibilidade com o banco de dados SQL Server existente, preservando toda a lógica de negócio já estabelecida, enquanto adiciona camadas de segurança, auditoria e controle de acesso que não existiam nos scripts originais.

### 1.2 Benefícios Esperados

A implementação deste sistema trará diversos benefícios organizacionais. Primeiro, a centralização das operações de cobrança em uma única plataforma web eliminará a necessidade de executar scripts individuais em diferentes máquinas, reduzindo significativamente o risco de erros operacionais e aumentando a eficiência do processo. Segundo, o sistema de controle de usuários e auditoria proporcionará rastreabilidade completa de todas as ações realizadas, permitindo identificar quem enviou quais mensagens e quando, atendendo aos requisitos de compliance e governança corporativa.

Terceiro, a interface web moderna e intuitiva reduzirá a curva de aprendizado para novos usuários e eliminará a dependência de conhecimento técnico específico em Python ou automação de desktop. Quarto, o sistema de templates personalizáveis permitirá maior flexibilidade na criação de mensagens, adaptando-se rapidamente a diferentes campanhas de cobrança ou comunicações especiais. Por fim, a arquitetura baseada em web services permitirá futuras integrações com outros sistemas do CRC-ES, criando um ecossistema tecnológico mais coeso e escalável.

## 2. Análise dos Requisitos Funcionais

### 2.1 Funcionalidades Essenciais

Com base na análise dos scripts existentes, o sistema deve implementar as seguintes funcionalidades essenciais. O módulo de envio de emails deve ser capaz de conectar-se ao banco de dados SQL Server existente, executar consultas personalizadas para identificar devedores, e enviar emails com anexos de boletos em PDF. O sistema deve suportar templates HTML personalizáveis, permitindo a inclusão de informações dinâmicas como nome do destinatário, valor da dívida, e data de vencimento.

O módulo de envio via WhatsApp deve integrar-se com APIs modernas de WhatsApp Business, substituindo a automação via Selenium WebDriver por uma solução mais robusta e confiável. O sistema deve suportar o envio de mensagens de texto personalizadas com anexos de documentos, mantendo a funcionalidade de senha nos PDFs baseada nos três primeiros dígitos do CPF do destinatário.

O sistema de gerenciamento de campanhas deve permitir a criação, agendamento e monitoramento de campanhas de envio em massa. Os usuários devem poder definir critérios de seleção de destinatários através de uma interface gráfica intuitiva, sem necessidade de escrever consultas SQL diretamente. O sistema deve incluir funcionalidades de preview das mensagens antes do envio, permitindo validação do conteúdo e dos destinatários selecionados.

### 2.2 Requisitos de Integração

O sistema deve manter total compatibilidade com a infraestrutura existente do CRC-ES. A conexão com o SQL Server deve ser configurável através de variáveis de ambiente, permitindo fácil migração entre ambientes de desenvolvimento, teste e produção. O sistema deve ser capaz de acessar as tabelas SCDA01, SCDA71 e SFNA01, mantendo a mesma lógica de consultas dos scripts originais, mas com melhorias na performance e segurança.

A integração com sistemas de email deve suportar tanto SMTP tradicional quanto APIs modernas de provedores como SendGrid ou Amazon SES, proporcionando maior confiabilidade na entrega das mensagens. Para WhatsApp, o sistema deve integrar-se com a API oficial do WhatsApp Business, garantindo compliance com as políticas da plataforma e maior estabilidade nas operações de envio.

O sistema deve incluir APIs RESTful bem documentadas, permitindo futuras integrações com outros sistemas do CRC-ES ou ferramentas de terceiros. Todas as APIs devem seguir padrões de segurança modernos, incluindo autenticação via JWT e rate limiting para prevenir abuso.

## 3. Arquitetura Técnica Detalhada

### 3.1 Stack Tecnológico

A arquitetura do sistema será baseada em tecnologias modernas e amplamente adotadas no mercado. O backend será desenvolvido em Python utilizando o framework Flask, escolhido por sua flexibilidade, facilidade de desenvolvimento e excelente suporte para APIs RESTful. Flask oferece a vantagem de ser leve e modular, permitindo a adição de funcionalidades conforme necessário sem overhead desnecessário.

O frontend será desenvolvido em React.js, proporcionando uma interface de usuário moderna, responsiva e altamente interativa. React foi escolhido por sua maturidade, vasta comunidade de desenvolvedores, e excelente ecossistema de bibliotecas complementares. A arquitetura de componentes do React facilitará a manutenção e evolução da interface, permitindo reutilização de código e desenvolvimento ágil de novas funcionalidades.

Para o banco de dados da aplicação, será utilizado PostgreSQL como banco principal para armazenar dados de usuários, logs de auditoria, templates de mensagens e configurações do sistema. PostgreSQL foi escolhido por sua robustez, recursos avançados de segurança, e excelente performance em operações complexas. O sistema manterá a conexão com o SQL Server existente exclusivamente para consultas aos dados dos registrados, preservando a integridade dos sistemas legados.

### 3.2 Arquitetura de Microserviços

O sistema será estruturado seguindo princípios de arquitetura de microserviços, com separação clara de responsabilidades entre diferentes módulos. O serviço de autenticação será responsável por gerenciar usuários, sessões e permissões, implementando OAuth 2.0 e JWT para segurança robusta. Este serviço será independente e poderá ser reutilizado por outros sistemas do CRC-ES no futuro.

O serviço de mensageria será responsável por toda a lógica de envio de emails e WhatsApp, incluindo gerenciamento de filas, retry de mensagens falhadas, e integração com provedores externos. Este serviço utilizará Redis como broker de mensagens, garantindo alta performance e confiabilidade no processamento de grandes volumes de envios.

O serviço de relatórios e auditoria será responsável por coletar, processar e apresentar dados sobre as operações realizadas no sistema. Este serviço incluirá dashboards em tempo real, relatórios personalizáveis, e alertas automáticos para situações que requerem atenção da equipe de TI ou gestão.

### 3.3 Segurança e Compliance

A segurança será implementada em múltiplas camadas, seguindo as melhores práticas da indústria. Todas as comunicações entre cliente e servidor utilizarão HTTPS com certificados TLS 1.3, garantindo criptografia end-to-end. As senhas dos usuários serão armazenadas utilizando algoritmos de hash seguros como bcrypt, com salt único para cada usuário.

O sistema implementará autenticação multifator (MFA) obrigatória para todos os usuários, utilizando aplicativos como Google Authenticator ou Authy. As sessões terão timeout automático configurável, e todas as ações sensíveis requererão reautenticação. O sistema manterá logs detalhados de todas as operações, incluindo tentativas de login, envios de mensagens, e alterações de configuração.

Para compliance com a Lei Geral de Proteção de Dados (LGPD), o sistema implementará controles rigorosos de acesso aos dados pessoais, com logs de auditoria detalhados sobre quem acessou quais informações e quando. Dados sensíveis como CPFs serão criptografados em repouso, e o sistema incluirá funcionalidades para atender a solicitações de portabilidade e exclusão de dados conforme requerido pela legislação.



## 4. Modelagem do Banco de Dados

### 4.1 Estrutura do Banco Principal (PostgreSQL)

O banco de dados principal do sistema será estruturado para suportar todas as funcionalidades de controle de usuários, auditoria e configurações. A tabela `users` armazenará informações dos usuários do sistema, incluindo dados de autenticação, perfis de acesso e configurações pessoais. Esta tabela incluirá campos como id, username, email, password_hash, salt, mfa_secret, is_active, created_at, updated_at, last_login, e failed_login_attempts.

A tabela `roles` definirá os diferentes níveis de acesso no sistema, como Administrador, Operador Senior, Operador Junior, e Visualizador. Cada role terá permissões específicas definidas na tabela `permissions`, que incluirá ações como enviar_email, enviar_whatsapp, criar_campanhas, visualizar_relatorios, gerenciar_usuarios, e configurar_sistema. A relação many-to-many entre users e roles será gerenciada pela tabela `user_roles`.

A tabela `campaigns` armazenará informações sobre campanhas de envio, incluindo nome, descrição, tipo (email/whatsapp/ambos), status, critérios de seleção, template utilizado, data de criação, data de execução, e estatísticas de envio. A tabela `campaign_messages` registrará cada mensagem individual enviada dentro de uma campanha, incluindo destinatário, status de entrega, timestamps de envio e entrega, e eventuais erros ocorridos.

### 4.2 Sistema de Auditoria e Logs

O sistema de auditoria será implementado através de várias tabelas especializadas. A tabela `audit_logs` registrará todas as ações realizadas no sistema, incluindo user_id, action_type, resource_type, resource_id, old_values, new_values, ip_address, user_agent, e timestamp. Esta estrutura permitirá rastreamento completo de todas as operações, atendendo aos requisitos de compliance e governança.

A tabela `email_logs` manterá registros detalhados de todos os emails enviados, incluindo recipient_email, subject, template_used, attachment_info, delivery_status, bounce_reason, open_tracking, click_tracking, e timestamps relevantes. Similarmente, a tabela `whatsapp_logs` registrará informações específicas dos envios via WhatsApp, incluindo recipient_phone, message_content, attachment_info, delivery_status, read_status, e response_time.

A tabela `system_health` monitorará a saúde geral do sistema, registrando métricas como CPU usage, memory usage, disk space, database connections, API response times, e error rates. Estes dados alimentarão dashboards de monitoramento em tempo real e alertas automáticos para a equipe de TI.

### 4.3 Integração com SQL Server Legado

A integração com o SQL Server existente será implementada através de uma camada de abstração que manterá a compatibilidade com as consultas existentes enquanto adiciona melhorias de performance e segurança. O sistema utilizará connection pooling para otimizar o uso de conexões com o banco legado, e implementará cache inteligente para consultas frequentes, reduzindo a carga no servidor de produção.

As consultas ao SQL Server serão parametrizadas e validadas para prevenir SQL injection, e o sistema incluirá monitoramento de performance para identificar consultas lentas ou problemáticas. Um sistema de fallback será implementado para garantir disponibilidade mesmo em caso de problemas temporários com o banco legado.

## 5. Design da Interface de Usuário

### 5.1 Princípios de UX/UI

A interface do usuário será projetada seguindo princípios modernos de User Experience (UX) e User Interface (UI), priorizando usabilidade, acessibilidade e eficiência operacional. O design seguirá uma abordagem mobile-first, garantindo que todas as funcionalidades sejam acessíveis e utilizáveis em dispositivos móveis, tablets e desktops.

A paleta de cores será baseada na identidade visual do CRC-ES, utilizando tons profissionais que transmitam confiança e seriedade. A tipografia será clara e legível, com hierarquia visual bem definida para facilitar a navegação e compreensão das informações. O sistema utilizará ícones intuitivos e consistentes, seguindo padrões estabelecidos como Material Design ou Ant Design.

A navegação será estruturada de forma lógica e intuitiva, com menu lateral retrátil para maximizar o espaço útil da tela. Breadcrumbs serão utilizados para orientar o usuário sobre sua localização atual no sistema, e tooltips contextuais fornecerão ajuda inline sem poluir a interface.

### 5.2 Módulos da Interface

O módulo Dashboard apresentará uma visão geral das operações do sistema, incluindo estatísticas de envios recentes, campanhas ativas, alertas do sistema, e métricas de performance. Gráficos interativos mostrarão tendências de envio, taxas de entrega, e comparativos entre diferentes períodos. Cards informativos destacarão informações importantes como campanhas pendentes, erros recentes, e lembretes de manutenção.

O módulo de Campanhas permitirá criar, editar e gerenciar campanhas de envio em massa. A interface incluirá um wizard step-by-step para criação de campanhas, com validação em tempo real dos dados inseridos. Os usuários poderão definir critérios de seleção através de uma interface gráfica intuitiva, sem necessidade de conhecimento em SQL. Preview das mensagens será disponibilizado antes do envio, incluindo simulação com dados reais para validação.

O módulo de Templates oferecerá um editor WYSIWYG para criação e edição de templates de email e WhatsApp. O editor incluirá funcionalidades de drag-and-drop, biblioteca de componentes pré-definidos, e sistema de variáveis dinâmicas para personalização das mensagens. Versionamento de templates permitirá controle de mudanças e rollback quando necessário.

### 5.3 Funcionalidades Avançadas da Interface

O sistema incluirá funcionalidades avançadas para melhorar a produtividade dos usuários. Um sistema de busca global permitirá encontrar rapidamente campanhas, templates, ou registros específicos. Filtros avançados e ordenação customizável facilitarão a análise de grandes volumes de dados.

Notificações em tempo real informarão sobre o progresso de campanhas, erros ocorridos, e outras informações relevantes. O sistema suportará notificações push no navegador e emails de alerta para situações críticas. Um centro de notificações centralizará todas as mensagens e permitirá gerenciamento do histórico.

A interface incluirá funcionalidades de exportação de dados em múltiplos formatos (PDF, Excel, CSV), com opções de personalização dos relatórios. Dashboards personalizáveis permitirão que cada usuário configure sua visão preferida do sistema, salvando layouts e filtros específicos.

## 6. Especificações de Segurança

### 6.1 Autenticação e Autorização

O sistema implementará um robusto sistema de autenticação baseado em múltiplos fatores. A autenticação primária utilizará username/email e senha, com políticas rigorosas de complexidade de senha incluindo mínimo de 12 caracteres, combinação de letras maiúsculas e minúsculas, números e símbolos especiais. Senhas serão validadas contra dicionários de senhas comuns e não poderão reutilizar as últimas 12 senhas utilizadas.

A autenticação multifator (MFA) será obrigatória para todos os usuários, suportando aplicativos TOTP como Google Authenticator, Authy, ou Microsoft Authenticator. Como alternativa, o sistema suportará SMS ou email como segundo fator, embora TOTP seja recomendado por sua maior segurança. Códigos de backup serão gerados para cada usuário, permitindo acesso em caso de perda do dispositivo MFA.

O sistema de autorização implementará controle de acesso baseado em roles (RBAC) com granularidade fina. Permissões serão definidas no nível de ação específica, permitindo controle preciso sobre o que cada usuário pode fazer. Sessões terão timeout configurável (padrão 30 minutos de inatividade), e ações sensíveis requererão reautenticação mesmo dentro de uma sessão válida.

### 6.2 Proteção de Dados

Todos os dados sensíveis serão criptografados em repouso utilizando AES-256, com chaves gerenciadas através de um sistema de gerenciamento de chaves robusto. Dados em trânsito serão protegidos por TLS 1.3 com perfect forward secrecy. Informações como CPFs, números de telefone e emails serão criptografados com chaves específicas, permitindo descriptografia apenas quando necessário para operações autorizadas.

O sistema implementará técnicas de anonimização e pseudonimização para dados utilizados em relatórios e análises, reduzindo a exposição de informações pessoais. Logs de auditoria incluirão hashes dos dados acessados em vez dos dados reais, permitindo rastreamento sem exposição desnecessária de informações sensíveis.

Backups serão criptografados e armazenados em locais seguros, com testes regulares de restauração para garantir integridade. O sistema incluirá funcionalidades para atender aos direitos dos titulares de dados conforme LGPD, incluindo portabilidade, correção e exclusão de dados pessoais.

### 6.3 Monitoramento e Detecção de Ameaças

O sistema incluirá monitoramento contínuo de segurança com detecção automática de atividades suspeitas. Algoritmos de machine learning analisarão padrões de acesso para identificar comportamentos anômalos, como tentativas de login de localizações incomuns, acessos fora do horário normal, ou padrões de uso inconsistentes com o perfil do usuário.

Rate limiting será implementado em todas as APIs para prevenir ataques de força bruta e DDoS. O sistema bloqueará automaticamente IPs que apresentem comportamento suspeito, com possibilidade de whitelist para IPs conhecidos e confiáveis. Honeypots serão implementados para detectar tentativas de acesso não autorizado.

Alertas automáticos serão enviados para a equipe de segurança em caso de eventos críticos como múltiplas tentativas de login falhadas, acessos administrativos, alterações em configurações de segurança, ou detecção de possíveis ataques. Um sistema de resposta a incidentes automatizado executará ações predefinidas como bloqueio de contas, isolamento de sessões suspeitas, e coleta de evidências forenses.

## 7. Plano de Implementação

### 7.1 Metodologia de Desenvolvimento

O desenvolvimento seguirá metodologia ágil com sprints de duas semanas, permitindo entregas incrementais e feedback contínuo dos stakeholders. A equipe utilizará práticas de DevOps incluindo integração contínua (CI) e entrega contínua (CD), garantindo qualidade e velocidade no desenvolvimento.

Testes automatizados serão implementados em múltiplas camadas, incluindo testes unitários, testes de integração, testes de API, e testes end-to-end. Cobertura de código mínima de 80% será mantida, com foco especial em funcionalidades críticas de segurança e envio de mensagens.

Code review será obrigatório para todas as alterações, com pelo menos dois desenvolvedores revisando cada pull request. Ferramentas de análise estática de código identificarão potenciais vulnerabilidades de segurança e problemas de qualidade antes da integração.

### 7.2 Fases de Desenvolvimento

A Fase 1 focará no desenvolvimento da infraestrutura base, incluindo configuração do ambiente, implementação do sistema de autenticação, e criação das APIs fundamentais. Esta fase incluirá também a configuração do banco de dados PostgreSQL e a integração básica com o SQL Server existente.

A Fase 2 implementará as funcionalidades core de envio de mensagens, incluindo integração com provedores de email e WhatsApp, sistema de templates, e funcionalidades básicas de campanhas. Testes extensivos garantirão a confiabilidade dos envios em massa.

A Fase 3 desenvolverá a interface de usuário completa, incluindo todos os módulos planejados, dashboards, e funcionalidades avançadas. Esta fase incluirá também a implementação de relatórios e sistema de auditoria completo.

A Fase 4 focará em otimizações de performance, implementação de funcionalidades avançadas de segurança, e preparação para produção. Testes de carga e penetração serão realizados para validar a robustez do sistema.

### 7.3 Critérios de Aceitação

Cada funcionalidade desenvolvida deve atender a critérios específicos de aceitação, incluindo performance (tempo de resposta inferior a 2 segundos para 95% das operações), segurança (aprovação em testes de penetração), usabilidade (aprovação em testes com usuários reais), e confiabilidade (uptime mínimo de 99.5%).

O sistema deve ser capaz de processar pelo menos 10.000 envios simultâneos sem degradação significativa de performance. Todas as funcionalidades devem ser acessíveis e utilizáveis em dispositivos móveis, tablets e desktops com diferentes resoluções de tela.

Documentação completa deve ser fornecida, incluindo manual do usuário, documentação técnica, e guias de instalação e manutenção. Treinamento será fornecido para todos os usuários finais, garantindo adoção efetiva do sistema.

