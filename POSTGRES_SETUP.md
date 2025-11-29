# Configuração do Banco de Dados PostgreSQL no Render

Este guia explica como configurar e inicializar o banco de dados PostgreSQL no Render.

## Pré-requisitos

1. Banco de dados PostgreSQL criado no Render
2. URL de conexão do banco de dados (External Database URL)
3. Variável de ambiente `DATABASE_URL` configurada no Render

## Passo a Passo

### 1. Configurar Variável de Ambiente no Render

No painel do Render, adicione a variável de ambiente:

**Nome:** `DATABASE_URL`
**Valor:** `postgresql://raisilva:mKvWcbLKL78ODmfIQRauoC1RDrbb3M3W@dpg-d4l4rtk9c44c73fadkpg-a.oregon-postgres.render.com/rsdb_a8ag`

⚠️ **IMPORTANTE:** Use a URL completa do seu banco de dados PostgreSQL.

### 2. Inicialização Automática

✅ **A inicialização acontece automaticamente!**

O script de inicialização será executado automaticamente quando a aplicação iniciar no Render. Não é necessário executar manualmente.

A aplicação verifica automaticamente se as tabelas já existem antes de criar. Isso significa que:

- Na primeira vez que a aplicação iniciar, as tabelas serão criadas automaticamente
- Em reinicializações subsequentes, nada será alterado (apenas verificará que tudo está OK)
- Não há risco de duplicar dados ou tabelas

**⚠️ Nota:** No plano free do Render, não há acesso ao console, então a inicialização automática é essencial!

### 3. Verificar Inicialização

Após executar o script, você deve ver mensagens como:

```
✓ Tabelas criadas com sucesso!
✓ Usuário admin criado (usuário: admin, senha: admin123)
✓ Conteúdo padrão inicializado
✓ Slides do carrossel inicializados
✓ Serviços padrão inicializados
...
✅ Banco de dados PostgreSQL inicializado com sucesso!
```

## Estrutura das Tabelas

O script cria as seguintes tabelas:

- `users` - Usuários do painel administrativo
- `site_content` - Conteúdo geral do site (logos, textos, etc.)
- `projects` - Projetos do portfólio
- `services` - Serviços oferecidos
- `pricing` - Planos de preços
- `carousel_slides` - Slides do carrossel principal
- `company_stats` - Estatísticas da empresa
- `client_images` - Imagens de clientes/parceiros
- `feature_tabs` - Abas da seção "Obtenha Mais Conosco"
- `contact_messages` - Mensagens de contato recebidas
- `blog_posts` - Posts do blog (para uso futuro)
- `settings` - Configurações gerais

## Dados Padrão

O script também insere dados padrão:

- **Usuário admin:** `admin` / `admin123` (⚠️ **ALTERE A SENHA APÓS O PRIMEIRO ACESSO!**)
- Conteúdo padrão do site (logos, informações de contato, etc.)
- 3 slides padrão do carrossel
- 3 serviços padrão
- Estatísticas da empresa
- 4 imagens de clientes
- 4 abas "Obtenha Mais Conosco"
- 3 planos de preço
- 8 projetos padrão

## Funcionamento Automático

Após configurar a variável `DATABASE_URL`, o aplicativo Flask detectará automaticamente que deve usar PostgreSQL em vez de SQLite. Não é necessário fazer nenhuma mudança no código - tudo funciona de forma transparente!

## Migração de Dados (Opcional)

Se você já possui dados no SQLite e deseja migrá-los para PostgreSQL, você precisará criar um script de migração personalizado. Por enquanto, o script apenas inicializa o banco com dados padrão.

## Solução de Problemas

### Erro: "module 'psycopg2' not found"

Certifique-se de que o `psycopg2-binary` está no `requirements.txt`:
```
psycopg2-binary==2.9.9
```

### Erro de Conexão

- Verifique se a `DATABASE_URL` está correta
- Certifique-se de que o banco de dados está rodando no Render
- Verifique se não há restrições de firewall bloqueando a conexão

### Erro: "relation already exists"

Isso significa que as tabelas já existem. O script usa `CREATE TABLE IF NOT EXISTS`, então isso não deve causar problemas. Se necessário, você pode executar o script novamente - ele verificará se os dados já existem antes de inserir.

## Importante

⚠️ **TODOS OS DADOS E IMAGENS SÃO ARMAZENADOS NO BANCO DE DADOS POSTGRESQL DO RENDER**

- Isso garante que nenhum dado seja perdido após hibernação
- As imagens são armazenadas como caminhos (paths) no banco de dados
- Os arquivos de imagem devem estar no sistema de arquivos do Render (use Render Disk para persistência)

