import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, Dict, List, Any
from datetime import datetime, date
import json

# Carregar variáveis de ambiente (SUPABASE_URL e SUPABASE_KEY)
load_dotenv()

# --- Configuração do Cliente Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Variável global para o cliente Supabase
supabase: Optional[Client] = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Cliente Supabase inicializado e pronto.")
    except Exception as e:
        print(f"❌ ERRO CRÍTICO ao inicializar o cliente Supabase: {e}")
        print("Verifique se SUPABASE_URL e SUPABASE_KEY estão corretos no .env")
else:
    print("⚠️ AVISO: Chaves do Supabase (SUPABASE_URL ou SUPABASE_KEY) não encontradas no .env.")
    print("As funções de DB não funcionarão.")


# =======================================================
# 1. USUÁRIOS (public.users)
# =======================================================

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Busca um usuário pelo email."""
    if not supabase:
        print("⚠️ Supabase não inicializado")
        return None
    try:
        response = supabase.table("users").select("*").eq("email", email).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Erro ao buscar usuário: {e}")
        return None


def create_user(email: str, password_hash: str, full_name: str, plan: str = "Profissional") -> Optional[Dict[str, Any]]:
    """Cria um novo usuário na tabela 'users'."""
    if not supabase:
        print("⚠️ Supabase não inicializado")
        return None
    try:
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "full_name": full_name,
            "plan": plan
        }
        response = supabase.table("users").insert(user_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Erro ao criar usuário (possivelmente email já existe): {e}")
        return None


# =======================================================
# 2. EMPRESAS (public.companies)
# =======================================================

def get_company_by_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Busca a primeira empresa de um usuário."""
    if not supabase:
        print("⚠️ Supabase não inicializado")
        return None
    try:
        response = (
            supabase.table("companies")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=False)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Erro ao buscar empresa: {e}")
        return None


def get_companies_by_user(user_id: str) -> List[Dict[str, Any]]:
    """Busca todas as empresas de um usuário."""
    if not supabase:
        return []
    try:
        response = (
            supabase.table("companies")
            .select("*")
            .eq("user_id", user_id)
            .order("name", desc=False)
            .execute()
        )
        return response.data
    except Exception as e:
        print(f"❌ Erro ao buscar empresas: {e}")
        return []


def create_company(user_id: str, company_data: dict) -> Optional[Dict[str, Any]]:
    """Cria uma nova empresa."""
    if not supabase:
        print("⚠️ Supabase não inicializado")
        return None
    try:
        company_data['user_id'] = user_id
        response = supabase.table("companies").insert(company_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Erro ao criar empresa: {e}")
        return None


# =======================================================
# 2A. LOGO DA EMPRESA
# =======================================================

def upload_company_logo(company_id: str, file_data: bytes, file_name: str) -> Optional[str]:
    """
    Faz upload ou substituição do logo da empresa no bucket 'logos'.
    Retorna a URL pública do arquivo.
    """
    if not supabase:
        print("⚠️ Supabase não inicializado")
        return None

    try:
        # Garante que o nome do arquivo é único por empresa
        file_extension = file_name.split('.')[-1].lower() if '.' in file_name else 'png'
        
        # Determina o content-type correto
        content_type_map = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'svg': 'image/svg+xml'
        }
        content_type = content_type_map.get(file_extension, 'image/png')
        
        file_path = f"company_{company_id}/logo.{file_extension}"
        
        print(f"📤 Iniciando upload: {file_path}")
        print(f"📏 Tamanho do arquivo: {len(file_data)} bytes")
        print(f"📄 Content-Type: {content_type}")

        # Remove o arquivo anterior (se existir)
        try:
            supabase.storage.from_("logos").remove([file_path])
            print(f"🗑️ Logo anterior removido")
        except Exception as e:
            print(f"ℹ️ Nenhum logo anterior para remover: {e}")

        # Upload do novo logo
        try:
            # Upload do novo logo (sem upsert)
            response = supabase.storage.from_("logos").upload(
                path=file_path,
                file=file_data,
                file_options={"content-type": content_type}
            )
            print(f"✅ Logo uploaded: {response}")
        except Exception as e:
            print(f"❌ Erro ao fazer upload do logo: {e}")
            import traceback
            traceback.print_exc()
            return None

        # Gera URL pública
        public_url = supabase.storage.from_("logos").get_public_url(file_path)
        
        # Adiciona timestamp para forçar refresh do cache
        timestamp = int(datetime.now().timestamp())
        public_url_with_cache = f"{public_url}?t={timestamp}"
        
        print(f"✅ Logo da empresa {company_id} enviado")
        print(f"🌐 URL gerada: {public_url_with_cache}")
        
        return public_url_with_cache
        
    except Exception as e:
        print(f"❌ Erro ao fazer upload do logo: {e}")
        import traceback
        traceback.print_exc()
        return None


def update_company_logo(company_id: str, logo_url: str) -> bool:
    """Atualiza o campo logo_path da empresa."""
    if not supabase:
        print("⚠️ Supabase não inicializado")
        return False
    try:
        print(f"💾 Atualizando logo_path no banco para empresa {company_id}")
        print(f"🔗 URL: {logo_url}")
        
        response = (
            supabase.table("companies")
            .update({"logo_path": logo_url})
            .eq("id", company_id)
            .execute()
        )
        
        if response.data:
            print(f"✅ Logo path atualizado no banco de dados")
            print(f"📊 Dados retornados: {response.data[0].get('logo_path', 'N/A')}")
            return True
        else:
            print(f"⚠️ Nenhum dado retornado na atualização")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao atualizar logo_path da empresa: {e}")
        import traceback
        traceback.print_exc()
        return False


# =======================================================
# 3. CONTAS BANCÁRIAS (public.bank_accounts)
# =======================================================

