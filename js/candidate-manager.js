class CandidateManager {
    constructor() {
        this.candidates = new Map();
        this.answers = new Map(); // candidateId -> Map(questionId -> answer)
        this.justifications = new Map(); // candidateId -> Map(questionId -> justification)
        this.userAnswers = new Map(); // questionId -> userAnswer
        this.storageKey = 'electionmachine-candidates';
        this.loadFromStorage();
    }

    async initialize() {
        // Create sample candidates if none exist
        if (this.candidates.size === 0) {
            await this.createSampleCandidates();
            await this.generateSampleAnswers();
            await this.generateSampleJustifications();
            await this.saveToStorage();
        }
        console.log('CandidateManager initialized with', this.candidates.size, 'candidates');
    }

    async createSampleCandidates() {
        const sampleCandidates = [
            {
                id: 'c1',
                name: 'John Smith',
                party: 'SDP',
                description: 'Experienced citizen advocating for social justice',
                image: '👨‍💼',
                contact: 'john@example.com'
            },
            {
                id: 'c2', 
                name: 'Lisa Johnson',
                party: 'Coalition Party',
                description: 'New thinking for economic policy',
                image: '👩‍💼',
                contact: 'lisa@example.com'
            },
            {
                id: 'c3',
                name: 'Peter Green',
                party: 'Green Party',
                description: 'Nature and environment first',
                image: '👨‍🌾',
                contact: 'peter@example.com'
            }
        ];

        sampleCandidates.forEach(c => this.candidates.set(c.id, c));
    }

    async generateSampleAnswers() {
        // Wait for QuestionManager to initialize
        if (!window.questionManager || !window.questionManager.getAllQuestions) {
            console.warn('QuestionManager not yet initialized, waiting...');
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        const questions = await window.questionManager.getAllQuestions();
        console.log('Generating sample answers for', questions.length, 'questions');
        
        // Initialize answers with empty maps if they don't exist
        if (!this.answers.has('c1')) this.answers.set('c1', new Map());
        if (!this.answers.has('c2')) this.answers.set('c2', new Map());
        if (!this.answers.has('c3')) this.answers.set('c3', new Map());

        // Candidate 1: SDP preferences
        const c1Answers = this.answers.get('c1');
        questions.forEach((q, index) => {
            if (index === 0) c1Answers.set(q.id, 5); // Strongly agree with basic income
            else if (index === 1) c1Answers.set(q.id, 2); // Disagree with NATO membership
            else if (index === 2) c1Answers.set(q.id, 4); // Somewhat agree with nuclear power
            else c1Answers.set(q.id, Math.floor(Math.random() * 5) + 1); // Random
        });

        // Candidate 2: Coalition Party preferences  
        const c2Answers = this.answers.get('c2');
        questions.forEach((q, index) => {
            if (index === 0) c2Answers.set(q.id, 1); // Strongly disagree with basic income
            else if (index === 1) c2Answers.set(q.id, 5); // Strongly agree with NATO membership
            else if (index === 2) c2Answers.set(q.id, 5); // Strongly agree with nuclear power
            else c2Answers.set(q.id, Math.floor(Math.random() * 5) + 1); // Random
        });

        // Candidate 3: Green Party preferences
        const c3Answers = this.answers.get('c3');
        questions.forEach((q, index) => {
            if (index === 0) c3Answers.set(q.id, 4); // Somewhat agree with basic income
            else if (index === 1) c3Answers.set(q.id, 3); // Neutral on NATO membership
            else if (index === 2) c3Answers.set(q.id, 1); // Strongly disagree with nuclear power
            else c3Answers.set(q.id, Math.floor(Math.random() * 5) + 1); // Random
        });

        await this.saveToStorage();
    }

    async generateSampleJustifications() {
        const questions = await window.questionManager.getAllQuestions();
        
        // Candidate 1: SDP preferences
        const c1Justifications = new Map();
        c1Justifications.set(questions[0].id, 'Basic income provides a safety net for all citizens and reduces bureaucracy. It is a modern way to fight poverty.');
        c1Justifications.set(questions[1].id, 'Finland should focus on EU cooperation and international peacekeeping instead of NATO.');
        c1Justifications.set(questions[2].id, 'Renewable energy sources are the future, but nuclear power can be used during the transition phase.');
        this.justifications.set('c1', c1Justifications);

        // Candidate 2: Coalition Party preferences  
        const c2Justifications = new Map();
        c2Justifications.set(questions[0].id, 'Basic income weakens work incentives. A better solution is to reduce work taxation and invest in education.');
        c2Justifications.set(questions[1].id, 'NATO membership would strengthen Finland security and close cooperation with neighboring countries.');
        c2Justifications.set(questions[2].id, 'Nuclear power is a reliable and emission-free energy source that ensures competitive electricity prices.');
        this.justifications.set('c2', c2Justifications);

        // Candidate 3: Green Party preferences
        const c3Justifications = new Map();
        c3Justifications.set(questions[0].id, 'Basic income could be part of the solution, but we also need proper services and housing support.');
        c3Justifications.set(questions[1].id, 'Finland should focus on peacebuilding and environmental protection as global security challenges.');
        c3Justifications.set(questions[2].id, 'The future is in renewable energy sources. Nuclear power produces dangerous waste and is too expensive.');
        this.justifications.set('c3', c3Justifications);
    }

    setUserAnswer(questionId, answer) {
        this.userAnswers.set(questionId, answer);
        this.saveToStorage();
    }

    getUserAnswer(questionId) {
        return this.userAnswers.get(questionId);
    }

    getJustification(candidateId, questionId) {
        const candidateJustifications = this.justifications.get(candidateId);
        return candidateJustifications ? candidateJustifications.get(questionId) || '' : '';
    }

    setJustification(candidateId, questionId, justification) {
        if (!this.justifications.has(candidateId)) {
            this.justifications.set(candidateId, new Map());
        }
        this.justifications.get(candidateId).set(questionId, justification);
        this.saveToStorage();
    }

    calculateCompatibility(candidateId) {
        const candidateAnswers = this.answers.get(candidateId);
        if (!candidateAnswers) return 0;

        let totalDifference = 0;
        let answeredQuestions = 0;

        for (const [questionId, userAnswer] of this.userAnswers) {
            const candidateAnswer = candidateAnswers.get(questionId);
            if (candidateAnswer !== undefined) {
                const difference = Math.abs(userAnswer - candidateAnswer);
                totalDifference += difference;
                answeredQuestions++;
            }
        }

        if (answeredQuestions === 0) return 0;

        // Convert difference to percentage (0-100%)
        // Maximum difference 4 (on 1-5 scale) per question
        const maxDifference = answeredQuestions * 4;
        const compatibility = 100 - (totalDifference / maxDifference * 100);
        
        return Math.round(compatibility * 10) / 10; // Round to 1 decimal
    }

    getAllCandidates() {
        return Array.from(this.candidates.values());
    }

    getCandidateAnswers(candidateId) {
        return this.answers.get(candidateId) || new Map();
    }

    loadFromStorage() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                const data = JSON.parse(stored);
                
                // Load candidates
                data.candidates.forEach(c => {
                    this.candidates.set(c.id, c);
                });
                
                // Load answers
                data.answers.forEach(([candidateId, answers]) => {
                    this.answers.set(candidateId, new Map(answers));
                });
                
                // Load justifications
                if (data.justifications) {
                    data.justifications.forEach(([candidateId, justifications]) => {
                        this.justifications.set(candidateId, new Map(justifications));
                    });
                }
                
                // Load user answers
                if (data.userAnswers) {
                    this.userAnswers = new Map(data.userAnswers);
                }
                
                console.log('Loaded candidates from storage:', this.candidates.size);
            }
        } catch (e) {
            console.error('Error loading candidates:', e);
        }
    }

    async saveToStorage() {
        try {
            const data = {
                candidates: Array.from(this.candidates.values()),
                answers: Array.from(this.answers.entries()).map(([candidateId, answerMap]) => 
                    [candidateId, Array.from(answerMap.entries())]
                ),
                justifications: Array.from(this.justifications.entries()).map(([candidateId, justificationMap]) => 
                    [candidateId, Array.from(justificationMap.entries())]
                ),
                userAnswers: Array.from(this.userAnswers.entries())
            };
            localStorage.setItem(this.storageKey, JSON.stringify(data));
        } catch (e) {
            console.error('Error saving candidates:', e);
        }
    }
}

window.candidateManager = new CandidateManager();
