# Banco de Dados PostgreSQL - Resumo

## O que foi feito

✅ **Sistema completo de suporte a PostgreSQL e SQLite**

1. **Módulo de Conexão Universal** (`db_connection.py`)
   - Detecta automaticamente se deve usar PostgreSQL ou SQLite
   - Compatível com ambos os bancos de dados
   - Adapta queries automaticamente (? para %s quando necessário)

2. **Script de Inicialização** (`init_postgres.py`)
   - Cria todas as tabelas necessárias
   - Insere dados padrão
   - Pode ser executado via console do Render

3. **Código Adaptado**
   - `helpers.py` - Adaptado para usar PostgreSQL/SQLite
   - `admin.py` - Usa o novo módulo de conexão
   - Suporte automático sem necessidade de mudanças no código

## Como usar

### 1. Configure a variável de ambiente no Render:

```
DATABASE_URL=postgresql://raisilva:mKvWcbLKL78ODmfIQRauoC1RDrbb3M3W@dpg-d4l4rtk9c44c73fadkpg-a.oregon-postgres.render.com/rsdb_a8ag
```

### 2. Pronto! A inicialização é automática!

✅ **Não precisa fazer mais nada!**

O script de inicialização será executado automaticamente quando a aplicação iniciar no Render. A aplicação detecta automaticamente:

- Se está usando PostgreSQL (quando `DATABASE_URL` está definido)
- Se as tabelas já existem
- Se precisa criar tabelas e dados padrão

**Na primeira inicialização:**
- Cria todas as tabelas
- Insere dados padrão
- Cria usuário admin (admin/admin123)

**Em reinicializações:**
- Verifica que tudo está OK
- Não faz alterações se já estiver inicializado

O aplicativo detectará automaticamente o PostgreSQL e usará o banco externo. Todos os dados e imagens serão armazenados no PostgreSQL do Render, garantindo que nada seja perdido após hibernação.

## Dependências adicionadas

- `psycopg2-binary==2.9.9` - Driver PostgreSQL para Python

## Arquivos criados/modificados

- ✅ `db_connection.py` - Módulo de conexão universal
- ✅ `init_postgres.py` - Script de inicialização do PostgreSQL
- ✅ `helpers.py` - Adaptado para PostgreSQL/SQLite
- ✅ `admin.py` - Usa novo módulo de conexão
- ✅ `requirements.txt` - Adicionado psycopg2-binary
- ✅ `POSTGRES_SETUP.md` - Documentação completa

## Importante

⚠️ **Todas as informações e imagens são armazenadas no banco PostgreSQL do Render**
- Dados persistem após hibernação
- Nenhum dado será perdido

⚠️ **Altere a senha do admin após o primeiro acesso**
- Usuário padrão: `admin`
- Senha padrão: `admin123`

