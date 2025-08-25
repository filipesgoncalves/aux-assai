from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT id, codigo, nome, cpf_cnpj, tipo_pessoa_valor FROM imobiliario.pessoa LIMIT 5"))
    rows = result.fetchall()
    
    print("Pessoas cadastradas:")
    for r in rows:
        print(f"ID: {r[0]}, Código: {r[1]}, Nome: {r[2]}, CPF/CNPJ: {r[3]}, Tipo: {r[4]}")
    
    print("\nPessoas com dados de óbito:")
    result = conn.execute(text("SELECT nome, dt_obito, cpf_cnpj FROM imobiliario.pessoa WHERE dt_obito IS NOT NULL"))
    rows = result.fetchall()
    for r in rows:
        print(f"Nome: {r[0]}, Data Óbito: {r[1]}, CPF: {r[2]}")
    
    print("\nPessoas jurídicas:")
    result = conn.execute(text("SELECT nome, cpf_cnpj, nome_fantasia FROM imobiliario.pessoa WHERE tipo_pessoa_valor = 'JURIDICA'"))
    rows = result.fetchall()
    for r in rows:
        print(f"Nome: {r[0]}, CNPJ: {r[1]}, Nome Fantasia: {r[2]}")
    
    result = conn.execute(text("SELECT COUNT(*) FROM imobiliario.pessoa"))
    total = result.fetchone()[0]
    print(f"\nTotal de pessoas cadastradas: {total}")
