// Puoluevertailun tila
const state = {
    parties: [],
    partyProfiles: new Map(),
    userAnswers: JSON.parse(localStorage.getItem('userAnswers')) || {},
    currentElection: null,
    comparisons: []
};

// DOM-elementit
const partiesContainer = document.getElementById('parties-container');
const comparePartiesBtn = document.getElementById('compare-parties-btn');
const generateProfilesBtn = document.getElementById('generate-profiles-btn');
const comparisonSection = document.getElementById('comparison-section');
const partyComparisonResults = document.getElementById('party-comparison-results');
const candidateFormContainer = document.getElementById('candidate-form-container');

// Ehdokkaan lisäämisen tila
const candidateState = {
    questions: [],
    currentStep: 1,
    totalSteps: 3
};

// Lataa järjestelmätiedot
async function loadSystemInfo() {
    try {
        const response = await fetch('/api/system_info');
        const systemInfo = await response.json();
        state.currentElection = systemInfo.election;
        
        // Päivitä sivun otsikko
        document.title = `Puoluevertailu - ${systemInfo.election.name.fi}`;
        
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

// Lataa puolueet
async function loadParties() {
    try {
        console.log('🔄 Ladataan puolueita...');
        showLoading(partiesContainer, 'Ladataan puolueita...');
        
        const response = await fetch('/api/parties');
        if (!response.ok) throw new Error('Puolueita ei voitu ladata');
        
        state.parties = await response.json();
        console.log('✅ Puolueet ladattu:', state.parties);
        
        renderParties();
        
    } catch (error) {
        console.error('❌ Virhe puolueiden lataamisessa:', error);
        showError(partiesContainer, 'Puolueiden lataus epäonnistui');
    }
}

// Renderöi puoluelista
function renderParties() {
    if (!partiesContainer) return;
    
    if (state.parties.length === 0) {
        partiesContainer.innerHTML = `
            <div class="no-data">
                <p>Ei puolueita saatavilla</p>
                <p class="suggestion">
                    Lisää ehdokkaita puolueineen ensin hallintapaneelissa.
                </p>
            </div>
        `;
        return;
    }
    
    partiesContainer.innerHTML = `
        <div class="parties-header">
            <h3>📊 Puolueet (${state.parties.length} kpl)</h3>
            <p>Valitse puolue nähdäksesi sen profiilin tai vertailaksesi sen kanssa</p>
        </div>
        <div class="parties-grid">
            ${state.parties.map(party => createPartyCard(party)).join('')}
        </div>
    `;
}

function createPartyCard(party) {
    const profile = state.partyProfiles.get(party);
    const candidateCount = profile?.total_candidates || 0;
    const consensus = profile?.consensus?.overall_consensus || 0;
    
    return `
        <div class="party-card">
            <div class="party-header">
                <h3 class="party-name">${party}</h3>
                <div class="party-stats">
                    <span class="candidate-count">👤 ${candidateCount} ehdokasta</span>
                    ${consensus > 0 ? `<span class="consensus-score">${consensus.toFixed(1)}% konsensus</span>` : ''}
                </div>
            </div>
            
            <div class="party-actions">
                <button class="btn small" onclick="loadPartyProfile('${party}')" title="Näytä puolueen profiili">
                    📈 Profiili
                </button>
                <button class="btn small secondary" onclick="compareWithParty('${party}')" title="Vertaa omaa kantaa puolueeseen">
                    🔍 Vertaa
                </button>
                ${candidateCount === 0 ? `
                    <button class="btn small warning" onclick="addCandidateToParty('${party}')" title="Lisää ehdokas puolueeseen">
                        ➕ Lisää ehdokas
                    </button>
                ` : ''}
            </div>
            
            <div class="party-profile" id="profile-${party.replace(/[^a-zA-Z0-9]/g, '-')}">
                ${profile ? renderPartyProfileMini(profile) : ''}
            </div>
        </div>
    `;
}

function renderPartyProfileMini(profile) {
    if (!profile.averaged_answers || Object.keys(profile.averaged_answers).length === 0) {
        return '<div class="no-profile">Ei profiilitietoja saatavilla</div>';
    }
    
    const answerCount = Object.keys(profile.averaged_answers).length;
    const consensusLevel = getConsensusLevel(profile.consensus?.overall_consensus || 0);
    
    return `
        <div class="profile-mini">
            <div class="mini-stats">
                <span class="stat">${answerCount} vastausta</span>
                <span class="consensus ${consensusLevel}">${profile.consensus?.overall_consensus?.toFixed(1) || 0}% yhtenäisyyttä</span>
            </div>
        </div>
    `;
}

function getConsensusLevel(consensus) {
    if (consensus >= 80) return 'high';
    if (consensus >= 60) return 'medium';
    return 'low';
}

// Lataa puolueen profiili
async function loadPartyProfile(partyName) {
    try {
        console.log(`🔄 Ladataan profiilia puolueelle: ${partyName}`);
        showProfileLoading(partyName);
        
        const response = await fetch(`/api/party/${encodeURIComponent(partyName)}`);
        if (!response.ok) throw new Error('Profiilia ei voitu ladata');
        
        const data = await response.json();
        state.partyProfiles.set(partyName, data);
        
        displayPartyProfile(partyName, data);
        
    } catch (error) {
        console.error('❌ Virhe profiilin lataamisessa:', error);
        showProfileError(partyName, 'Profiilin lataus epäonnistui');
    }
}

function showProfileLoading(partyName) {
    const profileContainer = getProfileContainer(partyName);
    if (profileContainer) {
        profileContainer.innerHTML = '<div class="loading">Ladataan profiilia...</div>';
    }
}

function showProfileError(partyName, message) {
    const profileContainer = getProfileContainer(partyName);
    if (profileContainer) {
        profileContainer.innerHTML = `
            <div class="error-message">
                ❌ ${message}
                <br><button class="btn small" onclick="loadPartyProfile('${partyName}')">Yritä uudelleen</button>
            </div>
        `;
    }
}

function getProfileContainer(partyName) {
    const safePartyName = partyName.replace(/[^a-zA-Z0-9]/g, '-');
    return document.getElementById(`profile-${safePartyName}`);
}

// Näytä puolueen profiili
function displayPartyProfile(partyName, data) {
    const profileContainer = getProfileContainer(partyName);
    if (!profileContainer) return;
    
    const profile = data.profile;
    const consensus = data.consensus;
    
    if (!profile || !consensus) {
        profileContainer.innerHTML = '<div class="no-data">Profiilia ei saatavilla</div>';
        return;
    }
    
    profileContainer.innerHTML = `
        <div class="party-profile-details">
            <div class="profile-stats">
                <div class="stat-item">
                    <span class="stat-label">Ehdokkaita:</span>
                    <span class="stat-value">${profile.total_candidates || 0}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Konsensus:</span>
                    <span class="stat-value ${getConsensusLevel(consensus.overall_consensus)}">
                        ${consensus.overall_consensus?.toFixed(1) || 0}%
                    </span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Vastauksia:</span>
                    <span class="stat-value">${Object.keys(profile.averaged_answers || {}).length}</span>
                </div>
            </div>
            
            ${Object.keys(profile.averaged_answers || {}).length > 0 ? `
                <div class="profile-actions">
                    <button class="btn small" onclick="showDetailedProfile('${partyName}')">
                        📊 Näytä yksityiskohtainen profiili
                    </button>
                </div>
            ` : ''}
        </div>
    `;
}

// Näytä yksityiskohtainen profiili
async function showDetailedProfile(partyName) {
    const data = state.partyProfiles.get(partyName);
    if (!data) return;
    
    const profile = data.profile;
    const consensus = data.consensus;
    
    const questions = await loadQuestions();
    const answers = profile.averaged_answers || {};
    
    const modalHtml = `
        <div class="modal-overlay" onclick="closeModal()">
            <div class="modal-content large" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3>📊 ${partyName} - Yksityiskohtainen profiili</h3>
                    <button class="modal-close" onclick="closeModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="profile-summary">
                        <div class="summary-stats">
                            <div class="summary-stat">
                                <strong>${profile.total_candidates || 0}</strong>
                                <span>Ehdokasta</span>
                            </div>
                            <div class="summary-stat">
                                <strong>${Object.keys(answers).length}</strong>
                                <span>Vastausta</span>
                            </div>
                            <div class="summary-stat">
                                <strong>${consensus.overall_consensus?.toFixed(1) || 0}%</strong>
                                <span>Konsensus</span>
                            </div>
                            <div class="summary-stat">
                                <strong>${consensus.comparison_pairs || 0}</strong>
                                <span>Vertailuparia</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="answers-section">
                        <h4>Keskiarvovastaukset</h4>
                        ${Object.keys(answers).length > 0 ? `
                            <div class="answers-list">
                                ${Object.entries(answers).map(([questionId, avgAnswer]) => {
                                    const question = questions.find(q => q.id == questionId);
                                    return question ? `
                                        <div class="answer-item">
                                            <div class="question-text">${question.question.fi}</div>
                                            <div class="answer-value">
                                                <span class="avg-answer">${avgAnswer.toFixed(1)}</span>
                                                <div class="answer-scale">
                                                    <div class="scale-labels">
                                                        <span>-5</span>
                                                        <span>0</span>
                                                        <span>+5</span>
                                                    </div>
                                                    <div class="scale-bar">
                                                        <div class="scale-fill" style="left: 50%; width: ${((avgAnswer + 5) / 10) * 100}%"></div>
                                                        <div class="scale-marker" style="left: ${((avgAnswer + 5) / 10) * 100}%"></div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    ` : '';
                                }).join('')}
                            </div>
                        ` : '<div class="no-data">Ei vastauksia saatavilla</div>'}
                    </div>
                    
                    <div class="consensus-section">
                        <h4>Puolueen sisäinen yhtenäisyys</h4>
                        <div class="consensus-info">
                            <div class="consensus-bar">
                                <div class="consensus-fill" style="width: ${consensus.overall_consensus || 0}%"></div>
                            </div>
                            <div class="consensus-text">
                                <strong>${consensus.overall_consensus?.toFixed(1) || 0}%</strong> - ${getConsensusDescription(consensus.overall_consensus || 0)}
                            </div>
                            <div class="consensus-details">
                                Perustuu ${consensus.comparison_pairs || 0} vertailupariin 
                                ${consensus.candidate_count || 0} ehdokkaan kesken
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn secondary" onclick="closeModal()">Sulje</button>
                </div>
            </div>
        </div>
    `;
    
    showModal(modalHtml);
}

function getConsensusDescription(consensus) {
    if (consensus >= 90) return 'Erittäin korkea yhtenäisyys';
    if (consensus >= 75) return 'Korkea yhtenäisyys';
    if (consensus >= 60) return 'Kohtalainen yhtenäisyys';
    if (consensus >= 40) return 'Matala yhtenäisyys';
    return 'Erittäin matala yhtenäisyys';
}

// Vertaa käyttäjän vastauksia puolueeseen
async function compareWithParty(partyName) {
    if (Object.keys(state.userAnswers).length === 0) {
        showComparisonError('Vastaa ensin kysymyksiin vaalikoneessa vertailuaksesi puolueita.');
        return;
    }
    
    try {
        showComparisonLoading();
        
        const response = await fetch('/api/compare_parties', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_answers: state.userAnswers,
                party_name: partyName
            })
        });
        
        if (!response.ok) throw new Error('Vertailu epäonnistui');
        
        const result = await response.json();
        displayPartyComparison(partyName, result);
        
    } catch (error) {
        console.error('❌ Virhe vertailussa:', error);
        showComparisonError('Vertailu epäonnistui: ' + error.message);
    }
}

