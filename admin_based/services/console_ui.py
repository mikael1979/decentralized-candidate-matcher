import sys
from getpass import getpass
import re
from datetime import datetime

def print_header(version: str, use_prod_mode: bool):
    mode = "TUOTANTO" if use_prod_mode else "KEHITYS (DEBUG)"
    print("=" * 60)
    print(f"🗳️  HAJAUTETUN VAALIKONEEN ASENNUSOHJELMA v{version}")
    print(f"🔧 Tila: {mode}")
    print("=" * 60)

def input_election_date() -> str:
    while True:
        date_str = input("Vaalipäivämäärä (YYYY-MM-DD): ").strip()
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except ValueError:
                pass
        print("❌ Virheellinen päivämäärä. Käytä muotoa YYYY-MM-DD")

def input_time_lock() -> tuple:
    print("\n🕒 KYSYMYSTEN MUOKKAUSIKKUNA")
    print("-" * 30)
    print("Milloin kysymysten, ehdokkaiden ja puolueiden muokkaus suljetaan?")
    print("Anna päivämäärä ja kellonaika muodossa YYYY-MM-DD HH:MM (esim. 2025-08-01 23:59)")
    
    edit_deadline_str = input("Muokkausikkunan päättymisaika (tyhjä = ei rajoitusta): ").strip()
    if not edit_deadline_str:
        return None, 0
    
    try:
        deadline_dt = datetime.strptime(edit_deadline_str, '%Y-%m-%d %H:%M')
        grace_input = input("Armonaika virheenkorjauksille (tuntia, oletus 24): ").strip()
        grace_hours = int(grace_input) if grace_input.isdigit() else 24
        if grace_hours < 0:
            grace_hours = 24
        return deadline_dt.isoformat(), grace_hours
    except ValueError:
        print("❌ Virheellinen muoto. Käytä: YYYY-MM-DD HH:MM")
        return input_time_lock()

def get_password() -> str:
    while True:
        password = getpass("Aseta asennussalasana (väh. 8 merkkiä): ")
        if len(password) < 8:
            print("❌ Salasanan tulee olla vähintään 8 merkkiä pitkä")
            continue
        
        # Tarkista salasanan vahvuus
        if not any(c.islower() for c in password):
            print("❌ Salasanassa tulee olla vähintään yksi pieni kirjain")
            continue
        if not any(c.isupper() for c in password):
            print("❌ Salasanassa tulee olla vähintään yksi iso kirjain")
            continue
        if not any(c.isdigit() for c in password):
            print("❌ Salasanassa tulee olla vähintään yksi numero")
            continue
        
        confirm = getpass("Vahvista salasana: ")
        if password != confirm:
            print("❌ Salasanat eivät täsmää")
            continue
        
        return password

def input_election_date() -> str:
    while True:
        date_str = input("Vaalipäivämäärä (YYYY-MM-DD): ").strip()
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except ValueError:
                pass
        print("❌ Virheellinen päivämäärä. Käytä muotoa YYYY-MM-DD")

def input_time_lock() -> tuple:
    print("\n🕒 KYSYMYSTEN MUOKKAUSIKKUNA")
    print("-" * 30)
    print("Milloin kysymysten, ehdokkaiden ja puolueiden muokkaus suljetaan?")
    print("(Voit jättää tyhjäksi, jos et halua aikalisäystä)")
    
    deadline = input("Päivämäärä ja kellonaika (YYYY-MM-DD HH:MM): ").strip()
    if not deadline:
        return None, 24
    
    grace = input("Armonaika tunneissa (oletus 24): ").strip()
    grace_hours = int(grace) if grace.isdigit() else 24
    
    return deadline, grace_hours
