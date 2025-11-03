# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import hashlib
import secrets
from PIL import Image
import io
import base64
import time
import re
import calendar

# Importa módulos locais
from database import *
from auth import authenticate_user, register_user

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do Tesseract OCR (descomente e ajuste o caminho se necessário)
# No Windows, o caminho padrão é:
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configuração da página
st.set_page_config(
    page_title="Cont-AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def format_cpf(cpf: str) -> str:
    """Formata CPF para o padrão 000.000.000-00"""
    cpf = re.sub(r'\D', '', cpf)  # Remove caracteres não numéricos
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

def validate_cpf(cpf: str) -> bool:
    """Valida se CPF é válido (apenas formato básico)"""
    cpf = re.sub(r'\D', '', cpf)  # Remove caracteres não numéricos
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais (CPFs inválidos conhecidos)
    if cpf == cpf[0] * 11:
        return False
    
    return True

def update_user_password(user_id: str, new_password_hash: str):
    """Atualiza a senha de um usuário (função auxiliar para recuperação de senha)"""
    try:
        from database import supabase
        if not supabase:
            return False
        
        response = (
            supabase.table('users')
            .update({'password_hash': new_password_hash})
            .eq('id', user_id)
            .execute()
        )
        return bool(response.data)
    except Exception as e:
        print(f"❌ Erro ao atualizar senha: {e}")
        return False

def show_module_header(title: str, icon: str = "📊", show_date_range: bool = False, module: str = "financial"):
    """Mostra o cabeçalho padrão de módulo com logo e informações da empresa"""
    if st.session_state.company:
        # Container para o cabeçalho
        with st.container():
            # Área de logo e título
            header_col1, header_col2 = st.columns([2, 1])
            
            with header_col1:
                # Logo e informações da empresa
                col_logo, col_info = st.columns([1, 3])
                
                with col_logo:
                    if st.session_state.company.get('logo_path'):
                        st.markdown(f"""
                            <div class="company-logo-container">
                                <img src="{st.session_state.company['logo_path']}" class="company-logo" alt="Logo">
                            </div>
                        """, unsafe_allow_html=True)
                
                with col_info:
                    st.markdown(f"# {icon} {title}")
                    st.markdown(f"""
                        **{st.session_state.company['name']}**  
                        CNPJ: {st.session_state.company['cnpj']} • {st.session_state.company['tax_regime']}
                    """)
            
            # Seletor de datas
            if show_date_range:
                with header_col2:
                    date_range_key = f"{module}_date_range"
                    st.markdown("#### Período de Análise")
                    
                    # Limites dinâmicos para evitar erros quando o padrão é a data de hoje
                    min_bound = datetime(2000, 1, 1).date()
                    max_bound = (datetime.now() + timedelta(days=365*5)).date()

                    new_date_range = st.date_input(
                        "Selecione o período",
                        value=st.session_state.get(f"{date_range_key}_{title.lower().replace(' ', '_')}", st.session_state[date_range_key]),
                        min_value=min_bound,
                        max_value=max_bound,
                        format="DD/MM/YYYY",
                        key=f"{module}_date_input_{title.lower().replace(' ', '_')}",
                        help="Selecione a data inicial e final do período arrastando o mouse ou clicando nas datas desejadas",
                    )
                    
                    if isinstance(new_date_range, tuple) and len(new_date_range) == 2:
                        start_date, end_date = new_date_range
                        if start_date <= end_date:
                            current_range = st.session_state.get(date_range_key, (None, None))
                            if current_range != new_date_range:
                                # Atualiza o state com as novas datas
                                st.session_state[date_range_key] = new_date_range
                                # Marca que o usuário definiu manualmente o período
                                st.session_state[f"{module}_date_range_user_set"] = True
                                # Limpa o cache dos dados do DRE para forçar recarregamento
                                cache_keys = [f"{module}_dre_data", "financial_dre_data"]
                                for key in cache_keys:
                                    if key in st.session_state:
                                        del st.session_state[key]
                                st.rerun()
                        else:
                            st.error("A data inicial deve ser menor ou igual à data final")
            
            st.markdown("---")

    else:
        st.markdown(f'<h1 class="main-header">{icon} {title}</h1>', unsafe_allow_html=True)

def format_currency(value: float) -> str:
    """Formata valor como moeda brasileira"""
    return f"R$ {value:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

def format_payment_status(bill: dict) -> str:
    """
    Formata o status de pagamento de forma clara
    
    Retorna:
    - "Em Dia" - pago antes/no vencimento
    - "Com Atraso" - pago após vencimento ou não pago e vencido
    - "Pendente" - não pago, ainda no prazo
    """
    situacao = bill.get('situacao', '')  # 'Pago' ou 'A Pagar'
    status = bill.get('status', '')      # 'Em Dia', 'Com Atraso', 'Pendente'
    
    if status == 'Em Dia':
        return '✅ Em Dia'
    elif status == 'Com Atraso':
        return '� Com Atraso'
    else:  # pendente
        return '🕒 Pendente'

def format_receipt_status(bill: dict) -> str:
    """
    Formata o status de recebimento de forma clara
    
    Retorna:
    - "Em Dia" - recebido antes/no vencimento
    - "Com Atraso" - recebido após vencimento ou não recebido e vencido
    - "Pendente" - não recebido, ainda no prazo
    """
    situacao = bill.get('situacao', '')  # 'Recebido' ou 'A Receber'
    status = bill.get('status', '')      # 'Em Dia', 'Com Atraso', 'Pendente'
    
    if status == 'Em Dia':
        return '✅ Em Dia'
    elif status == 'Com Atraso':
        return '� Com Atraso'
    else:  # pendente
        return '🕒 Pendente'

def validate_cnpj(cnpj: str) -> bool:
    """Valida CNPJ"""
    import re
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    if len(cnpj) != 14:
        return False
    
    if cnpj == cnpj[0] * 14:
        return False
    
    def calc_digit(cnpj_partial, weights):
        sum_val = sum(int(digit) * weight for digit, weight in zip(cnpj_partial, weights))
        remainder = sum_val % 11
        return 0 if remainder < 2 else 11 - remainder
    
    weights_first = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights_second = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    
    first_digit = calc_digit(cnpj[:12], weights_first)
    second_digit = calc_digit(cnpj[:13], weights_second)
    
    return cnpj[-2:] == f"{first_digit}{second_digit}"

def calculate_simples_nacional_tax(revenue: float, activity_annex: str = "III") -> dict:
    """Calcula imposto do Simples Nacional"""
    faixas = [
        {"limite": 180000, "aliquota": 0.06, "deducao": 0},
        {"limite": 360000, "aliquota": 0.112, "deducao": 9360},
        {"limite": 720000, "aliquota": 0.135, "deducao": 17640},
        {"limite": 1800000, "aliquota": 0.16, "deducao": 35640},
        {"limite": 3600000, "aliquota": 0.21, "deducao": 125640},
        {"limite": 4800000, "aliquota": 0.33, "deducao": 648000}
    ]
    
    aliquota_efetiva = 0.06
    deducao = 0
    
    for faixa in faixas:
        if revenue <= faixa["limite"]:
            aliquota_efetiva = faixa["aliquota"]
            deducao = faixa["deducao"]
            break
    
    imposto = (revenue * aliquota_efetiva) - deducao
    
    return {
        "receita_bruta_12_meses": revenue,
        "aliquota_nominal": aliquota_efetiva * 100,
        "deducao": deducao,
        "valor_devido": max(imposto, 0),
        "aliquota_efetiva": (max(imposto, 0) / revenue * 100) if revenue > 0 else 0
    }

def initialize_ai_client(model_type: str, api_key: str):
    """Inicializa cliente de IA - retorna apenas o client"""
    try:
        if model_type == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            return genai.GenerativeModel('gemini-1.5-flash')
        
        elif model_type == "openai":
            from openai import OpenAI
            return OpenAI(api_key=api_key)
        
        elif model_type == "groq":
            from groq import Groq
            return Groq(api_key=api_key)
        
        elif model_type == "anthropic":
            from anthropic import Anthropic
            return Anthropic(api_key=api_key)
        
        return None
    except Exception as e:
        st.error(f"Erro ao inicializar IA: {e}")
        return None

def chat_with_ai(client, model_type: str, system_prompt: str, user_message: str, chat_history=None):
    """Conversa com o agente de IA"""
    try:
        if model_type == "gemini":
            if chat_history is None:
                chat_history = client.start_chat(history=[])
            full_message = f"{system_prompt}\n\n---\nUSUÁRIO: {user_message}"
            response = chat_history.send_message(full_message)
            return response.text, chat_history
        
        elif model_type == "openai":
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            return response.choices[0].message.content, None
        
        elif model_type == "groq":
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            return response.choices[0].message.content, None
        
        elif model_type == "anthropic":
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            return response.content[0].text, None
        
    except Exception as e:
        return f"Erro ao comunicar com IA: {str(e)}", chat_history

def create_accounting_system_prompt(company_data: dict, dre_data: dict = None, financial_data: dict = None) -> str:
    """Cria prompt do sistema para o agente contábil com contexto completo da empresa"""
    
    prompt = f"""Você é um ESPECIALISTA EM CONTABILIDADE SOCIETÁRIA E GERENCIAL.

🎯 SUA ESPECIALIDADE (CONTABILIDADE):
- Contabilidade societária e gerencial
- Demonstrações contábeis (DRE, Balanço Patrimonial, DFC, DMPL, DVA)
- Legislação contábil brasileira (Lei 6.404/76, CPC, NBC)
- Conciliação de contas contábeis com transações bancárias
- Planejamento contábil e auditoria contábil
- Análise de riscos de situações não compliance contábil
- Consultoria sobre procedimentos contábeis e lançamentos

📋 PROTOCOLO DE ANÁLISE:

1️⃣ IDENTIFICAR TIPO DE PERGUNTA:
   - Pergunta sobre DEMONSTRAÇÕES CONTÁBEIS → Use os dados da DRE/Balanço fornecidos abaixo
   - Pergunta sobre LEGISLAÇÃO CONTÁBIL → Consulte Lei 6.404/76, CPC, NBC
   - Pergunta sobre LANÇAMENTOS/CONCILIAÇÕES → Explique procedimentos contábeis
   - Pergunta sobre AUDITORIA/COMPLIANCE → Analise riscos e controles internos
   - Pergunta sobre TRIBUTOS/IMPOSTOS → Redirecione ao Agente Fiscal

2️⃣ RESPONDER DE FORMA:
   - RESUMIDA: Máximo 3-4 linhas diretas
   - OBJETIVA: Vá direto ao ponto
   - CLARA: Use linguagem acessível
   - PRÁTICA: Em contextos complexos, use exemplos de lançamentos contábeis

3️⃣ QUANDO USAR EXEMPLOS:
   - Se a pergunta envolve lançamentos contábeis complexos
   - Se há múltiplas formas de contabilizar uma transação
   - Se o conceito é técnico demais (ex: avaliação a valor justo)
   - Exemplo: "Como contabilizar uma compra de equipamento?" → Mostre débito/crédito

⚠️ REGRAS CRÍTICAS:
- SEMPRE cite a base legal contábil (Lei 6.404/76, CPC, NBC)
- NUNCA invente números - use APENAS os dados fornecidos
- Se não tiver dados suficientes, diga claramente
- Para questões FISCAIS/TRIBUTÁRIAS → Redirecione ao Agente Fiscal
- Responda em português brasileiro

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏢 EMPRESA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{company_data.get('name', 'N/A')}
CNPJ: {company_data.get('cnpj', 'N/A')}
Regime Tributário: {company_data.get('tax_regime', 'N/A')}

"""
    
    if dre_data:
        # Se tiver dados do período
        if dre_data.get('period_start'):
            prompt += f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
� DRE DO PERÍODO: {dre_data.get('period_start')} até {dre_data.get('period_end')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Receita Bruta: R$ {dre_data.get('gross_revenue', 0):,.2f}
(-) Deduções: R$ {dre_data.get('deductions', 0):,.2f}
= Receita Líquida: R$ {dre_data.get('net_revenue', 0):,.2f}

(-) Custos: R$ {dre_data.get('costs', 0):,.2f}
= Lucro Bruto: R$ {dre_data.get('gross_profit', 0):,.2f}

(-) Despesas Operacionais: R$ {dre_data.get('expenses', 0):,.2f}
= Lucro Líquido: R$ {dre_data.get('net_profit', 0):,.2f}

� OBRIGAÇÕES FISCAIS:
Total de obrigações: {dre_data.get('total_obligations', 0)}
Urgentes (≤5 dias): {dre_data.get('urgent_obligations', 0)}

"""
        else:
            # Dados simples de DRE
            prompt += f"""💰 DRE RESUMIDO:
Receita Bruta: R$ {dre_data.get('gross_revenue', 0):,.2f}
Despesas: R$ {dre_data.get('expenses', 0):,.2f}
Lucro Líquido: R$ {dre_data.get('net_profit', 0):,.2f}

"""
    
    prompt += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ INSTRUÇÕES DE RESPOSTA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 FORMATO DE RESPOSTA:

✅ PERGUNTAS SOBRE DADOS DA EMPRESA:
Use os números fornecidos acima, máximo 2-3 linhas.

Exemplo:
P: "Qual foi meu lucro líquido no período?"
R: "No período de 01/01/2024 a 31/12/2024, o lucro líquido foi de R$ 125.000,00."

✅ PERGUNTAS SOBRE LEGISLAÇÃO:
Responda de forma direta, cite a base legal, máximo 3-4 linhas.

Exemplo:
P: "Qual o prazo para entregar a DCTF?"
R: "A DCTF deve ser transmitida até o 15º dia útil do 2º mês subsequente ao de ocorrência dos fatos geradores (IN RFB 2.005/2021). Exemplo: fatos de janeiro → entrega até 15º dia útil de março."

✅ PERGUNTAS SOBRE CÁLCULOS:
Combine dados + legislação, use exemplo numérico se complexo.

Exemplo:
P: "Como calcular o Simples Nacional?"
R: "Para o regime do Simples Nacional Anexo III, a alíquota varia de 6% a 33% conforme faturamento dos últimos 12 meses. Com sua receita bruta de R$ 500.000,00, a alíquota seria aproximadamente 11,2% (Lei Complementar 123/2006). Consulte a tabela completa no site da RFB para cálculo exato."

❌ NÃO RESPONDA:
- Perguntas sobre investimentos financeiros (redirecione ao agente financeiro)
- Perguntas sobre fluxo de caixa operacional (redirecione ao agente financeiro)
- Assessoria jurídica complexa (sugira consultar advogado)

� FONTES RECOMENDADAS:


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ INSTRUÇÕES DE RESPOSTA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 FORMATO DE RESPOSTA:

✅ PERGUNTAS SOBRE DEMONSTRAÇÕES CONTÁBEIS:
Use os números fornecidos acima, máximo 2-3 linhas.

Exemplo:
P: "Qual foi meu lucro líquido no período?"
R: "No período de 01/01/2024 a 31/12/2024, o lucro líquido foi de R$ 125.000,00, conforme DRE acima."

✅ PERGUNTAS SOBRE LANÇAMENTOS CONTÁBEIS:
Explique o procedimento, cite a base legal, mostre débito/crédito se necessário.

Exemplo:
P: "Como contabilizar a compra de um equipamento?"
R: "Debite Imobilizado (Ativo Não Circulante) e credite Caixa/Bancos ou Fornecedores, pelo valor da aquisição. Deprecie mensalmente conforme vida útil estimada (Lei 6.404/76, art. 183). Exemplo: Equipamento R$ 10.000 → D: Máquinas e Equipamentos R$ 10.000 / C: Bancos R$ 10.000."

✅ PERGUNTAS SOBRE LEGISLAÇÃO CONTÁBIL:
Responda com base na Lei 6.404/76, CPC ou NBC, máximo 3-4 linhas.

Exemplo:
P: "O que é avaliação a valor justo?"
R: "Valor justo é o preço que seria recebido pela venda de um ativo ou pago pela transferência de um passivo em transação ordenada entre participantes do mercado (CPC 46). Aplica-se a instrumentos financeiros, propriedades para investimento e ativos biológicos."

✅ PERGUNTAS SOBRE CONCILIAÇÃO BANCÁRIA:
Explique o procedimento de conciliação entre contabilidade e extratos bancários.

Exemplo:
P: "Como fazer conciliação bancária?"
R: "Compare o saldo contábil da conta Bancos com o extrato bancário. Identifique diferenças: cheques emitidos não compensados, depósitos em trânsito, tarifas bancárias não lançadas, erros de lançamento. Ajuste a contabilidade para refletir a realidade do extrato."

✅ PERGUNTAS SOBRE AUDITORIA/COMPLIANCE CONTÁBIL:
Analise riscos de não conformidade contábil e sugira controles.

Exemplo:
P: "Como evitar erros de classificação contábil?"
R: "Implemente plano de contas detalhado com manual de procedimentos, segregação de funções (quem lança ≠ quem aprova), revisão mensal por contador responsável, e conciliações periódicas. Riscos: multas CVM, distorção de demonstrações, auditoria desfavorável."

❌ NÃO RESPONDA (Redirecione ao Agente Fiscal):
- Perguntas sobre impostos (IR, CSLL, PIS, COFINS, ICMS, ISS)
- Perguntas sobre obrigações acessórias (SPED, DCTF, ECF, EFD)
- Perguntas sobre regime de tributação (Simples, Lucro Presumido, Lucro Real)
- Perguntas sobre planejamento tributário
- Perguntas sobre cálculos fiscais

Resposta: "Esta pergunta é sobre tributação/impostos. Por favor, consulte o Agente Fiscal na seção 📋 Fiscal para questões tributárias."

❌ NÃO RESPONDA (Redirecione ao Agente Financeiro):
- Perguntas sobre fluxo de caixa operacional
- Perguntas sobre investimentos financeiros
- Perguntas sobre gestão de capital de giro
- Perguntas sobre contas a pagar/receber específicas

Resposta: "Esta pergunta é sobre gestão financeira. Por favor, consulte o Agente Financeiro na seção 💰 Financeiro para análise de fluxo de caixa."

📚 FONTES CONTÁBEIS RECOMENDADAS:
- Lei das S.A. (Lei 6.404/1976)
- Comitê de Pronunciamentos Contábeis (CPC)
- Conselho Federal de Contabilidade (NBC)
- Normas Brasileiras de Contabilidade
"""
    
    return prompt

def create_financial_agent_prompt(company_data: dict, financial_data: dict = None, bank_accounts: list = None) -> str:
    """Cria prompt para o AGENTE FINANCEIRO - Especialista em Matemática Financeira"""
    
    prompt = f"""Você é um ESPECIALISTA EM MATEMÁTICA FINANCEIRA e GESTÃO DE FLUXO DE CAIXA.

🎯 SUA ESPECIALIDADE:
- Análise de liquidez e solvência
- Projeções de fluxo de caixa
- Gestão de contas a pagar e receber
- Identificação de riscos financeiros
- Otimização de capital de giro

📋 PROTOCOLO DE ANÁLISE:

1️⃣ IDENTIFICAR ESCOPO DA PERGUNTA:
   - Se pergunta é sobre período ESPECÍFICO mostrado abaixo → Use os dados do período
   - Se pergunta é GERAL (ex: "histórico completo", "todos os anos") → Informe que pode consultar banco de dados completo
   - Se pergunta é sobre LEGISLAÇÃO/CÁLCULOS FISCAIS → Redirecione ao agente Fiscal

2️⃣ USAR DADOS CORRETOS:
   - Os dados abaixo são do período selecionado pelo usuário
   - Para perguntas fora desse período, solicite que o usuário ajuste o filtro de datas OU informe que consultará histórico completo

⚠️ REGRA CRÍTICA: 
- SEMPRE cite o período ao responder (ex: "No período 01/01/2024 a 31/12/2024...")
- IMPORTANTE: Os dados abaixo são EXATAMENTE os mesmos que aparecem na tabela "Consulta de Dados" visível no dashboard
- O usuário pode ver a tabela completa clicando em "Ver Dados Completos"
- Se não houver dados para o período, diga claramente: "Não há contas cadastradas para o período [período]"
- NUNCA invente números - use APENAS os valores fornecidos abaixo
- Resposta: máximo 3 linhas, objetiva e com números exatos

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏢 EMPRESA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{company_data.get('name', 'N/A')}
CNPJ: {company_data.get('cnpj', 'N/A')}

"""
    
    # CONTAS BANCÁRIAS
    if bank_accounts:
        total_balance = sum(acc.get('balance_as_of', acc.get('balance', 0)) for acc in bank_accounts)
        prompt += f"""💰 SALDOS BANCÁRIOS:
Total em Caixa: R$ {total_balance:,.2f}
Contas:"""
        for acc in bank_accounts:
            balance = acc.get('balance_as_of', acc.get('balance', 0))
            prompt += f"\n  • {acc['bank_name']} (Ag {acc['agency']}, Cc {acc['account_number']}): R$ {balance:,.2f}"
        prompt += "\n\n"
    
    # DADOS FINANCEIROS DO PERÍODO
    if financial_data and financial_data.get('period_start'):
        period_start = financial_data.get('period_start')
        period_end = financial_data.get('period_end')
        
        prompt += f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 ANÁLISE DO PERÍODO: {period_start} até {period_end}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ ATENÇÃO: Estes são os ÚNICOS dados que você tem acesso!
- Estes números vêm DIRETAMENTE do banco de dados
- O usuário pode ver a MESMA tabela completa no dashboard (botão "Ver Dados Completos")
- Use EXATAMENTE esses números, nunca invente ou estime

🔴 CONTAS A PAGAR (OBRIGAÇÕES):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total de contas NO PERÍODO: {financial_data.get('period_payables_total', 0)}
Valor total NO PERÍODO: R$ {financial_data.get('period_payables_amount_total', 0):,.2f}

Status de Pagamento:
  ✅ PAGAS: {financial_data.get('period_payables_paid', 0)} contas = R$ {financial_data.get('period_payables_amount_paid', 0):,.2f}
  ❌ NÃO PAGAS (EM ABERTO): {financial_data.get('period_payables_unpaid', 0)} contas = R$ {financial_data.get('period_payables_amount_unpaid', 0):,.2f}
  
⏰ Situação de Vencimento DAS CONTAS NÃO PAGAS:
  🔴 COM ATRASO (vencidas e ainda não pagas): {financial_data.get('period_payables_overdue', 0)} contas = R$ {financial_data.get('period_payables_amount_overdue', 0):,.2f}
  🕒 PENDENTES (a vencer, ainda no prazo): {financial_data.get('period_payables_pending', 0)} contas

⚠️ IMPORTANTE: 
- "COM ATRASO" = contas NÃO PAGAS que já venceram (já passaram da data de vencimento)
- "PENDENTES" = contas NÃO PAGAS que ainda estão no prazo (não venceram ainda)
- Se perguntar sobre "atrasadas" ou "vencidas" = use o valor de COM ATRASO ({financial_data.get('period_payables_amount_overdue', 0):,.2f})


🟢 CONTAS A RECEBER (DIREITOS):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total de contas NO PERÍODO: {financial_data.get('period_receivables_total', 0)}
Valor total NO PERÍODO: R$ {financial_data.get('period_receivables_amount_total', 0):,.2f}

Status de Recebimento:
  ✅ RECEBIDAS: {financial_data.get('period_receivables_received', 0)} contas = R$ {financial_data.get('period_receivables_amount_received', 0):,.2f}
  ❌ NÃO RECEBIDAS: {financial_data.get('period_receivables_unreceived', 0)} contas = R$ {financial_data.get('period_receivables_amount_unreceived', 0):,.2f}
  
⏰ Situação de Vencimento DAS CONTAS NÃO RECEBIDAS:
  🔴 COM ATRASO (vencidas e ainda não recebidas): {financial_data.get('period_receivables_overdue', 0)} contas = R$ {financial_data.get('period_receivables_amount_overdue', 0):,.2f}
  🕒 PENDENTES (a vencer): {financial_data.get('period_receivables_pending', 0)} contas

⚠️ IMPORTANTE: 
- "COM ATRASO" = contas NÃO RECEBIDAS que já venceram
- "PENDENTES" = contas NÃO RECEBIDAS que ainda estão no prazo
- Se perguntar sobre "atrasadas" ou "vencidas" = use o valor de COM ATRASO ({financial_data.get('period_receivables_amount_overdue', 0):,.2f})


📈 INDICADORES FINANCEIROS:
Taxa de Inadimplência Passiva: {(financial_data.get('period_payables_overdue', 0) / max(financial_data.get('period_payables_total', 1), 1) * 100):.1f}%
Taxa de Inadimplência Ativa: {(financial_data.get('period_receivables_overdue', 0) / max(financial_data.get('period_receivables_total', 1), 1) * 100):.1f}%
Capital em Risco (atrasadas a receber): R$ {financial_data.get('period_receivables_amount_overdue', 0):,.2f}

"""
    
    # SALDO PROJETADO
    if financial_data:
        prompt += f"""💳 PROJEÇÃO DE CAIXA:
Saldo Atual: R$ {financial_data.get('total_bank_balance', 0):,.2f}
Saldo Projetado: R$ {financial_data.get('projected_balance', 0):,.2f}
Variação: R$ {financial_data.get('projected_balance', 0) - financial_data.get('total_bank_balance', 0):,.2f}

"""
    
    prompt += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ INSTRUÇÕES DE RESPOSTA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 REGRAS OBRIGATÓRIAS:
1. Use EXATAMENTE os números fornecidos acima - nunca invente ou estime
2. SEMPRE mencione o período analisado na sua resposta
3. Seja objetivo: máximo 2-3 linhas
4. Se o valor for ZERO, diga explicitamente que é zero

📊 TERMINOLOGIA IMPORTANTE:
- "ATRASADAS" ou "VENCIDAS" = use o valor de "COM ATRASO" (já passou da data de vencimento e ainda não foi pago/recebido)
- "NÃO PAGAS" = total em aberto (inclui atrasadas + pendentes)
- "PENDENTES" = ainda não venceu (ainda está dentro do prazo)

❌ NÃO responda sobre legislação fiscal - sugira consultar o agente contábil
"""
    
    return prompt

def create_fiscal_agent_prompt(company_data: dict, fiscal_data: dict = None) -> str:
    """Cria prompt para o AGENTE FISCAL - Consultor em Regime Tributário e Legislação Fiscal"""
    
    prompt = f"""Você é um ESPECIALISTA EM REGIME TRIBUTÁRIO E LEGISLAÇÃO FISCAL BRASILEIRA (Federal, Estadual e Municipal).

🎯 SUA ESPECIALIDADE:
- Regime de tributação (Simples Nacional, Lucro Presumido, Lucro Real, MEI)
- Legislação tributária brasileira (IR, CSLL, PIS, COFINS, ICMS, ISS, IPI)
- Obrigações acessórias (SPED Fiscal, SPED Contribuições, DCTF, ECF, EFD-REINF, etc.)
- Planejamento tributário e elisão fiscal (legal)
- Análise de enquadramento e mudança de regime
- Tributos federais, estaduais e municipais
- Consultoria sobre otimização de carga tributária

📋 PROTOCOLO DE ANÁLISE:

1️⃣ IDENTIFICAR TIPO DE PERGUNTA:
   - Pergunta sobre REGIME TRIBUTÁRIO → Analise dados de faturamento e regime atual
   - Pergunta sobre CÁLCULOS DE IMPOSTOS → Use alíquotas corretas para o regime
   - Pergunta sobre OBRIGAÇÕES ACESSÓRIAS → Consulte legislação e prazos
   - Pergunta sobre ELISÃO FISCAL → Sugira estratégias LEGAIS de economia
   - Pergunta sobre CONTABILIDADE → Redirecione ao Agente Contábil

2️⃣ RESPONDER DE FORMA:
   - RESUMIDA: Máximo 3-4 linhas diretas
   - OBJETIVA: Vá direto ao ponto
   - CLARA: Use linguagem acessível
   - PRÁTICA: Em contextos complexos, use exemplos numéricos de cálculos

3️⃣ QUANDO USAR EXEMPLOS:
   - Se a pergunta envolve cálculos de impostos complexos
   - Se há múltiplos regimes possíveis para comparação
   - Se o conceito fiscal é técnico (ex: apropriação de créditos PIS/COFINS)
   - Exemplo: "Como calcular Simples Nacional?" → Mostre fórmula + exemplo com alíquota

⚠️ REGRAS CRÍTICAS:
- SEMPRE cite a base legal (Lei Complementar 123/2006, IN RFB, etc.)
- NUNCA invente números - use APENAS os dados fornecidos
- Para ELISÃO FISCAL: sugira apenas estratégias LEGAIS (não evasão fiscal)
- Se não tiver dados suficientes, diga claramente
- Para questões CONTÁBEIS (lançamentos, DRE) → Redirecione ao Agente Contábil
- Responda em português brasileiro

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏢 EMPRESA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{company_data.get('name', 'N/A')}
CNPJ: {company_data.get('cnpj', 'N/A')}
Regime Tributário: {company_data.get('tax_regime', 'N/A')}

"""
    
    if fiscal_data:
        prompt += f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 ANÁLISE FISCAL DO PERÍODO: {fiscal_data.get('period_start')} até {fiscal_data.get('period_end')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 FATURAMENTO E REGIME:
Receita Bruta do Período: R$ {fiscal_data.get('gross_revenue', 0):,.2f}
Receita Bruta Últimos 12 Meses: R$ {fiscal_data.get('revenue_12m', 0):,.2f}
Regime Atual: {fiscal_data.get('current_regime', 'N/A')}
Limite do Regime: R$ {fiscal_data.get('regime_limit', 0):,.2f}
% Atingido: {fiscal_data.get('regime_percentage', 0):.1f}%

"""
        
        # ALERTAS DE REGIME
        if fiscal_data.get('regime_percentage', 0) >= 80:
            prompt += f"""⚠️ ALERTA CRÍTICO: Faturamento atingiu {fiscal_data.get('regime_percentage', 0):.1f}% do limite do {fiscal_data.get('current_regime')}!
Faltam apenas R$ {fiscal_data.get('remaining_to_limit', 0):,.2f} para ultrapassar o limite.
AÇÃO NECESSÁRIA: Analisar mudança de regime ou estratégias de elisão fiscal.

"""
        
        # OBRIGAÇÕES DO PERÍODO
        if fiscal_data.get('obligations'):
            prompt += f"""📅 OBRIGAÇÕES FISCAIS DO PERÍODO:
Total de obrigações: {fiscal_data.get('total_obligations', 0)}
Urgentes (≤5 dias): {fiscal_data.get('urgent_obligations', 0)}
Atenção (6-15 dias): {fiscal_data.get('warning_obligations', 0)}
Normal (>15 dias): {fiscal_data.get('normal_obligations', 0)}

Obrigações Detalhadas:
"""
            for obl in fiscal_data.get('obligations', [])[:5]:  # Mostra até 5 obrigações
                days_left = obl.get('days_left', 0)
                prompt += f"  • {obl.get('type', 'N/A')} - Vencimento: {obl.get('due_date', 'N/A')} ({days_left} dias) - R$ {obl.get('amount', 0):,.2f}\n"
            
            prompt += "\n"
        
        # ANÁLISE TRIBUTÁRIA
        if fiscal_data.get('tax_analysis'):
            tax = fiscal_data['tax_analysis']
            prompt += f"""💳 ANÁLISE TRIBUTÁRIA ESTIMADA (Período):
Simples Nacional: R$ {tax.get('simples', 0):,.2f} ({tax.get('simples_rate', 0):.2f}%)
Lucro Presumido: R$ {tax.get('presumido', 0):,.2f} ({tax.get('presumido_rate', 0):.2f}%)
Lucro Real: R$ {tax.get('real', 0):,.2f} ({tax.get('real_rate', 0):.2f}%)

💡 Regime Mais Vantajoso: {tax.get('best_regime', 'N/A')} (Economia: R$ {tax.get('savings', 0):,.2f})

"""
    
    prompt += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ INSTRUÇÕES DE RESPOSTA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 FORMATO DE RESPOSTA:

✅ PERGUNTAS SOBRE REGIME TRIBUTÁRIO:
Analise dados de faturamento, compare regimes, máximo 3-4 linhas.

Exemplo:
P: "Devo mudar de regime tributário?"
R: "Com faturamento de R$ 500.000 em 12 meses, você está no Simples Nacional (80% do limite de R$ 4,8 mi). O Simples ainda é vantajoso (alíquota ~11,2% Anexo III). Se ultrapassar, analise Lucro Presumido (estimativa 13,33%). Mantenha Simples enquanto possível."

✅ PERGUNTAS SOBRE CÁLCULOS DE IMPOSTOS:
Use regime atual, mostre fórmula e exemplo numérico.

Exemplo:
P: "Quanto vou pagar de imposto este mês?"
R: "No Simples Nacional Anexo III com receita de R$ 50.000, aplique a alíquota da faixa (ex: 11,2%). Cálculo: R$ 50.000 × 11,2% = R$ 5.600. Prazo: até dia 20 do mês seguinte. DAS gerado no Portal do Simples."

✅ PERGUNTAS SOBRE OBRIGAÇÕES ACESSÓRIAS:
Cite obrigação, prazo, base legal, máximo 3-4 linhas.

Exemplo:
P: "Qual o prazo da DCTF?"
R: "DCTF deve ser transmitida até o 15º dia útil do 2º mês subsequente ao de ocorrência dos fatos geradores (IN RFB 2.005/2021). Exemplo: fatos de janeiro → entrega até 15º dia útil de março. Multa por atraso: R$ 500/mês."

✅ PERGUNTAS SOBRE ELISÃO FISCAL (LEGAL):
Sugira estratégias legais de economia tributária com exemplos.

Exemplo:
P: "Como reduzir impostos legalmente?"
R: "Estratégias legais: 1) Aproveitar créditos de PIS/COFINS (Lucro Real/Presumido); 2) Pró-labore otimizado (reduz INSS patronal vs. distribuição de lucros); 3) Incentivos fiscais regionais (ex: ZFM, SUDENE). Consulte contador para estruturar plano específico. Economia potencial: 15-30% da carga."

✅ PERGUNTAS SOBRE MUDANÇA DE REGIME:
Compare cenários, mostre cálculos, indique melhor opção.

Exemplo:
P: "Vale a pena sair do Simples?"
R: "Compare: Simples 11,2% × R$ 500k = R$ 56k/ano vs. Lucro Presumido 13,33% × R$ 500k = R$ 66,65k/ano. Simples R$ 10,65k mais barato. Só vale sair se: 1) Ultrapassar limite; 2) Ter muitos créditos de ICMS/PIS/COFINS; 3) Margem alta permite apropriação de créditos."

❌ NÃO RESPONDA (Redirecione ao Agente Contábil):
- Perguntas sobre lançamentos contábeis (débito/crédito)
- Perguntas sobre demonstrações contábeis (estrutura DRE, Balanço)
- Perguntas sobre conciliação bancária
- Perguntas sobre auditoria contábil

Resposta: "Esta pergunta é sobre procedimentos contábeis. Por favor, consulte o Agente Contábil na seção 📊 Contabilidade para lançamentos e demonstrações."

❌ NÃO RESPONDA (Redirecione ao Agente Financeiro):
- Perguntas sobre fluxo de caixa operacional
- Perguntas sobre investimentos financeiros
- Perguntas sobre gestão de contas a pagar/receber

Resposta: "Esta pergunta é sobre gestão financeira. Por favor, consulte o Agente Financeiro na seção 💰 Financeiro para análise de caixa."

📚 FONTES FISCAIS RECOMENDADAS:
- Receita Federal do Brasil (www.gov.br/receitafederal)
- Portal do Simples Nacional (www8.receita.fazenda.gov.br/SimplesNacional)
- Legislação Tributária (SPED, IN RFB, Lei Complementar 123/2006)
- Secretaria da Fazenda Estadual (ICMS)
- Secretaria Municipal de Finanças (ISS)

⚠️ IMPORTANTE: Elisão fiscal (legal) ≠ Evasão fiscal (crime). Sempre sugira estratégias dentro da lei.
"""
    
    return prompt

def apply_futuristic_theme():
    """Aplica tema futurístico moderno"""
    
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* ===== VARIÁVEIS GLOBAIS ===== */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #8b5cf6;
        --accent: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --bg-main: #0f172a;
        --bg-card: #1e293b;
        --bg-card-hover: #334155;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --border: #334155;
        --shadow: rgba(0, 0, 0, 0.3);
    }
    
    /* ===== RESET E BASE ===== */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: var(--text-primary);
    }
    
    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid var(--border);
    }
    
    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    
    /* ===== HEADER COM LOGO ===== */
    .header-container {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card-hover) 100%);
        border-radius: 20px;
        border: 1px solid var(--border);
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px var(--shadow);
    }
    
    .company-logo-container {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: transparent;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        flex-shrink: 0;
        padding: 0;
        box-sizing: border-box;
        border: none;
    }
    
    .company-logo {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
        background: transparent;
    }
    
    .header-title {
        flex: 1;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }
    
    .company-info {
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin-top: 0.5rem;
    }
    
    /* ===== SECTION HEADERS ===== */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--primary);
        position: relative;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 60px;
        height: 2px;
        background: var(--accent);
    }
    
    /* ===== ALERT CARDS ===== */
    .alert-card {
        padding: 1.25rem;
        border-radius: 12px;
        border-left: 4px solid;
        margin: 0.75rem 0;
        backdrop-filter: blur(10px);
    }
    
    .warning-card {
        background: rgba(245, 158, 11, 0.1);
        border-color: var(--warning);
        color: var(--text-primary);
    }
    
    .success-card {
        background: rgba(16, 185, 129, 0.1);
        border-color: var(--success);
        color: var(--text-primary);
    }
    
    .error-card {
        background: rgba(239, 68, 68, 0.1);
        border-color: var(--error);
        color: var(--text-primary);
    }
    
    .info-card {
        background: rgba(6, 182, 212, 0.1);
        border-color: var(--accent);
        color: var(--text-primary);
    }
    
    /* ===== CHAT CONTAINER FIXO ===== */
    .chat-fixed-container {
        background: var(--bg-card);
        border-radius: 16px;
        border: 1px solid var(--border);
        padding: 1.5rem;
        margin-top: 2rem;
        box-shadow: 0 4px 16px var(--shadow);
        max-height: 300px;
        display: flex;
        flex-direction: column;
    }
    
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        margin-bottom: 1rem;
        padding-right: 0.5rem;
    }
    
    .chat-messages::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-messages::-webkit-scrollbar-track {
        background: var(--bg-main);
        border-radius: 4px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 4px;
    }
    
    /* ===== TABLES ===== */
    .dataframe {
        background: var(--bg-card) !important;
        border-radius: 12px;
        overflow: hidden;
    }
    
    .dataframe th {
        background: var(--primary) !important;
        color: white !important;
        font-weight: 600;
        padding: 1rem !important;
    }
    
    .dataframe td {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        padding: 0.875rem !important;
        border-bottom: 1px solid var(--border) !important;
    }
    
    /* ===== BUTTONS ===== */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border-radius: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
    }
    
    /* ===== INPUTS ===== */
    .stTextInput>div>div>input,
    .stSelectbox>div>div,
    .stDateInput>div>div>input {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }
    
    /* ===== METRICS (Streamlit native) ===== */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    div[data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-main);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-dark);
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

