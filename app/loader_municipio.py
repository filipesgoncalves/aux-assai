from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple, Set

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from .database import SessionLocal, engine, SETTINGS, check_schema
from .models import Base, Municipio

def _process_municipios_from_bairros(raw_data: Dict[str, Any]) -> Set[Dict[str, Any]]:
    """Extract unique municipalities from bairros data."""
    if not raw_data or not isinstance(raw_data, dict):
        return set()

    content = raw_data.get("content", [])
    if not content:
        return set()

    municipios = set()
    for item in content:
        try:
            mun = item.get("municipio", {})
            if not mun:
                continue

            estado = mun.get("estado", {})
            if not estado:
                continue

            mun_tuple = (
                mun.get("id"),
                mun.get("nome"),
                mun.get("codigoSIAFI"),
                mun.get("codigoIBGE"),
                estado.get("id"),
                estado.get("nome"),
                estado.get("uf"),
                estado.get("codigoIbge")
            )
            municipios.add(mun_tuple)

        except Exception as e:
            print(f"Error extracting municipality data: {e}")
            continue

    return [
        {
            "id": mun[0],
            "nome": mun[1],
            "codigo_siafi": mun[2],
            "codigo_ibge": mun[3],
            "estado_id": mun[4],
            "estado_nome": mun[5],
            "estado_uf": mun[6],
            "estado_codigo_ibge": mun[7]
        }
        for mun in municipios
    ]

def _upsert_municipio(sess: Session, data: Dict[str, Any]) -> None:
    """Insert or update a Municipio record."""
    if not data:
        return

    try:
        stmt = insert(Municipio).values(
            id=data["id"],
            nome=data["nome"],
            codigo_siafi=data["codigo_siafi"],
            codigo_ibge=data["codigo_ibge"],
            estado_id=data["estado_id"],
            estado_nome=data["estado_nome"],
            estado_uf=data["estado_uf"],
            estado_codigo_ibge=data["estado_codigo_ibge"]
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=[Municipio.codigo_siafi],  
            set_={
                "id": stmt.excluded.id,
                "nome": stmt.excluded.nome,
                "codigo_ibge": stmt.excluded.codigo_ibge,
                "estado_id": stmt.excluded.estado_id,
                "estado_nome": stmt.excluded.estado_nome,
                "estado_uf": stmt.excluded.estado_uf,
                "estado_codigo_ibge": stmt.excluded.estado_codigo_ibge
            }
        )

        sess.execute(stmt)
        
    except Exception as e:
        print(f"Error upserting municipio: {str(e)}")
        print(f"Municipio data: {data}")
        try:
            sess.rollback()
        except:
            pass  
        raise

def processar_cadastros_from_bairros(json_path: str | Path) -> None:
    """Process municipios from bairros JSON file."""
    if not json_path:
        raise ValueError("JSON path not provided")

    try:
       
        with open(json_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        municipios = _process_municipios_from_bairros(raw_data)
        if not municipios:
            print("No municipalities found in bairros data")
            return

        print(f"Processing {len(municipios)} municipalities...")
        
        successful_count = 0
        for mun in municipios:
            sess = SessionLocal()
            try:
                check_schema(sess)
                
                _upsert_municipio(sess, mun)
                
                sess.commit()
                successful_count += 1
                
            except Exception as e:
                print(f"Error processing municipality {mun.get('nome')}: {e}")
                try:
                    sess.rollback()
                except:
                    pass  
            finally:
                try:
                    sess.close()
                except:
                    pass  

        print(f"Successfully processed {successful_count} municipalities")
        
    except Exception as e:
        print(f"Error loading municipios from bairros: {e}")
        raise ValueError(f"Error processing {json_path}: {e}")
