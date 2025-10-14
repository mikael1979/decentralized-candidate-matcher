import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
import base58
import multihash

class MockIPFS:
    """
    Mock IPFS-implementaatio testaamista varten
    Simuloi IPFS-toimintoja ilman oikeaa verkkoa
    """
    
    def __init__(self):
        self.content_store: Dict[str, Dict[str, Any]] = {}
        self.pins: List[str] = []
        self.stats = {
            "add_count": 0,
            "get_count": 0,
            "pin_count": 0,
            "total_size": 0
        }
    
    def _calculate_cid(self, data: Any) -> str:
        """Laskee CID:n datalle samalla tavalla kuin IPFS"""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        else:
            data_str = str(data)
        
        # Käytetään SHA-256 hashia
        hash_bytes = hashlib.sha256(data_str.encode()).digest()
        
        # Luodaan multihash (SHA-256 = 0x12, pituus 32 bytes = 0x20)
        multihash_bytes = bytes([0x12, 0x20]) + hash_bytes
        
        # Enkoodaa base58:aan (kuten todellinen IPFS CID)
        cid = "Qm" + base58.b58encode(multihash_bytes).decode()
        
        return cid
    
    def add_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lisää JSON-datan mock-IPFS:ään
        Palauttaa saman formatin kuin ipfs.http_client.add_json()
        """
        cid = self._calculate_cid(data)
        
        # Tallenna data
        self.content_store[cid] = {
            "data": data,
            "size": len(json.dumps(data)),
            "added": datetime.now().isoformat(),
            "cid": cid
        }
        
        # Päivitä statistiikat
        self.stats["add_count"] += 1
        self.stats["total_size"] += len(json.dumps(data))
        
        return {
            "Hash": cid,
            "Size": len(json.dumps(data)),
            "Name": cid
        }
    
    def get_json(self, cid: str) -> Optional[Dict[str, Any]]:
        """Hakee JSON-datan CID:llä"""
        self.stats["get_count"] += 1
        
        if cid in self.content_store:
            return self.content_store[cid]["data"]
        return None
    
    def cat(self, cid: str) -> Optional[bytes]:
        """Hakee raakadataa CID:llä (kuten ipfs.cat())"""
        data = self.get_json(cid)
        if data:
            return json.dumps(data).encode()
        return None
    
    def pin_add(self, cid: str) -> bool:
        """Simuloi CID:n pinnausta"""
        if cid in self.content_store:
            if cid not in self.pins:
                self.pins.append(cid)
                self.stats["pin_count"] += 1
            return True
        return False
    
    def pin_rm(self, cid: str) -> bool:
        """Poistaa pinnauksen"""
        if cid in self.pins:
            self.pins.remove(cid)
            self.stats["pin_count"] -= 1
            return True
        return False
    
    def pins(self) -> List[str]:
        """Palauttaa listan pinatuista CIDEistä"""
        return self.pins.copy()
    
    def ls(self, cid: str) -> Optional[List[Dict]]:
        """Listaa linkedit (ei toteutettu mockissa)"""
        if cid in self.content_store:
            return [{
                "Hash": cid,
                "Size": self.content_store[cid]["size"],
                "Name": cid,
                "Type": 2  # File
            }]
        return None
    
    def repo_stat(self) -> Dict[str, Any]:
        """Palauttaa repository statistiikat"""
        return {
            "NumObjects": len(self.content_store),
            "RepoSize": self.stats["total_size"],
            "StorageMax": 10_000_000_000,  # 10GB
            "RepoPath": "/mock/ipfs/repo",
            "Version": "mock-0.1.0"
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Palauttaa mock-IPFS:n tilastot"""
        return {
            **self.stats,
            "total_objects": len(self.content_store),
            "pinned_objects": len(self.pins),
            "timestamp": datetime.now().isoformat()
        }
    
    def clear(self):
        """Tyhjentää koko mock-IPFS:n"""
        self.content_store.clear()
        self.pins.clear()
        self.stats = {
            "add_count": 0,
            "get_count": 0,
            "pin_count": 0,
            "total_size": 0
        }

