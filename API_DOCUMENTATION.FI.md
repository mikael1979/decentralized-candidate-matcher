Alla on laajennettu ja tarkennettu Markdown-dokumentaatio Decentralized Candidate Matcher (DCM) -backendin API:lle. Tämä versio täydentää aiemman Markdown-dokumentaation tarjoamalla syvempää tietoa, esimerkkipyyntöjä ja -vastauksia, selkeät ohjeet frontend-kehittäjille sekä viittaukset Swagger-dokumentaatioon tekniseen testaukseen. Dokumentaatio on suunniteltu selkeäksi GitHubiin (esim. `API_DOCS.md`) ja se tukee kehittäjiä, jotka rakentavat frontendia tai integroivat API:n.

# Decentralized Candidate Matcher (DCM) API-Dokumentaatio

Tämä dokumentaatio kuvaa DCM-backendin RESTful API:n, joka tukee vaalidataan hallintaa, kysymysten moderointia, ehdokkaiden profiileja ja puolueiden vertailua. API on rakennettu Flaskillä ja käyttää JSON-muotoa pyynnöissä ja vastauksissa. Dokumentaatio kattaa sekä admin- että julkiset endpointit, autentikointimekanismit ja virhekäsittelyn.

## Sisällys
- [Yleiset tiedot](#yleiset-tiedot)
- [Autentikointi](#autentikointi)
- [Virhekäsittely](#virhekäsittely)
- [API-Endpointit](#api-endpointit)
  - [Admin: Kirjautuminen](#admin-kirjautuminen)
  - [Admin: Kysymysten hallinta](#admin-kysymysten-hallinta)
  - [Admin: IPFS ja synkronointi](#admin-ipfs-ja-synkronointi)
  - [Admin: Asetukset](#admin-asetukset)
  - [Ehdokkaiden hallinta](#ehdokkaiden-hallinta)
  - [Puolueiden hallinta](#puolueiden-hallinta)
  - [Julkiset endpointit](#julkiset-endpointit)
- [Esimerkkipyynnöt](#esimerkkipyynnöt)
- [Swagger-dokumentaatio](#swagger-dokumentaatio)
- [Vinkkejä frontend-kehittäjille](#vinkkejä-frontend-kehittäjille)

## Yleiset tiedot
- **Base URL**: Kehityksessä `http://localhost:5000/api`, tuotannossa korvaa oikealla URL:lla (esim. `https://api.dcm.example.com/api`).
- **Formaatti**: Kaikki pyynnöt ja vastaukset ovat JSON-muodossa (`Content-Type: application/json`).
- **Versiointi**: API:n nykyinen versio on 1.0.0.
- **Aikaleimat**: ISO 8601 -formaatissa (esim. `2025-10-23T17:06:00Z`).
- **Kieli**: Kysymysten tekstit tukevat monikielisyyttä (esim. `{ "fi": "teksti", "en": "text" }`). Oletus on `fi` (suomi).
- **IPFS-integraatio**: Kysymykset ja data voidaan synkronoida IPFS:ään, jolloin frontend voi hakea dataa suoraan IPFS-nodesta (CID-viittauksilla).

## Autentikointi
Useimmat admin-endpointit vaativat autentikoinnin. Kaksi menetelmää tuetaan:
1. **Session-pohjainen**:
   - Kirjaudu sisään `POST /api/admin/login` (palauttaa session-cookien).
   - Sisällytä cookie pyyntöihin (automaattisesti selaimessa, tai `Cookie: session=...`).
2. **JWT (Bearer Token)**:
   - Kirjautumisen jälkeen saat JWT-tokenin (`Authorization: Bearer <token>`).
   - Sisällytä headeriin: `Authorization: Bearer eyJ...`.

**Huomio**: Julkiset endpointit (`/api/questions`, `/api/candidates` jne.) eivät vaadi autentikointia.

## Virhekäsittely
Kaikki virhevastaukset noudattavat muotoa:
```json
{
  "success": false,
  "error": "Kuvaava virheviesti"
}
```
Yleiset statuskoodit:
- `400`: Virheellinen pyyntö (esim. puuttuva parametri).
- `401`: Autentikointi epäonnistui.
- `404`: Resurssia ei löydy (esim. ehdokas-ID ei olemassa).
- `500`: Palvelinvirhe (harvinainen, tarkista logit).

## API-Endpointit

### Admin: Kirjautuminen
#### `POST /api/admin/login`
Kirjautuu adminina sisään.
- **Body**:
  ```json
  {
    "password": "salasana123"
  }
  ```
- **Vastaus** (200):
  ```json
  {
    "success": true,
    "message": "Login successful",
    "token": "eyJ..." // JWT, jos käytössä
  }
  ```
- **Virheet**: 401 (väärä salasana).

#### `POST /api/admin/logout`
Uloskirjautuminen, mitätöi session tai tokenin.
- **Vastaus** (200):
  ```json
  {
    "success": true,
    "message": "Logged out"
  }
  ```

#### `GET /api/admin/status`
Tarkistaa adminin kirjautumistilan.
- **Vastaus** (200):
  ```json
  {
    "authenticated": true,
    "login_time": "2025-10-23T17:06:00Z"
  }
  ```

### Admin: Kysymysten hallinta
Kaikki endpointit vaativat autentikoinnin.

#### `GET /api/admin/questions`
Hakee kaikki kysymykset (myös blokatut).
- **Vastaus** (200):
  ```json
  [
    {
      "question_id": "q1",
      "question": { "fi": "Mitä mieltä olet ilmastopolitiikasta?" },
      "category": "Environment",
      "tags": ["climate", "policy"],
      "scale": { "min": -5, "max": 5 },
      "elo_rating": 1500,
      "blocked": false
    },
    ...
  ]
  ```

#### `POST /api/admin/block_question`
Blokkaa kysymys.
- **Body**:
  ```json
  {
    "question_id": "q1",
    "reason": "Inappropriate content"
  }
  ```
- **Vastaus** (200):
  ```json
  {
    "success": true,
    "message": "Question blocked"
  }
  ```
- **Virheet**: 400 (puuttuva `question_id`), 404 (kysymystä ei löydy).

#### `POST /api/admin/unblock_question`
Poistaa kysymyksen blokkauksen.
- **Body**:
  ```json
  {
    "question_id": "q1"
  }
  ```
- **Vastaus** (200):
  ```json
  {
    "success": true,
    "message": "Question unblocked"
  }
  ```

#### `POST /api/admin/elo_update`
Päivittää kysymyksen Elo-arvon manuaalisesti.
- **Body**:
  ```json
  {
    "question_id": "q1",
    "delta": 50,
    "user_id": "user123"
  }
  ```
- **Vastaus** (200):
  ```json
  {
    "success": true,
    "message": "Elo updated"
  }
  ```

#### `GET /api/admin/questions/elo_ranking`
Hakee kysymykset Elo-arvon mukaan järjestettynä.
- **Vastaus** (200): Kuten `/api/admin/questions`, mutta järjestettynä `elo_rating` laskevasti.

#### `GET /api/admin/questions/select_for_sync`
Valitsee kysymykset IPFS-synkronointiin.
- **Query-parametrit**:
  - `strategy` (string, oletus: `balanced`): Synkronointistrategia (esim. `elo_priority`, `fifo`).
  - `limit` (int, oletus: 20): Maksimimäärä kysymyksiä.
- **Vastaus** (200):
  ```json
  {
    "questions": [{ ... }], // Kuten /api/admin/questions
    "strategy": "balanced",
    "limit": 20
  }
  ```

### Admin: IPFS ja synkronointi
#### `GET /api/admin/ipfs_sync_queue`
Hakee IPFS-synkronointijonon tilan.
- **Vastaus** (200):
  ```json
  {
    "queue": [
      { "cid": "Qm...", "status": "pending", "data": { ... } },
      ...
    ]
  }
  ```

#### `POST /api/admin/process_ipfs_sync`
Käsittelee synkronointijonon manuaalisesti.
- **Vastaus** (200):
  ```json
  {
    "success": true,
    "message": "Sync processed"
  }
  ```

#### `POST /api/admin/fetch_ipfs_questions`
Hakee kysymykset IPFS:stä (käyttäen hyvin tunnettua CID:tä).
- **Vastaus** (200):
  ```json
  {
    "success": true,
    "message": "Questions fetched",
    "questions": [{ ... }]
  }
  ```

### Admin: Asetukset
#### `GET /api/admin/settings`
Hakee järjestelmän asetukset.
- **Vastaus** (200):
  ```json
  {
    "election": { "name": "Municipal Election 2025", "date": "2025-06-01" },
    "community_moderation": { "enabled": true, "threshold": 0.7 },
    "system": { "ipfs_enabled": true, "log_level": "DEBUG" }
  }
  ```

#### `POST /api/admin/settings`
Päivittää asetukset.
- **Body**:
  ```json
  {
    "election": { "name": "Updated Election", "date": "2025-06-01" },
    "community_moderation": { "enabled": true },
    "system": { "ipfs_enabled": true }
  }
  ```
- **Vastaus** (200):
  ```json
  {
    "success": true,
    "message": "Settings updated"
  }
  ```
- **Virheet**: 400 (virheellinen JSON tai arvot).

### Ehdokkaiden hallinta
#### `GET /api/candidate/<candidate_id>/profile`
Hakee ehdokkaan profiilin.
- **Esimerkki**: `/api/candidate/c1/profile`
- **Vastaus** (200):
  ```json
  {
    "candidate": {
      "candidate_id": "c1",
      "name": "Matti Meikäläinen",
      "district": "Helsinki",
      "party": "Green Party",
      "answers": [
        { "question_id": "q1", "answer": 3, "confidence": 0.8, "justification": "Support renewable energy" }
      ],
      "deleted": false
    }
  }
  ```
- **Virheet**: 404 (ehdokasta ei löydy).

#### `PUT /api/candidate/<candidate_id>/answers`
Päivittää ehdokkaan vastaukset (admin).
- **Body**:
  ```json
  {
    "answers": [
      { "question_id": "q1", "answer": 3, "confidence": 0.8, "justification": "Support renewable energy" }
    ]
  }
  ```
- **Vastaus** (200):
  ```json
  {
    "success": true,
    "message": "Answers updated"
  }
  ```
- **Validointi**: `answer` (-5..5), `confidence` (0..1).

#### `PUT /api/candidate/<candidate_id>/profile`
Päivittää ehdokkaan profiilin (admin).
- **Body**:
  ```json
  {
    "name": "Matti Meikäläinen",
    "district": "Helsinki"
  }
  ```
- **Vastaus** (200):
  ```json
  {
    "success": true,
    "message": "Profile updated"
  }
  ```

### Puolueiden hallinta
#### `GET /api/party/<party_name>/candidates`
Hakee puolueen ehdokkaat.
- **Esimerkki**: `/api/party/Green%20Party/candidates`
- **Vastaus** (200):
  ```json
  {
    "candidates": [{ ... }], // Kuten /api/candidate/<id>/profile
    "count": 10
  }
  ```

#### `POST /api/party/<party_name>/candidates`
Lisää ehdokas puolueelle (admin).
- **Body**:
  ```json
  {
    "name": "Matti Meikäläinen",
    "district": "Helsinki",
    "answers": [{ "question_id": "q1", "answer": 3, "confidence": 0.8 }]
  }
  ```
- **Vastaus** (200):
  ```json
  {
    "success": true,
    "candidate_id": "c1"
  }
  ```

#### `PUT /api/party/<party_name>/candidate/<candidate_id>`
Päivittää ehdokkaan tiedot (admin).
- **Body**: Kuten `POST /api/party/<party_name>/candidates`.
- **Vastaus** (200):
  ```json
  {
    "success": true,
    "message": "Candidate updated"
  }
  ```

#### `DELETE /api/party/<party_name>/candidate/<candidate_id>`
Poistaa ehdokkaan (soft delete, admin).
- **Vastaus** (200):
  ```json
  {
    "success": true,
    "message": "Candidate deleted"
  }
  ```
- **Virheet**: 404 (ehdokasta ei löydy).

### Julkiset endpointit
#### `GET /api/meta`
Hakee järjestelmän metatiedot.
- **Vastaus** (200):
  ```json
  {
    "system_name": "DCM",
    "version": "1.0.0",
    "description": "Decentralized Candidate Matcher"
  }
  ```

#### `GET /api/system_info`
Hakee järjestelmän tiedot ja tilastot.
- **Vastaus** (200):
  ```json
  {
    "system_name": "DCM",
    "version": "1.0.0",
    "election": { "name": "Municipal Election 2025", "date": "2025-06-01" },
    "stats": { "question_count": 100, "candidate_count": 500 }
  }
  ```

#### `GET /api/questions`
Hakee kaikki julkiset (ei-blokatut) kysymykset.
- **Vastaus** (200): Kuten `/api/admin/questions`, mutta ilman `blocked: true`.

#### `GET /api/candidates`
Hakee kaikki aktiiviset ehdokkaat.
- **Vastaus** (200):
  ```json
  [
    { "candidate_id": "c1", "name": "Matti Meikäläinen", ... },
    ...
  ]
  ```

#### `GET /api/parties`
Hakee kaikkien puolueiden nimet.
- **Vastaus** (200):
  ```json
  ["Green Party", "Blue Party", ...]
  ```

#### `GET /api/party/<party_name>`
Hakee puolueen profiilin ja konsensusvastaukset.
- **Vastaus** (200):
  ```json
  {
    "profile": { "description": "Eco-friendly policies" },
    "consensus": { "q1": 4, "q2": -2 }
  }
  ```

#### `POST /api/submit_question`
Lähettää uuden kysymyksen (julkinen, moderoidaan).
- **Body**:
  ```json
  {
    "question": { "fi": "Mitä mieltä olet ilmastopolitiikasta?" },
    "category": "Environment",
    "tags": ["climate", "policy"],
    "scale": { "min": -5, "max": 5 }
  }
  ```
- **Vastaus** (200):
  ```json
  {
    "success": true,
    "cid": "Qm..."
  }
  ```

#### `GET /api/search_questions`
Hakee kysymyksiä hakusanalla.
- **Query**: `q=climate`
- **Vastaus** (200):
  ```json
  {
    "results": [{ ... }] // Kuten /api/questions
  }
  ```

#### `GET /api/available_tags`
Hakee käytetyt tagit ja niiden määrät.
- **Vastaus** (200):
  ```json
  {
    "tags": { "climate": 10, "policy": 15 }
  }
  ```

#### `POST /api/compare_parties`
Vertailee käyttäjän vastauksia puolueeseen.
- **Body**:
  ```json
  {
    "user_answers": { "q1": 3, "q2": -1 },
    "party_name": "Green Party"
  }
  ```
- **Vastaus** (200):
  ```json
  {
    "match_percentage": 85.5,
    "candidate_count": 10
  }
  ```

#### `POST /api/compare_all_parties`
Vertailee käyttäjän vastauksia kaikkiin puolueisiin.
- **Body**:
  ```json
  {
    "user_answers": { "q1": 3, "q2": -1 }
  }
  ```
- **Vastaus** (200):
  ```json
  [
    { "party": "Green Party", "match_percentage": 85.5 },
    { "party": "Blue Party", "match_percentage": 60.2 },
    ...
  ]
  ```

## Esimerkkipyynnöt
### Kirjautuminen (cURL)
```bash
curl -X POST http://localhost:5000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"password": "salasana123"}'
```

### Kysymysten haku (JavaScript/Fetch)
```javascript
fetch('http://localhost:5000/api/questions', {
  method: 'GET',
  headers: { 'Content-Type': 'application/json' }
})
  .then(res => res.json())
  .then(data => console.log(data));
```

### Ehdokkaan vastausten päivitys (admin)
```bash
curl -X PUT http://localhost:5000/api/candidate/c1/answers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d '{"answers": [{"question_id": "q1", "answer": 3, "confidence": 0.8, "justification": "Support renewable energy"}]}'
```

### Puolueiden vertailu (JavaScript)
```javascript
fetch('http://localhost:5000/api/compare_all_parties', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_answers: { q1: 3, q2: -1 } })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

## Swagger-dokumentaatio
Tarkempi tekninen dokumentaatio ja interaktiivinen testaus löytyy Swagger UI:sta:
- **URL**: `/api/docs` (jos integroitu Flaskiin).
- **YAML-tiedosto**: Katso `openapi.yaml` projektin juuresta tai kopioi se [Swagger Editoriin](https://editor.swagger.io).
- **Käyttö**: Swagger UI mahdollistaa endpointien testauksen selaimessa, mukaan lukien autentikoidut pyynnöt (syötä JWT tai käytä sessionia).

## Vinkkejä frontend-kehittäjille
1. **Kysymysten näyttäminen**:
   - Käytä `GET /api/questions` hakeaksesi aktiiviset kysymykset.
   - Renderöi `question.fi` (tai muu kieli) ja `scale` (esim. liukusäädin -5..5).
   - Näytä `tags` suodattimina ja `category` ryhmittelyyn.

2. **Käyttäjän vertailu**:
   - Tallenna käyttäjän vastaukset lokaalisti (esim. `{ q1: 3, q2: -1 }`).
   - Käytä `POST /api/compare_all_parties` näyttääksesi puolueiden osumat (lajittele `match_percentage` laskevasti).
   - Näytä `candidate_count` kontekstina.

3. **IPFS-integraatio**:
   - Jos haluat hakea dataa suoraan IPFS:stä, käytä `GET /api/admin/fetch_ipfs_questions` (admin) tai integroi IPFS-js-kirjasto frontendissä CID:iden perusteella.
   - Varmista, että IPFS-nodet ovat saatavilla (esim. `ipfs.io` tai oma node).

4. **Autentikointi**:
   - Tallenna JWT localStorageen tai käytä session-cookieta selaimessa.
   - Tarkista `GET /api/admin/status` ennen admin-toimintoja.

5. **Virheiden käsittely**:
   - Näytä käyttäjälle `error`-kentän viesti, jos `success: false`.
   - Ohjaa kirjautumiseen, jos saat 401-vastauksen.

6. **Optimointi**:
   - Välimuistita `GET /api/questions` ja `GET /api/candidates` (data muuttuu harvoin).
   - Käytä paginointia suurille datasetille (esim. `GET /api/questions?offset=0&limit=50`, jos lisäät tuen).

7. **UI/UX**:
   - Käytä `GET /api/available_tags` dynaamiseen suodatukseen.
   - Näytä `elo_rating` kysymyksille "suosituimpina" tai korosta korkean arvon kysymykset.

Jos tarvitset lisää esimerkkejä (esim. React-koodia endpointtien käyttöön), tarkennuksia tiettyihin endpointteihin tai apua Swagger-integraation kanssa, kerro! Voin myös generoida testidataa tai auttaa yksikkötestien kirjoittamisessa.
