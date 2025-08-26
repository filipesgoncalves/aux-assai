from sqlalchemy import create_engine, text
from config import DB_CONFIG

engine = create_engine(DB_CONFIG.url)

with engine.connect() as conn:
    result = conn.execute(text(f"""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = '{DB_CONFIG.schema}' 
    AND table_name = 'municipio';
    """))
    for row in result:
        print(row)
