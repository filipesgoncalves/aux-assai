# app/loader_pessoa.py
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from .database import SessionLocal, engine, SETTINGS, check_schema
from .models import Base, Pessoa
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
                "%Y-%m-%d",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S"
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
    """Process a single Pessoa record from the JSON."""
    if not raw:
        return None

    try:
        situacao = raw.get("situacao") or {}
        tipo_pessoa = raw.get("tipoPessoa") or {}
        optante_simples = raw.get("optanteSimplesNacional") or {}
        pessoa_fisica = raw.get("pessoaFisica") or {}
        pessoa_fisica_docs = raw.get("pessoaFisicaDocumentos") or {}
        pessoa_juridica = raw.get("pessoaJuridica") or {}

        return {
            "id": raw.get("id"),
            "codigo": _int_or_none(raw.get("codigo")),
            "nome": raw.get("nome"),
            "nome_sem_espolio": raw.get("nomeSemEspolio"),
            "cpf_cnpj": raw.get("cpfCnpj"),
            "inscricao_municipal": raw.get("inscricaoMunicipal"),
            "nome_fantasia": raw.get("nomeFantasia"),
            "contribuinte_estrangeiro": _bool_or_none(raw.get("contribuinteEstrangeiro")),
            "site": raw.get("site"),
            "situacao_valor": situacao.get("valor"),
            "tipo_pessoa_valor": tipo_pessoa.get("valor"),
            "optante_simples_nacional_valor": optante_simples.get("valor"),
            "endereco_principal_formatado": raw.get("enderecoPrincipalFormatado"),
            "created_by": raw.get("createdBy"),
            "created_in": _datetime_or_none(raw.get("createdIn")),
            "email": raw.get("email"),
            "telefone": raw.get("telefone"),
            "dh_operacao": _datetime_or_none(raw.get("dhOperacao")),
            
            # Campos específicos de pessoa física
            "dt_obito": _datetime_or_none(pessoa_fisica.get("dtObito")),
            "dt_emissao_pis_pasep": _datetime_or_none(pessoa_fisica_docs.get("dtEmissaoPisPasep")),
            
            # Campos específicos de pessoa jurídica
            "natureza_juridica": pessoa_juridica.get("naturezaJuridica")
        }
    except Exception as e:
        print(f"Error processing Pessoa record: {str(e)}")
        print(f"Raw data: {raw}")
        return None


def _upsert_pessoa(sess: Session, data: Dict[str, Any]) -> None:
    """Insert or update a Pessoa record."""
    if not data:
        return

    try:
        stmt = insert(Pessoa).values(**data)
        stmt = stmt.on_conflict_do_update(
            index_elements=[Pessoa.id],
            set_=data
        )
        sess.execute(stmt)
    except Exception as e:
        print(f"Error upserting pessoa: {str(e)}")
        print(f"Pessoa data: {data}")
        raise


def load_from_iterable(
    records: Iterable[Dict[str, Any]], chunk_size: int = 500
) -> Tuple[int, int]:
    """Load records individually to prevent transaction cascade failures. Returns (successes, skipped)."""
    ok = skipped = 0

    try:
        # Sanity check for schema
        check_schema(engine, SETTINGS.schema)
    except Exception as e:
        print(f"Error checking schema: {str(e)}")
        raise

    for rec in records:
        try:
            # Process record
            processed_data = _process_record(rec)
            if not processed_data:
                skipped += 1
                continue

            # Individual transaction for each record
            with SessionLocal() as sess:
                try:
                    _upsert_pessoa(sess, processed_data)
                    sess.commit()
                    ok += 1
                except Exception as e:
                    sess.rollback()
                    print(f"Error processing pessoa record {processed_data.get('id', 'unknown')}: {str(e)}")
                    skipped += 1

        except Exception as e:
            print(f"Error processing record: {str(e)}")
            skipped += 1

    return ok, skipped


def processar_cadastros(sess: Session, json_path: str) -> None:
    """
    Main entry point for loading pessoas from JSON file.
    Compatible with the interface expected by main.py.
    """
    path = Path(json_path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        
        if isinstance(data, dict) and "content" in data:
            records = data["content"]
            # Fix UTF-8 encoding issues in all records
            records = [fix_encoding_in_dict(record) for record in records]
            ok, skipped = load_from_iterable(records)
            print(f"Processed {ok} records successfully, skipped {skipped} records")
        else:
            raise ValueError("Invalid JSON format: expected object with 'content' array")
    except Exception as e:
        raise ValueError(f"Error processing {json_path}: {str(e)}")
