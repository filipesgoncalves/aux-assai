#!/usr/bin/env python3
"""
Script para atualizar todos os loaders com tratamento de erros aprimorado.
"""

import os
from pathlib import Path

LOADER_TEMPLATE = '''# app/loader_{entity_lower}.py
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from .database import SessionLocal, engine, SETTINGS, check_schema
from .models import Base, {models}

def _int_or_none(value) -> int | None:
    """Convert a value to integer or None if not possible."""
    if value in (None, "", "null"):
        return None
    try:
        return int(value)
    except Exception:
        return None


def _process_record(raw: Dict[str, Any]) -> Dict[str, Any] | None:
    """Process a single {entity} record from the JSON."""
    if not raw:
        return None

    try:
{process_record_body}
    except Exception as e:
        print(f"Error processing {entity} record: {{str(e)}}")
        print(f"Raw data: {{raw}}")
        return None


def _upsert_{entity_lower}(sess: Session, data: Dict[str, Any]) -> None:
    """Insert or update a {entity} record."""
    if not data:
        return

    try:
        stmt = insert({entity}).values(**data)
        stmt = stmt.on_conflict_do_update(
            index_elements=[{entity}.id],
            set_=data
        )
        sess.execute(stmt)
    except Exception as e:
        print(f"Error upserting {entity_lower}: {{str(e)}}")
        print(f"{entity} data: {{data}}")
        raise


def load_from_iterable(
    records: Iterable[Dict[str, Any]], chunk_size: int = 500
) -> Tuple[int, int]:
    """Load records in batches. Returns (successes, skipped)."""
    ok = skipped = 0

    try:
        # Sanity check for schema
        check_schema(engine, SETTINGS.schema)
    except Exception as e:
        print(f"Error checking schema: {{str(e)}}")
        raise

    buffer: List[Dict[str, Any]] = []

    def _flush(chunk: List[Dict[str, Any]]) -> int:
        success_count = 0
        with SessionLocal() as sess:
            for record in chunk:
                try:
                    # Process and insert record
                    processed_data = _process_record(record)
                    if processed_data:
                        _upsert_{entity_lower}(sess, processed_data)
                        success_count += 1
                except Exception as e:
                    print(f"Error processing record in chunk: {{str(e)}}")
                    continue

            try:
                sess.commit()
                return success_count
            except Exception as e:
                sess.rollback()
                print(f"Error committing chunk: {{str(e)}}")
                return 0

    for rec in records:
        try:
            processed_rec = _process_record(rec)
            if processed_rec:
                buffer.append(rec)
                if len(buffer) >= chunk_size:
                    ok += _flush(buffer)
                    buffer = []
            else:
                skipped += 1
        except Exception as e:
            print(f"Error processing record: {{str(e)}}")
            skipped += 1

    if buffer:
        ok += _flush(buffer)

    return ok, skipped


def processar_cadastros(sess: Session, json_path: str) -> None:
    """
    Main entry point for loading {entity_plural} from JSON file.
    Compatible with the interface expected by main.py.
    """
    path = Path(json_path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        
        if isinstance(data, dict) and "content" in data:
            records = data["content"]
            ok, skipped = load_from_iterable(records)
            print(f"Processed {{ok}} records successfully, skipped {{skipped}} records")
        else:
            raise ValueError("Invalid JSON format: expected object with 'content' array")
    except Exception as e:
        raise ValueError(f"Error processing {{json_path}}: {{str(e)}}")
'''

