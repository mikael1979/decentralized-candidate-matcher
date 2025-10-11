class TagSystem {
    constructor() {
        this.tags = new Map();
        this.questionTags = new Map();
        this.storageKey = 'electionmachine-tags';
        this.loadFromStorage();
    }

    async initialize() {
        // Load sample tags only if no saved tags exist
        if (this.tags.size === 0) {
            this.createTag('basicincome', 'Questions related to basic income');
            this.createTag('nato', 'Questions about NATO and defense');
            this.createTag('environment', 'Environmental and climate questions');
            this.createTag('healthcare', 'Questions related to healthcare');
            this.createTag('education', 'Questions related to education');
            await this.saveToStorage();
        }
        
        console.log('TagSystem initialized with', this.tags.size, 'tags');
    }

    loadFromStorage() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                const data = JSON.parse(stored);
                
                // Load tags
                data.tags.forEach(tag => {
                    this.tags.set(tag.id, tag);
                });
                
                // Load question tags
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
            .replace(/[^a-z0-9\-]/g, '');
    }
}

window.tagSystem = new TagSystem();
