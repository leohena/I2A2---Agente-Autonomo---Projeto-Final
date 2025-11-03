"""
CONT-AI - Sistema de Gestão Contábil com IA
Launcher para executar a aplicação Streamlit
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Inicia a aplicação CONT-AI"""
    
    # Obtém o diretório do executável
    if getattr(sys, 'frozen', False):
        # Se estiver rodando como executável
        app_dir = Path(sys._MEIPASS)
    else:
        # Se estiver rodando como script Python
        app_dir = Path(__file__).parent
    
    # Caminho do arquivo app.py
    app_file = app_dir / "app.py"
    
    # Verifica se o arquivo existe
    if not app_file.exists():
        print(f"❌ Erro: Arquivo app.py não encontrado em {app_dir}")
        input("Pressione Enter para sair...")
        sys.exit(1)
    
    # Configura variáveis de ambiente
    os.chdir(app_dir)
    
    print("="*60)
    print("🚀 CONT-AI - Sistema de Gestão Contábil com IA")
    print("="*60)
    print("\n📦 Iniciando aplicação...")
    print("⏳ Aguarde, isso pode levar alguns segundos...\n")
    
    try:
        # Executa o Streamlit
        subprocess.run([
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            str(app_file),
            "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\n\n✋ Aplicação encerrada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar aplicação: {e}")
        input("\nPressione Enter para sair...")
        sys.exit(1)

if __name__ == "__main__":
    main()
