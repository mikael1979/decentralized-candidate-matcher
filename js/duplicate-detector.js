class DuplicateDetector {
    constructor() {
        this.similarityThreshold = 0.7;
    }

    normalizeText(text) {
        return text
            .toLowerCase()
            .replace(/[^\w\säöå]/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
    }

    tokenize(text) {
        return text.split(' ').filter(word => word.length > 2);
    }

    calculateSimilarity(text1, text2) {
        const tokens1 = new Set(this.tokenize(this.normalizeText(text1)));
        const tokens2 = new Set(this.tokenize(this.normalizeText(text2)));
        
        const intersection = new Set([...tokens1].filter(x => tokens2.has(x)));
        const union = new Set([...tokens1, ...tokens2]);
        
        return intersection.size / union.size;
    }

    async findDuplicates(newQuestion, existingQuestions) {
        const duplicates = [];
        
        for (const existing of existingQuestions) {
            const similarity = this.calculateSimilarity(newQuestion, existing.content);
            
            if (similarity >= this.similarityThreshold) {
                duplicates.push({
                    question: existing,
                    similarity: similarity
                });
            }
        }
        
        return duplicates.sort((a, b) => b.similarity - a.similarity);
    }
}

// TÄRKEÄ: Tee globaaliksi
window.duplicateDetector = new DuplicateDetector();
