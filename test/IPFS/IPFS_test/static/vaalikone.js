// vaalikone.js - KORJATTU VERSIO (ilman closeModal konfliktia)

// Sovelluksen tila
const state = {
    questions: [],
    candidates: [],
    parties: [],
    userAnswers: {},
    partyProfiles: new Map(),
    currentTab: 'questions'
};

// DOM-elementit
const questionsContainer = document.getElementById('questions-container');
const candidatesContainer = document.getElementById('candidates-container');
const partiesComparisonContainer = document.getElementById('parties-comparison-container');
const categoryFilter = document.getElementById('category-filter');
const sortBySelect = document.getElementById('sort-by');
const compareBtn = document.getElementById('compare-btn');
const detailsBtn = document.getElementById('details-btn');
const exportBtn = document.getElementById('export-btn');
const progressBar = document.getElementById('progress-bar');
const progressText = document.getElementById('progress-text');
const comparisonModal = document.getElementById('comparison-modal');
const closeModalBtn = document.getElementById('close-modal'); // NIMI MUUTETTU: closeModal -> closeModalBtn
const comparisonContent = document.getElementById('comparison-content');

// UUDET ELEMENTIT PUOLUEVERTAILUUN
const compareAllPartiesBtn = document.getElementById('compare-all-parties');
const refreshPartyDataBtn = document.getElementById('refresh-party-data');
const partyDetailedComparison = document.getElementById('party-detailed-comparison');
const partyComparisonResults = document.getElementById('party-comparison-results');

// EHDOKAAN LISÄYKSEN ELEMENTIT
const candidateForm = document.getElementById('add-candidate-form');
const candidateResult = document.getElementById('candidate-result');

// Lataa kysymykset API:sta
async function loadQuestions() {
    try {
        const response = await fetch('/api/questions');
        if (!response.ok) throw new Error('Kysymyksiä ei voitu ladata');
        
        const questions = await response.json();
        state.questions = questions.map(q => ({
            ...q,
            id: parseInt(q.id),
            scale: {
                min: -5,
                max: 5,
                labels: {
                    fi: { "-5": "Täysin eri mieltä", "0": "Neutraali", "5": "Täysin samaa mieltä" }
                }
            }
        }));
        
        state.filteredQuestions = [...state.questions];
        renderQuestions();
        updateCategoryFilter();
        updateProgressBar();
        
    } catch (error) {
        console.error('Virhe kysymysten lataamisessa:', error);
        questionsContainer.innerHTML = '<div class="error">Virhe kysymysten lataamisessa. Tarkista konsoli lisätietoja varten.</div>';
    }
}

// Lataa ehdokkaat API:sta
async function loadCandidates() {
    try {
        const response = await fetch('/api/candidates');
        if (!response.ok) throw new Error('Ehdokkaita ei voitu ladata');
        
        const candidates = await response.json();
        state.candidates = candidates;
        state.filteredCandidates = [...candidates];
        renderCandidates();
        
    } catch (error) {
        console.error('Virhe ehdokkaiden lataamisessa:', error);
        candidatesContainer.innerHTML = '<div class="error">Virhe ehdokkaiden lataamisessa. Tarkista konsoli lisätietoja varten.</div>';
    }
}

