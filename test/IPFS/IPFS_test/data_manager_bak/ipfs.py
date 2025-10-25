from datetime import datetime

class IPFSMixin:
    def queue_for_ipfs_sync(self, question_id):
        queue = self.ensure_data_file('ipfs_sync_queue.json')
        all_questions = self.get_questions(include_blocked=True, include_ipfs=False)
        question = next((q for q in all_questions if q.get('id') == question_id), None)
        if not question:
            return False
        queue['pending_questions'].append({
            'question_id': question_id,
            'added_to_queue_at': datetime.now().isoformat(),
            'elo_rating': question.get('elo', {}).get('current_rating', 1200),
            'status': 'pending'
        })
        return self.write_json('ipfs_sync_queue.json', queue, "Kysymys lisätty synkronointijonoon")

    def process_ipfs_sync(self):
        queue = self.ensure_data_file('ipfs_sync_queue.json')
        if not queue.get('pending_questions'):
            return False
        last_sync = queue.get('last_sync')
        interval = queue.get('sync_interval_minutes', 10)
        if last_sync:
            last_sync_time = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
            if (datetime.now() - last_sync_time).total_seconds() < interval * 60:
                return False
        max_sync = queue.get('max_questions_per_sync', 20)
        pending = [q for q in queue['pending_questions'] if q['status'] == 'pending']
        selection_mode = self.get_meta().get('community_moderation', {}).get('ipfs_sync_mode', 'elo_priority')
        if selection_mode == 'elo_priority':
            pending.sort(key=lambda x: x.get('elo_rating', 1200), reverse=True)
        else:
            pending.sort(key=lambda x: x.get('added_to_queue_at', ''))
        selected = pending[:max_sync]
        if self.ipfs_client and selected:
            ipfs_questions = []
            all_questions = self.get_questions(include_blocked=True, include_ipfs=False)
            for item in selected:
                question = next((q for q in all_questions if q.get('id') == item['question_id']), None)
                if question:
                    ipfs_questions.append(question)
            if ipfs_questions:
                ipfs_data = {
                    "election_id": self.get_meta().get("election", {}).get("id"),
                    "timestamp": datetime.now().isoformat(),
                    "questions": ipfs_questions
                }
                result = self.ipfs_client.add_json(ipfs_data)
                if result:
                    for item in selected:
                        item['status'] = 'synced'
                        item['synced_at'] = datetime.now().isoformat()
                        item['ipfs_cid'] = result["Hash"]
                    queue['last_sync'] = datetime.now().isoformat()
                    queue['pending_questions'] = [q for q in queue['pending_questions'] if q not in selected] + selected
                    self.write_json('ipfs_sync_queue.json', queue, f"Synkronoitu {len(selected)} kysymystä IPFS:iin")
                    return True
        return False

    def fetch_questions_from_ipfs(self):
        if not self.ipfs_client:
            return False
        try:
            well_known_cid = "QmWellKnownQuestionsList"
            ipfs_data = self.ipfs_client.get_json(well_known_cid)
            if ipfs_data:
                cache = {
                    "last_fetch": datetime.now().isoformat(),
                    "questions": ipfs_data.get("questions", [])
                }
                self.write_json("ipfs_questions_cache.json", cache, "IPFS-kysymykset välimuistiin")
                return True
            return False
        except Exception as e:
            if self.debug:
                print(f"❌ IPFS-haku epäonnistui: {e}")
            return False