function showComparisonLoading() {
    comparisonSection.style.display = 'block';
    partyComparisonResults.innerHTML = `
        <div class="loading-comparison">
            <div class="spinner"></div>
            <p>Ladataan vertailutuloksia...</p>
        </div>
    `;
}

function showComparisonError(message) {
    comparisonSection.style.display = 'block';
    partyComparisonResults.innerHTML = `
        <div class="error-message">
            ❌ ${message}
            ${Object.keys(state.userAnswers).length === 0 ? `
                <br>
                <a href="/vaalikone" class="btn small">Siirry vaalikoneeseen</a>
            ` : ''}
        </div>
    `;
}

// Näytä puoluevertailu
function displayPartyComparison(partyName, comparison) {
    comparisonSection.style.display = 'block';
    
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
                    <div class="detail-item">
                        <span class="detail-label">Yhteensopivuus:</span>
                        <span class="detail-value ${matchLevel}">${getMatchDescription(matchPercentage)}</span>
                    </div>
                </div>
            </div>
            
            <div class="comparison-actions">
                <button class="btn" onclick="showDetailedComparison('${partyName}')">
                    📊 Näytä yksityiskohtainen vertailu
                </button>
                <button class="btn secondary" onclick="hideComparison()">
                    Sulje
                </button>
            </div>
        </div>
    `;
}

function getMatchLevel(percentage) {
    if (percentage >= 80) return 'excellent';
    if (percentage >= 60) return 'good';
    if (percentage >= 40) return 'moderate';
    return 'poor';
}

function getMatchDescription(percentage) {
    if (percentage >= 80) return 'Erittäin korkea';
    if (percentage >= 60) return 'Korkea';
    if (percentage >= 40) return 'Kohtalainen';
    if (percentage >= 20) return 'Matala';
    return 'Erittäin matala';
}

function hideComparison() {
    comparisonSection.style.display = 'none';
}

// Näytä yksityiskohtainen vertailu
async function showDetailedComparison(partyName) {
    const questions = await loadQuestions();
    const profile = state.partyProfiles.get(partyName);
    
    if (!profile) {
        alert('Puolueen profiilia ei saatavilla. Lataa profiili ensin.');
        return;
    }
    
    const partyAnswers = profile.profile.averaged_answers || {};
    const comparisonDetails = [];
    
    for (const [questionId, partyAnswer] of Object.entries(partyAnswers)) {
        const userAnswer = state.userAnswers[questionId];
        if (userAnswer !== undefined) {
            const question = questions.find(q => q.id == questionId);
            if (question) {
                const difference = Math.abs(userAnswer - partyAnswer);
                const similarity = Math.max(0, 100 - (difference * 10));
                
                comparisonDetails.push({
                    question: question.question.fi,
                    userAnswer,
                    partyAnswer: partyAnswer.toFixed(1),
                    difference: difference.toFixed(1),
                    similarity: similarity.toFixed(1),
                    similarityLevel: getMatchLevel(similarity)
                });
            }
        }
    }
    
    // Järjestä erotuksen mukaan (suurimmat erot ensin)
    comparisonDetails.sort((a, b) => b.difference - a.difference);
    
    const modalHtml = `
        <div class="modal-overlay" onclick="closeModal()">
            <div class="modal-content xlarge" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3>📊 Yksityiskohtainen vertailu: Sinun vs ${partyName}</h3>
                    <button class="modal-close" onclick="closeModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="detailed-comparison">
                        <div class="comparison-summary">
                            <div class="summary-item">
                                <strong>${comparisonDetails.length}</strong>
                                <span>Yhteensä vertailtua kysymystä</span>
                            </div>
                            <div class="summary-item">
                                <strong>${calculateOverallSimilarity(comparisonDetails).toFixed(1)}%</strong>
                                <span>Kokonaisyhteensopivuus</span>
                            </div>
                        </div>
                        
                        <div class="comparison-table">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Kysymys</th>
                                        <th>Sinun vastaus</th>
                                        <th>Puolueen keskiarvo</th>
                                        <th>Ero</th>
                                        <th>Yhteensopivuus</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${comparisonDetails.map(detail => `
                                        <tr>
                                            <td class="question-cell">${detail.question}</td>
                                            <td class="answer-cell">${detail.userAnswer}</td>
                                            <td class="answer-cell">${detail.partyAnswer}</td>
                                            <td class="difference-cell">${detail.difference}</td>
                                            <td class="similarity-cell ${detail.similarityLevel}">
                                                ${detail.similarity}%
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn secondary" onclick="closeModal()">Sulje</button>
                </div>
            </div>
        </div>
    `;
    
    showModal(modalHtml);
}

function calculateOverallSimilarity(comparisonDetails) {
    if (comparisonDetails.length === 0) return 0;
    const totalSimilarity = comparisonDetails.reduce((sum, detail) => sum + parseFloat(detail.similarity), 0);
    return totalSimilarity / comparisonDetails.length;
}

// Vertaa kaikkia puolueita
async function compareAllParties() {
    if (Object.keys(state.userAnswers).length === 0) {
        showComparisonError('Vastaa ensin kysymyksiin vaalikoneessa vertailuaksesi puolueita.');
        return;
    }
    
    try {
        showComparisonLoading();
        
        const response = await fetch('/api/compare_all_parties', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_answers: state.userAnswers })
        });
        
        if (!response.ok) throw new Error('Vertailu epäonnistui');
        
        const comparisons = await response.json();
        displayAllPartyComparisons(comparisons);
        
    } catch (error) {
        console.error('❌ Virhe vertailussa:', error);
        showComparisonError('Vertailu epäonnistui: ' + error.message);
    }
}

