"""Corrige aspas de fechamento com escape incorreto"""
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Corrigir fechamentos com escape
content = content.replace("\\')", "')")
content = content.replace("\\')", "')")  # Dupla verificação

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Aspas de fechamento corrigidas!")

