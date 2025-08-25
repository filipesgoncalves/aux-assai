#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify UTF-8 encoding fixes
"""

import psycopg2
from app.utils import fix_utf8_encoding

def test_encoding_in_database():
    """Check if encoding fixes worked in the database"""
    try:
        conn = psycopg2.connect('postgresql://postgres:postgres@localhost:5432/auxiliar_assai')
        cur = conn.cursor()
        
        # Check for names with Corn
        cur.execute("SELECT nome FROM imobiliario.pessoa WHERE nome ILIKE '%Corn%' LIMIT 5")
        results = cur.fetchall()
        
        print("Names containing 'Corn':")
        for row in results:
            print(f"  - {row[0]}")
        
        # Check for other accented characters
        cur.execute("SELECT nome FROM imobiliario.pessoa WHERE nome ~ '[ãáàâéêíóôõúç]' LIMIT 10")
        results = cur.fetchall()
        
        print("\nNames with accented characters:")
        for row in results:
            print(f"  - {row[0]}")
        
        conn.close()
        print("\nEncoding test completed successfully!")
        
    except Exception as e:
        print(f"Error testing encoding: {e}")

def test_encoding_function():
    """Test the encoding fix function directly"""
    test_cases = [
        "CornÃ©lio ProcÃ³pio",
        "SÃ£o Paulo", 
        "BrasÃ­lia",
        "ÃguÃ¡",
        "CoraÃ§Ã£o"
    ]
    
    print("Testing encoding function:")
    for test_case in test_cases:
        fixed = fix_utf8_encoding(test_case)
        print(f"  '{test_case}' -> '{fixed}'")

if __name__ == "__main__":
    print("Testing UTF-8 encoding corrections...\n")
    
    # Test the function
    test_encoding_function()
    
    print("\n" + "="*50 + "\n")
    
    # Test database content
    test_encoding_in_database()
