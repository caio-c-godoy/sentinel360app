#!/bin/bash
echo "Instalando dependências..."
pip install -r requirements.txt

echo "Iniciando aplicação Flask com Gunicorn..."
gunicorn --bind=0.0.0.0 --timeout 600 app:app
