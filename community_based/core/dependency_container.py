#!/usr/bin/env python3
"""
Dependency Container - PÄIVITETTY KORJATTUUN VERSIOON
"""

import os
import sys
from pathlib import Path

# Lisää polku jotta moduulit löytyvät
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from infrastructure.repositories.json_question_repository import JSONQuestionRepository
from infrastructure.repositories.ipfs_question_repository import IPFSQuestionRepository
from infrastructure.config.config_manager import ConfigManager
from infrastructure.logging.system_logger import SystemLogger
from application.services.question_service import QuestionService
from application.use_cases.submit_question import SubmitQuestionUseCase
from application.use_cases.sync_questions import SyncQuestionsUseCase
from application.use_cases.process_rating import ProcessRatingUseCase
from domain.repositories.question_repository import QuestionRepository

class DependencyContainer:
    """Riippuvuuksien kontti - KORJATTU VERSIO"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.runtime_dir.mkdir(exist_ok=True)
        
        # Alusta komponentit
        self._setup_infrastructure()
        self._setup_application()
        
        print("✅ Dependency Container alustettu onnistuneesti")
    
    def _setup_infrastructure(self):
        """Alusta infrastruktuurikomponentit"""
        print("🔄 Alustetaan infrastruktuuri...")
        
        # Config Manager
        self.config_manager = ConfigManager(str(self.runtime_dir))
        
        # System Logger
        self.system_logger = SystemLogger(str(self.runtime_dir))
        
        # JSON Question Repository - KORJATTU: vain runtime_dir
        self.json_question_repo = JSONQuestionRepository(
            runtime_dir=str(self.runtime_dir)
        )
        
        # IPFS Question Repository - KORJATTU: yksinkertainen konstruktori
        self.ipfs_question_repo = IPFSQuestionRepository(
            ipfs_client=self._get_ipfs_client()
        )
        
        # Legacy Integration (yhteensopivuus vanhojen moduulien kanssa)
        self.legacy_integration = self._create_legacy_integration()
    
    def _setup_application(self):
        """Alusta sovelluskerrroksen komponentit"""
        print("🔄 Alustetaan sovelluskerros...")
        
        # Question Service - KORJATTU: oikeat parametrit
        self.question_service = QuestionService(
            question_repository=self.json_question_repo,
            ipfs_repository=self.ipfs_question_repo
        )
        
        # Use Cases
        self.submit_question_use_case = SubmitQuestionUseCase(self.question_service)
        self.sync_questions_use_case = SyncQuestionsUseCase(
            question_service=self.question_service,
            ipfs_repository=self.ipfs_question_repo
        )
        self.process_rating_use_case = ProcessRatingUseCase(self.question_service)
    
    def _get_ipfs_client(self):
        """Hae IPFS-asiakas (mock tai oikea)"""
        try:
            # Yritä ensin mock-IPFS:ää
            from mock_ipfs import MockIPFS
            print("✅ Mock-IPFS saatavilla")
            return MockIPFS()
        except ImportError:
            try:
                # Yritä sitten oikeaa IPFS:ää
                from ipfs_client import IPFSClient
                print("✅ Oikea IPFS-asiakas saatavilla")
                return IPFSClient()
            except ImportError:
                print("⚠️  IPFS-asiakasta ei saatavilla - käytetään mockia")
                from mock_ipfs import MockIPFS
                return MockIPFS()
    
    def _create_legacy_integration(self):
        """Luo legacy-integration vanhojen moduulien yhteensopivuuteen"""
        class LegacyIntegration:
            def __init__(self, container):
                self.container = container
            
            def get_legacy_sync_status(self):
                """Hae legacy-synkronoinnin tila yhteensopivuuden vuoksi"""
                return {
                    "legacy_mode": True,
                    "compatibility_layer": "active",
                    "modern_architecture": True
                }
            
            def sync_new_to_main(self, force=False):
                """Synkronoi new -> main legacy-tilassa"""
                # Tämä on vain placeholder yhteensopivuuden vuoksi
                return {
                    "success": True,
                    "synced_count": 0,
                    "message": "Legacy synkronointi - käytä modernia arkkitehtuuria",
                    "modern_architecture": True
                }
        
        return LegacyIntegration(self)
    
    # Getter-metodit komponenteille
    def get_question_service(self):
        return self.question_service
    
    def get_config_manager(self):
        return self.config_manager
    
    def get_system_logger(self):
        return self.system_logger
    
    def get_legacy_integration(self):
        return self.legacy_integration

# Singleton instance
_container = None

def initialize_container(runtime_dir: str = "runtime"):
    """Alusta container (testausta varten)"""
    global _container
    _container = DependencyContainer(runtime_dir)
    return _container

def get_container(runtime_dir: str = "runtime"):
    """Hae container-instanssi"""
    global _container
    if _container is None:
        _container = DependencyContainer(runtime_dir)
    return _container
