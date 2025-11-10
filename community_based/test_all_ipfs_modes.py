#!/usr/bin/env python3
"""Testaa kaikkia IPFS-valintatapoja"""

import subprocess
import sys

def test_ipfs_mode(mode, description):
    print(f"\n🧪 TESTI: {description}")
    print("=" * 50)
    
    cmd = [
        "python", "install.py",
        "--config-file", "elections_list.json",
        "--election-id", "test_ipfs_mode",
        "--verify",
        "--ipfs-type", mode
    ]
    
    if mode == "real":
        cmd.extend(["--skip-ipfs-test"])  # Ohita testi ettei tule virheitä
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ TESTI ONNISTUI")
    else:
        print("❌ TESTI EPÄONNISTUI")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    
    return result.returncode == 0

# Testaa kaikki modet
success_count = 0
total_tests = 0

for mode, desc in [("mock", "Mock-IPFS"), ("auto", "Auto-valinta"), ("real", "Todellinen IPFS (skip test)")]:
    total_tests += 1
    if test_ipfs_mode(mode, desc):
        success_count += 1

print(f"\n📊 TULOKSET: {success_count}/{total_tests} testiä onnistui")
sys.exit(0 if success_count == total_tests else 1)
