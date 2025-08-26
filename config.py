"""
Configurações centralizadas do projeto.
Este arquivo pode ser importado por scripts na raiz do projeto.
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class DatabaseConfig:
    """Configurações do banco de dados PostgreSQL."""
    host: str = os.getenv("PGHOST", "localhost")
    port: int = int(os.getenv("PGPORT", "5432"))
    user: str = os.getenv("PGUSER", "postgres")
    password: str = os.getenv("PGPASSWORD", "postgres")
    dbname: str = os.getenv("PGDATABASE", "auxiliar_assai")
    schema: str = os.getenv("PGSCHEMA", "imobiliario")

    @property
    def url(self) -> str:
        """URL de conexão SQLAlchemy."""
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
    
    def conn_str(self, dbname: str = None) -> str:
        """String de conexão psycopg."""
        db = dbname or self.dbname
        return f"dbname={db} user={self.user} password={self.password} host={self.host} port={self.port}"

# Instância global das configurações
DB_CONFIG = DatabaseConfig()

# Para compatibilidade com código antigo
DB_HOST = DB_CONFIG.host
DB_PORT = DB_CONFIG.port
DB_USER = DB_CONFIG.user
DB_PASSWORD = DB_CONFIG.password
DB_NAME = DB_CONFIG.dbname
DB_SCHEMA = DB_CONFIG.schema

def _conn_str(dbname: str) -> str:
    """Função helper para compatibilidade."""
    return DB_CONFIG.conn_str(dbname)