# Definições dos loaders
LOADER_CONFIGS = {
    "bairro": {
        "models": "Municipio, Bairro",
        "entity": "Bairro",
        "process_record_body": '''        municipio_data = raw.get("municipio") or {}
        zona_rural = raw.get("zonaRural") or {}

        return {
            "id": raw.get("id"),
            "codigo": _int_or_none(raw.get("codigo")),
            "nome": raw.get("nome"),
            "municipio_codigo_siafi": municipio_data.get("codigoSIAFI"),
            "zona_rural_descricao": zona_rural.get("descricao")
        }'''
    },
    "condominio": {
        "models": "Condominio",
        "entity": "Condominio",
        "process_record_body": '''        tipo_condominio = raw.get("tipoCondominio") or {}

        return {
            "id": raw.get("id"),
            "codigo": _int_or_none(raw.get("codigo")),
            "nome": raw.get("nome"),
            "tipo_condominio_valor": tipo_condominio.get("valor"),
            "tipo_condominio_descricao": tipo_condominio.get("descricao")
        }'''
    },
    "distrito": {
        "models": "Municipio, Distrito",
        "entity": "Distrito",
        "process_record_body": '''        municipio_data = raw.get("municipio") or {}

        return {
            "id": raw.get("id"),
            "codigo": _int_or_none(raw.get("codigo")),
            "nome": raw.get("nome"),
            "municipio_codigo_siafi": municipio_data.get("codigoSIAFI")
        }'''
    },
    "logradouro": {
        "models": "Municipio, Logradouro",
        "entity": "Logradouro",
        "process_record_body": '''        municipio_data = raw.get("municipio") or {}

        return {
            "id": raw.get("id"),
            "codigo": _int_or_none(raw.get("codigo")),
            "nome": raw.get("nome"),
            "tipo_logradouro_descricao": raw.get("tipoLogradouroDescricao"),
            "tipo_logradouro_abreviatura": raw.get("tipoLogradouroAbreviatura"),
            "cep": raw.get("cep"),
            "extensao": _float_or_none(raw.get("extensao")),
            "lei": raw.get("lei"),
            "zona_fiscal": raw.get("zonaFiscal"),
            "municipio_codigo_siafi": municipio_data.get("codigoSIAFI"),
            "denominacao_anterior": raw.get("denominacaoAnterior"),
            "latitude": _float_or_none(raw.get("latitude")),
            "longitude": _float_or_none(raw.get("longitude"))
        }'''
    },
    "loteamento": {
        "models": "Municipio, Loteamento",
        "entity": "Loteamento",
        "process_record_body": '''        municipio_data = raw.get("municipio") or {}
        responsavel = raw.get("responsavel") or {}

        return {
            "id": raw.get("id"),
            "codigo": _int_or_none(raw.get("codigo")),
            "nome": raw.get("nome"),
            "responsavel_nome": responsavel.get("nome"),
            "municipio_codigo_siafi": municipio_data.get("codigoSIAFI")
        }'''
    },
    "plantaValor": {
        "models": "PlantaValor",
        "entity": "PlantaValor",
        "process_record_body": '''        return {
            "id": raw.get("id"),
            "valor": _float_or_none(raw.get("valor")),
            "data_referencia": raw.get("dataReferencia")
        }'''
    },
    "imovel": {
        "models": "Base, Municipio, Bairro, Condominio, Distrito, Logradouro, Loteamento, Imovel",
        "entity": "Imovel",
        "process_record_body": '''        bairro = raw.get("bairro") or {}
        distrito = raw.get("distrito") or {}
        logradouro = raw.get("logradouro") or {}
        tipo_imovel = raw.get("tipoImovel") or {}
        endereco_correspondencia = raw.get("enderecoCorrespondencia") or {}
        situacao = raw.get("situacao") or {}

        return {
            "id": raw.get("id"),
            "codigo": _int_or_none(raw.get("codigo")),
            "unidade": _int_or_none(raw.get("unidade")),
            "tipo_imovel_descricao": tipo_imovel.get("descricao"),
            "id_imovel_principal": _int_or_none(raw.get("idImovelPrincipal")),
            "endereco_correspondencia_descricao": endereco_correspondencia.get("descricao"),
            "englobado": _bool_or_none(raw.get("englobado")),
            "inscricao_incra": raw.get("inscricaoIncra"),
            "inscricao_anterior": raw.get("inscricaoAnterior"),
            "apartamento": raw.get("apartamento"),
            "bloco": raw.get("bloco"),
            "garagem": raw.get("garagem"),
            "sala": raw.get("sala"),
            "loja": raw.get("loja"),
            "cep": raw.get("cep"),
            "complemento": raw.get("complemento"),
            "lote": raw.get("lote"),
            "matricula": raw.get("matricula"),
            "numero": raw.get("numero"),
            "quadra": raw.get("quadra"),
            "setor": raw.get("setor"),
            "secao": raw.get("secao"),
            "situacao_descricao": situacao.get("descricao"),
            "inscricao_imobiliaria_formatada": raw.get("inscricaoImobiliariaFormatada"),
            "endereco_formatado": raw.get("enderecoFormatado"),
            "dt_construcao": _datetime_or_none(raw.get("dtConstrucao")),
            "dh_operacao": _datetime_or_none(raw.get("dhOperacao")),
            "created_by": raw.get("createdBy"),
            "created_in": _datetime_or_none(raw.get("createdIn")),
            "id_englobamento": _int_or_none(raw.get("idEnglobamento")),
            "id_imovel_englobado": _int_or_none(raw.get("idImovelEnglobado")),
            # Foreign Keys
            "bairro_id": bairro.get("id"),
            "condominio_id": None,  # raw.get("condominio", {}).get("id"),
            "distrito_id": distrito.get("id"),
            "logradouro_id": logradouro.get("id"),
            "loteamento_id": None  # raw.get("loteamento", {}).get("id")
        }'''
    },
    "secao": {
        "models": "Municipio, Secao",
        "entity": "Secao",
        "process_record_body": '''        municipio_data = raw.get("municipio") or {}

        return {
            "id": raw.get("id"),
            "codigo": _int_or_none(raw.get("codigo")),
            "nome": raw.get("nome"),
            "municipio_codigo_siafi": municipio_data.get("codigoSIAFI")
        }'''
    }
}

def update_loader_file(loader_name: str, file_path: str):
    """Atualiza um arquivo de loader específico."""
    config = LOADER_CONFIGS.get(loader_name)
    if not config:
        print(f"No configuration found for loader: {loader_name}")
        return

    content = LOADER_TEMPLATE.format(
        models=config["models"],
        entity=config["entity"],
        entity_lower=loader_name.lower(),
        entity_plural=f"{loader_name}s",
        process_record_body=config["process_record_body"]
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """Função principal que atualiza todos os loaders."""
    workspace_root = Path(".")
    loaders = workspace_root.glob("app/loader_*.py")
    
    for loader in loaders:
        if loader.name == "loader.py":  # Skip the main loader
            continue
            
        loader_name = loader.stem.split("_")[1]  # Get the name after "loader_"
        if loader_name in LOADER_CONFIGS:
            print(f"Updating {loader}")
            update_loader_file(loader_name, str(loader))
        else:
            print(f"Skipping {loader} - no configuration found")

if __name__ == "__main__":
    main()
