import os
import json
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'academic_tracker.db')
JSON_PATH = os.path.join(BASE_DIR, 'dados_fluig.json')
PESOS_CSV_PATH = os.path.join(BASE_DIR, 'pesos.csv')
MANUAIS_CSV_PATH = os.path.join(BASE_DIR, 'notas_manuais.csv')

def ingest_data():
    if not os.path.exists(JSON_PATH):
        print(f"[ERROR] Arquivo de dados não localizado: {JSON_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    avaliacoes = payload.get("data", [])

    for item in avaliacoes:
        cursor.execute('''
            INSERT OR REPLACE INTO materias (id_turma_disc, cod_disc, disciplina, cod_turma, situacao)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            item.get('IDTURMADISC'),
            item.get('CODDISC'),
            item.get('DISCIPLINA'),
            item.get('CODTURMA'),
            item.get('SITUACAO')
        ))

        cursor.execute('''
            INSERT OR REPLACE INTO avaliacoes (id_turma_disc, cod_prova, disciplina, prova, etapa, valor_maximo, nota_obtida, data_prova)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.get('IDTURMADISC'),
            item.get('CODPROVA'),
            item.get('DISCIPLINA'),
            item.get('PROVA'),
            item.get('ETAPA'),
            item.get('VALOR'),
            item.get('NOTA'),
            item.get('DTPROVA')
        ))

    if os.path.exists(PESOS_CSV_PATH):
        df_pesos = pd.read_csv(PESOS_CSV_PATH)
        df_pesos.to_sql('pesos', conn, if_exists='replace', index=False)
        print("[INFO] Tabela de pesos sincronizada via CSV.")
    else:
        print(f"[WARN] Arquivo {PESOS_CSV_PATH} não encontrado.")

    if os.path.exists(MANUAIS_CSV_PATH):
        try:
            df_manuais = pd.read_csv(MANUAIS_CSV_PATH)
            for _, row in df_manuais.iterrows():
                cursor.execute('''
                    INSERT OR REPLACE INTO avaliacoes (id_turma_disc, cod_prova, disciplina, prova, etapa, valor_maximo, nota_obtida, data_prova)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['id_turma_disc'], 
                    row['cod_prova'], 
                    row['disciplina'], 
                    row['prova'],
                    row['etapa'], 
                    row['valor_maximo'], 
                    row['nota_obtida'], 
                    row['data_prova']
                ))
            print("[INFO] Ajustes manuais de notas aplicados com sucesso.")
        except Exception as e:
            print(f"[WARN] Falha ao processar notas manuais: {e}")

    conn.commit()
    conn.close()
    print("[SUCCESS] Carga de dados concluída no banco SQLite.")

if __name__ == '__main__':
    ingest_data()