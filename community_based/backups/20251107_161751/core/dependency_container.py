# core/dependency_container.py - PÄIVITETTY VERSIO
"""
Dependency Container - PÄIVITETTY SISÄLTÄMÄÄN KAIKKI TARVITTAVAT KOMPONENTIT
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

# Infrastructure
from infrastructure.config.config_manager import ConfigManager
from infrastructure.repositories.json_question_repository import JSONQuestionRepository
from infrastructure.repositories.ipfs_question_repository import IPFSQuestionRepository
from infrastructure.adapters.ipfs_client import IPFSClient
from infrastructure.adapters.block_manager_adapter import BlockManagerAdapter
from infrastructure.logging.system_logger import SystemLogger
from infrastructure.services.legacy_integration import LegacyIntegrationService

# Domain Repositories
from domain.repositories.question_repository import QuestionRepository
from domain.repositories.election_repository import ElectionRepository

# Domain Services
from domain.services.rating_calculation import RatingCalculationService

# Application Services
from application.services.question_service import QuestionService

# Application Use Cases
from application.use_cases.submit_question import SubmitQuestionUseCase
from application.use_cases.sync_questions import SyncQuestionsUseCase
from application.use_cases.process_rating import ProcessRatingUseCase


class DependencyContainer:
    """Riippuvuuksien hallinta uudelle arkkitehtuurille"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.runtime_dir.mkdir(exist_ok=True)
        
        print("🔄 Alustetaan Dependency Container...")
        
        # 1. Infrastructure Layer
        self._setup_infrastructure()
        
        # 2. Domain Layer
        self._setup_domain()
        
        # 3. Application Layer
        self._setup_application()
        
        print("✅ Dependency Container alustettu onnistuneesti!")
    
    def _setup_infrastructure(self):
        """Alusta infrastruktuurikomponentit"""
        
        # Config
        self.config_manager = ConfigManager(self.runtime_dir)
        
        # Logging
        self.system_logger = SystemLogger(self.runtime_dir)
        
        # IPFS Client (Mock tai oikea)
        self.ipfs_client = self._create_ipfs_client()
        
        # Repositories
        self.json_question_repo = JSONQuestionRepository(
            questions_file=self.runtime_dir / "questions.json",
            config_manager=self.config_manager
        )
        
        self.ipfs_question_repo = IPFSQuestionRepository(
            ipfs_client=self.ipfs_client,
            config_manager=self.config_manager
        )
        
        # Block Manager (IPFS-lohkot)
        self.block_manager = BlockManagerAdapter(
            ipfs_client=self.ipfs_client,
            config_manager=self.config_manager
        )
        
        # Legacy Integration
        self.legacy_integration = LegacyIntegrationService(
            question_repository=self.json_question_repo,
            ipfs_client=self.ipfs_client,
            config_manager=self.config_manager
        )
    
    def _setup_domain(self):
        """Alusta domain-komponentit"""
        
        # Domain Repositories
        self.question_repository: QuestionRepository = self.json_question_repo
        self.election_repository = ElectionRepository(self.runtime_dir)
        
        # Domain Services
        self.rating_calculation = RatingCalculationService()
    
    def _setup_application(self):
        """Alusta application-komponentit"""
        
        # Application Services
        self.question_service = QuestionService(
            question_repository=self.question_repository,
            rating_service=self.rating_calculation,
            config_manager=self.config_manager,
            system_logger=self.system_logger
        )
        
        # Use Cases
        self.submit_question_use_case = SubmitQuestionUseCase(
            question_service=self.question_service
        )
        
        self.sync_questions_use_case = SyncQuestionsUseCase(
            question_service=self.question_service,
            ipfs_repository=self.ipfs_question_repo
        )
        
        self.process_rating_use_case = ProcessRatingUseCase(
            question_service=self.question_service,
            rating_service=self.rating_calculation
        )
    
    def _create_ipfs_client(self):
        """Luo IPFS-asiakas (Mock tai oikea)"""
        try:
            # Yritä luoda oikea IPFS-asiakas
            client = IPFSClient()
            if client.is_available():
                print("✅ Oikea IPFS-asiakas luotu")
                return client
        except Exception as e:
            print(f"⚠️  Oikea IPFS ei saatavilla: {e}")
        
        # Fallback: Mock IPFS
        try:
            from mock_ipfs import MockIPFS
            mock_client = MockIPFS()
            print("✅ Mock IPFS-asiakas luotu")
            return mock_client
        except ImportError:
            print("❌ Mock IPFS ei saatavilla")
            raise
    
    def get_question_service(self) -> QuestionService:
        """Hae Question Service"""
        return self.question_service
    
    def get_ipfs_client(self):
        """Hae IPFS Client"""
        return self.ipfs_client
    
    def get_config_manager(self) -> ConfigManager:
        """Hae Config Manager"""
        return self.config_manager
    
    def get_system_logger(self) -> SystemLogger:
        """Hae System Logger"""
        return self.system_logger
    
    def get_legacy_integration(self) -> LegacyIntegrationService:
        """Hae Legacy Integration Service"""
        return self.legacy_integration
    
    def initialize_services(self) -> bool:
        """Alusta kaikki palvelut"""
        try:
            # Alusta config
            self.config_manager.initialize()
            
            # Alusta IPFS-lohkot
            if self.block_manager:
                self.block_manager.initialize_blocks()
            
            # Alusta repositoryt
            self.question_repository.initialize()
            self.election_repository.initialize()
            
            print("✅ Kaikki palvelut alustettu onnistuneesti")
            return True
            
        except Exception as e:
            print(f"❌ Palveluiden alustus epäonnistui: {e}")
            return False
    
    def shutdown(self):
        """Sammuta kaikki palvelut turvallisesti"""
        try:
            if self.ipfs_client:
                self.ipfs_client.close()
            
            if self.system_logger:
                self.system_logger.flush()
            
            print("✅ Dependency Container sammutettu turvallisesti")
            
        except Exception as e:
            print(f"⚠️  Sammutusvirhe: {e}")


# Singleton instance
_container: Optional[DependencyContainer] = None


def get_container(runtime_dir: str = "runtime") -> DependencyContainer:
    """Hae Dependency Container singleton"""
    global _container
    if _container is None:
        _container = DependencyContainer(runtime_dir)
    return _container


def initialize_container(runtime_dir: str = "runtime") -> bool:
    """Alusta container ja kaikki palvelut"""
    try:
        container = get_container(runtime_dir)
        return container.initialize_services()
    except Exception as e:
        print(f"❌ Containerin alustus epäonnistui: {e}")
        return False


def shutdown_container():
    """Sammuta container turvallisesti"""
    global _container
    if _container:
        _container.shutdown()
        _container = None


# Testaus
if __name__ == "__main__":
    print("🧪 DEPENDENCY CONTAINER TESTI")
    print("=" * 50)
    
    try:
        # Alusta container
        container = get_container()
        
        # Testaa palvelut
        question_service = container.get_question_service()
        config_manager = container.get_config_manager()
        ipfs_client = container.get_ipfs_client()
        
        print(f"✅ Question Service: {question_service is not None}")
        print(f"✅ Config Manager: {config_manager is not None}")
        print(f"✅ IPFS Client: {ipfs_client is not None}")
        
        # Alusta palvelut
        if container.initialize_services():
            print("🎯 Kaikki testit läpäisty!")
        else:
            print("❌ Alustus epäonnistui")
            
    except Exception as e:
        print(f"❌ Testit epäonnistuivat: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Sammuta
        shutdown_container()