// Lataa puolueet
async function loadParties() {
    try {
        showLoading(partiesComparisonContainer, 'Ladataan puolueita...');
        
        const response = await fetch('/api/parties');
        if (!response.ok) throw new Error('Puolueita ei voitu ladata');
        
        state.parties = await response.json();
        renderPartiesComparison();
        
        // Päivitä puolue-ehdotukset ehdokaslomakkeeseen
        updatePartySuggestions();
        
    } catch (error) {
        console.error('Virhe puolueiden lataamisessa:', error);
        showError(partiesComparisonContainer, 'Puolueiden lataus epäonnistui');
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
        categoryElement.textContent = question.category?.fi || question.category || 'Yleinen';
        
        // Kysymyksen teksti
        const questionTextElement = document.createElement('div');
        questionTextElement.className = 'question-text';
        questionTextElement.textContent = question.question?.fi || question.question || 'Kysymys';
        
        // Asteikon selitteet
        const scaleLabelsElement = document.createElement('div');
        scaleLabelsElement.className = 'scale-labels';
        
        const minLabel = document.createElement('span');
        minLabel.textContent = question.scale.labels.fi[question.scale.min];
        
        const maxLabel = document.createElement('span');
        maxLabel.textContent = question.scale.labels.fi[question.scale.max];
        
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
            ((userAnswer - question.scale.min) / (question.scale.max - question.scale.min)) * 100 : 
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
                question.scale.min + 
                (clickPosition / rect.width) * (question.scale.max - question.scale.min)
            );
            
            // Päivitä käyttäjän vastaus
            state.userAnswers[question.id] = newValue;
            
            // Päivitä markkerin sijainti
            scaleMarkerElement.style.left = `${((newValue - question.scale.min) / (question.scale.max - question.scale.min)) * 100}%`;
            
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
        candidateDetailsElement.textContent = `Alue: ${candidate.district || 'Ei määritelty'}`;
        
        // Vastaukset kysymyksiin
        const answersListElement = document.createElement('div');
        answersListElement.className = 'answers-list';
        
        candidate.answers?.forEach(answer => {
            const question = state.questions.find(q => q.id === answer.question_id);
            if (!question) return;
            
            const answerElement = document.createElement('div');
            answerElement.className = 'answer-item';
            
            const questionTextElement = document.createElement('div');
            questionTextElement.className = 'answer-question';
            questionTextElement.textContent = question.question?.fi || question.question;
            
            const answerValueElement = document.createElement('div');
            answerValueElement.className = 'answer-value';
            answerValueElement.textContent = answer.answer;
            
            answerElement.appendChild(questionTextElement);
            answerElement.appendChild(answerValueElement);
            
            answersListElement.appendChild(answerElement);
        });
        
        // Kokoa ehdokkaan elementti
        candidateElement.appendChild(candidateHeaderElement);
        candidateElement.appendChild(matchBarElement);
        candidateElement.appendChild(candidateDetailsElement);
        if (candidate.answers) {
            candidateElement.appendChild(answersListElement);
        }
        
        candidatesContainer.appendChild(candidateElement);
    });
}

// Renderöi puoluevertailu
function renderPartiesComparison() {
    if (state.parties.length === 0) {
        partiesComparisonContainer.innerHTML = '<div class="no-data">Ei puolueita saatavilla</div>';
        return;
    }
    
    partiesComparisonContainer.innerHTML = `
        <div class="parties-grid">
            ${state.parties.map(party => `
                <div class="party-comparison-card">
                    <div class="party-header">
                        <h4>${party}</h4>
                        <div class="party-match-score">-</div>
                    </div>
                    <div class="party-actions">
                        <button class="btn small" onclick="compareWithParty('${party}')">
                            🔍 Vertaa
                        </button>
                        <button class="btn small secondary" onclick="showPartyProfile('${party}')">
                            📈 Profiili
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    
    // Laske match-prosentit jos käyttäjä on vastannut kysymyksiin
    if (Object.keys(state.userAnswers).length > 0) {
        calculatePartyMatches();
    }
}

// Laskee ehdokkaiden yhteensopivuuden käyttäjän vastausten kanssa
function calculateMatches() {
    const answeredQuestions = Object.keys(state.userAnswers).length;
    if (answeredQuestions === 0) {
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
        
        candidate.answers?.forEach(answer => {
            const question = state.questions.find(q => q.id === answer.question_id);
            if (!question || state.userAnswers[question.id] === undefined) return;
            
            const userAnswer = state.userAnswers[question.id];
            const candidateAnswer = answer.answer;
            
            const difference = Math.abs(userAnswer - candidateAnswer);
            totalDifference += difference;
            
            const maxDifference = question.scale.max - question.scale.min;
            maxPossibleDifference += maxDifference;
            answeredCount++;
        });
        
        if (maxPossibleDifference > 0 && answeredCount > 0) {
            candidate.matchScore = 1 - (totalDifference / maxPossibleDifference);
        } else {
            candidate.matchScore = 0;
        }
    });
    
    renderCandidates();
}

