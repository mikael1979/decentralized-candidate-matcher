# Superadmin CLI Tool Manual

Tämä manuaali kuvaa **superadmin.py**-työkalun käyttöä, joka on Superadmin CLI-työkalu Decentralized Candidate Matcher (DCM) -järjestelmän hallintaan. Työkalu mahdollistaa sisällön (kysymykset, ehdokkaat, puolueet) listauksen, tilapäisten tiedostojen synkronoinnin virallisiin tiedostoihin, päivitykset tilapäisiin tiedostoihin sekä järjestelmän eheysketjun tarkistuksen. Se auttaa ylläpitäjiä hallitsemaan dataa komentoriviltä ilman web-käyttöliittymää.

Työkalu käyttää `data`-kansiota tiedostojen tallentamiseen (esim. `data/questions.json`, `data/candidates.json`). Se tukee "tmp"-tiedostoja (`_tmp.json`) muutosten turvalliseen käsittelyyn ennen synkronointia.

## Edellytykset
- **Python**: 3.7+ (kuten koko DCM-projekti).
- **Riippuvuudet**: `json`, `os`, `argparse`, `hashlib`, `datetime` (standardikirjastot).
- **Käyttöympäristö**: Suorita projektin juuresta, jossa on `data`-kansio.
- **Oikeudet**: Kirjoitusoikeus `data`-kansioon.

## Asennus ja Käynnistys
1. Varmista, että skripti on tallennettu `superadmin.py`-tiedostoon.
2. Suorita suoraan: `python superadmin.py [komennot]`.
3. Jos virheitä: Tarkista `data`-kansio ja Python-versio.

## Yleinen Syntaksi
```
python superadmin.py <komento> [optiot]
```
- **Apu**: `python superadmin.py --help` näyttää yleisen ohjeen.
- **Virhetilanteet**: Työkalu tulostaa emoji-pohjaisia viestejä (✅ onnistunut, ❌ epäonnistunut) ja lopettaa exit-koodilla 1 jos virhe.

## Komennot ja Flagit
Työkalu käyttää sub-komentoja. Alla yksityiskohtainen kuvaus jokaisesta komennosta, sen flageista, esimerkeistä ja tulosteista.

### 1. `list` - Listaa sisältöä
**Kuvaus**: Listaa kysymyksiä, ehdokkaita tai puolueita joko virallisista tiedostoista tai tilapäisistä (`tmp`).

**Flagit**:
| Flagi | Tyyppi | Pakollinen? | Kuvaus | Oletusarvo |
|-------|--------|-------------|--------|------------|
| `--type` | string | Kyllä | Sisällön tyyppi: `questions` (kysymykset), `candidates` (ehdokkaat), `parties` (puolueet). | Ei |
| `--source` | string | Ei | Lähde: `official` (viralliset tiedostot) tai `tmp` (tilapäiset `_tmp.json`). | `official` |

**Esimerkkejä**:
- Listaa kysymykset virallisesta tiedostosta:
  ```
  python superadmin.py list --type questions
  ```
  **Tuloste-esimerkki**:
  ```
  📁 Ladataan virallisesta tiedostosta: questions.json
  📋 Questions (official): 2 kpl

  - ID 1: Pitäisikö kaupungin vähentää hiilidioksidipäästöjä 50% vuoteen 2030 mennessä?
  - ID 2: Pitäisikö kaupunkipyörien määrää lisätä kesäkaudella?
  ```

- Listaa ehdokkaat tilapäisestä tiedostosta:
  ```
  python superadmin.py list --type candidates --source tmp
  ```
  **Tuloste-esimerkki**:
  ```
  📁 Ladataan tmp-tiedostosta: candidates_tmp.json
  📋 Candidates (tmp): 3 kpl

  - ID 1: Päivitetty Nimi
  - ID 2: Liisa Esimerkki
  - ID 3: Päivitetty Ehdokas
  ```

- Listaa puolueet:
  ```
  python superadmin.py list --type parties
  ```
  **Tuloste-esimerkki**:
  ```
  📁 Ladataan virallisesta tiedostosta: candidates.json
  📋 Parties (official): 2 kpl

  - Test Puolue
  - Toinen Puolue
  ```

**Huomioita**:
- Puolueet johdetaan ehdokkaiden `party`-kentästä.
- Jos tmp-tiedostoa ei ole, varoitus: "Tmp-tiedostoa ei löydy".

### 2. `sync` - Synkronoi tmp → official
**Kuvaus**: Kopioi tilapäisen tiedoston (`_tmp.json`) viralliseen tiedostoon (`questions.json`, `candidates.json` tai `newquestions.json`). Turvallinen tapa julkaista muutokset.

**Flagit**:
| Flagi | Tyyppi | Pakollinen? | Kuvaus | Oletusarvo |
|-------|--------|-------------|--------|------------|
| `--type` | string | Kyllä | Synkronoitava tyyppi: `questions` (kysymykset), `candidates` (ehdokkaat), `newquestions` (uudet kysymykset). | Ei |

**Esimerkkejä**:
- Synkronoi kysymykset:
  ```
  python superadmin.py sync --type questions
  ```
  **Tuloste-esimerkki** (onnistunut):
  ```
  ✅ Synkronoitu: questions_tmp.json → questions.json
  ```
  **Tuloste-esimerkki** (epäonnistunut):
  ```
  ❌ Tmp-tiedostoa ei löydy: questions_tmp.json
  📁 Hakemistossa olevat tiedostot: ['questions.json', 'candidates.json']
  ```

