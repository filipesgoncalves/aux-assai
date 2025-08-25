# app/models.py
from datetime import datetime
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    Boolean,
    String,
    CHAR,
    UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text as sa_text

Base = declarative_base()
DEFAULT_SCHEMA = "imobiliario"

class PlantaValor(Base):
    """Modelo para a tabela de planta de valores."""
    __tablename__ = 'planta_valores'
    __table_args__ = {'schema': DEFAULT_SCHEMA}

    id = Column(BigInteger, primary_key=True)
    valor = Column(Numeric(10, 2), nullable=False)
    data_referencia = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=sa_text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=sa_text('CURRENT_TIMESTAMP'), onupdate=datetime.now)


class Municipio(Base):
    __tablename__ = "municipio"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    # ID interno do sistema de origem
    id = Column(BigInteger)
    
    # Código SIAFI é a chave primária pois é usado nas foreign keys
    codigo_siafi = Column(Integer, primary_key=True)
    codigo_ibge = Column(Integer)
    nome = Column(String(100), nullable=False)
    
    # Dados do estado
    estado_id = Column(Integer)
    estado_nome = Column(String(50))
    estado_uf = Column(CHAR(2), nullable=False)
    estado_codigo_ibge = Column(Integer)


class Bairro(Base):
    __tablename__ = "bairro"
    __table_args__ = (
        UniqueConstraint("codigo", "municipio_codigo_siafi", name="uq_bairro_codigo_municipio"),
        {"schema": DEFAULT_SCHEMA},
    )

    id = Column(BigInteger, primary_key=True)
    codigo = Column(Integer)
    nome = Column(String(100), nullable=False)
    municipio_codigo_siafi = Column(Integer, ForeignKey(f"{DEFAULT_SCHEMA}.municipio.codigo_siafi"))
    zona_rural_descricao = Column(String(3))


class Condominio(Base):
    __tablename__ = "condominio"
    __table_args__ = (
        UniqueConstraint("codigo", name="uq_condominio_codigo"),
        {"schema": DEFAULT_SCHEMA},
    )

    id = Column(BigInteger, primary_key=True)
    codigo = Column(Integer, nullable=False)
    nome = Column(String(200), nullable=False)
    tipo_condominio_valor = Column(String(20))
    tipo_condominio_descricao = Column(String(20))


class Distrito(Base):
    __tablename__ = "distrito"
    __table_args__ = (
        UniqueConstraint("codigo", "municipio_codigo_siafi", name="uq_distrito_codigo_municipio"),
        {"schema": DEFAULT_SCHEMA},
    )

    id = Column(BigInteger, primary_key=True)
    nome = Column(String(100), nullable=False)
    codigo = Column(Integer)
    municipio_codigo_siafi = Column(Integer, ForeignKey(f"{DEFAULT_SCHEMA}.municipio.codigo_siafi"))


class Logradouro(Base):
    __tablename__ = "logradouro"
    __table_args__ = (
        UniqueConstraint("codigo", "municipio_codigo_siafi", name="uq_logradouro_codigo_municipio"),
        {"schema": DEFAULT_SCHEMA},
    )

    id = Column(BigInteger, primary_key=True)
    codigo = Column(Integer, nullable=False)
    nome = Column(String(200), nullable=False)
    tipo_logradouro_descricao = Column(String(50))
    tipo_logradouro_abreviatura = Column(String(5))
    cep = Column(String(8))
    extensao = Column(Numeric(10, 2))
    lei = Column(String(50))
    zona_fiscal = Column(String(50))
    municipio_codigo_siafi = Column(Integer, ForeignKey(f"{DEFAULT_SCHEMA}.municipio.codigo_siafi"))
    denominacao_anterior = Column(String(200))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))


class Loteamento(Base):
    __tablename__ = "loteamento"
    __table_args__ = (
        UniqueConstraint("codigo", "municipio_codigo_siafi", name="uq_loteamento_codigo_municipio"),
        {"schema": DEFAULT_SCHEMA},
    )

    id = Column(BigInteger, primary_key=True)
    codigo = Column(Integer, nullable=False)
    nome = Column(String(200), nullable=False)
    matricula_imobiliaria = Column(String(50))
    dh_registro_imovel = Column(DateTime)
    nro_decreto_aprovacao = Column(String(50))
    nro_processo_aprovacao = Column(String(50))
    bairro_id = Column(BigInteger, ForeignKey(f"{DEFAULT_SCHEMA}.bairro.id"))
    municipio_codigo_siafi = Column(Integer, ForeignKey(f"{DEFAULT_SCHEMA}.municipio.codigo_siafi"))


