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

// Lataa kysymykset JSON-tiedostosta
async function loadQuestions() {
    try {
        // Tässä todellisessa sovelluksessa tämä ladataan tiedostosta tai API:sta
        const exampleQuestions = [
            {
                id: 1,
                category: { fi: "Ympäristö", en: "Environment" },
                question: { 
                    fi: "Pitäisikö kaupungin vähentää hiilidioksidipäästöjä 50% vuoteen 2030 mennessä?", 
                    en: "Should the city reduce carbon dioxide emissions by 50% by 2030?" 
                },
                scale: {
                    min: -5,
                    max: 5,
                    labels: {
                        fi: { "-5": "Täysin eri mieltä", "0": "Neutraali", "5": "Täysin samaa mieltä" }
                    }
                }
            },
            {
                id: 2,
                category: { fi: "Liikenne", en: "Transportation" },
                question: { 
                    fi: "Pitäisikö kaupunkipyörien määrää lisätä kesäkaudella?", 
                    en: "Should the number of city bikes be increased during summer season?" 
                },
                scale: {
                    min: -5,
                    max: 5,
                    labels: {
                        fi: { "-5": "Täysin eri mieltä", "0": "Neutraali", "5": "Täysin samaa mieltä" }
                    }
                }
            },
            {
                id: 3,
                category: { fi: "Koulutus", en: "Education" },
                question: { 
                    fi: "Pitäisikö kaupungin tarjota ilmaisia ohjelmointikursseja nuorille?", 
                    en: "Should the city offer free programming courses for youth?" 
                },
                scale: {
                    min: -5,
                    max: 5,
                    labels: {
                        fi: { "-5": "Täysin eri mieltä", "0": "Neutraali", "5": "Täysin samaa mieltä" }
                    }
                }
            },
            {
                id: 4,
                category: { fi: "Terveys", en: "Health" },
                question: { 
                    fi: "Pitäisikö terveyskeskusten aukioloaikoja pidentää iltaan asti?", 
                    en: "Should health center opening hours be extended until evening?" 
                },
                scale: {
                    min: -5,
                    max: 5,
                    labels: {
                        fi: { "-5": "Täysin eri mieltä", "0": "Neutraali", "5": "Täysin samaa mieltä" }
                    }
                }
            },
            {
                id: 5,
                category: { fi: "Asuminen", en: "Housing" },
                question: { 
                    fi: "Pitäisikö kaupungin rakentaa enemmän kaupungin vuokra-asuntoja?", 
                    en: "Should the city build more municipal rental apartments?" 
                },
                scale: {
                    min: -5,
                    max: 5,
                    labels: {
                        fi: { "-5": "Täysin eri mieltä", "0": "Neutraali", "5": "Täysin samaa mieltä" }
                    }
                }
            }
        ];
        
        state.questions = exampleQuestions;
        state.filteredQuestions = [...exampleQuestions];
        
        // Päivitä kysymysten näyttö
        renderQuestions();
        
        // Päivitä kategoriasuodatin
        updateCategoryFilter();
        
        // Päivitä edistymispalkki
        updateProgressBar();
        
    } catch (error) {
        console.error('Virhe kysymysten lataamisessa:', error);
        questionsContainer.innerHTML = '<div class="error">Virhe kysymysten lataamisessa. Tarkista konsoli lisätietoja varten.</div>';
    }
}

