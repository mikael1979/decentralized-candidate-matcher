# mock_sync_manager.py
from mock_ipfs import MockIPFS
import uuid
import json
from datetime import datetime

class MockSyncManager:
    """
    Synkronointimanageri joka käyttää Mock-IPFS:ää testausta varten.
    """
    
    def __init__(self, runtime_dir: str = "runtime", local_system_id: str = None):
        self.runtime_dir = runtime_dir
        self.local_system_id = local_system_id or f"mock_system_{uuid.uuid4().hex[:8]}"
        self.ipfs = MockIPFS(persist_data=True)
        
        print(f"=== MOCK-IPFS SYNCRONOINTIMANAGERI KÄYNNISTETTY ===")
        print(f"System ID: {self.local_system_id}")
        print(f"IPFS Tilasto: {self.ipfs.get_stats()}")
    
    def _get_current_timestamp(self) -> str:
        return datetime.now().isoformat(timespec='milliseconds') + 'Z'
    
    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Lataa JSON-tiedosto"""
        try:
            with open(f"{self.runtime_dir}/{filename}", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_json(self, filename: str, data: Dict[str, Any]):
        """Tallentaa JSON-tiedoston"""
        with open(f"{self.runtime_dir}/{filename}", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, ensure_ascii=False)
    
    def add_new_question(self, question_content: Dict[str, Any]) -> str:
        """Lisää uusi kysymys paikalliseen järjestelmään"""
        local_id = str(uuid.uuid4())
        
        new_question = {
            "local_id": local_id,
            "ipfs_cid": None,  # CID asetetaan vasta synkronoinnissa
            "source": "local",
            "global_version": 1,
            "timestamps": {
                "created_local": self._get_current_timestamp(),
                "modified_local": self._get_current_timestamp(),
                "synced_to_ipfs": None,
                "imported_from_ipfs": None
            },
            "content": question_content,
            "elo_rating": {
                "base_rating": 1000,
                "comparison_delta": 0,
                "vote_delta": 0,
                "current_rating": 1000
            }
        }
        
        # Lisää questions.json:iin
        questions_data = self._load_json('questions.json')
        questions_data.setdefault('questions', []).append(new_question)
        questions_data['metadata'] = {
            'local_system_id': self.local_system_id,
            'last_updated': self._get_current_timestamp(),
            'total_questions': len(questions_data['questions'])
        }
        
        self._save_json('questions.json', questions_data)
        
        print(f"Mock: Uusi kysymys lisätty - Local ID: {local_id}")
        return local_id
    
    def sync_local_to_ipfs(self) -> str:
        """Synkronoi paikalliset kysymykset Mock-IPFS:ään"""
        print("\n=== MOCK: PAIKALLINEN → IPFS SYNKRONOINTI ===")
        
        # 1. Lataa questions.json
        questions_data = self._load_json('questions.json')
        
        # 2. Etsi paikalliset kysymykset ilman CID:ä
        local_questions = [
            q for q in questions_data.get('questions', [])
            if q.get('ipfs_cid') is None and q.get('source') == 'local'
        ]
        
        if not local_questions:
            print("Mock: Ei uusia kysymyksiä synkronoitavaksi")
            return None
        
        print(f"Mock: Löydetty {len(local_questions)} uutta kysymystä")
        
        # 3. Lähetä Mock-IPFS:ään
        cid = self.ipfs.upload({
            "metadata": {
                "source_system": self.local_system_id,
                "upload_timestamp": self._get_current_timestamp(),
                "question_count": len(local_questions)
            },
            "questions": local_questions
        })
        
        # 4. Päivitä kysymysten CID:t
        for question in questions_data['questions']:
            if question.get('ipfs_cid') is None and question.get('source') == 'local':
                question['ipfs_cid'] = cid
                question['source'] = 'local_synced'
                question['timestamps']['synced_to_ipfs'] = self._get_current_timestamp()
        
        # 5. Tallenna päivitetty questions.json
        questions_data['metadata']['last_sync'] = self._get_current_timestamp()
        self._save_json('questions.json', questions_data)
        
        # 6. Päivitä ipfs_questions.json
        ipfs_data = {
            "metadata": {
                "cid": cid,
                "synced_at": self._get_current_timestamp(),
                "source_system": self.local_system_id
            },
            "questions": local_questions
        }
        self._save_json('ipfs_questions.json', ipfs_data)
        
        print(f"Mock: Synkronointi valmis - CID: {cid}")
        return cid
    
    def sync_ipfs_to_local(self) -> int:
        """Synkronoi Mock-IPFS:stä paikalliseen järjestelmään"""
        print("\n=== MOCK: IPFS → PAIKALLINEN SYNKRONOINTI ===")
        
        # 1. Hae kaikki saatavilla olevat CID:t mock-IPFS:stä
        all_cids = list(self.ipfs.content_store.keys())
        
        if not all_cids:
            print("Mock: Ei CID:ä saatavilla IPFS:stä")
            return 0
        
        print(f"Mock: Löydetty {len(all_cids)} CID:ä IPFS:stä")
        
        # 2. Lataa paikallinen questions.json
        local_questions = self._load_json('questions.json')
        local_question_ids = {q['local_id'] for q in local_questions.get('questions', [])}
        
        # 3. Käy läpi kaikki CID:t ja tuo uudet kysymykset
        new_questions_count = 0
        
        for cid in all_cids:
            ipfs_data = self.ipfs.download(cid)
            
            if ipfs_data and 'questions' in ipfs_data:
                for question in ipfs_data['questions']:
                    # Tarkista onko kysymys jo paikallisesti
                    if question['local_id'] not in local_question_ids:
                        # Merkitse IPFS:stä tuoduksi
                        question['source'] = 'ipfs_imported'
                        question['ipfs_cid'] = cid
                        question['timestamps']['imported_from_ipfs'] = self._get_current_timestamp()
                        
                        # Lisää paikalliseen
                        local_questions.setdefault('questions', []).append(question)
                        local_question_ids.add(question['local_id'])
                        new_questions_count += 1
        
        # 4. Tallenna päivitetty questions.json
        if new_questions_count > 0:
            local_questions['metadata'] = {
                'local_system_id': self.local_system_id,
                'last_updated': self._get_current_timestamp(),
                'last_ipfs_import': self._get_current_timestamp(),
                'total_questions': len(local_questions['questions'])
            }
            self._save_json('questions.json', local_questions)
            print(f"Mock: Tuotu {new_questions_count} uutta kysymystä IPFS:stä")
        else:
            print("Mock: Ei uusia kysymyksiä IPFS:stä")
        
        return new_questions_count
    
    def full_sync_cycle(self):
        """Suorittaa täydellisen kaksisuuntaisen synkronointisyklin"""
        print("\n" + "="*50)
        print("MOCK: TÄYSI KAKSISUUNTAINEN SYNKRONOINTI")
        print("="*50)
        
        # 1. Synkronoi paikalliset muutokset IPFS:ään
        upload_cid = self.sync_local_to_ipfs()
        
        # 2. Synkronoi IPFS:stä paikalliseen
        downloaded_count = self.sync_ipfs_to_local()
        
        # 3. Raportoi tilastot
        questions_data = self._load_json('questions.json')
        total_questions = len(questions_data.get('questions', []))
        
        local_count = len([q for q in questions_data.get('questions', []) 
                          if q.get('source') in ['local', 'local_synced']])
        ipfs_count = len([q for q in questions_data.get('questions', []) 
                         if q.get('source') == 'ipfs_imported'])
        
        print("\n=== MOCK: SYNKRONOINTITILASTOT ===")
        print(f"Kysymyksiä yhteensä: {total_questions}")
        print(f"Paikallisia: {local_count}")
        print(f"IPFS:stä tuotuja: {ipfs_count}")
        print(f"IPFS:ään lähetetty: {upload_cid or 'Ei uusia'}")
        print(f"IPFS:stä tuotu: {downloaded_count} uutta")
        print(f"Mock-IPFS tilasto: {self.ipfs.get_stats()}")
        
        return {
            'upload_cid': upload_cid,
            'downloaded_count': downloaded_count,
            'timestamp': self._get_current_timestamp()
        }