def get_bank_accounts(company_id: str, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
    """
    Busca todas as contas bancárias ativas de uma empresa.
    Calcula o saldo dinamicamente baseado nas transações do período.
    
    Args:
        company_id: ID da empresa
        start_date: Data inicial para cálculo do saldo (formato YYYY-MM-DD)
        end_date: Data final para cálculo do saldo (formato YYYY-MM-DD)
    
    Returns:
        Lista de contas com saldo calculado dinamicamente
    """
    if not supabase:
        return []
    try:
        # Busca as contas bancárias
        response = (
            supabase.table("bank_accounts")
            .select("*")
            .eq("company_id", company_id)
            .eq("is_active", True)
            .order("bank_name", desc=False)
            .execute()
        )
        
        accounts = response.data if response.data else []
        
        # Calcula o saldo dinâmico para cada conta baseado nas transações
        for account in accounts:
            account_id = account['id']
            
            # Query base para transações
            transactions_query = (
                supabase.table("bank_transactions")
                .select("type, amount")
                .eq("bank_account_id", account_id)
            )
            
            # Aplica filtros de data se fornecidos
            if start_date:
                transactions_query = transactions_query.gte("transaction_date", start_date)
            if end_date:
                transactions_query = transactions_query.lte("transaction_date", end_date)
            
            transactions_response = transactions_query.execute()
            transactions = transactions_response.data if transactions_response.data else []
            
            # Calcula saldo: entradas (+) - saídas (-)
            balance = 0
            for transaction in transactions:
                amount = float(transaction.get('amount', 0))
                transaction_type = transaction.get('type', '').lower()
                
                # Aceita tanto português quanto inglês
                if transaction_type in ['entrada', 'credit', 'credito', 'crédito']:
                    balance += amount
                elif transaction_type in ['saida', 'debit', 'debito', 'débito', 'saída']:
                    balance -= amount
            
            # Atualiza o saldo calculado na conta
            account['balance'] = balance
            account['calculated_balance'] = True  # Flag para indicar que foi calculado
        
        return accounts
        
    except Exception as e:
        print(f"❌ Erro ao buscar contas bancárias: {e}")
        return []


def get_company_bank_accounts(company_id: str, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
    """
    Alias para get_bank_accounts (compatibilidade).
    Retorna contas com saldo calculado dinamicamente.
    """
    return get_bank_accounts(company_id, start_date, end_date)


# =======================================================
# 4. TRANSAÇÕES BANCÁRIAS (public.bank_transactions)
# =======================================================

def get_transactions_by_account(bank_account_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Busca transações de uma conta em um período."""
    if not supabase:
        return []
    try:
        response = (
            supabase.table("bank_transactions")
            .select("*")
            .eq("bank_account_id", bank_account_id)
            .gte("transaction_date", start_date)
            .lte("transaction_date", end_date)
            .order("transaction_date", desc=True)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Erro ao buscar transações: {e}")
        return []


def save_bank_transaction(transaction_data: dict) -> Optional[Dict[str, Any]]:
    """Salva uma transação bancária."""
    if not supabase:
        print("⚠️ Supabase não inicializado")
        return None
    try:
        response = supabase.table("bank_transactions").insert(transaction_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Erro ao salvar transação: {e}")
        return None


def insert_batch_transactions(transactions_list: List[Dict[str, Any]]):
    """Insere múltiplas transações de uma vez."""
    if not supabase:
        return
    try:
        supabase.table("bank_transactions").insert(transactions_list).execute()
        print(f"✅ Inseridas {len(transactions_list)} transações com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao inserir lote de transações: {e}")


# =======================================================
# 5. NOTAS FISCAIS (public.invoices)
# =======================================================

def get_invoices_by_company(company_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Busca notas fiscais de uma empresa, opcionalmente filtrando por status."""
    if not supabase:
        return []
    try:
        query = supabase.table("invoices").select("*").eq("company_id", company_id)
        
        if status:
            query = query.eq("status", status)
        
        response = query.order("issue_date", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Erro ao buscar notas fiscais: {e}")
        return []


def save_invoice(invoice_data: dict) -> Optional[Dict[str, Any]]:
    """Salva uma nota fiscal."""
    if not supabase:
        print("⚠️ Supabase não inicializado")
        return None
    try:
        response = supabase.table("invoices").insert(invoice_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Erro ao salvar nota fiscal: {e}")
        return None


# =======================================================
# 6. DRE (public.income_statement)
# =======================================================

def get_or_create_dre(company_id: str, reference_month: str) -> Dict[str, Any]:
    """
    Busca ou cria uma DRE (Demonstração do Resultado do Exercício) para o mês.
    reference_month deve estar no formato 'YYYY-MM-DD' (ex: '2025-01-01')
    Retorna sempre um dict, mesmo se Supabase não estiver configurado.
    """
    default_dre = {
        'company_id': company_id,
        'reference_month': reference_month,
        'gross_revenue': 0,
        'deductions': 0,
        'net_revenue': 0,
        'costs': 0,
        'gross_profit': 0,
        'expenses': 0,
        'net_profit': 0
    }
    
    if not supabase:
        print("⚠️ Supabase não inicializado - retornando DRE vazia")
        return default_dre
    
    try:
        # 1. Tenta buscar DRE existente
        response = (
            supabase.table('income_statement')
            .select('*')
            .eq('company_id', company_id)
            .eq('reference_month', reference_month)
            .execute()
        )
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        
        # 2. Se não existir, cria um novo registro com valores zerados
        response = supabase.table('income_statement').insert(default_dre).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        else:
            return default_dre
        
    except Exception as e:
        print(f"❌ Erro ao buscar/criar DRE: {e}")
        return default_dre


def fetch_or_create_income_statement(company_id: str, reference_month: str) -> Optional[Dict[str, Any]]:
    """Alias para get_or_create_dre (compatibilidade)."""
    return get_or_create_dre(company_id, reference_month)


# =======================================================
# 6. CONTAS A PAGAR E RECEBER
# =======================================================

def get_upcoming_bills(company_id: str, limit: int = 10, start_date: Optional[Any] = None, end_date: Optional[Any] = None, include_paid: bool = True) -> List[Dict[str, Any]]:
    """Retorna as próximas contas a pagar. Tenta usar novo schema (accounts_payable), 
    faz fallback para schema antigo (tax_obligations + invoices entrada) se necessário.
    """
    if not supabase:
        return []
    
    print(f"\n🔍 DEBUG get_upcoming_bills:")
    print(f"  company_id: {company_id}")
    print(f"  start_date: {start_date}")
    print(f"  end_date: {end_date}")
    print(f"  limit: {limit}")
    
    # TENTA USAR NOVO SCHEMA PRIMEIRO
    try:
        # Testa se a tabela accounts_payable existe
        test_query = supabase.table('accounts_payable').select('id').limit(1).execute()
        print(f"  ✅ Tabela accounts_payable existe - usando novo schema")
        
        # Se chegou aqui, a tabela existe - usa o novo schema
        # Busca TODAS as contas (sem filtro de status) e filtra depois
        accounts = get_accounts_payable(
            company_id=company_id,
            status=None,  # Busca todas
            start_date=start_date,
            end_date=end_date,
            limit=limit * 3  # Busca mais para compensar filtro
        )
        
        print(f"  📋 get_accounts_payable retornou {len(accounts)} contas")
        
        # Formata para o formato esperado pelo app.py
        result = []
        today = datetime.now().date()
        
        for acc in accounts:
            # LÊ payment_date apenas para filtro include_paid
            payment_date = acc.get('payment_date')
            is_paid = payment_date is not None
            
            # Se include_paid=False, pula APENAS contas efetivamente pagas
            if not include_paid and is_paid:
                continue
            
            # Converte due_date para objeto date
            due_date_obj = datetime.strptime(acc['due_date'], '%Y-%m-%d').date() if isinstance(acc['due_date'], str) else acc['due_date']
            
            # LÊ SITUACAO E STATUS DIRETAMENTE DO BANCO (já vem em português!)
            situacao_app = acc.get('situacao', 'A Pagar')  # 'Pago' ou 'A Pagar'
            status_app = acc.get('status', 'Pendente')     # 'Em Dia', 'Com Atraso', 'Pendente'
            
            # DEBUG: Log primeira conta
            if len(result) == 0:
                print(f"\n  🔍 PRIMEIRA CONTA PROCESSADA:")
                print(f"    Descrição: {acc['description']}")
                print(f"    Vencimento: {due_date_obj}")
                print(f"    Pago?: {is_paid} (payment_date: {payment_date})")
                print(f"    Hoje: {today}")
                print(f"    SITUAÇÃO: {situacao_app}")
                print(f"    STATUS: {status_app}")
                
            supplier_name = acc.get('third_parties', {}).get('name') if acc.get('third_parties') else 'Fornecedor'
            # Usa net_amount (valor líquido) se amount não existir
            amount_value = acc.get('amount') or acc.get('net_amount') or 0
            result.append({
                'id': acc['id'],
                'type': 'account_payable',
                'description': f"{acc['description']} - {supplier_name}",
                'amount': float(amount_value),
                'due_date': due_date_obj,
                'situacao': situacao_app,  # 'pago' ou 'a_pagar'
                'status': status_app,      # 'pendente', 'vencido', 'no_prazo'
                'payment_date': payment_date
            })
            
            # Limita ao número solicitado
            if len(result) >= limit:
                break
        
        # Ordena: ordem de prioridade solicitada
        # 1º: a_pagar vencido (CRÍTICO - não pago e atrasado)
        # 2º: pago vencido (pago com atraso)
        # 3º: pago no_prazo (pago em dia)
        # 4º: a_pagar pendente (ainda não venceu)
        def sort_priority(x):
            situacao = x['situacao']
            status = x['status']
            
            # Define prioridade combinada
            if situacao == 'A Pagar' and status == 'Com Atraso':
                return (0, x['due_date'])  # 1º: vencido não pago (CRÍTICO)
            elif situacao == 'Pago' and status == 'Com Atraso':
                return (1, x['due_date'])  # 2º: pago atrasado
            elif situacao == 'Pago' and status == 'Em Dia':
                return (2, x['due_date'])  # 3º: pago no prazo
            else:  # A Pagar e Pendente
                return (3, x['due_date'])  # 4º: pendente
        
        result.sort(key=sort_priority)
        
        print(f"  ✅ Retornando {len(result)} contas após ordenação")
        if result:
            print(f"    Primeira conta: {result[0]['description']} - Situação: {result[0]['situacao']} | Status: {result[0]['status']}")
        
        return result
        
    except Exception as new_schema_error:
        # Tabela não existe ou deu erro - usa schema antigo
        print(f"⚠️ Usando schema antigo para contas a pagar: {new_schema_error}")
    
    # FALLBACK: USA SCHEMA ANTIGO
    try:
        bills = []
        
        # 1. Obrigações fiscais (tax_obligations) - têm due_date e status
        tax_query = (supabase.table("tax_obligations")
                    .select("*")
                    .eq("company_id", company_id))
        if not include_paid:
            tax_query = tax_query.eq("status", "pending")
        
        # Aplica filtros de data
        if start_date and end_date:
            s = start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date)
            e = end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date)
            tax_query = tax_query.gte("due_date", s).lte("due_date", e)
        elif start_date:
            # Apenas start_date: busca a partir dessa data
            s = start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date)
            tax_query = tax_query.gte("due_date", s)
        else:
            # Sem filtro de data: próximos 30 dias
            from datetime import datetime as dtmod, timedelta
            today = dtmod.now().date()
            future = today + timedelta(days=30)
            tax_query = tax_query.gte("due_date", today.isoformat()).lte("due_date", future.isoformat())
            if not include_paid:
                tax_query = tax_query.eq("status", "pending")
        
        tax_obligations = tax_query.order("due_date").limit(limit).execute()
        
        # Processa obrigações fiscais
        for tax in tax_obligations.data:
            bills.append({
                'id': tax['id'],
                'type': 'tax',
                'description': f"{tax['obligation_type']}",
                'amount': float(tax.get('amount', 0)) if tax.get('amount') else 0,
                'due_date': datetime.strptime(tax['due_date'], '%Y-%m-%d').date() if isinstance(tax['due_date'], str) else tax['due_date'],
                'status': tax.get('status', 'pending')
            })
        
        # 2. Notas fiscais de entrada (invoices tipo 'entrada') - usamos issue_date como referência
        # Nota: invoices não têm due_date no schema, então usamos issue_date
        inv_query = (supabase.table("invoices")
                    .select("*")
                    .eq("company_id", company_id)
                    .eq("invoice_type", "entrada"))
        if not include_paid:
            inv_query = inv_query.eq("status", "pending")
        if start_date and end_date:
            s = start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date)
            e = end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date)
            inv_query = inv_query.gte("issue_date", s).lte("issue_date", e)
        else:
            from datetime import datetime as dtmod, timedelta
            today = dtmod.now().date()
            future = today + timedelta(days=30)
            inv_query = inv_query.gte("issue_date", today.isoformat()).lte("issue_date", future.isoformat())
        
        invoices = inv_query.order("issue_date").limit(limit).execute()
        
        # Processa invoices de entrada
        for inv in invoices.data:
            bills.append({
                'id': inv['id'],
                'type': 'invoice_entrada',
                'description': f"NF {inv.get('invoice_number', 'S/N')} - {inv.get('issuer_name', 'Fornecedor')}",
                'amount': float(inv.get('total_value', 0)) if inv.get('total_value') else 0,
                'due_date': datetime.strptime(inv['issue_date'], '%Y-%m-%d').date() if isinstance(inv.get('issue_date'), str) else inv.get('issue_date'),
                'status': inv.get('status', 'pending')
            })
        
        # Ordena por data de vencimento
        bills.sort(key=lambda x: x['due_date'] if x['due_date'] else date.max)
        
        return bills[:limit]
        
    except Exception as e:
        print(f"❌ Erro ao buscar contas a pagar: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_upcoming_receivables(company_id: str, limit: int = 10, start_date: Optional[Any] = None, end_date: Optional[Any] = None, include_paid: bool = True) -> List[Dict[str, Any]]:
    """Retorna os próximos recebimentos previstos. Tenta usar novo schema (accounts_receivable),
    faz fallback para schema antigo (invoices saída) se necessário.
    """
    if not supabase:
        return []
    
    # TENTA USAR NOVO SCHEMA PRIMEIRO
    try:
        # Testa se a tabela accounts_receivable existe
        test_query = supabase.table('accounts_receivable').select('id').limit(1).execute()
        
        # Se chegou aqui, a tabela existe - usa o novo schema
        # Busca TODAS as contas (sem filtro de status) e filtra depois
        accounts = get_accounts_receivable(
            company_id=company_id,
            status=None,  # Busca todas
            start_date=start_date,
            end_date=end_date,
            limit=limit * 3  # Busca mais para compensar filtro
        )
        
        # Formata para o formato esperado pelo app.py
        result = []
        today = datetime.now().date()
        
        for acc in accounts:
            # LÊ payment_date apenas para filtro include_paid
            payment_date = acc.get('payment_date')
            is_received = payment_date is not None
            
            # Se include_paid=False, pula APENAS contas efetivamente recebidas
            if not include_paid and is_received:
                continue
            
            # Converte due_date para objeto date
            due_date_obj = datetime.strptime(acc['due_date'], '%Y-%m-%d').date() if isinstance(acc['due_date'], str) else acc['due_date']
            
            # LÊ SITUACAO E STATUS DIRETAMENTE DO BANCO (já vem em português!)
            situacao_app = acc.get('situacao', 'A Receber')  # 'Recebido' ou 'A Receber'
            status_app = acc.get('status', 'Pendente')       # 'Em Dia', 'Com Atraso', 'Pendente'
                
            customer_name = acc.get('third_parties', {}).get('name') if acc.get('third_parties') else 'Cliente'
            # Usa net_amount (valor líquido) se amount não existir
            amount_value = acc.get('amount') or acc.get('net_amount') or 0
            result.append({
                'id': acc['id'],
                'description': f"{acc['description']} - {customer_name}",
                'amount': float(amount_value),
                'due_date': due_date_obj,
                'situacao': situacao_app,  # 'Recebido' ou 'A Receber'
                'status': status_app,      # 'Pendente', 'Com Atraso', 'Em Dia'
                'payment_date': payment_date,
                'client': customer_name
            })
            
            # Limita ao número solicitado
            if len(result) >= limit:
                break
        
        # Ordena: mesma ordem de prioridade das contas a pagar
        # 1º: a_receber vencido (CRÍTICO - não recebido e atrasado)
        # 2º: recebido vencido (recebido com atraso)
        # 3º: recebido no_prazo (recebido em dia)
        # 4º: a_receber pendente (ainda não venceu)
        def sort_priority(x):
            situacao = x['situacao']
            status = x['status']
            
            # Define prioridade combinada
            if situacao == 'A Receber' and status == 'Com Atraso':
                return (0, x['due_date'])  # 1º: vencido não recebido (CRÍTICO)
            elif situacao == 'Recebido' and status == 'Com Atraso':
                return (1, x['due_date'])  # 2º: recebido atrasado
            elif situacao == 'Recebido' and status == 'Em Dia':
                return (2, x['due_date'])  # 3º: recebido no prazo
            else:  # A Receber e Pendente
                return (3, x['due_date'])  # 4º: pendente
        
        result.sort(key=sort_priority)
                
        return result
        
    except Exception as new_schema_error:
        # Tabela não existe ou deu erro - usa schema antigo
        print(f"⚠️ Usando schema antigo para contas a receber: {new_schema_error}")
    
    # FALLBACK: USA SCHEMA ANTIGO
    try:
        # Busca invoices do tipo 'saida' (notas fiscais de saída = contas a receber)
        receivables_query = (supabase.table("invoices")
                            .select("*")
                            .eq("company_id", company_id)
                            .eq("invoice_type", "saida"))
        if not include_paid:
            receivables_query = receivables_query.eq("status", "pending")
        
        # Aplica filtros de data
        if start_date and end_date:
            s = start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date)
            e = end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date)
            receivables_query = receivables_query.gte("issue_date", s).lte("issue_date", e)
        elif start_date:
            # Apenas start_date: busca a partir dessa data
            s = start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date)
            receivables_query = receivables_query.gte("issue_date", s)
        else:
            # Sem filtro de data: próximos 30 dias
            from datetime import datetime as dtmod, timedelta
            today = dtmod.now().date()
            future = today + timedelta(days=30)
            receivables_query = receivables_query.gte("issue_date", today.isoformat()).lte("issue_date", future.isoformat())
        
        receivables = receivables_query.order("issue_date").limit(limit).execute()
        
        # Formata os resultados
        result = []
        for rec in receivables.data:
            result.append({
                'id': rec['id'],
                'description': f"NF {rec.get('invoice_number', 'S/N')} - {rec.get('recipient_name', 'Cliente')}",
                'amount': float(rec.get('total_value', 0)) if rec.get('total_value') else 0,
                'due_date': datetime.strptime(rec['issue_date'], '%Y-%m-%d').date() if isinstance(rec.get('issue_date'), str) else rec.get('issue_date'),
                'status': rec.get('status', 'pending'),
                'client': rec.get('recipient_name', 'Cliente não informado')
            })
        
        return result
        
    except Exception as e:
        print(f"❌ Erro ao buscar contas a receber: {e}")
        import traceback
        traceback.print_exc()
        return []

