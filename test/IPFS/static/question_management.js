// Kysymysten hallinnan tila
const state = {
    questions: [],
    searchResults: [],
    availableTags: new Map(),
    availableCategories: new Set(),
    activeTab: 'submit',
    currentElection: null
};

// DOM-elementit
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');
const questionForm = document.getElementById('question-form');
const submissionResult = document.getElementById('submission-result');
const searchQuery = document.getElementById('search-query');
const searchBtn = document.getElementById('search-btn');
const fuzzySearchBtn = document.getElementById('fuzzy-search-btn');
const searchResults = document.getElementById('search-results');
const tagsContainer = document.getElementById('tags-container');
const categoriesContainer = document.getElementById('categories-container');
const statsContainer = document.getElementById('stats-container');

// Välilehtien käsittely
function initTabs() {
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Poista aktiiviset luokat
    tabButtons.forEach(btn => btn.classList.remove('active'));
    tabContents.forEach(content => content.classList.remove('active'));
    
    // Aseta uusi aktiivinen välilehti
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    state.activeTab = tabName;
    
    // Lataa välilehden sisältö
    if (tabName === 'tags') {
        loadTags();
    } else if (tabName === 'search') {
        clearSearchResults();
    } else if (tabName === 'stats') {
        loadStats();
    } else if (tabName === 'categories') {
        loadCategories();
    }
}

// Lataa järjestelmätiedot
async function loadSystemInfo() {
    try {
        const response = await fetch('/api/system_info');
        const systemInfo = await response.json();
        state.currentElection = systemInfo.election;
        
        // Päivitä sivun otsikko
        document.title = `Kysymysten hallinta - ${systemInfo.election.name.fi}`;
        
        // Päivitä vaalitiedot näkyviin
        const electionInfo = document.getElementById('election-info');
        if (electionInfo) {
            electionInfo.innerHTML = `
                <strong>${systemInfo.election.name.fi}</strong>
                <small>(${new Date(systemInfo.election.date).toLocaleDateString('fi-FI')})</small>
            `;
        }
    } catch (error) {
        console.error('Järjestelmätietojen lataus epäonnistui:', error);
    }
}

// Kysymyksen lähettäminen
function initQuestionForm() {
    if (!questionForm) return;
    
    questionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(questionForm);
        const questionData = {
            question: {
                fi: formData.get('question-fi').trim(),
                en: formData.get('question-en')?.trim() || formData.get('question-fi').trim()
            },
            category: formData.get('category').trim(),
            tags: formData.get('tags').split(',').map(tag => tag.trim()).filter(tag => tag),
            scale: {
                min: -5,
                max: 5,
                labels: {
                    fi: {
                        "-5": "Täysin eri mieltä",
                        "0": "Neutraali", 
                        "5": "Täysin samaa mieltä"
                    }
                }
            }
        };
        
        // Validointi
        const errors = validateQuestion(questionData);
        if (errors.length > 0) {
            showFormErrors(errors);
            return;
        }
        
        try {
            const response = await fetch('/api/submit_question', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(questionData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                showFormSuccess(result.message || 'Kysymys lähetetty onnistuneesti!', result.cid);
                questionForm.reset();
                
                // Päivitä tilastot ja tagit
                loadTags();
                loadStats();
                loadCategories();
                
            } else {
                showFormErrors(result.errors || ['Lähetys epäonnistui']);
            }
        } catch (error) {
            console.error('Lähetyksen virhe:', error);
            showFormErrors(['Verkkovirhe: ' + error.message]);
        }
    });
    
    // Automaattinen tag-ehdotus
    const tagsInput = document.getElementById('tags-input');
    if (tagsInput) {
        tagsInput.addEventListener('input', updateTagSuggestions);
    }
}

