"""Corrige todas as aspas escapadas incorretamente no template"""
import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Contar ocorrências antes
before = content.count("url_for(\\'")
print(f"Encontradas {before} ocorrências com escape incorreto")

# Corrigir todas as ocorrências de url_for com escape incorreto
# Padrão: url_for(\'static\', filename=\'...\')
content = re.sub(
    r"url_for\\(\'static\', filename=\'([^\']+)\'\\)",
    r"url_for('static', filename='\1')",
    content
)

# Corrigir também url_for(\'handle_contact_form\')
content = re.sub(
    r"url_for\\(\'([^\']+)\'\\)",
    r"url_for('\1')",
    content
)

# Contar ocorrências depois
after = content.count("url_for(\\'")
print(f"Restam {after} ocorrências com escape incorreto")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Todas as aspas corrigidas!")

