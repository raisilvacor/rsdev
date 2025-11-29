"""
Módulo para gerenciar armazenamento de imagens no banco de dados PostgreSQL
Garante persistência no Render Free (que tem sistema de arquivos efêmero)
"""
import os
from db_connection import get_db
from datetime import datetime
from werkzeug.utils import secure_filename

def save_image_to_db(image_file, image_key=None, category='images'):
    """
    Salva uma imagem no banco de dados PostgreSQL como BYTEA.
    
    Em produção (USE_DB_IMAGE_STORAGE=True ou DATABASE_URL definido):
    - Sempre salva no banco, retorna image_key ou None se falhar
    
    Em desenvolvimento (USE_DB_IMAGE_STORAGE=False e sem DATABASE_URL):
    - Tenta salvar no banco, mas pode retornar None se não houver banco configurado
    
    Args:
        image_file: Arquivo de imagem (Werkzeug FileStorage)
        image_key: Chave única para identificar a imagem (opcional, será gerada se não fornecida)
        category: Categoria da imagem (logos, banners, images)
    
    Returns:
        image_key: Chave única da imagem salva, ou None se falhar
    """
    if not image_file or not image_file.filename:
        return None
    
    # Verificar se deve usar banco de dados usando função centralizada
    from image_config import should_use_db_storage
    must_use_db = should_use_db_storage()
    has_database_url = bool(os.environ.get('DATABASE_URL'))
    
    # Se não deve usar banco e não tem DATABASE_URL, retornar None (fallback para arquivo)
    if not must_use_db and not has_database_url:
        # Em desenvolvimento sem DATABASE_URL e sem flag, não tentar salvar no banco
        return None
    
    # Tentar conectar ao banco (PostgreSQL ou SQLite)
    try:
        conn = get_db()
    except Exception as e:
        if must_use_db:
            # Em produção, não pode falhar
            print(f"❌ ERRO CRÍTICO: Não foi possível conectar ao banco em produção: {e}")
            raise
        # Em desenvolvimento, pode retornar None para usar fallback
        print(f"⚠️ Aviso: Não foi possível conectar ao banco: {e}")
        return None
    try:
        # Detectar qual banco está sendo usado: PostgreSQL wrapper tem _conn, SQLite não tem
        is_postgres_connection = hasattr(conn, '_conn')
        
        # Verificar se a tabela stored_images existe
        c = conn.cursor()
        try:
            # Tentar verificar se a tabela existe
            if is_postgres_connection:
                # PostgreSQL
                query = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='stored_images')"
                c.execute(query)
                table_exists = c.fetchone()
                table_exists = table_exists[0] if isinstance(table_exists, (tuple, list)) else False
            else:
                # SQLite
                c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stored_images'")
                table_exists = c.fetchone() is not None
        except:
            table_exists = False
        
        if not table_exists:
            print("⚠️ Tabela stored_images não existe. Criando...")
            # Criar tabela se não existir - usar detecção dinâmica
            if is_postgres_connection:
                # PostgreSQL
                c.execute('''
                    CREATE TABLE IF NOT EXISTS stored_images (
                        id SERIAL PRIMARY KEY,
                        image_key VARCHAR(500) UNIQUE NOT NULL,
                        image_data BYTEA NOT NULL,
                        mime_type VARCHAR(100) NOT NULL,
                        filename VARCHAR(255) NOT NULL,
                        file_size INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                c.execute('CREATE INDEX IF NOT EXISTS idx_stored_images_key ON stored_images(image_key)')
            else:
                # SQLite
                c.execute('''
                    CREATE TABLE IF NOT EXISTS stored_images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        image_key TEXT UNIQUE NOT NULL,
                        image_data BLOB NOT NULL,
                        mime_type TEXT NOT NULL,
                        filename TEXT NOT NULL,
                        file_size INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                try:
                    c.execute('CREATE INDEX IF NOT EXISTS idx_stored_images_key ON stored_images(image_key)')
                except:
                    pass
            conn.commit()
            print("✓ Tabela stored_images criada com sucesso!")
        
        # Ler dados binários da imagem
        image_file.seek(0)
        image_data = image_file.read()
        image_file.seek(0)  # Reset para possível reuso
        
        # Detectar MIME type
        filename = secure_filename(image_file.filename)
        mime_type = image_file.content_type or 'image/png'
        
        # Gerar image_key se não fornecido
        if not image_key:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_key = f"{category}/{timestamp}_{filename}"
        
        # Detectar dinamicamente qual banco está sendo usado
        # PostgreSQL wrapper do db_connection tem _conn, SQLite não tem
        is_postgres = hasattr(conn, '_conn')
        
        file_size = len(image_data) if isinstance(image_data, (bytes, bytearray)) else len(bytes(image_data)) if image_data else 0
        
        if is_postgres:
            # PostgreSQL: usar psycopg2.Binary para BYTEA
            try:
                import psycopg2
                image_data_binary = psycopg2.Binary(image_data)
            except ImportError:
                # Se psycopg2 não estiver disponível, usar bytes direto
                image_data_binary = image_data
            
            # PostgreSQL usa %s e ON CONFLICT funciona nativamente
            query = '''INSERT INTO stored_images (image_key, image_data, mime_type, filename, file_size, updated_at)
                       VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                       ON CONFLICT (image_key) DO UPDATE
                       SET image_data = EXCLUDED.image_data,
                           mime_type = EXCLUDED.mime_type,
                           filename = EXCLUDED.filename,
                           file_size = EXCLUDED.file_size,
                           updated_at = CURRENT_TIMESTAMP'''
            c.execute(query, (image_key, image_data_binary, mime_type, filename, file_size))
        else:
            # SQLite usa ? e INSERT OR REPLACE
            query = '''INSERT OR REPLACE INTO stored_images (image_key, image_data, mime_type, filename, file_size, updated_at)
                       VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'''
            c.execute(query, (image_key, image_data, mime_type, filename, file_size))
        
        conn.commit()
        print(f"✓ Imagem salva no banco: {image_key} ({file_size} bytes)")
        return image_key
    except Exception as e:
        if 'conn' in locals():
            try:
                conn.rollback()
            except:
                pass
        error_msg = f"Erro ao salvar imagem no banco: {e}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        
        # Se deve usar banco obrigatoriamente, re-raise o erro
        if must_use_db:
            raise Exception(f"Falha crítica ao salvar imagem no banco: {e}") from e
        
        return None
    finally:
        if 'conn' in locals():
            try:
                conn.close()
            except:
                pass

def get_image_from_db(image_key):
    """
    Recupera uma imagem do banco de dados.
    
    Args:
        image_key: Chave única da imagem
    
    Returns:
        tuple: (image_data, mime_type, filename) ou (None, None, None) se não encontrada
    """
    if not image_key:
        return None, None, None
    
    conn = get_db()
    try:
        c = conn.cursor()
        
        # Detectar qual banco está sendo usado dinamicamente
        is_postgres = hasattr(conn, '_conn')
        
        # Adaptar query para PostgreSQL ou SQLite
        if is_postgres:
            query = 'SELECT image_data, mime_type, filename FROM stored_images WHERE image_key = %s'
        else:
            query = 'SELECT image_data, mime_type, filename FROM stored_images WHERE image_key = ?'
        
        row = c.execute(query, (image_key,)).fetchone()
        
        if row:
            # Acessar valores da row
            if hasattr(row, 'get'):
                image_data = row.get('image_data')
                mime_type = row.get('mime_type')
                filename = row.get('filename')
            else:
                image_data = row['image_data'] if 'image_data' in row else row[0]
                mime_type = row['mime_type'] if 'mime_type' in row else row[1]
                filename = row['filename'] if 'filename' in row else row[2]
            
            return image_data, mime_type, filename
        else:
            return None, None, None
    except Exception as e:
        print(f"Erro ao recuperar imagem do banco: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None
    finally:
        conn.close()

def delete_image_from_db(image_key):
    """
    Remove uma imagem do banco de dados.
    
    Args:
        image_key: Chave única da imagem
    
    Returns:
        bool: True se removida com sucesso, False caso contrário
    """
    if not image_key:
        return False
    
    conn = get_db()
    try:
        c = conn.cursor()
        
        # Detectar qual banco está sendo usado dinamicamente
        is_postgres = hasattr(conn, '_conn')
        
        # Adaptar query para PostgreSQL ou SQLite
        if is_postgres:
            query = 'DELETE FROM stored_images WHERE image_key = %s'
        else:
            query = 'DELETE FROM stored_images WHERE image_key = ?'
        
        c.execute(query, (image_key,))
        conn.commit()
        
        return c.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Erro ao remover imagem do banco: {e}")
        return False
    finally:
        conn.close()

def image_exists_in_db(image_key):
    """
    Verifica se uma imagem existe no banco de dados.
    
    Args:
        image_key: Chave única da imagem
    
    Returns:
        bool: True se existe, False caso contrário
    """
    if not image_key:
        return False
    
    conn = get_db()
    try:
        c = conn.cursor()
        
        # Detectar qual banco está sendo usado dinamicamente
        is_postgres = hasattr(conn, '_conn')
        
        # Adaptar query para PostgreSQL ou SQLite
        if is_postgres:
            query = 'SELECT COUNT(*) FROM stored_images WHERE image_key = %s'
        else:
            query = 'SELECT COUNT(*) FROM stored_images WHERE image_key = ?'
        
        row = c.execute(query, (image_key,)).fetchone()
        
        if row:
            count = row[0] if isinstance(row, (tuple, list)) else row.get('count', 0) if hasattr(row, 'get') else row['count']
            return count > 0
        return False
    except Exception as e:
        print(f"Erro ao verificar imagem no banco: {e}")
        return False
    finally:
        conn.close()

