# ipfs_sync.py
class IPFSSyncPipeline:
    def __init__(self, runtime_dir="runtime"):
        self.runtime_dir = runtime_dir
        
    def sync_questions_to_ipfs(self):
        """Synkronoi questions.json → ipfs_questions.json → IPFS"""
        # 1. Lataa questions.json
        questions = self._load_json('questions.json')
        
        # 2. Päivitä ipfs_questions.json (paikallinen IPFS-mirror)
        ipfs_questions = {
            "metadata": {
                "synced_at": datetime.now().isoformat(),
                "source_hash": self._calculate_hash(questions),
                "ipfs_cid": None
            },
            "data": questions['data']
        }
        
        # 3. Tallenna ipfs_questions.json
        self._save_json('ipfs_questions.json', ipfs_questions)
        
        # 4. Lähetä IPFS:ään (simuloitu)
        ipfs_cid = self._upload_to_ipfs(ipfs_questions)
        ipfs_questions['metadata']['ipfs_cid'] = ipfs_cid
        
        # 5. Päivitä ipfs_questions.json CID:llä
        self._save_json('ipfs_questions.json', ipfs_questions)
        
        # 6. Päivitä meta.json
        meta = self._load_json('meta.json')
        meta['ipfs_questions_cid'] = ipfs_cid
        meta['last_ipfs_sync'] = datetime.now().isoformat()
        self._save_json('meta.json', meta)
        
        print(f"Synkronoitu IPFS:ään CID: {ipfs_cid}")
        return ipfs_cid
        
    def sync_ipfs_to_local(self):
        """Synkronoi IPFS → ipfs_questions.json → questions.json"""
        # 1. Hae viimeisin CID meta.json:sta
        meta = self._load_json('meta.json')
        cid = meta.get('ipfs_questions_cid')
        
        if not cid:
            print("Ei CID:ä saatavilla")
            return None
            
        # 2. Hae data IPFS:stä (simuloitu)
        ipfs_data = self._download_from_ipfs(cid)
        
        # 3. Tallenna ipfs_questions.json
        self._save_json('tmp_ipfs_questions.json', ipfs_data)
        
        # 4. Vertaile ja merge questions.json:iin
        local_questions = self._load_json('questions.json')
        
        # Yksinkertainen merge-strategia: korvaa koko sisältö
        # Tässä voisi olla älykkäämpi konfliktien hallinta
        local_questions['data'] = ipfs_data['data']
        local_questions['metadata']['last_ipfs_sync'] = datetime.now().isoformat()
        
        # 5. Tallenna questions.json
        self._save_json('questions.json', local_questions)
        
        # 6. Vahvista synkronointi
        self._save_json('ipfs_questions.json', ipfs_data)
        
        print(f"Synkronoitu IPFS:stä CID: {cid}")
        return cid
