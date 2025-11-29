# ⚠️ SOLUÇÃO URGENTE: Rebuild Manual Necessário no Render

## Problema Atual

O Render está usando **Python 3.13** que não é compatível com `psycopg2-binary`. O arquivo `runtime.txt` especifica Python 3.12, mas **não foi aplicado** porque o build foi feito antes do arquivo existir.

## Solução: Rebuild Manual no Render

### Passo 1: Acesse o Painel do Render
1. Vá para: https://dashboard.render.com
2. Faça login na sua conta
3. Encontre o serviço **`rsdev`**

### Passo 2: Limpar Cache e Fazer Rebuild
1. Clique no serviço `rsdev`
2. Vá na aba **"Events"** ou procure por **"Manual Deploy"**
3. Clique no menu **"..."** (três pontos) no canto superior direito
4. Selecione **"Clear build cache & deploy"** ou **"Manual Deploy"**
5. Isso forçará o Render a:
   - ✅ Ler o arquivo `runtime.txt` na raiz do projeto
   - ✅ Usar Python 3.12 em vez de 3.13
   - ✅ Reinstalar todas as dependências corretamente
   - ✅ Instalar psycopg2-binary compatível

### Passo 3: Aguarde o Build
- O build pode levar 3-5 minutos
- Monitore os logs para verificar:
  - `Using Python version 3.12.x` ✅
  - `Successfully installed psycopg2-binary` ✅

### Passo 4: Verifique se Funcionou
Após o rebuild, acesse:
- https://rsdev.onrender.com/admin/
- Deve funcionar sem erro 500

## Verificação

Nos logs do Render, você deve ver:
```
✓ Python 3.12.x detected
✓ psycopg2-binary installed successfully  
✓ PostgreSQL connection working
```

## Alternativa: Configurar Python no Painel do Render

Se o `runtime.txt` não funcionar, tente:

1. No painel do Render, vá em **Settings** do serviço
2. Procure por **"Environment"** ou **"Build & Deploy"**
3. Procure por **"Python Version"** ou campo para especificar runtime
4. Se disponível, defina como **3.12** ou **python-3.12**
5. Salve e faça deploy novamente

## Status Atual

- ✅ `runtime.txt` criado com `python-3.12`
- ✅ Código preparado para usar Python 3.12
- ⏳ **AGUARDANDO REBUILD MANUAL NO RENDER**

**IMPORTANTE:** O rebuild manual é necessário porque o Render não aplicou automaticamente o `runtime.txt` do commit anterior.

