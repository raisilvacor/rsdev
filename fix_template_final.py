"""Corrige todas as aspas escapadas no template usando substituição simples"""
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Contar antes
count_before = content.count("url_for(\\'")
print(f"Ocorrências encontradas: {count_before}")

# Substituir diretamente - método mais simples e confiável
# Substituir url_for(\'static\', filename=\' por url_for('static', filename='
while "url_for(\\'static\\', filename=\\'" in content:
    content = content.replace("url_for(\\'static\\', filename=\\'", "url_for('static', filename='")

# Substituir url_for(\'handle_contact_form\') por url_for('handle_contact_form')
while "url_for(\\'handle_contact_form\\')" in content:
    content = content.replace("url_for(\\'handle_contact_form\\')", "url_for('handle_contact_form')")

# Contar depois
count_after = content.count("url_for(\\'")
print(f"Ocorrências restantes: {count_after}")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

if count_after == 0:
    print("✓ Todas as aspas foram corrigidas!")
else:
    print(f"⚠ Ainda restam {count_after} ocorrências")
    # Mostrar algumas linhas problemáticas
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if "url_for(\\'" in line:
            print(f"  Linha {i}: {line[:80]}...")

