"""
Script para resetar a senha do usuário admin
Uso: python reset_admin_password.py [nova_senha]
Se não fornecer uma senha, será usada a senha padrão: admin123
"""
import os
import sys
from werkzeug.security import generate_password_hash
from db_connection import get_db

def reset_admin_password(new_password='admin123', username='admin'):
    """
    Reseta a senha do usuário admin no banco de dados
    
    Args:
        new_password: Nova senha (padrão: admin123)
        username: Nome do usuário (padrão: admin)
    """
    try:
        print(f"🔄 Conectando ao banco de dados...")
        conn = get_db()
        
        # Verificar se o usuário existe
        cursor = conn.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Erro: Usuário '{username}' não encontrado no banco de dados!")
            print(f"💡 Criando novo usuário admin...")
            # Criar novo usuário admin
            password_hash = generate_password_hash(new_password)
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                        (username, password_hash))
            conn.commit()
            print(f"✅ Usuário '{username}' criado com sucesso!")
        else:
            print(f"✅ Usuário '{username}' encontrado!")
            print(f"🔄 Atualizando senha...")
            # Atualizar senha
            password_hash = generate_password_hash(new_password)
            conn.execute('UPDATE users SET password = ? WHERE username = ?', 
                        (password_hash, username))
            conn.commit()
            print(f"✅ Senha atualizada com sucesso!")
        
        conn.close()
        
        print(f"\n{'='*50}")
        print(f"✅ RESET CONCLUÍDO!")
        print(f"{'='*50}")
        print(f"👤 Usuário: {username}")
        print(f"🔑 Nova senha: {new_password}")
        print(f"{'='*50}")
        print(f"\n💡 Você pode fazer login agora com essas credenciais.")
        print(f"⚠️  IMPORTANTE: Altere a senha após fazer login!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao resetar senha: {e}")
        import traceback
        traceback.print_exc()
        return False

def list_users():
    """Lista todos os usuários no banco de dados"""
    try:
        print(f"🔄 Conectando ao banco de dados...")
        conn = get_db()
        
        cursor = conn.execute('SELECT id, username FROM users')
        users = cursor.fetchall()
        
        if users:
            print(f"\n{'='*50}")
            print(f"👥 USUÁRIOS NO BANCO DE DADOS:")
            print(f"{'='*50}")
            for user in users:
                print(f"  ID: {user['id']} | Usuário: {user['username']}")
            print(f"{'='*50}\n")
        else:
            print(f"⚠️  Nenhum usuário encontrado no banco de dados.")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print(f"\n{'='*50}")
    print(f"🔐 RESET DE SENHA DO ADMIN")
    print(f"{'='*50}\n")
    
    # Verificar argumentos
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            print("Uso: python reset_admin_password.py [nova_senha] [username]")
            print("\nOpções:")
            print("  nova_senha  - Nova senha para o admin (padrão: admin123)")
            print("  username    - Nome do usuário (padrão: admin)")
            print("  --list      - Lista todos os usuários")
            print("\nExemplos:")
            print("  python reset_admin_password.py")
            print("  python reset_admin_password.py minhaNovaSenha123")
            print("  python reset_admin_password.py minhaSenha admin")
            print("  python reset_admin_password.py --list")
            sys.exit(0)
        elif sys.argv[1] == '--list':
            list_users()
            sys.exit(0)
        else:
            new_password = sys.argv[1]
            username = sys.argv[2] if len(sys.argv) > 2 else 'admin'
    else:
        new_password = 'admin123'
        username = 'admin'
        print(f"💡 Usando senha padrão: admin123")
        print(f"💡 Para definir uma senha personalizada, use: python reset_admin_password.py sua_senha\n")
    
    # Confirmar ação
    print(f"⚠️  Você está prestes a resetar a senha do usuário '{username}'")
    if new_password == 'admin123':
        print(f"⚠️  A senha será definida como 'admin123' (padrão)")
    
    response = input(f"\n❓ Continuar? (s/N): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print(f"❌ Operação cancelada.")
        sys.exit(0)
    
    # Resetar senha
    success = reset_admin_password(new_password, username)
    
    if not success:
        sys.exit(1)

