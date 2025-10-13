const fs = require('fs');
const crypto = require('crypto');
const path = require('path');

class EnhancedJSONEditor {
    constructor(dataDir = './test-data') {
        this.dataDir = dataDir;
        this.ensureDataDirectory();
        this.loadedFiles = new Map();
    }

    ensureDataDirectory() {
        if (!fs.existsSync(this.dataDir)) {
            fs.mkdirSync(this.dataDir, { recursive: true });
            console.log(`📁 Created data directory: ${this.dataDir}`);
        }
    }

    // Enhanced file operations with backup
    readJSON(filename) {
        try {
            const filepath = path.join(this.dataDir, filename);
            if (!fs.existsSync(filepath)) {
                console.log(`⚠️  File ${filename} not found, creating default`);
                return this.createDefaultFile(filename);
            }

            const data = fs.readFileSync(filepath, 'utf8');
            const parsed = JSON.parse(data);
            this.loadedFiles.set(filename, parsed);
            return parsed;
        } catch (error) {
            console.error(`❌ Error reading ${filename}:`, error.message);
            return null;
        }
    }

    writeJSON(filename, data, createBackup = true) {
        try {
            const filepath = path.join(this.dataDir, filename);
            
            // Create backup before writing
            if (createBackup && fs.existsSync(filepath)) {
                const backupPath = `${filepath}.backup-${Date.now()}`;
                fs.copyFileSync(filepath, backupPath);
            }

            const jsonString = JSON.stringify(data, null, 2);
            fs.writeFileSync(filepath, jsonString, 'utf8');
            this.loadedFiles.set(filename, data);
            
            // Verify write was successful
            const verifyData = this.readJSON(filename);
            const isValid = this.calculateHash(data) === this.calculateHash(verifyData);
            
            if (isValid) {
                console.log(`✓ Successfully wrote ${filename}`);
                return true;
            } else {
                console.error(`❌ Write verification failed for ${filename}`);
                return false;
            }
        } catch (error) {
            console.error(`❌ Error writing ${filename}:`, error.message);
            return false;
        }
    }

    createDefaultFile(filename) {
        const defaults = {
            'meta.json': {
                system: "Decentralized Candidate Matcher",
                version: "1.0.0",
                election: {
                    id: "test_election_2024",
                    country: "FI",
                    type: "test",
                    name: { fi: "Test Vaalit 2024", en: "Test Election 2024" },
                    date: "2024-01-01",
                    language: "fi"
                },
                content: {}
            },
            'questions.json': {
                election_id: "test_election_2024",
                language: "fi",
                questions: []
            },
            'newquestions.json': {
                election_id: "test_election_2024", 
                language: "fi",
                question_type: "user_submitted",
                questions: []
            },
            'candidates.json': {
                election_id: "test_election_2024",
                language: "fi",
                candidates: []
            },
            'community_votes.json': {
                election_id: "test_election_2024",
                language: "fi",
                question_votes: [],
                user_votes: []
            }
        };

        const defaultData = defaults[filename] || {};
        this.writeJSON(filename, this.updateIntegrity(defaultData), false);
        return defaultData;
    }

    calculateHash(data) {
        const dataCopy = JSON.parse(JSON.stringify(data));
        delete dataCopy.integrity;
        
        const jsonString = JSON.stringify(dataCopy, null, 0);
        const hash = crypto.createHash('sha256').update(jsonString).digest('hex');
        return `sha256:${hash}`;
    }

    updateIntegrity(data) {
        const hash = this.calculateHash(data);
        return {
            ...data,
            integrity: {
                algorithm: 'sha256',
                hash: hash,
                computed: new Date().toISOString()
            }
        };
    }

    validateDataConsistency() {
        console.log('\n🔍 Validating data consistency...');
        const errors = [];

        // Check that all files have the same election_id
        const electionIds = new Set();
        for (const [filename, data] of this.loadedFiles) {
            if (data.election_id) {
                electionIds.add(data.election_id);
            }
        }

        if (electionIds.size > 1) {
            errors.push(`Multiple election IDs found: ${Array.from(electionIds).join(', ')}`);
        }

        // Validate integrity hashes
        for (const [filename, data] of this.loadedFiles) {
            if (data.integrity) {
                const computedHash = this.calculateHash(data);
                if (computedHash !== data.integrity.hash) {
                    errors.push(`Integrity hash mismatch in ${filename}`);
                }
            }
        }

        if (errors.length === 0) {
            console.log('✓ All data consistency checks passed');
            return true;
        } else {
            console.log('❌ Data consistency errors:');
            errors.forEach(error => console.log(`  - ${error}`));
            return false;
        }
    }

