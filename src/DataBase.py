import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'academic_tracker.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS materias (
        id_turma_disc INTEGER PRIMARY KEY,
        cod_disc TEXT,
        disciplina TEXT,
        cod_turma TEXT,
        situacao TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS avaliacoes (
        id_turma_disc INTEGER,
        cod_prova INTEGER,
        disciplina TEXT,
        prova TEXT,
        etapa TEXT,
        valor_maximo REAL,
        nota_obtida REAL,
        data_prova TEXT,
        PRIMARY KEY (id_turma_disc, prova),
        FOREIGN KEY (id_turma_disc) REFERENCES materias (id_turma_disc)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS historico_alertas (
        id_alerta INTEGER PRIMARY KEY AUTOINCREMENT,
        id_turma_disc INTEGER,
        cod_prova INTEGER,
        nota_nova REAL,
        data_alerta DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pesos (
        cod_disc TEXT PRIMARY KEY,
        peso_p1 REAL DEFAULT 0,
        peso_p2 REAL DEFAULT 0,
        peso_p3 REAL DEFAULT 0,
        peso_p4 REAL DEFAULT 0,
        peso_t1 REAL DEFAULT 0,
        peso_t2 REAL DEFAULT 0,
        peso_t3 REAL DEFAULT 0,
        peso_t4 REAL DEFAULT 0
    )
    ''')

    conn.commit()
    conn.close()
    print(f"[INFO] Esquema do banco de dados inicializado em: {DB_PATH}")

if __name__ == '__main__':
    init_db()