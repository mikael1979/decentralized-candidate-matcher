// Sovelluksen tila
const state = {
    questions: [],
    candidates: [],
    userAnswers: {},
    filteredQuestions: [],
    filteredCandidates: [],
    sortBy: 'match'
};

// DOM-elementit
const questionsContainer = document.getElementById('questions-container');
const candidatesContainer = document.getElementById('candidates-container');
const categoryFilter = document.getElementById('category-filter');
const sortBySelect = document.getElementById('sort-by');
const compareBtn = document.getElementById('compare-btn');
const detailsBtn = document.getElementById('details-btn');
const exportBtn = document.getElementById('export-btn');
const progressBar = document.getElementById('progress-bar');
const progressText = document.getElementById('progress-text');
const comparisonModal = document.getElementById('comparison-modal');
const closeModal = document.getElementById('close-modal');
const comparisonContent = document.getElementById('comparison-content');

// Lataa kysymykset palvelimelta
async function loadQuestions() {
    try {
        const response = await fetch('/api/questions');
        if (!response.ok) {
            throw new Error('Kysymyksiä ei voitu ladata');
        }
        state.questions = await response.json();
        state.filteredQuestions = [...state.questions];
        
        renderQuestions();
        updateCategoryFilter();
        updateProgressBar();
        
    } catch (error) {
        console.error('Virhe kysymysten lataamisessa:', error);
        questionsContainer.innerHTML = '<div class="error">Virhe kysymysten lataamisessa. Tarkista konsoli lisätietoja varten.</div>';
    }
}

// Lataa ehdokkaat palvelimelta
async function loadCandidates() {
    try {
        const response = await fetch('/api/candidates');
        if (!response.ok) {
            throw new Error('Ehdokkaita ei voitu ladata');
        }
        state.candidates = await response.json();
        state.filteredCandidates = [...state.candidates];
        
        renderCandidates();
        
    } catch (error) {
        console.error('Virhe ehdokkaiden lataamisessa:', error);
        candidatesContainer.innerHTML = '<div class="error">Virhe ehdokkaiden lataamisessa. Tarkista konsoli lisätietoja varten.</div>';
    }
}

// Päivittää kysymysten näytön
function renderQuestions() {
    if (state.filteredQuestions.length === 0) {
        questionsContainer.innerHTML = '<div class="no-data">Ei kysymyksiä valitulla suodattimella.</div>';
        return;
    }
    
    questionsContainer.innerHTML = '';
    
    state.filteredQuestions.forEach(question => {
        const questionElement = document.createElement('div');
        questionElement.className = 'question-item';
        
        // Kysymyksen kategoria
        const categoryElement = document.createElement('span');
        categoryElement.className = 'question-category';
        categoryElement.textContent = question.category.fi;
        
        // Kysymyksen teksti
        const questionTextElement = document.createElement('div');
        questionTextElement.className = 'question-text';
        questionTextElement.textContent = question.question.fi;
        
        // Asteikon selitteet
        const scaleLabelsElement = document.createElement('div');
        scaleLabelsElement.className = 'scale-labels';
        
        const minLabel = document.createElement('span');
        minLabel.textContent = '-5 (Täysin eri mieltä)';
        
        const maxLabel = document.createElement('span');
        maxLabel.textContent = '+5 (Täysin samaa mieltä)';
        
        scaleLabelsElement.appendChild(minLabel);
        scaleLabelsElement.appendChild(maxLabel);
        
        // Asteikko
        const scaleContainerElement = document.createElement('div');
        scaleContainerElement.className = 'scale-container';
        
        const scaleRangeElement = document.createElement('div');
        scaleRangeElement.className = 'scale-range';
        
        // Aseta käyttäjän vastaus
        const userAnswer = state.userAnswers[question.id] !== undefined ? state.userAnswers[question.id] : null;
        const position = userAnswer !== null ? 
            ((userAnswer - (-5)) / (5 - (-5))) * 100 : 
            50;
        
        const scaleMarkerElement = document.createElement('div');
        scaleMarkerElement.className = 'scale-marker';
        scaleMarkerElement.style.left = `${position}%`;
        scaleMarkerElement.dataset.questionId = question.id;
        
        // Tee asteikosta klikattava
        scaleRangeElement.addEventListener('click', (e) => {
            const rect = scaleRangeElement.getBoundingClientRect();
            const clickPosition = e.clientX - rect.left;
            const newValue = Math.round(
                -5 + 
                (clickPosition / rect.width) * (5 - (-5))
            );
            
            // Päivitä käyttäjän vastaus
            state.userAnswers[question.id] = newValue;
            
            // Päivitä markkerin sijainti
            scaleMarkerElement.style.left = `${((newValue - (-5)) / (5 - (-5))) * 100}%`;
            
            // Päivitä vastauksen arvon näyttö
            answerValueElement.textContent = newValue;
            
            // Päivitä edistymispalkki
            updateProgressBar();
            
            // Päivitä ehdokkaiden vertailu
            calculateMatches();
        });
        
        scaleRangeElement.appendChild(scaleMarkerElement);
        scaleContainerElement.appendChild(scaleRangeElement);
        
        // Vastauksen arvon näyttö
        const answerValueElement = document.createElement('span');
        answerValueElement.className = 'answer-value';
        answerValueElement.textContent = userAnswer !== null ? userAnswer : '-';
        
        scaleContainerElement.appendChild(answerValueElement);
        
        // Kokoa kysymyksen elementti
        questionElement.appendChild(categoryElement);
        questionElement.appendChild(questionTextElement);
        questionElement.appendChild(scaleLabelsElement);
        questionElement.appendChild(scaleContainerElement);
        
        questionsContainer.appendChild(questionElement);
    });
}

