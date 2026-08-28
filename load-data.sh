#!/bin/bash

# =========================================================
# LA LEGIÓN DEL CÓDIGO
# CARGA DE DATOS EN MYSQL
# =========================================================

set -e

echo ""
echo "=========================================="
echo " LA LEGIÓN DEL CÓDIGO"
echo " CARGA DE DATOS"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

echo ">> Directorio actual:"
pwd

echo ""
echo ">> Verificando Python..."
python --version

echo ""
echo "=========================================="
echo " 1. LIMPIEZA Y FILTRADO"
echo "=========================================="
echo ""

python scripts/clean-up.py

echo ""
echo ">> CLEAN-UP OK"

echo ""
echo "=========================================="
echo " 2. CARGA A MYSQL"
echo "=========================================="
echo ""

python scripts/load-to-mysql.py

echo ""
echo ">> LOAD MYSQL OK"

echo ""
echo "=========================================="
echo " CARGA COMPLETADA"
echo "=========================================="
echo ""

