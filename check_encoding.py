#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple script to verify UTF-8 encoding fixes in database
"""

from app.database import SessionLocal
from app.models import Pessoa
from sqlalchemy import text

def test_encoding_in_db():
    """Check if encoding fixes worked in the database"""
    try:
        with SessionLocal() as session:
            # Search for any names that might have encoding issues
            query = text("""
                SELECT nome 
                FROM imobiliario.pessoa 
                WHERE nome LIKE '%Ã%' OR nome LIKE '%ã%' OR nome LIKE '%é%' OR nome LIKE '%ó%'
                LIMIT 10
            """)
            
            results = session.execute(query).fetchall()
            
            print("Names with potentially accented characters:")
            for row in results:
                print(f"  - {row[0]}")
            
            # Also check using ORM
            pessoas = session.query(Pessoa).filter(
                Pessoa.nome.contains('ã')
            ).limit(5).all()
            
            print("\nNames with 'ã' using ORM:")
            for pessoa in pessoas:
                print(f"  - {pessoa.nome}")
                
            print(f"\nTotal pessoas in database: {session.query(Pessoa).count()}")
        
        print("\nEncoding verification completed!")
        
    except Exception as e:
        print(f"Error checking encoding: {e}")

if __name__ == "__main__":
    print("Verifying UTF-8 encoding fixes in database...\n")
    test_encoding_in_db()
