# 🚀 CONT-AI - Sistema de Gestão Contábil com IA# 🚀 CONT-AI - Sistema de Gestão Contábil com IA# 📊 CONT-AI - Sistema de Gestão Contábil e Financeira com IA



Sistema completo de gestão contábil e fiscal com processamento inteligente de documentos e análise tributária automatizada.



## 📋 ÍndiceSistema completo de gestão contábil e fiscal com processamento inteligente de documentos e análise tributária automatizada.Sistema completo de gestão contábil e financeira com agentes de IA especializados, desenvolvido para oferecer uma visão integrada entre os aspectos financeiros (fluxo de caixa, pagamentos, recebimentos) e contábeis (DRE, plano de contas, obrigações fiscais) do negócio.



- [Características](#-características)

- [Tecnologias](#-tecnologias)

- [Pré-requisitos](#-pré-requisitos)## 📋 Índice## 🚀 Funcionalidades

- [Instalação](#-instalação)

- [Configuração](#-configuração)

- [Como Usar](#-como-usar)

- [Funcionalidades](#-funcionalidades)- [Características](#-características)### 💰 Dashboard Financeiro

- [Estrutura do Projeto](#-estrutura-do-projeto)

- [Solução de Problemas](#-solução-de-problemas)- [Tecnologias](#-tecnologias)**Foco: Gestão de Caixa e Pagamentos**

- [Requisitos de Sistema](#-requisitos-de-sistema)

- [Roadmap](#-roadmap)- [Pré-requisitos](#-pré-requisitos)

- [Licença](#-licença)

- [Autor](#-autor)- [Instalação](#-instalação)O dashboard financeiro concentra-se na gestão do fluxo de caixa e das operações de pagamento e recebimento:



## ✨ Características- [Configuração](#-configuração)



- 🤖 **Análise de Documentos com IA**: Extração automática de dados de NFe, NFSe, e outros documentos fiscais usando IA (OpenAI GPT-4, Anthropic Claude, Google Gemini, Groq Llama)- [Como Usar](#-como-usar)- **Contas a Pagar**: Controle de fornecedores, boletos, despesas operacionais

- 📊 **Dashboard Completo**: Visualização em tempo real de contas a pagar/receber, situação fiscal, e principais indicadores

- 👥 **Sistema Multi-Usuário**: Níveis de acesso (Geral e Senior) com fluxo de aprovações hierárquico- [Funcionalidades](#-funcionalidades)- **Contas a Receber**: Gestão de recebíveis de clientes, notas fiscais

- ✅ **Fluxo de Aprovações**: Aprovação de uploads para usuários de nível Geral

- 💼 **Gestão Completa**: Contas a pagar/receber, funcionários, terceiros, e documentos- [Estrutura do Projeto](#-estrutura-do-projeto)- **Contas Bancárias**: Saldos atuais e histórico de movimentações

- 📈 **Análise Tributária**: Cálculo automático de impostos (INSS, IRRF, ISS) com visualizações

- 🔐 **Segurança**: Sistema de autenticação com PBKDF2, recuperação de senha, e controle de acesso- [Solução de Problemas](#-solução-de-problemas)- **Status Automático**: 

- 📱 **Responsivo**: Interface adaptável para desktop e mobile

- [Requisitos de Sistema](#-requisitos-de-sistema)  - **Situação**: Pago/A Pagar (payables) | Recebido/A Receber (receivables)

## 🛠 Tecnologias

- [Roadmap](#-roadmap)  - **Status Temporal**: Em Dia | Com Atraso | Pendente

### Backend

- **Python 3.8+**- [Licença](#-licença)- **Agente IA Financeiro**: Especialista em matemática financeira, análise de fluxo de caixa, projeções e riscos

- **Streamlit**: Framework web

- **Supabase**: Banco de dados PostgreSQL + Storage- [Autor](#-autor)

- **python-dotenv**: Gerenciamento de variáveis de ambiente

### 📊 Dashboard Contábil  

### Inteligência Artificial

- **OpenAI GPT-4**: Análise de documentos## ✨ Características**Foco: Contabilidade e Conformidade Fiscal**

- **Anthropic Claude**: Análise alternativa

- **Google Gemini**: Análise alternativa

- **Groq Llama**: Análise alternativa

- **Tesseract OCR**: Extração de texto de imagens- 🤖 **Análise de Documentos com IA**: Extração automática de dados de NFe, NFSe, e outros documentos fiscais usando IA (OpenAI GPT-4, Anthropic Claude, Google Gemini)O dashboard contábil trata dos aspectos contábeis e de compliance:



### Processamento de Documentos- 📊 **Dashboard Completo**: Visualização em tempo real de contas a pagar/receber, situação fiscal, e principais indicadores

- **pdf2image**: Conversão PDF para imagem

- **pdfplumber**: Extração de texto de PDF- 👥 **Sistema Multi-Usuário**: Níveis de acesso (Geral e Senior) com fluxo de aprovações hierárquico- **DRE (Demonstração do Resultado do Exercício)**: Análise de receitas, custos e despesas

- **pytesseract**: Interface Python para Tesseract

- **Pillow (PIL)**: Manipulação de imagens- ✅ **Fluxo de Aprovações**: Aprovação de uploads para usuários de nível Geral- **Plano de Contas**: Estrutura contábil completa (ativo, passivo, receitas, despesas)



### Visualização- 💼 **Gestão Completa**: Contas a pagar/receber, funcionários, terceiros, e documentos- **Lançamentos Contábeis**: Registro de débitos e créditos

- **Plotly**: Gráficos interativos

- **Pandas**: Manipulação de dados- 📈 **Análise Tributária**: Cálculo automático de impostos (INSS, IRRF, ISS) com visualizações- **Obrigações Fiscais**: Acompanhamento de DCTF, SPED, DASN, etc.



## 📦 Pré-requisitos- 🔐 **Segurança**: Sistema de autenticação com PBKDF2, recuperação de senha, e controle de acesso- **Folha de Pagamento**: Gestão de eventos trabalhistas e encargos



### Para Executável (Usuários Finais)- 📱 **Responsivo**: Interface adaptável para desktop e mobile- **Gráficos de Evolução**: Visualização temporal de indicadores contábeis

- ✅ Windows 10/11 (64-bit)

- ✅ 8 GB RAM (mínimo)- **Agente IA Contábil**: Expert em contabilidade, legislação tributária e consultoria fiscal

- ✅ 500 MB espaço livre

- ✅ Conexão com internet## 🛠 Tecnologias

- ✅ Conta Supabase (gratuita)

- ✅ API Key de pelo menos um provedor de IA> **📌 Diferença-chave**: O dashboard **financeiro** responde "Tenho dinheiro para pagar?", enquanto o dashboard **contábil** responde "Qual foi meu resultado contábil?" e "Estou em conformidade fiscal?"



### Para Instalação Manual (Desenvolvedores)### Backend

- Python 3.8 ou superior

- pip (gerenciador de pacotes Python)- **Python 3.8+**## 🛠️ Instalação

- Tesseract OCR instalado

- Conta Supabase (gratuita)- **Streamlit**: Framework web

- API Key de pelo menos um provedor de IA

- **Supabase**: Banco de dados PostgreSQL + Storage```bash

## 📥 Instalação

- **python-dotenv**: Gerenciamento de variáveis de ambiente# 1. Clone o repositório

### Opção 1: Executável (Recomendado para Usuários Finais)

git clone [seu-repositorio]

1. **Baixe o executável**:

   - Download: `CONT-AI.exe` (125 MB)### Inteligência Artificial



2. **Crie o arquivo .env**:- **OpenAI GPT-4**: Análise de documentos# 2. Crie ambiente virtual

   - Crie um arquivo `.env` na mesma pasta do executável

   - Adicione apenas as credenciais do Supabase (veja [Configuração](#-configuração))- **Anthropic Claude**: Análise alternativapython -m venv venv



3. **Execute**:- **Google Gemini**: Análise alternativavenv\Scripts\activate  # Windows

   - Duplo clique em `CONT-AI.exe`

   - Aguarde a janela do navegador abrir automaticamente- **Tesseract OCR**: Extração de texto de imagenssource venv/bin/activate  # Linux/Mac

   - Acesso: `http://localhost:8502`



4. **Configure a IA**:

   - Após login, configure a IA pela interface (veja [Como Usar](#-como-usar))### Processamento de Documentos# 3. Instale dependências



### Opção 2: Instalação Manual (Desenvolvedores)- **pdf2image**: Conversão PDF para imagempip install -r requirements.txt



1. **Clone o repositório**:- **pdfplumber**: Extração de texto de PDF

```bash

git clone https://github.com/seu-usuario/CONT-AI.git- **pytesseract**: Interface Python para Tesseract# 4. Configure variáveis de ambiente

cd CONT-AI

```- **Pillow (PIL)**: Manipulação de imagens# Crie arquivo .env com:



2. **Crie um ambiente virtual**:SUPABASE_URL=sua_url_supabase

```bash

python -m venv venv### VisualizaçãoSUPABASE_KEY=sua_chave_supabase

```

- **Plotly**: Gráficos interativos

3. **Ative o ambiente virtual**:

   - **Windows**:- **Pandas**: Manipulação de dados# 5. Execute migração do banco de dados

     ```powershell

     venv\Scripts\activate# No Supabase SQL Editor, execute:

     ```

   - **Linux/Mac**:## 📦 Pré-requisitossql_migrations/add_situacao_field.sql

     ```bash

     source venv/bin/activate

     ```

### Para Executável (Usuários Finais)# 6. Popule dados iniciais (opcional)

4. **Instale as dependências**:

```bash- ✅ Windows 10/11 (64-bit)python scripts/populate_complete_dataset.py

pip install -r requirements.txt

```- ✅ 8 GB RAM (mínimo)



5. **Configure o arquivo .env** (veja [Configuração](#-configuração))- ✅ 500 MB espaço livre# 7. Execute a aplicação



6. **Execute o aplicativo**:- ✅ Conexão com internetstreamlit run app.py

```bash

streamlit run app.py```

```

### Para Instalação Manual (Desenvolvedores)

7. **Acesse no navegador**:

   - URL: `http://localhost:8501` ou `http://localhost:8502`- Python 3.8 ou superior## 📁 Estrutura do Projeto



## ⚙ Configuração- pip (gerenciador de pacotes Python)



### 1. Configuração do Banco de Dados (Supabase)- Tesseract OCR instalado```



Crie um arquivo `.env` na raiz do projeto com **APENAS** as credenciais do Supabase:- Conta Supabase (gratuita)CONT-AI/



```env- API Key de pelo menos um provedor de IA (OpenAI, Anthropic ou Google)├── app.py                          # Aplicação principal Streamlit

# Supabase (OBRIGATÓRIO)

SUPABASE_URL=sua_url_do_supabase├── auth.py                         # Autenticação de usuários

SUPABASE_KEY=sua_chave_do_supabase

```## 📥 Instalação├── database.py                     # Funções de banco de dados



**Como obter as credenciais:**├── requirements.txt                # Dependências Python

1. Acesse [supabase.com](https://supabase.com)

2. Crie um novo projeto (gratuito)### Opção 1: Executável (Recomendado para Usuários Finais)├── .env                           # Variáveis de ambiente (não versionado)

3. Vá em **Settings** → **API**

4. Copie:├── scripts/

   - `URL` → `SUPABASE_URL`

   - `anon public` → `SUPABASE_KEY`1. **Baixe o executável**:│   ├── populate_complete_dataset.py  # Popular dados de exemplo



> ⚠️ **Importante**: As API Keys de IA (OpenAI, Anthropic, Gemini, Groq) **NÃO** vão no `.env`. Elas são configuradas diretamente na interface da plataforma após o login.   - Download: `CONT-AI.exe`│   └── recalculate_statuses.py       # Recalcular status/situacao



**Estrutura de Tabelas Necessárias:**└── sql_migrations/



Execute os seguintes comandos SQL no Supabase SQL Editor:2. **Execute**:    └── add_situacao_field.sql      # Migração para campo situacao



```sql   - Duplo clique em `CONT-AI.exe````

-- Tabela de empresas

CREATE TABLE companies (   - Aguarde a janela do navegador abrir automaticamente

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    name TEXT NOT NULL,   - Acesso: `http://localhost:8502`

    cnpj TEXT UNIQUE NOT NULL,

    created_at TIMESTAMP DEFAULT NOW()## 🗄️ Banco de Dados

);

3. **Configure as API Keys** (veja [Configuração](#-configuração))

-- Tabela de usuários

CREATE TABLE users (### Estrutura de Dados

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    email TEXT UNIQUE NOT NULL,### Opção 2: Instalação Manual (Desenvolvedores)

    password_hash TEXT NOT NULL,

    name TEXT NOT NULL,O sistema utiliza Supabase (PostgreSQL) com tabelas organizadas por domínio:

    company_id UUID REFERENCES companies(id),

    access_level TEXT DEFAULT 'geral',1. **Clone o repositório**:

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW()```bash#### 📋 Cadastros Básicos

);

git clone https://github.com/seu-usuario/CONT-AI.git- **companies** - Empresas cadastradas (id, name, cnpj, tax_regime, logo_path)

-- Tabela de contas

CREATE TABLE bills (cd CONT-AI- **users** - Usuários do sistema (id, email, password_hash)

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    company_id UUID REFERENCES companies(id),```- **third_parties** - Clientes e fornecedores (id, company_id, name, cpf_cnpj, type)

    type TEXT NOT NULL,

    description TEXT,- **financial_categories** - Categorias de receitas/despesas (id, company_id, name, type)

    value NUMERIC,

    due_date DATE,2. **Crie um ambiente virtual**:

    status TEXT,

    category TEXT,```bash#### 💰 Módulo Financeiro (Gestão de Caixa)

    document_url TEXT,

    created_at TIMESTAMP DEFAULT NOW()python -m venv venv- **accounts_payable** - Contas a pagar

);

```  - Campos: id, company_id, description, amount, due_date, payment_date

-- Tabela de funcionários

CREATE TABLE employees (  - **situacao**: 'Pago' | 'A Pagar' (estado: foi pago?)

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    company_id UUID REFERENCES companies(id),3. **Ative o ambiente virtual**:  - **status**: 'Em Dia' | 'Com Atraso' | 'Pendente' (timing: quando foi pago?)

    name TEXT NOT NULL,

    cpf TEXT,   - **Windows**:  

    salary NUMERIC,

    admission_date DATE,     ```powershell- **accounts_receivable** - Contas a receber

    position TEXT,

    created_at TIMESTAMP DEFAULT NOW()     venv\Scripts\activate  - Campos: id, company_id, description, amount, due_date, receipt_date

);

     ```  - **situacao**: 'Recebido' | 'A Receber' (estado: foi recebido?)

-- Tabela de terceiros

CREATE TABLE third_parties (   - **Linux/Mac**:  - **status**: 'Em Dia' | 'Com Atraso' | 'Pendente' (timing: quando foi recebido?)

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    company_id UUID REFERENCES companies(id),     ```bash

    name TEXT NOT NULL,

    cnpj_cpf TEXT,     source venv/bin/activate- **bank_accounts** - Contas bancárias (id, company_id, bank_name, account_number, balance)

    type TEXT,

    created_at TIMESTAMP DEFAULT NOW()     ```- **bank_account_balances** - Histórico de saldos (id, bank_account_id, balance, as_of_date)

);

- **bank_transactions** - Transações bancárias (id, bank_account_id, description, amount, date)

-- Tabela de requisições de aprovação

CREATE TABLE approval_requests (4. **Instale as dependências**:

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    company_id UUID REFERENCES companies(id),```bash#### 📊 Módulo Contábil (Escrituração e Compliance)

    requester_id UUID REFERENCES users(id),

    document_type TEXT,pip install -r requirements.txt- **chart_of_accounts** - Plano de contas contábil

    document_data JSONB,

    status TEXT DEFAULT 'pending',```  - Estrutura hierárquica: 1.Ativo, 2.Passivo, 3.Patrimônio Líquido, 4.Receitas, 5.Despesas

    file_url TEXT,

    reviewed_by UUID REFERENCES users(id),  - Campos: id, company_id, account_code, account_name, account_type, parent_account_id

    reviewed_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW()5. **Configure o arquivo .env** (veja [Configuração](#-configuração))  

);

- **accounting_entries** - Lançamentos contábeis

-- Tabela de códigos de recuperação

CREATE TABLE recovery_codes (6. **Execute o aplicativo**:  - Débitos e créditos seguindo o método das partidas dobradas

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    email TEXT NOT NULL,```bash  - Campos: id, company_id, entry_date, description, debit_account_id, credit_account_id, amount

    code TEXT NOT NULL,

    expires_at TIMESTAMP NOT NULL,streamlit run app.py

    used BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT NOW()```- **tax_obligations** - Obrigações fiscais

);

```  - Tipos: DCTF, SPED, DASN, DARF, GPS, etc.



**Configuração do Storage:**7. **Acesse no navegador**:  - Campos: id, company_id, obligation_type, reference_period, due_date, status

1. No Supabase, vá em **Storage**

2. Crie um bucket chamado `documents`   - URL: `http://localhost:8501` ou `http://localhost:8502`

3. Defina as políticas de acesso (público ou privado conforme necessidade)

- **employees** - Funcionários (id, company_id, name, cpf, role, salary, admission_date)

### 2. Configuração das APIs de IA (Na Plataforma)

## ⚙ Configuração- **payroll_events** - Eventos de folha de pagamento (id, employee_id, event_type, amount, event_date)

As API Keys de IA são configuradas **diretamente na interface** após o login:



1. **Faça login** na plataforma

2. **Na sidebar**, clique em **"🤖 Configurar IA"**### 1. Configuração do Supabase### 📌 Schema de Situação e Status

3. **Escolha o modelo**:

   - Google Gemini

   - OpenAI GPT-4

   - Groq LlamaCrie um arquivo `.env` na raiz do projeto:**Importante**: Os valores no banco de dados estão em **PORTUGUÊS** (não em snake_case ou inglês).

   - Anthropic Claude

4. **Cole sua API Key** no campo

5. **Clique em "🔌 Conectar"**

6. **Aguarde** a confirmação **"🟢 IA Ativa"**```env#### Contas a Pagar (`accounts_payable`)



**Onde obter as API Keys:**# Supabase```

- **OpenAI**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

- **Anthropic**: [console.anthropic.com](https://console.anthropic.com)SUPABASE_URL=sua_url_do_supabasesituacao: 'Pago' | 'A Pagar'

- **Google Gemini**: [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

- **Groq**: [console.groq.com](https://console.groq.com)SUPABASE_KEY=sua_chave_do_supabase  └─ Representa se a conta foi paga ou não



> 💡 **Dica**: Você pode trocar de modelo a qualquer momento pela sidebar sem reiniciar a aplicação.```



> ⚠️ **Nota**: A configuração da IA é **por sessão**. Se fechar o navegador, precisará reconectar.status: 'Em Dia' | 'Com Atraso' | 'Pendente'  



### 3. Configuração do Tesseract OCR**Como obter as credenciais:**  ├─ Em Dia: Pago antes/no vencimento



**Windows:**1. Acesse [supabase.com](https://supabase.com)  ├─ Com Atraso: Pago após vencimento OU não pago e já venceu

1. Baixe o instalador: [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

2. Instale em `C:\Program Files\Tesseract-OCR`2. Crie um novo projeto (gratuito)  └─ Pendente: Não pago e ainda dentro do prazo

3. Adicione ao PATH ou configure no código:

```python3. Vá em **Settings** → **API**```

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

```4. Copie:



**Linux:**   - `URL` → `SUPABASE_URL`#### Contas a Receber (`accounts_receivable`)

```bash

sudo apt-get install tesseract-ocr   - `anon public` → `SUPABASE_KEY````

sudo apt-get install tesseract-ocr-por

```situacao: 'Recebido' | 'A Receber'



**Mac:****Estrutura de Tabelas Necessárias:**  └─ Representa se a conta foi recebida ou não

```bash

brew install tesseract

brew install tesseract-lang

```Execute os seguintes comandos SQL no Supabase SQL Editor:status: 'Em Dia' | 'Com Atraso' | 'Pendente'



## 📖 Como Usar  ├─ Em Dia: Recebido antes/no vencimento



### 1. Primeiro Acesso```sql  ├─ Com Atraso: Recebido após vencimento OU não recebido e já venceu



1. **Acesse o sistema**:-- Tabela de empresas  └─ Pendente: Não recebido e ainda dentro do prazo

   - Executável: Duplo clique em `CONT-AI.exe`

   - Manual: `streamlit run app.py`CREATE TABLE companies (```



2. **Crie sua conta**:    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

   - Na tela de login, clique em **"Criar Nova Conta"**

   - Preencha: Nome, Email, Senha    name TEXT NOT NULL,**Constraints SQL**:

   - **Importante**: A primeira conta criada terá acesso de **Senior**

    cnpj TEXT UNIQUE NOT NULL,```sql

3. **Configure sua empresa**:

   - Após login, vá em **"⚙️ Configurações"** → **"Empresa"**    created_at TIMESTAMP DEFAULT NOW()-- Contas a Pagar

   - Cadastre: Nome da Empresa, CNPJ

);CHECK (situacao IN ('Pago', 'A Pagar'))

### 2. Configurar IA

CHECK (status IN ('Em Dia', 'Com Atraso', 'Pendente'))

1. **Conecte um modelo de IA**:

   - Na **sidebar**, clique em **"🤖 Configurar IA"**-- Tabela de usuários

   - Escolha: Google Gemini, OpenAI GPT-4, Anthropic Claude, ou Groq Llama

   - Cole sua API Key no campoCREATE TABLE users (-- Contas a Receber

   - Clique em **"🔌 Conectar"**

   - Aguarde confirmação **"🟢 IA Ativa"** na sidebar    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),CHECK (situacao IN ('Recebido', 'A Receber'))



> 💡 **Importante**: Você precisa configurar a IA em cada sessão (sempre que abrir o sistema).    email TEXT UNIQUE NOT NULL,CHECK (status IN ('Em Dia', 'Com Atraso', 'Pendente'))



### 3. Upload de Documentos    password_hash TEXT NOT NULL,```



**Para Usuários Senior:**    name TEXT NOT NULL,

1. Vá em **"📤 Upload de Documentos"** (na sidebar)

2. Arraste ou selecione o arquivo (PDF, JPG, PNG)    company_id UUID REFERENCES companies(id),### 🔄 Histórico de Migrações

3. Escolha o tipo de documento (NFe, NFSe, Recibo, etc.)

4. Clique em **"Processar com IA"**    access_level TEXT DEFAULT 'geral',

5. Revise os dados extraídos

6. Confirme para salvar    is_active BOOLEAN DEFAULT TRUE,#### ✅ Migração: Normalização para Português (Novembro 2025)



**Para Usuários Geral:**    created_at TIMESTAMP DEFAULT NOW()

1. Upload do documento (mesmos passos)

2. Sistema cria **Requisição de Aprovação**);**Motivação**: Eliminar camada de tradução entre banco de dados e interface.

3. Aguarde aprovação de um usuário Senior

4. Após aprovação, documento é processado



### 4. Gerenciar Usuários (Apenas Senior)-- Tabela de contas**Mudanças**:



1. Vá em **"👥 Usuários"**CREATE TABLE bills (- ❌ **Antes**: Valores em inglês/snake_case no BD → conversão em queries → tradução no app → display em português

2. Clique em **"Adicionar Novo Usuário"**

3. Preencha:    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),- ✅ **Depois**: Valores em português no BD → leitura direta → uso direto → display em português

   - Nome

   - Email    company_id UUID REFERENCES companies(id),

   - Senha temporária

   - Nível de acesso (Geral ou Senior)    type TEXT NOT NULL,**Fluxo de Dados (Antigo)**:

4. Salve

    description TEXT,```

### 5. Aprovar Uploads (Apenas Senior)

    value NUMERIC,DB('paid','pending') → Query(converte) → App(traduz) → Display('Pago','Pendente')

1. Vá em **"✅ Aprovações"**

2. Visualize lista de requisições pendentes    due_date DATE,```

3. Para cada requisição:

   - Clique em **"Ver Documento"** para revisar    status TEXT,

   - Escolha: **Aprovar** ou **Rejeitar**

   - Documento aprovado é processado automaticamente    category TEXT,**Fluxo de Dados (Novo)**:



### 6. Recuperar Senha    document_url TEXT,```



1. Na tela de login, clique em **"Esqueci minha senha"**    created_at TIMESTAMP DEFAULT NOW()DB('Pago','Pendente') → Query(lê direto) → App(usa direto) → Display('Pago','Pendente')

2. Digite seu email cadastrado

3. Sistema gera código de 6 dígitos (exibido na tela));```

4. **Importante**: Copie o código imediatamente (válido por 30 minutos)

5. Clique em **"Já tenho o código"**

6. Insira:

   - Email-- Tabela de funcionários**Alterações Realizadas**:

   - Código de 6 dígitos

   - Nova senha (mínimo 6 caracteres)CREATE TABLE employees (1. Atualização de valores no banco de dados

7. Confirme e faça login com a nova senha

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),2. Remoção de funções de conversão em `database.py`

## 🎯 Funcionalidades

    company_id UUID REFERENCES companies(id),3. Atualização de constraints para aceitar valores em português

### Dashboard

- 📊 Resumo financeiro (a pagar, a receber, saldo)    name TEXT NOT NULL,4. Simplificação de lógica de filtros em `app.py`

- 📅 Contas vencendo nos próximos 7 dias

- 📈 Gráficos de situação fiscal    cpf TEXT,5. Remoção completa da camada de tradução

- 🔔 Alertas de vencimentos

    salary NUMERIC,

### Contas a Pagar/Receber

- ➕ Cadastro manual de contas    admission_date DATE,**Benefícios**:

- 📤 Upload de documentos com extração automática

- 📝 Edição e exclusão    position TEXT,- ✅ Menos processamento (sem conversões)

- 🔍 Filtros por status, categoria, período

- 💰 Cálculo automático de impostos (INSS, IRRF, ISS)    created_at TIMESTAMP DEFAULT NOW()- ✅ Menos pontos de falha



### Gestão de Funcionários);- ✅ Código mais simples e manutenível

- 👤 Cadastro completo (CPF, cargo, salário, admissão)

- 📊 Visualização em tabela- ✅ Performance melhorada

- ✏️ Edição de dados

- 🗑️ Exclusão de registros-- Tabela de terceiros- ✅ Alinhamento completo BD ↔ App ↔ UI



### Gestão de TerceirosCREATE TABLE third_parties (

- 🏢 Cadastro de fornecedores e prestadores

- 📋 Informações de CNPJ/CPF    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

- 🏷️ Categorização por tipo

    company_id UUID REFERENCES companies(id),## 🤖 Agentes de IA

### Upload e Processamento

- 📄 Suporte a PDF, JPG, PNG    name TEXT NOT NULL,

- 🤖 Extração automática via IA

- 🔍 OCR para documentos escaneados    cnpj_cpf TEXT,### 💰 Agente Financeiro

- ✅ Validação de dados extraídos

- 💾 Armazenamento seguro no Supabase Storage    type TEXT,**Especialidade**: Matemática Financeira e Gestão de Caixa



### Segurança    created_at TIMESTAMP DEFAULT NOW()

- 🔐 Autenticação com hash PBKDF2 (100.000 iterações)

- 👥 Níveis de acesso (Geral, Senior));**Capacidades**:

- ✅ Fluxo de aprovações

- 🔑 Recuperação de senha com código de 6 dígitos- 📊 Análise de fluxo de caixa (entradas vs saídas)

- 🛡️ Sessões persistentes

-- Tabela de requisições de aprovação- 💳 Gestão de contas a pagar e receber

## 📁 Estrutura do Projeto

CREATE TABLE approval_requests (- 📈 Projeções financeiras e análise de riscos

```

CONT-AI/    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),- 💰 Cálculo de indicadores de liquidez

├── app.py                  # Aplicação principal Streamlit

├── database.py             # Funções de interação com Supabase    company_id UUID REFERENCES companies(id),- 🎯 Sugestões de otimização de capital de giro

├── auth.py                 # Autenticação e hash de senha

├── launcher.py             # Entry point para executável    requester_id UUID REFERENCES users(id),

├── CONT-AI.spec            # Configuração PyInstaller

├── build_exe.bat           # Script de build do executável    document_type TEXT,**Contexto de Atuação**:

├── requirements.txt        # Dependências Python

├── .env                    # Variáveis de ambiente (NÃO COMITAR!)    document_data JSONB,- Período analisado (mês/ano)

├── .env.example            # Template do .env

├── .gitignore              # Arquivos ignorados pelo Git    status TEXT DEFAULT 'pending',- Contas pagas vs a pagar

├── README.md               # Esta documentação

├── venv/                   # Ambiente virtual Python    file_url TEXT,- Contas recebidas vs a receber

├── __pycache__/            # Cache Python

├── build/                  # Arquivos temporários do build    reviewed_by UUID REFERENCES users(id),- Status temporal (em dia, com atraso, pendente)

└── dist/                   # Executável gerado (após build)

    └── CONT-AI.exe         # Executável (125 MB)    reviewed_at TIMESTAMP,- Saldos bancários

```

    created_at TIMESTAMP DEFAULT NOW()

## 🔧 Solução de Problemas

);**Exemplo de Pergunta**: 

### Erro: "Cliente Supabase não inicializado"

**Causa**: Credenciais Supabase inválidas ou ausentes- "Qual o valor total de contas a pagar com atraso em 2024?"



**Solução**:-- Tabela de códigos de recuperação- "Quantas contas a receber estão pendentes para janeiro?"

1. Verifique o arquivo `.env`

2. Confirme que `SUPABASE_URL` e `SUPABASE_KEY` estão corretosCREATE TABLE recovery_codes (- "Qual meu fluxo de caixa projetado para o próximo trimestre?"

3. Teste a conexão no Supabase Dashboard

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

### Erro: "API Key não configurada" ou "IA não conectada"

**Causa**: Nenhum modelo de IA foi configurado na sessão    email TEXT NOT NULL,### 📊 Agente Contábil



**Solução**:    code TEXT NOT NULL,**Especialidade**: Contabilidade, Legislação e Compliance Fiscal

1. **Na sidebar**, clique em **"🤖 Configurar IA"**

2. Escolha um modelo (OpenAI, Gemini, Anthropic, ou Groq)    expires_at TIMESTAMP NOT NULL,

3. Cole sua API Key válida

4. Clique em **"🔌 Conectar"**    used BOOLEAN DEFAULT FALSE,**Capacidades**:

5. Verifique se aparece **"🟢 IA Ativa"** na sidebar

    created_at TIMESTAMP DEFAULT NOW()- 📋 Análise de DRE (Demonstração do Resultado do Exercício)

> 💡 **Nota**: A configuração da IA é **por sessão**. Se fechar o navegador, precisará reconectar.

);- 🏛️ Orientação sobre obrigações fiscais (DCTF, SPED, DASN, etc.)

### Erro: "Tesseract não encontrado"

**Causa**: Tesseract OCR não instalado ou não no PATH```- 📊 Consultoria tributária e planejamento fiscal



**Solução Windows**:- 💼 Análise de estrutura patrimonial (balanço)

1. Baixe: [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

2. Instale em `C:\Program Files\Tesseract-OCR`**Configuração do Storage:**- 📑 Interpretação de plano de contas

3. Adicione ao PATH do sistema

1. No Supabase, vá em **Storage**- 👥 Orientação sobre eventos de folha de pagamento

**Solução Linux**:

```bash2. Crie um bucket chamado `documents`

sudo apt-get install tesseract-ocr tesseract-ocr-por

```3. Defina as políticas de acesso (público ou privado conforme necessidade)**Contexto de Atuação**:



### Login não funciona- Regime tributário da empresa (Simples, Lucro Real, Lucro Presumido)

**Possíveis Causas**:

1. Senha incorreta### 2. Configuração das APIs de IA- Plano de contas estruturado

2. Email não cadastrado

3. Usuário inativo- Lançamentos contábeis (débito/crédito)



**Solução**:Adicione pelo menos uma das seguintes chaves ao `.env`:- Obrigações fiscais e prazos

1. Verifique email/senha

2. Use **"Esqueci minha senha"** para resetar- Eventos trabalhistas

3. Contate administrador para ativar conta

```env

### Upload falha ao processar documento

**Possíveis Causas**:# OpenAI (Recomendado)**Exemplo de Pergunta**:

1. IA não configurada

2. Arquivo corrompidoOPENAI_API_KEY=sua_chave_openai- "Qual foi meu resultado contábil (lucro/prejuízo) em 2024?"

3. Formato não suportado

4. API de IA sem créditos- "Quais obrigações fiscais vencem este mês?"



**Solução**:# OU Anthropic- "Como devo classificar contabilmente uma compra de equipamento?"

1. Configure a IA pela sidebar (🤖 Configurar IA)

2. Tente outro arquivoANTHROPIC_API_KEY=sua_chave_anthropic- "Qual o impacto tributário de contratar um novo funcionário?"

3. Use apenas PDF, JPG ou PNG

4. Verifique saldo da API no provedor de IA



## 💻 Requisitos de Sistema# OU Google Gemini### 🔄 Integração entre Agentes



### MínimoGEMINI_API_KEY=sua_chave_gemini

- **OS**: Windows 10 (64-bit), Linux, macOS

- **RAM**: 8 GB```Embora especializados em áreas diferentes, os agentes compartilham dados:

- **Processador**: Intel Core i5 ou equivalente

- **Espaço**: 500 MB livres

- **Internet**: Conexão estável (para APIs)

**Como obter:****Fluxo de Informação**:

### Recomendado

- **OS**: Windows 11 (64-bit)- **OpenAI**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)```

- **RAM**: 16 GB

- **Processador**: Intel Core i7 ou equivalente- **Anthropic**: [console.anthropic.com](https://console.anthropic.com)┌─────────────────────┐         ┌──────────────────────┐

- **Espaço**: 2 GB livres

- **Internet**: Conexão de banda larga- **Google**: [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)│  Agente Financeiro  │ ◄─────► │   Agente Contábil    │



## 🗺 Roadmap│  (Caixa e Fluxo)    │         │  (Resultado e Fiscal)│



### v2.0 (Próxima Versão)### 3. Configuração do Tesseract OCR└─────────────────────┘         └──────────────────────┘

- [ ] Notificações por email

- [ ] Relatórios em PDF         │                                │

- [ ] Integração com bancos (open finance)

- [ ] Backup automático**Windows:**         ├── Contas a Pagar              ├── Lançamentos

- [ ] Logs de auditoria

1. Baixe o instalador: [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)         ├── Contas a Receber            ├── Plano de Contas

### v2.1 (Futuro)

- [ ] App mobile (iOS/Android)2. Instale em `C:\Program Files\Tesseract-OCR`         ├── Saldos Bancários            ├── Obrigações Fiscais

- [ ] Integração com SPED

- [ ] Dashboard personalizado3. Adicione ao PATH ou configure no código:         └── Transações                  └── Folha de Pagamento

- [ ] IA preditiva para fluxo de caixa

- [ ] Multi-empresa por usuário```python```



## 📦 Distribuiçãopytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



### Para Distribuir o Executável:```**Exemplo de Pergunta Integrada**: 



1. **Gerar Build:**- "Tenho dinheiro em caixa para pagar os impostos que vencem este mês?" 

   ```batch

   build_exe.bat**Linux:**  → Requer dados **financeiros** (saldo) + **contábeis** (obrigações fiscais)

   ```

```bash

2. **Incluir na Distribuição:**

   - `dist/CONT-AI.exe` (executável)sudo apt-get install tesseract-ocr

   - `.env.example` (template apenas com Supabase)

   - `README.md` (instruções completas)sudo apt-get install tesseract-ocr-por## 📚 Documentação Adicional



3. **Instruções para Usuário Final:**```

   - Baixar CONT-AI.exe

   - Criar arquivo `.env` com credenciais Supabase- `README_MIGRACAO_SITUACAO.md` - Detalhes técnicos sobre migração do campo situacao

   - Duplo clique no executável

   - Após login, configurar IA pela interface (Sidebar → 🤖 Configurar IA)**Mac:**- Logs de debug disponíveis durante execução (procure por `🔴 DEBUG` no terminal)



## 📄 Licença```bash



Este projeto é de propriedade privada. Todos os direitos reservados.brew install tesseract## 🐛 Troubleshooting



**Proibido**:brew install tesseract-lang

- ❌ Redistribuição

- ❌ Uso comercial sem autorização```### Agente IA retorna dados zerados

- ❌ Modificação sem autorização



**Permitido**:

- ✅ Uso pessoal### Arquivo .env Completo (Exemplo)**Sintoma**: Dashboard mostra valores corretos, mas agente retorna "0 contas" ou valores zerados.

- ✅ Teste e avaliação

- ✅ Uso comercial com licença



Para adquirir licença comercial, entre em contato: leo.cvsm@hotmail.com```env**Causa Comum**: Confusão entre terminologia "atrasadas" vs "não pagas".



## 👤 Autor# Supabase



**Leonel Carvalho**SUPABASE_URL=https://xxxxxxxxxxx.supabase.co**Solução**:

- 📧 Email: leo.cvsm@hotmail.com

- 💼 LinkedIn: [linkedin.com/in/leonelcarvalho](https://linkedin.com/in/leonelcarvalho)SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...1. Verifique os logs no terminal - procure por:

- 🐙 GitHub: [github.com/leonelcarvalho](https://github.com/leonelcarvalho)

   ```

## 🤝 Contribuindo

# IA (escolha pelo menos uma)   🔴 DEBUG - CONTAS COM ATRASO DETECTADAS

Este é um projeto privado. Contribuições são aceitas mediante aprovação prévia.

OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx   🔍 DEBUG - Período ajustado

**Para sugerir melhorias**:

1. Envie email para leo.cvsm@hotmail.comANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx   🤖 DEBUG - DADOS QUE SERÃO ENVIADOS AO AGENTE

2. Descreva a melhoria ou bug

3. Aguarde respostaGEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxx   ```



---```



**Desenvolvido com ❤️ usando Python, Streamlit e IA**2. Verifique se o período foi corretamente detectado:



*Última atualização: Novembro 2024*## 📖 Como Usar   - Se perguntar "em 2024", o agente deve ajustar para o ano completo


   - Logs mostrarão: `Período ajustado para: 2024-01-01 a 2024-12-31`

### 1. Primeiro Acesso

3. Execute a pergunta de forma explícita:

1. **Acesse o sistema**:   ```

   - Executável: Duplo clique em `CONT-AI.exe`   ❌ Evite: "Quantas contas vencidas?"

   - Manual: `streamlit run app.py`   ✅ Prefira: "Qual o valor de contas a pagar com atraso em 2024?"

   ```

2. **Crie sua conta**:

   - Na tela de login, clique em **"Criar Nova Conta"**### Dashboard mostra dados corretos, agente não

   - Preencha: Nome, Email, Senha

   - **Importante**: A primeira conta criada terá acesso de **Administrador****Causa**: Diferença entre período do dashboard vs período da pergunta.



3. **Configure sua empresa**:**Verificação**:

   - Após login, vá em **"⚙️ Configurações"** → **"Empresa"**- Dashboard pode estar mostrando "todos os períodos"

   - Cadastre: Nome da Empresa, CNPJ- Agente responde ao período específico da pergunta

- Compare os filtros aplicados

### 2. Configurar IA

**Solução**: Especifique o período na pergunta:

1. **Escolha o modelo**:```

   - Vá em **"⚙️ Configurações"** → **"Configurar IA"**"Qual o total de contas a pagar com atraso no período de janeiro a março de 2024?"

   - Selecione: OpenAI GPT-4, Anthropic Claude, ou Google Gemini```

   - Confirme que a API Key está configurada no `.env`

### Erro: check constraint violation

### 3. Upload de Documentos

**Sintoma**: Ao inserir/atualizar registro, erro `violates check constraint`.

**Para Usuários Senior:**

1. Vá em **"📤 Upload de Documentos"****Causa**: Tentativa de inserir valores em inglês/snake_case em campos que aceitam apenas português.

2. Arraste ou selecione o arquivo (PDF, JPG, PNG)

3. Escolha o tipo de documento (NFe, NFSe, Recibo, etc.)**Solução**: Execute a migração de valores:

4. Clique em **"Processar com IA"**```sql

5. Revise os dados extraídos-- Atualizar valores para português

6. Confirme para salvarUPDATE accounts_payable 

SET situacao = CASE 

**Para Usuários Geral:**    WHEN payment_date IS NOT NULL THEN 'Pago' 

1. Upload do documento (mesmos passos)    ELSE 'A Pagar' 

2. Sistema cria **Requisição de Aprovação**END,

3. Aguarde aprovação de um usuário Seniorstatus = CASE 

4. Após aprovação, documento é processado    WHEN payment_date IS NOT NULL AND payment_date <= due_date THEN 'Em Dia'

    WHEN payment_date IS NOT NULL AND payment_date > due_date THEN 'Com Atraso'

### 4. Gerenciar Usuários (Apenas Senior)    WHEN payment_date IS NULL AND CURRENT_DATE > due_date THEN 'Com Atraso'

    ELSE 'Pendente'

1. Vá em **"👥 Usuários"**END;

2. Clique em **"Adicionar Novo Usuário"**

3. Preencha:-- Verificar valores atualizados

   - NomeSELECT DISTINCT situacao, status FROM accounts_payable;

   - Email-- Deve retornar apenas valores em português

   - Senha temporária```

   - Nível de acesso (Geral ou Senior)

4. Usuário receberá credenciais por email (se configurado)## 📝 Contribuindo



### 5. Aprovar Uploads (Apenas Senior)Ao fazer alterações no código:



1. Vá em **"✅ Aprovações"**1. **Mantenha valores em português** no banco de dados

2. Visualize lista de requisições pendentes2. **Não adicione camadas de tradução** - leia valores diretamente

3. Para cada requisição:3. **Use DEBUG logs** para diagnosticar problemas de dados

   - Clique em **"Ver Documento"** para revisar4. **Documente mudanças** no schema ou fluxo de dados

   - Escolha: **Aprovar** ou **Rejeitar**

   - Documento aprovado é processado automaticamente

## 🔧 Tecnologias

### 6. Recuperar Senha

- **Frontend**: Streamlit

1. Na tela de login, clique em **"Esqueci minha senha"**- **Backend**: Python 3.11+

2. Digite seu email cadastrado- **Banco de Dados**: Supabase (PostgreSQL)

3. Sistema gera código de 6 dígitos (exibido na tela)- **IA**: Google Gemini, OpenAI GPT-4, Groq, Anthropic Claude

4. **Importante**: Copie o código imediatamente (válido por 30 minutos)- **Gráficos**: Plotly

5. Clique em **"Já tenho o código"**- **Manipulação de Dados**: Pandas

6. Insira:

   - Email## � Licença

   - Código de 6 dígitos

   - Nova senha (mínimo 6 caracteres)Projeto educacional - I2A2 Course

7. Confirme e faça login com a nova senha

## 👨‍� Autor

## 🎯 Funcionalidades

Leonel - Desafio Final I2A2 Course

### Dashboard

- 📊 Resumo financeiro (a pagar, a receber, saldo)
- 📅 Contas vencendo nos próximos 7 dias
- 📈 Gráficos de situação fiscal
- 🔔 Alertas de vencimentos

### Contas a Pagar/Receber
- ➕ Cadastro manual de contas
- 📤 Upload de documentos com extração automática
- 📝 Edição e exclusão
- 🔍 Filtros por status, categoria, período
- 💰 Cálculo automático de impostos (INSS, IRRF, ISS)

### Gestão de Funcionários
- 👤 Cadastro completo (CPF, cargo, salário, admissão)
- 📊 Visualização em tabela
- ✏️ Edição de dados
- 🗑️ Exclusão de registros

### Gestão de Terceiros
- 🏢 Cadastro de fornecedores e prestadores
- 📋 Informações de CNPJ/CPF
- 🏷️ Categorização por tipo

### Upload e Processamento
- 📄 Suporte a PDF, JPG, PNG
- 🤖 Extração automática via IA
- 🔍 OCR para documentos escaneados
- ✅ Validação de dados extraídos
- 💾 Armazenamento seguro no Supabase Storage

### Segurança
- 🔐 Autenticação com hash PBKDF2 (100.000 iterações)
- 👥 Níveis de acesso (Geral, Senior)
- ✅ Fluxo de aprovações
- 🔑 Recuperação de senha com código de 6 dígitos
- 🛡️ Sessões persistentes

## 📁 Estrutura do Projeto

```
CONT-AI/
├── app.py                  # Aplicação principal Streamlit
├── database.py             # Funções de interação com Supabase
├── auth.py                 # Autenticação e hash de senha
├── launcher.py             # Entry point para executável
├── CONT-AI.spec            # Configuração PyInstaller
├── build_exe.bat           # Script de build do executável
├── requirements.txt        # Dependências Python
├── .env                    # Variáveis de ambiente (não comitar!)
├── .gitignore              # Arquivos ignorados pelo Git
├── README.md               # Esta documentação
├── venv/                   # Ambiente virtual Python
├── __pycache__/            # Cache Python
└── dist/                   # Executável gerado (após build)
    └── CONT-AI.exe
```

## 🔧 Solução de Problemas

### Erro: "Cliente Supabase não inicializado"
**Causa**: Credenciais Supabase inválidas ou ausentes

**Solução**:
1. Verifique o arquivo `.env`
2. Confirme que `SUPABASE_URL` e `SUPABASE_KEY` estão corretos
3. Teste a conexão no Supabase Dashboard

### Erro: "API Key não configurada" ou "IA não conectada"
**Causa**: Nenhum modelo de IA foi configurado na sessão

**Solução**:
1. **Na sidebar**, clique em **"🤖 Configurar IA"**
2. Escolha um modelo (OpenAI, Gemini, Anthropic, ou Groq)
3. Cole sua API Key válida
4. Clique em **"🔌 Conectar"**
5. Verifique se aparece **"🟢 IA Ativa"** na sidebar

> 💡 **Nota**: A configuração da IA é **por sessão**. Se fechar o navegador, precisará reconectar.

### Erro: "Tesseract não encontrado"
**Causa**: Tesseract OCR não instalado ou não no PATH

**Solução Windows**:
1. Baixe: [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Instale em `C:\Program Files\Tesseract-OCR`
3. Adicione ao PATH do sistema

**Solução Linux**:
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-por
```

### Login não funciona
**Possíveis Causas**:
1. Senha incorreta
2. Email não cadastrado
3. Usuário inativo

**Solução**:
1. Verifique email/senha
2. Use **"Esqueci minha senha"** para resetar
3. Contate administrador para ativar conta

### Upload falha ao processar documento
**Possíveis Causas**:
1. Arquivo corrompido
2. Formato não suportado
3. API de IA sem créditos

**Solução**:
1. Tente outro arquivo
2. Use PDF, JPG ou PNG
3. Verifique saldo da API no provedor de IA

## 💻 Requisitos de Sistema

### Mínimo
- **OS**: Windows 10 (64-bit), Linux, macOS
- **RAM**: 8 GB
- **Processador**: Intel Core i5 ou equivalente
- **Espaço**: 500 MB livres
- **Internet**: Conexão estável (para APIs)

### Recomendado
- **OS**: Windows 11 (64-bit)
- **RAM**: 16 GB
- **Processador**: Intel Core i7 ou equivalente
- **Espaço**: 2 GB livres
- **Internet**: Conexão de banda larga

## 🗺 Roadmap

### v2.0 (Próxima Versão)
- [ ] Notificações por email
- [ ] Relatórios em PDF
- [ ] Integração com bancos (open finance)
- [ ] Backup automático
- [ ] Logs de auditoria

### v2.1 (Futuro)
- [ ] App mobile (iOS/Android)
- [ ] Integração com SPED
- [ ] Dashboard personalizado
- [ ] IA preditiva para fluxo de caixa
- [ ] Multi-empresa por usuário

## 📄 Licença

Este projeto é de propriedade privada. Todos os direitos reservados.

**Proibido**:
- ❌ Redistribuição
- ❌ Uso comercial sem autorização
- ❌ Modificação sem autorização

**Permitido**:
- ✅ Uso pessoal
- ✅ Teste e avaliação
- ✅ Uso comercial com licença

Para adquirir licença comercial, entre em contato: leo.cvsm@hotmail.com

## 👤 Autor

**Leonel Carvalho**
- 📧 Email: leo.cvsm@hotmail.com
- 💼 LinkedIn: [linkedin.com/in/leonelcarvalho](https://linkedin.com/in/leonelcarvalho)
- 🐙 GitHub: [github.com/leonelcarvalho](https://github.com/leonelcarvalho)

## 🤝 Contribuindo

Este é um projeto privado. Contribuições são aceitas mediante aprovação prévia.

**Para sugerir melhorias**:
1. Envie email para leo.cvsm@hotmail.com
2. Descreva a melhoria ou bug
3. Aguarde resposta

---

**Desenvolvido com ❤️ usando Python, Streamlit e IA**

*Última atualização: Novembro 2024*
