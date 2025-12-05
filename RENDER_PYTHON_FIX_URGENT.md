# 🚨 SOLUÇÃO URGENTE: Python 3.13 no Render

## Problema Crítico

O Render está usando **Python 3.13** que **NÃO é compatível** com `psycopg2-binary`. Isso causa:
- ❌ Erro: `undefined symbol: _PyInterpreterState_Get`
- ❌ Aplicação não inicia
- ❌ Perda de dados após hibernação

## ✅ SOLUÇÃO IMEDIATA (Escolha UMA das opções)

### Opção 1: Variável de Ambiente no Render (MAIS RÁPIDO)

1. Acesse: https://dashboard.render.com
2. Vá no serviço **rsdev**
3. Clique em **"Environment"** ou **"Settings"**
4. Adicione variável de ambiente:
   - **Key:** `PYTHON_VERSION`
   - **Value:** `3.12.8`
5. Salve e faça **"Manual Deploy"**

### Opção 2: Clear Build Cache (RECOMENDADO)

1. Acesse: https://dashboard.render.com
2. Vá no serviço **rsdev**
3. Clique no menu **"..."** (três pontos)
4. Selecione **"Clear build cache & deploy"**
5. Aguarde o rebuild (3-5 minutos)

### Opção 3: Configurar no Painel do Render

1. No painel do Render, vá em **Settings** do serviço
2. Procure por **"Python Version"** ou **"Runtime"**
3. Se disponível, defina como **3.12** ou **3.12.8**
4. Salve e faça deploy

## 📋 Arquivos Criados

- ✅ `runtime.txt` → `python-3.12.8`
- ✅ `.python-version` → `3.12.8`

## ✅ Verificação

Após o rebuild, nos logs você deve ver:
```
Using Python version 3.12.8
Successfully installed psycopg2-binary-2.9.9
✓ PostgreSQL inicializado com sucesso!
```

## ⚠️ IMPORTANTE

**NÃO** faça deploy sem resolver o Python 3.13, pois:
- A aplicação não iniciará
- Os dados serão perdidos (SQLite é efêmero)
- PostgreSQL é obrigatório em produção

