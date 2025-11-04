#!/usr/bin/env python3
# question_manager.py - PÄIVITETTY UUDELLE ARKKITEHTUURILLE
"""
Kysymysten hallinta - PÄIVITETTY KÄYTTÄMÄÄN UUTTA ARKKITEHTUURIA
Käyttää domain/application/infrastructure layer -komponentteja
"""

import json
import argparse
from datetime import datetime, timedelta
from datetime import timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading
import time
import hashlib
from enum import Enum

# UUSI ARKKITEHTUURI: Käytä uusia moduuleja
from core.dependency_container import get_container
from application.commands import SubmitQuestionCommand, SyncQuestionsCommand
from application.use_cases.submit_question import SubmitQuestionUseCase
from application.use_cases.sync_questions import SyncQuestionsUseCase
from application.use_cases.process_rating import ProcessRatingUseCase
from domain.entities.question import Question
from domain.value_objects import QuestionContent, QuestionScale

# Yhteensopavuus vanhoille komponenteille
try:
    from ipfs_schedule_manager import IPFSScheduleManager, ReservationType, ReservationStatus
    IPFS_SCHEDULE_AVAILABLE = True
except ImportError:
    IPFS_SCHEDULE_AVAILABLE = False
    print("⚠️  IPFS Schedule Manager ei saatavilla")

# Singleton instance
_question_manager_instance = None

def get_question_manager(runtime_dir: str = "runtime"):
    """Singleton-funktio uudella arkkitehtuurilla"""
    global _question_manager_instance
    if _question_manager_instance is None:
        _question_manager_instance = ModernQuestionManager(runtime_dir)
    return _question_manager_instance