// Laske puolueiden yhteensopivuus
async function calculatePartyMatches() {
    try {
        const response = await fetch('/api/compare_all_parties', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_answers: state.userAnswers })
        });
        
        const comparisons = await response.json();
        
        comparisons.forEach(comparison => {
            const partyElement = document.querySelector(`.party-comparison-card:has(h4:contains("${comparison.party_name}"))`);
            if (partyElement) {
                const scoreElement = partyElement.querySelector('.party-match-score');
                scoreElement.textContent = `${comparison.match_percentage?.toFixed(1) || 0}%`;
                scoreElement.className = `party-match-score ${getMatchLevel(comparison.match_percentage)}`;
            }
        });
    } catch (error) {
        console.error('Puoluevertailun laskenta epäonnistui:', error);
    }
}

// Vertaa tiettyyn puolueeseen
async function compareWithParty(partyName) {
    if (Object.keys(state.userAnswers).length === 0) {
        alert('Vastaa ensin kysymyksiin nähdäksesi puoluevertailun');
        switchTab('questions');
        return;
    }
    
    try {
        const response = await fetch('/api/compare_parties', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_answers: state.userAnswers,
                party_name: partyName
            })
        });
        
        const result = await response.json();
        showPartyComparison(partyName, result);
        
    } catch (error) {
        console.error('Puoluevertailu epäonnistui:', error);
        alert('Vertailu epäonnistui: ' + error.message);
    }
}

// Näytä puoluevertailun tulos
function showPartyComparison(partyName, comparison) {
    partyDetailedComparison.style.display = 'block';
    
    const matchPercentage = comparison.match_percentage || 0;
    const matchLevel = getMatchLevel(matchPercentage);
    
    partyComparisonResults.innerHTML = `
        <div class="comparison-result">
            <div class="comparison-header">
                <h3>🔍 Vertailu: Sinun vs ${partyName}</h3>
                <div class="match-score ${matchLevel}">
                    <div class="match-percentage">${matchPercentage.toFixed(1)}%</div>
                    <div class="match-label">Yhteensopivuus</div>
                </div>
            </div>
            
            <div class="comparison-details">
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-label">Vastattuja kysymyksiä:</span>
                        <span class="detail-value">${comparison.matched_questions || 0}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Ehdokkaita puolueessa:</span>
                        <span class="detail-value">${comparison.candidate_count || 0}</span>
                    </div>
                </div>
            </div>
            
            <div class="comparison-actions">
                <button class="btn" onclick="showDetailedPartyComparison('${partyName}')">
                    📊 Näytä yksityiskohtainen vertailu
                </button>
                <button class="btn secondary" onclick="hidePartyComparison()">
                    Sulje
                </button>
            </div>
        </div>
    `;
    
    // Skrollaa vertailuosion näkyviin
    partyDetailedComparison.scrollIntoView({ behavior: 'smooth' });
}

// PUUTTUVAT FUNKTIOT - LISÄTTY NYT

// Näytä puolueen profiili
async function showPartyProfile(partyName) {
    try {
        // Demo-toteutus - oikeassa sovelluksessa tämä hakee datan API:sta
        const demoData = {
            profile: {
                total_candidates: Math.floor(Math.random() * 10) + 1,
                averaged_answers: {}
            },
            consensus: {
                overall_consensus: Math.floor(Math.random() * 40) + 60 // 60-100%
            }
        };
        
        showPartyProfileModal(partyName, demoData);
        
    } catch (error) {
        console.error('Puolueen profiilin lataus epäonnistui:', error);
        alert('Profiilin lataus epäonnistui: ' + error.message);
    }
}