class ElectionDataManager:
    """
    Korkeamman tason wrapperi vaalikonedatan hallintaan MockIPFS:n päällä
    """
    
    def __init__(self, ipfs: MockIPFS):
        self.ipfs = ipfs
        self.root_cid = None
        
    def initialize_election(self, meta_data: Dict[str, Any]) -> str:
        """Alustaa uuden vaalin"""
        # Lisää meta.json
        meta_cid = self.ipfs.add_json(meta_data)["Hash"]
        
        # Alusta tyhjät datasetit
        questions_cid = self.ipfs.add_json({
            "election_id": meta_data["election"]["id"],
            "language": "fi",
            "questions": [],
            "integrity": self._create_integrity_hash([])
        })["Hash"]
        
        candidates_cid = self.ipfs.add_json({
            "election_id": meta_data["election"]["id"],
            "language": "fi",
            "candidates": [],
            "integrity": self._create_integrity_hash([])
        })["Hash"]
        
        new_questions_cid = self.ipfs.add_json({
            "election_id": meta_data["election"]["id"],
            "language": "fi",
            "question_type": "user_submitted",
            "questions": [],
            "integrity": self._create_integrity_hash([])
        })["Hash"]
        
        community_votes_cid = self.ipfs.add_json({
            "election_id": meta_data["election"]["id"],
            "language": "fi",
            "question_votes": [],
            "user_votes": [],
            "integrity": self._create_integrity_hash([])
        })["Hash"]
        
        # Luo root index
        root_index = {
            "election_id": meta_data["election"]["id"],
            "files": {
                "meta.json": meta_cid,
                "questions.json": questions_cid,
                "candidates.json": candidates_cid,
                "newquestions.json": new_questions_cid,
                "community_votes.json": community_votes_cid
            },
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        self.root_cid = self.ipfs.add_json(root_index)["Hash"]
        self.ipfs.pin_add(self.root_cid)
        
        return self.root_cid
    
    def _create_integrity_hash(self, data: Any) -> Dict[str, Any]:
        """Luo integrity hashin datalle"""
        data_to_hash = data if isinstance(data, dict) else {"data": data}
        
        # Poista nykyinen integrity hash jos on olemassa
        if 'integrity' in data_to_hash:
            data_to_hash = {k: v for k, v in data_to_hash.items() if k != 'integrity'}
        
        json_str = json.dumps(data_to_hash, sort_keys=True, separators=(',', ':'))
        hash_value = hashlib.sha256(json_str.encode()).hexdigest()
        
        return {
            "algorithm": "sha256",
            "hash": f"sha256:{hash_value}",
            "computed": datetime.now().isoformat()
        }
    
    def add_question(self, question_data: Dict[str, Any], is_official: bool = True) -> str:
        """Lisää kysymyksen"""
        file_key = "questions.json" if is_official else "newquestions.json"
        
        # Hae nykyinen data
        root_data = self.ipfs.get_json(self.root_cid)
        questions_cid = root_data["files"][file_key]
        questions_data = self.ipfs.get_json(questions_cid)
        
        # Lisää uusi kysymys
        if is_official:
            questions_data["questions"].append(question_data)
        else:
            questions_data["questions"].append(question_data)
        
        # Päivitä integrity hash
        questions_data["integrity"] = self._create_integrity_hash(questions_data)
        
        # Tallenna uusi versio
        new_cid = self.ipfs.add_json(questions_data)["Hash"]
        root_data["files"][file_key] = new_cid
        root_data["timestamp"] = datetime.now().isoformat()
        
        # Päivitä root
        self.root_cid = self.ipfs.add_json(root_data)["Hash"]
        
        return new_cid
    
    def add_candidate(self, candidate_data: Dict[str, Any]) -> str:
        """Lisää ehdokkaan"""
        root_data = self.ipfs.get_json(self.root_cid)
        candidates_cid = root_data["files"]["candidates.json"]
        candidates_data = self.ipfs.get_json(candidates_cid)
        
        # Lisää ehdokas
        candidates_data["candidates"].append(candidate_data)
        candidates_data["integrity"] = self._create_integrity_hash(candidates_data)
        
        # Tallenna
        new_cid = self.ipfs.add_json(candidates_data)["Hash"]
        root_data["files"]["candidates.json"] = new_cid
        root_data["timestamp"] = datetime.now().isoformat()
        
        self.root_cid = self.ipfs.add_json(root_data)["Hash"]
        
        return new_cid
    
    def get_election_data(self, file_name: str) -> Optional[Dict[str, Any]]:
        """Hakee vaalidataa tiedostonimellä"""
        if not self.root_cid:
            return None
            
        root_data = self.ipfs.get_json(self.root_cid)
        if file_name not in root_data["files"]:
            return None
            
        return self.ipfs.get_json(root_data["files"][file_name])
    
    def verify_integrity(self, data: Dict[str, Any]) -> bool:
        """Tarkistaa datan eheyden"""
        if 'integrity' not in data:
            return False
            
        stored_hash = data['integrity']['hash']
        data_without_integrity = {k: v for k, v in data.items() if k != 'integrity'}
        
        calculated_hash = self._create_integrity_hash(data_without_integrity)['hash']
        return stored_hash == calculated_hash

# Testauskoodi
def test_mock_ipfs():
    """Testaa MockIPFS-toiminnallisuutta"""
    
    print("🚀 ALKAA MOCK-IPFS TESTI")
    
    # Alusta MockIPFS
    ipfs = MockIPFS()
    manager = ElectionDataManager(ipfs)
    
    # 1. Alusta vaali
    meta_data = {
        "system": "Decentralized Candidate Matcher",
        "version": "1.0.0",
        "election": {
            "id": "test_election_2024",
            "country": "FI",
            "type": "municipal",
            "name": {
                "fi": "Testivaalit 2024",
                "en": "Test Election 2024"
            },
            "date": "2024-04-14",
            "language": "fi"
        }
    }
    
    root_cid = manager.initialize_election(meta_data)
    print(f"✅ Vaali alustettu - Root CID: {root_cid}")
    
    # 2. Lisää virallinen kysymys
    official_question = {
        "id": 1,
        "category": {"fi": "Ympäristö", "en": "Environment"},
        "question": {
            "fi": "Pitäisikö kaupungin vähentää hiilidioksidipäästöjä?",
            "en": "Should the city reduce carbon emissions?"
        },
        "scale": {
            "min": -5,
            "max": 5,
            "labels": {
                "fi": {
                    "-5": "Täysin eri mieltä",
                    "0": "Neutraali", 
                    "5": "Täysin samaa mieltä"
                }
            }
        }
    }
    
    q_cid = manager.add_question(official_question, is_official=True)
    print(f"✅ Virallinen kysymys lisätty - CID: {q_cid}")
    
    # 3. Lisää käyttäjän kysymys
    user_question = {
        "id": "user_123456789",
        "category": {"fi": "Liikenne", "en": "Transportation"},
        "question": {
            "fi": "Pitäisikö pyöräteitä parantaa?",
            "en": "Should bicycle paths be improved?"
        },
        "scale": {
            "min": -5,
            "max": 5,
            "labels": {
                "fi": {
                    "-5": "Täysin eri mieltä",
                    "0": "Neutraali", 
                    "5": "Täysin samaa mieltä"
                }
            }
        },
        "submission": {
            "user_public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIuser123",
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
    }
    
    user_q_cid = manager.add_question(user_question, is_official=False)
    print(f"✅ Käyttäjän kysymys lisätty - CID: {user_q_cid}")
    
    # 4. Lisää ehdokas
    candidate = {
        "id": 1,
        "name": "Matti Testi",
        "party": "Test Puolue",
        "district": "Helsinki",
        "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIcandidate1",
        "answer_cid": "QmAnswers123",
        "verified": True
    }
    
    candidate_cid = manager.add_candidate(candidate)
    print(f"✅ Ehdokas lisätty - CID: {candidate_cid}")
    
    # 5. Hae ja näytä data
    print("\n📊 HAETAAN VAALIDATAA:")
    
    questions = manager.get_election_data("questions.json")
    print(f"Virallisia kysymyksiä: {len(questions['questions'])}")
    
    new_questions = manager.get_election_data("newquestions.json")
    print(f"Käyttäjien kysymyksiä: {len(new_questions['questions'])}")
    
    candidates = manager.get_election_data("candidates.json")
    print(f"Ehdokkaita: {len(candidates['candidates'])}")
    
    # 6. Tarkista eheys
    print("\n🔒 EHETYSTARKISTUS:")
    for data in [questions, new_questions, candidates]:
        is_valid = manager.verify_integrity(data)
        print(f"Data eheys: {is_valid}")
    
    # 7. Näytä statistiikat
    print(f"\n📈 MOCK-IPFS STATISTIIKAT:")
    stats = ipfs.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n📌 PINNATTUJA CIDEJÄ: {len(ipfs.pins)}")
    
    print("\n🎉 MOCK-IPFS TESTI SUORITETTU ONNISTUNEESTI!")

if __name__ == "__main__":
    test_mock_ipfs()
