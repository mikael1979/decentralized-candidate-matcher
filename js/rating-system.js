class RatingSystem {
    constructor() {
        this.kFactor = 32;
    }

    async processVote(winnerId, loserId) {
        console.log('Processing vote:', winnerId, 'vs', loserId);
        
        const winner = await window.questionManager.getQuestion(winnerId);
        const loser = await window.questionManager.getQuestion(loserId);
        
        if (!winner || !loser) {
            console.error('Could not find questions:', winnerId, loserId);
            return;
        }
        
        console.log('Before - Winner:', winner.rating, 'Loser:', loser.rating);
        
        const expectedWinner = 1 / (1 + Math.pow(10, (loser.rating - winner.rating) / 400));
        const expectedLoser = 1 - expectedWinner;
        
        const newWinnerRating = Math.round(winner.rating + this.kFactor * (1 - expectedWinner));
        const newLoserRating = Math.round(loser.rating + this.kFactor * (0 - expectedLoser));
        
        console.log('After - Winner:', newWinnerRating, 'Loser:', newLoserRating);
        
        // Päivitä ratingit
        await window.questionManager.updateQuestion(winnerId, { 
            rating: newWinnerRating 
        });
        await window.questionManager.updateQuestion(loserId, { 
            rating: newLoserRating 
        });
        
        // Päivitä vertailumäärät
        await window.questionManager.incrementComparisons(winnerId);
        await window.questionManager.incrementComparisons(loserId);
        
        console.log(`Rating updated: ${winnerId} -> ${newWinnerRating}, ${loserId} -> ${newLoserRating}`);
        
        return { winner: newWinnerRating, loser: newLoserRating };
    }
}

window.ratingSystem = new RatingSystem();
