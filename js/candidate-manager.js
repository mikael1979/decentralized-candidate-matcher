class CandidateManager {
    constructor() {
        this.candidates = new Map();
        this.answers = new Map(); // candidateId -> Map(questionId -> answer)
        this.justifications = new Map(); // candidateId -> Map(questionId -> justification)
        this.userAnswers = new Map(); // questionId -> userAnswer
        this.storageKey = 'vaalikone-candidates';
        this.loadFromStorage();
    }

    async initialize() {
        // Luo esimerkkehdokkaat jos ei ole olemassa
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
                name: 'Matti Meikäläinen',
                party: 'SDP',
                description: 'Kokenut kansalainen, joka ajaa sosiaalista oikeudenmukaisuutta',
                image: '👨‍💼',
                contact: 'matti@example.com'
            },
            {
                id: 'c2', 
                name: 'Liisa Laatikainen',
                party: 'Kokoomus',
                description: 'Uusi ajattelu talouspolitiikkaan',
                image: '👩‍💼',
                contact: 'liisa@example.com'
            },
            {
                id: 'c3',
                name: 'Pekka Puupää',
                party: 'Vihreät',
                description: 'Luonto ja ympäristö etusijalla',
                image: '👨‍🌾',
                contact: 'pekka@example.com'
            }
        ];

        sampleCandidates.forEach(c => this.candidates.set(c.id, c));
    }

    async generateSampleAnswers() {
        // Odota että QuestionManager on alustettu
        if (!window.questionManager || !window.questionManager.getAllQuestions) {
            console.warn('QuestionManager ei ole vielä alustettu, odota...');
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        const questions = await window.questionManager.getAllQuestions();
        console.log('Generating sample answers for', questions.length, 'questions');
        
        // Alusta vastaukset tyhjillä mapeilla jos ei ole olemassa
        if (!this.answers.has('c1')) this.answers.set('c1', new Map());
        if (!this.answers.has('c2')) this.answers.set('c2', new Map());
        if (!this.answers.has('c3')) this.answers.set('c3', new Map());

        // Ehdokas 1: SDP-mieltymykset
        const c1Answers = this.answers.get('c1');
        questions.forEach((q, index) => {
            if (index === 0) c1Answers.set(q.id, 5); // Täysin samaa mieltä perustulosta
            else if (index === 1) c1Answers.set(q.id, 2); // Eri mieltä NATO-jäsenyydestä
            else if (index === 2) c1Answers.set(q.id, 4); // Melko samaa mieltä ydinvoimasta
            else c1Answers.set(q.id, Math.floor(Math.random() * 5) + 1); // Satunnainen
        });

        // Ehdokas 2: Kokoomus-mieltymykset  
        const c2Answers = this.answers.get('c2');
        questions.forEach((q, index) => {
            if (index === 0) c2Answers.set(q.id, 1); // Täysin eri mieltä perustulosta
            else if (index === 1) c2Answers.set(q.id, 5); // Täysin samaa mieltä NATO-jäsenyydestä
            else if (index === 2) c2Answers.set(q.id, 5); // Täysin samaa mieltä ydinvoimasta
            else c2Answers.set(q.id, Math.floor(Math.random() * 5) + 1); // Satunnainen
        });

        // Ehdokas 3: Vihreät-mieltymykset
        const c3Answers = this.answers.get('c3');
        questions.forEach((q, index) => {
            if (index === 0) c3Answers.set(q.id, 4); // Melko samaa mieltä perustulosta
            else if (index === 1) c3Answers.set(q.id, 3); // Neutraali NATO-jäsenyydestä
            else if (index === 2) c3Answers.set(q.id, 1); // Täysin eri mieltä ydinvoimasta
            else c3Answers.set(q.id, Math.floor(Math.random() * 5) + 1); // Satunnainen
        });

        await this.saveToStorage();
    }

    async generateSampleJustifications() {
        const questions = await window.questionManager.getAllQuestions();
        
        // Ehdokas 1: SDP-mieltymykset
        const c1Justifications = new Map();
        c1Justifications.set(questions[0].id, 'Perustulo takaa kaikille kansalaisille turvaverkon ja vähentää byrokratiaa. Se on moderni tapa taistella köyhyyttä vastaan.');
        c1Justifications.set(questions[1].id, 'Suomen pitäisi keskittyä EU-yhteistyöhön ja maidenväliseen rauhanturvaamiseen Naton sijaan.');
        c1Justifications.set(questions[2].id, 'Uusiutuvat energialähteet ovat tulevaisuus, mutta ydinvoimaa voidaan käyttää siirtymävaiheessa.');
        this.justifications.set('c1', c1Justifications);

        // Ehdokas 2: Kokoomus-mieltymykset  
        const c2Justifications = new Map();
        c2Justifications.set(questions[0].id, 'Perustulo heikentää kannustimia työntekoon. Parempi ratkaisu on keventää työn verotusta ja investoida koulutukseen.');
        c2Justifications.set(questions[1].id, 'Nato-jäsenyys vahvistaisi Suomen turvallisuutta ja läheistä yhteistyötä lähimaidemme kanssa.');
        c2Justifications.set(questions[2].id, 'Ydinvoima on luotettava ja päästötön energianlähde, joka takaa kilpailukykyisen sähkönhinnan.');
        this.justifications.set('c2', c2Justifications);

        // Ehdokas 3: Vihreät-mieltymykset
        const c3Justifications = new Map();
        c3Justifications.set(questions[0].id, 'Perustulo voi olla osa ratkaisua, mutta tarvitaan myös kunnollisia palveluja ja asumisen tukea.');
        c3Justifications.set(questions[1].id, 'Suomen tulisi keskittyä rauhanrakentamiseen ja ympäristönsuojeluun globaaleina turvallisuushaasteina.');
        c3Justifications.set(questions[2].id, 'Tulevaisuus on uusiutuvissa energialähteissä. Ydinvoima tuottaa vaarallista jätettä ja on liian kallista.');
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

        // Muunna ero prosentteiksi (0-100%)
        // Maksimiero 4 (1-5 asteikolla) per kysymys
        const maxDifference = answeredQuestions * 4;
        const compatibility = 100 - (totalDifference / maxDifference * 100);
        
        return Math.round(compatibility * 10) / 10; // Pyöristä 1 desimaaliin
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
                
                // Lataa ehdokkaat
                data.candidates.forEach(c => {
                    this.candidates.set(c.id, c);
                });
                
                // Lataa vastaukset
                data.answers.forEach(([candidateId, answers]) => {
                    this.answers.set(candidateId, new Map(answers));
                });
                
                // Lataa perustelut
                if (data.justifications) {
                    data.justifications.forEach(([candidateId, justifications]) => {
                        this.justifications.set(candidateId, new Map(justifications));
                    });
                }
                
                // Lataa käyttäjän vastaukset
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