// Näytä kaikkien puolueiden vertailu
function displayAllPartyComparisons(comparisons) {
    comparisonSection.style.display = 'block';
    
    partyComparisonResults.innerHTML = `
        <div class="all-comparisons">
            <div class="comparisons-header">
                <h3>🏛️ Kaikkien puolueiden vertailu</h3>
                <p>Parhaiten sinun vastauksiisi sopivat puolueet:</p>
            </div>
            
            <div class="comparisons-list">
                ${comparisons.map((comp, index) => `
                    <div class="comparison-item ${index < 3 ? 'top-three' : ''}">
                        <div class="party-rank">#${index + 1}</div>
                        <div class="party-comparison">
                            <div class="party-name">${comp.party_name}</div>
                            <div class="match-info">
                                <div class="match-percentage">${comp.match_percentage?.toFixed(1) || 0}%</div>
                                <div class="match-details">
                                    ${comp.candidate_count || 0} ehdokasta
                                    ${comp.overall_consensus ? ` • ${comp.overall_consensus.toFixed(1)}% konsensus` : ''}
                                </div>
                            </div>
                            <div class="match-bar">
                                <div class="match-fill" style="width: ${comp.match_percentage || 0}%"></div>
                            </div>
                        </div>
                        <div class="comparison-actions">
                            <button class="btn small" onclick="compareWithParty('${comp.party_name}')">
                                🔍 Vertaa
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
            
            <div class="comparisons-footer">
                <p>
                    <small>
                        Vertailu perustuu ${Object.keys(state.userAnswers).length} vastaamaasi kysymykseen.
                        ${comparisons.length > 0 ? `Paras yhteensopivuus: <strong>${comparisons[0].match_percentage?.toFixed(1) || 0}%</strong>` : ''}
                    </small>
                </p>
            </div>
        </div>
    `;
}

// Lataa kysymykset
async function loadQuestions() {
    try {
        const response = await fetch('/api/questions');
        return await response.json();
    } catch (error) {
        console.error('Kysymysten lataus epäonnistui:', error);
        return [];
    }
}

// Ehdokkaan lisääminen
function initCandidateForm() {
    if (!candidateFormContainer) return;
    
    candidateFormContainer.innerHTML = `
        <div class="candidate-form-section">
            <h3>👤 Lisää uusi ehdokas</h3>
            <form id="add-candidate-form" class="candidate-form">
                <div class="form-step" id="step-1">
                    <h4>Vaihe 1: Perustiedot</h4>
                    <div class="form-group">
                        <label for="candidate-name">Ehdokkaan nimi:</label>
                        <input type="text" id="candidate-name" name="name" required>
                    </div>
                    <div class="form-group">
                        <label for="candidate-party">Puolue:</label>
                        <input type="text" id="candidate-party" list="party-suggestions" required>
                        <datalist id="party-suggestions"></datalist>
                    </div>
                    <div class="form-group">
                        <label for="candidate-district">Vaalipiiri:</label>
                        <input type="text" id="candidate-district" name="district" required>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn" onclick="nextStep(2)">Seuraava →</button>
                    </div>
                </div>
                
                <div class="form-step" id="step-2" style="display: none;">
                    <h4>Vaihe 2: Vastaukset kysymyksiin</h4>
                    <div id="candidate-answers" class="answers-container">
                        <div class="loading">Ladataan kysymyksiä...</div>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn secondary" onclick="prevStep(1)">← Edellinen</button>
                        <button type="button" class="btn" onclick="nextStep(3)">Seuraava →</button>
                    </div>
                </div>
                
                <div class="form-step" id="step-3" style="display: none;">
                    <h4>Vaihe 3: Vahvistus</h4>
                    <div id="confirmation-details" class="confirmation-container">
                        <!-- Tähän tulee yhteenveto -->
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn secondary" onclick="prevStep(2)">← Edellinen</button>
                        <button type="submit" class="btn">✅ Lähetä ehdokas</button>
                    </div>
                </div>
            </form>
            <div id="candidate-result"></div>
        </div>
    `;
    
    // Lataa puolue-ehdotukset
    loadPartySuggestions();
    
    // Aseta lomakkeen käsittelijä
    document.getElementById('add-candidate-form').addEventListener('submit', handleCandidateSubmit);
}

// Lataa puolue-ehdotukset
function loadPartySuggestions() {
    const datalist = document.getElementById('party-suggestions');
    if (!datalist) return;
    
    datalist.innerHTML = state.parties.map(party => 
        `<option value="${party}">`
    ).join('');
}

// Lataa kysymykset ehdokaslomaketta varten
async function loadQuestionsForCandidateForm() {
    try {
        const response = await fetch('/api/questions');
        candidateState.questions = await response.json();
        renderCandidateAnswers();
    } catch (error) {
        console.error('Kysymysten lataus epäonnistui:', error);
        document.getElementById('candidate-answers').innerHTML = `
            <div class="error-message">
                ❌ Kysymysten lataus epäonnistui
                <br><button class="btn small" onclick="loadQuestionsForCandidateForm()">Yritä uudelleen</button>
            </div>
        `;
    }
}

// Renderöi vastauskentät
function renderCandidateAnswers() {
    const answersContainer = document.getElementById('candidate-answers');
    if (!answersContainer) return;

    answersContainer.innerHTML = candidateState.questions.map(question => `
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
}