// Näytä puolueen profiili modaalissa
function showPartyProfileModal(partyName, data) {
    const profile = data.profile;
    const consensus = data.consensus;
    
    const modalHtml = `
        <div class="modal-overlay" onclick="closePartyModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3>📊 ${partyName} - Profiili</h3>
                    <button class="modal-close" onclick="closePartyModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="profile-stats">
                        <div class="stat-item">
                            <span class="stat-label">Ehdokkaita:</span>
                            <span class="stat-value">${profile.total_candidates || 0}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Konsensus:</span>
                            <span class="stat-value">${consensus.overall_consensus?.toFixed(1) || 0}%</span>
                        </div>
                    </div>
                    <div class="profile-notes">
                        <p><small>📝 Täydellinen puolueprofiili on kehitteillä.</small></p>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn secondary" onclick="closePartyModal()">Sulje</button>
                </div>
            </div>
        </div>
    `;
    
    // Lisää modaali DOM:iin
    const modalContainer = document.createElement('div');
    modalContainer.id = 'party-profile-modal';
    modalContainer.innerHTML = modalHtml;
    document.body.appendChild(modalContainer);
}

// Sulje puolueprofiilin modaali
function closePartyModal() {
    const modal = document.getElementById('party-profile-modal');
    if (modal) {
        modal.remove();
    }
}

// Näytä yksityiskohtainen puoluevertailu
async function showDetailedPartyComparison(partyName) {
    // Demo-toteutus
    const questions = await loadQuestionsForComparison();
    const userAnswers = state.userAnswers;
    
    let comparisonHTML = `
        <div class="detailed-comparison">
            <h4>Yksityiskohtainen vertailu: Sinun vs ${partyName}</h4>
            <div class="comparison-table">
                <table>
                    <thead>
                        <tr>
                            <th>Kysymys</th>
                            <th>Sinun vastaus</th>
                            <th>Puolueen keskiarvo</th>
                            <th>Ero</th>
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    // Lisää demo-dataa
    questions.slice(0, 5).forEach(question => {
        const userAnswer = userAnswers[question.id] || 0;
        const partyAverage = (Math.random() * 10 - 5).toFixed(1); // Satunnainen demo-arvo
        const difference = Math.abs(userAnswer - partyAverage).toFixed(1);
        
        comparisonHTML += `
            <tr>
                <td>${question.question?.fi || question.question}</td>
                <td>${userAnswer}</td>
                <td>${partyAverage}</td>
                <td>${difference}</td>
            </tr>
        `;
    });
    
    comparisonHTML += `
                    </tbody>
                </table>
            </div>
            <div class="comparison-notes">
                <p><small>📊 Demo-data - oikea vertailu vaatii puolueprofiilien generoinnin</small></p>
            </div>
        </div>
    `;
    
    partyComparisonResults.innerHTML = comparisonHTML;
}

function hidePartyComparison() {
    partyDetailedComparison.style.display = 'none';
}

// EHDOKAAN LISÄYSTOIMINNALLISUUS
function updatePartySuggestions() {
    const datalist = document.getElementById('party-suggestions');
    if (!datalist) return;
    
    datalist.innerHTML = state.parties.map(party => 
        `<option value="${party}">`
    ).join('');
}

function initCandidateForm() {
    if (!candidateForm) return;
    
    // Lataa kysymykset lomaketta varten
    loadQuestionsForCandidateForm();
    
    candidateForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(candidateForm);
        const candidateData = {
            name: formData.get('name'),
            party: formData.get('party'),
            district: formData.get('district'),
            answers: []
        };
        
        // Kerää vastaukset kysymyksiin
        state.questions.forEach(question => {
            const answerInput = document.querySelector(`input[name="answer_${question.id}"]`);
            if (answerInput) {
                candidateData.answers.push({
                    question_id: question.id,
                    answer: parseInt(answerInput.value),
                    confidence: 1.0
                });
            }
        });
        
        try {
            const response = await fetch('/api/add_candidate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(candidateData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                candidateResult.innerHTML = `
                    <div class="success-message">
                        ✅ Ehdokas "${candidateData.name}" lisätty onnistuneesti!
                    </div>
                `;
                candidateForm.reset();
                
                // Päivitä ehdokkaat ja puolueet
                loadCandidates();
                loadParties();
                
            } else {
                candidateResult.innerHTML = `
                    <div class="error-message">❌ Virhe: ${result.error}</div>
                `;
            }
        } catch (error) {
            candidateResult.innerHTML = `
                <div class="error-message">❌ Verkkovirhe: ${error.message}</div>
            `;
        }
    });
}

// Lataa kysymykset ehdokaslomaketta varten
async function loadQuestionsForCandidateForm() {
    try {
        const answersContainer = document.getElementById('candidate-answers');
        if (!answersContainer) return;

        answersContainer.innerHTML = state.questions.map(question => `
            <div class="answer-row">
                <div class="question-text">
                    <strong>${question.question?.fi || question.question}</strong>
                    ${question.category?.fi ? `<br><small>Kategoria: ${question.category.fi}</small>` : ''}
                </div>
                <div class="answer-controls">
                    <span class="scale-min">-5</span>
                    <input type="range" id="answer-${question.id}" 
                           name="answer_${question.id}" 
                           min="-5" max="5" value="0" 
                           class="answer-slider"
                           oninput="updateAnswerValue(${question.id}, this.value)">
                    <span class="scale-max">+5</span>
                    <span class="answer-value" id="value-${question.id}">0</span>
                </div>
                <div class="scale-labels">
                    <span>Täysin eri mieltä</span>
                    <span>Neutraali</span>
                    <span>Täysin samaa mieltä</span>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Kysymysten lataus epäonnistui:', error);
    }
}

