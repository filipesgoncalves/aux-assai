import psycopg
from psycopg import sql

# Configurações do banco
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "auxiliar_assai"
DB_USER = "postgres"
DB_PASSWORD = "tributech"
DB_SCHEMA = "imobiliario"

def _conn_str(dbname: str) -> str:
    return f"dbname={dbname} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"

# Dropar tudo e recriar
with psycopg.connect(_conn_str("postgres"), autocommit=True) as conn:
    with conn.cursor() as cur:
        try:
            cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(DB_NAME)))
            print(f"Database {DB_NAME} removida")
        except Exception as e:
            print(f"Erro ao remover database: {e}")
        
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        print(f"Database {DB_NAME} criada")

# Criar schema e tabelas
with psycopg.connect(_conn_str(DB_NAME), autocommit=True) as conn:
    with conn.cursor() as cur:
        # Criar schema
        cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(DB_SCHEMA)))
        print(f"Schema {DB_SCHEMA} criado")
        
        # Configurar search_path
        cur.execute(sql.SQL("SET search_path TO {}, public").format(sql.Identifier(DB_SCHEMA)))
        
        # Criar tabela município
        cur.execute("""
        CREATE TABLE municipio (
            id BIGINT,
            codigo_siafi INTEGER PRIMARY KEY,
            codigo_ibge INTEGER,
            nome VARCHAR(100) NOT NULL,
            estado_id INTEGER,
            estado_nome VARCHAR(100),
            estado_uf VARCHAR(2),
            estado_codigo_ibge INTEGER
        )
        """)
        print("Tabela municipio criada")
        
        # Criar tabela bairro
        cur.execute("""
        CREATE TABLE bairro (
            id BIGINT PRIMARY KEY,
            codigo INTEGER,
            nome VARCHAR(100) NOT NULL,
            municipio_codigo_siafi INTEGER REFERENCES municipio(codigo_siafi),
            zona_rural_descricao VARCHAR(3),
            UNIQUE(codigo, municipio_codigo_siafi)
        )
        """)
        print("Tabela bairro criada")
        
        # Criar tabela distrito
        cur.execute("""
        CREATE TABLE distrito (
            id BIGINT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            codigo INTEGER,
            municipio_codigo_siafi INTEGER REFERENCES municipio(codigo_siafi),
            UNIQUE(codigo, municipio_codigo_siafi)
        )
        """)
        print("Tabela distrito criada")

print("✅ Database recriada com sucesso!")
