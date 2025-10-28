# complete_bidirectional_sync.py
class CompleteBidirectionalSync:
    def __init__(self, sync_manager):
        self.sync_manager = sync_manager
    
    def full_sync_cycle(self):
        """Suorittaa täydellisen kaksisuuntaisen synkronointisyklin"""
        print("=== ALKAA TÄYSI KAKSISUUNTAINEN SYNKRONOINTI ===")
        
        sync_results = {
            'local_to_ipfs': None,
            'ipfs_to_local': None,
            'timestamp': self.sync_manager._get_current_timestamp()
        }
        
        # 1. Synkronoi paikalliset kysymykset IPFS:ään
        try:
            sync_results['local_to_ipfs'] = self.sync_manager.sync_questions_to_ipfs()
        except Exception as e:
            print(f"Virhe paikallisesta IPFS:ään synkronoinnissa: {e}")
            sync_results['local_to_ipfs_error'] = str(e)
        
        # 2. Synkronoi IPFS:stä paikalliseen
        try:
            sync_results['ipfs_to_local'] = self.sync_manager.sync_ipfs_to_questions()
        except Exception as e:
            print(f"Virhe IPFS:stä paikalliseen synkronoinnissa: {e}")
            sync_results['ipfs_to_local_error'] = str(e)
        
        # 3. Päivitä system_chain
        self._update_system_chain(sync_results)
        
        # 4. Raportoi tilastoja
        self._report_sync_statistics(sync_results)
        
        print("=== KAKSISUUNTAINEN SYNKRONOINTI VALMIS ===")
        return sync_results
    
    def _update_system_chain(self, sync_results):
        """Päivittää system_chain.json synkronointitiedolla"""
        system_chain = self.sync_manager._load_json('system_chain.json')
        
        new_block = {
            "block_id": len(system_chain.get('blocks', [])),
            "timestamp": sync_results['timestamp'],
            "operation": "bidirectional_sync",
            "sync_results": sync_results,
            "files_affected": ["questions.json", "ipfs_questions.json"],
            "previous_hash": system_chain.get('blocks', [{}])[-1].get('block_hash', ''),
            "block_hash": self.sync_manager._generate_cid_for_questions([sync_results])
        }
        
        system_chain.setdefault('blocks', []).append(new_block)
        system_chain['current_state']['last_sync'] = sync_results['timestamp']
        system_chain['current_state']['questions_count'] = len(
            self.sync_manager._load_json('questions.json').get('questions', [])
        )
        
        self.sync_manager._save_json('system_chain.json', system_chain)
    
    def _report_sync_statistics(self, sync_results):
        """Raportoi synkronointitilastoja"""
        questions_data = self.sync_manager._load_json('questions.json')
        ipfs_questions_data = self.sync_manager._load_json('ipfs_questions.json')
        
        total_questions = len(questions_data.get('questions', []))
        local_questions = len([q for q in questions_data.get('questions', []) 
                             if q.get('source') in ['local', 'local_synced']])
        ipfs_questions = len([q for q in questions_data.get('questions', []) 
                            if q.get('source') == 'ipfs_imported'])
        
        print("\n=== SYNKRONOINTITILASTOT ===")
        print(f"Kysymyksiä yhteensä: {total_questions}")
        print(f"Paikallisia kysymyksiä: {local_questions}")
        print(f"IPFS:stä tuotuja kysymyksiä: {ipfs_questions}")
        print(f"IPFS:ään synkronoitu: {sync_results['local_to_ipfs'] is not None}")
        print(f"IPFS:stä tuotu: {sync_results['ipfs_to_local'] or 0} uutta kysymystä")