// Lataa kysymykset vertailua varten
async function loadQuestionsForComparison() {
    // Palauta olemassa olevat kysymykset
    return state.questions;
}

// Päivitä vastauksen arvon näyttö
function updateAnswerValue(questionId, value) {
    const valueDisplay = document.getElementById(`value-${questionId}`);
    if (valueDisplay) {
        valueDisplay.textContent = value;
    }
}

// VÄLILEHTIEN HALLINTA
function initTabs() {
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', (e) => {
            const tabName = e.target.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Päivitä aktiivinen välilehti
    document.querySelectorAll('.tab-button').forEach(btn => 
        btn.classList.remove('active')
    );
    document.querySelectorAll('.tab-content').forEach(content => 
        content.classList.remove('active')
    );
    
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
    state.currentTab = tabName;
    
    // Lataa välilehden spesifinen data
    if (tabName === 'parties' && state.parties.length === 0) {
        loadParties();
    }
}

// Päivittää kategoriasuodattimen vaihtoehdot
function updateCategoryFilter() {
    const categories = [...new Set(state.questions.map(q => q.category?.fi || q.category || 'Yleinen'))];
    
    if (categoryFilter) {
        categoryFilter.innerHTML = '<option value="all">Kaikki kategoriat</option>';
        
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            categoryFilter.appendChild(option);
        });
    }
}

// Päivittää edistymispalkin
function updateProgressBar() {
    const totalQuestions = state.questions.length;
    const answeredQuestions = Object.keys(state.userAnswers).length;
    const percentage = totalQuestions > 0 ? (answeredQuestions / totalQuestions) * 100 : 0;
    
    if (progressBar) {
        progressBar.style.width = `${percentage}%`;
    }
    if (progressText) {
        progressText.textContent = `${answeredQuestions}/${totalQuestions} kysymykseen vastattu`;
    }
}

