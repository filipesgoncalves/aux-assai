-- ============================================================
-- SCHEMA
-- ============================================================
CREATE SCHEMA IF NOT EXISTS imobiliario;

-- ============================================================
-- MUNICÍPIO
-- ============================================================
CREATE TABLE IF NOT EXISTS imobiliario.municipio (
    id BIGINT,
    codigo_siafi INTEGER PRIMARY KEY,
    codigo_ibge INTEGER,
    nome VARCHAR(100) NOT NULL,
    estado_id INTEGER,
    estado_nome VARCHAR(100),
    estado_uf VARCHAR(2),
    estado_codigo_ibge INTEGER
);

-- ============================================================
-- BAIRROS
-- ============================================================
CREATE TABLE IF NOT EXISTS imobiliario.bairro (
    id BIGINT PRIMARY KEY,
    codigo INTEGER,
    nome VARCHAR(100) NOT NULL,
    municipio_codigo_siafi INTEGER REFERENCES imobiliario.municipio(codigo_siafi),
    zona_rural_descricao VARCHAR(3),
    UNIQUE(codigo, municipio_codigo_siafi)
);

-- ============================================================
-- CONDOMÍNIOS
-- ============================================================
CREATE TABLE IF NOT EXISTS imobiliario.condominio (
    id BIGINT PRIMARY KEY,
    codigo INTEGER NOT NULL,
    nome VARCHAR(200) NOT NULL,
    tipo_condominio_valor VARCHAR(20),
    tipo_condominio_descricao VARCHAR(20),
    UNIQUE(codigo)
);

-- ============================================================
-- DISTRITOS
-- ============================================================
CREATE TABLE IF NOT EXISTS imobiliario.distrito (
    id BIGINT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    codigo INTEGER,
    municipio_codigo_siafi INTEGER REFERENCES imobiliario.municipio(codigo_siafi),
    UNIQUE(codigo, municipio_codigo_siafi)
);

-- ============================================================
-- LOGRADOUROS
-- ============================================================
CREATE TABLE IF NOT EXISTS imobiliario.logradouro (
    id BIGINT PRIMARY KEY,
    codigo INTEGER NOT NULL,
    nome VARCHAR(200) NOT NULL,
    tipo_logradouro_descricao VARCHAR(50),
    tipo_logradouro_abreviatura VARCHAR(5),
    cep VARCHAR(8),
    extensao DECIMAL(10,2),
    lei VARCHAR(50),
    zona_fiscal VARCHAR(50),
    municipio_codigo_siafi INTEGER REFERENCES imobiliario.municipio(codigo_siafi),
    denominacao_anterior VARCHAR(200),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    UNIQUE(codigo, municipio_codigo_siafi)
);

-- ============================================================
-- LOTEAMENTOS
-- ============================================================
CREATE TABLE IF NOT EXISTS imobiliario.loteamento (
    id BIGINT PRIMARY KEY,
    codigo INTEGER NOT NULL,
    nome VARCHAR(200) NOT NULL,
    matricula_imobiliaria VARCHAR(50),
    dh_registro_imovel TIMESTAMP,
    nro_decreto_aprovacao VARCHAR(50),
    nro_processo_aprovacao VARCHAR(50),
    bairro_id BIGINT REFERENCES imobiliario.bairro(id),
    municipio_codigo_siafi INTEGER REFERENCES imobiliario.municipio(codigo_siafi),
    UNIQUE(codigo, municipio_codigo_siafi)
);

-- ============================================================
-- FACES
-- ============================================================
CREATE TABLE IF NOT EXISTS imobiliario.face (
    id BIGINT PRIMARY KEY,
    abreviatura VARCHAR(5),
    descricao VARCHAR(50),
    padrao_valor VARCHAR(3),
    padrao_descricao VARCHAR(3)
);

-- ============================================================
-- SEÇÕES DE LOGRADOUROS
-- ============================================================
CREATE TABLE IF NOT EXISTS imobiliario.secao (
    id BIGINT PRIMARY KEY,
    nro_secao INTEGER NOT NULL,
    logradouro_id BIGINT REFERENCES imobiliario.logradouro(id),
    face_id BIGINT REFERENCES imobiliario.face(id),
    UNIQUE(nro_secao, logradouro_id)
);

