# app/loader.py
"""
Central loader module that coordinates all individual data loaders.
Exposes processar_cadastros as the main entry point for loading any type of cadastro data.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Callable
from sqlalchemy.orm import Session

# Import all specific loaders
from .loader_bairro import processar_cadastros as processar_bairros
from .loader_condominio import processar_cadastros as processar_condominios
from .loader_distrito import processar_cadastros as processar_distritos
from .loader_imovel import processar_cadastros as processar_imoveis
from .loader_logradouro import processar_cadastros as processar_logradouros
from .loader_pessoa import processar_cadastros as processar_pessoas
from .loader_loteamento import processar_cadastros as processar_loteamentos
from .loader_secao import processar_cadastros as processar_secoes
from .loader_plantaValor import processar_cadastros as processar_planta_valores
from .utils import fix_encoding_in_dict

# Set up logging
LOG = logging.getLogger(__name__)


def _determine_loader(data: Dict[str, Any], json_path: str | Path) -> Callable:
    """
    Determine which loader to use based on the content of the JSON file.
    
    Args:
        data: The parsed JSON data to analyze
        json_path: Path to the JSON file (needed for some loaders that process dependencies)
    """
    if not isinstance(data, dict) or "content" not in data:
        raise ValueError("Invalid JSON format: expected object with 'content' array")
    
    content = data["content"]
    if not content:
        return None
    
    # Get the first record to analyze its structure
    sample = content[0]
    
    # Check for distinctive fields to determine the type
    if "municipio" in sample and "zonaRural" in sample:
        return processar_bairros
    elif "tipoCondominio" in sample:
        return processar_condominios
    elif "tipoLogradouroDescricao" in sample and "tipoLogradouroAbreviatura" in sample:
        return processar_logradouros
    elif "matriculaImobiliaria" in sample and "nroDecretoAprovacao" in sample:
        return processar_loteamentos
    elif all(key in sample for key in ["id", "nome", "municipio"]) and "zonaRural" not in sample:
        return processar_distritos
    elif "inscricaoImobiliariaFormatada" in sample:
        return processar_imoveis
    elif "cpfCnpj" in sample or "tipoPessoa" in sample or "pessoaFisica" in sample:
        return processar_pessoas
    elif "nroSecao" in sample and "logradouro" in sample and "face" in sample:
        return processar_secoes
    elif any(key.startswith("planta") for key in sample.keys()):
        return processar_planta_valores
    
    raise ValueError("Could not determine appropriate loader for the given JSON structure")


def processar_cadastros(sess: Session, json_path: str) -> None:
    """
    Main entry point for loading cadastros from JSON file.
    This function determines the appropriate loader based on the JSON content
    and delegates to the correct specific loader.
    
    Args:
        sess: SQLAlchemy Session for database operations
        json_path: Path to the JSON file containing cadastro data
        
    Raises:
        ValueError: If the JSON file is invalid or if no appropriate loader is found
    """
    path = Path(json_path)
    
    try:
        LOG.info(f"Loading cadastros from {json_path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        
        # Fix encoding issues in the data
        data = fix_encoding_in_dict(data)
        
        loader = _determine_loader(data, json_path)
        if loader:
            LOG.info(f"Using loader: {loader.__module__}")
            loader(sess, json_path)
            LOG.info("Loading completed successfully")
        else:
            raise ValueError("No content found in JSON file")
            
    except json.JSONDecodeError as e:
        LOG.error(f"Invalid JSON file {json_path}: {str(e)}")
        raise ValueError(f"Invalid JSON file {json_path}: {str(e)}")
    except Exception as e:
        LOG.error(f"Error processing {json_path}: {str(e)}")
        raise ValueError(f"Error processing {json_path}: {str(e)}")
