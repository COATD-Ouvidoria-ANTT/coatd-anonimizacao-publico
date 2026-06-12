#!/bin/bash
set -e

echo "Iniciando API..."
python /app/scripts/python/api_ner.py &
PID_API=\$!

echo "Renderizando o relatorio inicial..."
quarto render /app/scripts/qmd/relatorio_rme.qmd --output-dir /app/outputs/html

echo "Iniciando servidor HTTP na porta 4200..."
cd /app/outputs/html
python -m http.server 4200 &
PID_HTTP=\$!

trap "echo 'Encerrando...'; kill \ \ 2>/dev/null; exit 0" SIGINT SIGTERM

echo "Sistema Iniciado!"
echo "Rotulador: http://localhost:5000"
echo "Relatorio: http://localhost:4200"

wait