// Kysymyksen validointi
function validateQuestion(questionData) {
    const errors = [];
    
    // Kysymysteksti
    const fiText = questionData.question.fi;
    if (!fiText) {
        errors.push('Kysymys suomeksi on pakollinen');
    } else if (fiText.length < 10) {
        errors.push('Kysymyksen tulee olla vähintään 10 merkkiä pitkä');
    } else if (fiText.length > 500) {
        errors.push('Kysymys saa olla enintään 500 merkkiä pitkä');
    }
    
    // Kategoria
    if (!questionData.category) {
        errors.push('Kategoria on pakollinen');
    }
    
    // Tagit
    if (questionData.tags.length === 0) {
        errors.push('Vähintään yksi tagi on pakollinen');
    } else if (questionData.tags.length > 10) {
        errors.push('Kysymyksessä saa olla enintään 10 tagia');
    }
    
    // Tarkista tagien pituus
    for (const tag of questionData.tags) {
        if (tag.length < 2) {
            errors.push('Tagien tulee olla vähintään 2 merkkiä pitkiä');
            break;
        }
        if (tag.length > 20) {
            errors.push('Tagien enimmäispituus on 20 merkkiä');
            break;
        }
    }
    
    return errors;
}

// Näytä lomakkeen virheet
function showFormErrors(errors) {
    if (!submissionResult) return;
    
    submissionResult.innerHTML = `
        <div class="error-message">
            <strong>❌ Lähetys epäonnistui:</strong>
            <ul>
                ${errors.map(error => `<li>${error}</li>`).join('')}
            </ul>
        </div>
    `;
    
    // Korosta virheellisiä kenttiä
    highlightInvalidFields(errors);
}

// Näytä lomakkeen onnistuminen
function showFormSuccess(message, cid) {
    if (!submissionResult) return;
    
    let html = `
        <div class="success-message">
            <strong>✅ ${message}</strong>
    `;
    
    if (cid) {
        html += `<br><small>Kysymys ID: ${cid}</small>`;
    }
    
    html += `</div>`;
    
    submissionResult.innerHTML = html;
}

// Korosta virheellisiä kenttiä
function highlightInvalidFields(errors) {
    // Poista vanhat korostukset
    document.querySelectorAll('.invalid-field').forEach(el => {
        el.classList.remove('invalid-field');
    });
    
    // Lisää uudet korostukset
    if (errors.some(e => e.includes('suomeksi'))) {
        document.getElementById('question-fi')?.classList.add('invalid-field');
    }
    
    if (errors.some(e => e.includes('Kategoria'))) {
        document.getElementById('category')?.classList.add('invalid-field');
    }
    
    if (errors.some(e => e.includes('tagi'))) {
        document.getElementById('tags-input')?.classList.add('invalid-field');
    }
}

// Päivitä tag-ehdotukset
function updateTagSuggestions() {
    const tagsInput = document.getElementById('tags-input');
    const suggestionsContainer = document.getElementById('tag-suggestions');
    
    if (!tagsInput || !suggestionsContainer) return;
    
    const currentValue = tagsInput.value.toLowerCase();
    if (currentValue.length < 2) {
        suggestionsContainer.innerHTML = '';
        return;
    }
    
    // Etsi vastaavat tagit
    const matchingTags = Array.from(state.availableTags.entries())
        .filter(([tag, count]) => tag.toLowerCase().includes(currentValue))
        .slice(0, 5);
    
    if (matchingTags.length > 0) {
        suggestionsContainer.innerHTML = `
            <div class="tag-suggestions-list">
                ${matchingTags.map(([tag, count]) => `
                    <div class="tag-suggestion" onclick="addTag('${tag}')">
                        ${tag} <small>(${count} kpl)</small>
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        suggestionsContainer.innerHTML = '';
    }
}

// Lisää tag syöttökenttään
function addTag(tag) {
    const tagsInput = document.getElementById('tags-input');
    if (!tagsInput) return;
    
    const currentTags = tagsInput.value.split(',').map(t => t.trim()).filter(t => t);
    
    // Älä lisää duplikaatteja
    if (!currentTags.includes(tag)) {
        currentTags.push(tag);
        tagsInput.value = currentTags.join(', ');
    }
    
    // Tyhjennä ehdotukset
    document.getElementById('tag-suggestions').innerHTML = '';
    tagsInput.focus();
}