// Näyttää yksityiskohtaisen vertailun
function showDetailedComparison() {
    const answeredQuestions = Object.keys(state.userAnswers).length;
    if (answeredQuestions === 0) {
        alert('Vastaa ensin vähintään yhteen kysymykseen nähdäksesi yksityiskohtaisen vertailun.');
        return;
    }
    
    let tableHTML = `
        <table class="comparison-table">
            <thead>
                <tr>
                    <th>Kysymys</th>
                    <th>Sinun vastauksesi</th>
    `;
    
    state.candidates.forEach(candidate => {
        tableHTML += `<th>${candidate.name} (${candidate.party})</th>`;
    });
    
    tableHTML += `</tr></thead><tbody>`;
    
    state.questions.forEach(question => {
        const userAnswer = state.userAnswers[question.id];
        if (userAnswer === undefined) return;
        
        tableHTML += `<tr>
            <td>${question.question?.fi || question.question}</td>
            <td>${userAnswer}</td>`;
        
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
        state.filteredQuestions = state.questions.filter(q => 
            (q.category?.fi || q.category) === category
        );
    }
    renderQuestions();
}

// APUFUNKTIOT
function getMatchLevel(percentage) {
    if (percentage >= 80) return 'excellent';
    if (percentage >= 60) return 'good';
    if (percentage >= 40) return 'moderate';
    return 'poor';
}

function showLoading(element, message = 'Ladataan...') {
    if (element) {
        element.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        `;
    }
}

function showError(element, message) {
    if (element) {
        element.innerHTML = `
            <div class="error-message">
                ❌ ${message}
            </div>
        `;
    }
}

function loadUserAnswers() {
    const savedAnswers = localStorage.getItem('userAnswers');
    if (savedAnswers) {
        state.userAnswers = JSON.parse(savedAnswers);
    }
}

// Alusta tapahtumankäsittelijät
function initEventHandlers() {
    // Olemassa olevat käsittelijät
    if (categoryFilter) {
        categoryFilter.addEventListener('change', (e) => {
            filterQuestionsByCategory(e.target.value);
        });
    }
    
    if (sortBySelect) {
        sortBySelect.addEventListener('change', (e) => {
            state.sortBy = e.target.value;
            renderCandidates();
        });
    }
    
    if (compareBtn) {
        compareBtn.addEventListener('click', () => {
            calculateMatches();
        });
    }
    
    if (detailsBtn) {
        detailsBtn.addEventListener('click', () => {
            showDetailedComparison();
        });
    }
    
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            exportResults();
        });
    }
    
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => {
            comparisonModal.style.display = 'none';
        });
    }
    
    // Sulje modaali, kun klikataan sen ulkopuolelle
    window.addEventListener('click', (e) => {
        if (e.target === comparisonModal) {
            comparisonModal.style.display = 'none';
        }
    });
    
    // Uudet käsittelijät
    if (compareAllPartiesBtn) {
        compareAllPartiesBtn.addEventListener('click', () => {
            if (Object.keys(state.userAnswers).length === 0) {
                alert('Vastaa ensin kysymyksiin nähdäksesi puoluevertailun');
                switchTab('questions');
                return;
            }
            calculatePartyMatches();
        });
    }
    
    if (refreshPartyDataBtn) {
        refreshPartyDataBtn.addEventListener('click', loadParties);
    }
    
    // Alusta ehdokaslomake
    initCandidateForm();
}

// Alustus
function init() {
    loadQuestions();
    loadCandidates();
    loadParties();
    initTabs();
    initEventHandlers();
    
    // Lataa käyttäjän tallennetut vastaukset
    loadUserAnswers();
}

// Julkiset funktiot
window.compareWithParty = compareWithParty;
window.showPartyProfile = showPartyProfile;
window.showDetailedPartyComparison = showDetailedPartyComparison;
window.hidePartyComparison = hidePartyComparison;
window.closePartyModal = closePartyModal;
window.updateAnswerValue = updateAnswerValue;

// Käynnistä sovellus
document.addEventListener('DOMContentLoaded', init);
