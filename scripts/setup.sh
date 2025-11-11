#!/bin/bash

echo "🔨 Hajautetun vaalikoneen asennus"

# Tarkista Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 ei asennettuna"
    exit 1
fi

# Luo virtuaaliympäristö
echo "📦 Luodaan virtuaaliympäristö..."
python3 -m venv venv
source venv/bin/activate

# Asenna riippuvuudet
echo "📚 Asennetaan riippuvuudet..."
pip install -r requirements.txt

# Luo tarvittavat hakemistot
echo "📁 Luodaan hakemistorakenne..."
mkdir -p data/{tmp,runtime,backup} logs

echo "✅ Asennus valmis!"
echo "🚀 Käynnistä: source venv/bin/activate"
echo "📖 Lue dokumentaatio: cat docs/quickstart.md"
