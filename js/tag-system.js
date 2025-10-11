class TagSystem {
    constructor() {
        this.tags = new Map();
        this.questionTags = new Map();
        this.storageKey = 'vaalikone-tags';
        this.loadFromStorage();
    }

    async initialize() {
        // Lataa esimerkkitägit vain jos ei tallennettuja tägejä
        if (this.tags.size === 0) {
            this.createTag('perustulo', 'Perustuloon liittyvät kysymykset');
            this.createTag('nato', 'Natoon ja puolustukseen liittyvät kysymykset');
            this.createTag('ympäristö', 'Ympäristö- ja ilmastokysymykset');
            this.createTag('terveys', 'Terveydenhuoltoon liittyvät kysymykset');
            this.createTag('koulutus', 'Koulutukseen liittyvät kysymykset');
            await this.saveToStorage();
        }
        
        console.log('TagSystem initialized with', this.tags.size, 'tags');
    }

    loadFromStorage() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                const data = JSON.parse(stored);
                
                // Lataa tägit
                data.tags.forEach(tag => {
                    this.tags.set(tag.id, tag);
                });
                
                // Lataa kysymysten tägit
                data.questionTags.forEach(([questionId, tagIds]) => {
                    this.questionTags.set(questionId, new Set(tagIds));
                });
                
                console.log('Loaded tags from localStorage:', this.tags.size);
            }
        } catch (e) {
            console.error('Error loading tags from storage:', e);
        }
    }

    async saveToStorage() {
        try {
            const data = {
                tags: Array.from(this.tags.values()),
                questionTags: Array.from(this.questionTags.entries()).map(([questionId, tagSet]) => 
                    [questionId, Array.from(tagSet)]
                )
            };
            localStorage.setItem(this.storageKey, JSON.stringify(data));
        } catch (e) {
            console.error('Error saving tags to storage:', e);
        }
    }

    createTag(name, description = '') {
        const tagId = this.normalizeTagName(name);
        
        if (!this.tags.has(tagId)) {
            const tag = {
                id: tagId,
                name: name,
                description: description,
                usageCount: 0
            };
            this.tags.set(tagId, tag);
        }
        return this.tags.get(tagId);
    }

    async addTagToQuestion(questionId, tagName) {
        const tag = this.createTag(tagName);
        tag.usageCount++;

        if (!this.questionTags.has(questionId)) {
            this.questionTags.set(questionId, new Set());
        }
        
        this.questionTags.get(questionId).add(tag.id);
        await this.saveToStorage();
        return tag;
    }

    getQuestionTags(questionId) {
        if (!this.questionTags.has(questionId)) return [];
        const tagIds = this.questionTags.get(questionId);
        return Array.from(tagIds).map(id => this.tags.get(id)).filter(Boolean);
    }

    getPopularTags(limit = 10) {
        return Array.from(this.tags.values())
            .sort((a, b) => b.usageCount - a.usageCount)
            .slice(0, limit);
    }

    getAllTags() {
        return this.tags;
    }

    normalizeTagName(name) {
        return name.toLowerCase()
            .trim()
            .replace(/\s+/g, '-')
            .replace(/[^a-z0-9äöå\-]/g, '');
    }
}

window.tagSystem = new TagSystem();
