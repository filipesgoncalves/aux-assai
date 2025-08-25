#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verificar se os imóveis foram carregados
"""

from app.database import SessionLocal
from app.models import Imovel

def check_imoveis():
    """Verificar se os imóveis foram carregados corretamente"""
    
    with SessionLocal() as sess:
        total_imoveis = sess.query(Imovel).count()
        print(f"Total de imóveis na base: {total_imoveis}")
        
        if total_imoveis > 0:
            print("\nPrimeiros 5 imóveis:")
            for i, imovel in enumerate(sess.query(Imovel).limit(5), 1):
                endereco = imovel.endereco_formatado[:80] + "..." if len(imovel.endereco_formatado) > 80 else imovel.endereco_formatado
                print(f"  {i}. ID: {imovel.id}, Código: {imovel.codigo}, Unidade: {imovel.unidade}")
                print(f"     Endereço: {endereco}")
                print(f"     Refs - Bairro: {imovel.bairro_id}, Distrito: {imovel.distrito_id}, Logradouro: {imovel.logradouro_id}")
                print()

if __name__ == "__main__":
    print("Verificando imóveis carregados...\n")
    check_imoveis()
