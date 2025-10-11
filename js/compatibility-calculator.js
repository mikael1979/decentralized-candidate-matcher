class CompatibilityCalculator {
    constructor() {
        this.scaleDescriptions = {
            1: 'Täysin eri mieltä',
            2: 'Jokseenkin eri mieltä', 
            3: 'Ei samaa eikä eri mieltä',
            4: 'Jokseenkin samaa mieltä',
            5: 'Täysin samaa mieltä'
        };
    }

    getScaleDescription(value) {
        return this.scaleDescriptions[value] || 'Ei vastausta';
    }

    calculateDetailedCompatibility(candidateId) {
        const candidateAnswers = window.candidateManager.getCandidateAnswers(candidateId);
        const userAnswers = window.candidateManager.userAnswers;
        
        let exactMatches = 0;
        let closeMatches = 0;
        let disagreements = 0;
        let totalCompared = 0;

        for (const [questionId, userAnswer] of userAnswers) {
            const candidateAnswer = candidateAnswers.get(questionId);
            if (candidateAnswer !== undefined) {
                const difference = Math.abs(userAnswer - candidateAnswer);
                
                if (difference === 0) exactMatches++;
                else if (difference <= 1) closeMatches++;
                else disagreements++;
                
                totalCompared++;
            }
        }

        const compatibility = window.candidateManager.calculateCompatibility(candidateId);

        return {
            compatibility,
            exactMatches,
            closeMatches, 
            disagreements,
            totalCompared,
            breakdown: this.getCompatibilityBreakdown(exactMatches, closeMatches, disagreements, totalCompared)
        };
    }

    getCompatibilityBreakdown(exact, close, disagree, total) {
        if (total === 0) return { exact: 0, close: 0, disagree: 0 };
        
        return {
            exact: Math.round((exact / total) * 100),
            close: Math.round((close / total) * 100),
            disagree: Math.round((disagree / total) * 100)
        };
    }

    getTopCompatibleCandidates(limit = 3) {
        const candidates = window.candidateManager.getAllCandidates();
        const results = candidates.map(candidate => ({
            candidate,
            compatibility: window.candidateManager.calculateCompatibility(candidate.id),
            details: this.calculateDetailedCompatibility(candidate.id)
        }));

        return results
            .filter(result => result.details.totalCompared > 0) // Vain vertailtu
            .sort((a, b) => b.compatibility - a.compatibility)
            .slice(0, limit);
    }
}

window.compatibilityCalculator = new CompatibilityCalculator();
