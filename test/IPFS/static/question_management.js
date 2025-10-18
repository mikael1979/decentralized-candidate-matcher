// Kysymysten hallinnan tila
const state = {
    questions: [],
    searchResults: [],
    availableTags: [],
    activeTab: 'submit'
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

// Välilehtien käsittely
tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        const tab = button.dataset.tab;
        switchTab(tab);
    });
});

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
        // Tyhjennä hakutulokset
        searchResults.innerHTML = '<div class="no-data">Syötä hakusana ja klikkaa "Hae"</div>';
    } else if (tabName === 'stats') {
        loadStats();
    }
}

// Kysymyksen lähettäminen
questionForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(questionForm);
    const questionData = {
        question: {
            fi: formData.get('question-fi'),
            en: formData.get('question-en') || formData.get('question-fi')
        },
        category: formData.get('category'),
        tags: formData.get('tags').split(',').map(tag => tag.trim()).filter(tag => tag),
        scale: {
            min: -5,
            max: 5
        }
    };
    
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
            submissionResult.innerHTML = `
                <div class="success-message">
                    ✅ Kysymys lähetetty onnistuneesti!
                    ${result.cid ? `<br><small>CID: ${result.cid}</small>` : ''}
                </div>
            `;
            questionForm.reset();
        } else {
            submissionResult.innerHTML = `
                <div class="error-message">
                    ❌ Lähetys epäonnistui: ${result.errors?.join(', ') || 'Tuntematon virhe'}
                </div>
            `;
        }
    } catch (error) {
        submissionResult.innerHTML = `
            <div class="error-message">
                ❌ Verkkovirhe: ${error.message}
            </div>
        `;
    }
});

// Kysymysten haku
searchBtn.addEventListener('click', performSearch);
fuzzySearchBtn.addEventListener('click', () => performSearch(true));

async function performSearch(fuzzy = false) {
    const query = searchQuery.value.trim();
    
    if (!query) {
        searchResults.innerHTML = '<div class="no-data">Syötä hakusana</div>';
        return;
    }
    
    try {
        const params = new URLSearchParams({ q: query });
        if (fuzzy) params.append('fuzzy', 'true');
        
        const response = await fetch(`/api/search_questions?${params}`);
        const result = await response.json();
        
        if (result.success) {
            displaySearchResults(result.results);
        } else {
            searchResults.innerHTML = `<div class="error">Hakutulosten hakeminen epäonnistui: ${result.error}</div>`;
        }
    } catch (error) {
        searchResults.innerHTML = `<div class="error">Verkkovirhe: ${error.message}</div>`;
    }
}

function displaySearchResults(results) {
    if (results.length === 0) {
        searchResults.innerHTML = '<div class="no-data">Ei hakutuloksia</div>';
        return;
    }
    
    searchResults.innerHTML = results.map(question => `
        <div class="search-result-item">
            <h4>${question.question?.fi || question.question}</h4>
            <div class="question-meta">
                <span class="category">${question.category?.fi || question.category}</span>
                <span class="tags">${question.tags?.join(', ') || 'Ei tageja'}</span>
            </div>
            ${question.question?.en ? `<p><em>${question.question.en}</em></p>` : ''}
        </div>
    `).join('');
}

// Tagien lataus
async function loadTags() {
    try {
        const response = await fetch('/api/available_tags');
        const result = await response.json();
        
        if (result.success) {
            displayTags(result.tags);
        } else {
            tagsContainer.innerHTML = `<div class="error">Tagien lataus epäonnistui: ${result.error}</div>`;
        }
    } catch (error) {
        tagsContainer.innerHTML = `<div class="error">Verkkovirhe: ${error.message}</div>`;
    }
}

function displayTags(tags) {
    if (!tags || Object.keys(tags).length === 0) {
        tagsContainer.innerHTML = '<div class="no-data">Ei tageja saatavilla</div>';
        return;
    }
    
    tagsContainer.innerHTML = `
        <div class="tags-container">
            ${Object.entries(tags).map(([tag, count]) => `
                <div class="tag">
                    ${tag}
                    <span class="tag-count">${count}</span>
                </div>
            `).join('')}
        </div>
    `;
}

// Tilastojen lataus
async function loadStats() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Tässä voitaisiin näyttää tilastoja charteilla
        document.getElementById('category-stats').innerHTML = `
            <p>Virallisia kysymyksiä: ${data.official_questions || 0}</p>
            <p>Käyttäjien kysymyksiä: ${data.user_questions || 0}</p>
            <p>Yhteensä: ${(data.official_questions || 0) + (data.user_questions || 0)}</p>
        `;
        
        document.getElementById('tag-stats').innerHTML = `
            <p>Tagien määrä: ${Object.keys(state.availableTags).length}</p>
            <p>Kysymystä kohden keskimäärin: ${calculateAverageTags()}</p>
        `;
    } catch (error) {
        console.error('Tilastojen lataus epäonnistui:', error);
    }
}

function calculateAverageTags() {
    const totalQuestions = state.questions.length;
    const totalTags = Object.values(state.availableTags).reduce((sum, count) => sum + count, 0);
    return totalQuestions > 0 ? (totalTags / totalQuestions).toFixed(1) : 0;
}

// Alustus
function init() {
    // Lataa saatavilla olevat tagit
    loadTags();
    
    // Aseta enter-painike hakua varten
    searchQuery.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
}

document.addEventListener('DOMContentLoaded', init);
