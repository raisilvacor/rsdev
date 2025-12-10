# 🔐 Reset de Senha do Admin

Este guia explica como resetar a senha do usuário admin caso você tenha esquecido.

## 📋 Informações Padrão

**Credenciais padrão do sistema:**
- **Usuário:** `admin`
- **Senha:** `admin123`

## 🚀 Como Resetar a Senha

### Opção 1: Usar o Script Automático (Recomendado)

Execute o script `reset_admin_password.py`:

```bash
# Resetar para senha padrão (admin123)
python reset_admin_password.py

# Definir uma nova senha personalizada
python reset_admin_password.py minhaNovaSenha123

# Resetar senha de um usuário específico
python reset_admin_password.py novaSenha nomeUsuario

# Listar todos os usuários
python reset_admin_password.py --list
```

### Opção 2: Reset Manual via SQL

#### Para SQLite (desenvolvimento local):

```bash
# Abrir o banco SQLite
sqlite3 site_content.db

# Ver usuários existentes
SELECT id, username FROM users;

# Resetar senha do admin (substitua 'nova_senha_hash' pelo hash gerado)
UPDATE users SET password = 'nova_senha_hash' WHERE username = 'admin';
```

Para gerar o hash da senha, use Python:
```python
from werkzeug.security import generate_password_hash
print(generate_password_hash('sua_senha'))
```

#### Para PostgreSQL (produção):

```bash
# Conectar ao banco PostgreSQL
psql $DATABASE_URL

# Ver usuários existentes
SELECT id, username FROM users;

# Resetar senha do admin
UPDATE users SET password = 'nova_senha_hash' WHERE username = 'admin';
```

## ⚠️ Importante

1. **Altere a senha padrão em produção!** A senha `admin123` é apenas para desenvolvimento.

2. **O script funciona automaticamente** com SQLite e PostgreSQL - ele detecta qual banco está sendo usado.

3. **Após resetar**, faça login e altere a senha através do painel administrativo.

## 🔍 Verificar Usuários Existentes

Para ver todos os usuários cadastrados:

```bash
python reset_admin_password.py --list
```

## 📝 Exemplos de Uso

```bash
# Resetar para senha padrão
python reset_admin_password.py

# Criar nova senha forte
python reset_admin_password.py MinhaSenh@Segura123!

# Resetar outro usuário
python reset_admin_password.py novaSenha outroUsuario
```

## 🆘 Problemas Comuns

### Erro: "Usuário não encontrado"
- O script criará automaticamente um novo usuário admin se não existir.

### Erro: "Não foi possível conectar ao banco"
- Verifique se o banco de dados está acessível
- Para PostgreSQL, verifique a variável de ambiente `DATABASE_URL`
- Para SQLite, verifique se o arquivo `site_content.db` existe

### Erro: "Módulo não encontrado"
- Certifique-se de ter instalado as dependências: `pip install -r requirements.txt`

