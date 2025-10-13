# JSON Data Structures for Decentralized Candidate Matcher

This directory contains example JSON structures for the decentralized system.

## File Structure

- `meta.json` - System configuration and metadata
- `questions.json` - Official election questions  
- `newquestions.json` - User-submitted questions awaiting moderation
- `candidates.json` - Candidate information and answer references
- `community_votes.json` - Community moderation votes
- `answer_template.json` - Template for candidate answers
- `integrity_example.json` - Example of integrity hash verification

## Key Concepts

### Integrity Hashes
Every JSON file includes an `integrity` field with SHA256 hash to prevent tampering.

### IPFS CID References
Candidate answers are stored as IPFS Content Identifiers (CIDs) for decentralization.

### Community Moderation
User questions are moderated through community voting with auto-approval/blocking thresholds.
