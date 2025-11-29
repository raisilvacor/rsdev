"""Corrige todas as aspas escapadas no template"""
import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Contar antes
count_before = len(re.findall(r"url_for\\(\'", content))
print(f"Ocorrências encontradas: {count_before}")

# Substituir usando regex
# Padrão: url_for(\'static\', filename=\'...\')
content = re.sub(
    r"url_for\\(\'static\', filename=\\'([^\']+)\'\\)",
    r"url_for('static', filename='\1')",
    content
)

# Padrão: url_for(\'handle_contact_form\')
content = re.sub(
    r"url_for\\(\'handle_contact_form\'\\)",
    r"url_for('handle_contact_form')",
    content
)

# Contar depois
count_after = len(re.findall(r"url_for\\(\'", content))
print(f"Ocorrências restantes: {count_after}")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

if count_after == 0:
    print("✓ Todas as aspas foram corrigidas!")
else:
    print(f"⚠ Ainda restam {count_after} ocorrências")

