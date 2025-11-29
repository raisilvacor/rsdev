"""
Módulo para gerenciar conexões com banco de dados
Suporta SQLite (desenvolvimento) e PostgreSQL (produção)
"""
import os
import sqlite3

# Classe para compatibilidade de Row entre SQLite e PostgreSQL
class CompatRow:
    """Wrapper para tornar dicionários do PostgreSQL compatíveis com sqlite3.Row"""
    def __init__(self, row_dict):
        if isinstance(row_dict, dict):
            self._dict = row_dict
        else:
            # Se já for um objeto row-like, tentar converter
            self._dict = dict(row_dict) if hasattr(row_dict, 'keys') else {}
    
    def __getitem__(self, key):
        return self._dict[key]
    
    def __getattr__(self, key):
        return self._dict.get(key)
    
    def keys(self):
        return self._dict.keys()
    
    def __contains__(self, key):
        return key in self._dict
    
    def get(self, key, default=None):
        return self._dict.get(key, default)
    
    def __iter__(self):
        return iter(self._dict.values())
    
    def __repr__(self):
        return f"CompatRow({self._dict})"

def get_db():
    """
    Obtém conexão com o banco de dados.
    Usa PostgreSQL se DATABASE_URL estiver definido, caso contrário usa SQLite.
    
    Retorna uma conexão compatível com sqlite3.
    """
    database_url = os.environ.get('DATABASE_URL')
    
    # Tentar usar PostgreSQL se DATABASE_URL estiver definido
    psycopg2_module = None
    RealDictCursor_class = None
    
    if database_url:
        # Tentar importar psycopg2
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            # Armazenar referências aos módulos importados
            psycopg2_module = psycopg2
            RealDictCursor_class = RealDictCursor
        except ImportError as e:
            # Se psycopg2 não pode ser importado (ex: Python 3.13 incompatível),
            # fazer fallback para SQLite com aviso nos logs
            import sys
            print(f"⚠️ AVISO CRÍTICO: Não foi possível importar psycopg2. Erro: {e}", file=sys.stderr)
            print(f"⚠️ Isso geralmente acontece quando psycopg2-binary não é compatível com Python 3.13.", file=sys.stderr)
            print(f"⚠️ SOLUÇÃO: No painel do Render, faça 'Clear Build Cache & Deploy' para aplicar runtime.txt", file=sys.stderr)
            print(f"⚠️ Usando SQLite como fallback temporário...", file=sys.stderr)
            psycopg2_module = None
            RealDictCursor_class = None
    
    # Se psycopg2 foi importado com sucesso e DATABASE_URL está definido, usar PostgreSQL
    if psycopg2_module is not None and database_url:
        # Converter URL do formato postgres:// para postgresql:// se necessário
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        # Usar as referências aos módulos importados com sucesso
        conn = psycopg2_module.connect(database_url, sslmode='require')
        
        # Criar uma classe wrapper para a conexão PostgreSQL
        class PostgresConnection:
            def __init__(self, pg_conn):
                self._conn = pg_conn
                self.row_factory = None  # Para compatibilidade
            
            def cursor(self):
                return PostgresCursor(self._conn.cursor(cursor_factory=RealDictCursor_class))
            
            def commit(self):
                return self._conn.commit()
            
            def rollback(self):
                return self._conn.rollback()
            
            def close(self):
                return self._conn.close()
            
            def execute(self, query, params=None):
                """Método de conveniência para executar queries diretamente"""
                cursor = self.cursor()
                # Converter ? para %s
                if '?' in query:
                    query = query.replace('?', '%s')
                cursor.execute(query, params)
                return cursor
        
        class PostgresCursor:
            def __init__(self, pg_cursor):
                self._cursor = pg_cursor
            
            def execute(self, query, params=None):
                # Converter ? para %s para PostgreSQL
                if '?' in query:
                    query = query.replace('?', '%s')
                if params:
                    self._cursor.execute(query, params)
                else:
                    self._cursor.execute(query)
                return self
            
            def fetchone(self):
                row = self._cursor.fetchone()
                return CompatRow(row) if row else None
            
            def fetchall(self):
                rows = self._cursor.fetchall()
                return [CompatRow(row) for row in rows] if rows else []
            
            def fetchmany(self, size=None):
                rows = self._cursor.fetchmany(size)
                return [CompatRow(row) for row in rows] if rows else []
            
            def close(self):
                return self._cursor.close()
            
            @property
            def rowcount(self):
                return self._cursor.rowcount
        
        return PostgresConnection(conn)
    else:
        # SQLite (desenvolvimento ou fallback)
        DB_PATH = 'site_content.db'
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
