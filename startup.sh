#!/bin/bash
echo "Iniciando aplicação Flask com Gunicorn..."
gunicorn --bind=0.0.0.0 --timeout 600 app:app
