# test_imports.py
try:
    from src.cli.config import *
    print("🎉 KAIKKI CONFIG-MODUULIN IMPORTIT ONNISTUIVAT!")
except Exception as e:
    print(f"❌ IMPORT-VIRHE: {e}")
