# app/loader_imovel.py
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple, Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from .database import SessionLocal, engine, SETTINGS, check_schema
from .models import Base, Base, Municipio, Bairro, Condominio, Distrito, Logradouro, Loteamento, Imovel
from .utils import fix_encoding_in_dict

def _int_or_none(value) -> int | None:
    """Convert a value to integer or None if not possible."""
    if value in (None, "", "null"):
        return None
    try:
        return int(value)
    except Exception:
        return None


def _bool_or_none(value) -> bool | None:
    """Convert a value to boolean or None if not possible."""
    if value in (None, "", "null"):
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', 't', '1', 'yes', 'sim', 'verdadeiro')
    try:
        return bool(value)
    except Exception:
        return None


def _datetime_or_none(value):
    """Convert a value to datetime or None if not possible."""
    if value in (None, "", "null"):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            # Try different datetime formats
            formats = [
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d"
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        except Exception:
            pass
    return None


def _safe_foreign_key_id(sess: Session, model_class, ref_id: int) -> Optional[int]:
    """
    Safely check if a foreign key reference exists in the database.
    Returns the ID if exists, None if not.
    """
    if not ref_id:
        return None
    
    try:
        exists = sess.query(model_class).filter(model_class.id == ref_id).first()
        return ref_id if exists else None
    except Exception:
        return None


def _process_record(raw: Dict[str, Any]) -> Dict[str, Any] | None:
    """Process a single Imovel record from the JSON."""
    if not raw:
        return None

    try:
        bairro = raw.get("bairro") or {}
        distrito = raw.get("distrito") or {}
        logradouro = raw.get("logradouro") or {}
        tipo_imovel = raw.get("tipoImovel") or {}
        endereco_correspondencia = raw.get("enderecoCorrespondencia") or {}
        situacao = raw.get("situacao") or {}

        return {
            "id": raw.get("id"),
            "codigo": _int_or_none(raw.get("codigo")),
            "unidade": _int_or_none(raw.get("unidade")) or 1,
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
        }
    except Exception as e:
        print(f"Error processing Imovel record: {str(e)}")
        print(f"Raw data: {raw}")
        return None


def _upsert_imovel(sess: Session, data: Dict[str, Any]) -> None:
    """Insert or update a Imovel record."""
    if not data:
        return

    try:
        # Verificar e corrigir referências de chaves estrangeiras
        data['bairro_id'] = _safe_foreign_key_id(sess, Bairro, data.get('bairro_id'))
        data['distrito_id'] = _safe_foreign_key_id(sess, Distrito, data.get('distrito_id'))
        data['logradouro_id'] = _safe_foreign_key_id(sess, Logradouro, data.get('logradouro_id'))
        
        stmt = insert(Imovel).values(**data)
        stmt = stmt.on_conflict_do_update(
            index_elements=[Imovel.id],
            set_=data
        )
        sess.execute(stmt)
    except Exception as e:
        print(f"Error upserting imovel: {str(e)}")
        print(f"Imovel data: {data}")
        raise


def load_from_iterable(
    records: Iterable[Dict[str, Any]], chunk_size: int = 500
) -> Tuple[int, int]:
    """Load records individually with separate transactions. Returns (successes, skipped)."""
    ok = skipped = 0

    try:
        # Sanity check for schema
        check_schema(engine, SETTINGS.schema)
    except Exception as e:
        print(f"Error checking schema: {str(e)}")
        raise

    for rec in records:
        try:
            processed_data = _process_record(rec)
            if processed_data:
                # Individual transaction for each record
                with SessionLocal() as sess:
                    try:
                        _upsert_imovel(sess, processed_data)
                        sess.commit()
                        ok += 1
                    except Exception as e:
                        sess.rollback()
                        print(f"Error processing individual record: {str(e)}")
                        print(f"Imovel data: {processed_data}")
                        skipped += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"Error processing record: {str(e)}")
            skipped += 1

    return ok, skipped


def processar_cadastros(sess: Session, json_path: str) -> None:
    """
    Main entry point for loading imovels from JSON file.
    Compatible with the interface expected by main.py.
    """
    path = Path(json_path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        
        # Fix encoding issues
        data = fix_encoding_in_dict(data)
        
        if isinstance(data, dict) and "content" in data:
            records = data["content"]
            ok, skipped = load_from_iterable(records)
            print(f"Processed {ok} records successfully, skipped {skipped} records")
        else:
            raise ValueError("Invalid JSON format: expected object with 'content' array")
    except Exception as e:
        raise ValueError(f"Error processing {json_path}: {str(e)}")