-- ============================================================
-- PESSOAS
-- ============================================================
CREATE TABLE IF NOT EXISTS imobiliario.pessoa (
    id BIGINT PRIMARY KEY,
    codigo INTEGER,
    nome VARCHAR(200) NOT NULL,
    nome_sem_espolio VARCHAR(200),
    cpf_cnpj VARCHAR(20),
    inscricao_municipal VARCHAR(20),
    nome_fantasia VARCHAR(200),
    contribuinte_estrangeiro BOOLEAN,
    site VARCHAR(200),
    situacao_valor VARCHAR(20),
    tipo_pessoa_valor VARCHAR(20),
    optante_simples_nacional_valor VARCHAR(20),
    endereco_principal_formatado VARCHAR(500),
    created_by VARCHAR(50),
    created_in TIMESTAMP,
    email VARCHAR(200),
    telefone VARCHAR(20),
    dh_operacao TIMESTAMP,
    dt_obito DATE,
    dt_emissao_pis_pasep DATE,
    natureza_juridica VARCHAR(100)
);

-- ============================================================
-- IMÓVEIS
-- ============================================================
CREATE TABLE IF NOT EXISTS imobiliario.imovel (
    id BIGINT PRIMARY KEY,
    codigo BIGINT NOT NULL,
    unidade INTEGER NOT NULL,
    tipo_imovel_descricao VARCHAR(20),
    id_imovel_principal BIGINT REFERENCES imobiliario.imovel(id),
    endereco_correspondencia_descricao VARCHAR(20),
    englobado BOOLEAN DEFAULT FALSE,
    inscricao_incra VARCHAR(50),
    inscricao_anterior VARCHAR(50),
    apartamento VARCHAR(10),
    bloco VARCHAR(10),
    garagem VARCHAR(10),
    sala VARCHAR(10),
    loja VARCHAR(10),
    cep VARCHAR(8),
    complemento VARCHAR(100),
    lote VARCHAR(20),
    matricula VARCHAR(50),
    numero VARCHAR(10),
    quadra VARCHAR(20),
    setor VARCHAR(20),
    secao VARCHAR(20),
    situacao_descricao VARCHAR(20),
    inscricao_imobiliaria_formatada VARCHAR(50),
    endereco_formatado VARCHAR(500),
    dt_construcao DATE,
    dh_operacao TIMESTAMP,
    created_by VARCHAR(50),
    created_in TIMESTAMP,
    id_englobamento BIGINT,
    id_imovel_englobado BIGINT REFERENCES imobiliario.imovel(id),
    bairro_id BIGINT REFERENCES imobiliario.bairro(id),
    condominio_id BIGINT REFERENCES imobiliario.condominio(id),
    distrito_id BIGINT REFERENCES imobiliario.distrito(id),
    logradouro_id BIGINT REFERENCES imobiliario.logradouro(id),
    loteamento_id BIGINT REFERENCES imobiliario.loteamento(id),
    UNIQUE(codigo, unidade)
);

-- Índices para busca eficiente
CREATE INDEX IF NOT EXISTS ix_imovel_inscricao ON imobiliario.imovel (inscricao_imobiliaria_formatada);
CREATE INDEX IF NOT EXISTS ix_imovel_situacao ON imobiliario.imovel (situacao_descricao);
CREATE INDEX IF NOT EXISTS ix_imovel_bairro ON imobiliario.imovel (bairro_id);
CREATE INDEX IF NOT EXISTS ix_imovel_condominio ON imobiliario.imovel (condominio_id);
CREATE INDEX IF NOT EXISTS ix_imovel_distrito ON imobiliario.imovel (distrito_id);
CREATE INDEX IF NOT EXISTS ix_imovel_logradouro ON imobiliario.imovel (logradouro_id);
CREATE INDEX IF NOT EXISTS ix_imovel_loteamento ON imobiliario.imovel (loteamento_id);
CREATE INDEX IF NOT EXISTS ix_imovel_cep ON imobiliario.imovel (cep);

CREATE INDEX IF NOT EXISTS ix_bairro_municipio ON imobiliario.bairro (municipio_codigo_siafi);
CREATE INDEX IF NOT EXISTS ix_distrito_municipio ON imobiliario.distrito (municipio_codigo_siafi);
CREATE INDEX IF NOT EXISTS ix_logradouro_municipio ON imobiliario.logradouro (municipio_codigo_siafi);
CREATE INDEX IF NOT EXISTS ix_logradouro_cep ON imobiliario.logradouro (cep);
CREATE INDEX IF NOT EXISTS ix_loteamento_municipio ON imobiliario.loteamento (municipio_codigo_siafi);
