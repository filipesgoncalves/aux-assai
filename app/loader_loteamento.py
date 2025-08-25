# app/loader_loteamento.py
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from .database import SessionLocal, engine, SETTINGS, check_schema
from .models import Base, Municipio, Loteamento
from .utils import fix_encoding_in_dict

def _int_or_none(value) -> int | None:
    """Convert a value to integer or None if not possible."""
    if value in (None, "", "null"):
        return None
    try:
        return int(value)
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


def _process_record(raw: Dict[str, Any]) -> Dict[str, Any] | None:
    """Process a single Loteamento record from the JSON."""
    if not raw:
        return None

    try:
        municipio_data = raw.get("municipio") or {}
        bairro_data = raw.get("bairro") or {}

        return {
            "id": raw.get("id"),
            "codigo": _int_or_none(raw.get("codigo")),
            "nome": raw.get("nome"),
            "matricula_imobiliaria": raw.get("matriculaImobiliaria"),
            "dh_registro_imovel": _datetime_or_none(raw.get("dhRegistroImovel")),
            "nro_decreto_aprovacao": raw.get("nroDecretoAprovacao"),
            "nro_processo_aprovacao": raw.get("nroProcessoAprovacao"),
            "bairro_id": bairro_data.get("id"),
            "municipio_codigo_siafi": municipio_data.get("codigoSIAFI")
        }
    except Exception as e:
        print(f"Error processing Loteamento record: {str(e)}")
        print(f"Raw data: {raw}")
        return None


def _upsert_loteamento(sess: Session, data: Dict[str, Any]) -> None:
    """Insert or update a Loteamento record."""
    if not data:
        return

    try:
        stmt = insert(Loteamento).values(**data)
        stmt = stmt.on_conflict_do_update(
            index_elements=[Loteamento.id],
            set_=data
        )
        sess.execute(stmt)
    except Exception as e:
        print(f"Error upserting loteamento: {str(e)}")
        print(f"Loteamento data: {data}")
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
        print(f"Error checking schema: {str(e)}")
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
                        _upsert_loteamento(sess, processed_data)
                        success_count += 1
                except Exception as e:
                    print(f"Error processing record in chunk: {str(e)}")
                    continue

            try:
                sess.commit()
                return success_count
            except Exception as e:
                sess.rollback()
                print(f"Error committing chunk: {str(e)}")
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
            print(f"Error processing record: {str(e)}")
            skipped += 1

    if buffer:
        ok += _flush(buffer)

    return ok, skipped


def processar_cadastros(sess: Session, json_path: str) -> None:
    """
    Main entry point for loading loteamentos from JSON file.
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
