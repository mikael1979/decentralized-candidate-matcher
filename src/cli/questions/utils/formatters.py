# src/cli/questions/utils/formatters.py
"""
Tulostusapufunktiot kysymysten listaukselle.
"""

def format_question_list(questions, election_id="", enable_multinode=False, node_identity=None):
    """Muotoile kysymyslista näyttökelpoiseksi."""
    output = []
    
    if enable_multinode:
        output.append(f"🌐 MULTINODE MODE - Node: {node_identity.node_id if node_identity else 'N/A'}")
    
    output.append(f"📝 KYSYMYSLISTA - {election_id}")
    output.append("=" * 50)
    
    # Ryhmittele kategorioittain
    categories = {}
    for question in questions:
        cat = question["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(question)
    
    for category_name, category_questions in categories.items():
        output.append(f"\n📁 KATEGORIA: {category_name}")
        output.append("-" * 40)
        
        for i, question in enumerate(category_questions, 1):
            output.append(f"{i}. [{question['id']}] {question['question_fi']}")
            if question.get('question_en') and question['question_en'] != question['question_fi']:
                output.append(f"   EN: {question['question_en']}")
            output.append(f"   🎯 ELO-luokitus: {question['elo_rating']}")
    
    return "\n".join(output)


def format_stats(stats):
    """Muotoile tilastot näyttökelpoiseksi."""
    output = []
    output.append(f"\n📊 YHTEENVETO:")
    output.append(f"   ❓ Kysymyksiä: {stats['total_questions']}")
    output.append(f"   📁 Kategorioita: {len(stats['categories'])}")
    output.append(f"   📈 Keskim. ELO: {stats['average_elo']}")
    
    for cat, count in stats['categories'].items():
        output.append(f"      - {cat}: {count} kysymystä")
    
    # Lisää verkontilastot jos saatavilla
    if "network" in stats:
        output.append(f"\n🌐 VERKKOTILASTOT:")
        output.append(f"   🆔 Node ID: {stats['network']['node_id']}")
        output.append(f"   📡 Peerit: {stats['network']['peer_count']}")
        output.append(f"   🔗 Tila: {stats['network']['connection_status']}")
    
    return "\n".join(output)
