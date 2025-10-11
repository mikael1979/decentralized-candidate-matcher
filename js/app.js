class VaalikoneApp {
    constructor() {
        this.currentView = 'compare';
        this.comparisonCount = 0;
        this.maxComparisons = 10;
        this.currentPair = null;
        this.initialized = false;
        this.currentQuestionIndex = 0;
        this.questions = [];
        
        this.setupEventListeners();
    }

    async initializeApp() {
        try {
            console.log('🚀 Starting Decentralized Candidate Matcher...');
            
            // DEBUG: Check modules
            console.log('Modules available:', {
                questionManager: !!window.questionManager,
                tagSystem: !!window.tagSystem,
                candidateManager: !!window.candidateManager,
                compatibilityCalculator: !!window.compatibilityCalculator
            });
            
            // Initialize modules
            await window.questionManager.initialize();
            console.log('QuestionManager initialized');
            
            await window.tagSystem.initialize();
            console.log('TagSystem initialized');
            
            if (window.candidateManager && typeof window.candidateManager.initialize === 'function') {
                await window.candidateManager.initialize();
                console.log('CandidateManager initialized');
            }
            
            console.log('✅ All modules initialized');
            
            // Load questions for candidate matching
            this.questions = await window.questionManager.getAllQuestions();
            console.log('Questions loaded for app:', this.questions.length);
            
            // Load view
            this.showView('compare');
            await this.loadComparisonPair();
            
            // Update stats
            this.updateStats();
            
            this.initialized = true;
            console.log('🎉 Decentralized Candidate Matcher started successfully!');
            
        } catch (error) {
            console.error('App initialization failed:', error);
            this.showError(`App initialization failed: ${error.message}`);
        }
    }

    setupEventListeners() {
        // Form submit event
        const questionForm = document.getElementById('question-form');
        if (questionForm) {
            questionForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleQuestionSubmit();
            });
        } else {
            console.warn('Question form not found');
        }
    }

    showView(viewName) {
        console.log('Showing view:', viewName);
        
        // Hide all views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.remove('active');
        });
        
        // Show target view
        const targetView = document.getElementById(`${viewName}-view`);
        if (targetView) {
            targetView.classList.add('active');
            this.currentView = viewName;
        } else {
            console.error('View not found:', viewName);
        }
        
        // Load view-specific data
        switch(viewName) {
            case 'browse':
                this.loadAllQuestions();
                break;
            case 'stats':
                this.updateStats();
                break;
            case 'submit':
                this.loadTagSuggestions();
                break;
            case 'candidate-questions':
                this.loadCurrentQuestion();
                break;
            case 'compatibility-results':
                this.displayCompatibilityResults();
                break;
        }
    }

    async loadComparisonPair() {
        console.log('Loading comparison pair...');
        
        try {
            this.currentPair = await window.questionManager.getComparisonPair();
            console.log('Current pair loaded:', this.currentPair);
            
            const questionAText = document.getElementById('question-a-text');
            const questionBText = document.getElementById('question-b-text');
            
            if (questionAText && questionBText) {
                if (this.currentPair) {
                    questionAText.textContent = this.currentPair.a.content;
                    questionBText.textContent = this.currentPair.b.content;
                    console.log('Questions displayed successfully');
                } else {
                    questionAText.textContent = 'No questions available';
                    questionBText.textContent = 'Create questions first';
                    console.warn('No question pair available');
                }
            } else {
                console.error('Question text elements not found');
            }
            
            this.updateProgress();
        } catch (error) {
            console.error('Error loading comparison pair:', error);
            this.showError('Question loading failed');
        }
    }

    async vote(winner) {
        console.log('Voting for winner:', winner);
        
        if (!this.currentPair) {
            console.error('No current pair for voting');
            return;
        }
        
        const winnerId = winner === 'a' ? this.currentPair.a.id : this.currentPair.b.id;
        const loserId = winner === 'a' ? this.currentPair.b.id : this.currentPair.a.id;
        
        console.log('Vote details - Winner:', winnerId, 'Loser:', loserId);
        
        try {
            const result = await window.ratingSystem.processVote(winnerId, loserId);
            this.comparisonCount++;
            
            // Update stats view
            this.updateStats();
            
            if (this.comparisonCount >= this.maxComparisons) {
                alert('Thank you! You have completed enough comparisons.');
                this.comparisonCount = 0;
            }
            
            // Load new pair
            await this.loadComparisonPair();
            
        } catch (error) {
            console.error('Error processing vote:', error);
            this.showError('Vote processing failed');
        }
    }

    updateProgress() {
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        
        if (progressBar && progressText) {
            progressBar.value = this.comparisonCount;
            progressText.textContent = `${this.comparisonCount}/${this.maxComparisons} comparisons done`;
        }
    }

    async loadAllQuestions() {
        console.log('Loading all questions for browsing...');
        
        try {
            const questions = await window.questionManager.getAllQuestions();
            const container = document.getElementById('questions-list');
            
            if (container) {
                if (questions.length > 0) {
                    container.innerHTML = questions.map(q => `
                        <div class="question-item">
                            <h3>${q.content}</h3>
                            <div class="tags-container">
                                ${q.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                            </div>
                            <div class="question-meta">
                                <span>Rating: ${Math.round(q.rating)}</span>
                                <span>Comparisons: ${q.comparisons}</span>
                                <span>${new Date(q.createdAt).toLocaleDateString('en-US')}</span>
                            </div>
                        </div>
                    `).join('');
                    console.log('Questions displayed in browse view');
                } else {
                    container.innerHTML = '<p>No questions yet. Create the first question!</p>';
                }
            }
        } catch (error) {
            console.error('Error loading questions for browse:', error);
        }
    }

    async updateStats() {
        console.log('Updating statistics...');
        
        try {
            const questions = await window.questionManager.getAllQuestions();
            const tags = window.tagSystem.getAllTags();
            
            // Update basic stats
            if (document.getElementById('total-questions')) {
                document.getElementById('total-questions').textContent = questions.length;
                document.getElementById('total-tags').textContent = tags.size;
                document.getElementById('total-comparisons').textContent = 
                    questions.reduce((sum, q) => sum + q.comparisons, 0);
                document.getElementById('total-users').textContent = 1;
            }
            
            // Show popular tags
            const popularTags = window.tagSystem.getPopularTags(10);
            const popularTagsContainer = document.getElementById('popular-tags');
            if (popularTagsContainer) {
                popularTagsContainer.innerHTML = popularTags
                    .map(tag => `<span class="tag">${tag.name} (${tag.usageCount})</span>`)
                    .join('');
            }
            
            // Show top questions
            const topQuestions = questions
                .sort((a, b) => b.rating - a.rating)
                .slice(0, 5);
                
            const topQuestionsContainer = document.getElementById('top-questions');
            if (topQuestionsContainer) {
                topQuestionsContainer.innerHTML = topQuestions
                    .map(q => `
                        <div class="question-item">
                            <h4>${q.content}</h4>
                            <div class="question-meta">
                                <span>Rating: ${Math.round(q.rating)}</span>
                                <span>Comparisons: ${q.comparisons}</span>
                            </div>
                        </div>
                    `).join('');
            }
        } catch (error) {
            console.error('Error updating stats:', error);
        }
    }

    async handleQuestionSubmit() {
        const questionInput = document.getElementById('question-input');
        const questionText = questionInput.value.trim();
        
        if (!questionText) {
            alert('Please write a question first!');
            return;
        }
        
        try {
            // Check duplicates
            const questions = await window.questionManager.getAllQuestions();
            const duplicates = await window.duplicateDetector.findDuplicates(questionText, questions);
            
            if (duplicates.length > 0) {
                const duplicateList = document.getElementById('duplicate-list');
                const warning = document.getElementById('duplicate-warning');
                
                duplicateList.innerHTML = duplicates.map(dup => `
                    <div class="duplicate-item">
                        <p>${dup.question.content}</p>
                        <small>Similarity: ${Math.round(dup.similarity * 100)}%</small>
                    </div>
                `).join('');
                
                warning.classList.remove('hidden');
                return;
            }
            
            // Create new question
            const question = await window.questionManager.createQuestion(questionText);
            
            // Add selected tags
            const selectedTags = document.querySelectorAll('#tag-suggestions .tag.selected');
            for (const tagElement of selectedTags) {
                await window.tagSystem.addTagToQuestion(question.id, tagElement.textContent);
            }
            
            // Clear form
            questionInput.value = '';
            document.querySelectorAll('#tag-suggestions .tag.selected').forEach(tag => {
                tag.classList.remove('selected');
            });
            
            document.getElementById('duplicate-warning').classList.add('hidden');
            
            alert('Question created successfully!');
            this.showView('compare');
            
        } catch (error) {
            console.error('Error creating question:', error);
            alert('Question creation failed: ' + error.message);
        }
    }

    loadTagSuggestions() {
        const container = document.getElementById('tag-suggestions');
        if (!container) return;
        
        const tags = window.tagSystem.getAllTags();
        container.innerHTML = '';
        
        Array.from(tags.values()).forEach(tag => {
            const tagElement = document.createElement('span');
            tagElement.className = 'tag';
            tagElement.textContent = tag.name;
            tagElement.onclick = () => tagElement.classList.toggle('selected');
            container.appendChild(tagElement);
        });
    }

    loadCurrentQuestion() {
        const container = document.getElementById('candidate-question-container');
        if (!container || this.currentQuestionIndex >= this.questions.length) return;
        
        const question = this.questions[this.currentQuestionIndex];
        const userAnswer = window.candidateManager.getUserAnswer(question.id);
        
        container.innerHTML = `
            <div class="candidate-question">
                <div class="progress">
                    <span>Question ${this.currentQuestionIndex + 1}/${this.questions.length}</span>
                    <progress value="${this.currentQuestionIndex}" max="${this.questions.length}"></progress>
                </div>
                
                <div class="question-text">${question.content}</div>
                
                <div class="answer-scale">
                    ${[1, 2, 3, 4, 5].map(value => `
                        <label class="scale-option ${userAnswer === value ? 'selected' : ''}">
                            <input type="radio" name="answer" value="${value}" 
                                   ${userAnswer === value ? 'checked' : ''}>
                            <div class="scale-value">${value}</div>
                            <div class="scale-desc">${window.compatibilityCalculator.getScaleDescription(value)}</div>
                        </label>
                    `).join('')}
                </div>
                
                <div class="navigation-buttons">
                    <button onclick="window.app.previousQuestion()" 
                            ${this.currentQuestionIndex === 0 ? 'disabled' : ''}>
                        Previous
                    </button>
                    <button onclick="window.app.nextQuestion()">
                        ${this.currentQuestionIndex === this.questions.length - 1 ? 'Show Results' : 'Next'}
                    </button>
                </div>
            </div>
        `;
    }

    displayCompatibilityResults() {
        const container = document.getElementById('compatibility-results-container');
        if (!container) return;
        
        const topCandidates = window.compatibilityCalculator.getTopCompatibleCandidates(3);
        
        if (topCandidates.length === 0) {
            container.innerHTML = `
                <div class="no-results">
                    <h3>No results</h3>
                    <p>Answer some questions first to see your compatibility with candidates.</p>
                    <button onclick="startCandidateComparison()">Start Answering</button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = `
            <div class="compatibility-header">
                <h3>Your Best Matches</h3>
                <p>You have answered ${window.candidateManager.userAnswers.size} questions</p>
            </div>
            
            <div class="candidate-results">
                ${topCandidates.map((result, index) => {
                    const isTop = index === 0;
                    return `
                        <div class="candidate-result ${isTop ? 'top-result' : ''}">
                            <div class="candidate-card">
                                <div class="candidate-image">${result.candidate.image}</div>
                                <div class="candidate-info">
                                    <h3>${result.candidate.name}</h3>
                                    <p class="party">${result.candidate.party}</p>
                                    <p class="description">${result.candidate.description}</p>
                                    <button onclick="showCandidateDetails('${result.candidate.id}')" class="view-details-btn">
                                        View Detailed Answers
                                    </button>
                                </div>
                                <div class="compatibility-score">
                                    <div class="percentage">${result.compatibility}%</div>
                                    <div class="match-breakdown">
                                        <span class="match exact">Exact: ${result.details.exactMatches}</span>
                                        <span class="match close">Close: ${result.details.closeMatches}</span>
                                        <span class="match disagree">Disagree: ${result.details.disagreements}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
            
            <div class="results-actions">
                <button onclick="startCandidateComparison()">Answer Again</button>
                <button onclick="showView('compare')">Back to Comparison</button>
            </div>
        `;
    }

    showCandidateDetails(candidateId) {
        this.showView('candidate-details');
        this.loadCandidateDetails(candidateId);
    }

    loadCandidateDetails(candidateId) {
        const container = document.getElementById('candidate-details-container');
        if (!container) return;

        const candidate = window.candidateManager.candidates.get(candidateId);
        if (!candidate) {
            container.innerHTML = '<p>Candidate not found</p>';
            return;
        }

        const candidateAnswers = window.candidateManager.getCandidateAnswers(candidateId);
        const compatibility = window.candidateManager.calculateCompatibility(candidateId);
        const userAnswers = window.candidateManager.userAnswers;

        let html = `
            <div class="candidate-profile">
                <div class="candidate-profile-image">${candidate.image}</div>
                <div class="candidate-profile-info">
                    <h3>${candidate.name}</h3>
                    <p class="candidate-profile-party">${candidate.party}</p>
                    <p class="candidate-profile-description">${candidate.description}</p>
                    <div class="compatibility-badge">Match: ${compatibility}%</div>
                </div>
            </div>
            <div class="answers-list">
        `;

        this.questions.forEach(question => {
            const candidateAnswer = candidateAnswers.get(question.id);
            const userAnswer = userAnswers.get(question.id);
            const justification = window.candidateManager.getJustification(candidateId, question.id);
            
            const answerDescription = candidateAnswer ? 
                window.compatibilityCalculator.getScaleDescription(candidateAnswer) : 
                'No answer';
            
            const answerClass = candidateAnswer === userAnswer ? 'exact' : 
                               candidateAnswer && userAnswer && Math.abs(candidateAnswer - userAnswer) <= 1 ? 'close' : 
                               'disagree';

            html += `
                <div class="answer-item ${answerClass}">
                    <div class="answer-question">${question.content}</div>
                    <div class="answer-details">
                        <div class="answer-scale">
                            <div class="answer-value">${candidateAnswer || '-'}</div>
                            <div class="answer-description">${answerDescription}</div>
                            ${userAnswer ? `
                                <div class="user-comparison">
                                    <small>Your answer: ${userAnswer} (${window.compatibilityCalculator.getScaleDescription(userAnswer)})</small>
                                </div>
                            ` : ''}
                        </div>
                        <div class="justification-section">
                            <h4>Candidate's Justification:</h4>
                            <div class="justification-text">
                                ${justification || '<span class="empty-justification">No justification provided</span>'}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        html += `</div>`;
        container.innerHTML = html;
    }

    startCandidateComparison() {
        this.currentQuestionIndex = 0;
        this.showView('candidate-questions');
        this.loadCurrentQuestion();
    }

    nextQuestion() {
        const selectedAnswer = document.querySelector('input[name="answer"]:checked');
        if (!selectedAnswer) {
            alert('Please select an answer before continuing!');
            return;
        }
        
        const currentQuestion = this.questions[this.currentQuestionIndex];
        window.candidateManager.setUserAnswer(currentQuestion.id, parseInt(selectedAnswer.value));
        
        this.currentQuestionIndex++;
        
        if (this.currentQuestionIndex < this.questions.length) {
            this.loadCurrentQuestion();
        } else {
            this.showView('compatibility-results');
            this.displayCompatibilityResults();
        }
    }

    previousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.currentQuestionIndex--;
            this.loadCurrentQuestion();
        }
    }

    showError(message) {
        console.error('Error:', message);
        alert(message);
    }
}

// GLOBAL FUNCTIONS - MOVE TO TOP OF FILE
function showView(viewName) {
    if (window.app && window.app.initialized) {
        window.app.showView(viewName);
    } else {
        console.warn('App not initialized yet');
    }
}

function vote(winner) {
    if (window.app && window.app.initialized) {
        window.app.vote(winner);
    } else {
        console.warn('App not initialized yet');
    }
}

function toggleTag(tagName) {
    const tagElement = event.target;
    tagElement.classList.toggle('selected');
}

function addCustomTag() {
    const input = document.getElementById('tag-input');
    const tagName = input.value.trim();
    
    if (tagName) {
        const container = document.getElementById('tag-suggestions');
        const newTag = document.createElement('span');
        newTag.className = 'tag';
        newTag.textContent = tagName;
        newTag.onclick = () => toggleTag(tagName);
        container.appendChild(newTag);
        input.value = '';
    }
}

function searchQuestions(query) {
    if (window.app && window.app.initialized) {
        console.log('Search:', query);
        window.app.loadAllQuestions();
    }
}

function hideIntegrityAlert() {
    const alert = document.getElementById('integrity-alert');
    if (alert) {
        alert.classList.add('hidden');
    }
}

function startCandidateComparison() {
    if (window.app && window.app.initialized) {
        window.app.startCandidateComparison();
    } else {
        console.warn('App not initialized yet');
    }
}

function showCandidateDetails(candidateId) {
    if (window.app && window.app.initialized) {
        window.app.showCandidateDetails(candidateId);
    } else {
        console.warn('App not initialized yet');
    }
}

// Global functions for JSON operations
async function exportData() {
    try {
        const data = await window.questionManager.exportToJSON();
        alert('Data exported successfully to JSON format');
    } catch (error) {
        console.error('Export failed:', error);
        alert('Export failed: ' + error.message);
    }
}

function importData() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        try {
            const text = await file.text();
            const count = await window.questionManager.importFromJSON(text);
            alert(`Import successful! Imported ${count} questions.`);
            window.app.loadAllQuestions(); // Update view
        } catch (error) {
            console.error('Import failed:', error);
            alert('Import failed: ' + error.message);
        }
    };
    
    input.click();
}

function showStats() {
    if (window.app && window.app.initialized) {
        window.app.showView('stats');
    } else {
        console.warn('App not initialized yet');
    }
}

// Start app when page is loaded
window.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM loaded, initializing app...');
    window.app = new VaalikoneApp();
    await window.app.initializeApp();
});
