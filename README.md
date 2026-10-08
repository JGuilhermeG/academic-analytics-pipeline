# Academic Performance Tracker & Analytics Pipeline

Pipeline automatizado em Python para extração, normalização, modelagem relacional (SQLite) e geração de diagnósticos analíticos de desempenho acadêmico com suporte a IA generativa.

## 📌 Funcionalidades

- **Modelagem Relacional (SQLite):** Normalização de disciplinas, notas, pesos e regras de substituição via CTEs e Window Functions em SQL.
- **Ingestão Flexível:** Carga automatizada a partir de payloads JSON e suporte a sobreposições (*overrides*) via arquivos CSV.
- **Relatórios Automatizados:** Exportação de dados consolidados e formatados em planilhas Excel (`openpyxl`).
- **Diagnóstico com LLM:** Integração com o Google Gemini API para análise contextual de gaps de nota e priorização de estudos.

## 🚀 Tecnologias

- Python 3.10+
- SQLite3
- Pandas
- OpenPyXL
- Google GenAI SDK

## ⚙️ Como Executar

### 1. Clonar repositório e preparar ambiente
```bash
git clone https://github.com/JGuilhermeG/academic-analytics-pipeline.git
cd academic-analytics-pipeline
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente
Crie um arquivo `.env` na raiz baseado no `.env.example`:
```env
GEMINI_API_KEY=sua_chave_aqui
```

### 3. Execução do pipeline
```bash
# 1. Cria as tabelas no banco de dados
python src/DataBase.py

# 2. Ingestão dos dados do JSON e tabelas de pesos
python src/GetDados.py

# 3. Consulta rápida no terminal
python src/Analytics.py

# 4. Geração da planilha Excel formatada
python src/GerarRelatorio_Excel.py

# 5. Geração de diagnóstico analítico via IA
python src/GerarDiagnostico_IA.py
```