class Face(Base):
    __tablename__ = "face"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = Column(BigInteger, primary_key=True)
    abreviatura = Column(String(5))
    descricao = Column(String(50))
    padrao_valor = Column(String(3))
    padrao_descricao = Column(String(3))


class Secao(Base):
    __tablename__ = "secao"
    __table_args__ = (
        UniqueConstraint("nro_secao", "logradouro_id", name="uq_secao_nro_logradouro"),
        {"schema": DEFAULT_SCHEMA},
    )

    id = Column(BigInteger, primary_key=True)
    nro_secao = Column(Integer, nullable=False)
    logradouro_id = Column(BigInteger, ForeignKey(f"{DEFAULT_SCHEMA}.logradouro.id"))
    face_id = Column(BigInteger, ForeignKey(f"{DEFAULT_SCHEMA}.face.id"))


class Imovel(Base):
    __tablename__ = "imovel"
    __table_args__ = (
        UniqueConstraint("codigo", "unidade", name="uq_imovel_codigo_unidade"),
        {"schema": DEFAULT_SCHEMA},
    )

    id = Column(BigInteger, primary_key=True)
    codigo = Column(BigInteger, nullable=False)
    unidade = Column(Integer, nullable=False)
    tipo_imovel_descricao = Column(String(20))
    id_imovel_principal = Column(BigInteger, ForeignKey(f"{DEFAULT_SCHEMA}.imovel.id"))
    endereco_correspondencia_descricao = Column(String(20))
    englobado = Column(Boolean, default=False)
    inscricao_incra = Column(String(50))
    inscricao_anterior = Column(String(50))
    apartamento = Column(String(10))
    bloco = Column(String(10))
    garagem = Column(String(10))
    sala = Column(String(10))
    loja = Column(String(10))
    cep = Column(String(8))
    complemento = Column(String(100))
    lote = Column(String(20))
    matricula = Column(String(50))
    numero = Column(String(10))
    quadra = Column(String(20))
    setor = Column(String(20))
    secao = Column(String(20))
    situacao_descricao = Column(String(20))
    inscricao_imobiliaria_formatada = Column(String(50))
    endereco_formatado = Column(String(500))
    dt_construcao = Column(DateTime)
    dh_operacao = Column(DateTime)
    created_by = Column(String(50))
    created_in = Column(DateTime)
    id_englobamento = Column(BigInteger)
    id_imovel_englobado = Column(BigInteger, ForeignKey(f"{DEFAULT_SCHEMA}.imovel.id"))
    bairro_id = Column(BigInteger, ForeignKey(f"{DEFAULT_SCHEMA}.bairro.id"))
    condominio_id = Column(BigInteger, ForeignKey(f"{DEFAULT_SCHEMA}.condominio.id"))
    distrito_id = Column(BigInteger, ForeignKey(f"{DEFAULT_SCHEMA}.distrito.id"))
    logradouro_id = Column(BigInteger, ForeignKey(f"{DEFAULT_SCHEMA}.logradouro.id"))
    loteamento_id = Column(BigInteger, ForeignKey(f"{DEFAULT_SCHEMA}.loteamento.id"))


class Pessoa(Base):
    """Modelo para a tabela de pessoas."""
    __tablename__ = 'pessoa'
    __table_args__ = {'schema': DEFAULT_SCHEMA}

    id = Column(BigInteger, primary_key=True)
    codigo = Column(Integer)
    nome = Column(String(200), nullable=False)
    nome_sem_espolio = Column(String(200))
    cpf_cnpj = Column(String(20))
    inscricao_municipal = Column(String(20))
    nome_fantasia = Column(String(200))
    contribuinte_estrangeiro = Column(Boolean)
    site = Column(String(200))
    situacao_valor = Column(String(20))
    tipo_pessoa_valor = Column(String(20))
    optante_simples_nacional_valor = Column(String(10))
    endereco_principal_formatado = Column(String(500))
    created_by = Column(String(50))
    created_in = Column(DateTime)
    email = Column(String(100))
    telefone = Column(String(20))
    dh_operacao = Column(DateTime)
    
    # Campos específicos de pessoa física
    dt_obito = Column(DateTime)
    dt_emissao_pis_pasep = Column(DateTime)
    
    # Campos específicos de pessoa jurídica
    natureza_juridica = Column(String(100))
