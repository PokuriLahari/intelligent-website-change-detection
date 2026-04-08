#!/bin/bash
# Azure App Service startup script for WatchDog Website Monitor
# Set in Azure portal: Configuration → General settings → Startup Command:
#   bash startup.sh
pip install -r requirements.txt
waitress-serve --port=${PORT:-8000} --call app:app
