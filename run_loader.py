#!/usr/bin/env python3
"""
Script auxiliar para executar o carregamento de dados.
Execute este script da raiz do projeto para evitar problemas de import.

Uso:
    python run_loader.py --json data/bairros.json
    python run_loader.py --json data/pessoas.json
    
Ou execute diretamente:
    python -m app.main --json data/bairros.json
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Executa o app.main como módulo."""
    # Garantir que estamos na raiz do projeto
    project_root = Path(__file__).parent
    
    # Executar o módulo app.main com os argumentos passados
    args = ["python", "-m", "app.main"] + sys.argv[1:]
    
    try:
        subprocess.run(args, cwd=project_root, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar: {e}", file=sys.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError:
        # Tentar com 'py' se 'python' não funcionar
        args[0] = "py"
        try:
            subprocess.run(args, cwd=project_root, check=True)
        except Exception as e:
            print(f"Erro ao executar com 'py': {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