// Päivittää ehdokkaiden näytön
function renderCandidates() {
    if (state.filteredCandidates.length === 0) {
        candidatesContainer.innerHTML = '<div class="no-data">Ei ehdokkaita valitulla suodattimella.</div>';
        return;
    }
    
    candidatesContainer.innerHTML = '';
    
    // Järjestä ehdokkaat valitun kriteerin mukaan
    const sortedCandidates = [...state.filteredCandidates];
    
    if (state.sortBy === 'match') {
        sortedCandidates.sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0));
    } else if (state.sortBy === 'name') {
        sortedCandidates.sort((a, b) => a.name.localeCompare(b.name));
    } else if (state.sortBy === 'party') {
        sortedCandidates.sort((a, b) => a.party.localeCompare(b.party));
    }
    
    sortedCandidates.forEach(candidate => {
        const candidateElement = document.createElement('div');
        candidateElement.className = 'candidate-card';
        
        // Ehdokkaan otsikko
        const candidateHeaderElement = document.createElement('div');
        candidateHeaderElement.className = 'candidate-header';
        
        const candidateNameElement = document.createElement('div');
        candidateNameElement.className = 'candidate-name';
        candidateNameElement.textContent = candidate.name;
        
        const candidatePartyElement = document.createElement('div');
        candidatePartyElement.className = 'candidate-party';
        candidatePartyElement.textContent = candidate.party;
        
        const matchScoreElement = document.createElement('div');
        matchScoreElement.className = 'match-score';
        matchScoreElement.textContent = `${Math.round((candidate.matchScore || 0) * 100)}%`;
        
        candidateHeaderElement.appendChild(candidateNameElement);
        candidateHeaderElement.appendChild(candidatePartyElement);
        candidateHeaderElement.appendChild(matchScoreElement);
        
        // Yhteensopivuuspalkki
        const matchBarElement = document.createElement('div');
        matchBarElement.className = 'match-bar';
        
        const matchFillElement = document.createElement('div');
        matchFillElement.className = 'match-fill';
        matchFillElement.style.width = `${(candidate.matchScore || 0) * 100}%`;
        
        matchBarElement.appendChild(matchFillElement);
        
        // Ehdokkaan lisätiedot
        const candidateDetailsElement = document.createElement('div');
        candidateDetailsElement.className = 'candidate-details';
        candidateDetailsElement.textContent = `Alue: ${candidate.district}`;
        
        // Vastaukset kysymyksiin
        const answersListElement = document.createElement('div');
        answersListElement.className = 'answers-list';
        
        if (candidate.answers && candidate.answers.length > 0) {
            candidate.answers.forEach(answer => {
                const question = state.questions.find(q => q.id == answer.question_id);
                if (!question) return;
                
                const answerElement = document.createElement('div');
                answerElement.className = 'answer-item';
                
                const questionTextElement = document.createElement('div');
                questionTextElement.className = 'answer-question';
                questionTextElement.textContent = question.question.fi;
                
                const answerValueElement = document.createElement('div');
                answerValueElement.className = 'answer-value';
                answerValueElement.textContent = answer.answer;
                
                answerElement.appendChild(questionTextElement);
                answerElement.appendChild(answerValueElement);
                
                answersListElement.appendChild(answerElement);
            });
        } else {
            answersListElement.innerHTML = '<div class="no-data">Ei vastauksia saatavilla</div>';
        }
        
        // Kokoa ehdokkaan elementti
        candidateElement.appendChild(candidateHeaderElement);
        candidateElement.appendChild(matchBarElement);
        candidateElement.appendChild(candidateDetailsElement);
        candidateElement.appendChild(answersListElement);
        
        candidatesContainer.appendChild(candidateElement);
    });
}

