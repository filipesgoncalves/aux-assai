from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

import psycopg
from psycopg import sql
from dotenv import load_dotenv


# =========================
# Config via .env (com defaults)
# =========================
load_dotenv()

DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = int(os.getenv("PGPORT", "5432"))
DB_NAME = os.getenv("PGDATABASE", "auxiliar_assai")
DB_USER = os.getenv("PGUSER", "postgres")
DB_PASSWORD = os.getenv("PGPASSWORD", "postgres")
DB_SCHEMA = os.getenv("PGSCHEMA", "imobiliario")

ADMIN_DB = os.getenv("ADMIN_DB", "postgres")  # DB de manutenção p/ CREATE DATABASE

# Ajusta o caminho do SQL para ser relativo à raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent
SQL_SCHEMA_PATH = PROJECT_ROOT / os.getenv("SQL_SCHEMA_PATH", "sql/schema_auxiliar.sql")

# Novos JSONs a serem carregados (caminhos relativos à raiz do projeto)
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
    return (
        f"dbname={dbname} user={DB_USER} password={DB_PASSWORD} "
        f"host={DB_HOST} port={DB_PORT}"
    )


def ensure_database() -> None:
    """
    Conecta no banco de manutenção (ADMIN_DB) e cria a DB alvo caso não exista.
    Idempotente.
    """
    with psycopg.connect(_conn_str(ADMIN_DB), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
            if cur.fetchone():
                print(f"✅ Database '{DB_NAME}' já existe.")
                return
            print(f"📦 Criando database '{DB_NAME}'…")
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"✅ Database '{DB_NAME}' criada.")


def ensure_schema() -> None:
    """
    Garante que o schema alvo exista e define o search_path para a sessão.
    Idempotente.
    """
    with psycopg.connect(_conn_str(DB_NAME), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM information_schema.schemata WHERE schema_name = %s",
                (DB_SCHEMA,),
            )
            if not cur.fetchone():
                print(f"📁 Criando schema '{DB_SCHEMA}'…")
                cur.execute(
                    sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(DB_SCHEMA))
                )
                print(f"✅ Schema '{DB_SCHEMA}' criado.")
            else:
                print(f"✅ Schema '{DB_SCHEMA}' já existe.")
            # define search_path padrão para a sessão atual
            cur.execute(
                sql.SQL("SET search_path TO {}, public").format(
                    sql.Identifier(DB_SCHEMA)
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
    # IMPORTANTE: autocommit=True permite executar DDL múltiplos
    with psycopg.connect(_conn_str(DB_NAME), autocommit=True) as conn:
        with conn.cursor() as cur:
            # garante search_path antes de rodar o script
            cur.execute(
                sql.SQL("SET search_path TO {}, public").format(
                    sql.Identifier(DB_SCHEMA)
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
    
    # Mostra mais informações sobre o arquivo
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
        "bairros",      # Depende apenas de município que já deve existir
        "condominios",  # Independente
        "distritos",    # Depende apenas de município
        "logradouros",  # Depende apenas de município
        "loteamentos",  # Depende de bairro e município
        "secoes",       # Depende de logradouro e face
        "planta_valores", # Pode depender de vários
        "imoveis"       # Depende de vários (bairro, logradouro, etc)
    ]


def main() -> None:
    print(f"🔧 Host={DB_HOST}:{DB_PORT} | DB={DB_NAME} | Schema={DB_SCHEMA}")
    
    # 1. Garantir que a estrutura do banco existe
    ensure_database()
    ensure_schema()
    apply_schema(SQL_SCHEMA_PATH)
    
    # 2. Validar arquivos JSON antes de começar
    validate_json_files()
    
    # 3. O carregamento real dos dados será feito pelos loaders específicos
    print("\n⚠️  Database e schema prontos!")
    print("Use os loaders específicos para carregar os dados:")
    print("python -m app.main --json <arquivo.json>")


if __name__ == "__main__":
    main()