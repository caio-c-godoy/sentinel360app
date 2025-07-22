#!/bin/bash
echo "Iniciando aplicação Flask com Gunicorn..."
/opt/python/3.11.9/bin/gunicorn --bind=0.0.0.0 --timeout 600 app:app