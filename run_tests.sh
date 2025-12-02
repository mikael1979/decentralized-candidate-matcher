#!/bin/bash
# Test runner for decentralized-candidate-matcher

echo "🧪 TEST RUNNER - Decentralized Candidate Matcher"
echo "================================================"
echo ""

# Check if in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Not in a virtual environment"
    echo "   Activate with: source venv/bin/activate"
    echo ""
fi

# Options
case "$1" in
    "unit")
        echo "📊 Running unit tests..."
        echo "------------------------"
        python -m pytest tests/unit/ -v --tb=short
        ;;
    "integration")
        echo "🔗 Running integration tests..."
        echo "-----------------------------"
        python -m pytest tests/integration/ -v --tb=short
        ;;
    "cli")
        echo "🖥️  Running CLI tests..."
        echo "----------------------"
        python -m pytest tests/unit/cli/ -v --tb=short
        ;;
    "core")
        echo "⚙️  Running core tests..."
        echo "-----------------------"
        python -m pytest tests/unit/core/ -v --tb=short
        ;;
    "ipfs")
        echo "🌐 Running IPFS tests..."
        echo "----------------------"
        python -m pytest tests/integration/ipfs/ -v --tb=short
        ;;
    "config")
        echo "⚙️  Running config tests..."
        echo "-------------------------"
        python -m pytest tests/integration/config/ -v --tb=short
        ;;
    "all"|"")
        echo "🚀 Running all tests..."
        echo "---------------------"
        python -m pytest tests/ -v --tb=short
        ;;
    "coverage")
        echo "📈 Running tests with coverage..."
        echo "------------------------------"
        python -m pytest tests/ --cov=src --cov-report=html --cov-report=term
        echo "Coverage report: htmlcov/index.html"
        ;;
    "list")
        echo "📋 Listing all tests..."
        echo "---------------------"
        python -m pytest tests/ --collect-only 2>/dev/null | grep "<Function test_" | wc -l
        echo " test functions found"
        ;;
    *)
        echo "Usage: $0 [unit|integration|cli|core|ipfs|config|all|coverage|list]"
        echo ""
        echo "Examples:"
        echo "  $0 unit        # Run unit tests"
        echo "  $0 integration # Run integration tests"
        echo "  $0 all         # Run all tests"
        echo "  $0 coverage    # Run with coverage report"
        ;;
esac
