API-Dokumentaatio (Markdown-versio)Tämä dokumentaatio kattaa Decentralized Candidate Matcher (DCM) -backendin kaikki API-endpointit. API on rakennettu Flaskillä ja käyttää JSON-muotoa. Kaikki endpointit ovat suojattuja admin-kirjautumisella (paitsi julkiset GETit). Käytä Authorization: Bearer <token> tai session-pohjaista authia.Yleiset HuomiotBase URL: http://localhost:5000/api (kehitys) tai tuotanto-URL.
Autentikointi: Admin-endpointit vaativat kirjautumisen (POST /api/admin/login body: { "password": "salasana" }). Käytä sessionia tai JWT:tä.
Virheet: Palauttaa { "success": false, "error": "viesti" } status 400/401/404/500.
Parametrit: Query (?key=value), Body (JSON), Path (/<id>).
Vastaukset: Aina JSON, { "success": true, ... }.

Endpoint-Ryhmät1. Admin-KirjautuminenPOST /api/admin/loginKuvaus: Kirjautuu adminina.
Body: { "password": string } (pakollinen).
Vastaus: 200: { "success": true, "message": string }; 401: unauthorized.

POST /api/admin/logoutKuvaus: Uloskirjautuminen.
Vastaus: 200: { "success": true, "message": string }.

GET /api/admin/statusKuvaus: Tarkistaa admin-statuksen.
Vastaus: { "authenticated": bool, "login_time": string }.

2. Kysymysten Hallinta (Admin)GET /api/admin/questionsKuvaus: Hakee kaikki kysymykset (ml. blokatut).
Vastaus: Array of questions (JSON-objektit).

POST /api/admin/block_questionKuvaus: Blokkaa kysymys.
Body: { "question_id": int/string, "reason": string (opt) }.
Vastaus: { "success": bool, "message": string }.

POST /api/admin/unblock_questionKuvaus: Poistaa blokkaus.
Body: { "question_id": int/string }.
Vastaus: { "success": bool, "message": string }.

POST /api/admin/elo_updateKuvaus: Päivittää Elo-arvo manuaalisesti.
Body: { "question_id": int/string, "delta": int, "user_id": string (opt) }.
Vastaus: { "success": bool, "message": string }.

GET /api/admin/questions/elo_rankingKuvaus: Kysymykset Elo-järjestyksessä.
Vastaus: Array of questions (sorted by Elo).

GET /api/admin/questions/select_for_syncKuvaus: Valitsee kysymykset synkronointiin.
Query: strategy (string, opt: balanced), limit (int, opt: 20).
Vastaus: { "questions": array, "strategy": string, "limit": int }.

3. IPFS ja Synkronointi (Admin)GET /api/admin/ipfs_sync_queueKuvaus: Hakee synkronointijonon.
Vastaus: Queue-objekti (JSON).

POST /api/admin/process_ipfs_syncKuvaus: Käsittelee synkronointi manuaalisesti.
Vastaus: { "success": bool, "message": string }.

POST /api/admin/fetch_ipfs_questionsKuvaus: Hakee kysymykset IPFS:stä.
Vastaus: { "success": bool, "message": string }.

4. Asetukset (Admin)GET /api/admin/settingsKuvaus: Hakee asetukset.
Vastaus: Settings-objekti (election, community_moderation, system).

POST /api/admin/settingsKuvaus: Päivittää asetukset.
Body: { "election": obj, "community_moderation": obj, "system": obj }.
Vastaus: { "success": bool, "message": string }; 400 virheellisillä arvoilla.

5. Ehdokkaiden Hallinta (Admin)GET /api/candidate/<candidate_id>/profileKuvaus: Hakee ehdokkaan profiili.
Vastaus: { "candidate": obj }.

PUT /api/candidate/<candidate_id>/answersKuvaus: Päivittää vastaukset.
Body: { "answers": array of {question_id, answer, confidence, justification} }.
Vastaus: { "success": bool, "message": string }.

PUT /api/candidate/<candidate_id>/profileKuvaus: Päivittää profiili (name, district).
Body: { "name": string, "district": string }.
Vastaus: { "success": bool, "message": string }.

6. Puolueiden Hallinta (Admin)GET /api/party/<party_name>/candidatesKuvaus: Hakee puolueen ehdokkaat.
Vastaus: { "candidates": array, "count": int }.

POST /api/party/<party_name>/candidatesKuvaus: Lisää ehdokas puolueelle.
Body: { "name": string, "district": string, "answers": array }.
Vastaus: { "success": bool, "candidate_id": int }.

PUT /api/party/<party_name>/candidate/<candidate_id>Kuvaus: Päivittää ehdokas.
Body: { "name": string, "district": string, "answers": array }.
Vastaus: { "success": bool, "message": string }.

DELETE /api/party/<party_name>/candidate/<candidate_id>Kuvaus: Poistaa ehdokas (soft delete).
Vastaus: { "success": bool, "message": string }.

7. Julkiset ReititGET /api/metaKuvaus: Järjestelmän meta-tiedot.
Vastaus: Meta-objekti.

GET /api/system_infoKuvaus: Järjestelmätiedot ja tilastot.
Vastaus: { "system_name": string, "version": string, "election": obj, "stats": obj }.

GET /api/questionsKuvaus: Kaikki kysymykset.
Vastaus: Array of questions.

GET /api/candidatesKuvaus: Kaikki ehdokkaat.
Vastaus: Array of candidates.

GET /api/partiesKuvaus: Kaikki puolueet.
Vastaus: Array of party names.

GET /api/party/<party_name>Kuvaus: Puolueen profiili ja konsensus.
Vastaus: { "profile": obj, "consensus": obj }.

POST /api/submit_questionKuvaus: Lähetä uusi kysymys.
Body: { "question": { "fi": string }, "category": string, "tags": array, "scale": obj }.
Vastaus: { "success": bool, "cid": string }.

GET /api/search_questionsKuvaus: Hae kysymyksiä.
Query: q (string).
Vastaus: { "results": array }.

GET /api/available_tagsKuvaus: Käytössä olevat tagit.
Vastaus: { "tags": obj (tag: count) }.

POST /api/compare_partiesKuvaus: Vertaile käyttäjän vastauksia puolueeseen.
Body: { "user_answers": { qid: int }, "party_name": string }.
Vastaus: { "match_percentage": float, "candidate_count": int }.

POST /api/compare_all_partiesKuvaus: Vertaile kaikkiin puolueisiin.
Body: { "user_answers": { qid: int } }.
Vastaus: Array of { party, match_percentage } (sorted).


