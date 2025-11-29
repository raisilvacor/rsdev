#!/bin/bash
# Script de start para produção no Render.com
gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 app:app

