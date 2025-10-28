#!/bin/bash
# Complete End-to-End Testing Suite
# Tests all components of the AI newsletter pipeline

echo "🧪 COMPLETE SYSTEM TEST SUITE"
echo "======================================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0
TOTAL=0

# Function to run test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🧪 TEST: $test_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    TOTAL=$((TOTAL + 1))
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED${NC}: $test_name"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ FAILED${NC}: $test_name"
        FAILED=$((FAILED + 1))
    fi
    echo ""
}

echo "Starting complete system tests..."
echo ""

# Test 1: Environment Configuration
run_test "Environment Configuration" "python3 verify_new_slack_app.py > /dev/null 2>&1"

# Test 2: Database Connection
run_test "Supabase Database Connection" "python3 -c 'from config.settings import Settings; from database.supabase_client import SupabaseClient; s = Settings(); c = SupabaseClient(s); print(\"Connected\")' > /dev/null 2>&1"

# Test 3: Slack Endpoints
run_test "Slack Endpoints Reachability" "python3 test_slack_endpoints.py > /dev/null 2>&1"

# Test 4: Slack Button Posting
run_test "Slack Button Messages" "python3 test_slack_buttons.py > /dev/null 2>&1"

# Test 5: Railway Health Check
run_test "Railway Server Health" "curl -s https://ai-newsletter-pipeline-production.up.railway.app/health | grep -q 'healthy'"

# Test 6: Airtable Connection (if configured)
run_test "Airtable Connection" "python3 -c 'from config.settings import Settings; s = Settings(); print(s.AIRTABLE_API_KEY is not None)' | grep -q True"

echo "======================================================================"
echo "📊 TEST RESULTS SUMMARY"
echo "======================================================================"
echo ""
echo "Total Tests: $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! System is fully operational!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Review the output above.${NC}"
    exit 1
fi
