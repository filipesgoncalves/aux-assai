"""
Configurações centralizadas do projeto.
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class DatabaseConfig:
    host: str = os.getenv("PGHOST")
    port: int = int(os.getenv("PGPORT"))
    user: str = os.getenv("PGUSER")
    password: str = os.getenv("PGPASSWORD")
    dbname: str = os.getenv("PGDATABASE")
    schema: str = os.getenv("PGSCHEMA")

    @property
    def url(self) -> str:
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
    
    def conn_str(self, dbname: str = None) -> str:
        db = dbname or self.dbname
        return f"dbname={db} user={self.user} password={self.password} host={self.host} port={self.port}"

DB_CONFIG = DatabaseConfig()

DB_HOST = DB_CONFIG.host
DB_PORT = DB_CONFIG.port
DB_USER = DB_CONFIG.user
DB_PASSWORD = DB_CONFIG.password
DB_NAME = DB_CONFIG.dbname
DB_SCHEMA = DB_CONFIG.schema

def _conn_str(dbname: str) -> str:
    return DB_CONFIG.conn_str(dbname)
