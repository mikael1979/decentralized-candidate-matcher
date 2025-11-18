#!/usr/bin/env python3
"""
Automaattinen arkistojen julkaisu
"""
import schedule
import time
from datetime import datetime, timedelta

class AutoPublisher:
    def __init__(self, election_id):
        self.election_id = election_id
        self.last_publish = None
    
    def should_publish(self):
        """Tarkista onko aika julkaista uusi arkisto"""
        if not self.last_publish:
            return True
        
        # Julkaise kun:
        # - 1 tunti kulunut viime julkaisusta
        # - Tietty määrä muutoksia tapahtunut
        # - Manuaalinen käsky
        time_since_last = datetime.now() - self.last_publish
        return time_since_last.total_seconds() > 3600  # 1 tunti
    
    def auto_publish(self):
        """Automaattinen julkaisu"""
        if self.should_publish():
            click.echo("🕒 AUTOMAATTINEN JULKAISU...")
            # Käytä sync_coordinator.py --publish -logiikkaa
            self.last_publish = datetime.now()
