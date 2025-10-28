# cid_sync_manager.py
class CIDSyncManager:
    def __init__(self, runtime_dir="runtime", local_system_id=None):
        self.runtime_dir = runtime_dir
        self.local_system_id = local_system_id or self._generate_system_id()
    
    def sync_questions_to_ipfs(self):
        """Synkronoi vain paikallisesti lisätyt kysymykset IPFS:ään"""
        print("=== QUESTIONS.JSON → IPFS_QUESTIONS.JSON SYNKRONOINTI ===")
        
        # 1. Lataa questions.json
        questions_data = self._load_json('questions.json')
        
        # 2. Erota paikallisesti lisätyt kysymykset (joilla ei ole CID:ä)
        local_questions = [
            q for q in questions_data.get('questions', []) 
            if q.get('ipfs_cid') is None and q.get('source') == 'local'
        ]
        
        if not local_questions:
            print("Ei uusia paikallisia kysymyksiä synkronoitavaksi")
            return None
        
        print(f"Löydetty {len(local_questions)} uutta paikallista kysymystä")
        
        # 3. Lataa nykyinen ipfs_questions.json
        ipfs_questions = self._load_json('ipfs_questions.json')
        
        # 4. Lisää uudet kysymykset ipfs_questions.json:iin
        for question in local_questions:
            # Generoi CID paikalliselle kysymykselle
            cid = self._generate_cid_for_question(question)
            question['ipfs_cid'] = cid
            question['source'] = 'local_synced'
            question['timestamps']['synced_to_ipfs'] = self._get_current_timestamp()
            
            # Lisää IPFS-kysymyksiin
            ipfs_questions.setdefault('questions', []).append(question)
        
        # 5. Päivitä ipfs_questions.json metadata
        ipfs_questions['metadata'] = {
            'local_system_id': self.local_system_id,
            'last_sync': self._get_current_timestamp(),
            'total_questions': len(ipfs_questions.get('questions', [])),
            'last_cid_batch': self._generate_cid_for_questions(ipfs_questions['questions'])
        }
        
        # 6. Tallenna ipfs_questions.json
        self._save_json('ipfs_questions.json', ipfs_questions)
        
        # 7. Päivitä questions.json CID:illä
        self._update_questions_with_cids(local_questions)
        
        # 8. Synkronoi ipfs_questions.json IPFS-verkkoon
        ipfs_cid = self._upload_to_ipfs(ipfs_questions)
        
        # 9. Päivitä meta.json
        self._update_meta_ipfs_reference('questions', ipfs_cid)
        
        print(f"Synkronoitu {len(local_questions)} uutta kysymystä IPFS:ään CID: {ipfs_cid}")
        return ipfs_cid
    
    def sync_ipfs_to_questions(self):
        """Synkronoi IPFS:stä tuodut kysymykset questions.json:iin"""
        print("=== IPFS_QUESTIONS.JSON → QUESTIONS.JSON SYNKRONOINTI ===")
        
        # 1. Hae viimeisin IPFS CID
        meta = self._load_json('meta.json')
        cid = meta.get('ipfs_references', {}).get('questions_latest')
        
        if not cid:
            print("Ei CID:ä saatavilla IPFS-synkronointiin")
            return None
        
        # 2. Lataa data IPFS:stä
        ipfs_data = self._download_from_ipfs(cid)
        
        if not ipfs_data:
            print("Ei dataa saatavilla IPFS:stä")
            return None
        
        # 3. Lataa paikallinen questions.json
        local_questions = self._load_json('questions.json')
        local_questions_map = {q['local_id']: q for q in local_questions.get('questions', [])}
        
        # 4. Suodata vain IPFS-kysymykset, joita ei vielä ole paikallisesti
        new_questions = []
        for ipfs_question in ipfs_data.get('questions', []):
            ipfs_cid = ipfs_question.get('ipfs_cid')
            local_id = ipfs_question.get('local_id')
            
            # Tarkista onko kysymys jo paikallisesti
            if local_id in local_questions_map:
                existing = local_questions_map[local_id]
                # Päivitä vain jos IPFS-versio on uudempi
                if (ipfs_question['timestamps']['synced_to_ipfs'] > 
                    existing['timestamps'].get('synced_to_ipfs', '1970-01-01')):
                    existing.update(ipfs_question)
            else:
                # Uusi kysymys IPFS:stä
                ipfs_question['source'] = 'ipfs_imported'
                ipfs_question['timestamps']['imported_from_ipfs'] = self._get_current_timestamp()
                new_questions.append(ipfs_question)
        
        # 5. Lisää uudet kysymykset paikalliseen questions.json:iin
        if new_questions:
            local_questions.setdefault('questions', []).extend(new_questions)
            local_questions['metadata']['last_updated'] = self._get_current_timestamp()
            local_questions['metadata']['last_ipfs_import'] = self._get_current_timestamp()
            
            # Tallenna päivitetty questions.json
            self._save_json('questions.json', local_questions)
            
            print(f"Tuotu {len(new_questions)} uutta kysymystä IPFS:stä")
        else:
            print("Ei uusia kysymyksiä IPFS:stä")
        
        return len(new_questions)
    
    def _update_questions_with_cids(self, questions_with_cids):
        """Päivittää questions.json tiedoston kysymyksiin CID:t"""
        questions_data = self._load_json('questions.json')
        questions_map = {q['local_id']: q for q in questions_data.get('questions', [])}
        
        for question in questions_with_cids:
            local_id = question['local_id']
            if local_id in questions_map:
                questions_map[local_id]['ipfs_cid'] = question['ipfs_cid']
                questions_map[local_id]['source'] = question['source']
                questions_map[local_id]['timestamps']['synced_to_ipfs'] = question['timestamps']['synced_to_ipfs']
        
        # Päivitä metadata
        questions_data['metadata']['last_updated'] = self._get_current_timestamp()
        questions_data['metadata']['last_sync'] = self._get_current_timestamp()
        questions_data['metadata']['sync_status']['ipfs_synced'] = True
        questions_data['metadata']['sync_status']['local_modified'] = False
        
        self._save_json('questions.json', questions_data)
    
    def _generate_cid_for_question(self, question):
        """Generoi CID:n yksittäiselle kysymykselle"""
        import hashlib
        question_string = json.dumps(question, sort_keys=True, ensure_ascii=False)
        return "Qm" + hashlib.sha256(question_string.encode('utf-8')).hexdigest()[:40]
    
    def _generate_cid_for_questions(self, questions):
        """Generoi CID:n kysymyskokoelmalle"""
        import hashlib
        questions_string = json.dumps(questions, sort_keys=True, ensure_ascii=False)
        return "Qm" + hashlib.sha256(questions_string.encode('utf-8')).hexdigest()[:40]