# Inicializa session state
def init_session_state():
    defaults = {
        'user': None,
        'company': None,
        'current_page': 'login',
        'ai_client': None,
        'ai_model_type': None,
        'chat_history': None,
        'messages': [],
        # Financeiro: por padrão usar a data de hoje (saldos bancários) e listas padrão (próximas 10)
        'financial_date_range': (datetime.now().date(), datetime.now().date()),
        'financial_date_range_user_set': False,
        # Contábil mantém período padrão anual (ajuste se necessário)
        'accounting_date_range': (datetime(2024, 1, 1).date(), datetime(2024, 12, 31).date()),
        'accounting_date_range_user_set': False,
        # Fiscal mantém período padrão anual (mesmo que contábil)
        'fiscal_date_range': (datetime(2024, 1, 1).date(), datetime(2024, 12, 31).date()),
        'fiscal_date_range_user_set': False,
        'sidebar_expanded': {
            'ai_config': False,
            'uploads': False,
            'company': False
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Aplica tema futurístico
apply_futuristic_theme()

# ==========================================
# MÓDULO FINANCEIRO
# ==========================================

def show_financial_dashboard():
    """Mostra o dashboard financeiro"""
    
    # Header com logo usando o componente padrão
    show_module_header(
        title="Dashboard Financeiro",
        icon="💰",
        show_date_range=True,
        module="financial"
    )
    
    if not st.session_state.company:
        st.warning("⚠️ Cadastre sua empresa primeiro!")
        return
    
    company = st.session_state.company
    start_date, end_date = st.session_state.financial_date_range
    user_set_range = st.session_state.get('financial_date_range_user_set', False)

    # Define a chave do cache financeiro
    financial_cache = "financial_dre_data"
    date_key = f"{start_date}_{end_date}"
    
    # Inicializa o cache se não existir
    if financial_cache not in st.session_state:
        st.session_state[financial_cache] = {}
    
    # Se não tiver em cache ou as datas mudaram, recalcula
    if date_key not in st.session_state[financial_cache]:
        with st.spinner("Carregando dados financeiros..."):
            total_revenue = 0
            total_expenses = 0
            total_profit = 0
            
            # Itera pelos meses do período
            current_date = start_date.replace(day=1)
            end_month = end_date.replace(day=1)
            
            while current_date <= end_month:
                month_str = current_date.strftime('%Y-%m-01')
                dre = get_or_create_dre(company['id'], month_str)
                
                total_revenue += dre.get('gross_revenue', 0)
                total_expenses += dre.get('expenses', 0)
                total_profit += dre.get('net_profit', 0)
                
                # Próximo mês
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            
            # Salva no cache
            st.session_state[financial_cache][date_key] = {
                'total_revenue': total_revenue,
                'total_expenses': total_expenses,
                'total_profit': total_profit
            }
    
    # Usa os dados do cache
    data = st.session_state[financial_cache][date_key]
    total_revenue = data['total_revenue']
    total_expenses = data['total_expenses']
    total_profit = data['total_profit']
    
    # ===== SEÇÃO 1: CONTAS BANCÁRIAS =====
    st.markdown('<div class="section-header">🏦 Contas Bancárias</div>', unsafe_allow_html=True)
    
    # Saldos bancários: por padrão usar "hoje"; se usuário mudou o range, usa a data final selecionada
    as_of_date = end_date if user_set_range else datetime.now().date()
    bank_accounts = get_bank_account_balances_asof(company['id'], as_of_date)
    
    if not bank_accounts:
        st.info("Não há contas bancárias cadastradas.")
        if st.button("➕ Adicionar Conta Bancária"):
            # TODO: Implementar modal/form para adicionar conta
            pass
    else:
        account_cols = st.columns(len(bank_accounts))
        for i, account in enumerate(bank_accounts):
            with account_cols[i]:
                st.markdown(f"""
                <div style="padding: 1rem; background: var(--bg-card); border-radius: 8px; border: 1px solid var(--border)">
                    <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem">
                        {account['bank_name']} • Ag: {account['agency']} • Cc: {account['account_number']}
                    </div>
                    <div style="font-size: 1.5rem; font-weight: bold; margin-bottom: 0.5rem">
                        {format_currency(account.get('balance_as_of', account.get('balance', 0)))}
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary)">
                        Última atualização: {account['last_sync'].strftime('%d/%m/%Y %H:%M') if account['last_sync'] else 'Nunca sincronizado'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # ===== SEÇÃO 2: CONTAS A PAGAR E RECEBER =====
    col1, col2 = st.columns(2)
    
    # Calcula a data de início para buscar (dia seguinte ao fim do range)
    from datetime import timedelta
    next_day = end_date + timedelta(days=1)
    
    with col1:
        st.markdown('<div class="section-header">📉 Contas a Pagar</div>', unsafe_allow_html=True)
        
        # Sempre mostra as 10 próximas a vencer após a data fim do range
        bills_to_pay = get_upcoming_bills(
            company['id'], 
            limit=10, 
            start_date=next_day,  # Busca a partir do dia seguinte à data fim
            end_date=None,  # Sem limite superior
            include_paid=True  # Mostra TODAS (pagas e não pagas) para ver a data de pagamento
        )
        
        if not bills_to_pay:
            st.info("Não há pagamentos a serem realizados")
        else:
            for bill in bills_to_pay:
                # Define cor baseada na situação e status
                if bill.get('situacao') == 'Pago':
                    border_color = '#10b981' if bill.get('status') == 'Em Dia' else '#f59e0b'
                    situacao_emoji = '✅' if bill.get('status') == 'Em Dia' else '⚠️'
                else:
                    border_color = '#ef4444' if bill.get('status') == 'Com Atraso' else '#06b6d4'
                    situacao_emoji = '🔴' if bill.get('status') == 'Com Atraso' else '🕒'
                
                # Formata datas para exibição
                due_date_str = bill.get('due_date').strftime('%d/%m/%Y') if bill.get('due_date') else '-'
                
                # Se já foi pago, mostra a data de pagamento
                payment_info = ""
                if bill.get('payment_date'):
                    payment_date_obj = datetime.strptime(bill['payment_date'], '%Y-%m-%d').date() if isinstance(bill['payment_date'], str) else bill['payment_date']
                    payment_date_str = payment_date_obj.strftime('%d/%m/%Y')
                    payment_info = f" | Pago em: {payment_date_str}"
                
                st.markdown(f"""
                <div style="padding: 0.5rem; background: var(--bg-card); border-radius: 4px; 
                     border-left: 3px solid {border_color}; margin-bottom: 0.25rem">
                    <div style="display: flex; justify-content: space-between; align-items: center">
                        <div>
                            <div style="font-weight: bold; font-size: 0.75rem">{situacao_emoji} {bill.get('description', 'Conta a pagar')}</div>
                            <div style="font-size: 0.65rem; color: var(--text-secondary)">
                                Vencimento: {due_date_str}{payment_info} • {format_payment_status(bill)}
                            </div>
                        </div>
                        <div style="font-size: 0.85rem; font-weight: bold; color: var(--error)">
                            {format_currency(bill.get('amount', 0))}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-header">📈 Contas a Receber</div>', unsafe_allow_html=True)
        
        # Sempre mostra as 10 próximas a vencer após a data fim do range
        bills_to_receive = get_upcoming_receivables(
            company['id'], 
            limit=10, 
            start_date=next_day,  # Busca a partir do dia seguinte à data fim
            end_date=None,  # Sem limite superior
            include_paid=True  # Mostra TODAS (recebidas e não recebidas) para ver a data de recebimento
        )
        
        if not bills_to_receive:
            st.info("Não há recebimentos previstos")
        else:
            for bill in bills_to_receive:
                # Define cor baseada na situação e status
                if bill.get('situacao') == 'Recebido':
                    border_color = '#10b981' if bill.get('status') == 'Em Dia' else '#f59e0b'
                    situacao_emoji = '✅' if bill.get('status') == 'Em Dia' else '⚠️'
                else:
                    border_color = '#ef4444' if bill.get('status') == 'Com Atraso' else '#06b6d4'
                    situacao_emoji = '🔴' if bill.get('status') == 'Com Atraso' else '🕒'
                
                # Formata datas para exibição
                due_date_str = bill.get('due_date').strftime('%d/%m/%Y') if bill.get('due_date') else '-'
                
                # Se já foi recebido, mostra a data de recebimento
                payment_info = ""
                if bill.get('payment_date'):
                    payment_date_obj = datetime.strptime(bill['payment_date'], '%Y-%m-%d').date() if isinstance(bill['payment_date'], str) else bill['payment_date']
                    payment_date_str = payment_date_obj.strftime('%d/%m/%Y')
                    payment_info = f" | Recebido em: {payment_date_str}"
                
                st.markdown(f"""
                <div style="padding: 0.5rem; background: var(--bg-card); border-radius: 4px; 
                     border-left: 3px solid {border_color}; margin-bottom: 0.25rem">
                    <div style="display: flex; justify-content: space-between; align-items: center">
                        <div>
                            <div style="font-weight: bold; font-size: 0.75rem">{situacao_emoji} {bill.get('description', 'Conta a receber')}</div>
                            <div style="font-size: 0.65rem; color: var(--text-secondary)">
                                Vencimento: {due_date_str}{payment_info} • {format_receipt_status(bill)}
                            </div>
                        </div>
                        <div style="font-size: 0.85rem; font-weight: bold; color: var(--success)">
                            {format_currency(bill.get('amount', 0))}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # ===== SEÇÃO 3: TABELA DINÂMICA DE CONSULTA =====
    st.markdown("---")
    st.markdown('<div class="section-header">📊 Consulta de Dados - Período Selecionado</div>', unsafe_allow_html=True)
    
    # Botão para expandir/recolher
    if 'show_data_table' not in st.session_state:
        st.session_state.show_data_table = False
    
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        st.markdown(f"**Período consultado:** {start_date.strftime('%d/%m/%Y')} até {end_date.strftime('%d/%m/%Y')}")
    with col_btn2:
        if st.button("📋 Ver Dados Completos" if not st.session_state.show_data_table else "🔼 Ocultar Dados", 
                     key="toggle_data_table", use_container_width=True):
            st.session_state.show_data_table = not st.session_state.show_data_table
    
    if st.session_state.show_data_table:
        # Busca TODAS as contas do período selecionado
        all_bills_payable_display = get_upcoming_bills(company['id'], start_date=start_date, end_date=end_date, limit=None, include_paid=True)
        all_bills_receivable_display = get_upcoming_receivables(company['id'], start_date=start_date, end_date=end_date, limit=None, include_paid=True)
        
        tab1, tab2 = st.tabs([f"📉 Contas a Pagar ({len(all_bills_payable_display)})", f"📈 Contas a Receber ({len(all_bills_receivable_display)})"])
        
        with tab1:
            if all_bills_payable_display:
                # Calcula estatísticas
                pagas = [b for b in all_bills_payable_display if b.get('situacao') == 'Pago']
                nao_pagas = [b for b in all_bills_payable_display if b.get('situacao') == 'A Pagar']
                vencidas = [b for b in nao_pagas if b.get('status') == 'Com Atraso']
                pendentes = [b for b in nao_pagas if b.get('status') == 'Pendente']
                
                st.markdown(f"""
                <div style="padding: 1rem; background: var(--bg-card); border-radius: 8px; margin-bottom: 1rem">
                    <b>📊 Resumo:</b> {len(all_bills_payable_display)} contas | 
                    ✅ Pagas: {len(pagas)} (R$ {sum(b.get('amount', 0) for b in pagas):,.2f}) | 
                    🔴 Vencidas: {len(vencidas)} (R$ {sum(b.get('amount', 0) for b in vencidas):,.2f}) | 
                    🕒 Pendentes: {len(pendentes)} (R$ {sum(b.get('amount', 0) for b in pendentes):,.2f})
                </div>
                """, unsafe_allow_html=True)
                
                # Cria DataFrame
                import pandas as pd
                df_payable = pd.DataFrame([
                    {
                        'Descrição': b.get('description', ''),
                        'Vencimento': b.get('due_date').strftime('%d/%m/%Y') if b.get('due_date') else '',
                        'Pagamento': b.get('payment_date').strftime('%d/%m/%Y') if b.get('payment_date') else '-',
                        'Valor': f"R$ {b.get('amount', 0):,.2f}",
                        'Status': format_payment_status(b)
                    }
                    for b in all_bills_payable_display
                ])
                
                st.dataframe(df_payable, use_container_width=True, height=400)
            else:
                st.info("📭 Nenhuma conta a pagar encontrada no período selecionado")
        
        with tab2:
            if all_bills_receivable_display:
                # Calcula estatísticas
                recebidas = [b for b in all_bills_receivable_display if b.get('situacao') == 'Recebido']
                nao_recebidas = [b for b in all_bills_receivable_display if b.get('situacao') == 'A Receber']
                vencidas_rec = [b for b in nao_recebidas if b.get('status') == 'Com Atraso']
                pendentes_rec = [b for b in nao_recebidas if b.get('status') == 'Pendente']
                
                st.markdown(f"""
                <div style="padding: 1rem; background: var(--bg-card); border-radius: 8px; margin-bottom: 1rem">
                    <b>📊 Resumo:</b> {len(all_bills_receivable_display)} contas | 
                    ✅ Recebidas: {len(recebidas)} (R$ {sum(b.get('amount', 0) for b in recebidas):,.2f}) | 
                    🔴 Vencidas: {len(vencidas_rec)} (R$ {sum(b.get('amount', 0) for b in vencidas_rec):,.2f}) | 
                    🕒 Pendentes: {len(pendentes_rec)} (R$ {sum(b.get('amount', 0) for b in pendentes_rec):,.2f})
                </div>
                """, unsafe_allow_html=True)
                
                # Cria DataFrame
                import pandas as pd
                df_receivable = pd.DataFrame([
                    {
                        'Descrição': b.get('description', ''),
                        'Vencimento': b.get('due_date').strftime('%d/%m/%Y') if b.get('due_date') else '',
                        'Recebimento': b.get('payment_date').strftime('%d/%m/%Y') if b.get('payment_date') else '-',
                        'Valor': f"R$ {b.get('amount', 0):,.2f}",
                        'Status': format_receipt_status(b)
                    }
                    for b in all_bills_receivable_display
                ])
                
                st.dataframe(df_receivable, use_container_width=True, height=400)
            else:
                st.info("📭 Nenhuma conta a receber encontrada no período selecionado")
    
    # ===== AGENTE FINANCEIRO ===== 
    st.markdown("---")
    st.markdown('<div class="section-header">🤖 Agente Financeiro - Consultor de Finanças</div>', unsafe_allow_html=True)
    
    if not st.session_state.ai_client:
        st.info("💡 Configure um modelo de IA na barra lateral para ativar o agente financeiro")
    else:
        # MOSTRA RESUMO DOS DADOS DO PERÍODO ATUAL (para referência visual)
        period_summary_payable = get_upcoming_bills(company['id'], start_date=start_date, end_date=end_date, limit=None, include_paid=True)
        period_summary_receivable = get_upcoming_receivables(company['id'], start_date=start_date, end_date=end_date, limit=None, include_paid=True)
        
        summary_payables_unpaid = len([b for b in period_summary_payable if b.get('situacao') == 'A Pagar'])
        summary_payables_overdue = len([b for b in period_summary_payable if b.get('situacao') == 'A Pagar' and b.get('status') == 'Com Atraso'])
        summary_payables_unpaid_amount = sum(b.get('amount', 0) for b in period_summary_payable if b.get('situacao') == 'A Pagar')
        summary_payables_overdue_amount = sum(b.get('amount', 0) for b in period_summary_payable if b.get('situacao') == 'A Pagar' and b.get('status') == 'Com Atraso')
        
        summary_receivables_unreceived = len([b for b in period_summary_receivable if b.get('situacao') == 'A Receber'])
        summary_receivables_overdue = len([b for b in period_summary_receivable if b.get('situacao') == 'A Receber' and b.get('status') == 'Com Atraso'])
        summary_receivables_unreceived_amount = sum(b.get('amount', 0) for b in period_summary_receivable if b.get('situacao') == 'A Receber')
        summary_receivables_overdue_amount = sum(b.get('amount', 0) for b in period_summary_receivable if b.get('situacao') == 'A Receber' and b.get('status') == 'Com Atraso')
        
        st.markdown(f"""
        <div style="padding: 1rem; background: rgba(99, 102, 241, 0.1); border-left: 4px solid #6366f1; border-radius: 8px; margin-bottom: 1rem">
            <b>📊 Dados do Período Atual ({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}):</b><br>
            🔴 <b>Contas a Pagar:</b> {len(period_summary_payable)} total | {summary_payables_unpaid} em aberto (R$ {summary_payables_unpaid_amount:,.2f}) | {summary_payables_overdue} vencidas (R$ {summary_payables_overdue_amount:,.2f})<br>
            🟢 <b>Contas a Receber:</b> {len(period_summary_receivable)} total | {summary_receivables_unreceived} em aberto (R$ {summary_receivables_unreceived_amount:,.2f}) | {summary_receivables_overdue} vencidas (R$ {summary_receivables_overdue_amount:,.2f})
        </div>
        """, unsafe_allow_html=True)
        
        # Inicializa histórico de mensagens específico do agente financeiro
        if 'financial_agent_messages' not in st.session_state:
            st.session_state.financial_agent_messages = []
        
        # Botão de reset
        col_reset1, col_reset2 = st.columns([5, 1])
        with col_reset2:
            if st.button("🔄 Limpar", key="reset_financial_chat", use_container_width=True):
                st.session_state.financial_agent_messages = []
                st.session_state.financial_agent_chat_history = None
                st.rerun()
        
        # Container com altura fixa e scroll (usando componente nativo do Streamlit)
        with st.container(height=300):
            for message in st.session_state.financial_agent_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Input de chat
        if prompt := st.chat_input("Pergunte sobre fluxo de caixa, contas, projeções, riscos financeiros...", key="financial_agent_input"):
            # Adiciona mensagem do usuário
            st.session_state.financial_agent_messages.append({"role": "user", "content": prompt})
            
            # Coleta dados do período SELECIONADO PELO USUÁRIO para o agente
            from datetime import timedelta
            import re
            
            # IMPORTANTE: Usa o período selecionado pelo usuário no date_range
            # SEMPRE usa financial_date_range, não accounting_date_range
            period_start = st.session_state.financial_date_range[0]
            period_end = st.session_state.financial_date_range[1]
            
            # DETECÇÃO INTELIGENTE: Verifica se pergunta menciona outro período
            # Exemplos: "2023", "janeiro 2024", "jan e fev 2024", "histórico completo"
            prompt_lower = prompt.lower()
            
            # Detecta meses mencionados
            month_names = {
                'janeiro': 1, 'jan': 1,
                'fevereiro': 2, 'fev': 2,
                'março': 3, 'mar': 3,
                'abril': 4, 'abr': 4,
                'maio': 5, 'mai': 5,
                'junho': 6, 'jun': 6,
                'julho': 7, 'jul': 7,
                'agosto': 8, 'ago': 8,
                'setembro': 9, 'set': 9,
                'outubro': 10, 'out': 10,
                'novembro': 11, 'nov': 11,
                'dezembro': 12, 'dez': 12
            }
            
            mentioned_months = []
            for month_name, month_num in month_names.items():
                if month_name in prompt_lower:
                    mentioned_months.append(month_num)
            
            # Remove duplicatas e ordena
            mentioned_months = sorted(set(mentioned_months))
            
            # Detecta anos mencionados
            year_matches = re.findall(r'\b(20\d{2})\b', prompt)
            
            # AJUSTE AUTOMÁTICO DO PERÍODO
            if mentioned_months and year_matches:
                # Se menciona meses específicos e ano
                from datetime import date
                import calendar
                
                mentioned_year = int(year_matches[0])
                first_month = min(mentioned_months)
                last_month = max(mentioned_months)
                
                # Último dia do último mês
                last_day = calendar.monthrange(mentioned_year, last_month)[1]
                
                period_start = date(mentioned_year, first_month, 1)
                period_end = date(mentioned_year, last_month, last_day)
                print(f"🔍 DEBUG - Período ajustado para MESES específicos: {period_start} até {period_end}")
                
            elif year_matches:
                # Se menciona apenas ano (sem meses específicos)
                mentioned_year = int(year_matches[0])
                selected_year = period_start.year
                
                if mentioned_year != selected_year:
                    # Ajusta automaticamente o período para o ano mencionado
                    from datetime import date
                    period_start = date(mentioned_year, 1, 1)
                    period_end = date(mentioned_year, 12, 31)
                    print(f"🔍 DEBUG - Período ajustado para ANO COMPLETO: {period_start} até {period_end}")
                    
                    # Mostra aviso visual ao usuário
                    st.info(f"🔍 **Ajuste automático de período**: Detectei que você perguntou sobre {mentioned_year}. Consultando dados de 01/01/{mentioned_year} a 31/12/{mentioned_year}.")
            
            # Se pergunta é sobre "histórico completo", "todos os dados", etc.
            elif any(keyword in prompt_lower for keyword in ['histórico completo', 'todos os dados', 'tudo', 'histórico total']):
                # Busca desde o início (ajuste conforme necessário)
                from datetime import date
                period_start = date(2020, 1, 1)
                period_end = datetime.now().date()
                print(f"🔍 DEBUG - Buscando histórico completo: {period_start} até {period_end}")
                
                # Mostra aviso visual ao usuário
                st.info(f"🔍 **Histórico completo**: Consultando TODOS os dados desde 2020 até hoje.")
            
            # DEBUG: Mostra qual período está sendo usado
            print(f"🔍 DEBUG - Período selecionado: {period_start} até {period_end}")
            
            # Busca TODAS as contas do período SELECIONADO (sem limite)
            print(f"🔍 DEBUG - Chamando get_upcoming_bills com:")
            print(f"  - company_id: {company['id']}")
            print(f"  - start_date: {period_start} (tipo: {type(period_start)})")
            print(f"  - end_date: {period_end} (tipo: {type(period_end)})")
            print(f"  - limit: None")
            print(f"  - include_paid: True")
            
            all_bills_payable = get_upcoming_bills(company['id'], start_date=period_start, end_date=period_end, limit=None, include_paid=True)
            all_bills_receivable = get_upcoming_receivables(company['id'], start_date=period_start, end_date=period_end, limit=None, include_paid=True)
            
            # DEBUG: Mostra DETALHES das contas encontradas
            print(f"\n{'='*80}")
            print(f"🔍 DEBUG - RESULTADO DA CONSULTA AO BANCO DE DADOS")
            print(f"{'='*80}")
            print(f"Período: {period_start} até {period_end}")
            print(f"\n📋 CONTAS A PAGAR ENCONTRADAS: {len(all_bills_payable)}")
            
            if all_bills_payable:
                print(f"\n🔍 Primeiras 10 contas a pagar:")
                for i, bill in enumerate(all_bills_payable[:10], 1):
                    print(f"  {i}. {bill.get('description', 'Sem descrição')}")
                    print(f"     Vencimento: {bill.get('due_date')}")
                    print(f"     Valor: R$ {bill.get('amount', 0):,.2f}")
                    print(f"     Situação: {bill.get('situacao')} | Status: {bill.get('status')}")
                    print()
            else:
                print("  ❌ NENHUMA conta a pagar encontrada no período!")
            
            print(f"\n📋 CONTAS A RECEBER ENCONTRADAS: {len(all_bills_receivable)}")
            
            if all_bills_receivable:
                print(f"\n🔍 Primeiras 10 contas a receber:")
                for i, bill in enumerate(all_bills_receivable[:10], 1):
                    print(f"  {i}. {bill.get('description', 'Sem descrição')}")
                    print(f"     Vencimento: {bill.get('due_date')}")
                    print(f"     Valor: R$ {bill.get('amount', 0):,.2f}")
                    print(f"     Situação: {bill.get('situacao')} | Status: {bill.get('status')}")
                    print()
            else:
                print("  ❌ NENHUMA conta a receber encontrada no período!")
            
            print(f"{'='*80}\n")
            
            # Calcula estatísticas do período SELECIONADO
            payables_total = len(all_bills_payable)
            payables_paid = len([b for b in all_bills_payable if b.get('situacao') == 'Pago'])
            payables_unpaid = len([b for b in all_bills_payable if b.get('situacao') == 'A Pagar'])
            payables_overdue = len([b for b in all_bills_payable if b.get('situacao') == 'A Pagar' and b.get('status') == 'Com Atraso'])
            payables_pending = len([b for b in all_bills_payable if b.get('situacao') == 'A Pagar' and b.get('status') == 'Pendente'])
            
            # DEBUG: Lista as contas COM ATRASO especificamente
            contas_atrasadas = [b for b in all_bills_payable if b.get('situacao') == 'A Pagar' and b.get('status') == 'Com Atraso']
            if contas_atrasadas:
                print(f"\n🔴 DEBUG - CONTAS COM ATRASO DETECTADAS ({len(contas_atrasadas)}):")
                for i, conta in enumerate(contas_atrasadas[:5], 1):
                    print(f"  {i}. {conta.get('description', 'Sem descrição')}")
                    print(f"     Valor: R$ {conta.get('amount', 0):,.2f}")
                    print(f"     Vencimento: {conta.get('due_date')}")
                    print(f"     Situação: '{conta.get('situacao')}' | Status: '{conta.get('status')}'")
                    print()
            else:
                print(f"\n⚠️ DEBUG - NENHUMA conta COM ATRASO detectada!")
                print(f"  Total de contas a pagar: {len(all_bills_payable)}")
                if all_bills_payable:
                    print(f"  Primeira conta - Situação: '{all_bills_payable[0].get('situacao')}' | Status: '{all_bills_payable[0].get('status')}'")
            
            
            payables_amount_total = sum(b.get('amount', 0) for b in all_bills_payable)
            payables_amount_paid = sum(b.get('amount', 0) for b in all_bills_payable if b.get('situacao') == 'Pago')
            payables_amount_unpaid = sum(b.get('amount', 0) for b in all_bills_payable if b.get('situacao') == 'A Pagar')
            payables_amount_overdue = sum(b.get('amount', 0) for b in all_bills_payable if b.get('situacao') == 'A Pagar' and b.get('status') == 'Com Atraso')
            
            receivables_total = len(all_bills_receivable)
            receivables_received = len([b for b in all_bills_receivable if b.get('situacao') == 'Recebido'])
            receivables_unreceived = len([b for b in all_bills_receivable if b.get('situacao') == 'A Receber'])
            receivables_overdue = len([b for b in all_bills_receivable if b.get('situacao') == 'A Receber' and b.get('status') == 'Com Atraso'])
            receivables_pending = len([b for b in all_bills_receivable if b.get('situacao') == 'A Receber' and b.get('status') == 'Pendente'])
            
            receivables_amount_total = sum(b.get('amount', 0) for b in all_bills_receivable)
            receivables_amount_received = sum(b.get('amount', 0) for b in all_bills_receivable if b.get('situacao') == 'Recebido')
            receivables_amount_unreceived = sum(b.get('amount', 0) for b in all_bills_receivable if b.get('situacao') == 'A Receber')
            receivables_amount_overdue = sum(b.get('amount', 0) for b in all_bills_receivable if b.get('situacao') == 'A Receber' and b.get('status') == 'Com Atraso')
            
            # DEBUG: Mostra ESTATÍSTICAS CALCULADAS
            print(f"\n{'='*80}")
            print(f"📊 DEBUG - ESTATÍSTICAS CALCULADAS DO PERÍODO")
            print(f"{'='*80}")
            print(f"\n🔴 CONTAS A PAGAR:")
            print(f"  Total de contas: {payables_total}")
            print(f"  Pagas: {payables_paid} (R$ {payables_amount_paid:,.2f})")
            print(f"  Não pagas: {payables_unpaid} (R$ {payables_amount_unpaid:,.2f})")
            print(f"  Vencidas (não pagas): {payables_overdue} (R$ {payables_amount_overdue:,.2f})")
            print(f"  Pendentes: {payables_pending}")
            print(f"  Valor total: R$ {payables_amount_total:,.2f}")
            
            print(f"\n🟢 CONTAS A RECEBER:")
            print(f"  Total de contas: {receivables_total}")
            print(f"  Recebidas: {receivables_received} (R$ {receivables_amount_received:,.2f})")
            print(f"  Não recebidas: {receivables_unreceived} (R$ {receivables_amount_unreceived:,.2f})")
            print(f"  Vencidas (não recebidas): {receivables_overdue} (R$ {receivables_amount_overdue:,.2f})")
            print(f"  Pendentes: {receivables_pending}")
            print(f"  Valor total: R$ {receivables_amount_total:,.2f}")
            print(f"{'='*80}\n")
            
            # AVISO IMPORTANTE: Se não houver dados, alerta o usuário ANTES de chamar o agente
            if payables_total == 0 and receivables_total == 0:
                st.warning(f"⚠️ **Atenção**: Não há contas cadastradas para o período **{period_start.strftime('%d/%m/%Y')} a {period_end.strftime('%d/%m/%Y')}**. Tente selecionar outro período usando o filtro de datas no topo da página.")
                # Adiciona resposta automática ao histórico
                auto_response = f"Não há contas cadastradas para o período {period_start.strftime('%d/%m/%Y')} a {period_end.strftime('%d/%m/%Y')}. Por favor, selecione outro período usando o filtro de datas no topo da página para ver os dados disponíveis."
                st.session_state.financial_agent_messages.append({"role": "assistant", "content": auto_response})
                st.rerun()
            
            # Saldo total bancário
            total_bank_balance = sum(acc.get('balance_as_of', acc.get('balance', 0)) for acc in bank_accounts) if bank_accounts else 0
            
            # Próximas contas (para projeção) - usa dia seguinte ao período
            next_day = period_end + timedelta(days=1)
            bills_to_pay_next = get_upcoming_bills(company['id'], limit=10, start_date=next_day, end_date=None, include_paid=False)
            bills_to_receive_next = get_upcoming_receivables(company['id'], limit=10, start_date=next_day, end_date=None, include_paid=False)
            
            total_to_pay_next = sum(bill.get('amount', 0) for bill in bills_to_pay_next)
            total_to_receive_next = sum(bill.get('amount', 0) for bill in bills_to_receive_next)
            
            # Monta dados financeiros completos com período SELECIONADO
            financial_stats = {
                'total_bank_balance': total_bank_balance,
                'projected_balance': total_bank_balance - total_to_pay_next + total_to_receive_next,
                'period_start': period_start.strftime('%d/%m/%Y'),
                'period_end': period_end.strftime('%d/%m/%Y'),
                'period_payables_total': payables_total,
                'period_payables_paid': payables_paid,
                'period_payables_unpaid': payables_unpaid,
                'period_payables_overdue': payables_overdue,
                'period_payables_pending': payables_pending,
                'period_payables_amount_total': payables_amount_total,
                'period_payables_amount_paid': payables_amount_paid,
                'period_payables_amount_unpaid': payables_amount_unpaid,
                'period_payables_amount_overdue': payables_amount_overdue,
                'period_receivables_total': receivables_total,
                'period_receivables_received': receivables_received,
                'period_receivables_unreceived': receivables_unreceived,
                'period_receivables_overdue': receivables_overdue,
                'period_receivables_pending': receivables_pending,
                'period_receivables_amount_total': receivables_amount_total,
                'period_receivables_amount_received': receivables_amount_received,
                'period_receivables_amount_unreceived': receivables_amount_unreceived,
                'period_receivables_amount_overdue': receivables_amount_overdue,
            }
            
            # DEBUG: Mostra o que será enviado ao agente
            print(f"\n{'='*80}")
            print(f"🤖 DEBUG - DADOS QUE SERÃO ENVIADOS AO AGENTE")
            print(f"{'='*80}")
            print(f"Período: {financial_stats['period_start']} até {financial_stats['period_end']}")
            print(f"\n📊 CONTAS A PAGAR:")
            print(f"  Total: {financial_stats['period_payables_total']} contas = R$ {financial_stats['period_payables_amount_total']:,.2f}")
            print(f"  Pagas: {financial_stats['period_payables_paid']} = R$ {financial_stats['period_payables_amount_paid']:,.2f}")
            print(f"  Não pagas: {financial_stats['period_payables_unpaid']} = R$ {financial_stats['period_payables_amount_unpaid']:,.2f}")
            print(f"  🔴 ATRASADAS: {financial_stats['period_payables_overdue']} = R$ {financial_stats['period_payables_amount_overdue']:,.2f}")
            print(f"\n📊 CONTAS A RECEBER:")
            print(f"  Total: {financial_stats['period_receivables_total']} contas = R$ {financial_stats['period_receivables_amount_total']:,.2f}")
            print(f"  Recebidas: {financial_stats['period_receivables_received']} = R$ {financial_stats['period_receivables_amount_received']:,.2f}")
            print(f"  Não recebidas: {financial_stats['period_receivables_unreceived']} = R$ {financial_stats['period_receivables_amount_unreceived']:,.2f}")
            print(f"  🔴 ATRASADAS: {financial_stats['period_receivables_overdue']} = R$ {financial_stats['period_receivables_amount_overdue']:,.2f}")
            print(f"{'='*80}\n")
            
            # Cria prompt do agente financeiro
            system_prompt = create_financial_agent_prompt(
                company_data=company,
                financial_data=financial_stats,
                bank_accounts=bank_accounts
            )
            
            # Chama a IA
            with st.spinner("🤔 Analisando dados financeiros..."):
                response, chat_history = chat_with_ai(
                    st.session_state.ai_client,
                    st.session_state.ai_model_type,
                    system_prompt,
                    prompt,
                    st.session_state.get('financial_agent_chat_history')
                )
                
                st.session_state.financial_agent_chat_history = chat_history
            
            # Adiciona resposta ao histórico
            st.session_state.financial_agent_messages.append({"role": "assistant", "content": response})
            st.rerun()

# ==========================================
# TELA DE LOGIN E CADASTRO
# ==========================================

def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<h1 class="main-header">📊 Cont-AI</h1>', unsafe_allow_html=True)
        st.markdown("### Gestão Contábil e Tributária Inteligente e Automatizada")
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Cadastro"])
        
        with tab1:
            st.markdown("#### Acesse sua conta")
            
            email = st.text_input("Email", key="login_email", placeholder="seu@email.com")
            password = st.text_input("Senha", type="password", key="login_password", placeholder="••••••••")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("🔓 Entrar", use_container_width=True):
                    if email and password:
                        with st.spinner("Autenticando..."):
                            user = authenticate_user(email, password)
                            
                            if user:
                                st.session_state.user = user
                                st.session_state.company = get_company_by_user(user['id'])
                                
                                # Carrega nível de acesso do usuário
                                if st.session_state.company:
                                    user_access = get_user_access_level(user['id'], st.session_state.company['id'])
                                    st.session_state.user_access_level = user_access if user_access else 'senior'
                                else:
                                    # Se ainda não tem empresa, será senior (owner)
                                    st.session_state.user_access_level = 'senior'
                                
                                st.session_state.current_page = 'dashboard'
                                st.success("✅ Login realizado com sucesso!")
                                st.rerun()
                            else:
                                st.error("❌ Email ou senha incorretos")
                    else:
                        st.warning("⚠️ Preencha todos os campos")
            
            with col_btn2:
                if st.button("🔑 Esqueci a senha", use_container_width=True):
                    st.session_state.show_password_reset = True
                    st.rerun()
        
        # ===== RECUPERAÇÃO DE SENHA =====
        if st.session_state.get('show_password_reset', False):
            st.markdown("---")
            st.markdown("### 🔑 Recuperar Senha")
            
            with st.form("password_reset_form"):
                reset_email = st.text_input("Digite seu email cadastrado", placeholder="seu@email.com")
                
                col_r1, col_r2 = st.columns(2)
                
                with col_r1:
                    submitted_reset = st.form_submit_button("📧 Enviar Código", use_container_width=True)
                
                with col_r2:
                    if st.form_submit_button("❌ Cancelar", use_container_width=True):
                        st.session_state.show_password_reset = False
                        st.rerun()
                
                if submitted_reset:
                    if reset_email:
                        # Verifica se o usuário existe
                        user = get_user_by_email(reset_email)
                        
                        if user:
                            # Gera código de 6 dígitos
                            import random
                            reset_code = str(random.randint(100000, 999999))
                            
                            # Armazena no session_state (em produção, enviar por email)
                            st.session_state.reset_code = reset_code
                            st.session_state.reset_email = reset_email
                            st.session_state.reset_user_id = user['id']
                            st.session_state.show_reset_code_form = True
                            
                            st.success(f"✅ Código de recuperação gerado!")
                            st.info(f"🔐 **Código temporário:** {reset_code}")
                            st.caption("⚠️ Em produção, este código seria enviado por email")
                            st.rerun()
                        else:
                            st.error("❌ Email não encontrado no sistema")
                    else:
                        st.warning("⚠️ Digite seu email")
            
            # Formulário para inserir código e nova senha
            if st.session_state.get('show_reset_code_form', False):
                st.markdown("---")
                
                with st.form("new_password_form"):
                    st.markdown("#### 🔐 Digite o código e a nova senha")
                    
                    input_code = st.text_input("Código de 6 dígitos", max_chars=6, placeholder="123456")
                    new_password = st.text_input("Nova senha", type="password", placeholder="Mínimo 8 caracteres")
                    confirm_password = st.text_input("Confirme a nova senha", type="password")
                    
                    if st.form_submit_button("✅ Alterar Senha", use_container_width=True):
                        errors = []
                        
                        if not input_code:
                            errors.append("Digite o código de verificação")
                        elif input_code != st.session_state.get('reset_code'):
                            errors.append("Código inválido")
                        
                        if not new_password:
                            errors.append("Digite a nova senha")
                        elif len(new_password) < 8:
                            errors.append("Senha deve ter no mínimo 8 caracteres")
                        
                        if new_password != confirm_password:
                            errors.append("As senhas não coincidem")
                        
                        if errors:
                            for error in errors:
                                st.error(f"❌ {error}")
                        else:
                            # Atualiza a senha usando o mesmo método do auth.py (PBKDF2)
                            from auth import hash_password
                            new_hash = hash_password(new_password)
                            
                            if update_user_password(st.session_state.reset_user_id, new_hash):
                                st.success("✅ Senha alterada com sucesso!")
                                st.info("🔓 Faça login com sua nova senha")
                                
                                # Limpa session state
                                st.session_state.show_password_reset = False
                                st.session_state.show_reset_code_form = False
                                del st.session_state.reset_code
                                del st.session_state.reset_email
                                del st.session_state.reset_user_id
                                
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("❌ Erro ao atualizar senha. Tente novamente.")
        
        with tab2:
            st.markdown("#### Crie sua conta")
            
            with st.form("signup_form"):
                full_name = st.text_input("Nome Completo", placeholder="João Silva")
                email_signup = st.text_input("Email", placeholder="joao@empresa.com")
                password_signup = st.text_input("Senha", type="password", placeholder="Mínimo 8 caracteres")
                password_confirm = st.text_input("Confirme a Senha", type="password")
                
                st.markdown("#### Escolha seu Plano")
                
                plan_col1, plan_col2, plan_col3 = st.columns(3)
                
                with plan_col1:
                    st.markdown("""
                    **Profissional**
                    - R$ 199/mês
                    - 2 uploads/mês
                    - Dashboard básico
                    """)
                
                with plan_col2:
                    st.markdown("""
                    **Profissional Gold** ⭐
                    - R$ 399/mês
                    - 6 uploads/mês
                    - 2 contas bancárias
                    - Dashboard completo
                    """)
                
                with plan_col3:
                    st.markdown("""
                    **Premium** 👑
                    - R$ 699/mês
                    - Uploads ilimitados
                    - 4 contas bancárias
                    - Suporte 24/7
                    """)
                
                plan = st.selectbox(
                    "Selecione o plano",
                    ["Profissional", "Profissional Gold", "Profissional Premium"]
                )
                
                terms = st.checkbox("Aceito os termos de uso e política de privacidade")
                
                submit = st.form_submit_button("🚀 Criar Conta")
                
                if submit:
                    if not all([full_name, email_signup, password_signup, password_confirm]):
                        st.error("❌ Preencha todos os campos")
                    elif len(password_signup) < 8:
                        st.error("❌ A senha deve ter no mínimo 8 caracteres")
                    elif password_signup != password_confirm:
                        st.error("❌ As senhas não coincidem")
                    elif not terms:
                        st.error("❌ Você precisa aceitar os termos")
                    else:
                        with st.spinner("Criando conta..."):
                            user, message = register_user(email_signup, password_signup, full_name, plan)
                            
                            if user:
                                st.success(f"✅ {message}")
                                st.info("📧 Faça login com suas credenciais na aba 'Login'")
                            else:
                                st.error(f"❌ {message}")

# ==========================================
# SIDEBAR
# ==========================================

def show_sidebar():
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user['full_name']}")
        st.markdown(f"**Plano:** {st.session_state.user['plan']}")
        
        st.markdown("---")
        
        # ===== CONFIGURAÇÃO DO MODELO DE IA =====
        if st.button("🤖 Configurar IA", use_container_width=True, key="toggle_ai"):
            st.session_state.sidebar_expanded['ai_config'] = not st.session_state.sidebar_expanded['ai_config']
        
        if st.session_state.sidebar_expanded['ai_config']:
            with st.container():
                model_choice = st.selectbox(
                    "Escolha o modelo:",
                    ["Selecione...", "Google Gemini", "OpenAI GPT-4", "Groq Llama", "Anthropic Claude"],
                    key="ai_model_select"
                )
                
                if model_choice != "Selecione...":
                    api_key_input = st.text_input(
                        f"API Key:",
                        type="password",
                        key="ai_api_key"
                    )
                    
                    if st.button("🔌 Conectar", key="connect_ai", use_container_width=True):
                        if api_key_input:
                            model_map = {
                                "Google Gemini": "gemini",
                                "OpenAI GPT-4": "openai",
                                "Groq Llama": "groq",
                                "Anthropic Claude": "anthropic"
                            }
                            
                            client = initialize_ai_client(model_map[model_choice], api_key_input)
                            
                            if client:
                                st.session_state.ai_client = client
                                st.session_state.ai_model_type = model_map[model_choice]
                                # Recolhe automaticamente após conectar
                                st.session_state.sidebar_expanded['ai_config'] = False
                                st.success("✅ IA Conectada!")
                                st.rerun()
                            else:
                                st.error("❌ Erro ao conectar")
                        else:
                            st.warning("⚠️ Insira a API Key")
        
        if st.session_state.ai_client:
            st.success(f"🟢 IA Ativa: {st.session_state.ai_model_type}")
        
        st.markdown("---")
        
        # ===== UPLOAD DE DOCUMENTOS =====
        if st.button("📤 Upload de Documentos", use_container_width=True, key="toggle_uploads"):
            st.session_state.sidebar_expanded['uploads'] = not st.session_state.sidebar_expanded['uploads']
        
        if st.session_state.sidebar_expanded['uploads']:
            with st.container():
                st.markdown("**📎 Tipos aceitos:**")
                st.caption("• Notas Fiscais (XML, PDF)")
                st.caption("• Extratos Bancários (PDF, CSV)")
                st.caption("• Guias de Impostos (PDF)")
                st.caption("• Boletos (PDF)")
                st.caption("• Recibos e Comprovantes (JPG, PNG)")
                st.caption("🤖 **OCR automático** para imagens e PDFs escaneados")
                
                uploaded_files = st.file_uploader(
                    "Arraste arquivos aqui ou clique para selecionar",
                    type=['pdf', 'xml', 'csv', 'xlsx', 'jpg', 'jpeg', 'png'],
                    accept_multiple_files=True,
                    key="document_uploader",
                    help="Suporta PDFs digitais, PDFs escaneados (OCR), XMLs, CSVs e imagens (JPG/PNG). Para melhor precisão do OCR, use imagens com boa resolução (300 DPI ou mais)."
                )
                
                if uploaded_files:
                    st.success(f"✅ {len(uploaded_files)} arquivo(s) selecionado(s)")
                    
                    if st.button("🚀 Processar Documentos", use_container_width=True, key="process_docs"):
                        process_uploaded_documents(uploaded_files)
        
        st.markdown("---")
        
        # ===== MENU DE NAVEGAÇÃO =====
        if not st.session_state.company:
            if st.button("🏢 Cadastrar Empresa", use_container_width=True):
                st.session_state.current_page = 'company_form'
        
        st.markdown("---")
        
        if st.button("🚪 Sair", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ==========================================
# GESTÃO DE FUNCIONÁRIOS
# ==========================================

def show_employee_management():
    """Interface completa de gestão de funcionários"""
    
    if not st.session_state.company:
        st.warning("⚠️ Cadastre sua empresa primeiro para gerenciar funcionários")
        return
    
    company_id = st.session_state.company['id']
    
    # Header
    st.markdown('<div class="section-header">👥 Gestão de Funcionários</div>', unsafe_allow_html=True)
    
    # Tabs: Listagem e Cadastro
    tab_list, tab_new = st.tabs(["📋 Funcionários Cadastrados", "➕ Novo Funcionário"])
    
    # ===== TAB: LISTAGEM =====
    with tab_list:
        # Busca funcionários
        employees = get_employees_by_company(company_id, is_active=True)
        
        if not employees:
            st.info("📝 Nenhum funcionário cadastrado ainda. Use a aba 'Novo Funcionário' para adicionar.")
        else:
            st.markdown(f"**Total de funcionários ativos:** {len(employees)}")
            st.markdown("---")
            
            # Filtros
            col1, col2, col3 = st.columns(3)
            with col1:
                search_name = st.text_input("🔍 Buscar por nome", key="search_employee_name")
            with col2:
                filter_department = st.selectbox(
                    "Filtrar por departamento",
                    ["Todos"] + list(set([emp.get('department', 'Sem departamento') for emp in employees]))
                )
            with col3:
                filter_position = st.selectbox(
                    "Filtrar por cargo",
                    ["Todos"] + list(set([emp.get('position', 'Sem cargo') for emp in employees]))
                )
            
            # Aplica filtros
            filtered_employees = employees
            if search_name:
                filtered_employees = [emp for emp in filtered_employees 
                                    if search_name.lower() in emp.get('full_name', '').lower()]
            if filter_department != "Todos":
                filtered_employees = [emp for emp in filtered_employees 
                                    if emp.get('department') == filter_department]
            if filter_position != "Todos":
                filtered_employees = [emp for emp in filtered_employees 
                                    if emp.get('position') == filter_position]
            
            st.markdown(f"**Mostrando:** {len(filtered_employees)} funcionário(s)")
            st.markdown("---")
            
            # Listagem em cards
            for emp in filtered_employees:
                with st.expander(f"👤 {emp.get('full_name', 'Sem nome')} - {emp.get('position', 'Sem cargo')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📋 Dados Pessoais**")
                        st.markdown(f"**Nome completo:** {emp.get('full_name', 'N/A')}")
                        st.markdown(f"**CPF:** {emp.get('cpf', 'N/A')}")
                        st.markdown(f"**Data de nascimento:** {emp.get('birth_date', 'N/A')}")
                        st.markdown(f"**E-mail:** {emp.get('email', 'N/A')}")
                        st.markdown(f"**Telefone:** {emp.get('phone', 'N/A')}")
                        
                        st.markdown("**📍 Endereço**")
                        st.markdown(f"{emp.get('address', 'N/A')}")
                    
                    with col2:
                        st.markdown("**💼 Dados Profissionais**")
                        st.markdown(f"**Cargo:** {emp.get('position', 'N/A')}")
                        st.markdown(f"**Departamento:** {emp.get('department', 'N/A')}")
                        st.markdown(f"**Data de admissão:** {emp.get('hire_date', 'N/A')}")
                        st.markdown(f"**Salário:** R$ {float(emp.get('salary', 0)):,.2f}")
                        st.markdown(f"**Tipo de contrato:** {emp.get('contract_type', 'N/A')}")
                        st.markdown(f"**Jornada:** {emp.get('work_schedule', 'N/A')}")
                        
                        st.markdown("**💳 Dados Bancários**")
                        st.markdown(f"**Banco:** {emp.get('bank_name', 'N/A')}")
                        st.markdown(f"**Agência:** {emp.get('bank_branch', 'N/A')}")
                        st.markdown(f"**Conta:** {emp.get('bank_account', 'N/A')}")
                    
                    # Ações
                    col_actions1, col_actions2 = st.columns(2)
                    with col_actions1:
                        if st.button("✏️ Editar", key=f"edit_emp_{emp['id']}", use_container_width=True):
                            st.info("🚧 Funcionalidade de edição em desenvolvimento")
                    with col_actions2:
                        if st.button("🗑️ Desativar", key=f"deactivate_emp_{emp['id']}", use_container_width=True):
                            # Atualiza para is_active = False
                            try:
                                supabase.table('employees').update({'is_active': False}).eq('id', emp['id']).execute()
                                st.success("✅ Funcionário desativado com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Erro ao desativar: {str(e)}")
    
    # ===== TAB: NOVO FUNCIONÁRIO =====
    with tab_new:
        st.markdown("### ➕ Cadastrar Novo Funcionário")
        
        with st.form("employee_form", clear_on_submit=True):
            # Seção 1: Dados Pessoais
            st.markdown("#### 📋 Dados Pessoais")
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Nome completo *", placeholder="João Silva Santos")
                cpf = st.text_input("CPF *", placeholder="000.000.000-00", max_chars=14)
                birth_date = st.date_input("Data de nascimento *", value=None)
                email = st.text_input("E-mail", placeholder="joao@email.com")
            
            with col2:
                phone = st.text_input("Telefone", placeholder="(11) 98765-4321")
                address = st.text_area("Endereço completo", placeholder="Rua, número, bairro, cidade - UF, CEP")
            
            st.markdown("---")
            
            # Seção 2: Dados Profissionais
            st.markdown("#### 💼 Dados Profissionais")
            col3, col4 = st.columns(2)
            
            with col3:
                position = st.text_input("Cargo *", placeholder="Analista de Sistemas")
                department = st.selectbox(
                    "Departamento *",
                    ["Administrativo", "Financeiro", "Comercial", "Operacional", "TI", "RH", "Marketing", "Outro"]
                )
                hire_date = st.date_input("Data de admissão *", value=datetime.now().date())
                salary = st.number_input("Salário (R$) *", min_value=0.0, step=100.0, format="%.2f")
            
            with col4:
                contract_type = st.selectbox(
                    "Tipo de contrato *",
                    ["CLT", "PJ", "Estágio", "Temporário", "Autônomo"]
                )
                work_schedule = st.text_input("Jornada de trabalho", placeholder="Segunda a Sexta, 9h às 18h")
                pis_pasep = st.text_input("PIS/PASEP", placeholder="000.00000.00-0")
            
            st.markdown("---")
            
            # Seção 3: Dados Bancários
            st.markdown("#### 💳 Dados Bancários")
            col5, col6 = st.columns(2)
            
            with col5:
                bank_name = st.text_input("Banco", placeholder="Banco do Brasil")
                bank_branch = st.text_input("Agência", placeholder="1234-5")
            
            with col6:
                bank_account = st.text_input("Conta", placeholder="12345-6")
                pix_key = st.text_input("Chave PIX", placeholder="CPF, e-mail ou telefone")
            
            st.markdown("---")
            
            # Seção 4: Observações
            notes = st.text_area("Observações", placeholder="Informações adicionais sobre o funcionário...")
            
            # Botão de submissão
            submitted = st.form_submit_button("💾 Cadastrar Funcionário", use_container_width=True)
            
            if submitted:
                # Validações
                errors = []
                
                if not full_name:
                    errors.append("Nome completo é obrigatório")
                if not cpf:
                    errors.append("CPF é obrigatório")
                elif not validate_cpf(cpf):
                    errors.append("CPF inválido. Verifique o formato e os dígitos.")
                if not birth_date:
                    errors.append("Data de nascimento é obrigatória")
                if not position:
                    errors.append("Cargo é obrigatório")
                if not department:
                    errors.append("Departamento é obrigatório")
                if not hire_date:
                    errors.append("Data de admissão é obrigatória")
                if salary <= 0:
                    errors.append("Salário deve ser maior que zero")
                if not contract_type:
                    errors.append("Tipo de contrato é obrigatório")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    # Formata CPF
                    cpf_formatted = format_cpf(cpf)
                    
                    # Prepara dados para inserção
                    employee_data = {
                        'company_id': company_id,
                        'full_name': full_name,
                        'cpf': cpf_formatted,
                        'birth_date': birth_date.isoformat() if birth_date else None,
                        'email': email if email else None,
                        'phone': phone if phone else None,
                        'address': address if address else None,
                        'position': position,
                        'department': department,
                        'hire_date': hire_date.isoformat() if hire_date else None,
                        'salary': float(salary),
                        'contract_type': contract_type,
                        'work_schedule': work_schedule if work_schedule else None,
                        'pis_pasep': pis_pasep if pis_pasep else None,
                        'bank_name': bank_name if bank_name else None,
                        'bank_branch': bank_branch if bank_branch else None,
                        'bank_account': bank_account if bank_account else None,
                        'pix_key': pix_key if pix_key else None,
                        'notes': notes if notes else None,
                        'is_active': True
                    }
                    
                    # Salva no banco
                    try:
                        result = create_employee(employee_data)
                        
                        if result:
                            st.success(f"✅ Funcionário {full_name} cadastrado com sucesso!")
                            st.balloons()
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("❌ Erro ao cadastrar funcionário. Verifique os dados e tente novamente.")
                    except Exception as e:
                        st.error(f"❌ Erro ao cadastrar: {str(e)}")

# ==========================================
# GESTÃO DE USUÁRIOS E NÍVEIS DE ACESSO
# ==========================================

def show_user_management():
    """Interface completa de gestão de usuários com níveis de acesso"""
    
    if not st.session_state.company:
        st.warning("⚠️ Cadastre sua empresa primeiro para gerenciar usuários")
        return
    
    company_id = st.session_state.company['id']
    current_user_id = st.session_state.user['id']
    
    # Verifica o nível de acesso do usuário atual
    user_access_level = get_user_access_level(current_user_id, company_id)
    if not user_access_level:
        # Fallback: se não encontrou no banco, considera owner como senior
        is_senior = st.session_state.user.get('email') == st.session_state.company.get('user_email')
    else:
        is_senior = user_access_level == 'senior'
    
    # Header
    st.markdown('<div class="section-header">🔑 Gestão de Usuários</div>', unsafe_allow_html=True)
    
    # Indicador de nível de acesso atual
    if is_senior:
        st.info("👑 **Seu nível de acesso:** Senior (permissões completas)")
    else:
        st.info("👤 **Seu nível de acesso:** Geral (permissões limitadas)")
    
    # Tabs
    tab_list, tab_new, tab_approvals = st.tabs([
        "📋 Usuários Cadastrados", 
        "➕ Novo Usuário", 
        f"✋ Aprovações Pendentes"
    ])
    
    # ===== TAB: LISTAGEM =====
    with tab_list:
        st.markdown("### 📋 Usuários do Sistema")
        
        # Busca usuários do banco de dados
        users = get_users_by_company(company_id)
        
        if not users:
            st.info("📝 Nenhum usuário adicional cadastrado. Use a aba 'Novo Usuário' para adicionar.")
        else:
            st.markdown(f"**Total de usuários ativos:** {len(users)}")
            st.markdown("---")
            
            for user in users:
                with st.expander(f"👤 {user.get('full_name')} - {user.get('email')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Nome:** {user.get('full_name')}")
                        st.markdown(f"**E-mail:** {user.get('email')}")
                        st.markdown(f"**Nível de acesso:** {user.get('access_level').title()}")
                        st.markdown(f"**Status:** {'✅ Ativo' if user.get('is_active') else '❌ Inativo'}")
                    
                    with col2:
                        st.markdown(f"**Criado em:** {user.get('created_at', 'N/A')}")
                        
                        # Ações (apenas para usuários senior)
                        if is_senior:
                            st.markdown("**Ações:**")
                            
                            col_a1, col_a2 = st.columns(2)
                            
                            with col_a1:
                                new_level = "senior" if user.get('access_level') == "geral" else "geral"
                                if st.button(
                                    f"🔄 Alterar para {new_level.title()}",
                                    key=f"change_level_{user['id']}",
                                    use_container_width=True
                                ):
                                    if update_user_access_level(user['id'], new_level):
                                        st.success(f"✅ Nível alterado para {new_level.title()}!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Erro ao alterar nível de acesso")
                            
                            with col_a2:
                                if st.button(
                                    "🗑️ Desativar",
                                    key=f"deactivate_user_{user['id']}",
                                    use_container_width=True
                                ):
                                    if deactivate_user(user['id']):
                                        st.success("✅ Usuário desativado!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Erro ao desativar usuário")
                        else:
                            st.warning("⚠️ Apenas usuários Senior podem gerenciar outros usuários")
    
    # ===== TAB: NOVO USUÁRIO =====
    with tab_new:
        st.markdown("### ➕ Cadastrar Novo Usuário")
        
        if not is_senior:
            st.warning("⚠️ Apenas usuários Senior podem cadastrar novos usuários")
            return
        
        with st.form("user_form", clear_on_submit=True):
            st.markdown("#### 👤 Informações do Usuário")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_full_name = st.text_input("Nome completo *", placeholder="Maria Silva")
                new_email = st.text_input("E-mail *", placeholder="maria@empresa.com")
            
            with col2:
                new_password = st.text_input("Senha temporária *", type="password", placeholder="Mínimo 8 caracteres")
                new_access_level = st.selectbox(
                    "Nível de acesso *",
                    ["geral", "senior"],
                    format_func=lambda x: "👤 Geral - Pode fazer upload e solicitar aprovações" if x == "geral" else "👑 Senior - Pode aprovar e gerenciar tudo"
                )
            
            st.markdown("---")
            st.markdown("#### 📋 Permissões por Nível")
            
            col_p1, col_p2 = st.columns(2)
            
            with col_p1:
                st.markdown("**👤 Usuário Geral:**")
                st.caption("✅ Fazer upload de documentos")
                st.caption("✅ Ver análise da IA")
                st.caption("✅ Solicitar aprovação")
                st.caption("❌ Aprovar documentos")
                st.caption("❌ Gerenciar usuários")
            
            with col_p2:
                st.markdown("**👑 Usuário Senior:**")
                st.caption("✅ Todas as permissões do Geral")
                st.caption("✅ **Aprovar/Rejeitar documentos**")
                st.caption("✅ **Inserir dados no banco**")
                st.caption("✅ **Gerenciar usuários**")
                st.caption("✅ **Alterar níveis de acesso**")
            
            submitted = st.form_submit_button("💾 Cadastrar Usuário", use_container_width=True)
            
            if submitted:
                errors = []
                
                if not new_full_name:
                    errors.append("Nome completo é obrigatório")
                if not new_email:
                    errors.append("E-mail é obrigatório")
                elif '@' not in new_email:
                    errors.append("E-mail inválido")
                if not new_password:
                    errors.append("Senha é obrigatória")
                elif len(new_password) < 8:
                    errors.append("Senha deve ter no mínimo 8 caracteres")
                
                # Verifica duplicidade
                existing_users = get_users_by_company(company_id)
                if any(u.get('email') == new_email for u in existing_users):
                    errors.append("E-mail já cadastrado")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    # Cria hash da senha
                    password_hash = hashlib.sha256(new_password.encode()).hexdigest()
                    
                    # Cria usuário no banco
                    new_user = create_company_user(
                        company_id=company_id,
                        email=new_email,
                        full_name=new_full_name,
                        access_level=new_access_level,
                        password_hash=password_hash
                    )
                    
                    if new_user:
                        st.success(f"✅ Usuário {new_full_name} cadastrado com nível {new_access_level.title()}!")
                        st.info(f"📧 Envie as credenciais para: {new_email}\nSenha temporária: {new_password}")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("❌ Erro ao cadastrar usuário no banco de dados")
    
    # ===== TAB: APROVAÇÕES =====
    with tab_approvals:
        show_approval_queue(is_senior)

def show_approval_queue(is_senior: bool):
    """Fila de aprovações para usuários Senior"""
    
    st.markdown("### ✋ Fila de Aprovações")
    
    if not is_senior:
        st.warning("⚠️ Apenas usuários Senior podem visualizar e aprovar solicitações")
        st.info("💡 Quando você fizer upload de documentos, eles aparecerão aqui para aprovação de um usuário Senior")
        return
    
    if not st.session_state.company:
        st.warning("⚠️ Cadastre sua empresa primeiro")
        return
    
    company_id = st.session_state.company['id']
    
    # Busca aprovações pendentes do banco
    pending = get_pending_approvals(company_id)
    
    if not pending:
        st.success("✅ Não há solicitações pendentes de aprovação!")
        return
    
    st.markdown(f"**📊 Total de solicitações pendentes:** {len(pending)}")
    st.markdown("---")
    
    for request in pending:
        priority_icon = "🔴" if request.get('priority') == 'urgent' else "🟡" if request.get('priority') == 'high' else "🟢"
        
        # Busca dados do usuário solicitante (vem do JOIN)
        requester = request.get('users', {})
        requester_name = requester.get('full_name', 'Usuário desconhecido')
        
        with st.expander(
            f"{priority_icon} {request.get('document_type', 'Documento')} - Solicitado por {requester_name}",
            expanded=True
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**📄 Tipo de documento:** {request.get('document_type')}")
                st.markdown(f"**👤 Solicitante:** {requester_name} ({requester.get('email', 'N/A')})")
                st.markdown(f"**📅 Data da solicitação:** {request.get('created_at')}")
                st.markdown(f"**⚡ Prioridade:** {request.get('priority', 'normal').title()}")
                
                st.markdown("---")
                st.markdown("**🤖 Análise da IA:**")
                ai_analysis = request.get('ai_analysis', {})
                st.markdown(f"- **Confiança:** {ai_analysis.get('confianca', 0)*100:.0f}%")
                st.markdown(f"- **Ação recomendada:** {ai_analysis.get('acao_recomendada', 'N/A')}")
                
                st.markdown("---")
                st.markdown("**📊 Dados a serem inseridos:**")
                st.json(request.get('document_data', {}))
                
                if request.get('requester_notes'):
                    st.markdown("---")
                    st.markdown("**💬 Observações do solicitante:**")
                    st.info(request.get('requester_notes'))
            
            with col2:
                st.markdown("**⚙️ Ações:**")
                
                approval_notes = st.text_area(
                    "Observações (opcional)",
                    key=f"notes_{request['id']}",
                    placeholder="Adicione observações sobre a aprovação..."
                )
                
                col_a1, col_a2 = st.columns(2)
                
                with col_a1:
                    if st.button("✅ Aprovar", key=f"approve_{request['id']}", use_container_width=True):
                        # Aprova no banco
                        if approve_request(request['id'], st.session_state.user['id'], approval_notes):
                            # Salva o documento no banco
                            doc_data = request.get('document_data', {})
                            doc_type = request.get('document_type')
                            
                            # Mapeia tipo de documento para função de salvamento
                            success = False
                            if doc_type in ['Cliente', 'Fornecedor']:
                                # Cria terceiro (cliente ou fornecedor)
                                third_party_data = {
                                    'type': 'cliente' if doc_type == 'Cliente' else 'fornecedor',
                                    'name': doc_data.get('nome') or doc_data.get('razao_social'),
                                    'cpf_cnpj': doc_data.get('cpf_cnpj') or doc_data.get('cpf') or doc_data.get('cnpj'),
                                    'email': doc_data.get('email'),
                                    'phone': doc_data.get('telefone'),
                                    'legal_type': 'pf' if len(str(doc_data.get('cpf_cnpj', '')).replace('-', '').replace('.', '').replace('/', '')) == 11 else 'pj'
                                }
                                success = create_third_party(st.session_state.company['id'], third_party_data)
                            elif doc_type == 'Funcionário':
                                # Cria funcionário
                                employee_data = {
                                    'company_id': st.session_state.company['id'],
                                    'full_name': doc_data.get('nome'),
                                    'cpf': doc_data.get('cpf'),
                                    'position': doc_data.get('cargo'),
                                    'department': doc_data.get('departamento'),
                                    'admission_date': doc_data.get('data_admissao'),
                                    'salary': doc_data.get('salario'),
                                    'is_active': True
                                }
                                success = create_employee(employee_data)
                            
                            if success:
                                st.success(f"✅ Documento aprovado e cadastrado!")
                                st.balloons()
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("❌ Documento aprovado, mas houve erro ao cadastrar no banco")
                        else:
                            st.error("❌ Erro ao aprovar solicitação")
                
                with col_a2:
                    if st.button("❌ Rejeitar", key=f"reject_{request['id']}", use_container_width=True):
                        if not approval_notes:
                            st.error("❌ Informe o motivo da rejeição nas observações")
                        else:
                            if reject_request(request['id'], st.session_state.user['id'], approval_notes):
                                st.warning(f"⚠️ Documento rejeitado. Motivo: {approval_notes}")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("❌ Erro ao rejeitar solicitação")

# ==========================================
# FORMULÁRIO DE EMPRESA COM LOGO
# ==========================================

def show_company_form_inline(unique_id=""):
    with st.container():
        # Upload do Logo
        st.markdown("#### 🎨 Logo da Empresa")
        
        # Mostra logo atual se existir
        if st.session_state.company and st.session_state.company.get('logo_path'):
            try:
                st.image(st.session_state.company['logo_path'], width=60)
                st.caption("Logo atual")
            except:
                st.caption("Erro ao carregar logo")
        
        logo_file = st.file_uploader(
            "Envie o logo (PNG/JPG - máx 5MB)",
            type=['png', 'jpg', 'jpeg'],
            key=f"logo_uploader_{unique_id}",
            label_visibility="collapsed"
        )
        
        if logo_file:
            file_size = len(logo_file.getvalue())
            max_size = 5 * 1024 * 1024
            
            if file_size > max_size:
                st.error(f"❌ Arquivo muito grande: {file_size/1024/1024:.2f}MB. Máximo: 5MB")
            else:
                st.info(f"📄 {logo_file.name} ({file_size/1024:.2f}KB)")
                
                if st.button("💾 Salvar Logo", use_container_width=True):
                    if st.session_state.company:
                        with st.spinner("Salvando logo..."):
                            try:
                                logo_bytes = logo_file.getvalue()
                                
                                # Valida imagem
                                try:
                                    img = Image.open(io.BytesIO(logo_bytes))
                                    st.success(f"✅ Imagem válida: {img.format} - {img.size[0]}x{img.size[1]}px")
                                except Exception as e:
                                    st.error(f"❌ Arquivo não é uma imagem: {e}")
                                    return
                                
                                # Processa imagem
                                try:
                                    # Detecta o tipo de conteúdo
                                    content_type = logo_file.type
                                    if not content_type:
                                        content_type = 'image/png'  # fallback
                                    
                                    # Converte para base64
                                    base64_logo = base64.b64encode(logo_bytes).decode()
                                    
                                    # Cria a URL data
                                    logo_url = f"data:{content_type};base64,{base64_logo}"
                                    
                                    # Mostra preview da imagem
                                    st.image(logo_file, caption="Preview do Logo", width=60)
                                except Exception as e:
                                    st.error(f"❌ Erro ao processar a imagem: {str(e)}")
                                    st.info("Por favor, tente com outra imagem ou formato")
                                    st.image(logo_file, caption="Preview do Logo", width=100)
                                    
                                # Atualiza no banco
                                success = update_company_logo(st.session_state.company['id'], logo_url)
                                
                                if success:
                                    st.session_state.company['logo_path'] = logo_url
                                    st.success("✅ Logo atualizado!")
                                    st.rerun()
                                else:
                                    st.error("❌ Erro ao atualizar no banco")
                                    st.info("Verifique os logs do terminal")
                                    st.code("""
Verifique:
1. O formato da imagem é suportado (PNG, JPG, JPEG ou GIF)?
2. O tamanho do arquivo é menor que 5MB?
3. A imagem não está corrompida?
4. O tipo de conteúdo (content-type) está correto?
                                    """)
                            except Exception as e:
                                st.error(f"❌ Erro: {e}")
                    else:
                        st.warning("⚠️ Cadastre a empresa primeiro")
        
        st.markdown("---")
        
        # Dados da empresa
        with st.form(f"company_form_{unique_id}", clear_on_submit=False):
            if st.session_state.company:
                cnpj = st.text_input("CNPJ", value=st.session_state.company.get('cnpj', ''))
                name = st.text_input("Razão Social", value=st.session_state.company.get('name', ''))
                trade_name = st.text_input("Nome Fantasia", value=st.session_state.company.get('trade_name', ''))
                tax_regime = st.selectbox(
                    "Regime Tributário",
                    ["Simples Nacional", "Lucro Presumido", "Lucro Real"],
                    index=["Simples Nacional", "Lucro Presumido", "Lucro Real"].index(
                        st.session_state.company.get('tax_regime', 'Simples Nacional')
                    )
                )
            else:
                cnpj = st.text_input("CNPJ")
                name = st.text_input("Razão Social")
                trade_name = st.text_input("Nome Fantasia")
                tax_regime = st.selectbox(
                    "Regime Tributário",
                    ["Simples Nacional", "Lucro Presumido", "Lucro Real"]
                )
            
            submit = st.form_submit_button("💾 Salvar", use_container_width=True)
            
            if submit:
                if not cnpj or not name:
                    st.error("❌ CNPJ e Razão Social obrigatórios")
                elif not validate_cnpj(cnpj):
                    st.error("❌ CNPJ inválido")
                else:
                    company_data = {
                        'cnpj': cnpj,
                        'name': name,
                        'trade_name': trade_name,
                        'tax_regime': tax_regime
                    }
                    
                    if st.session_state.company:
                        try:
                            supabase.table('companies').update(company_data).eq('id', st.session_state.company['id']).execute()
                            st.success("✅ Empresa atualizada!")
                            st.session_state.company.update(company_data)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erro: {e}")
                    else:
                        result = create_company(st.session_state.user['id'], company_data)
                        if result:
                            st.success("✅ Empresa cadastrada!")
                            st.session_state.company = result
                            st.rerun()
                        else:
                            st.error("❌ Erro ao cadastrar")

# ==========================================
# FUNÇÕES AUXILIARES PARA ANÁLISE FISCAL
# ==========================================

def calculate_regime_limits():
    """Retorna limites de faturamento por regime tributário"""
    return {
        'MEI': 81000.00,  # R$ 81 mil/ano
        'Simples Nacional': 4800000.00,  # R$ 4,8 milhões/ano
        'Lucro Presumido': 78000000.00,  # R$ 78 milhões/ano
        'Lucro Real': float('inf')  # Sem limite
    }

def calculate_simples_tax(revenue_12m: float, anexo: int = 3) -> dict:
    """
    Calcula imposto do Simples Nacional
    Anexo 3 (Serviços) é o mais comum
    """
    # Tabela Simples Nacional - Anexo III (Serviços)
    faixas = [
        {'ate': 180000, 'aliquota': 0.060, 'deducao': 0},
        {'ate': 360000, 'aliquota': 0.112, 'deducao': 9360},
        {'ate': 720000, 'aliquota': 0.135, 'deducao': 17640},
        {'ate': 1800000, 'aliquota': 0.160, 'deducao': 35640},
        {'ate': 3600000, 'aliquota': 0.210, 'deducao': 125640},
        {'ate': 4800000, 'aliquota': 0.330, 'deducao': 648000}
    ]
    
    for faixa in faixas:
        if revenue_12m <= faixa['ate']:
            # Alíquota efetiva = (RBT12 × Aliq - PD) / RBT12
            aliquota_efetiva = (revenue_12m * faixa['aliquota'] - faixa['deducao']) / revenue_12m
            return {
                'aliquota': aliquota_efetiva,
                'valor_mensal': revenue_12m / 12 * aliquota_efetiva,
                'valor_anual': revenue_12m * aliquota_efetiva
            }
    
    # Se ultrapassar R$ 4,8 mi, não pode ser Simples
    return {'aliquota': 0, 'valor_mensal': 0, 'valor_anual': 0}

def calculate_lucro_presumido_tax(revenue: float, atividade: str = 'servicos') -> dict:
    """
    Calcula impostos no Lucro Presumido
    Presunção de 32% para serviços, 8% para comércio
    """
    # Presunção de lucro
    presuncao = 0.32 if atividade == 'servicos' else 0.08
    lucro_presumido = revenue * presuncao
    
    # IRPJ: 15% sobre lucro presumido + adicional 10% sobre excedente de R$ 20k/mês
    irpj_base = lucro_presumido * 0.15
    adicional_irpj = max(0, (lucro_presumido - 20000 * 12) * 0.10) if lucro_presumido > 240000 else 0
    irpj = irpj_base + adicional_irpj
    
    # CSLL: 9% sobre lucro presumido
    csll = lucro_presumido * 0.09
    
    # PIS: 0,65% sobre faturamento
    pis = revenue * 0.0065
    
    # COFINS: 3% sobre faturamento
    cofins = revenue * 0.03
    
    # ISS: ~5% sobre faturamento (varia por município, usando média)
    iss = revenue * 0.05 if atividade == 'servicos' else 0
    
    total = irpj + csll + pis + cofins + iss
    
    return {
        'irpj': irpj,
        'csll': csll,
        'pis': pis,
        'cofins': cofins,
        'iss': iss,
        'total': total,
        'aliquota': total / revenue if revenue > 0 else 0
    }

def calculate_lucro_real_tax(revenue: float, expenses: float, atividade: str = 'servicos') -> dict:
    """
    Calcula impostos no Lucro Real
    Usa lucro REAL (receita - despesas)
    """
    lucro_real = max(0, revenue - expenses)
    
    # IRPJ: 15% sobre lucro real + adicional 10% sobre excedente de R$ 20k/mês
    irpj_base = lucro_real * 0.15
    adicional_irpj = max(0, (lucro_real - 20000 * 12) * 0.10) if lucro_real > 240000 else 0
    irpj = irpj_base + adicional_irpj
    
    # CSLL: 9% sobre lucro real
    csll = lucro_real * 0.09
    
    # PIS: 1,65% sobre faturamento (não cumulativo)
    pis = revenue * 0.0165
    
    # COFINS: 7,6% sobre faturamento (não cumulativo)
    cofins = revenue * 0.076
    
    # ISS: ~5% sobre faturamento (varia por município)
    iss = revenue * 0.05 if atividade == 'servicos' else 0
    
    total = irpj + csll + pis + cofins + iss
    
    return {
        'irpj': irpj,
        'csll': csll,
        'pis': pis,
        'cofins': cofins,
        'iss': iss,
        'total': total,
        'aliquota': total / revenue if revenue > 0 else 0,
        'lucro_real': lucro_real
    }

def get_revenue_last_12_months(company_id: int, end_date: date) -> float:
    """Calcula receita bruta dos últimos 12 meses"""
    # Calcula data de início (12 meses atrás)
    start_date = end_date.replace(day=1)
    if start_date.month <= 12:
        start_date = start_date.replace(year=start_date.year - 1, month=start_date.month)
    else:
        start_date = start_date.replace(month=start_date.month - 12)
    
    # Soma receita bruta de todos os meses
    total_revenue = 0
    current_date = start_date
    
    while current_date <= end_date.replace(day=1):
        month_str = current_date.strftime('%Y-%m-01')
        month_dre = get_or_create_dre(company_id, month_str)
        total_revenue += month_dre.get('gross_revenue', 0)
        
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return total_revenue

# ==========================================
# SISTEMA DE PROCESSAMENTO DE DOCUMENTOS COM IA
# ==========================================

def create_document_analysis_prompt(file_name: str, file_type: str, content_preview: str = "") -> str:
    """Cria prompt para o agente de análise de documentos"""
    
    prompt = f"""Você é um AGENTE ESPECIALISTA em CIÊNCIA DE DADOS e ANÁLISE DOCUMENTAL FISCAL/CONTÁBIL.

🎯 SUA MISSÃO:
Analisar documentos fiscais, contábeis e financeiros e extrair informações estruturadas para cadastro em banco de dados.

📋 TIPOS DE DOCUMENTOS QUE VOCÊ PROCESSA:
1. **Notas Fiscais** (NF-e, NFS-e) - XML ou PDF
2. **Extratos Bancários** - PDF ou CSV
3. **Guias de Impostos** (DAS, DARF, GPS, GARE) - PDF
4. **Boletos Bancários** - PDF
5. **Recibos e Comprovantes** - PDF, imagem

⚙️ PROTOCOLO DE ANÁLISE:

**PASSO 1: IDENTIFICAÇÃO DO DOCUMENTO**
Identifique o tipo de documento analisando:
- Cabeçalhos e títulos
- Campos obrigatórios
- Layout e estrutura
- Palavras-chave específicas

**PASSO 2: EXTRAÇÃO DE DADOS**
Extraia TODAS as informações relevantes em formato JSON estruturado.

**PASSO 3: VALIDAÇÃO**
Verifique se todos os campos obrigatórios foram identificados.
Se algum campo estiver FALTANDO ou INCERTO, marque como "PENDENTE_CONFIRMACAO".

**PASSO 4: MAPEAMENTO PARA BANCO DE DADOS**
Determine a tabela de destino e os campos correspondentes.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 DOCUMENTO ATUAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nome do Arquivo: {file_name}
Tipo de Arquivo: {file_type}

{f"Prévia do Conteúdo:\\n{content_preview[:1000]}..." if content_preview else ""}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 FORMATO DE RESPOSTA ESPERADO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Responda APENAS com um JSON no seguinte formato:

{{
    "tipo_documento": "NOTA_FISCAL | EXTRATO_BANCARIO | GUIA_IMPOSTO | BOLETO | RECIBO | OUTRO",
    "confianca": 0.95,
    "tabela_destino": "accounts_payable | accounts_receivable | bank_transactions | tax_obligations",
    "dados_extraidos": {{
        "campo1": "valor1",
        "campo2": "valor2",
        ...
    }},
    "campos_pendentes": [
        {{
            "campo": "nome_do_campo",
            "motivo": "Não encontrado no documento",
            "sugestao": "Valor sugerido (se houver)"
        }}
    ],
    "validacao": {{
        "completo": true/false,
        "erros": ["lista de erros se houver"],
        "avisos": ["lista de avisos se houver"]
    }},
    "acao_recomendada": "CADASTRAR_AUTOMATICO | SOLICITAR_CONFIRMACAO | SOLICITAR_APROVACAO"
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗂️ MAPEAMENTO DE CAMPOS POR TIPO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**NOTA FISCAL → accounts_payable (se compra) ou accounts_receivable (se venda)**
- description: Descrição da NF
- amount: Valor total
- due_date: Data de vencimento
- emission_date: Data de emissão
- supplier/customer: Fornecedor ou Cliente
- document_number: Número da NF
- category: Categoria fiscal

**EXTRATO BANCÁRIO → bank_transactions**
- transaction_date: Data da transação
- description: Descrição
- amount: Valor (positivo=entrada, negativo=saída)
- balance: Saldo
- category: Categoria da transação

**GUIA DE IMPOSTO → tax_obligations**
- obligation_type: Tipo (DAS, DARF, etc)
- due_date: Vencimento
- amount: Valor
- reference_period: Período de referência
- status: Situação

**BOLETO → accounts_payable**
- description: Descrição do boleto
- amount: Valor
- due_date: Vencimento
- supplier: Beneficiário
- barcode: Código de barras
- document_number: Nosso número

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ REGRAS CRÍTICAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. SEMPRE responda APENAS com JSON válido (sem explicações adicionais)
2. Se não tiver CERTEZA (confiança < 70%), marque como PENDENTE_CONFIRMACAO
3. Datas devem estar no formato YYYY-MM-DD
4. Valores monetários devem ser números decimais (sem R$, pontos ou vírgulas)
5. Para campos obrigatórios ausentes, SEMPRE peça confirmação
6. Se o documento for ilegível ou corrompido, retorne erro claro

Agora analise o documento e retorne o JSON estruturado.
"""
    
    return prompt

def extract_text_from_pdf(file_bytes) -> str:
    """Extrai texto de PDF usando pdfplumber (melhor que PyPDF2)"""
    try:
        import pdfplumber
        from io import BytesIO
        
        text = ""
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if text.strip():
            return text
        else:
            # Se não conseguiu extrair texto, tenta OCR
            return extract_text_from_pdf_with_ocr(file_bytes)
    except Exception as e:
        st.warning(f"⚠️ Erro ao extrair texto do PDF: {str(e)}. Tentando OCR...")
        return extract_text_from_pdf_with_ocr(file_bytes)

def extract_text_from_pdf_with_ocr(file_bytes) -> str:
    """Extrai texto de PDF usando OCR (para PDFs escaneados)"""
    try:
        from pdf2image import convert_from_bytes
        import pytesseract
        from io import BytesIO
        
        # Converte PDF para imagens
        images = convert_from_bytes(file_bytes, dpi=300)
        
        text = ""
        for i, image in enumerate(images):
            # Aplica OCR em cada página
            page_text = pytesseract.image_to_string(image, lang='por')
            text += f"\n--- Página {i+1} ---\n{page_text}\n"
        
        return text if text.strip() else "[Não foi possível extrair texto do PDF]"
    except Exception as e:
        return f"[Erro ao aplicar OCR no PDF: {str(e)}. Instale o Tesseract-OCR em seu sistema]"

def extract_text_from_image(file_bytes) -> str:
    """Extrai texto de imagem usando OCR"""
    try:
        import pytesseract
        from PIL import Image
        from io import BytesIO
        
        # Abre a imagem
        image = Image.open(BytesIO(file_bytes))
        
        # Aplica OCR
        text = pytesseract.image_to_string(image, lang='por')
        
        return text if text.strip() else "[Não foi possível extrair texto da imagem]"
    except Exception as e:
        return f"[Erro ao aplicar OCR na imagem: {str(e)}. Instale o Tesseract-OCR em seu sistema]"

def extract_text_from_xml(file_bytes) -> str:
    """Extrai informações de XML (NFe)"""
    try:
        import xml.etree.ElementTree as ET
        
        xml_text = file_bytes.decode('utf-8')
        return xml_text[:2000]  # Primeiros 2000 caracteres
    except:
        return "[Erro ao ler XML]"

def extract_text_from_csv(file_bytes) -> str:
    """Extrai preview de CSV"""
    try:
        import pandas as pd
        from io import BytesIO
        
        df = pd.read_csv(BytesIO(file_bytes), nrows=10)
        return df.to_string()
    except:
        return "[Erro ao ler CSV]"

def process_uploaded_documents(uploaded_files):
    """Processa documentos enviados usando IA"""
    
    if not st.session_state.ai_client:
        st.error("❌ Configure um modelo de IA primeiro para processar documentos!")
        return
    
    if not st.session_state.company:
        st.error("❌ Cadastre sua empresa primeiro!")
        return
    
    # Inicializa lista de processamento
    if 'document_processing_queue' not in st.session_state:
        st.session_state.document_processing_queue = []
    
    with st.spinner("🔍 Analisando documentos..."):
        results = []
        
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_type = uploaded_file.type
            file_bytes = uploaded_file.read()
            
            # Extrai texto baseado no tipo
            content_preview = ""
            if file_type == "application/pdf":
                content_preview = extract_text_from_pdf(file_bytes)
            elif file_type in ["text/xml", "application/xml"]:
                content_preview = extract_text_from_xml(file_bytes)
            elif file_type == "text/csv":
                content_preview = extract_text_from_csv(file_bytes)
            elif file_type in ["image/jpeg", "image/png", "image/jpg"]:
                content_preview = extract_text_from_image(file_bytes)
            else:
                content_preview = "[Tipo de arquivo não suportado para extração automática]"
            
            # Cria prompt para análise
            analysis_prompt = create_document_analysis_prompt(file_name, file_type, content_preview)
            
            # Chama IA para análise
            try:
                import json
                
                response, _ = chat_with_ai(
                    st.session_state.ai_client,
                    st.session_state.ai_model_type,
                    analysis_prompt,
                    f"Analise o documento: {file_name}",
                    None
                )
                
                # Tenta extrair JSON da resposta
                # Remove markdown code blocks se houver
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()
                
                analysis_result = json.loads(response)
                
                results.append({
                    'file_name': file_name,
                    'analysis': analysis_result,
                    'file_bytes': file_bytes,
                    'processed': False
                })
                
            except Exception as e:
                st.error(f"❌ Erro ao analisar {file_name}: {str(e)}")
                results.append({
                    'file_name': file_name,
                    'analysis': None,
                    'error': str(e),
                    'processed': False
                })
        
        # Armazena resultados no session state
        st.session_state.document_processing_queue = results
        st.session_state.sidebar_expanded['uploads'] = False
        st.rerun()

def show_document_approval_interface():
    """Interface para revisar e aprovar documentos processados"""
    
    if 'document_processing_queue' not in st.session_state or not st.session_state.document_processing_queue:
        return
    
    # Verifica nível de acesso do usuário
    user_access_level = st.session_state.get('user_access_level', 'senior')
    is_senior = user_access_level == 'senior'
    
    st.markdown("---")
    
    if is_senior:
        st.markdown("### 📋 Documentos Aguardando Aprovação")
        st.caption("👑 Como usuário **Senior**, você pode aprovar e cadastrar documentos diretamente no banco")
    else:
        st.markdown("### 📋 Documentos Processados - Aguardando Envio para Aprovação")
        st.caption("👤 Como usuário **Geral**, seus documentos serão enviados para aprovação de um usuário Senior")
    
    pending_docs = [doc for doc in st.session_state.document_processing_queue if not doc.get('processed', False)]
    
    if not pending_docs:
        st.success("✅ Todos os documentos foram processados!")
        if st.button("🔄 Limpar Fila"):
            st.session_state.document_processing_queue = []
            st.rerun()
        return
    
    for idx, doc in enumerate(pending_docs):
        analysis = doc.get('analysis')
        
        if not analysis:
            st.error(f"❌ **{doc['file_name']}** - Erro: {doc.get('error', 'Desconhecido')}")
            continue
        
        with st.expander(f"📄 {doc['file_name']} - {analysis.get('tipo_documento', 'Tipo desconhecido')}", expanded=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Tipo:** {analysis.get('tipo_documento')}")
                st.markdown(f"**Confiança:** {analysis.get('confianca', 0)*100:.0f}%")
                st.markdown(f"**Destino:** `{analysis.get('tabela_destino')}`")
                
                st.markdown("**📊 Dados Extraídos:**")
                st.json(analysis.get('dados_extraidos', {}))
                
                # Campos pendentes
                if analysis.get('campos_pendentes'):
                    st.warning("⚠️ **Campos Pendentes de Confirmação:**")
                    for campo in analysis['campos_pendentes']:
                        user_value = st.text_input(
                            f"{campo['campo']}: {campo['motivo']}",
                            value=campo.get('sugestao', ''),
                            key=f"pending_{idx}_{campo['campo']}"
                        )
                        # Atualiza dados extraídos com valor fornecido
                        if user_value:
                            analysis['dados_extraidos'][campo['campo']] = user_value
            
            with col2:
                st.markdown("**🎯 Ação Recomendada:**")
                st.info(analysis.get('acao_recomendada', 'N/A'))
                
                if analysis.get('validacao'):
                    val = analysis['validacao']
                    if val.get('completo'):
                        st.success("✅ Validação OK")
                    else:
                        st.warning(f"⚠️ Incompleto")
                    
                    if val.get('erros'):
                        st.error("**Erros:**")
                        for erro in val['erros']:
                            st.markdown(f"- {erro}")
                
                st.markdown("---")
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if is_senior:
                        # Senior aprova diretamente
                        if st.button("✅ Aprovar", key=f"approve_{idx}", use_container_width=True):
                            save_document_to_database(doc)
                            st.session_state.document_processing_queue[idx]['processed'] = True
                            st.success(f"✅ {doc['file_name']} cadastrado!")
                            st.rerun()
                    else:
                        # Usuário Geral solicita aprovação
                        if st.button("📤 Enviar para Aprovação", key=f"send_approval_{idx}", use_container_width=True):
                            # Determina prioridade baseada na confiança da IA
                            confidence = analysis.get('confianca', 0)
                            if confidence >= 0.9:
                                priority = 'normal'
                            elif confidence >= 0.7:
                                priority = 'high'
                            else:
                                priority = 'urgent'
                            
                            # Cria solicitação de aprovação
                            request_data = {
                                'company_id': st.session_state.company['id'],
                                'requester_user_id': st.session_state.user['id'],
                                'document_type': analysis.get('tipo_documento'),
                                'document_file_name': doc['file_name'],
                                'document_data': analysis.get('dados_extraidos', {}),
                                'ai_analysis': analysis,
                                'ai_confidence': confidence,
                                'status': 'pending',
                                'priority': priority,
                                'requester_notes': f"Documento processado automaticamente via IA"
                            }
                            
                            if create_approval_request(request_data):
                                st.session_state.document_processing_queue[idx]['processed'] = True
                                st.success(f"✅ {doc['file_name']} enviado para aprovação!")
                                st.info("💡 Um usuário Senior receberá sua solicitação")
                                st.rerun()
                            else:
                                st.error("❌ Erro ao criar solicitação de aprovação")
                
                with col_btn2:
                    if st.button("❌ Rejeitar", key=f"reject_{idx}", use_container_width=True):
                        st.session_state.document_processing_queue[idx]['processed'] = True
                        st.warning(f"❌ {doc['file_name']} rejeitado!")
                        st.rerun()

def save_document_to_database(doc):
    """Salva documento aprovado no banco de dados"""
    
    analysis = doc['analysis']
    table = analysis.get('tabela_destino')
    data = analysis.get('dados_extraidos', {})
    company_id = st.session_state.company['id']
    
    try:
        if table in ['bills_payable', 'accounts_payable']:
            # Cadastra conta a pagar
            payable_data = {
                'description': data.get('description', 'Sem descrição'),
                'amount': float(data.get('amount', 0)),
                'due_date': data.get('due_date'),
                'issue_date': data.get('emission_date') or data.get('issue_date'),
                'document_number': data.get('document_number'),
                'notes': data.get('notes') or f"Importado de: {doc['file_name']}"
            }
            
            # Adiciona supplier_id se houver nome do fornecedor
            if data.get('supplier'):
                payable_data['notes'] = f"Fornecedor: {data['supplier']}\n" + (payable_data.get('notes') or '')
            
            result = create_account_payable(company_id, payable_data)
            if result:
                st.success(f"✅ Conta a pagar cadastrada com sucesso!")
            else:
                st.error("❌ Erro ao cadastrar conta a pagar")
            
        elif table in ['bills_receivable', 'accounts_receivable']:
            # Cadastra conta a receber
            receivable_data = {
                'description': data.get('description', 'Sem descrição'),
                'amount': float(data.get('amount', 0)),
                'due_date': data.get('due_date'),
                'issue_date': data.get('emission_date') or data.get('issue_date'),
                'document_number': data.get('document_number'),
                'notes': data.get('notes') or f"Importado de: {doc['file_name']}"
            }
            
            # Adiciona customer_id se houver nome do cliente
            if data.get('customer'):
                receivable_data['notes'] = f"Cliente: {data['customer']}\n" + (receivable_data.get('notes') or '')
            
            result = create_account_receivable(company_id, receivable_data)
            if result:
                st.success(f"✅ Conta a receber cadastrada com sucesso!")
            else:
                st.error("❌ Erro ao cadastrar conta a receber")
            
        elif table == 'tax_obligations':
            # Cadastra obrigação fiscal
            obligation_data = {
                'company_id': company_id,
                'obligation_type': data.get('obligation_type', 'Outros'),
                'due_date': data.get('due_date'),
                'amount': float(data.get('amount', 0)),
                'reference_period': data.get('reference_period'),
                'status': data.get('status', 'Pendente'),
                'notes': data.get('notes') or f"Importado de: {doc['file_name']}"
            }
            
            result = create_tax_obligation(obligation_data)
            if result:
                st.success(f"✅ Obrigação fiscal cadastrada com sucesso!")
            else:
                st.error("❌ Erro ao cadastrar obrigação fiscal")
        
        else:
            st.warning(f"⚠️ Tipo de tabela '{table}' não suportado para cadastro automático")
        
    except Exception as e:
        st.error(f"❌ Erro ao salvar no banco: {str(e)}")

# ==========================================
# DASHBOARD FISCAL
# ==========================================

def show_fiscal_dashboard():
    """Dashboard Fiscal com análise tributária completa"""
    
    # Header com seletor de datas
    show_module_header(
        title="Dashboard Fiscal",
        icon="📋",
        show_date_range=True,
        module="fiscal"
    )
    
    company = st.session_state.company
    if not company:
        st.warning("⚠️ Cadastre sua empresa primeiro")
        return
    
    # Pega datas do session_state (definidas pelo show_module_header)
    start_date, end_date = st.session_state.get('fiscal_date_range', (date.today().replace(day=1), date.today()))
    
    # ===== SEÇÃO 1: REGIME TRIBUTÁRIO E BARRA DE ATINGIMENTO =====
    st.markdown('<div class="section-header">🏛️ Regime Tributário</div>', unsafe_allow_html=True)
    
    current_regime = company.get('tax_regime', 'Simples Nacional')
    regime_limits = calculate_regime_limits()
    regime_limit = regime_limits.get(current_regime, 4800000)
    
    # Calcula faturamento dos últimos 12 meses
    revenue_12m = get_revenue_last_12_months(company['id'], end_date)
    regime_percentage = (revenue_12m / regime_limit * 100) if regime_limit != float('inf') else 0
    remaining_to_limit = max(0, regime_limit - revenue_12m)
    
    # Card de Regime
    col_regime1, col_regime2 = st.columns([2, 1])
    
    with col_regime1:
        # Determina cor baseado no percentual
        if regime_percentage >= 80:
            color = "#ef4444"  # Vermelho
            status_icon = "🔴"
            status_text = "ATENÇÃO: Próximo do limite!"
        elif regime_percentage >= 60:
            color = "#f59e0b"  # Amarelo
            status_icon = "🟡"
            status_text = "Atenção: Monitorar faturamento"
        else:
            color = "#10b981"  # Verde
            status_icon = "🟢"
            status_text = "Regime adequado"
        
        card_html = f"""<div style="padding: 1.5rem; background: var(--bg-card); border-radius: 12px; border-left: 4px solid {color}">
<div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 0.5rem">
{status_icon} Regime Atual: {current_regime}
</div>
<div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 1rem">
{status_text}
</div>
<div style="margin-bottom: 0.5rem">
<div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.25rem">
<span>Faturamento 12 meses</span>
<span style="font-weight: bold">{format_currency(revenue_12m)}</span>
</div>
<div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-secondary)">
<span>Limite do regime</span>
<span>{format_currency(regime_limit) if regime_limit != float('inf') else 'Sem limite'}</span>
</div>
</div>
<div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 28px; overflow: hidden; margin: 1rem 0; position: relative">
<div style="background: {color}; height: 100%; width: {min(regime_percentage, 100)}%; display: flex; align-items: center; justify-content: center; transition: width 0.3s ease"></div>
<div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.85rem; text-shadow: 0 1px 3px rgba(0,0,0,0.5)">
{format_currency(revenue_12m)} • {regime_percentage:.1f}% do limite
</div>
</div>
<div style="font-size: 0.85rem; color: var(--text-secondary)">
💰 Faltam <b>{format_currency(remaining_to_limit)}</b> para atingir o limite
</div>
</div>"""
        
        st.markdown(card_html, unsafe_allow_html=True)
    
    with col_regime2:
        st.metric(
            "📊 Faturamento 12m",
            format_currency(revenue_12m),
            f"{regime_percentage:.1f}% do limite"
        )
        st.metric(
            "⏰ Disponível",
            format_currency(remaining_to_limit)
        )
    
    # ALERTA se >= 80%
    if regime_percentage >= 80:
        st.warning(f"""
        ⚠️ **ALERTA CRÍTICO**: Você já atingiu **{regime_percentage:.1f}%** do limite do **{current_regime}**!
        
        🎯 **Ações Recomendadas**:
        - Consulte o **Agente Fiscal** abaixo para estratégias de elisão fiscal
        - Analise mudança de regime tributário
        - Planeje distribuição de lucros x pró-labore
        - Considere abertura de nova empresa (holding)
        
        💡 **Dica**: Pergunte ao agente "Como me manter no {current_regime}?" ou "Qual o melhor regime para mim?"
        """)
    
    # ===== SEÇÃO 2: OBRIGAÇÕES TRIBUTÁRIAS DO PERÍODO =====
    st.markdown("---")
    st.markdown('<div class="section-header">📅 Obrigações Fiscais</div>', unsafe_allow_html=True)
    
    obligations = get_pending_obligations(company['id'], start_date=start_date, end_date=end_date)
    
    # Define variáveis de obrigações (sempre, mesmo se lista vazia)
    urgent = [o for o in obligations if (datetime.strptime(o['due_date'], '%Y-%m-%d').date() - datetime.now().date()).days <= 5] if obligations else []
    warning = [o for o in obligations if 5 < (datetime.strptime(o['due_date'], '%Y-%m-%d').date() - datetime.now().date()).days <= 15] if obligations else []
    normal = [o for o in obligations if (datetime.strptime(o['due_date'], '%Y-%m-%d').date() - datetime.now().date()).days > 15] if obligations else []
    
    if obligations:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🔴 Urgente (≤5 dias)", len(urgent))
        with col2:
            st.metric("🟡 Atenção (6-15 dias)", len(warning))
        with col3:
            st.metric("🟢 Normal (>15 dias)", len(normal))
        
        # Cards de obrigações urgentes (mesmo formato do Contábil)
        if urgent:
            st.markdown("#### � Obrigações Urgentes")
            
            # Divide em 2 colunas
            col_urg1, col_urg2 = st.columns(2)
            
            for i, obl in enumerate(urgent):
                days_left = (datetime.strptime(obl['due_date'], '%Y-%m-%d').date() - datetime.now().date()).days
                
                # Alterna entre as colunas
                with col_urg1 if i % 2 == 0 else col_urg2:
                    st.markdown(f"""
                    <div style="padding: 0.5rem; background: var(--bg-card); border-radius: 4px; 
                         border-left: 3px solid #ef4444; margin-bottom: 0.25rem">
                        <div style="display: flex; justify-content: space-between; align-items: center">
                            <div>
                                <div style="font-weight: bold; font-size: 0.75rem">🔴 {obl['obligation_type']}</div>
                                <div style="font-size: 0.65rem; color: var(--text-secondary)">
                                    Vencimento: {datetime.strptime(obl['due_date'], '%Y-%m-%d').strftime('%d/%m/%Y')} • {days_left} dias
                                </div>
                            </div>
                            <div style="font-size: 0.85rem; font-weight: bold; color: var(--error)">
                                {format_currency(obl.get('amount', 0))}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="success-card">✅ Nenhuma obrigação pendente</div>', unsafe_allow_html=True)
    
    # ===== SEÇÃO 3: ANÁLISE TRIBUTÁRIA COMPLETA =====
    st.markdown("---")
    st.markdown('<div class="section-header">💳 Análise Tributária Comparativa</div>', unsafe_allow_html=True)
    
    # Calcula receita e despesas do período para análise
    period_revenue = 0
    period_expenses = 0
    
    current_date = start_date.replace(day=1)
    end_month = end_date.replace(day=1)
    
    while current_date <= end_month:
        month_str = current_date.strftime('%Y-%m-01')
        month_dre = get_or_create_dre(company['id'], month_str)
        period_revenue += month_dre.get('gross_revenue', 0)
        period_expenses += month_dre.get('expenses', 0) + month_dre.get('costs', 0)
        
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    # Calcula impostos em cada regime
    simples_tax = calculate_simples_tax(revenue_12m)
    presumido_tax = calculate_lucro_presumido_tax(revenue_12m)
    real_tax = calculate_lucro_real_tax(revenue_12m, period_expenses)
    
    # Exibe comparação
    col_tax1, col_tax2, col_tax3 = st.columns(3)
    
    with col_tax1:
        is_current = current_regime == 'Simples Nacional'
        border_color = "#6366f1" if is_current else "#334155"
        
        st.markdown(f"""
        <div style="padding: 1rem; background: var(--bg-card); border-radius: 12px; 
             border: 2px solid {border_color}; height: 100%">
            <div style="text-align: center">
                <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem">
                    Simples Nacional {'⭐' if is_current else ''}
                </div>
                <div style="font-size: 1.8rem; font-weight: bold; color: #10b981; margin-bottom: 0.5rem">
                    {format_currency(simples_tax['valor_anual'])}
                </div>
                <div style="font-size: 0.85rem; color: var(--text-secondary)">
                    Alíquota: {simples_tax['aliquota']*100:.2f}%
                </div>
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem">
                    Mensal: {format_currency(simples_tax['valor_mensal'])}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_tax2:
        is_current = current_regime == 'Lucro Presumido'
        border_color = "#6366f1" if is_current else "#334155"
        
        st.markdown(f"""
        <div style="padding: 1rem; background: var(--bg-card); border-radius: 12px; 
             border: 2px solid {border_color}; height: 100%">
            <div style="text-align: center">
                <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem">
                    Lucro Presumido {'⭐' if is_current else ''}
                </div>
                <div style="font-size: 1.8rem; font-weight: bold; color: #f59e0b; margin-bottom: 0.5rem">
                    {format_currency(presumido_tax['total'])}
                </div>
                <div style="font-size: 0.85rem; color: var(--text-secondary)">
                    Alíquota: {presumido_tax['aliquota']*100:.2f}%
                </div>
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem">
                    IRPJ+CSLL+PIS+COFINS+ISS
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_tax3:
        is_current = current_regime == 'Lucro Real'
        border_color = "#6366f1" if is_current else "#334155"
        
        st.markdown(f"""
        <div style="padding: 1rem; background: var(--bg-card); border-radius: 12px; 
             border: 2px solid {border_color}; height: 100%">
            <div style="text-align: center">
                <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem">
                    Lucro Real {'⭐' if is_current else ''}
                </div>
                <div style="font-size: 1.8rem; font-weight: bold; color: #ef4444; margin-bottom: 0.5rem">
                    {format_currency(real_tax['total'])}
                </div>
                <div style="font-size: 0.85rem; color: var(--text-secondary)">
                    Alíquota: {real_tax['aliquota']*100:.2f}%
                </div>
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem">
                    Lucro Real: {format_currency(real_tax['lucro_real'])}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Determina melhor regime
    regimes_comparison = [
        {'regime': 'Simples Nacional', 'valor': simples_tax['valor_anual']},
        {'regime': 'Lucro Presumido', 'valor': presumido_tax['total']},
        {'regime': 'Lucro Real', 'valor': real_tax['total']}
    ]
    
    best_regime = min(regimes_comparison, key=lambda x: x['valor'])
    current_tax = next(r['valor'] for r in regimes_comparison if r['regime'] == current_regime)
    savings = current_tax - best_regime['valor']
    
    if savings > 0 and best_regime['regime'] != current_regime:
        st.success(f"""
        💡 **Oportunidade de Economia**: O regime **{best_regime['regime']}** economizaria **{format_currency(savings)}** por ano 
        em comparação com o regime atual ({current_regime}).
        
        🎯 **Consulte o Agente Fiscal** abaixo para analisar viabilidade de mudança e estratégias de elisão fiscal!
        """)
    else:
        st.info(f"✅ Você está no regime tributário mais vantajoso (**{current_regime}**) para seu perfil de faturamento!")
    
    # ===== AGENTE FISCAL =====
    st.markdown("---")
    st.markdown('<div class="section-header">🤖 Agente Fiscal - Consultor em Regime Tributário e Legislação Fiscal</div>', unsafe_allow_html=True)
    
    if not st.session_state.ai_client:
        st.info("💡 Configure um modelo de IA na barra lateral para ativar o agente fiscal")
    else:
        # Resumo para o agente
        st.markdown(f"""
        <div style="padding: 1rem; background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; border-radius: 8px; margin-bottom: 1rem">
            <b>📊 Dados Fiscais do Período ({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}):</b><br>
            💰 <b>Receita Bruta (12 meses):</b> {format_currency(revenue_12m)}<br>
            🏛️ <b>Regime Atual:</b> {current_regime} ({regime_percentage:.1f}% do limite)<br>
            💳 <b>Imposto Estimado:</b> {format_currency(current_tax)} ({current_tax/revenue_12m*100:.2f}%)<br>
            📅 <b>Obrigações:</b> {len(obligations)} obrigações ({len(urgent)} urgentes)<br><br>
            <i style="font-size: 0.85rem; color: var(--text-secondary)">
            💡 Este agente é especialista em <b>legislação fiscal e tributária</b>. Para questões sobre <b>contabilidade</b>, consulte o Agente Contábil na seção 📊 Contabilidade.
            </i>
        </div>
        """, unsafe_allow_html=True)
        
        # Inicializa histórico de mensagens
        if 'fiscal_agent_messages' not in st.session_state:
            st.session_state.fiscal_agent_messages = []
        
        # Botão de reset
        col_reset1, col_reset2 = st.columns([5, 1])
        with col_reset2:
            if st.button("🔄 Limpar", key="reset_fiscal_chat", use_container_width=True):
                st.session_state.fiscal_agent_messages = []
                st.session_state.fiscal_agent_chat_history = None
                st.rerun()
        
        # Container de chat
        with st.container(height=300):
            for message in st.session_state.fiscal_agent_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Input de chat
        if prompt := st.chat_input("Pergunte sobre impostos, regime tributário, obrigações fiscais, elisão fiscal...", key="fiscal_agent_input"):
            # Adiciona mensagem do usuário
            st.session_state.fiscal_agent_messages.append({"role": "user", "content": prompt})
            
            # Prepara dados para o agente
            obligations_data = []
            for obl in obligations[:10]:  # Top 10 obrigações
                days_left = (datetime.strptime(obl['due_date'], '%Y-%m-%d').date() - datetime.now().date()).days
                obligations_data.append({
                    'type': obl['obligation_type'],
                    'due_date': datetime.strptime(obl['due_date'], '%Y-%m-%d').strftime('%d/%m/%Y'),
                    'days_left': days_left,
                    'amount': obl.get('amount', 0)
                })
            
            fiscal_stats = {
                'period_start': start_date.strftime('%d/%m/%Y'),
                'period_end': end_date.strftime('%d/%m/%Y'),
                'gross_revenue': period_revenue,
                'revenue_12m': revenue_12m,
                'current_regime': current_regime,
                'regime_limit': regime_limit,
                'regime_percentage': regime_percentage,
                'remaining_to_limit': remaining_to_limit,
                'total_obligations': len(obligations),
                'urgent_obligations': len(urgent),
                'warning_obligations': len(warning),
                'normal_obligations': len(normal),
                'obligations': obligations_data,
                'tax_analysis': {
                    'simples': simples_tax['valor_anual'],
                    'simples_rate': simples_tax['aliquota'] * 100,
                    'presumido': presumido_tax['total'],
                    'presumido_rate': presumido_tax['aliquota'] * 100,
                    'real': real_tax['total'],
                    'real_rate': real_tax['aliquota'] * 100,
                    'best_regime': best_regime['regime'],
                    'savings': savings
                }
            }
            
            # Cria prompt do agente fiscal
            system_prompt = create_fiscal_agent_prompt(
                company_data=company,
                fiscal_data=fiscal_stats
            )
            
            # Chama a IA
            with st.spinner("🤔 Analisando legislação fiscal e regime tributário..."):
                response, chat_history = chat_with_ai(
                    st.session_state.ai_client,
                    st.session_state.ai_model_type,
                    system_prompt,
                    prompt,
                    st.session_state.get('fiscal_agent_chat_history')
                )
                
                st.session_state.fiscal_agent_chat_history = chat_history
            
            # Adiciona resposta
            st.session_state.fiscal_agent_messages.append({"role": "assistant", "content": response})
            st.rerun()

# ==========================================
# DASHBOARD COM RANGE DE DATAS
# ==========================================

def show_dashboard(module: str = "accounting", unique_id: str = ""):
    # Header com logo usando o componente padrão
    show_module_header(
        title="Dashboard Contábil",
        icon="📊",
        show_date_range=True,
        module=module
    )
    
    if not st.session_state.company:
        st.warning("⚠️ Cadastre sua empresa primeiro!")
        return
    
    company = st.session_state.company
    start_date, end_date = st.session_state.accounting_date_range
    
    # Verifica se já temos os dados em cache para o dashboard específico
    accounting_cache = "accounting_dre_data"
    date_key = f"{start_date}_{end_date}"
    
    if accounting_cache not in st.session_state:
        st.session_state[accounting_cache] = {}
    
    # Se não tiver em cache ou as datas mudaram, recalcula
    if date_key not in st.session_state[accounting_cache]:
        with st.spinner("Carregando dados..."):
            total_revenue = 0
            total_expenses = 0
            total_profit = 0
            
            # Itera pelos meses do período
            current_date = start_date.replace(day=1)
            end_month = end_date.replace(day=1)
            
            while current_date <= end_month:
                month_str = current_date.strftime('%Y-%m-01')
                dre = get_or_create_dre(company['id'], month_str)
                
                total_revenue += dre.get('gross_revenue', 0)
                total_expenses += dre.get('expenses', 0)
                total_profit += dre.get('net_profit', 0)
                
                # Próximo mês
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            
            # Salva no cache
            st.session_state[accounting_cache][date_key] = {
                'total_revenue': total_revenue,
                'total_expenses': total_expenses,
                'total_profit': total_profit
            }
    
    # Usa os dados do cache
    data = st.session_state[accounting_cache][date_key]
    total_revenue = data['total_revenue']
    total_expenses = data['total_expenses']
    total_profit = data['total_profit']
    
    obligations = get_pending_obligations(company['id'], start_date=start_date, end_date=end_date)
    
    # Remove o input de datas duplicado pois já está no header
    start_date, end_date = st.session_state.accounting_date_range
    days_diff = (end_date - start_date).days
    
    # ===== SEÇÃO 1: CARDS DE MÉTRICAS =====
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Receita Bruta", format_currency(total_revenue))
    
    with col2:
        st.metric("📉 Despesas", format_currency(total_expenses))
    
    with col3:
        st.metric("✅ Lucro Líquido", format_currency(total_profit))
    
    with col4:
        st.metric("⏰ Obrigações Pendentes", len(obligations))
    
    st.markdown("---")
    
    # ===== SEÇÃO 2: GRÁFICOS =====
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">📊 Evolução das Despesas</div>', unsafe_allow_html=True)
        
        months = []
        expenses_data = []
        
        current_date = start_date.replace(day=1)
        end_month = end_date.replace(day=1)
        while current_date <= end_month:
            month_str = current_date.strftime('%Y-%m-01')
            month_label = current_date.strftime('%b/%y')
            
            month_dre = get_or_create_dre(company['id'], month_str)
            months.append(month_label)
            expenses_data.append(month_dre.get('expenses', 0))
            
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        fig_expenses = go.Figure()
        fig_expenses.add_trace(go.Bar(
            x=months,
            y=expenses_data,
            marker_color='#f59e0b',
            name='Despesas'
        ))
        
        fig_expenses.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#f1f5f9',
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        
        st.plotly_chart(fig_expenses, use_container_width=True, key=f"{module}_expenses_chart_{unique_id}")
    
    with col2:
        st.markdown('<div class="section-header">📈 Evolução dos Lucros</div>', unsafe_allow_html=True)
        
        profit_data = []
        
        current_date = start_date.replace(day=1)
        end_month = end_date.replace(day=1)
        while current_date <= end_month:
            month_str = current_date.strftime('%Y-%m-01')
            
            month_dre = get_or_create_dre(company['id'], month_str)
            profit_data.append(month_dre.get('net_profit', 0))
            
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        fig_profit = go.Figure()
        fig_profit.add_trace(go.Scatter(
            x=months,
            y=profit_data,
            mode='lines+markers',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8),
            name='Lucro'
        ))
        
        fig_profit.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#f1f5f9',
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        
        st.plotly_chart(fig_profit, use_container_width=True, key=f"{module}_profit_chart_{unique_id}")
    
    # ===== SEÇÃO 3: DRE DO PERÍODO =====
    st.markdown('<div class="section-header">💼 DRE do Período</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Soma de todos os meses do período
        period_dre = {
            'gross_revenue': total_revenue,
            'deductions': 0,
            'net_revenue': 0,
            'costs': 0,
            'gross_profit': 0,
            'expenses': total_expenses,
            'net_profit': total_profit
        }
        
        # Calcula valores agregados
        current_date = start_date.replace(day=1)
        end_month = end_date.replace(day=1)
        while current_date <= end_month:
            month_str = current_date.strftime('%Y-%m-01')
            month_dre = get_or_create_dre(company['id'], month_str)
            
            period_dre['deductions'] += month_dre.get('deductions', 0)
            period_dre['net_revenue'] += month_dre.get('net_revenue', 0)
            period_dre['costs'] += month_dre.get('costs', 0)
            period_dre['gross_profit'] += month_dre.get('gross_profit', 0)
            
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        dre_data = {
            'Item': ['Receita Bruta', '(-) Deduções', 'Receita Líquida', '(-) Custos', 
                    'Lucro Bruto', '(-) Despesas', 'Lucro Líquido'],
            'Valor': [
                period_dre['gross_revenue'],
                -period_dre['deductions'],
                period_dre['net_revenue'],
                -period_dre['costs'],
                period_dre['gross_profit'],
                -period_dre['expenses'],
                period_dre['net_profit']
            ]
        }
        
        df_dre = pd.DataFrame(dre_data)
        df_dre['Valor Formatado'] = df_dre['Valor'].apply(lambda x: format_currency(x))
        
        st.dataframe(df_dre[['Item', 'Valor Formatado']], hide_index=True, use_container_width=True, height=300, key=f"{module}_dre_table_{unique_id}")
    
    with col2:
        if period_dre['net_revenue'] > 0:
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Receita Líquida', 'Custos', 'Despesas'],
                values=[
                    period_dre['net_revenue'],
                    period_dre['costs'],
                    period_dre['expenses']
                ],
                hole=.4,
                marker=dict(colors=['#10b981', '#ef4444', '#f59e0b'])
            )])
            
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#f1f5f9',
                height=300,
                margin=dict(l=20, r=20, t=40, b=20),
                title="Composição"
            )
            
            st.plotly_chart(fig_pie, use_container_width=True, key=f"{module}_pie_chart_{unique_id}")
        else:
            st.info("📊 Aguardando dados do período")
    
    # ===== SEÇÃO 4: OBRIGAÇÕES =====
    st.markdown('<div class="section-header">📅 Obrigações Fiscais</div>', unsafe_allow_html=True)
    
    if obligations:
        col1, col2, col3 = st.columns(3)
        
        urgent = [o for o in obligations if (datetime.strptime(o['due_date'], '%Y-%m-%d').date() - datetime.now().date()).days <= 5]
        warning = [o for o in obligations if 5 < (datetime.strptime(o['due_date'], '%Y-%m-%d').date() - datetime.now().date()).days <= 15]
        normal = [o for o in obligations if (datetime.strptime(o['due_date'], '%Y-%m-%d').date() - datetime.now().date()).days > 15]
        
        with col1:
            st.metric("🔴 Urgente (≤5 dias)", len(urgent))
        with col2:
            st.metric("🟡 Atenção (6-15 dias)", len(warning))
        with col3:
            st.metric("🟢 Normal (>15 dias)", len(normal))
        
        if urgent:
            st.markdown("#### 🔴 Obrigações Urgentes")
            
            # Divide em 2 colunas
            col_urg1, col_urg2 = st.columns(2)
            
            for i, obl in enumerate(urgent):
                days_left = (datetime.strptime(obl['due_date'], '%Y-%m-%d').date() - datetime.now().date()).days
                
                # Alterna entre as colunas
                with col_urg1 if i % 2 == 0 else col_urg2:
                    st.markdown(f"""
                    <div style="padding: 0.5rem; background: var(--bg-card); border-radius: 4px; 
                         border-left: 3px solid #ef4444; margin-bottom: 0.25rem">
                        <div style="display: flex; justify-content: space-between; align-items: center">
                            <div>
                                <div style="font-weight: bold; font-size: 0.75rem">🔴 {obl['obligation_type']}</div>
                                <div style="font-size: 0.65rem; color: var(--text-secondary)">
                                    Vencimento: {datetime.strptime(obl['due_date'], '%Y-%m-%d').strftime('%d/%m/%Y')} • {days_left} dias
                                </div>
                            </div>
                            <div style="font-size: 0.85rem; font-weight: bold; color: var(--error)">
                                {format_currency(obl.get('amount', 0))}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="success-card">✅ Nenhuma obrigação pendente</div>', unsafe_allow_html=True)
    
    # ===== AGENTE CONTÁBIL ===== 
    st.markdown("---")
    st.markdown('<div class="section-header">🤖 Agente Contábil - Consultor Contábil</div>', unsafe_allow_html=True)
    
    if not st.session_state.ai_client:
        st.info("💡 Configure um modelo de IA na barra lateral para ativar o agente contábil")
    else:
        # MOSTRA RESUMO DOS DADOS DO PERÍODO ATUAL (para referência visual)
        st.markdown(f"""
        <div style="padding: 1rem; background: rgba(139, 92, 246, 0.1); border-left: 4px solid #8b5cf6; border-radius: 8px; margin-bottom: 1rem">
            <b>📊 Demonstrações Contábeis do Período ({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}):</b><br>
            💰 <b>Receita Bruta:</b> {format_currency(total_revenue)}<br>
            📉 <b>Despesas:</b> {format_currency(total_expenses)}<br>
            ✅ <b>Lucro Líquido:</b> {format_currency(total_profit)}<br><br>
            <i style="font-size: 0.85rem; color: var(--text-secondary)">
            💡 Este agente é especialista em <b>contabilidade</b>. Para questões sobre <b>impostos/tributos</b>, consulte o Agente Fiscal na seção 📋 Fiscal.
            </i>
        </div>
        """, unsafe_allow_html=True)
        
        # Inicializa histórico de mensagens específico do agente contábil
        if 'accounting_agent_messages' not in st.session_state:
            st.session_state.accounting_agent_messages = []
        
        # Botão de reset
        col_reset1, col_reset2 = st.columns([5, 1])
        with col_reset2:
            if st.button("🔄 Limpar", key="reset_accounting_chat", use_container_width=True):
                st.session_state.accounting_agent_messages = []
                st.session_state.accounting_agent_chat_history = None
                st.rerun()
        
        # Container com altura fixa e scroll (usando componente nativo do Streamlit)
        with st.container(height=300):
            for message in st.session_state.accounting_agent_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Input de chat
        if prompt := st.chat_input("Pergunte sobre contabilidade, demonstrações contábeis, lançamentos, conciliações, auditoria...", key="accounting_agent_input"):
            # Adiciona mensagem do usuário
            st.session_state.accounting_agent_messages.append({"role": "user", "content": prompt})
            
            # Calcula DRE do período completo para contexto
            period_dre = {
                'gross_revenue': total_revenue,
                'net_revenue': 0,
                'gross_profit': 0,
                'net_profit': total_profit,
                'expenses': total_expenses,
                'deductions': 0,
                'costs': 0
            }
            
            # Itera pelos meses do período para calcular valores agregados
            current_date = start_date.replace(day=1)
            end_month = end_date.replace(day=1)
            
            while current_date <= end_month:
                month_str = current_date.strftime('%Y-%m-01')
                month_dre = get_or_create_dre(company['id'], month_str)
                
                period_dre['deductions'] += month_dre.get('deductions', 0)
                period_dre['net_revenue'] += month_dre.get('net_revenue', 0)
                period_dre['costs'] += month_dre.get('costs', 0)
                period_dre['gross_profit'] += month_dre.get('gross_profit', 0)
                
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            
            # Busca obrigações fiscais do período
            all_obligations = get_pending_obligations(company['id'], start_date=start_date, end_date=end_date)
            
            # Monta dados contábeis completos
            accounting_stats = {
                'period_start': start_date.strftime('%d/%m/%Y'),
                'period_end': end_date.strftime('%d/%m/%Y'),
                'gross_revenue': period_dre['gross_revenue'],
                'deductions': period_dre['deductions'],
                'net_revenue': period_dre['net_revenue'],
                'costs': period_dre['costs'],
                'gross_profit': period_dre['gross_profit'],
                'expenses': period_dre['expenses'],
                'net_profit': period_dre['net_profit'],
                'total_obligations': len(all_obligations),
                'urgent_obligations': len([o for o in all_obligations if (datetime.strptime(o['due_date'], '%Y-%m-%d').date() - datetime.now().date()).days <= 5]),
            }
            
            # Cria prompt do agente contábil
            system_prompt = create_accounting_system_prompt(
                company_data=company,
                dre_data=accounting_stats,
                financial_data=None  # Agente contábil não precisa de dados financeiros detalhados
            )
            
            # Chama a IA
            with st.spinner("🤔 Analisando dados contábeis e legislação..."):
                response, chat_history = chat_with_ai(
                    st.session_state.ai_client,
                    st.session_state.ai_model_type,
                    system_prompt,
                    prompt,
                    st.session_state.get('accounting_agent_chat_history')
                )
                
                st.session_state.accounting_agent_chat_history = chat_history
            
            # Adiciona resposta ao histórico
            st.session_state.accounting_agent_messages.append({"role": "assistant", "content": response})
            st.rerun()

# ==========================================
# PÁGINA DO AGENTE AI
# ==========================================

def show_ai_agent_page():
    st.markdown('<h1 class="main-header">🤖 Agente AI - Expert Contábil</h1>', unsafe_allow_html=True)
    
    if not st.session_state.ai_client:
        st.markdown('<div class="warning-card">⚠️ <strong>Configure o modelo de IA</strong> na barra lateral para usar o agente contábil.</div>', unsafe_allow_html=True)
        return
    
    company = st.session_state.company
    start_date, end_date = st.session_state.date_range
    
    # Calcula DRE do período para contexto
    period_dre = {'gross_revenue': 0, 'net_revenue': 0, 'gross_profit': 0, 'net_profit': 0, 'expenses': 0}
    
    current_date = start_date.replace(day=1)
    end_month = end_date.replace(day=1)
    
    while current_date <= end_month:
        month_str = current_date.strftime('%Y-%m-01')
        month_dre = get_or_create_dre(company['id'], month_str)
        
        period_dre['gross_revenue'] += month_dre.get('gross_revenue', 0)
        period_dre['net_revenue'] += month_dre.get('net_revenue', 0)
        period_dre['gross_profit'] += month_dre.get('gross_profit', 0)
        period_dre['net_profit'] += month_dre.get('net_profit', 0)
        period_dre['expenses'] += month_dre.get('expenses', 0)
        
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    # Container fixo com scroll
    st.markdown('<div class="chat-fixed-container">', unsafe_allow_html=True)
    
    # Botão de reset no topo
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🔄 Resetar", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = None
            st.rerun()
    
    # Área de mensagens com scroll
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input de chat
    if prompt := st.chat_input("Faça sua pergunta sobre contabilidade, impostos, DRE..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        system_prompt = create_accounting_system_prompt(company, period_dre)
        
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analisando..."):
                response, chat_history = chat_with_ai(
                    st.session_state.ai_client,
                    st.session_state.ai_model_type,
                    system_prompt,
                    prompt,
                    st.session_state.chat_history
                )
                
                st.markdown(response)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                if chat_history:
                    st.session_state.chat_history = chat_history
        
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# NAVEGAÇÃO PRINCIPAL
# ==========================================

def main():
    if st.session_state.current_page == 'login':
        show_login_page()
    else:
        show_sidebar()
        
        # Interface de aprovação de documentos (aparece em todas as abas se houver documentos pendentes)
        show_document_approval_interface()
        
        # Navegação por módulos
        tab_fin, tab_cont, tab_fiscal, tab_admin = st.tabs([
            "💰 Financeiro",
            "📊 Contabilidade", 
            "📋 Fiscal",
            "⚙️ Administrativa"
        ])
        
        with tab_fin:
            show_financial_dashboard()
            
        with tab_cont:
            show_dashboard(unique_id="principal")
            
        with tab_fiscal:
            show_fiscal_dashboard()
        
        with tab_admin:
            subtab1, subtab2, subtab3, subtab4 = st.tabs([
                "🏢 Empresa",
                "👥 Funcionários",
                "🔑 Usuários",
                "💼 Folha de Pagamento"
            ])
            
            with subtab1:
                show_company_form_inline(unique_id="administrative")
            
            with subtab2:
                show_employee_management()
            
            with subtab3:
                show_user_management()
            
            with subtab4:
                st.info("Em desenvolvimento: Folha de pagamento")

if __name__ == "__main__":
    main()
