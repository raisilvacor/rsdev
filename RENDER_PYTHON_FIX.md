# Como Corrigir o Problema de Python 3.13 no Render

## Problema

O Render está usando Python 3.13 que não é compatível com `psycopg2-binary`. O erro é:
```
undefined symbol: _PyInterpreterState_Get
```

## Solução

O arquivo `runtime.txt` foi criado para especificar Python 3.12, mas o Render pode precisar de um **rebuild manual** para aplicar a mudança.

### Opção 1: Rebuild Manual no Render (RECOMENDADO)

1. Acesse o painel do Render: https://dashboard.render.com
2. Vá até seu serviço `rsdev`
3. Clique em **"Manual Deploy"** ou **"Clear Build Cache & Deploy"**
4. Isso forçará o Render a ler o `runtime.txt` e usar Python 3.12

### Opção 2: Configurar Python Version no Painel do Render

1. No painel do Render, vá em **Settings** do seu serviço
2. Na seção **Environment**, procure por **"Python Version"** ou **"Runtime"**
3. Se disponível, defina explicitamente como **Python 3.12**
4. Salve e faça um novo deploy

### Opção 3: Verificar se runtime.txt está no lugar certo

O `runtime.txt` deve estar na **raiz do repositório** (mesmo nível que `app.py`).

### Verificação

Após o rebuild, verifique nos logs se está usando Python 3.12:

```
Using Python version 3.12.x
```

Ou verifique se o erro desapareceu ao acessar `/admin`.

## Status Atual

- ✅ `runtime.txt` criado com `python-3.12`
- ✅ Código de erro melhorado
- ⏳ Aguardando rebuild no Render para aplicar

