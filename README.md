# Configuração do Ambiente (.env)

Este projeto utiliza variáveis de ambiente para manter informações sensíveis seguras.

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
   PGDATABASE=seu_banco
   PGSCHEMA=seu_schema
   
   # Caminho do arquivo SQL de schema
   SQL_SCHEMA_PATH=sql/schema_auxiliar.sql
   
   # (Opcional) Nome da database de manutenção usada para criar outras DBs
   ADMIN_DB=postgres
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

# As variáveis ficam disponíveis via os.getenv()
db_password = os.getenv("PGPASSWORD")
```
