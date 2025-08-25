from sqlalchemy import create_engine, text

db_url = "postgresql://postgres:tributech@localhost/auxiliar_assai"
engine = create_engine(db_url)

with engine.connect() as conn:
    result = conn.execute(text("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'imobiliario' 
    AND table_name = 'municipio';
    """))
    for row in result:
        print(row)
