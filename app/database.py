# app/database.py
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker


@dataclass(frozen=True)
class Settings:
    host: str = os.getenv("PGHOST", "localhost")
    port: int = int(os.getenv("PGPORT", "5432"))
    user: str = os.getenv("PGUSER", "postgres")
    password: str = os.getenv("PGPASSWORD", "tributech")
    dbname: str = os.getenv("PGDATABASE", "auxiliar_assai")
    schema: str = os.getenv("PGSCHEMA", "imobiliario")

    @property
    def url(self) -> str:
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"


SETTINGS = Settings()


def make_engine(schema: Optional[str] = None) -> Engine:
    schema = schema or SETTINGS.schema

    engine: Engine = create_engine(
        SETTINGS.url,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )

    # ✅ forma correta de registrar o hook de conexão
    @event.listens_for(engine, "connect")
    def _set_search_path(dbapi_conn, connection_record):  # type: ignore[override]
        with dbapi_conn.cursor() as cur:
            cur.execute(f'SET search_path TO "{schema}", public')

    return engine


engine: Engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def check_schema(conn, schema: Optional[str] = None) -> None:
    """Verifica e ajusta o search path do banco de dados.
    
    Args:
        conn: Uma conexão SQLAlchemy (Engine, Connection, Session)
        schema: Schema para configurar no search_path
    """
    # Se é uma session, pegamos a conexão
    if hasattr(conn, 'connection'):
        conn = conn.connection()
    
    # Se é uma engine, abrimos uma conexão
    if hasattr(conn, 'connect'):
        conn = conn.connect()
    
    # Define o schema
    schema = schema or SETTINGS.schema
    
    # Mostra o search_path atual
    sp = conn.execute(text("SHOW search_path")).scalar_one()
    print(f"[database] search_path atual: {sp}")
    
    # Define o search_path se necessário
    if schema:
        conn.execute(text(f'SET search_path TO "{schema}", public'))
        conn.commit()