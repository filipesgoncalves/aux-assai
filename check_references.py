#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verificar incompatibilidade entre imóveis e logradouros
"""

import json
from app.database import SessionLocal
from app.models import Logradouro, Imovel

def check_reference_integrity():
    """Verifica integridade referencial entre imóveis e logradouros"""
    
    # Carregar IDs de logradouros que os imóveis referenciam
    with open('data/imoveis.json', 'r', encoding='utf-8') as f:
        imoveis_data = json.load(f)
    
    logradouro_ids_needed = set()
    for imovel in imoveis_data.get('content', []):
        if 'logradouro' in imovel and imovel['logradouro']:
            logradouro_ids_needed.add(imovel['logradouro']['id'])
    
    print(f"IDs de logradouros referenciados pelos imóveis: {len(logradouro_ids_needed)}")
    print(f"Primeiros 10: {list(logradouro_ids_needed)[:10]}")
    
    # Verificar logradouros na base
    with SessionLocal() as sess:
        logradouros_count = sess.query(Logradouro).count()
        print(f"Logradouros na base de dados: {logradouros_count}")
        
        if logradouros_count > 0:
            logradouros_ids_db = set([l.id for l in sess.query(Logradouro.id).all()])
            print(f"Primeiros 10 IDs na base: {list(logradouros_ids_db)[:10]}")
            
            # Verificar quantos IDs necessários estão faltando
            missing_ids = logradouro_ids_needed - logradouros_ids_db
            print(f"IDs de logradouros FALTANDO na base: {len(missing_ids)}")
            if missing_ids:
                print(f"Primeiros 10 faltando: {list(missing_ids)[:10]}")
                
            # Verificar quantos existem
            existing_ids = logradouro_ids_needed & logradouros_ids_db
            print(f"IDs de logradouros que EXISTEM na base: {len(existing_ids)}")
    
    print("\n" + "="*50)
    
    # Verificar dados do JSON de logradouros
    with open('data/logradouros.json', 'r', encoding='utf-8') as f:
        logradouros_data = json.load(f)
    
    logradouro_ids_json = set()
    for logradouro in logradouros_data.get('content', []):
        logradouro_ids_json.add(logradouro['id'])
    
    print(f"IDs de logradouros no JSON: {len(logradouro_ids_json)}")
    print(f"Primeiros 10: {list(logradouro_ids_json)[:10]}")
    
    # Verificar overlap
    overlap = logradouro_ids_needed & logradouro_ids_json
    missing_from_json = logradouro_ids_needed - logradouro_ids_json
    
    print(f"IDs que existem em ambos (imóveis e logradouros JSON): {len(overlap)}")
    print(f"IDs que faltam no JSON de logradouros: {len(missing_from_json)}")
    if missing_from_json:
        print(f"Primeiros 10 faltando no JSON: {list(missing_from_json)[:10]}")

if __name__ == "__main__":
    print("Verificando integridade referencial...\n")
    check_reference_integrity()
