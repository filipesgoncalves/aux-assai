import psycopg
from psycopg import sql
from config import DB_CONFIG

def _conn_str(dbname: str) -> str:
    return DB_CONFIG.conn_str(dbname)

# Dropar tabelas e recriar sem referências FK para município
with psycopg.connect(_conn_str(DB_CONFIG.dbname), autocommit=True) as conn:
    with conn.cursor() as cur:
        # Configurar search_path
        cur.execute(sql.SQL("SET search_path TO {}, public").format(sql.Identifier(DB_CONFIG.schema)))
        
        # Dropar tabelas existentes
        try:
            cur.execute("DROP TABLE IF EXISTS bairro CASCADE")
            print("Tabela bairro removida")
        except Exception as e:
            print(f"Erro ao remover bairro: {e}")
            
        try:
            cur.execute("DROP TABLE IF EXISTS distrito CASCADE")
            print("Tabela distrito removida")
        except Exception as e:
            print(f"Erro ao remover distrito: {e}")
            
        try:
            cur.execute("DROP TABLE IF EXISTS municipio CASCADE")
            print("Tabela municipio removida")
        except Exception as e:
            print(f"Erro ao remover municipio: {e}")
        
        # Criar tabela bairro (sem FK para município)
        cur.execute("""
        CREATE TABLE bairro (
            id BIGINT PRIMARY KEY,
            codigo INTEGER,
            nome VARCHAR(100) NOT NULL,
            municipio_codigo_siafi INTEGER,
            zona_rural_descricao VARCHAR(3),
            UNIQUE(codigo, municipio_codigo_siafi)
        )
        """)
        print("Tabela bairro criada")
        
        # Criar tabela distrito (sem FK para município)
        cur.execute("""
        CREATE TABLE distrito (
            id BIGINT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            codigo INTEGER,
            municipio_codigo_siafi INTEGER,
            UNIQUE(codigo, municipio_codigo_siafi)
        )
        """)
        print("Tabela distrito criada")

print("✅ Tabelas recriadas sem dependência de município!")
