def main():
    """Pääkäyttöliittymä"""
    ipfs = MockIPFS()
    manager = ElectionDataManager(ipfs)
    
    print("🎯 HAJautettu Vaalikone")
    print("======================")
    
    while True:
        print("\nValitse toiminto:")
        print("1. Näytä kysymykset")
        print("2. Vastaa kysymyksiin")
        print("3. Etsi ehdokkaita")
        print("4. Lopeta")
        
        choice = input("Valinta: ")
        
        if choice == "1":
            show_questions(manager)
        elif choice == "2":
            user_answers = answer_questions(manager)
        elif choice == "3":
            if 'user_answers' in locals():
                find_candidates(manager, user_answers)
            else:
                print("Vastaa ensin kysymyksiin!")
        elif choice == "4":
            break