class ModernQuestionManager:
    """Moderni kysymysten hallinta uuden arkkitehtuurin päällä"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        
        # UUSI ARKKITEHTUURI: Hae riippuvuudet containerista
        self.container = get_container(runtime_dir)
        self.question_service = self.container.get_question_service()
        self.config_manager = self.container.get_config_manager()
        self.system_logger = self.container.get_system_logger()
        self.legacy_integration = self.container.get_legacy_integration()
        
        # Synkronointiasetukset
        self.sync_config = {
            "batch_size": 5,
            "max_batch_size": 20,
            "time_interval_hours": 24,
            "auto_sync_enabled": True,
            "use_schedule": IPFS_SCHEDULE_AVAILABLE
        }
        
        # IPFS Ajanvarausmanageri (jos saatavilla)
        self.schedule_manager = None
        if IPFS_SCHEDULE_AVAILABLE:
            try:
                self.schedule_manager = IPFSScheduleManager()
                print("✅ IPFS Ajanvarausmanageri alustettu")
            except Exception as e:
                print(f"⚠️  IPFS Ajanvarausmanagerin alustus epäonnistui: {e}")
        
        # Synkronointi
        self._sync_lock = threading.Lock()
        self._load_sync_config()
        self._start_background_sync()
        
        print("✅ Modern Question Manager alustettu uudella arkkitehtuurilla")
    
    def _load_sync_config(self):
        """Lataa synkronointikonfiguraatio"""
        config_file = self.runtime_dir / "sync_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.sync_config.update(loaded_config)
            except Exception as e:
                print(f"⚠️  Virhe synkronointikonfiguraatiota ladatessa: {e}")
    
    def _save_sync_config(self):
        """Tallenna synkronointikonfiguraatio"""
        config_file = self.runtime_dir / "sync_config.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.sync_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Virhe synkronointikonfiguraatiota tallennettaessa: {e}")
    
    def get_sync_status(self) -> Dict:
        """Hae synkronoinnin tila - UUSI ARKKITEHTUURI"""
        try:
            # UUSI ARKKITEHTUURI: Käytä question serviceä
            status = self.question_service.get_sync_status()
            
            # Lisää legacy-tiedot yhteensopivuuden vuoksi
            legacy_status = self.legacy_integration.get_legacy_sync_status()
            
            # Yhdistä tulokset
            result = {
                **status,
                "legacy_status": legacy_status,
                "auto_sync_enabled": self.sync_config["auto_sync_enabled"],
                "use_schedule": self.sync_config.get("use_schedule", False),
                "sync_rules": self.sync_config
            }
            
            # Lisää ajanvarauksen tila jos saatavilla
            if self.schedule_manager:
                schedule_status = self.schedule_manager.get_schedule_status(self._get_node_id())
                result["schedule_status"] = schedule_status
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "tmp_questions_count": 0,
                "new_questions_count": 0,
                "main_questions_count": 0
            }
    
    def submit_question(self, question_data: Dict, user_id: str) -> Dict:
        """Lähetä uusi kysymys järjestelmään - UUSI ARKKITEHTUURI"""
        try:
            # UUSI ARKKITEHTUURI: Käytä Command/UseCase -mallia
            command = SubmitQuestionCommand(
                content=question_data["content"],
                category=question_data.get("category", "general"),
                scale=question_data.get("scale", "agree_disagree"),
                submitted_by=user_id,
                tags=question_data.get("tags", []),
                metadata=question_data.get("metadata", {})
            )
            
            use_case = SubmitQuestionUseCase(self.question_service)
            result = use_case.execute(command)
            
            # Tarkista automaattinen synkronointi
            auto_synced = False
            sync_result = None
            
            if (self.sync_config["auto_sync_enabled"] and 
                result.success and 
                self._should_auto_sync()):
                sync_result = self.sync_tmp_to_new()
                auto_synced = sync_result["success"]
            
            return {
                "success": result.success,
                "question_id": result.question_id,
                "auto_synced": auto_synced,
                "sync_result": sync_result,
                "queue_position": result.queue_position,
                "estimated_sync_time": self._get_next_sync_time(),
                "message": result.message
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def sync_tmp_to_new(self, force: bool = False) -> Dict:
        """Synkronoi tmp-kysymykset new-kysymyksiin - UUSI ARKKITEHTUURI"""
        
        # Käytä ajanvarausta jos saatavilla
        reservation_result = None
        if (self.sync_config.get("use_schedule", False) and 
            self.schedule_manager and 
            not force):
            
            reservation_result = self.schedule_manager.request_reservation(
                ReservationType.NODE_SYNC if IPFS_SCHEDULE_AVAILABLE else None,
                self._get_node_id(),
                urgency="high" if force else "normal"
            )
            
            if not reservation_result.get("success", False):
                return {
                    "success": False,
                    "error": f"Ei saatavilla aikaa synkronointiin: {reservation_result.get('error')}",
                    "suggested_times": reservation_result.get("suggested_times", []),
                    "use_force": "Käytä --force ohittaaksesi ajanvarauksen"
                }
            
            print(f"🕒 Synkronointi ajastettu: {reservation_result.get('reservation_id')}")
        
        # UUSI ARKKITEHTUURI: Käytä synkronointi use casea
        try:
            command = SyncQuestionsCommand(
                sync_type="tmp_to_new",
                force=force,
                batch_size=self.sync_config["batch_size"] if not force else None
            )
            
            use_case = SyncQuestionsUseCase(
                question_service=self.question_service,
                ipfs_repository=self.container.ipfs_question_repo
            )
            
            result = use_case.execute(command)
            
            response = {
                "success": result.success,
                "synced_count": result.synced_count,
                "message": result.message,
                "remaining_in_tmp": result.remaining_count,
                "batch_id": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            # Lisää ajanvarauksen tiedot jos käytettiin
            if reservation_result and reservation_result.get("success"):
                response["reservation_id"] = reservation_result.get("reservation_id")
                response["scheduled_sync"] = True
            
            return response
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "synced_count": 0
            }
    
    def sync_new_to_main(self, force: bool = False) -> Dict:
        """Synkronoi new-kysymykset pääkantaan - UUSI ARKKITEHTUURI"""
        
        # Käytä ajanvarausta jos saatavilla
        reservation_result = None
        if (self.sync_config.get("use_schedule", False) and 
            self.schedule_manager and 
            not force):
            
            reservation_result = self.schedule_manager.request_reservation(
                ReservationType.SYSTEM_SYNC if IPFS_SCHEDULE_AVAILABLE else None,
                self._get_node_id(),
                urgency="high" if force else "normal"
            )
            
            if not reservation_result.get("success", False):
                return {
                    "success": False,
                    "error": f"Ei saatavilla aikaa synkronointiin: {reservation_result.get('error')}",
                    "suggested_times": reservation_result.get("suggested_times", [])
                }
        
        # UUSI ARKKITEHTUURI: Käytä legacy integrationia yhteensopivuuden vuoksi
        try:
            result = self.legacy_integration.sync_new_to_main(force)
            
            # Lisää ajanvarauksen tiedot jos käytettiin
            if reservation_result and reservation_result.get("success"):
                result["reservation_id"] = reservation_result.get("reservation_id")
                result["scheduled_sync"] = True
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def emergency_sync(self) -> Dict:
        """Hätäsynkronointi - ohittaa ajanvarauksen"""
        print("🚨 HÄTÄSYNKRONOINTI AKTIVOITU!")
        
        # UUSI ARKKITEHTUURI: Käytä use caseja
        tmp_result = self.sync_tmp_to_new(force=True)
        main_result = self.sync_new_to_main(force=True)
        
        return {
            "emergency_sync": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tmp_sync": tmp_result,
            "main_sync": main_result,
            "node_id": self._get_node_id()
        }
    
    def update_sync_rules(self, new_rules: Dict):
        """Päivitä synkronointisääntöjä"""
        self.sync_config.update(new_rules)
        self._save_sync_config()
        
        # UUSI ARKKITEHTUURI: Päivitä config manager
        self.config_manager.update_sync_config(new_rules)
        
        print(f"✅ Synkronointisäännöt päivitetty: {new_rules}")
    
    def _should_auto_sync(self) -> bool:
        """Tarkista täyttävätkö ehdot automaattiselle synkronointiin"""
        # UUSI ARKKITEHTUURI: Käytä question serviceä
        status = self.question_service.get_sync_status()
        
        # Tarkista määrä
        if status.get("tmp_questions_count", 0) >= self.sync_config["batch_size"]:
            return True
        
        # Tarkista aika
        next_sync = self._get_next_sync_time()
        if datetime.now(timezone.utc) >= datetime.fromisoformat(next_sync):
            return True
        
        return False
    
    def _get_next_sync_time(self) -> str:
        """Laske seuraavan synkronoinnin aika"""
        last_sync_file = self.runtime_dir / "last_sync.txt"
        
        if last_sync_file.exists():
            with open(last_sync_file, 'r') as f:
                last_sync = datetime.fromisoformat(f.read().strip())
        else:
            last_sync = datetime.now(timezone.utc)
        
        next_sync = last_sync + timedelta(hours=self.sync_config["time_interval_hours"])
        return next_sync.isoformat()
    
    def _get_time_until_sync(self, next_sync_time: str) -> str:
        """Laske aikaa seuraavaan synkronointiin"""
        next_sync = datetime.fromisoformat(next_sync_time)
        now = datetime.now(timezone.utc)
        
        if now >= next_sync:
            return "Nyt"
        
        delta = next_sync - now
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        return f"{hours}h {minutes}min"
    
    def _start_background_sync(self):
        """Käynnistä taustasynkronointi"""
        def background_sync():
            while True:
                try:
                    # Tarkista synkronointi 5 minuutin välein
                    time.sleep(300)
                    
                    # Tarkista onko aika synkronoida
                    if self._should_auto_sync():
                        print("🔄 Taustasynkronointi käynnistyy...")
                        self.sync_tmp_to_new()
                        
                        # Päivitä viimeisen synkronoinnin aika
                        with open(self.runtime_dir / "last_sync.txt", 'w') as f:
                            f.write(datetime.now(timezone.utc).isoformat())
                            
                except Exception as e:
                    print(f"⚠️  Taustasynkronointivirhe: {e}")
        
        if self.sync_config["auto_sync_enabled"]:
            sync_thread = threading.Thread(target=background_sync, daemon=True)
            sync_thread.start()
            print("✅ Taustasynkronointi käynnistetty")
    
    def _get_node_id(self) -> str:
        """Hae noden ID"""
        try:
            # UUSI ARKKITEHTUURI: Käytä config manageria
            machine_info = self.config_manager.get_machine_info()
            return machine_info.get('machine_id', 'unknown_node')
        except:
            return 'unknown_node'
    
    def get_schedule_info(self) -> Dict:
        """Hae ajanvarauksen tiedot"""
        if self.schedule_manager:
            return self.schedule_manager.get_schedule_status(self._get_node_id())
        return {"error": "Ajanvarausmanageri ei saatavilla"}

# Testaus
if __name__ == "__main__":
    # Alusta container ensin
    from core.dependency_container import initialize_container
    initialize_container()
    
    manager = get_question_manager()
    status = manager.get_sync_status()
    
    print("🔍 MODERN QUESTION MANAGER TESTI - UUSI ARKKITEHTUURI")
    print("=" * 50)
    print(f"Tmp-kysymyksiä: {status.get('tmp_questions_count', 0)}")
    print(f"New-kysymyksiä: {status.get('new_questions_count', 0)}")
    print(f"Pääkannan kysymyksiä: {status.get('main_questions_count', 0)}")
    print(f"Seuraava synkronointi: {status.get('next_sync_time', 'N/A')}")
    print(f"Uusi arkkitehtuuri: ✅ KÄYTÖSSÄ")
    
    # Testaa kysymyksen lähetys
    test_question = {
        "content": {
            "question": {
                "fi": "Testikysymys uudella arkkitehtuurilla",
                "en": "Test question with new architecture",
                "sv": "Testfråga med ny arkitektur"
            }
        },
        "category": "test",
        "scale": "agree_disagree",
        "tags": ["test", "new-architecture"]
    }
    
    result = manager.submit_question(test_question, "test_user")
    print(f"\n🧪 Kysymyksen lähetystesti: {'✅ ONNISTUI' if result['success'] else '❌ EPÄONNISTUI'}")
    if result['success']:
        print(f"   Kysymys ID: {result['question_id']}")
        print(f"   Auto-synkronoitu: {result['auto_synced']}")
    
    # Testaa synkronointi
    sync_result = manager.sync_tmp_to_new()
    print(f"🧪 Synkronointitesti: {'✅ ONNISTUI' if sync_result['success'] else '❌ EPÄONNISTUI'}")
    if sync_result['success']:
        print(f"   Synkronoitu: {sync_result['synced_count']} kysymystä")
    
    print("\n🎯 MODERN QUESTION MANAGER VALMIS UUDELLE ARKKITEHTUURILLE!")
