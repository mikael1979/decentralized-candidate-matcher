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
        console.log('🔄 Ladataan puolueita...');
        const response = await fetch('/api/parties');
        if (!response.ok) throw new Error('Puolueita ei voitu ladata');
        
        state.parties = await response.json();
        console.log('✅ Puolueet ladattu:', state.parties);
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
        console.log(`🔄 Ladataan profiilia puolueelle: ${partyName}`);
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

// Luo puolueprofiilit - DEBUG VERSIO
generateProfilesBtn.addEventListener('click', async () => {
    console.log('🔄 Painike painettu - aloitetaan profiilien luonti');
    
    try {
        // Testaa vain yhden puolueen kanssa ensin
        const testParty = state.parties[0];
        if (!testParty) {
            alert('Ei puolueita saatavilla');
            return;
        }
        
        console.log(`🔍 Testataan puoluetta: "${testParty}"`);
        
        const encodedParty = encodeURIComponent(testParty);
        console.log(`🔍 Encoded party: "${encodedParty}"`);
        
        const response = await fetch(`/api/generate_party_profile/${encodedParty}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        console.log('📡 Vastaus saatu:', response.status, response.statusText);
        
        // Käsittele vastaus
        const responseText = await response.text();
        console.log('📄 Raaka vastaus:', responseText.substring(0, 200) + '...');
        
        let result;
        try {
            result = JSON.parse(responseText);
            console.log('✅ JSON parsittu:', result);
        } catch (e) {
            console.error('❌ JSON parsiminen epäonnistui:', e);
            throw new Error('Palvelin palautti virheellistä dataa: ' + responseText.substring(0, 100));
        }
        
        if (!response.ok) {
            throw new Error(`HTTP virhe! status: ${response.status}, viesti: ${result.error || 'Tuntematon virhe'}`);
        }
        
        if (result.success) {
            alert(`✅ Puolueprofiili luotu onnistuneesti!\nPuolue: ${testParty}\nCID: ${result.cid}`);
        } else {
            alert(`❌ Profiilin luonti epäonnistui: ${result.error}`);
        }
        
    } catch (error) {
        console.error('💥 Virhe profiilin luonnissa:', error);
        alert('Profiilin luonti epäonnistui: ' + error.message);
    }
});

// Alustus
function init() {
    console.log('🚀 Alustetaan puolueet-sivu...');
    loadParties();
    
    // Lataa käyttäjän vastaukset localStoragesta
    const savedAnswers = localStorage.getItem('userAnswers');
    if (savedAnswers) {
        state.userAnswers = JSON.parse(savedAnswers);
    }
    
    console.log('✅ Puolueet-sivu alustettu');
}

document.addEventListener('DOMContentLoaded', init);