    // Enhanced question management
    addUserQuestion(questionData) {
        const questions = this.loadedFiles.get('newquestions.json');
        if (!questions) {
            console.error('❌ newquestions.json not loaded');
            return null;
        }

        // Validate required fields
        const required = ['category', 'question', 'scale'];
        const missing = required.filter(field => !questionData[field]);
        if (missing.length > 0) {
            console.error(`❌ Missing required fields: ${missing.join(', ')}`);
            return null;
        }

        const newQuestion = {
            id: `user_${Date.now()}`,
            original_id: questions.questions.length + 1001,
            ...questionData,
            submission: {
                user_public_key: questionData.user_public_key || "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIuser_" + Date.now(),
                timestamp: new Date().toISOString(),
                status: "pending",
                upvotes: 0,
                downvotes: 0,
                user_comment: questionData.user_comment || ""
            },
            moderation: {
                moderated: false,
                approved: null,
                blocked: false
            },
            community_moderation: {
                status: "pending",
                votes_received: 0,
                inappropriate_ratio: 0,
                confidence_score: 0,
                community_approved: false,
                auto_moderated: false,
                requires_admin_review: false
            },
            elo_rating: {
                rating: 1500,
                total_matches: 0,
                wins: 0,
                losses: 0,
                last_updated: new Date().toISOString()
            }
        };

        questions.questions.push(newQuestion);
        console.log(`✓ Added question: ${newQuestion.question.fi.substring(0, 50)}...`);
        return newQuestion;
    }

    // Batch operations
    addMultipleQuestions(questionsData) {
        console.log(`\n📝 Adding ${questionsData.length} questions...`);
        const results = [];
        
        for (const qData of questionsData) {
            try {
                const result = this.addUserQuestion(qData);
                results.push({ success: true, question: result });
            } catch (error) {
                results.push({ success: false, error: error.message });
            }
        }

        const successCount = results.filter(r => r.success).length;
        console.log(`✓ Successfully added ${successCount}/${questionsData.length} questions`);
        return results;
    }

    // Search and filter functionality
    searchQuestions(query, field = 'question') {
        const allQuestions = [
            ...(this.loadedFiles.get('questions.json')?.questions || []),
            ...(this.loadedFiles.get('newquestions.json')?.questions || [])
        ];

        return allQuestions.filter(question => {
            const value = question[field];
            if (typeof value === 'object') {
                return Object.values(value).some(text => 
                    text.toLowerCase().includes(query.toLowerCase())
                );
            }
            return value?.toLowerCase().includes(query.toLowerCase());
        });
    }

    getQuestionsByStatus(status) {
        const userQuestions = this.loadedFiles.get('newquestions.json')?.questions || [];
        return userQuestions.filter(q => q.community_moderation?.status === status);
    }

    // Statistics and analytics
    generateReport() {
        const questions = this.loadedFiles.get('questions.json')?.questions || [];
        const userQuestions = this.loadedFiles.get('newquestions.json')?.questions || [];
        const votes = this.loadedFiles.get('community_votes.json')?.user_votes || [];
        const candidates = this.loadedFiles.get('candidates.json')?.candidates || [];

        const statusCounts = {};
        userQuestions.forEach(q => {
            const status = q.community_moderation?.status || 'unknown';
            statusCounts[status] = (statusCounts[status] || 0) + 1;
        });

        const voteDistribution = {};
        votes.forEach(vote => {
            voteDistribution[vote.vote] = (voteDistribution[vote.vote] || 0) + 1;
        });

        return {
            timestamp: new Date().toISOString(),
            summary: {
                total_official_questions: questions.length,
                total_user_questions: userQuestions.length,
                total_candidates: candidates.length,
                total_votes: votes.length
            },
            user_questions_by_status: statusCounts,
            vote_distribution: voteDistribution,
            average_elo: this.calculateAverageElo([...questions, ...userQuestions]),
            top_questions: this.getTopRatedQuestions(5)
        };
    }

    calculateAverageElo(questions) {
        const ratedQuestions = questions.filter(q => q.elo_rating?.rating);
        if (ratedQuestions.length === 0) return 0;
        
        const total = ratedQuestions.reduce((sum, q) => sum + q.elo_rating.rating, 0);
        return Math.round(total / ratedQuestions.length);
    }

