#!/usr/bin/env python3
"""
Testien suorittamisen pääohjelma - KORJATTU VERSIO
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
import pytest

# Lisää src-hakemisto Python-polkuun
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_tests():
    """Suorita testit"""
    print("🚀 AJETAAN TESTEJÄ...")
    print("=" * 50)
    
    # Testihakemisto
    test_dir = os.path.dirname(__file__)
    
    # Suorita testit
    result = pytest.main([
        test_dir,
        "-v",  # verbose
        "--tb=short",  # lyhyet tracebackit
        # "-x",  # pysähdy ensimmäiseen virheeseen - KOMMENTOITU POIS, jotta nähdään kaikki virheet
    ])
    
    print("=" * 50)
    if result == 0:
        print("🎉 KAIKKI TESTIT MENIVÄT LÄPI!")
    else:
        print(f"❌ TESTIT PALAUTTI VIHEKODEIN: {result}")
    
    return result

if __name__ == '__main__':
    sys.exit(run_tests())
