# Hajautetun Vaalikoneen API-dokumentaatio

Järjestelmäversio: `0.0.6-alpha`  
Perus-URL: `http://localhost:5000`

## 🔐 Autentikaatio

- **Julkiset reitit**: Ei vaadi kirjautumista
- **Admin-reitit**: Vaativat admin-kirjautumisen
  - Kirjaudu ensin: `POST /api/admin/login`
  - Istunto säilyy evästeissä (`session`)

---

## 🌐 Julkiset API-reitit

### `GET /api/meta`
Hakee järjestelmän meta-tiedot.

**Vastaus**:
```json
{
  "system": "Decentralized Candidate Matcher",
  "version": "0.0.6-alpha",
  "election": {
    "id": "election_2026-01-01_fi_satakunta",
    "name": {"fi": "...", "en": "...", "sv": "..."},
    "date": "2026-01-01"
  },
  "content": {
    "questions_count": 2,
    "candidates_count": 3,
    "parties_count": 2
  }
}
