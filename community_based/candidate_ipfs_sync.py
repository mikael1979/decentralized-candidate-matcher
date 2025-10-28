# candidate_ipfs_sync.py
class CandidateIPFSSync:
    def __init__(self, runtime_dir="runtime"):
        self.runtime_dir = runtime_dir
        
    def sync_candidates_to_ipfs(self):
        """Synkronoi candidate_profiles.json → ipfs_candidate_profiles.json → IPFS"""
        # 1. Lataa candidate_profiles.json
        profiles = self._load_json('candidate_profiles.json')
        
        # 2. Päivitä ipfs_candidate_profiles.json
        ipfs_profiles = {
            "metadata": {
                "synced_at": datetime.now().isoformat(),
                "source_hash": self._calculate_hash(profiles),
                "total_candidates": len(profiles['candidates']),
                "total_answers": self._count_total_answers(profiles),
                "ipfs_cid": None
            },
            "candidates": profiles['candidates']
        }
        
        # 3. Tallenna ipfs_candidate_profiles.json
        self._save_json('ipfs_candidate_profiles.json', ipfs_profiles)
        
        # 4. Lähetä IPFS:ään
        ipfs_cid = self._upload_to_ipfs(ipfs_profiles)
        ipfs_profiles['metadata']['ipfs_cid'] = ipfs_cid
        
        # 5. Päivitä ipfs_candidate_profiles.json CID:llä
        self._save_json('ipfs_candidate_profiles.json', ipfs_profiles)
        
        # 6. Päivitä meta.json
        meta = self._load_json('meta.json')
        if 'ipfs_candidates_cid' not in meta:
            meta['ipfs_candidates_cid'] = {}
        meta['ipfs_candidates_cid'] = ipfs_cid
        meta['last_candidate_sync'] = datetime.now().isoformat()
        self._save_json('meta.json', meta)
        
        print(f"Ehdokkaat synkronoitu IPFS:ään CID: {ipfs_cid}")
        return ipfs_cid
        
    def sync_ipfs_to_candidates(self):
        """Synkronoi IPFS → ipfs_candidate_profiles.json → candidate_profiles.json"""
        # 1. Hae viimeisin CID meta.json:sta
        meta = self._load_json('meta.json')
        cid = meta.get('ipfs_candidates_cid')
        
        if not cid:
            print("Ei CID:ä saatavilla ehdokkaille")
            return None
            
        # 2. Hae data IPFS:stä
        ipfs_data = self._download_from_ipfs(cid)
        
        # 3. Tallenna väliaikaisesti
        self._save_json('tmp_ipfs_candidate_profiles.json', ipfs_data)
        
        # 4. Merge candidate_profiles.json:iin
        local_profiles = self._load_json('candidate_profiles.json')
        
        # Yksinkertainen merge: korvaa koko sisältö
        # Tässä voisi olla älykkäämpi konfliktien hallinta
        local_profiles['candidates'] = ipfs_data['candidates']
        local_profiles['metadata']['last_ipfs_sync'] = datetime.now().isoformat()
        local_profiles['metadata']['total_candidates'] = len(ipfs_data['candidates'])
        
        # 5. Tallenna candidate_profiles.json
        self._save_json('candidate_profiles.json', local_profiles)
        
        # 6. Vahvista synkronointi
        self._save_json('ipfs_candidate_profiles.json', ipfs_data)
        
        print(f"Ehdokkaat synkronoitu IPFS:stä CID: {cid}")
        return cid