// Päivitä vastauksen arvon näyttö
function updateAnswerValue(questionId, value) {
    const valueDisplay = document.getElementById(`value-${questionId}`);
    if (valueDisplay) {
        valueDisplay.textContent = value;
    }
}

// Vaiheiden hallinta
function nextStep(step) {
    // Piilota nykyinen vaihe
    document.getElementById(`step-${step - 1}`).style.display = 'none';
    
    // Näytä uusi vaihe
    document.getElementById(`step-${step}`).style.display = 'block';
    
    // Lataa tarvittava data
    if (step === 2) {
        loadQuestionsForCandidateForm();
    } else if (step === 3) {
        showConfirmation();
    }
    
    candidateState.currentStep = step;
}

function prevStep(step) {
    document.getElementById(`step-${candidateState.currentStep}`).style.display = 'none';
    document.getElementById(`step-${step}`).style.display = 'block';
    candidateState.currentStep = step;
}

// Näytä vahvistussivu
function showConfirmation() {
    const confirmationContainer = document.getElementById('confirmation-details');
    if (!confirmationContainer) return;
    
    const name = document.getElementById('candidate-name').value;
    const party = document.getElementById('candidate-party').value;
    const district = document.getElementById('candidate-district').value;
    
    // Kerää vastaukset
    const answers = [];
    candidateState.questions.forEach(question => {
        const slider = document.getElementById(`answer-${question.id}`);
        if (slider) {
            answers.push({
                question_id: parseInt(question.id),
                answer: parseInt(slider.value),
                confidence: 1.0
            });
        }
    });
    
    confirmationContainer.innerHTML = `
        <div class="confirmation-details">
            <div class="detail-section">
                <h5>Perustiedot</h5>
                <p><strong>Nimi:</strong> ${name}</p>
                <p><strong>Puolue:</strong> ${party}</p>
                <p><strong>Vaalipiiri:</strong> ${district}</p>
            </div>
            
            <div class="detail-section">
                <h5>Vastaukset (${answers.length} kpl)</h5>
                <div class="answers-summary">
                    ${answers.slice(0, 5).map(answer => {
                        const question = candidateState.questions.find(q => q.id == answer.question_id);
                        return question ? `
                            <div class="answer-summary">
                                <span class="question-text">${question.question.fi.substring(0, 50)}...</span>
                                <span class="answer-value">${answer.answer}</span>
                            </div>
                        ` : '';
                    }).join('')}
                    ${answers.length > 5 ? `<p>...ja ${answers.length - 5} muuta vastausta</p>` : ''}
                </div>
            </div>
        </div>
    `;
}