// Kysymysten haku
function initSearch() {
    if (searchBtn) {
        searchBtn.addEventListener('click', () => performSearch());
    }
    
    if (fuzzySearchBtn) {
        fuzzySearchBtn.addEventListener('click', () => performSearch(true));
    }
    
    if (searchQuery) {
        searchQuery.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
}

async function performSearch(fuzzy = false) {
    const query = searchQuery.value.trim();
    
    if (!query) {
        showSearchMessage('Syötä hakusana');
        return;
    }
    
    try {
        showSearchMessage('Haetaan kysymyksiä...');
        
        const searchUrl = fuzzy ? 
            `/api/search_questions?q=${encodeURIComponent(query)}&fuzzy=true` :
            `/api/search_questions?q=${encodeURIComponent(query)}`;
        
        const response = await fetch(searchUrl);
        const result = await response.json();
        
        if (result.success) {
            displaySearchResults(result.results, query);
        } else {
            showSearchMessage('Hakutulosten hakeminen epäonnistui: ' + (result.error || 'Tuntematon virhe'));
        }
    } catch (error) {
        console.error('Hakutapahtuman virhe:', error);
        showSearchMessage('Verkkovirhe: ' + error.message);
    }
}

function displaySearchResults(results, query) {
    if (!searchResults) return;
    
    if (results.length === 0) {
        searchResults.innerHTML = `
            <div class="no-data">
                <p>Ei hakutuloksia hakusanalle: <strong>"${query}"</strong></p>
                <p class="suggestion">Kokeile:</p>
                <ul class="suggestions">
                    <li>Erilaisia hakusanoja</li>
                    <li>Laajempaa hakua (vähemmän tarkka)</li>
                    <li>Tarkista kirjoitusasu</li>
                </ul>
            </div>
        `;
        return;
    }
    
    searchResults.innerHTML = `
        <div class="search-header">
            <h4>Hakutulokset (${results.length} kpl)</h4>
            <p>Hakutermi: <strong>"${query}"</strong></p>
        </div>
        <div class="search-results-list">
            ${results.map((result, index) => createSearchResultItem(result, index)).join('')}
        </div>
    `;
}

function createSearchResultItem(result, index) {
    const question = result.question;
    const relevance = Math.round((result.relevance_score || 0) * 100);
    
    return `
        <div class="search-result-item">
            <div class="result-header">
                <span class="result-number">${index + 1}.</span>
                <span class="result-score ${getRelevanceClass(relevance)}">
                    ${relevance}% sopivuus
                </span>
            </div>
            
            <div class="result-question">
                <strong>${question.question.fi}</strong>
                ${question.question.en ? `<br><em>${question.question.en}</em>` : ''}
            </div>
            
            <div class="result-meta">
                <span class="category-badge">${question.category.fi}</span>
                <span class="tags">${question.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}</span>
            </div>
            
            <div class="result-actions">
                <button class="btn small" onclick="useQuestionAsTemplate(${question.id})">
                    📝 Käytä mallina
                </button>
                <button class="btn small secondary" onclick="showQuestionDetails(${question.id})">
                    🔍 Näytä tiedot
                </button>
            </div>
        </div>
    `;
}

function getRelevanceClass(score) {
    if (score >= 80) return 'relevance-high';
    if (score >= 60) return 'relevance-medium';
    return 'relevance-low';
}

function showSearchMessage(message) {
    if (!searchResults) return;
    
    searchResults.innerHTML = `
        <div class="search-message">
            ${message}
        </div>
    `;
}

function clearSearchResults() {
    if (searchResults) {
        searchResults.innerHTML = '<div class="no-data">Syötä hakusana ja klikkaa "Hae"</div>';
    }
    if (searchQuery) {
        searchQuery.value = '';
    }
}

// Käytä kysymystä mallina
function useQuestionAsTemplate(questionId) {
    const question = state.questions.find(q => q.id == questionId);
    if (!question) return;
    
    // Täytä lomake kysymyksen tiedoilla
    document.getElementById('question-fi').value = question.question.fi;
    document.getElementById('question-en').value = question.question.en || '';
    document.getElementById('category').value = question.category.fi;
    document.getElementById('tags-input').value = question.tags.join(', ');
    
    // Siirry lähetys-välilehdelle
    switchTab('submit');
    
    // Näytä viesti
    if (submissionResult) {
        submissionResult.innerHTML = `
            <div class="info-message">
                ✅ Kysymys ladattu malliksi! Muokkaa tarvittaessa ja lähetä uutena kysymyksenä.
            </div>
        `;
    }
}

// Näytä kysymyksen tiedot
function showQuestionDetails(questionId) {
    const question = state.questions.find(q => q.id == questionId);
    if (!question) return;
    
    const modalHtml = `
        <div class="modal-overlay" onclick="closeModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3>Kysymyksen tiedot</h3>
                    <button class="modal-close" onclick="closeModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="question-detail">
                        <h4>Kysymys</h4>
                        <p><strong>Suomeksi:</strong> ${question.question.fi}</p>
                        ${question.question.en ? `<p><strong>Englanniksi:</strong> ${question.question.en}</p>` : ''}
                    </div>
                    
                    <div class="question-meta">
                        <div class="meta-item">
                            <strong>Kategoria:</strong> ${question.category.fi}
                        </div>
                        <div class="meta-item">
                            <strong>Tagit:</strong> ${question.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                        <div class="meta-item">
                            <strong>Vastausasteikko:</strong> ${question.scale.min} - ${question.scale.max}
                        </div>
                        <div class="meta-item">
                            <strong>ID:</strong> ${question.id}
                        </div>
                    </div>
                    
                    ${question.elo_rating ? `
                    <div class="question-stats">
                        <h4>Elo-luokitus</h4>
                        <div class="elo-stats">
                            <span>Rating: ${question.elo_rating.rating}</span>
                            <span>Voitot: ${question.elo_rating.wins || 0}</span>
                            <span>Häviöt: ${question.elo_rating.losses || 0}</span>
                        </div>
                    </div>
                    ` : ''}
                </div>
                <div class="modal-footer">
                    <button class="btn" onclick="useQuestionAsTemplate(${question.id}); closeModal();">
                        📝 Käytä mallina
                    </button>
                    <button class="btn secondary" onclick="closeModal()">
                        Sulje
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Lisää modaali DOM:iin
    const modalContainer = document.createElement('div');
    modalContainer.id = 'question-modal';
    modalContainer.innerHTML = modalHtml;
    document.body.appendChild(modalContainer);
}

function closeModal() {
    const modal = document.getElementById('question-modal');
    if (modal) {
        modal.remove();
    }
}

// Tagien lataus ja näyttö
async function loadTags() {
    try {
        const response = await fetch('/api/available_tags');
        const result = await response.json();
        
        if (result.success) {
            state.availableTags = new Map(Object.entries(result.tags));
            displayTags();
        } else {
            showTagsError(result.error || 'Tagien lataus epäonnistui');
        }
    } catch (error) {
        console.error('Tagien latausvirhe:', error);
        showTagsError('Verkkovirhe: ' + error.message);
    }
}

function displayTags() {
    if (!tagsContainer) return;
    
    if (state.availableTags.size === 0) {
        tagsContainer.innerHTML = '<div class="no-data">Ei tageja saatavilla</div>';
        return;
    }
    
    // Järjestä tagit suosiojärjestykseen
    const sortedTags = Array.from(state.availableTags.entries())
        .sort((a, b) => b[1] - a[1]);
    
    tagsContainer.innerHTML = `
        <div class="tags-header">
            <h4>Käytössä olevat tagit (${sortedTags.length} kpl)</h4>
            <p>Klikkaa tagia lisätäksesi sen kysymykseen</p>
        </div>
        <div class="tags-cloud">
            ${sortedTags.map(([tag, count]) => `
                <div class="tag-item" onclick="addTag('${tag}')" data-count="${count}">
                    ${tag}
                    <span class="tag-count">${count}</span>
                </div>
            `).join('')}
        </div>
    `;
}

function showTagsError(message) {
    if (!tagsContainer) return;
    
    tagsContainer.innerHTML = `
        <div class="error-message">
            ❌ ${message}
            <br><button class="btn small" onclick="loadTags()">Yritä uudelleen</button>
        </div>
    `;
}

// Kategorioiden lataus
async function loadCategories() {
    try {
        const questions = await loadAllQuestions();
        const categories = new Set();
        
        questions.forEach(q => {
            if (q.category && q.category.fi) {
                categories.add(q.category.fi);
            }
        });
        
        state.availableCategories = categories;
        displayCategories();
    } catch (error) {
        console.error('Kategorioiden latausvirhe:', error);
    }
}

function displayCategories() {
    if (!categoriesContainer) return;
    
    const categories = Array.from(state.availableCategories).sort();
    
    if (categories.length === 0) {
        categoriesContainer.innerHTML = '<div class="no-data">Ei kategorioita saatavilla</div>';
        return;
    }
    
    categoriesContainer.innerHTML = `
        <div class="categories-header">
            <h4>Käytössä olevat kategoriat (${categories.length} kpl)</h4>
        </div>
        <div class="categories-list">
            ${categories.map(category => `
                <div class="category-item" onclick="setCategory('${category}')">
                    ${category}
                </div>
            `).join('')}
        </div>
    `;
}

function setCategory(category) {
    const categoryInput = document.getElementById('category');
    if (categoryInput) {
        categoryInput.value = category;
        switchTab('submit');
    }
}

// Tilastojen lataus
async function loadStats() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        
        displayStats(status);
    } catch (error) {
        console.error('Tilastojen latausvirhe:', error);
    }
}

function displayStats(status) {
    if (!statsContainer) return;
    
    const totalQuestions = status.official_questions + status.user_questions;
    
    statsContainer.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-content">
                    <div class="stat-number">${totalQuestions}</div>
                    <div class="stat-label">Kysymystä yhteensä</div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">🏢</div>
                <div class="stat-content">
                    <div class="stat-number">${status.official_questions}</div>
                    <div class="stat-label">Virallista kysymystä</div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">👥</div>
                <div class="stat-content">
                    <div class="stat-number">${status.user_questions}</div>
                    <div class="stat-label">Käyttäjien kysymystä</div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">👤</div>
                <div class="stat-content">
                    <div class="stat-number">${status.candidates}</div>
                    <div class="stat-label">Ehdokasta</div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">🏛️</div>
                <div class="stat-content">
                    <div class="stat-number">${status.parties}</div>
                    <div class="stat-label">Puoluetta</div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">🕒</div>
                <div class="stat-content">
                    <div class="stat-date">${new Date(status.timestamp).toLocaleString('fi-FI')}</div>
                    <div class="stat-label">Päivitetty</div>
                </div>
            </div>
        </div>
        
        <div class="stats-actions">
            <button class="btn small" onclick="refreshStats()">
                🔄 Päivitä tilastot
            </button>
        </div>
    `;
}

async function refreshStats() {
    await loadStats();
    await loadTags();
    await loadCategories();
}

// Lataa kaikki kysymykset
async function loadAllQuestions() {
    try {
        const response = await fetch('/api/questions');
        state.questions = await response.json();
        return state.questions;
    } catch (error) {
        console.error('Kysymysten latausvirhe:', error);
        return [];
    }
}

// Alustus
async function init() {
    console.log('🚀 Alustetaan kysymysten hallinta...');
    
    // Lataa järjestelmätiedot
    await loadSystemInfo();
    
    // Alusta välilehdet
    initTabs();
    
    // Alusta lomake
    initQuestionForm();
    
    // Alusta haku
    initSearch();
    
    // Lataa alustavat tiedot
    await loadAllQuestions();
    await loadTags();
    await loadCategories();
    await loadStats();
    
    console.log('✅ Kysymysten hallinta alustettu');
}

// Käynnistä sovellus
document.addEventListener('DOMContentLoaded', init);