// Lataa ehdokkaat JSON-tiedostosta
async function loadCandidates() {
    try {
        // Tässä todellisessa sovelluksessa tämä ladataan tiedostosta tai API:sta
        const exampleCandidates = [
            {
                id: 1,
                name: "Matti Meikäläinen",
                party: "Test Puolue",
                district: "Helsinki",
                answers: [
                    { question_id: 1, answer: 4, confidence: 0.8 },
                    { question_id: 2, answer: 3, confidence: 0.6 },
                    { question_id: 3, answer: 5, confidence: 0.9 },
                    { question_id: 4, answer: -2, confidence: 0.7 },
                    { question_id: 5, answer: 2, confidence: 0.5 }
                ]
            },
            {
                id: 2,
                name: "Liisa Esimerkki",
                party: "Toinen Puolue",
                district: "Espoo",
                answers: [
                    { question_id: 1, answer: 2, confidence: 0.5 },
                    { question_id: 2, answer: 5, confidence: 0.8 },
                    { question_id: 3, answer: 1, confidence: 0.4 },
                    { question_id: 4, answer: 3, confidence: 0.6 },
                    { question_id: 5, answer: -3, confidence: 0.7 }
                ]
            },
            {
                id: 3,
                name: "Pekka Kokeilu",
                party: "Kolmas Puolue",
                district: "Vantaa",
                answers: [
                    { question_id: 1, answer: -3, confidence: 0.7 },
                    { question_id: 2, answer: -1, confidence: 0.5 },
                    { question_id: 3, answer: 4, confidence: 0.8 },
                    { question_id: 4, answer: 5, confidence: 0.9 },
                    { question_id: 5, answer: 4, confidence: 0.8 }
                ]
            },
            {
                id: 4,
                name: "Anna Malli",
                party: "Test Puolue",
                district: "Helsinki",
                answers: [
                    { question_id: 1, answer: 5, confidence: 0.9 },
                    { question_id: 2, answer: 4, confidence: 0.7 },
                    { question_id: 3, answer: -2, confidence: 0.6 },
                    { question_id: 4, answer: -4, confidence: 0.8 },
                    { question_id: 5, answer: -1, confidence: 0.5 }
                ]
            }
        ];
        
        state.candidates = exampleCandidates;
        state.filteredCandidates = [...exampleCandidates];
        
        // Päivitä ehdokkaiden näyttö
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
        
        // Aseta käyttäjän vastaus oletusarvoiseksi neutraaliksi (0)
        const userAnswer = state.userAnswers[question.id] !== undefined ? state.userAnswers[question.id] : null;
        const position = userAnswer !== null ? 
            ((userAnswer - question.scale.min) / (question.scale.max - question.scale.min)) * 100 : 
            50; // Neutraali keskellä jos ei vastausta
        
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
        candidateDetailsElement.textContent = `Alue: ${candidate.district}`;
        
        // Vastaukset kysymyksiin
        const answersListElement = document.createElement('div');
        answersListElement.className = 'answers-list';
        
        candidate.answers.forEach(answer => {
            const question = state.questions.find(q => q.id === answer.question_id);
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
        
        candidate.answers.forEach(answer => {
            const question = state.questions.find(q => q.id === answer.question_id);
            if (!question || state.userAnswers[question.id] === undefined) return;
            
            const userAnswer = state.userAnswers[question.id];
            const candidateAnswer = answer.answer;
            
            // Laske ero käyttäjän ja ehdokkaan vastauksen välillä
            const difference = Math.abs(userAnswer - candidateAnswer);
            totalDifference += difference;
            
            // Laske suurin mahdollinen ero tälle kysymykselle
            const maxDifference = question.scale.max - question.scale.min;
            maxPossibleDifference += maxDifference;
            answeredCount++;
        });
        
        // Laske yhteensopivuusprosentti
        // Mitä pienempi ero, sitä suurempi yhteensopivuus
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
            const candidateAnswer = candidate.answers.find(a => a.question_id === question.id);
            const answerValue = candidateAnswer ? candidateAnswer.answer : '-';
            
            // Lisää värikoodattu ympyrä vastausten yhteensopivuudesta
            let matchClass = '';
            if (candidateAnswer) {
                const difference = Math.abs(userAnswer - candidateAnswer.answer);
                if (difference <= 1) {
                    matchClass = 'match-perfect';
                } else if (difference <= 3) {
                    matchClass = 'match-good';
                } else {
                    matchClass = 'match-poor';
                }
            }
            
            tableHTML += `<td>
                <span class="answer-match ${matchClass}"></span>
                ${answerValue}
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
    
    // Laske alustavat yhteensopivuudet
    setTimeout(() => {
        calculateMatches();
    }, 500);
}

// Käynnistä sovellus
init();