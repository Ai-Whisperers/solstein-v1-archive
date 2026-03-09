#!/bin/bash
set -e

echo "🚀 Setting up Solstein Improvements System-Wide Access"
echo "======================================================"

SOLSTEIN_PATH="/home/ai-whisperers/Documents/Work/solstein"
IMPROVEMENTS_PATH="$SOLSTEIN_PATH/solstein-improvements"

# 1. Verify all scripts are present
echo "✓ Verifying improvements..."
SCRIPT_COUNT=$(ls -1 "$IMPROVEMENTS_PATH"/*.py 2>/dev/null | wc -l)
echo "  Found $SCRIPT_COUNT production scripts"

if [ $SCRIPT_COUNT -lt 15 ]; then
    echo "❌ ERROR: Expected 25+ scripts, found $SCRIPT_COUNT"
    exit 1
fi

# 2. Install dependencies
echo "✓ Checking Python dependencies..."
python3 -c "import fastapi" 2>/dev/null && echo "  ✓ FastAPI installed" || {
    echo "  Installing FastAPI and dependencies..."
    pip install -q fastapi uvicorn pydantic pyjwt scikit-learn xgboost numpy
}

# 3. Create convenience symlinks
echo "✓ Creating command-line shortcuts..."
mkdir -p /home/ai-whisperers/bin

create_symlink() {
    local script=$1
    local command=$2
    local symlink="/home/ai-whisperers/bin/$command"
    
    if [ -f "$IMPROVEMENTS_PATH/$script" ]; then
        ln -sf "$IMPROVEMENTS_PATH/$script" "$symlink" 2>/dev/null || true
        chmod +x "$IMPROVEMENTS_PATH/$script"
        echo "  ✓ solstein-$command → $script"
    fi
}

create_symlink "solstein-api-server.py" "api"
create_symlink "agent-coordinator.py" "coordinator"
create_symlink "analytics-engine.py" "analytics"
create_symlink "webhook-manager.py" "webhooks"
create_symlink "ml-models-engine.py" "ml"
create_symlink "dashboard-generator.py" "dashboard"
create_symlink "integration-orchestrator.py" "orchestrator"

# 4. Verify databases will be created
echo "✓ Database locations (auto-initialize on first run):"
for db in api.db distributed.db analytics.db webhooks.db ml-models.db dashboard.db orchestration.db; do
    echo "  • $SOLSTEIN_PATH/$db"
done

# 5. Test imports
echo "✓ Testing Python imports..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/home/ai-whisperers/Documents/Work/solstein/solstein-improvements')

components = [
    ('solstein_api_server', 'FastAPI Server'),
    ('agent_coordinator', 'Agent Coordinator'),
    ('analytics_engine', 'Analytics Engine'),
    ('webhook_manager', 'Webhook Manager'),
    ('ml_models_engine', 'ML Models'),
    ('dashboard_generator', 'Dashboard Generator'),
    ('integration_orchestrator', 'Orchestrator'),
]

for module, name in components:
    try:
        __import__(module)
        print(f"  ✓ {name}")
    except ImportError as e:
        print(f"  ✗ {name}: {e}")
        sys.exit(1)
PYEOF

# 6. Verify Docker setup
echo "✓ Checking Docker deployment..."
if [ -f "$SOLSTEIN_PATH/Dockerfile" ]; then
    echo "  ✓ Dockerfile found"
    if [ -f "$SOLSTEIN_PATH/docker-compose.yml" ]; then
        echo "  ✓ docker-compose.yml found"
    fi
    if [ -f "$SOLSTEIN_PATH/kubernetes-deployment.yaml" ]; then
        echo "  ✓ kubernetes-deployment.yaml found"
    fi
fi

# 7. Display usage
echo ""
echo "✅ Setup Complete!"
echo "======================================================"
echo ""
echo "📦 Quick Start Options:"
echo ""
echo "1. Start API Server (from any directory):"
echo "   solstein-api"
echo "   # or"
echo "   python3 $IMPROVEMENTS_PATH/solstein-api-server.py"
echo ""
echo "2. Use Docker (from solstein directory):"
echo "   cd $SOLSTEIN_PATH"
echo "   docker-compose up -d"
echo "   curl http://localhost:8000/api/v1/health"
echo ""
echo "3. Use in Your Python Project:"
echo "   import sys"
echo "   sys.path.insert(0, '$IMPROVEMENTS_PATH')"
echo "   from integration_orchestrator import IntegrationOrchestrator"
echo ""
echo "4. Deploy to Kubernetes:"
echo "   kubectl apply -f $SOLSTEIN_PATH/kubernetes-deployment.yaml"
echo ""
echo "📚 Documentation:"
echo "   • $SOLSTEIN_PATH/SOLSTEIN_IMPROVEMENTS_GUIDE.md"
echo "   • $SOLSTEIN_PATH/.claude/TIER_4_SPECIFICATION.md"
echo ""
echo "🎯 Next Steps:"
echo "   1. Copy this file path to your ~/.bashrc for easy access"
echo "   2. Start the API server: solstein-api"
echo "   3. Access docs: http://localhost:8000/docs"
echo ""
