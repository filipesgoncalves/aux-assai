# Configuração do Ambiente (.env)

Este projeto utiliza variáveis de ambiente para manter informações sensíveis seguras.

## Arquivos de Configuração

- **`.env`**: Contém suas configurações reais (ignorado pelo Git)
- **`.env.example`**: Template para outros desenvolvedores
- **`config.py`**: Configurações centralizadas para scripts na raiz
- **`app/database.py`**: Configurações para o módulo app

## Configuração

1. **Copie o arquivo de exemplo:**
   ```bash
   cp .env.example .env
   ```

2. **Edite o arquivo `.env` com suas configurações:**
   ```bash
   # Configurações do Banco de Dados PostgreSQL
   PGHOST=localhost
   PGPORT=5432
   PGUSER=postgres
   PGPASSWORD=sua_senha_real
   PGDATABASE=auxiliar_assai
   PGSCHEMA=imobiliario
   
   # Caminho do arquivo SQL de schema
   SQL_SCHEMA_PATH=sql/schema_auxiliar.sql
   
   # (Opcional) Nome da database de manutenção usada para criar outras DBs
   ADMIN_DB=postgres
   ```

## Como usar no código

### Para scripts na raiz do projeto:
```python
from config import DB_CONFIG

# Usar as configurações
connection_string = DB_CONFIG.conn_str()
database_url = DB_CONFIG.url
schema_name = DB_CONFIG.schema
```

### Para código no módulo app:
```python
from app.database import SETTINGS

# Usar as configurações
database_url = SETTINGS.url
schema_name = SETTINGS.schema
```

## Variáveis de Ambiente

- **PGHOST**: Host do banco PostgreSQL (padrão: localhost)
- **PGPORT**: Porta do banco PostgreSQL (padrão: 5432)  
- **PGUSER**: Usuário do banco de dados
- **PGPASSWORD**: Senha do banco de dados (MANTENHA SEGURA!)
- **PGDATABASE**: Nome da base de dados
- **PGSCHEMA**: Schema padrão a ser usado
- **SQL_SCHEMA_PATH**: Caminho para o arquivo de schema SQL
- **ADMIN_DB**: Base de dados administrativa para operações de manutenção

## Segurança

⚠️ **IMPORTANTE**: 
- O arquivo `.env` contém informações sensíveis e está no `.gitignore`
- NUNCA committe o arquivo `.env` no Git
- Use o `.env.example` como template para outros desenvolvedores
- Mantenha suas senhas seguras e não as compartilhe

## Arquivos atualizados

Os seguintes scripts agora usam configurações centralizadas:
- ✅ `check_schema.py` - usa `config.py`
- ✅ `fix_schema.py` - usa `config.py`
- ✅ `recreate_db.py` - usa `config.py`
- ✅ `recreate_tables.py` - usa `config.py`
- ✅ `repo/setup_db.py` - usa `config.py` 
- ✅ `app/database.py` - configurações do módulo app
- ✅ `repo/setup_rdb.py` - usa `app.database.SETTINGS`
