#!/usr/bin/env python3
"""
Puolueiden hajautettu hallinta - PÄIVITETTY MODULAARINEN VERSIO
Käyttää uusia modulaarisia komponentteja
"""
import click

# Tuodaan modulaariset komponentit
try:
    from src.cli.party_commands import PartyCommands
    from src.cli.party_verification import PartyVerification
    from src.cli.party_analytics import PartyAnalytics
except ImportError:
    from party_commands import PartyCommands
    from party_verification import PartyVerification
    from party_analytics import PartyAnalytics

@click.group()
def manage_parties():
    """Puolueiden hajautettu hallinta"""
    pass

@manage_parties.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--name-fi', required=True, help='Puolueen nimi suomeksi')
@click.option('--name-en', help='Puolueen nimi englanniksi')
@click.option('--name-sv', help='Puolueen nimi ruotsiksi')
@click.option('--description-fi', help='Puolueen kuvaus suomeksi')
@click.option('--email', help='Yhteysemail')
@click.option('--website', help='Verkkosivusto')
@click.option('--founding-year', default='2024', help='Perustamisvuosi')
def propose(election, name_fi, name_en, name_sv, description_fi, email, website, founding_year):
    """Ehdotta uutta puoluetta"""
    commands = PartyCommands(election)
    commands.propose_party(name_fi, name_en, name_sv, description_fi, email, website, founding_year)

@manage_parties.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--show-pending', is_flag=True, help='Näytä myös odottavat puolueet')
@click.option('--show-rejected', is_flag=True, help='Näytä myös hylätyt puolueet')
def list(election, show_pending, show_rejected):
    """Listaa kaikki puolueet"""
    commands = PartyCommands(election)
    commands.list_parties(show_pending, show_rejected)

@manage_parties.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--party-id', required=True, help='Puolueen tunniste')
def info(election, party_id):
    """Näytä yksittäisen puolueen tiedot"""
    commands = PartyCommands(election)
    commands.get_party_info(party_id)

@manage_parties.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--party-id', required=True, help='Puolueen tunniste')
@click.option('--node-id', required=True, help='Vahvistavan noden tunniste')
@click.option('--verify', is_flag=True, help='Vahvista puolue')
@click.option('--reject', is_flag=True, help='Hylkää puolue')
@click.option('--reason', help='Syy vahvistukseen/hylkäämiseen')
def verify(election, party_id, node_id, verify, reject, reason):
    """Vahvista tai hylkää puolue"""
    verification = PartyVerification(election)
    
    if verify:
        verification.verify_party(party_id, node_id, reason)
    elif reject:
        verification.reject_party(party_id, node_id, reason)
    else:
        click.echo("❌ Valitse joko --verify tai --reject")

@manage_parties.command()
@click.option('--election', required=True, help='Vaalin tunniste')
def stats(election):
    """Näytä puolueiden tilastot"""
    analytics = PartyAnalytics(election)
    analytics.show_stats()

@manage_parties.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--party-id', required=True, help='Puolueen tunniste')
@click.confirmation_option(prompt='Haluatko varmasti poistaa tämän puolueen?')
def remove(election, party_id):
    """Poista puolue rekisteristä"""
    analytics = PartyAnalytics(election)
    analytics.remove_party(party_id)

if __name__ == '__main__':
    manage_parties()