// Käsittele ehdokkaan lähetys
async function handleCandidateSubmit(e) {
    e.preventDefault();
    
    const resultDiv = document.getElementById('candidate-result');
    try {
        // Kerää lomakkeen tiedot
        const candidateData = {
            name: document.getElementById('candidate-name').value,
            party: document.getElementById('candidate-party').value,
            district: document.getElementById('candidate-district').value,
            answers: []
        };

        // Kerää vastaukset
        candidateState.questions.forEach(question => {
            const slider = document.getElementById(`answer-${question.id}`);
            if (slider) {
                candidateData.answers.push({
                    question_id: parseInt(question.id),
                    answer: parseInt(slider.value),
                    confidence: 1.0
                });
            }
        });

        const response = await fetch('/api/add_candidate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(candidateData)
        });

        const result = await response.json();

        if (result.success) {
            resultDiv.innerHTML = `
                <div class="success-message">
                    ✅ Ehdokas "${candidateData.name}" lisätty onnistuneesti!
                    <br><small>Ehdokas ID: ${result.candidate_id}</small>
                </div>
            `;
            
            // Tyhjennä lomake
            document.getElementById('add-candidate-form').reset();
            
            // Palaa ensimmäiseen vaiheeseen
            document.getElementById('step-3').style.display = 'none';
            document.getElementById('step-1').style.display = 'block';
            candidateState.currentStep = 1;
            
            // Päivitä puoluelista
            setTimeout(() => {
                loadParties();
            }, 1000);
            
        } else {
            resultDiv.innerHTML = `<div class="error-message">❌ Virhe: ${result.error}</div>`;
        }
    } catch (error) {
        console.error('Ehdokkaan lisäämisen virhe:', error);
        resultDiv.innerHTML = `
            <div class="error-message">
                ❌ Verkkovirhe: ${error.message}
            </div>
        `;
    }
}

