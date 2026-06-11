import spacy
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import render_template
import pandas as pd
import json
from pathlib import Path
import subprocess

app = Flask(__name__, template_folder="/app/scripts/templates")
CORS(app)

# --- CONFIGURAÇÕES DE CAMINHOS E DADOS ---
BASE_DIR = Path("/app")
RAW_DIR = BASE_DIR / "data" / "raw" / "csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

csv_files = list(RAW_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(f"Nenhum arquivo CSV encontrado em: {RAW_DIR}")
  
DATA_PATH = csv_files[0]

OUTPUT_PATH = PROCESSED_DIR / "json" / "dataset_rotulado.json"
OUTPUT_PATH_NER = BASE_DIR / "ner" / "data" / "raw" / "json" / "dataset_rotulado.json"
PULADOS_PATH = PROCESSED_DIR / "json" / "dataset_pulados.json"

MODELS_BASE_DIR = BASE_DIR / "models"
model_folders = list(MODELS_BASE_DIR.glob("*/model-best"))

if model_folders:
    MODEL_PATH = model_folders[0]
else:
    MODEL_PATH = None
    print("Aviso: Nenhum modelo 'model-best' encontrado em /models")

try:
    if MODEL_PATH and MODEL_PATH.exists():
        nlp = spacy.load(str(MODEL_PATH))
        print(f"Modelo carregado com sucesso de: {MODEL_PATH}")
    else:
        raise OSError("Caminho do modelo não definido ou inexistente.")
except Exception as e:
    print(f"Erro ao carregar modelo: {e}")
    nlp = None

# Carregamento do CSV original
df = pd.read_csv(DATA_PATH, sep=";")

# --- INICIALIZAÇÃO DOS ARQUIVOS ---
def inicializar_arquivos():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH_NER.parent.mkdir(parents=True, exist_ok=True)
    
    if not OUTPUT_PATH.exists():
        with open(OUTPUT_PATH, "w", encoding="utf8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
            
    if not OUTPUT_PATH_NER.exists():
        with open(OUTPUT_PATH_NER, "w", encoding="utf8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
            
    if not PULADOS_PATH.exists():
        with open(PULADOS_PATH, "w", encoding="utf8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

inicializar_arquivos()

# --- FUNÇÕES AUXILIARES ---
def ler_json():
    try:
        with open(OUTPUT_PATH, "r", encoding="utf8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

# --- ROTA: BUSCAR TEXTOS (COM SUGESTÕES DA IA) ---
@app.route("/")
def index():
    return render_template("index_ner.html")
  
@app.route("/textos", methods=["GET"])
def get_textos():
    dados = ler_json()
    ids_rotulados = [d["id_descricao"] for d in dados]
    
    # Lê os pulados
    try:
        with open(PULADOS_PATH, "r", encoding="utf8") as f:
            ids_pulados = json.load(f)
    except:
        ids_pulados = []
    
    lista_textos = df[["id_descricao", "id_mensagem", "ordem_parte", "descricao"]].to_dict(orient="records")

    return jsonify({
        "textos": lista_textos,
        "ids_feitos": ids_rotulados,
        "ids_pulados": ids_pulados,
        "anotacoes_salvas": dados
    })

@app.route("/pular", methods=["POST"])
def salvar_pulado():
    dados_req = request.json
    id_descricao = dados_req.get("id_descricao")
    
    try:
        with open(PULADOS_PATH, "r", encoding="utf8") as f:
            pulados = json.load(f)
    except:
        pulados = []
        
    if id_descricao not in pulados:
        pulados.append(id_descricao)
        with open(PULADOS_PATH, "w", encoding="utf8") as f:
            json.dump(pulados, f, indent=2)
            
    return jsonify({"status": "pulado_salvo"})
    
@app.route("/sugerir", methods=["POST"])
def sugerir_ia():
    if not nlp:
        return jsonify({"sugestoes": []})
    
    dados = request.json
    texto = dados.get("texto", "")
    
    if not texto:
        return jsonify({"sugestoes": []})
    
    doc = nlp(str(texto))
    sugestoes = []
    for ent in doc.ents:
        sugestoes.append([ent.start_char, ent.end_char, ent.label_])
    
    return jsonify({"sugestoes": sugestoes})

# --- ROTA: SALVAR RÓTULO (COM LIMPEZA AUTOMÁTICA) ---
@app.route("/rotulo", methods=["POST"])
def salvar_rotulo():
    dados_req = request.json
    id_descricao = dados_req.get("id_descricao")
    anotacoes = dados_req.get("anotacoes", [])
    
    row_match = df.loc[df["id_descricao"] == id_descricao]
    if row_match.empty:
        return jsonify({"status": "erro", "mensagem": "ID não encontrado"}), 404
    
    row = row_match.iloc[0]
    texto_original = str(row["descricao"])
    id_mensagem = row["id_mensagem"]
    ordem_parte = row["ordem_parte"]
    entidades_limpas = []
    
    for a in anotacoes:
        start = int(a["start"])
        end = int(a["end"])
        label = str(a["label"])
        entidades_limpas.append([start, end, label])
            
    registro = {
        "id_descricao": int(id_descricao),
        "id_mensagem": str(id_mensagem),
        "ordem_parte": int(ordem_parte),
        "text": texto_original,
        "entities": entidades_limpas
    }
    
    dados = ler_json()
    dados = [d for d in dados if d["id_descricao"] != id_descricao]
    dados.append(registro)
    
    with open(OUTPUT_PATH, "w", encoding="utf8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

    with open(OUTPUT_PATH_NER, "w", encoding="utf8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
        
    return jsonify({"status": "salvo"})

# --- ROTA: REMOVER RÓTULO ---
@app.route("/remover/<int:id_descricao>", methods=["POST"])
def remover_rotulo(id_descricao):
    dados = ler_json()
    dados = [d for d in dados if d["id_descricao"] != id_descricao]
    
    with open(OUTPUT_PATH, "w", encoding="utf8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    
    with open(OUTPUT_PATH_NER, "w", encoding="utf8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
        
    return jsonify({"status": "removido"})

# --- ROTA: STATUS DO PROGRESSO ---
@app.route("/status", methods=["GET"])
def status():
    dados = ler_json()
    return jsonify({
        "rotulados": len(dados),
        "total": len(df)
    })
    
# --- ROTA: RENDERIZAR DASHBOARD ---
@app.route("/render", methods=["POST"])
def render_dashboard():
    try:
        comando = [
            "quarto", 
            "render", 
            "scripts/qmd/relatorio_rme.qmd", 
            "--output-dir", 
            "../../outputs/html"
        ]

        process = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            cwd="/app" 
        )

        if process.returncode == 0:
            return jsonify({"status": "sucesso", "mensagem": "Dashboard renderizado!"})
        else:
            return jsonify({"status": "erro", "detalhes": process.stderr}), 500
            
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

# --- EXECUÇÃO ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
