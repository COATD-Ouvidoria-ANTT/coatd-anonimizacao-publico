#!/bin/bash

echo "Iniciando API..."
python scripts/python/api_ner.py &
PID_API=$!

echo "Renderizando o relatório inicial..."
cd /app
quarto render scripts/qmd/relatorio_rme.qmd --output-dir ../../outputs/html

echo "Iniciando servidor HTTP na porta 4200..."
cd outputs/html/
python -m http.server 4200 &
PID_HTTP=$!

trap "echo 'Encerrando...'; kill $PID_API $PID_HTTP 2>/dev/null; exit 0" SIGINT SIGTERM

echo "Sistema Iniciado!"
echo "Rotulador: http://localhost:5000"
echo "Relatório: http://localhost:4200"

wait