// Laskee ehdokkaiden yhteensopivuuden käyttäjän vastausten kanssa
function calculateMatches() {
    // Tarkista, onko käyttäjä vastannut riittävästi kysymyksiin
    const answeredQuestions = Object.keys(state.userAnswers).length;
    if (answeredQuestions === 0) {
        // Jos ei ole vastauksia, aseta kaikille ehdokkaille 0% yhteensopivuus
        state.candidates.forEach(candidate => {
            candidate.matchScore = 0;
        });
        renderCandidates();
        return;
    }
    
    state.candidates.forEach(candidate => {
        let totalDifference = 0;
        let maxPossibleDifference = 0;
        let answeredCount = 0;
        
        if (candidate.answers) {
            candidate.answers.forEach(answer => {
                const questionId = answer.question_id.toString();
                if (state.userAnswers[questionId] === undefined) return;
                
                const userAnswer = state.userAnswers[questionId];
                const candidateAnswer = answer.answer;
                
                // Laske ero käyttäjän ja ehdokkaan vastauksen välillä
                const difference = Math.abs(userAnswer - candidateAnswer);
                totalDifference += difference;
                
                // Laske suurin mahdollinen ero tälle kysymykselle
                const maxDifference = 10; // -5 - +5 = 10
                maxPossibleDifference += maxDifference;
                answeredCount++;
            });
        }
        
        // Laske yhteensopivuusprosentti
        if (maxPossibleDifference > 0 && answeredCount > 0) {
            candidate.matchScore = 1 - (totalDifference / maxPossibleDifference);
        } else {
            candidate.matchScore = 0;
        }
    });
    
    renderCandidates();
}

// Päivittää kategoriasuodattimen vaihtoehdot
function updateCategoryFilter() {
    // Kerää kaikki uniikit kategoriat
    const categories = [...new Set(state.questions.map(q => q.category.fi))];
    
    // Tyhjennä nykyiset vaihtoehdot
    categoryFilter.innerHTML = '<option value="all">Kaikki kategoriat</option>';
    
    // Lisää uudet vaihtoehdot
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categoryFilter.appendChild(option);
    });
}

// Päivittää edistymispalkin
function updateProgressBar() {
    const totalQuestions = state.questions.length;
    const answeredQuestions = Object.keys(state.userAnswers).length;
    const percentage = totalQuestions > 0 ? (answeredQuestions / totalQuestions) * 100 : 0;
    
    progressBar.style.width = `${percentage}%`;
    progressText.textContent = `${answeredQuestions}/${totalQuestions} kysymykseen vastattu`;
}