- Synkronoi uudet kysymykset:
  ```
  python superadmin.py sync --type newquestions
  ```

**Huomioita**:
- Vain jos tmp-tiedosto on olemassa; muuten virhe.
- Synkronoinnin jälkeen tmp-tiedosto poistuu (os.replace).

### 3. `update` - Päivitä sisältöä tmp-tiedostossa
**Kuvaus**: Päivittää yksittäistä kohdetta (kysymys, ehdokas, uusi kysymys) tilapäisessä tiedostossa. Luo tmp-tiedoston jos ei ole. Tukee yksinkertaisia kenttäpäivityksiä ja Elo-deltan lisäyksiä.

**Flagit**:
| Flagi | Tyyppi | Pakollinen? | Kuvaus | Oletusarvo |
|-------|--------|-------------|--------|------------|
| `--type` | string | Kyllä | Kohdetyyppi: `question` (kysymys), `candidate` (ehdokkaat), `newquestion` (uudet kysymykset). | Ei |
| `--id` | int | Kyllä | Kohteen ID (esim. 1). | Ei |
| `--changes` | string (JSON) | Kyllä | Muutokset JSON-muodossa, esim. `'{"question.fi": "Uusi teksti"}'` tai `'{"elo_delta": {"value": 50, "user_id": "admin", "reason": "manual"}}'`. | Ei |

**Esimerkkejä**:
- Päivitä kysymyksen teksti
  ```
  python superadmin.py update --type question --id 1 --changes '{"question.fi": "Päivitetty kysymys?"}'
  ```
  **Tuloste-esimerkki**:
  ```
  📁 Luodaan tmp-tiedosto virallisesta: questions.json → questions_tmp.json
  ✅ Kohde löytyi: Pitäisikö kaupungin vähentää hiilidioksidipäästöjä 50% vuoteen 2030 mennessä?
  ✅ Päivitetty kenttä question.fi: 'Pitäisikö kaupungin vähentää hiilidioksidipäästöjä 50% vuoteen 2030 mennessä?' → 'Päivitetty kysymys?'
  ✅ Päivitys onnistui tmp-tiedostoon
  ```

- Lisää Elo-delta ehdokkaalle
  ```
  python superadmin.py update --type candidate --id 1 --changes '{"elo_delta": {"value": 50, "user_id": "admin", "reason": "manual"}}'
  ```
  **Tuloste-esimerkki**:
  ```
  📁 Käytetään olemassa olevaa tmp-tiedostoa: candidates_tmp.json
  ✅ Kohde löytyi: Päivitetty Nimi
  ✅ Päivitetty ELO: 1200 → 1250
  ✅ Päivitys onnistui tmp-tiedostoon
  ```

**Huomioita**:
- `--changes` on merkkijono, joka parsitaan JSON:ksi; käytä lainausmerkkejä koko argumentille.
- Sisäkkäiset päivitykset: Käytä pistemerkintää, esim. `question.fi` tai `answers.0.justification.fi`.
- Jos kohdetta ei löydy: Näyttää saatavilla olevat ID:t ja epäonnistuu.

### 4. `verify-chain` - Tarkista system_chain.json
**Kuvaus**: Tarkistaa järjestelmän eheysketjun (`data/system_chain.json`) ja vertaa tiedostojen hash-arvoja. Havaitsee muutokset tai korruptioon.

**Flagit**: Ei flageja; suorittaa suoraan.

**Esimerkki**:
```
python superadmin.py verify-chain
```
**Tuloste-esimerkki** (onnistunut):
```
✅ Järjestelmän eheys tarkistettu onnistuneesti
```
**Tuloste-esimerkki** (epäonnistunut):
```
❌ EHEYSRIKKOMUS:
  - questions.json
```

**Huomioita**:
- Tarkistaa kaikki `current_state`-hashit.
- Jos ristiriitoja, lopettaa exit-koodilla 1.

## Yleiset Virheet ja Vianetsintä
- **❌ Tiedostoa ei löydy**: Tarkista `data`-kansio (`ls data/`).
- **❌ Virheellinen JSON muutoksissa**: Tarkista `--changes`-JSON syntaksi (esim. `echo '{"key": "value"}'` testaa).
- **Exit-koodi 1**: Tarkista tulosteet; työkalu lopettaa virheissä.
- **Ei tmp-tiedostoa**: Työkalu luo sen automaattisesti `update`-komennossa.

## Lisävinkkejä
- **Kehityskäyttö**: Yhdistä `list` ja `update` + `sync` workflow: Listaa → Päivitä tmp → Synkronoi.
- **Automaatio**: Käytä skripteissä, esim. cron-job synkronointiin.
- **Debug**: Lisää `print`-lauseita koodiin tarvittaessa; työkalu on yksinkertainen muokata.
- **Laajennus**: Lisää uusia komentoja `argparse`-subparseriin, jos tarvitset (esim. `bulk-import`).

Tämä manuaali auttaa muistamaan komennot ja flagit nopeasti. Jos tarvitset päivityksiä tai esimerkkejä skripteihin, kerro!
