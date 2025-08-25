# app/__init__.py

# Import all loaders so they're available when the package is imported
from . import (
    loader_bairro,
    loader_condominio,
    loader_distrito,
    loader_imovel,
    loader_logradouro,
    loader_loteamento,
    loader_secao,
    loader_plantaValor
)

# Import and expose the main loader function
from .loader import processar_cadastros

__all__ = ['processar_cadastros']