// Näyttää yksityiskohtaisen vertailun
function showDetailedComparison() {
    const answeredQuestions = Object.keys(state.userAnswers).length;
    if (answeredQuestions === 0) {
        alert('Vastaa ensin vähintään yhteen kysymykseen nähdäksesi yksityiskohtaisen vertailun.');
        return;
    }
    
    // Luo vertailutaulukko
    let tableHTML = `
        <table class="comparison-table">
            <thead>
                <tr>
                    <th>Kysymys</th>
                    <th>Sinun vastauksesi</th>
    `;
    
    // Lisää ehdokkaiden otsikot
    state.candidates.forEach(candidate => {
        tableHTML += `<th>${candidate.name} (${candidate.party})</th>`;
    });
    
    tableHTML += `</tr></thead><tbody>`;
    
    // Lisää kysymykset ja vastaukset
    state.questions.forEach(question => {
        const userAnswer = state.userAnswers[question.id];
        if (userAnswer === undefined) return; // Ohita kysymykset, joihin ei ole vastattu
        
        tableHTML += `<tr>
            <td>${question.question.fi}</td>
            <td>${userAnswer}</td>`;
        
        // Lisää ehdokkaiden vastaukset
        state.candidates.forEach(candidate => {
            let candidateAnswer = '-';
            let matchClass = '';
            
            if (candidate.answers) {
                const answerObj = candidate.answers.find(a => a.question_id == question.id);
                if (answerObj) {
                    candidateAnswer = answerObj.answer;
                    
                    // Lisää värikoodattu ympyrä vastausten yhteensopivuudesta
                    const difference = Math.abs(userAnswer - candidateAnswer);
                    if (difference <= 1) {
                        matchClass = 'match-perfect';
                    } else if (difference <= 3) {
                        matchClass = 'match-good';
                    } else {
                        matchClass = 'match-poor';
                    }
                }
            }
            
            tableHTML += `<td>
                <span class="answer-match ${matchClass}"></span>
                ${candidateAnswer}
            </td>`;
        });
        
        tableHTML += `</tr>`;
    });
    
    tableHTML += `</tbody></table>`;
    
    // Aseta sisältö modaaliin
    comparisonContent.innerHTML = tableHTML;
    
    // Näytä modaali
    comparisonModal.style.display = 'flex';
}

// Vie tulokset JSON-tiedostona
function exportResults() {
    const answeredQuestions = Object.keys(state.userAnswers).length;
    if (answeredQuestions === 0) {
        alert('Ei tallennettavia tuloksia. Vastaa ensin kysymyksiin.');
        return;
    }
    
    const results = {
        userAnswers: state.userAnswers,
        candidates: state.candidates.map(candidate => ({
            name: candidate.name,
            party: candidate.party,
            matchScore: candidate.matchScore
        })),
        timestamp: new Date().toISOString()
    };
    
    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'vaalikone-tulokset.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Suodata kysymykset kategorian mukaan
function filterQuestionsByCategory(category) {
    if (category === 'all') {
        state.filteredQuestions = [...state.questions];
    } else {
        state.filteredQuestions = state.questions.filter(q => q.category.fi === category);
    }
    renderQuestions();
}

// Kysymysten hallinta
function initQuestionManagement() {
    // Välilehtien käsittely
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            // Poista aktiivinen luokka kaikilta
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            // Lisää aktiivinen luokka valitulle
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab') + '-tab';
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Kysymyksen lähettäminen
    document.getElementById('question-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const questionData = {
            question: {
                fi: formData.get('question-fi'),
                en: formData.get('question-en') || formData.get('question-fi')
            },
            category: {
                fi: formData.get('category'),
                en: formData.get('category')
            },
            tags: {
                fi: formData.get('tags').split(',').map(tag => tag.trim()).filter(tag => tag),
                en: formData.get('tags').split(',').map(tag => tag.trim()).filter(tag => tag)
            },
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
        
        try {
            const response = await fetch('/api/submit_question', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(questionData)
            });
            
            const result = await response.json();
            
            const resultDiv = document.getElementById('submission-result');
            if (result.success) {
                resultDiv.innerHTML = `
                    <div class="success-message">
                        ✅ Kysymys lähetetty onnistuneesti!
                        <br><small>Kysymys ID: ${result.question_id}</small>
                    </div>
                `;
                e.target.reset();
                
                // Päivitä kysymyslista
                loadQuestions();
            } else {
                let errorHtml = '<div class="error-message">❌ Lähetys epäonnistui:<ul>';
                result.errors.forEach(error => {
                    errorHtml += `<li>${error}</li>`;
                });
                errorHtml += '</ul></div>';
                
                // Näytä samankaltaiset kysymykset
                if (result.similar_questions && result.similar_questions.length > 0) {
                    errorHtml += '<div class="similar-questions"><h4>Samankaltaisia kysymyksiä:</h4>';
                    result.similar_questions.forEach(similar => {
                        errorHtml += `
                            <div class="similar-question">
                                <strong>${similar.question.question.fi}</strong>
                                <br><small>Samankaltaisuus: ${Math.round(similar.similarity_score * 100)}%</small>
                            </div>
                        `;
                    });
                    errorHtml += '</div>';
                }
                
                resultDiv.innerHTML = errorHtml;
            }
        } catch (error) {
            document.getElementById('submission-result').innerHTML = `
                <div class="error-message">❌ Virhe lähetyksessä: ${error.message}</div>
            `;
        }
    });
    
    // Kysymysten haku
    document.getElementById('search-btn').addEventListener('click', searchQuestions);
    document.getElementById('fuzzy-search-btn').addEventListener('click', () => searchQuestions(true));
    
    // Lataa tagit
    loadAvailableTags();
}

