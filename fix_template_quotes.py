"""Corrige aspas escapadas incorretamente no template"""
import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Corrigir url_for com escape incorreto
content = re.sub(
    r"url_for\\(\'static\', filename=\'([^\']+)\'\\)",
    r"url_for('static', filename='\1')",
    content
)

# Corrigir action dos formulários
content = content.replace(
    'action="{{ url_for(\'handle_contact_form\') }}"',
    "action=\"{{ url_for('handle_contact_form') }}\""
)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Aspas corrigidas!")

