class QuestionManager {
    constructor() {
        this.questions = new Map();
        this.nextId = 1;
        this.storageKey = 'electionmachine-questions';
        this.statsKey = 'electionmachine-stats';
        this.jsonFilePath = 'data/questions.json';
        
        this.runJSONTest().then(() => {
            this.loadFromStorage();
        });
    }

    async runJSONTest() {
        console.log('🧪 Starting JSON file processing test...');
        
        try {
            await this.testJSONFileAccess();
            const stats = await this.updateAccessStats();
            console.log('✅ JSON test passed:', stats);
        } catch (error) {
            console.warn('❌ JSON test failed, using fallback data:', error.message);
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
                    console.log('📁 JSON file loaded successfully:', data);
                    resolve(data);
                })
                .catch(error => {
                    console.warn('JSON file could not be loaded:', error.message);
                    console.log('🔄 Switching directly to fallback data');
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
            console.log(`📊 Statistics updated: Access count ${stats.accessCount}`);
            
            return stats;
        } catch (error) {
            console.error('Statistics update failed:', error);
            stats.fileStatus = 'error';
            return stats;
        }
    }

    async initializeFallbackData() {
        console.log('🔄 Initializing fallback data...');
        
        const fallbackQuestions = [
            {
                id: 'q1',
                content: 'Should basic income be a citizen salary?',
                category: 'socialpolicy',
                tags: ['basicincome', 'economy'],
                rating: 1200,
                comparisons: 0,
                createdAt: new Date().toISOString(),
                status: 'active',
                source: 'fallback'
            },
            {
                id: 'q2',
                content: 'Should Finland join NATO?',
                category: 'foreignpolicy', 
                tags: ['nato', 'security'],
                rating: 1200,
                comparisons: 0,
                createdAt: new Date().toISOString(),
                status: 'active',
                source: 'fallback'
            },
            {
                id: 'q3',
                content: 'Should nuclear power usage be increased?',
                category: 'environment',
                tags: ['nuclearpower', 'energy'],
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

        console.log('✅ Fallback data initialized:', this.questions.size, 'questions');
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
            console.error('Reading statistics failed:', error);
            return {
                accessCount: 0,
                lastAccess: null,
                firstAccess: new Date().toISOString(),
                fileStatus: 'error'
            };
        }
    }

    async exportToJSON() {
        console.log('💾 Exporting data to JSON file...');
        
        try {
            const data = {
                metadata: {
                    exportedAt: new Date().toISOString(),
                    version: '1.0',
                    totalQuestions: this.questions.size,
                    source: 'electionmachine-web3'
                },
                questions: Array.from(this.questions.values()),
                stats: await this.getStats()
            };

            const jsonString = JSON.stringify(data, null, 2);
            localStorage.setItem('electionmachine-export', jsonString);
            this.createDownloadableJSON(jsonString);
            
            console.log('✅ Data exported to JSON format successfully');
            return data;
        } catch (error) {
            console.error('JSON export failed:', error);
            throw error;
        }
    }

    createDownloadableJSON(jsonString) {
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `electionmachine-data-${new Date().toISOString().split('T')[0]}.json`;
        a.textContent = 'Download JSON file';
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
        console.log('📥 Downloadable JSON file created:', a.download);
    }

    async importFromJSON(jsonData) {
        console.log('📤 Importing data from JSON file...');
        
        try {
            const data = typeof jsonData === 'string' ? JSON.parse(jsonData) : jsonData;
            
            if (!data.questions || !Array.isArray(data.questions)) {
                throw new Error('Invalid JSON data: questions field missing or not an array');
            }

            this.questions.clear();
            
            data.questions.forEach(q => {
                const question = {
                    id: q.id || `q${this.nextId++}`,
                    content: q.content || 'Untitled question',
                    category: q.category || 'general',
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

            console.log('✅ JSON data imported successfully:', this.questions.size, 'questions');
            return this.questions.size;
        } catch (error) {
            console.error('JSON import failed:', error);
            throw error;
        }
    }

    async initialize() {
        console.log('🔄 Initializing QuestionManager...');
        
        if (this.questions.size === 0) {
            console.log('No data available, loading fallback data...');
            await this.initializeFallbackData();
        } else {
            console.log('Data available:', this.questions.size, 'questions');
        }

        const stats = await this.getStats();
        console.log('📈 System statistics:', stats);
        return true;
    }

    // ADDED METHODS INSIDE THE CLASS:
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

    async createQuestion(content, category = 'general', tags = []) {
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
                console.log('📂 Loading questions from localStorage:', data.questions?.length || 0);
                
                if (data.questions && Array.isArray(data.questions)) {
                    data.questions.forEach(q => {
                        this.questions.set(q.id, q);
                    });
                    this.nextId = data.nextId || this.nextId;
                }
            }
        } catch (e) {
            console.error('❌ Error loading from localStorage:', e);
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
            console.log('💾 Questions saved to localStorage:', data.questions.length);
        } catch (e) {
            console.error('❌ Error saving to localStorage:', e);
        }
    }
}

window.questionManager = new QuestionManager();