# =======================================================
# 7. OBRIGAÇÕES FISCAIS (public.tax_obligations)
# =======================================================

def get_pending_obligations(company_id: str, start_date: Optional[Any] = None, end_date: Optional[Any] = None) -> List[Dict[str, Any]]:
    """Busca obrigações fiscais pendentes. Por padrão, próximos 30 dias; se start_date/end_date forem fornecidos, usa o período informado."""
    if not supabase:
        return []
    
    try:
        from datetime import datetime as dtmod, timedelta
        if start_date and end_date:
            sdate = start_date if not hasattr(start_date, 'isoformat') else start_date
            edate = end_date if not hasattr(end_date, 'isoformat') else end_date
        else:
            today = dtmod.now().date()
            sdate = today
            edate = today + timedelta(days=30)
        
        response = (
            supabase.table('tax_obligations')
            .select('*')
            .eq('company_id', company_id)
            .eq('status', 'pending')
            .lte('due_date', edate.isoformat())
            .gte('due_date', sdate.isoformat())
            .order('due_date', desc=False)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Erro ao buscar obrigações: {e}")
        return []


def create_tax_obligation(obligation_data: dict) -> Optional[Dict[str, Any]]:
    """Cria uma nova obrigação fiscal."""
    if not supabase:
        print("⚠️ Supabase não inicializado")
        return None
    try:
        response = supabase.table("tax_obligations").insert(obligation_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Erro ao criar obrigação: {e}")
        return None


# =======================================================
# 8. FUNCIONÁRIOS (public.employees)
# =======================================================

def get_employees_by_company(company_id: str, is_active: bool = True) -> List[Dict[str, Any]]:
    """Busca funcionários de uma empresa."""
    if not supabase:
        return []
    try:
        response = (
            supabase.table("employees")
            .select("*")
            .eq("company_id", company_id)
            .eq("is_active", is_active)
            .order("full_name", desc=False)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Erro ao buscar funcionários: {e}")
        return []


def create_employee(employee_data: dict) -> Optional[Dict[str, Any]]:
    """Cria um novo funcionário."""
    if not supabase:
        print("⚠️ Supabase não inicializado")
        return None
    try:
        response = supabase.table("employees").insert(employee_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Erro ao criar funcionário: {e}")
        return None


# =======================================================
# 9. FOLHA DE PAGAMENTO (public.payroll)
# =======================================================

def get_payroll_by_month(company_id: str, reference_month: str) -> List[Dict[str, Any]]:
    """Busca folha de pagamento de um mês específico."""
    if not supabase:
        return []
    try:
        response = (
            supabase.table("payroll")
            .select("*")
            .eq("company_id", company_id)
            .eq("reference_month", reference_month)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Erro ao buscar folha de pagamento: {e}")
        return []


def create_payroll_entry(payroll_data: dict) -> Optional[Dict[str, Any]]:
    """Cria um registro de folha de pagamento."""
    if not supabase:
        print("⚠️ Supabase não inicializado")
        return None
    try:
        response = supabase.table("payroll").insert(payroll_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Erro ao criar folha: {e}")
        return None


# =======================================================
# 10. AUDITORIA (public.audit_log)
# =======================================================

def log_audit(user_id: str, company_id: str, action: str, entity_type: str, entity_id: str, old_values: dict, new_values: dict):
    """Registra ação na tabela 'audit_log'."""
    if not supabase:
        return
    try:
        audit_data = {
            'user_id': user_id,
            'company_id': company_id,
            'action': action,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'old_values': old_values,
            'new_values': new_values
        }
        supabase.table('audit_log').insert(audit_data).execute()
        print(f"✅ Auditoria registrada: {action} em {entity_type}")
    except Exception as e:
        print(f"❌ Erro ao registrar auditoria: {e}")


# =======================================================
# 11. UPLOADS DE ARQUIVOS (public.file_uploads)
# =======================================================

def create_file_upload(upload_data: dict) -> Optional[Dict[str, Any]]:
    """Registra um upload de arquivo."""
    if not supabase:
        print("⚠️ Supabase não inicializado")
        return None
    try:
        response = supabase.table("file_uploads").insert(upload_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Erro ao registrar upload: {e}")
        return None


def get_file_uploads_by_company(company_id: str) -> List[Dict[str, Any]]:
    """Busca uploads de uma empresa."""
    if not supabase:
        return []
    try:
        response = (
            supabase.table("file_uploads")
            .select("*")
            .eq("company_id", company_id)
            .order("upload_date", desc=True)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Erro ao buscar uploads: {e}")
        return []


# =======================================================
# 12. FUNÇÕES AUXILIARES
# =======================================================

def update_dre(company_id: str, reference_month: str, dre_data: dict) -> Optional[Dict[str, Any]]:
    """Atualiza valores da DRE."""
    if not supabase:
        print("⚠️ Supabase não inicializado")
        return None
    try:
        response = (
            supabase.table('income_statement')
            .update(dre_data)
            .eq('company_id', company_id)
            .eq('reference_month', reference_month)
            .execute()
        )
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Erro ao atualizar DRE: {e}")
        return None


def get_recent_transactions(bank_account_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Busca transações recentes de uma conta."""
    if not supabase:
        return []


# =======================================================
# 12A. SALDOS DE CONTAS BANCÁRIAS POR DATA
# =======================================================

def get_bank_account_balances_asof(company_id: str, as_of: Any) -> List[Dict[str, Any]]:
    """
    Retorna as contas bancárias com saldo recalculado até a data informada (inclusive).
    Calcula baseado no tipo de transação (entrada/saida) e saldo inicial.
    
    Args:
        company_id: ID da empresa
        as_of: Data limite para cálculo (pode ser date, datetime ou string)
    
    Returns:
        Lista de contas com balance_as_of calculado
    """
    if not supabase:
        # Sem DB, devolve contas como estão
        return get_bank_accounts(company_id)

    try:
        accounts = get_bank_accounts(company_id)
        if not accounts:
            return []

        # Normaliza data
        if hasattr(as_of, 'isoformat'):
            as_of_str = as_of.isoformat()
        elif isinstance(as_of, (datetime, date)):
            as_of_str = as_of.strftime('%Y-%m-%d')
        else:
            as_of_str = str(as_of)

        result = []
        for acc in accounts:
            acc_id = acc['id']
            # Busca transações até a data
            tx_response = (
                supabase.table('bank_transactions')
                .select('type, amount, transaction_date')
                .eq('bank_account_id', acc_id)
                .lte('transaction_date', as_of_str)
                .execute()
            )

            txs = tx_response.data if tx_response and tx_response.data else []
            
            # Calcula movimentações: entradas (+) e saídas (-)
            total_mov = 0.0
            for t in txs:
                try:
                    amount = float(t.get('amount', 0) or 0)
                    transaction_type = t.get('type', '').lower()
                    
                    # Aceita tanto português quanto inglês
                    if transaction_type in ['entrada', 'credit', 'credito', 'crédito']:
                        total_mov += amount
                    elif transaction_type in ['saida', 'debit', 'debito', 'débito', 'saída']:
                        total_mov -= amount
                except Exception:
                    pass

            # Saldo inicial (se existir)
            initial = 0.0
            if 'initial_balance' in acc and acc['initial_balance'] is not None:
                try:
                    initial = float(acc['initial_balance'])
                except Exception:
                    initial = 0.0

            # Saldo calculado = inicial + movimentações
            computed = initial + total_mov
            new_acc = dict(acc)
            new_acc['balance_as_of'] = computed
            new_acc['balance'] = computed  # Atualiza também o balance padrão
            result.append(new_acc)

        return result
    except Exception as e:
        print(f"❌ Erro ao calcular saldos por data: {e}")
        return get_bank_accounts(company_id)
    try:
        response = (
            supabase.table('bank_transactions')
            .select('*')
            .eq('bank_account_id', bank_account_id)
            .order('transaction_date', desc=True)
            .limit(limit)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Erro ao buscar transações recentes: {e}")
        return []


# =======================================================
# 13. TESTE DE CONEXÃO
# =======================================================

def test_connection():
    """Testa a conexão com o Supabase."""
    if not supabase:
        print("❌ Supabase não está inicializado. Verifique suas credenciais no .env")
        return False
    
    try:
        response = supabase.table('users').select('id').limit(1).execute()
        print("✅ Conexão com Supabase estabelecida com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {e}")
        return False


# =======================================================
# 14. TERCEIROS (CLIENTES/FORNECEDORES) - NOVO SCHEMA
# =======================================================

def create_third_party(company_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Cria um terceiro (cliente ou fornecedor)."""
    if not supabase:
        return None
    try:
        third_party_data = {
            'company_id': company_id,
            'type': data.get('type', 'cliente'),  # 'cliente', 'fornecedor', 'ambos'
            'name': data.get('name') or data.get('legal_name'),  # Compatibilidade
            'cpf_cnpj': data.get('cpf_cnpj') or data.get('tax_id'),  # Compatibilidade
            'legal_type': data.get('legal_type', 'pj'),  # 'pf' ou 'pj'
            'email': data.get('email'),
            'phone': data.get('phone'),
            'is_active': data.get('is_active', True)
        }
        response = supabase.table('third_parties').insert(third_party_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Erro ao criar terceiro: {e}")
        return None


def get_third_parties(company_id: str, party_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lista terceiros da empresa. Se party_type especificado, filtra por tipo."""
    if not supabase:
        return []
    try:
        query = supabase.table('third_parties').select('*').eq('company_id', company_id).eq('is_active', True)
        
        if party_type:
            # Filtra por tipo: 'cliente', 'fornecedor' ou 'ambos'
            query = query.or_(f"type.eq.{party_type},type.eq.ambos")
        
        response = query.order('name').execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Erro ao buscar terceiros: {e}")
        return []


# =======================================================
# 15. FUNÇÕES DE RECÁLCULO AUTOMÁTICO DE SITUAÇÃO/STATUS
# =======================================================

def recalculate_payable_status(company_id: str, payable_id: Optional[str] = None) -> bool:
    """
    Recalcula automaticamente a situação e status de contas a pagar baseado em:
    - payment_date (se foi pago ou não)
    - due_date (se está vencido ou pendente)
    - Data atual
    
    Args:
        company_id: ID da empresa
        payable_id: ID específico da conta (None = recalcula todas da empresa)
    
    Returns:
        True se sucesso, False se erro
    """
    if not supabase:
        return False
    
    try:
        from datetime import datetime, date
        today = datetime.now().date()
        
        # Busca as contas a recalcular
        query = supabase.table('accounts_payable').select('*').eq('company_id', company_id)
        
        if payable_id:
            query = query.eq('id', payable_id)
        
        response = query.execute()
        accounts = response.data if response.data else []
        
        print(f"\n🔄 Recalculando status de {len(accounts)} contas a pagar...")
        
        updated_count = 0
        for acc in accounts:
            payment_date = acc.get('payment_date')
            due_date_str = acc.get('due_date')
            
            if not due_date_str:
                continue
            
            # Converte due_date para objeto date
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if isinstance(due_date_str, str) else due_date_str
            
            # CALCULA SITUACAO (se foi pago ou não)
            is_paid = payment_date is not None
            situacao = 'Pago' if is_paid else 'A Pagar'
            
            # CALCULA STATUS (quando foi pago - timing)
            if is_paid:
                # Se foi pago, verifica se foi no prazo ou após vencimento
                payment_date_obj = datetime.strptime(payment_date, '%Y-%m-%d').date() if isinstance(payment_date, str) else payment_date
                if payment_date_obj <= due_date:
                    status = 'Em Dia'  # pago no prazo
                else:
                    status = 'Com Atraso'  # pago com atraso
            else:
                # Se não foi pago, verifica se está pendente ou com atraso
                if due_date >= today:
                    status = 'Pendente'  # não pago, ainda dentro do prazo
                else:
                    status = 'Com Atraso'  # não pago e já vencido
            
            # Atualiza AMBOS os campos no banco (situacao + status)
            supabase.table('accounts_payable').update({
                'situacao': situacao,   # 'Pago' ou 'A Pagar'
                'status': status        # 'Em Dia', 'Com Atraso', 'Pendente'
            }).eq('id', acc['id']).execute()
            
            updated_count += 1
        
        print(f"✅ {updated_count} contas a pagar atualizadas")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao recalcular status de contas a pagar: {e}")
        return False


def recalculate_receivable_status(company_id: str, receivable_id: Optional[str] = None) -> bool:
    """
    Recalcula automaticamente a situação e status de contas a receber baseado em:
    - payment_date (se foi recebido ou não)
    - due_date (se está vencido ou pendente)
    - Data atual
    
    Args:
        company_id: ID da empresa
        receivable_id: ID específico da conta (None = recalcula todas da empresa)
    
    Returns:
        True se sucesso, False se erro
    """
    if not supabase:
        return False
    
    try:
        from datetime import datetime, date
        today = datetime.now().date()
        
        # Busca as contas a recalcular
        query = supabase.table('accounts_receivable').select('*').eq('company_id', company_id)
        
        if receivable_id:
            query = query.eq('id', receivable_id)
        
        response = query.execute()
        accounts = response.data if response.data else []
        
        print(f"\n🔄 Recalculando status de {len(accounts)} contas a receber...")
        
        updated_count = 0
        for acc in accounts:
            payment_date = acc.get('payment_date')
            due_date_str = acc.get('due_date')
            
            if not due_date_str:
                continue
            
            # Converte due_date para objeto date
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if isinstance(due_date_str, str) else due_date_str
            
            # CALCULA SITUACAO (se foi recebido ou não)
            is_received = payment_date is not None
            situacao = 'Recebido' if is_received else 'A Receber'
            
            # CALCULA STATUS (quando foi recebido - timing)
            if is_received:
                # Se foi recebido, verifica se foi no prazo ou com atraso
                payment_date_obj = datetime.strptime(payment_date, '%Y-%m-%d').date() if isinstance(payment_date, str) else payment_date
                if payment_date_obj <= due_date:
                    status = 'Em Dia'  # recebido no prazo
                else:
                    status = 'Com Atraso'  # recebido com atraso
            else:
                # Se não foi recebido, verifica se está pendente ou com atraso
                if due_date >= today:
                    status = 'Pendente'  # não recebido, ainda dentro do prazo
                else:
                    status = 'Com Atraso'  # não recebido e já vencido
            
            # Atualiza AMBOS os campos no banco (situacao + status)
            supabase.table('accounts_receivable').update({
                'situacao': situacao,   # 'Recebido' ou 'A Receber'
                'status': status        # 'Em Dia', 'Com Atraso', 'Pendente'
            }).eq('id', acc['id']).execute()
            
            updated_count += 1
        
        print(f"✅ {updated_count} contas a receber atualizadas")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao recalcular status de contas a receber: {e}")
        return False


def recalculate_all_statuses(company_id: str) -> bool:
    """
    Recalcula TODAS as situações e status de contas a pagar e receber.
    Útil para manutenção ou após mudanças nas regras de negócio.
    
    Args:
        company_id: ID da empresa
    
    Returns:
        True se sucesso em ambas, False se erro em qualquer uma
    """
    print(f"\n{'='*60}")
    print(f"🔄 RECALCULANDO TODOS OS STATUS - Empresa: {company_id}")
    print(f"{'='*60}")
    
    payables_ok = recalculate_payable_status(company_id)
    receivables_ok = recalculate_receivable_status(company_id)
    
    if payables_ok and receivables_ok:
        print(f"\n✅ Recálculo completo finalizado com sucesso!")
        return True
    else:
        print(f"\n⚠️ Recálculo finalizado com erros")
        return False


# =======================================================
# 16. CONTAS A PAGAR - NOVO SCHEMA
# =======================================================

def create_account_payable(company_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Cria uma conta a pagar no novo schema e recalcula automaticamente seu status."""
    if not supabase:
        return None
    try:
        payable_data = {
            'company_id': company_id,
            'supplier_id': data.get('supplier_id'),
            'category_id': data.get('category_id'),
            'description': data['description'],
            'amount': data['amount'],
            'due_date': data['due_date'],
            'issue_date': data.get('issue_date', datetime.now().date().isoformat()),
            'competence_date': data.get('competence_date', data.get('due_date')),
            'status': data.get('status', 'pending'),  # pending, paid, overdue, cancelled
            'payment_method': data.get('payment_method'),
            'document_number': data.get('document_number'),
            'notes': data.get('notes'),
            'is_recurring': data.get('is_recurring', False),
            'recurrence_frequency': data.get('recurrence_frequency'),
            'recurrence_day': data.get('recurrence_day')
        }
        response = supabase.table('accounts_payable').insert(payable_data).execute()
        
        # Recalcula automaticamente o status da conta recém-criada
        if response.data:
            new_account = response.data[0]
            recalculate_payable_status(company_id, new_account['id'])
            # Busca novamente para retornar com status atualizado
            updated = supabase.table('accounts_payable').select('*').eq('id', new_account['id']).execute()
            return updated.data[0] if updated.data else new_account
        
        return None
    except Exception as e:
        print(f"❌ Erro ao criar conta a pagar: {e}")
        return None


def get_accounts_payable(
    company_id: str, 
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Lista contas a pagar com filtros opcionais.
    
    Args:
        company_id: ID da empresa
        status: 'pending', 'paid', 'overdue', 'cancelled' (None = todos)
        start_date: Data inicial do vencimento
        end_date: Data final do vencimento
        limit: Limite de registros
    """
    if not supabase:
        return []
    try:
        query = (
            supabase.table('accounts_payable')
            .select('*, third_parties(name, cpf_cnpj), financial_categories(name)')
            .eq('company_id', company_id)
        )
        
        if status:
            query = query.eq('status', status)
        
        if start_date:
            query = query.gte('due_date', start_date.isoformat())
        
        if end_date:
            query = query.lte('due_date', end_date.isoformat())
        
        response = query.order('due_date').limit(limit).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Erro ao buscar contas a pagar: {e}")
        return []


def update_account_payable_status(payable_id: str, status: str, payment_date: Optional[str] = None) -> bool:
    """Atualiza o status de uma conta a pagar e recalcula automaticamente baseado nas datas."""
    if not supabase:
        return False
    try:
        update_data = {'status': status}
        if payment_date:
            update_data['payment_date'] = payment_date
        
        supabase.table('accounts_payable').update(update_data).eq('id', payable_id).execute()
        
        # Recalcula automaticamente o status baseado nas datas atualizadas
        # Busca company_id para fazer a recalculação
        account = supabase.table('accounts_payable').select('company_id').eq('id', payable_id).execute()
        if account.data:
            recalculate_payable_status(account.data[0]['company_id'], payable_id)
        
        return True
    except Exception as e:
        print(f"❌ Erro ao atualizar conta a pagar: {e}")
        return False


# =======================================================
# 17. CONTAS A RECEBER - NOVO SCHEMA
# =======================================================

def create_account_receivable(company_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Cria uma conta a receber no novo schema e recalcula automaticamente seu status."""
    if not supabase:
        return None
    try:
        receivable_data = {
            'company_id': company_id,
            'customer_id': data.get('customer_id'),
            'invoice_id': data.get('invoice_id'),
            'category_id': data.get('category_id'),
            'description': data['description'],
            'amount': data['amount'],
            'due_date': data['due_date'],
            'issue_date': data.get('issue_date', datetime.now().date().isoformat()),
            'competence_date': data.get('competence_date', data.get('due_date')),
            'status': data.get('status', 'pending'),
            'payment_method': data.get('payment_method'),
            'document_number': data.get('document_number'),
            'notes': data.get('notes'),
            'is_recurring': data.get('is_recurring', False),
            'recurrence_frequency': data.get('recurrence_frequency'),
            'recurrence_day': data.get('recurrence_day')
        }
        response = supabase.table('accounts_receivable').insert(receivable_data).execute()
        
        # Recalcula automaticamente o status da conta recém-criada
        if response.data:
            new_account = response.data[0]
            recalculate_receivable_status(company_id, new_account['id'])
            # Busca novamente para retornar com status atualizado
            updated = supabase.table('accounts_receivable').select('*').eq('id', new_account['id']).execute()
            return updated.data[0] if updated.data else new_account
        
        return None
    except Exception as e:
        print(f"❌ Erro ao criar conta a receber: {e}")
        return None


def get_accounts_receivable(
    company_id: str,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Lista contas a receber com filtros opcionais."""
    if not supabase:
        return []
    try:
        query = (
            supabase.table('accounts_receivable')
            .select('*, third_parties(name, cpf_cnpj), financial_categories(name)')
            .eq('company_id', company_id)
        )
        
        if status:
            query = query.eq('status', status)
        
        if start_date:
            query = query.gte('due_date', start_date.isoformat())
        
        if end_date:
            query = query.lte('due_date', end_date.isoformat())
        
        response = query.order('due_date').limit(limit).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Erro ao buscar contas a receber: {e}")
        return []


def update_account_receivable_status(receivable_id: str, status: str, payment_date: Optional[str] = None) -> bool:
    """Atualiza o status de uma conta a receber e recalcula automaticamente baseado nas datas."""
    if not supabase:
        return False
    try:
        update_data = {'status': status}
        if payment_date:
            update_data['payment_date'] = payment_date
        
        supabase.table('accounts_receivable').update(update_data).eq('id', receivable_id).execute()
        
        # Recalcula automaticamente o status baseado nas datas atualizadas
        # Busca company_id para fazer a recalculação
        account = supabase.table('accounts_receivable').select('company_id').eq('id', receivable_id).execute()
        if account.data:
            recalculate_receivable_status(account.data[0]['company_id'], receivable_id)
        
        return True
    except Exception as e:
        print(f"❌ Erro ao atualizar conta a receber: {e}")
        return False


# =======================================================
# 17. CATEGORIAS FINANCEIRAS - NOVO SCHEMA
# =======================================================

def create_financial_category(company_id: str, name: str, category_type: str, parent_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Cria uma categoria financeira."""
    if not supabase:
        return None
    try:
        category_data = {
            'company_id': company_id,
            'name': name,
            'type': category_type,  # 'revenue', 'expense', 'cost'
            'parent_id': parent_id
        }
        response = supabase.table('financial_categories').insert(category_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Erro ao criar categoria: {e}")
        return None


def get_financial_categories(company_id: str, category_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lista categorias financeiras."""
    if not supabase:
        return []
    try:
        query = supabase.table('financial_categories').select('*').eq('company_id', company_id)
        
        if category_type:
            query = query.eq('type', category_type)
        
        response = query.order('name').execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Erro ao buscar categorias: {e}")
        return []


# =======================================================
# SISTEMA DE USUÁRIOS E NÍVEIS DE ACESSO
# =======================================================

def get_users_by_company(company_id: str) -> List[Dict[str, Any]]:
    """Busca todos os usuários de uma empresa."""
    if not supabase:
        return []
    try:
        response = (
            supabase.table("users")
            .select("*")
            .eq("company_id", company_id)
            .eq("is_active", True)
            .order("created_at", desc=False)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Erro ao buscar usuários da empresa: {e}")
        return []


def create_company_user(company_id: str, email: str, full_name: str, access_level: str, password_hash: str) -> Optional[Dict[str, Any]]:
    """
    Cria um novo usuário vinculado a uma empresa.
    access_level: 'geral' ou 'senior'
    """
    if not supabase:
        return None
    try:
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "full_name": full_name,
            "company_id": company_id,
            "access_level": access_level,
            "is_active": True,
            "plan": "Profissional"
        }
        
        response = supabase.table("users").insert(user_data).execute()
        return response.data[0] if response.data else None
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return None


def update_user_access_level(user_id: str, access_level: str) -> bool:
    """Atualiza o nível de acesso de um usuário."""
    if not supabase:
        return False
    try:
        response = (
            supabase.table("users")
            .update({"access_level": access_level})
            .eq("id", user_id)
            .execute()
        )
        return bool(response.data)
    except Exception as e:
        print(f"❌ Erro ao atualizar nível de acesso: {e}")
        return False


def deactivate_user(user_id: str) -> bool:
    """Desativa um usuário."""
    if not supabase:
        return False
    try:
        response = (
            supabase.table("users")
            .update({"is_active": False})
            .eq("id", user_id)
            .execute()
        )
        return bool(response.data)
    except Exception as e:
        print(f"❌ Erro ao desativar usuário: {e}")
        return False


def get_user_access_level(user_id: str, company_id: str) -> Optional[str]:
    """Retorna o nível de acesso de um usuário em uma empresa."""
    if not supabase:
        return None
    try:
        response = (
            supabase.table("users")
            .select("access_level")
            .eq("id", user_id)
            .eq("company_id", company_id)
            .eq("is_active", True)
            .execute()
        )
        return response.data[0]['access_level'] if response.data else None
    except Exception as e:
        print(f"❌ Erro ao buscar nível de acesso: {e}")
        return None


# =======================================================
# SISTEMA DE APROVAÇÕES
# =======================================================

def create_approval_request(request_data: dict) -> Optional[Dict[str, Any]]:
    """
    Cria uma solicitação de aprovação.
    request_data = {
        'company_id': str,
        'requester_user_id': str,
        'document_type': str,
        'document_file_name': str,
        'document_data': dict (JSON),
        'ai_analysis': dict (JSON),
        'ai_confidence': float,
        'status': 'pending',
        'priority': 'normal' | 'high' | 'urgent',
        'requester_notes': str (opcional)
    }
    """
    if not supabase:
        return None
    try:
        response = supabase.table("approval_requests").insert(request_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Erro ao criar solicitação de aprovação: {e}")
        return None


def get_pending_approvals(company_id: str) -> List[Dict[str, Any]]:
    """Busca todas as solicitações pendentes de aprovação de uma empresa."""
    if not supabase:
        return []
    try:
        response = (
            supabase.table("approval_requests")
            .select("*, users!approval_requests_requester_user_id_fkey(*)")
            .eq("company_id", company_id)
            .eq("status", "pending")
            .order("priority", desc=True)
            .order("created_at", desc=False)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Erro ao buscar aprovações pendentes: {e}")
        return []


def approve_request(approval_id: str, approver_user_id: str, notes: Optional[str] = None) -> bool:
    """Aprova uma solicitação."""
    if not supabase:
        return False
    try:
        update_data = {
            "status": "approved",
            "approver_user_id": approver_user_id,
            "approved_at": datetime.now().isoformat(),
            "approval_notes": notes
        }
        
        response = (
            supabase.table("approval_requests")
            .update(update_data)
            .eq("id", approval_id)
            .execute()
        )
        return bool(response.data)
    except Exception as e:
        print(f"❌ Erro ao aprovar solicitação: {e}")
        return False


def reject_request(approval_id: str, approver_user_id: str, reason: str) -> bool:
    """Rejeita uma solicitação."""
    if not supabase:
        return False
    try:
        update_data = {
            "status": "rejected",
            "approver_user_id": approver_user_id,
            "approved_at": datetime.now().isoformat(),
            "approval_notes": reason
        }
        
        response = (
            supabase.table("approval_requests")
            .update(update_data)
            .eq("id", approval_id)
            .execute()
        )
        return bool(response.data)
    except Exception as e:
        print(f"❌ Erro ao rejeitar solicitação: {e}")
        return False


def get_approval_by_id(approval_id: str) -> Optional[Dict[str, Any]]:
    """Busca uma aprovação específica com informações do solicitante."""
    if not supabase:
        return None
    try:
        response = (
            supabase.table("approval_requests")
            .select("*, users!approval_requests_requester_user_id_fkey(*)")
            .eq("id", approval_id)
            .execute()
        )
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Erro ao buscar aprovação: {e}")
        return None


# Executa teste de conexão ao importar o módulo
if __name__ == "__main__":
    print("🔍 Testando conexão com Supabase...")
    test_connection()