// Lisää ehdokas puolueeseen
function addCandidateToParty(partyName) {
    // Täytä puolue-kenttä automaattisesti
    const partyInput = document.getElementById('candidate-party');
    if (partyInput) {
        partyInput.value = partyName;
    }
    
    // Siirry ehdokaslomakkeeseen
    candidateFormContainer.scrollIntoView({ behavior: 'smooth' });
}

// Luo puolueprofiilit
async function generatePartyProfiles() {
    try {
        console.log('🔄 Luodaan puolueprofiileja...');
        
        // Testaa vain ensimmäisen puolueen kanssa
        const testParty = state.parties[0];
        if (!testParty) {
            alert('Ei puolueita saatavilla');
            return;
        }
        
        const encodedParty = encodeURIComponent(testParty);
        const response = await fetch(`/api/generate_party_profile/${encodedParty}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`✅ Puolueprofiili luotu onnistuneesti!\nPuolue: ${testParty}\nCID: ${result.cid}`);
            
            // Lataa puolueet uudelleen näyttääksesi päivitetyt profiilit
            loadParties();
        } else {
            alert(`❌ Profiilin luonti epäonnistui: ${result.error}`);
        }
        
    } catch (error) {
        console.error('❌ Virhe profiilin luonnissa:', error);
        alert('Profiilin luonti epäonnistui: ' + error.message);
    }
}

// Modal-toiminnot
function showModal(html) {
    const modalContainer = document.createElement('div');
    modalContainer.id = 'dynamic-modal';
    modalContainer.innerHTML = html;
    document.body.appendChild(modalContainer);
}

function closeModal() {
    const modal = document.getElementById('dynamic-modal');
    if (modal) {
        modal.remove();
    }
}

// Apufunktiot
function showLoading(container, message = 'Ladataan...') {
    if (container) {
        container.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        `;
    }
}

function showError(container, message) {
    if (container) {
        container.innerHTML = `
            <div class="error-message">
                ❌ ${message}
            </div>
        `;
    }
}

// Alustus
async function init() {
    console.log('🚀 Alustetaan puolueet-sivu...');
    
    // Lataa järjestelmätiedot
    await loadSystemInfo();
    
    // Lataa puolueet
    await loadParties();
    
    // Alusta ehdokaslomake
    initCandidateForm();
    
    // Lataa käyttäjän vastaukset
    loadUserAnswers();
    
    // Aseta tapahtumankäsittelijät
    if (comparePartiesBtn) {
        comparePartiesBtn.addEventListener('click', compareAllParties);
    }
    
    if (generateProfilesBtn) {
        generateProfilesBtn.addEventListener('click', generatePartyProfiles);
    }
    
    console.log('✅ Puolueet-sivu alustettu');
}

// Lataa käyttäjän vastaukset
function loadUserAnswers() {
    const savedAnswers = localStorage.getItem('userAnswers');
    if (savedAnswers) {
        state.userAnswers = JSON.parse(savedAnswers);
        console.log(`📝 Käyttäjän vastaukset ladattu: ${Object.keys(state.userAnswers).length} vastausta`);
    }
}

// Käynnistä sovellus
document.addEventListener('DOMContentLoaded', init);
