// Puoluevertailun tila
const state = {
    parties: [],
    partyProfiles: {},
    userAnswers: JSON.parse(localStorage.getItem('userAnswers')) || {}
};

// DOM-elementit
const partiesContainer = document.getElementById('parties-container');
const comparePartiesBtn = document.getElementById('compare-parties-btn');
const generateProfilesBtn = document.getElementById('generate-profiles-btn');
const comparisonSection = document.getElementById('comparison-section');
const partyComparisonResults = document.getElementById('party-comparison-results');

// Lataa puolueet
async function loadParties() {
    try {
        const response = await fetch('/api/parties');
        if (!response.ok) throw new Error('Puolueita ei voitu ladata');
        
        state.parties = await response.json();
        renderParties();
        
    } catch (error) {
        console.error('Virhe puolueiden lataamisessa:', error);
        partiesContainer.innerHTML = '<div class="error">Virhe puolueiden lataamisessa</div>';
    }
}

// Renderöi puoluelista
function renderParties() {
    if (state.parties.length === 0) {
        partiesContainer.innerHTML = '<div class="no-data">Ei puolueita saatavilla</div>';
        return;
    }
    
    partiesContainer.innerHTML = state.parties.map(party => `
        <div class="party-card">
            <h3>${party}</h3>
            <div class="party-actions">
                <button class="btn small" onclick="loadPartyProfile('${party}')">
                    Näytä profiili
                </button>
                <button class="btn small secondary" onclick="compareWithParty('${party}')">
                    Vertaa
                </button>
            </div>
            <div class="party-profile" id="profile-${party}"></div>
        </div>
    `).join('');
}

// Lataa puolueen profiili
async function loadPartyProfile(partyName) {
    try {
        const response = await fetch(`/api/party/${encodeURIComponent(partyName)}`);
        if (!response.ok) throw new Error('Profiilia ei voitu ladata');
        
        const data = await response.json();
        state.partyProfiles[partyName] = data;
        
        displayPartyProfile(partyName, data);
        
    } catch (error) {
        console.error('Virhe profiilin lataamisessa:', error);
        document.getElementById(`profile-${partyName}`).innerHTML = 
            '<div class="error">Profiilin lataus epäonnistui</div>';
    }
}

// Näytä puolueen profiili
function displayPartyProfile(partyName, data) {
    const profileContainer = document.getElementById(`profile-${partyName}`);
    const profile = data.profile;
    const consensus = data.consensus;
    
    if (!profile || !consensus) {
        profileContainer.innerHTML = '<div class="no-data">Profiilia ei saatavilla</div>';
        return;
    }
    
    profileContainer.innerHTML = `
        <div class="party-stats">
            <div class="stat">
                <strong>Ehdokkaita:</strong> ${profile.total_candidates || 0}
            </div>
            <div class="stat">
                <strong>Konsensus:</strong> ${consensus.overall_consensus?.toFixed(1) || 0}%
            </div>
            <div class="stat">
                <strong>Vastauksia:</strong> ${Object.keys(profile.averaged_answers || {}).length}
            </div>
        </div>
        ${renderPartyAnswers(profile.averaged_answers)}
    `;
}

// Renderöi puolueen vastaukset
function renderPartyAnswers(answers) {
    if (!answers || Object.keys(answers).length === 0) {
        return '<div class="no-data">Ei vastauksia</div>';
    }
    
    return `
        <div class="party-answers">
            <h4>Keskeisimmät kannat:</h4>
            ${Object.entries(answers).slice(0, 3).map(([qId, answer]) => `
                <div class="party-answer">
                    <div class="answer-value">${answer.answer}/5</div>
                    <div class="answer-confidence">
                        Luottamus: ${(answer.confidence * 100).toFixed(0)}%
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// Vertaa käyttäjän vastauksia puolueeseen
async function compareWithParty(partyName) {
    if (Object.keys(state.userAnswers).length === 0) {
        alert('Vastaa ensin kysymyksiin vaalikoneessa vertailuaksesi puolueita.');
        return;
    }
    
    try {
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
        console.error('Virhe vertailussa:', error);
        alert('Vertailu epäonnistui');
    }
}

// Näytä puoluevertailu
function displayPartyComparison(partyName, comparison) {
    comparisonSection.style.display = 'block';
    partyComparisonResults.innerHTML = `
        <div class="comparison-result">
            <h3>Vertailu puolueen ${partyName} kanssa</h3>
            <div class="match-score">
                Yhteensopivuus: <strong>${comparison.match_percentage?.toFixed(1) || 0}%</strong>
            </div>
            <div class="match-details">
                <p>Vastattuja kysymyksiä: ${comparison.matched_questions || 0}</p>
                <p>Yhteensopivuus pistemäärä: ${comparison.match_score || 0}/${comparison.max_possible_score || 0}</p>
            </div>
        </div>
    `;
}

// Vertaa kaikkia puolueita
comparePartiesBtn.addEventListener('click', async () => {
    if (Object.keys(state.userAnswers).length === 0) {
        alert('Vastaa ensin kysymyksiin vaalikoneessa vertailuaksesi puolueita.');
        return;
    }
    
    try {
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
        console.error('Virhe vertailussa:', error);
        alert('Vertailu epäonnistui');
    }
});

// Näytä kaikkien puolueiden vertailu
function displayAllPartyComparisons(comparisons) {
    comparisonSection.style.display = 'block';
    
    partyComparisonResults.innerHTML = `
        <h3>Kaikkien puolueiden vertailu</h3>
        <div class="comparisons-list">
            ${comparisons.map(comp => `
                <div class="comparison-item">
                    <div class="party-name">${comp.party_name}</div>
                    <div class="match-percentage">${comp.match_percentage?.toFixed(1) || 0}%</div>
                    <div class="match-bar">
                        <div class="match-fill" style="width: ${comp.match_percentage || 0}%"></div>
                    </div>
                    <div class="match-details">
                        Ehdokkaita: ${comp.candidate_count || 0} | 
                        Konsensus: ${comp.overall_consensus?.toFixed(1) || 0}%
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// Luo puolueprofiilit
generateProfilesBtn.addEventListener('click', async () => {
    try {
        const responses = await Promise.all(
            state.parties.map(party => 
                fetch(`/api/generate_party_profile/${encodeURIComponent(party)}`)
            )
        );
        
        const results = await Promise.all(responses.map(r => r.json()));
        
        alert(`Puolueprofiilit luotu onnistuneesti!`);
        
        // Päivitä näkymä
        state.parties.forEach(party => {
            if (state.partyProfiles[party]) {
                loadPartyProfile(party);
            }
        });
        
    } catch (error) {
        console.error('Virhe profiilien luonnissa:', error);
        alert('Profiilien luonti epäonnistui');
    }
});

// Alustus
function init() {
    loadParties();
    
    // Lataa käyttäjän vastaukset localStoragesta
    const savedAnswers = localStorage.getItem('userAnswers');
    if (savedAnswers) {
        state.userAnswers = JSON.parse(savedAnswers);
    }
}

document.addEventListener('DOMContentLoaded', init);
