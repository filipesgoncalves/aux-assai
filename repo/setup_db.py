from __future__ import annotations

import os
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

import psycopg
from psycopg import sql

# Adiciona o diretório pai ao path para importar config
sys.path.append(str(Path(__file__).parent.parent))
from config import DB_CONFIG

# =========================
# Configurações de arquivos
# =========================
ADMIN_DB = os.getenv("ADMIN_DB", "postgres") 

PROJECT_ROOT = Path(__file__).parent.parent
SQL_SCHEMA_PATH = PROJECT_ROOT / os.getenv("SQL_SCHEMA_PATH", "sql/schema_auxiliar.sql")

DATA_FILES = {
    "bairros": PROJECT_ROOT / "data/bairros.json",
    "condominios": PROJECT_ROOT / "data/condominios.json",
    "distritos": PROJECT_ROOT / "data/distritos.json",
    "imoveis": PROJECT_ROOT / "data/imoveis.json",
    "logradouros": PROJECT_ROOT / "data/logradouros.json",
    "loteamentos": PROJECT_ROOT / "data/loteamentos.json",
    "pessoas": PROJECT_ROOT / "data/pessoas.json",
    "secoes": PROJECT_ROOT / "data/secoes.json",
    "planta_valores": PROJECT_ROOT / "data/planta-valores.json"
}


def _conn_str(dbname: str) -> str:
    return DB_CONFIG.conn_str(dbname)


def ensure_database() -> None:
    """
    Conecta no banco de manutenção (ADMIN_DB) e cria a DB alvo caso não exista.
    Idempotente.
    """
    with psycopg.connect(_conn_str(ADMIN_DB), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG.dbname,))
            if cur.fetchone():
                print(f"✅ Database '{DB_CONFIG.dbname}' já existe.")
                return
            print(f"📦 Criando database '{DB_CONFIG.dbname}'…")
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_CONFIG.dbname)))
            print(f"✅ Database '{DB_CONFIG.dbname}' criada.")


def ensure_schema() -> None:
    """
    Garante que o schema alvo exista e define o search_path para a sessão.
    Idempotente.
    """
    with psycopg.connect(_conn_str(DB_CONFIG.dbname), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM information_schema.schemata WHERE schema_name = %s",
                (DB_CONFIG.schema,),
            )
            if not cur.fetchone():
                print(f"📁 Criando schema '{DB_CONFIG.schema}'…")
                cur.execute(
                    sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(DB_CONFIG.schema))
                )
                print(f"✅ Schema '{DB_CONFIG.schema}' criado.")
            else:
                print(f"✅ Schema '{DB_CONFIG.schema}' já existe.")
            # define search_path padrão para a sessão atual
            cur.execute(
                sql.SQL("SET search_path TO {}, public").format(
                    sql.Identifier(DB_CONFIG.schema)
                )
            )


def apply_schema(sql_path: Optional[Path] = None) -> None:
    """
    Aplica o arquivo SQL do schema (DDL). Executa no contexto da database alvo.
    """
    path = sql_path or SQL_SCHEMA_PATH
    if not path.exists():
        raise FileNotFoundError(f"Arquivo SQL não encontrado: {path}")

    sql_text = path.read_text(encoding="utf-8").strip()
    if not sql_text:
        print(f"⚠️  Arquivo vazio: {path}")
        return

    print(f"📑 Aplicando schema a partir de: {path}")
    with psycopg.connect(_conn_str(DB_CONFIG.dbname), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("SET search_path TO {}, public").format(
                    sql.Identifier(DB_CONFIG.schema)
                )
            )
            cur.execute(sql_text)
    print("✅ Schema aplicado com sucesso.")


def load_json_data(file_path: Path) -> Dict[str, Any]:
    """
    Carrega e valida o conteúdo de um arquivo JSON.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    
    data = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "content" not in data:
        raise ValueError(f"Formato JSON inválido em {file_path}: esperado objeto com array 'content'")
    
    size_kb = file_path.stat().st_size / 1024
    print(f"  📄 Tamanho: {size_kb:.1f}KB")
    
    return data


def validate_json_files() -> None:
    """
    Valida a existência e formato de todos os arquivos JSON necessários.
    """
    print("🔍 Validando arquivos JSON...")
    for name, path in DATA_FILES.items():
        try:
            data = load_json_data(path)
            records = len(data["content"])
            print(f"✅ {name}: {records} registros encontrados")
        except Exception as e:
            print(f"❌ {name}: {str(e)}")


def get_dependency_order() -> List[str]:
    """
    Retorna a ordem correta de carregamento dos dados baseado nas dependências.
    """
    return [
        "bairros",      
        "condominios",  
        "distritos",   
        "logradouros", 
        "loteamentos",  
        "secoes",       
        "planta_valores", 
        "imoveis"       
    ]


def main() -> None:
    print(f"🔧 Host={DB_CONFIG.host}:{DB_CONFIG.port} | DB={DB_CONFIG.dbname} | Schema={DB_CONFIG.schema}")
    
    # 1. Garantir que a estrutura do banco existe
    ensure_database()
    ensure_schema()
    apply_schema(SQL_SCHEMA_PATH)
    
    # 2. Validar arquivos JSON antes de começar
    validate_json_files()
    
    print("\n⚠️  Database e schema prontos!")
    print("Use os loaders específicos para carregar os dados:")
    print("python -m app.main --json <arquivo.json>")


if __name__ == "__main__":
    main()