#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verify UTF-8 encoding fixes across all tables
"""

from app.database import SessionLocal
from app.models import Pessoa, Bairro, Logradouro
from sqlalchemy import text

def check_all_tables():
    """Check encoding in all tables"""
    try:
        with SessionLocal() as session:
            print("=== PESSOAS ===")
            pessoas = session.query(Pessoa).filter(
                Pessoa.nome.contains('ã') | 
                Pessoa.nome.contains('é') |
                Pessoa.nome.contains('ó')
            ).limit(5).all()
            
            for pessoa in pessoas:
                print(f"  - {pessoa.nome}")
            
            print(f"Total pessoas: {session.query(Pessoa).count()}")
            
            print("\n=== BAIRROS ===")
            bairros = session.query(Bairro).filter(
                Bairro.nome.contains('ã') | 
                Bairro.nome.contains('é') |
                Bairro.nome.contains('ó')
            ).limit(5).all()
            
            for bairro in bairros:
                print(f"  - {bairro.nome}")
                
            print(f"Total bairros: {session.query(Bairro).count()}")
            
            print("\n=== LOGRADOUROS ===")
            logradouros = session.query(Logradouro).filter(
                Logradouro.nome.contains('ã') | 
                Logradouro.nome.contains('é') |
                Logradouro.nome.contains('ó')
            ).limit(5).all()
            
            for logradouro in logradouros:
                print(f"  - {logradouro.nome}")
                
            print(f"Total logradouros: {session.query(Logradouro).count()}")
        
        print("\n✅ UTF-8 encoding verification completed successfully!")
        
    except Exception as e:
        print(f"❌ Error checking encoding: {e}")

if __name__ == "__main__":
    print("Verifying UTF-8 encoding fixes across all tables...\n")
    check_all_tables()