    getTopRatedQuestions(limit = 10) {
        const allQuestions = [
            ...(this.loadedFiles.get('questions.json')?.questions || []),
            ...(this.loadedFiles.get('newquestions.json')?.questions || [])
        ];

        return allQuestions
            .filter(q => q.elo_rating?.rating && q.elo_rating.total_matches > 0)
            .sort((a, b) => b.elo_rating.rating - a.elo_rating.rating)
            .slice(0, limit)
            .map(q => ({
                id: q.id,
                question: q.question.fi,
                rating: q.elo_rating.rating,
                matches: q.elo_rating.total_matches,
                win_rate: q.elo_rating.wins / q.elo_rating.total_matches
            }));
    }

    // Load all data with validation
    loadAllData() {
        console.log('📁 Loading all JSON files...');
        
        const files = ['meta.json', 'questions.json', 'newquestions.json', 'candidates.json', 'community_votes.json'];
        const results = files.map(file => ({
            file,
            data: this.readJSON(file),
            success: this.loadedFiles.has(file)
        }));

        const successCount = results.filter(r => r.success).length;
        console.log(`✓ Loaded ${successCount}/${files.length} files successfully`);

        results.forEach(result => {
            if (!result.success) {
                console.log(`⚠️  Failed to load: ${result.file}`);
            }
        });

        return successCount === files.length;
    }

    // Save all data with validation
    saveAllData() {
        console.log('\n💾 Saving all JSON files...');
        
        const results = Array.from(this.loadedFiles.entries()).map(([filename, data]) => {
            const updatedData = this.updateIntegrity(data);
            return this.writeJSON(filename, updatedData);
        });

        const successCount = results.filter(Boolean).length;
        console.log(`✓ Saved ${successCount}/${results.length} files successfully`);
        
        return successCount === results.length;
    }
}

// Demo with enhanced features
async function runEnhancedDemo() {
    console.log('🚀 Enhanced Decentralized Candidate Matcher Demo\n');
    
    const editor = new EnhancedJSONEditor();
    
    // Load data
    if (!editor.loadAllData()) {
        console.log('⚠️  Some files failed to load, but continuing with demo...');
    }

    // Validate consistency
    editor.validateDataConsistency();

    // Demo: Add multiple questions at once
    const sampleQuestions = [
        {
            category: { fi: "Terveys", en: "Health" },
            question: { 
                fi: "Pitäisikö terveyskeskusten aukioloaikoja pidentää iltaan saakka?",
                en: "Should health center opening hours be extended until the evening?"
            },
            scale: {
                min: -5, max: 5,
                labels: { fi: { "-5": "Täysin eri mieltä", "0": "Neutraali", "5": "Täysin samaa mieltä" } }
            },
            tags: { fi: ["terveys", "terveyskeskukset", "aukioloajat"] },
            user_comment: "Pitäisi olla palvelut saatavilla myös työaikojen jälkeen"
        },
        {
            category: { fi: "Kulttuuri", en: "Culture" },
            question: { 
                fi: "Pitäisikö kaupungin tukea enemmän paikallista musiikkielämää?",
                en: "Should the city support local music scene more?"
            },
            scale: {
                min: -5, max: 5,
                labels: { fi: { "-5": "Täysin eri mieltä", "0": "Neutraali", "5": "Täysin samaa mieltä" } }
            },
            tags: { fi: ["kulttuuri", "musiikki", "taide"] },
            user_comment: "Paikallisille muusikoille tarvitaan enemmän esiintymismahdollisuuksia"
        }
    ];

    editor.addMultipleQuestions(sampleQuestions);

    // Demo: Search functionality
    console.log('\n🔍 Searching for questions about "terveys"...');
    const healthQuestions = editor.searchQuestions('terveys');
    console.log(`Found ${healthQuestions.length} questions:`);
    healthQuestions.forEach(q => {
        console.log(`  - ${q.question.fi} (${q.community_moderation?.status || 'pending'})`);
    });

    // Demo: Generate report
    console.log('\n📈 Generating system report...');
    const report = editor.generateReport();
    console.log('System Report:');
    console.log(`- Total questions: ${report.summary.total_official_questions + report.summary.total_user_questions}`);
    console.log(`- Total votes: ${report.summary.total_votes}`);
    console.log(`- Question statuses:`, report.user_questions_by_status);
    console.log(`- Average Elo rating: ${report.average_elo}`);

    // Save everything
    if (editor.saveAllData()) {
        console.log('\n🎉 Enhanced demo completed successfully!');
        
        // Final validation
        console.log('\n🔍 Final data validation...');
        editor.validateDataConsistency();
    } else {
        console.log('\n❌ Some files failed to save');
    }
}

// Run the enhanced demo
runEnhancedDemo().catch(console.error);
