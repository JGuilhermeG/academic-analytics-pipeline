import os
import time
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY não definida no arquivo .env.")

client = genai.Client(api_key=api_key)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'academic_tracker.db')

QUERY_DESEMPENHO = '''
WITH notas_pivot AS (
    SELECT 
        m.cod_disc, m.disciplina, 6.0 as meta_aprovacao, 
        MAX(CASE WHEN a.prova = 'P1' THEN a.nota_obtida END) as P1,
        MAX(CASE WHEN a.prova = 'P2' THEN a.nota_obtida END) as P2,
        MAX(CASE WHEN a.prova = 'P3' THEN a.nota_obtida END) as P3,
        MAX(CASE WHEN a.prova = 'P4' THEN a.nota_obtida END) as P4,
        MAX(CASE WHEN a.prova = 'SUB1' THEN a.nota_obtida END) as SUB1,
        MAX(CASE WHEN a.prova = 'SUB2' THEN a.nota_obtida END) as SUB2,
        MAX(CASE WHEN a.prova = 'T1' THEN a.nota_obtida END) as T1,
        MAX(CASE WHEN a.prova = 'T2' THEN a.nota_obtida END) as T2,
        MAX(CASE WHEN a.prova = 'T3' THEN a.nota_obtida END) as T3,
        MAX(CASE WHEN a.prova = 'T4' THEN a.nota_obtida END) as T4
    FROM materias m
    LEFT JOIN avaliacoes a ON m.id_turma_disc = a.id_turma_disc
    WHERE m.cod_disc IS NOT NULL
    GROUP BY m.cod_disc, m.disciplina
),
notas_substituidas AS (
    SELECT
        cod_disc, disciplina, meta_aprovacao,
        MAX(COALESCE(P1, 0), COALESCE(SUB1, 0)) as P1_final,
        MAX(COALESCE(P2, 0), COALESCE(SUB1, 0)) as P2_final,
        MAX(COALESCE(P3, 0), COALESCE(SUB2, 0)) as P3_final,
        MAX(COALESCE(P4, 0), COALESCE(SUB2, 0)) as P4_final,
        COALESCE(T1, 0) as T1_final,
        COALESCE(T2, 0) as T2_final,
        COALESCE(T3, 0) as T3_final,
        COALESCE(T4, 0) as T4_final
    FROM notas_pivot
)
SELECT 
    ns.cod_disc, ns.disciplina, ns.meta_aprovacao,
    ROUND((ns.P1_final * COALESCE(p.peso_p1, 0)) + (ns.P2_final * COALESCE(p.peso_p2, 0)) + (ns.P3_final * COALESCE(p.peso_p3, 0)) + (ns.P4_final * COALESCE(p.peso_p4, 0)) + (ns.T1_final * COALESCE(p.peso_t1, 0)) + (ns.T2_final * COALESCE(p.peso_t2, 0)) + (ns.T3_final * COALESCE(p.peso_t3, 0)) + (ns.T4_final * COALESCE(p.peso_t4, 0)), 2) as nota_final_ponderada,
    CASE 
        WHEN ROUND((ns.P1_final * COALESCE(p.peso_p1, 0)) + (ns.P2_final * COALESCE(p.peso_p2, 0)) + (ns.P3_final * COALESCE(p.peso_p3, 0)) + (ns.P4_final * COALESCE(p.peso_p4, 0)) + (ns.T1_final * COALESCE(p.peso_t1, 0)) + (ns.T2_final * COALESCE(p.peso_t2, 0)) + (ns.T3_final * COALESCE(p.peso_t3, 0)) + (ns.T4_final * COALESCE(p.peso_t4, 0)), 2) >= ns.meta_aprovacao THEN 'Aprovado'
        ELSE 'Faltam ' || ROUND(ns.meta_aprovacao - ((ns.P1_final * COALESCE(p.peso_p1, 0)) + (ns.P2_final * COALESCE(p.peso_p2, 0)) + (ns.P3_final * COALESCE(p.peso_p3, 0)) + (ns.P4_final * COALESCE(p.peso_p4, 0)) + (ns.T1_final * COALESCE(p.peso_t1, 0)) + (ns.T2_final * COALESCE(p.peso_t2, 0)) + (ns.T3_final * COALESCE(p.peso_t3, 0)) + (ns.T4_final * COALESCE(p.peso_t4, 0))), 2) || ' pts'
    END as status
FROM notas_substituidas ns
LEFT JOIN pesos p ON ns.cod_disc = p.cod_disc;
'''

def gerar_diagnostico():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(QUERY_DESEMPENHO, conn)
    conn.close()

    dados_em_texto = df.to_string(index=False)

    prompt = f"""
Atue como consultor analítico educacional. Analise a tabela de desempenho acadêmico abaixo:

{dados_em_texto}

Estruture a resposta com:
1. Resumo Executivo: Visão geral da performance no período.
2. Análise de Risco: Disciplinas com maior déficit em relação à meta de aprovação (6.0) e recomendação de prioridade.
3. Plano de Ação: Próximos passos operacionais focados em recuperação de notas.
"""

    print("[INFO] Enviando dados para processamento no Gemini...")
    max_tentativas = 3
    for tentativa in range(max_tentativas):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            print("\n" + "="*70)
            print(" DIAGNÓSTICO ANALÍTICO - GEMINI")
            print("="*70)
            print(response.text)
            print("="*70)
            return
        except Exception as e:
            if '503' in str(e):
                print(f"[WARN] Serviço indisponível temporariamente. Tentativa {tentativa + 1} de {max_tentativas}. Aguardando 5s...")
                time.sleep(5)
            else:
                print(f"[ERROR] Erro na requisição: {e}")
                break

if __name__ == '__main__':
    gerar_diagnostico()