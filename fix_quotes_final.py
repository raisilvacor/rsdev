"""Corrige todas as aspas escapadas no template"""
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir todas as ocorrências
# url_for(\'static\', filename=\'...\') -> url_for('static', filename='...')
old_pattern = "url_for(\\'static\\', filename=\\'"
new_pattern = "url_for('static', filename='"
content = content.replace(old_pattern, new_pattern)

# url_for(\'handle_contact_form\') -> url_for('handle_contact_form')
old_pattern2 = "url_for(\\'handle_contact_form\\')"
new_pattern2 = "url_for('handle_contact_form')"
content = content.replace(old_pattern2, new_pattern2)

# Verificar se ainda há problemas
if "url_for(\\'" in content:
    print("Aviso: Ainda há ocorrências com escape!")
    # Tentar uma abordagem mais agressiva
    import re
    # Substituir qualquer url_for(\'...\')
    content = re.sub(r"url_for\\(\'([^\']+)\'\\)", r"url_for('\1')", content)
    # Substituir url_for(\'static\', filename=\'...\')
    content = re.sub(r"url_for\\(\'static\', filename=\\'([^\']+)\'\\)", r"url_for('static', filename='\1')", content)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Aspas corrigidas!")
print(f"Verificação: {'url_for(\\'' in content and 'PROBLEMA!' or 'OK'}")

