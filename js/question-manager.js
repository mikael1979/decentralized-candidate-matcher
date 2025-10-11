class QuestionManager {
    constructor() {
        this.questions = new Map();
        this.nextId = 1;
        this.storageKey = 'vaalikone-questions';
        this.statsKey = 'vaalikone-stats';
        this.jsonFilePath = 'data/questions.json';
        
        this.runJSONTest().then(() => {
            this.loadFromStorage();
        });
    }

    async runJSONTest() {
        console.log('🧪 Aloitetaan JSON-tiedoston käsittelytesti...');
        
        try {
            await this.testJSONFileAccess();
            const stats = await this.updateAccessStats();
            console.log('✅ JSON-testi läpäisty:', stats);
        } catch (error) {
            console.warn('❌ JSON-testi epäonnistui, käytetään fallback-dataa:', error.message);
            await this.initializeFallbackData();
        }
    }

    async testJSONFileAccess() {
        return new Promise((resolve, reject) => {
            fetch(this.jsonFilePath)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('📁 JSON-tiedosto ladattu onnistuneesti:', data);
                    resolve(data);
                })
                .catch(error => {
                    console.warn('JSON-tiedostoa ei voitu ladata:', error.message);
                    console.log('🔄 Siirrytään suoraan fallback-dataan');
                    resolve(null);
                });
        });
    }

    async updateAccessStats() {
        let stats = {
            accessCount: 0,
            lastAccess: null,
            firstAccess: new Date().toISOString(),
            fileStatus: 'unknown'
        };

        try {
            const storedStats = localStorage.getItem(this.statsKey);
            if (storedStats) {
                stats = { ...stats, ...JSON.parse(storedStats) };
            }

            stats.accessCount++;
            stats.lastAccess = new Date().toISOString();
            stats.fileStatus = 'tested';

            localStorage.setItem(this.statsKey, JSON.stringify(stats));
            console.log(`📊 Tilastot päivitetty: Käyttökerrat ${stats.accessCount}`);
            
            return stats;
        } catch (error) {
            console.error('Tilastojen päivitys epäonnistui:', error);
            stats.fileStatus = 'error';
            return stats;
        }
    }

    async initializeFallbackData() {
        console.log('🔄 Alustetaan fallback-data...');
        
        const fallbackQuestions = [
            {
                id: 'q1',
                content: 'Pitäisikö perustulon olla kansalaispalkka?',
                category: 'sosiaalipolitiikka',
                tags: ['perustulo', 'talous'],
                rating: 1200,
                comparisons: 0,
                createdAt: new Date().toISOString(),
                status: 'active',
                source: 'fallback'
            },
            {
                id: 'q2',
                content: 'Tuleeko Suomen liittyä Natoon?',
                category: 'ulkopolitiikka', 
                tags: ['nato', 'turvallisuus'],
                rating: 1200,
                comparisons: 0,
                createdAt: new Date().toISOString(),
                status: 'active',
                source: 'fallback'
            },
            {
                id: 'q3',
                content: 'Pitäisikö ydinvoiman käyttöä lisätä?',
                category: 'ympäristö',
                tags: ['ydinvoima', 'energia'],
                rating: 1200,
                comparisons: 0,
                createdAt: new Date().toISOString(),
                status: 'active',
                source: 'fallback'
            }
        ];

        this.questions.clear();
        fallbackQuestions.forEach(q => {
            this.questions.set(q.id, q);
        });
        this.nextId = 4;

        await this.saveToStorage();

        const stats = await this.getStats();
        stats.fileStatus = 'fallback_used';
        localStorage.setItem(this.statsKey, JSON.stringify(stats));

        console.log('✅ Fallback-data alustettu:', this.questions.size, 'kysymystä');
    }

    async getStats() {
        try {
            const storedStats = localStorage.getItem(this.statsKey);
            return storedStats ? JSON.parse(storedStats) : {
                accessCount: 0,
                lastAccess: null,
                firstAccess: new Date().toISOString(),
                fileStatus: 'unknown'
            };
        } catch (error) {
            console.error('Tilastojen lukeminen epäonnistui:', error);
            return {
                accessCount: 0,
                lastAccess: null,
                firstAccess: new Date().toISOString(),
                fileStatus: 'error'
            };
        }
    }

    async exportToJSON() {
        console.log('💾 Viedään data JSON-tiedostoon...');
        
        try {
            const data = {
                metadata: {
                    exportedAt: new Date().toISOString(),
                    version: '1.0',
                    totalQuestions: this.questions.size,
                    source: 'vaalikone-web3'
                },
                questions: Array.from(this.questions.values()),
                stats: await this.getStats()
            };

            const jsonString = JSON.stringify(data, null, 2);
            localStorage.setItem('vaalikone-export', jsonString);
            this.createDownloadableJSON(jsonString);
            
            console.log('✅ Data viety JSON-muotoon onnistuneesti');
            return data;
        } catch (error) {
            console.error('JSON-vienti epäonnistui:', error);
            throw error;
        }
    }

    createDownloadableJSON(jsonString) {
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `vaalikone-data-${new Date().toISOString().split('T')[0]}.json`;
        a.textContent = 'Lataa JSON-tiedosto';
        a.style.display = 'block';
        a.style.margin = '10px 0';
        a.style.padding = '10px';
        a.style.background = '#3498db';
        a.style.color = 'white';
        a.style.textDecoration = 'none';
        a.style.borderRadius = '5px';
        a.style.textAlign = 'center';
        
        document.body.appendChild(a);
        this.updateAccessStats();
        console.log('📥 Ladattava JSON-tiedosto luotu:', a.download);
    }

    async importFromJSON(jsonData) {
        console.log('📤 Tuodaan data JSON-tiedostosta...');
        
        try {
            const data = typeof jsonData === 'string' ? JSON.parse(jsonData) : jsonData;
            
            if (!data.questions || !Array.isArray(data.questions)) {
                throw new Error('Virheellinen JSON-data: questions-kenttä puuttuu tai ei ole taulukko');
            }

            this.questions.clear();
            
            data.questions.forEach(q => {
                const question = {
                    id: q.id || `q${this.nextId++}`,
                    content: q.content || 'Nimetön kysymys',
                    category: q.category || 'yleinen',
                    tags: q.tags || [],
                    rating: q.rating || 1200,
                    comparisons: q.comparisons || 0,
                    createdAt: q.createdAt || new Date().toISOString(),
                    status: q.status || 'active',
                    source: 'json_import'
                };
                this.questions.set(question.id, question);
            });

            this.nextId = Math.max(...Array.from(this.questions.values()).map(q => 
                parseInt(q.id.replace('q', '')) || 0
            )) + 1;

            await this.saveToStorage();

            const stats = await this.getStats();
            stats.lastImport = new Date().toISOString();
            stats.importedQuestions = data.questions.length;
            localStorage.setItem(this.statsKey, JSON.stringify(stats));

            console.log('✅ JSON-data tuotu onnistuneesti:', this.questions.size, 'kysymystä');
            return this.questions.size;
        } catch (error) {
            console.error('JSON-tuonti epäonnistui:', error);
            throw error;
        }
    }

    async initialize() {
        console.log('🔄 Alustetaan QuestionManager...');
        
        if (this.questions.size === 0) {
            console.log('Ei dataa saatavilla, ladataan fallback-data...');
            await this.initializeFallbackData();
        } else {
            console.log('Data saatavilla:', this.questions.size, 'kysymystä');
        }

        const stats = await this.getStats();
        console.log('📈 Järjestelmän tilastot:', stats);
        return true;
    }

    // LISÄTYT METODIT LUOKAN SISÄLLE:
    getAllQuestions() {
        return Array.from(this.questions.values());
    }

    async getQuestion(id) {
        return this.questions.get(id);
    }

    async getComparisonPair() {
        const questions = this.getAllQuestions();
        if (questions.length < 2) {
            return null;
        }

        const randomIndex1 = Math.floor(Math.random() * questions.length);
        let randomIndex2 = Math.floor(Math.random() * questions.length);
        while (randomIndex2 === randomIndex1) {
            randomIndex2 = Math.floor(Math.random() * questions.length);
        }

        return {
            a: questions[randomIndex1],
            b: questions[randomIndex2]
        };
    }

    async createQuestion(content, category = 'yleinen', tags = []) {
        const question = {
            id: `q${this.nextId++}`,
            content,
            category,
            tags,
            rating: 1200,
            comparisons: 0,
            createdAt: new Date().toISOString(),
            status: 'active'
        };
        this.questions.set(question.id, question);
        await this.saveToStorage();
        return question;
    }

    async updateQuestion(questionId, updates) {
        const question = this.questions.get(questionId);
        if (question) {
            Object.assign(question, updates);
            await this.saveToStorage();
        }
        return question;
    }

    async incrementComparisons(questionId) {
        const question = this.questions.get(questionId);
        if (question) {
            question.comparisons = (question.comparisons || 0) + 1;
            await this.saveToStorage();
        }
    }

    loadFromStorage() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                const data = JSON.parse(stored);
                console.log('📂 Ladataan kysymykset localStoragesta:', data.questions?.length || 0);
                
                if (data.questions && Array.isArray(data.questions)) {
                    data.questions.forEach(q => {
                        this.questions.set(q.id, q);
                    });
                    this.nextId = data.nextId || this.nextId;
                }
            }
        } catch (e) {
            console.error('❌ Virhe ladattaessa localStoragesta:', e);
        }
    }

    async saveToStorage() {
        try {
            const data = {
                questions: Array.from(this.questions.values()),
                nextId: this.nextId,
                savedAt: new Date().toISOString()
            };
            localStorage.setItem(this.storageKey, JSON.stringify(data));
            console.log('💾 Kysymykset tallennettu localStorageen:', data.questions.length);
        } catch (e) {
            console.error('❌ Virhe tallennettaessa localStorageen:', e);
        }
    }
}

window.questionManager = new QuestionManager();