async function searchQuestions(fuzzy = false) {
    const query = document.getElementById('search-query').value;
    const resultsDiv = document.getElementById('search-results');
    
    if (!query.trim()) {
        resultsDiv.innerHTML = '<div class="error-message">❌ Syötä hakusana</div>';
        return;
    }
    
    resultsDiv.innerHTML = '<div class="loading">Haetaan kysymyksiä...</div>';
    
    try {
        const url = fuzzy ? 
            `/api/search_questions?q=${encodeURIComponent(query)}` :
            `/api/search_questions?q=${encodeURIComponent(query)}`;
        
        const response = await fetch(url);
        const result = await response.json();
        
        if (result.success) {
            if (result.results.length === 0) {
                resultsDiv.innerHTML = '<div class="no-data">Ei hakutuloksia</div>';
            } else {
                let html = `<h4>Hakutulokset (${result.results.length} kpl):</h4>`;
                
                result.results.forEach((item, index) => {
                    const question = item.question;
                    const score = item.relevance_score || item.similarity_score || 0;
                    
                    html += `
                        <div class="search-result-item">
                            <div class="result-header">
                                <strong>${index + 1}. ${question.question.fi}</strong>
                                <span class="score">${Math.round(score * 100)}%</span>
                            </div>
                            <div class="result-details">
                                <small>ID: ${question.id} | Kategoria: ${question.category.fi} | Tagit: ${question.tags.fi.join(', ')}</small>
                            </div>
                        </div>
                    `;
                });
                
                resultsDiv.innerHTML = html;
            }
        } else {
            resultsDiv.innerHTML = `<div class="error-message">❌ Haku epäonnistui: ${result.error}</div>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<div class="error-message">❌ Virhe haussa: ${error.message}</div>`;
    }
}

async function loadAvailableTags() {
    try {
        const response = await fetch('/api/available_tags');
        const result = await response.json();
        
        const tagsDiv = document.getElementById('tags-container');
        
        if (result.success) {
            if (result.tags.length === 0) {
                tagsDiv.innerHTML = '<div class="no-data">Ei tageja vielä</div>';
            } else {
                let html = `<h4>Käytössä olevat tagit (${result.tags.length} kpl):</h4><div class="tags-list">`;
                
                result.tags.forEach(tag => {
                    html += `<span class="tag">${tag}</span>`;
                });
                
                html += '</div>';
                tagsDiv.innerHTML = html;
            }
        } else {
            tagsDiv.innerHTML = `<div class="error-message">❌ Tägien lataus epäonnistui: ${result.error}</div>`;
        }
    } catch (error) {
        document.getElementById('tags-container').innerHTML = 
            `<div class="error-message">❌ Virhe tégien latauksessa: ${error.message}</div>`;
    }
}

// Alustus
function init() {
    // Lataa kysymykset ja ehdokkaat
    loadQuestions();
    loadCandidates();
    
    // Aseta tapahtumankäsittelijät
    categoryFilter.addEventListener('change', (e) => {
        filterQuestionsByCategory(e.target.value);
    });
    
    sortBySelect.addEventListener('change', (e) => {
        state.sortBy = e.target.value;
        renderCandidates();
    });
    
    compareBtn.addEventListener('click', () => {
        calculateMatches();
    });
    
    detailsBtn.addEventListener('click', () => {
        showDetailedComparison();
    });
    
    exportBtn.addEventListener('click', () => {
        exportResults();
    });
    
    closeModal.addEventListener('click', () => {
        comparisonModal.style.display = 'none';
    });
    
    // Sulje modaali, kun klikataan sen ulkopuolelle
    window.addEventListener('click', (e) => {
        if (e.target === comparisonModal) {
            comparisonModal.style.display = 'none';
        }
    });
    
    // Alusta kysymysten hallinta
    initQuestionManagement();
}

// Käynnistä sovellus
document.addEventListener('DOMContentLoaded', init);
