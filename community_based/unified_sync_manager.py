# unified_sync_manager.py
class UnifiedSyncManager:
    def __init__(self):
        self.question_pipeline = QuestionPipeline()
        self.candidate_pipeline = CandidatePipeline()
        self.question_ipfs_sync = IPFSSyncPipeline()
        self.candidate_ipfs_sync = CandidateIPFSSync()
        self.system_chain = SystemChainManager()
        
    def full_sync_cycle(self):
        """Suorita täysi synkronointisykli molemmille"""
        print("=== ALKAA TÄYSI SYNKRONOINTISYKLI ===")
        
        # 1. Synkronoi uudet kysymykset
        new_questions = self.question_pipeline.sync_new_to_main()
        
        # 2. Synkronoi uudet ehdokkaat
        new_candidates = self.candidate_pipeline.sync_new_candidates_to_main()
        
        changes_detected = False
        
        if new_questions > 0:
            # 3. Synkronoi questions.json → IPFS
            questions_cid = self.question_ipfs_sync.sync_questions_to_ipfs()
            changes_detected = True
            
            self.system_chain.add_block(
                operation="SYNC_NEW_QUESTIONS",
                files_affected=["questions.json", "ipfs_questions.json"],
                metadata={"new_questions": new_questions, "ipfs_cid": questions_cid}
            )
            
        if new_candidates > 0:
            # 4. Synkronoi candidate_profiles.json → IPFS
            candidates_cid = self.candidate_ipfs_sync.sync_candidates_to_ipfs()
            changes_detected = True
            
            self.system_chain.add_block(
                operation="SYNC_NEW_CANDIDATES",
                files_affected=["candidate_profiles.json", "ipfs_candidate_profiles.json"],
                metadata={"new_candidates": new_candidates, "ipfs_cid": candidates_cid}
            )
            
        if not changes_detected:
            # 5. Synkronoi ajoituksesta riippumatta tärkeät tiedot
            questions_cid = self.question_ipfs_sync.sync_questions_to_ipfs()
            candidates_cid = self.candidate_ipfs_sync.sync_candidates_to_ipfs()
            
            self.system_chain.add_block(
                operation="ROUTINE_SYNC",
                files_affected=["questions.json", "candidate_profiles.json"],
                metadata={"ipfs_cid_questions": questions_cid, "ipfs_cid_candidates": candidates_cid}
            )
            
        print("=== TÄYSI SYNKRONOINTISYKLI VALMIS ===")
        
    def add_candidate_with_answers(self, candidate_data, answers):
        """Lisää ehdokas ja hänen vastauksensa kerralla"""
        # 1. Lisää ehdokas
        candidate_id = self.candidate_pipeline.add_new_candidate_profile(candidate_data)
        
        # 2. Lisää vastaukset
        for answer in answers:
            self.candidate_pipeline.add_candidate_answer(
                candidate_id, 
                answer['question_id'], 
                answer
            )
        
        # 3. Synkronoi
        self.candidate_pipeline.sync_new_candidates_to_main()
        
        return candidate_id
