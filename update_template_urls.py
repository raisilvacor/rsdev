"""
Script para atualizar todas as URLs de arquivos estáticos no template
para usar url_for do Flask
"""
import re

def update_template_urls():
    """Atualiza URLs no template para usar url_for"""
    template_path = 'templates/index.html'
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrões para substituir
    replacements = [
        # CSS
        (r'href="css/([^"]+)"', r'href="{{ url_for(\'static\', filename=\'css/\1\') }}"'),
        # JS
        (r'src="js/([^"]+)"', r'src="{{ url_for(\'static\', filename=\'js/\1\') }}"'),
        # Images (src)
        (r'src="images/([^"]+)"', r'src="{{ url_for(\'static\', filename=\'images/\1\') }}"'),
        # Images (href)
        (r'href="images/([^"]+)"', r'href="{{ url_for(\'static\', filename=\'images/\1\') }}"'),
        # Images em data-slide-bg
        (r'data-slide-bg="images/([^"]+)"', r'data-slide-bg="{{ url_for(\'static\', filename=\'images/\1\') }}"'),
        # Images em data-parallax-img
        (r'data-parallax-img="images/([^"]+)"', r'data-parallax-img="{{ url_for(\'static\', filename=\'images/\1\') }}"'),
        # Images em url() no CSS inline
        (r'url\(images/([^)]+)\)', r'url({{ url_for(\'static\', filename=\'images/\1\') }})'),
        # Images em srcset
        (r'srcset="images/([^"]+)"', r'srcset="{{ url_for(\'static\', filename=\'images/\1\') }}"'),
        # Images em data-icon
        (r'data-icon="images/([^"]+)"', r'data-icon="{{ url_for(\'static\', filename=\'images/\1\') }}"'),
        # Images em data-icon-active
        (r'data-icon-active="images/([^"]+)"', r'data-icon-active="{{ url_for(\'static\', filename=\'images/\1\') }}"'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Atualizar action dos formulários
    content = content.replace('action="bat/rd-mailform.php"', 'action="{{ url_for(\'handle_contact_form\') }}"')
    
    # Salvar
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ URLs atualizadas no template!")

if __name__ == '__main__':
    update_template_urls()

