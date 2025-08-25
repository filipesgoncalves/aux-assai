# -*- coding: utf-8 -*-
"""
main.py — Orquestra a carga dos cadastros e do BCI (bci_item)

Uso:
    # apenas cadastros
    python3 -m app.main --json data/cadastros.json

    # apenas BCI
    python3 -m app.main --bci data/bci.json

    # ambos
    python3 -m app.main --json data/cadastros.json --bci data/bci.json
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

# ==============================
# Logging
# ==============================
LOG = logging.getLogger("app.main")


def _setup_logging(verbosity: int = 1) -> None:
    """Configura logging em console e arquivo, sem duplicar handlers."""
    if LOG.handlers:
        return

    level = logging.INFO if verbosity <= 1 else logging.DEBUG
    LOG.setLevel(level)

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    logfile = log_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(fmt)

    fh = logging.FileHandler(logfile, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(fmt)

    LOG.addHandler(ch)
    LOG.addHandler(fh)


# ==============================
# DB session helpers
# ==============================
@contextmanager
def _fallback_session():
    """
    Caso o projeto não exponha get_session(), usa SessionLocal de app.database.
    Mantém o padrão: commit controlado pelo chamador.
    """
    from app.database import SessionLocal  # type: ignore

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _get_session_ctx():
    """
    Retorna um contextmanager de sessão:
      1) app.database.get_session (se existir)
      2) fallback para SessionLocal()
    """
    try:
        from app.database import get_session  # type: ignore

        return get_session
    except Exception:
        return _fallback_session


# ==============================
# Cadastro loader resolver
# ==============================
def _resolve_cadastro_loader() -> Callable:
    """
    Mantém o padrão do cadastro que já funciona, tentando importar a função
    que você já usa. Suporta alguns nomes comuns sem quebrar compatibilidade.
    """
    try:
        # Tenta importações absolutas primeiro
        from app.loader import processar_cadastros
        LOG.debug("Using loader: app.loader.processar_cadastros")
        return processar_cadastros
    except ImportError:
        # Se não funcionar, tenta outras localizações
        candidates = [
            ("app.loader", "processar_cadastros"),
            ("app.loader", "load_cadastros_json"),
            ("app.cadastro_loader", "processar_cadastros"),
            ("app.cadastro_loader", "load_cadastros_json"),
            ("app.loader", "run")
        ]

        for mod_name, func_name in candidates:
            try:
                if "." in mod_name:
                    mod = __import__(mod_name, fromlist=[func_name])
                else:
                    mod = __import__(mod_name)
                func = getattr(mod, func_name, None)
                if callable(func):
                    LOG.debug("Usando loader de cadastros: %s.%s", mod_name, func_name)
                    return func  # esperado: func(session, path)
            except Exception as e:  # pragma: no cover
                LOG.debug("Failed to import %s.%s: %s", mod_name, func_name, str(e))
                continue

        raise ImportError(
            "Não foi possível localizar a função de carga de cadastros existente. "
            "Tente expor algo como 'processar_cadastros(session, path)' em app.loader "
            "ou ajuste os aliases em _resolve_cadastro_loader()."
        )


# ==============================
# BCI loader
# ==============================
def _resolve_bci_loader() -> Callable:
    """Importa o loader novo do BCI (bci_item)."""
    from app.bci_loader import load_bci_json  # type: ignore

    return load_bci_json  # esperado: func(session, path[, chunk_size])


# ==============================
# CLI
# ==============================
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="app.main",
        description="Carga de cadastros e BCI (bci_item) no schema 'imobiliario'.",
    )
    p.add_argument("--json", help="Caminho para cadastros.json")
    p.add_argument("--bci", help="Caminho para bci.json")
    p.add_argument(
        "--chunk-size",
        type=int,
        default=5000,
        help="Tamanho do lote para UPSERT do BCI (default: 5000)",
    )
    p.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=1,
        help="Aumenta verbosidade (-v, -vv)",
    )
    return p.parse_args()


# ==============================
# Main
# ==============================
def main() -> None:
    args = parse_args()
    _setup_logging(args.verbose)

    start = time.time()
    LOG.info("Iniciando carga...")

    # resolve sessões e loaders mantendo o padrão que já funciona
    session_ctx = _get_session_ctx()
    cadastro_loader: Optional[Callable] = None
    if args.json:
        cadastro_loader = _resolve_cadastro_loader()
    bci_loader: Optional[Callable] = None
    if args.bci:
        bci_loader = _resolve_bci_loader()

    if not args.json and not args.bci:
        LOG.warning("Nada a fazer: informe --json e/ou --bci.")
        return

    try:
        with session_ctx() as session:
            # 1) CADASTROS (mantém seu fluxo atual)
            if args.json and cadastro_loader:
                LOG.info("Carregando cadastros de: %s", args.json)
                cadastro_loader(session, args.json)
                session.commit()
                LOG.info("Cadastros: commit concluído.")

            # 2) BCI (novo fluxo)
            if args.bci and bci_loader:
                LOG.info("Carregando BCI de: %s (chunk=%d)", args.bci, args.chunk_size)
                lidos, upsertados = bci_loader(
                    session, args.bci, chunk_size=args.chunk_size
                )
                session.commit()
                LOG.info(
                    "BCI: lidos=%d, upsertados=%d. Commit concluído.", lidos, upsertados
                )

    except KeyboardInterrupt:
        LOG.error("Execução interrompida pelo usuário (CTRL+C).")
        sys.exit(130)
    except Exception as exc:
        LOG.exception("Falha na execução: %s", exc)
        sys.exit(1)
    finally:
        elapsed = time.time() - start
        LOG.info("Finalizado em %.2fs.", elapsed)


if __name__ == "__main__":
    main()