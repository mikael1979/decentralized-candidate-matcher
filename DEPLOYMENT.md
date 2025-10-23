# Deployment Guide - Decentralized Candidate Matcher

## 🚀 Quick Deployment Options

### 1. Local Development

#### Basic Flask Development Server
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python web_app.py

# Access at: http://localhost:5000

# Development with Mock IPFS (default)
python web_app.py

# Development with Real IPFS
python web_app.py --real-ipfs

# Debug mode with verbose logging
DEBUG=True python web_app.py

# For real IPFS deployment
export IPFS_HOST=127.0.0.1
export IPFS_PORT=5001

# Start IPFS daemon (if using real IPFS)
ipfs daemon
