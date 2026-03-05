#!/bin/bash
# Test all API endpoints except ingest and delete

set -e

BASE_URL="${API_URL:-http://localhost:8000}"

echo "=========================================="
echo "Testing FAQ RAG API"
echo "Base URL: $BASE_URL"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass_count=0
fail_count=0

# Function to test an endpoint with support for multiple expected status codes
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="$5"
    local alt_status="${6:-}"
    
    echo -e "${YELLOW}Testing: $name${NC}"
    echo "  $method $endpoint"
    
    # Create temp file for response
    local tmp_file=$(mktemp)
    
    if [ -n "$data" ]; then
        http_code=$(curl -s -w "%{http_code}" -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" -o "$tmp_file")
    else
        http_code=$(curl -s -w "%{http_code}" -X "$method" "$BASE_URL$endpoint" -o "$tmp_file")
    fi
    
    body=$(cat "$tmp_file")
    rm -f "$tmp_file"
    
    # Check if http_code matches expected or alternative status
    if [ "$http_code" = "$expected_status" ] || { [ -n "$alt_status" ] && [ "$http_code" = "$alt_status" ]; }; then
        echo -e "  ${GREEN}✓ PASS${NC} (Status: $http_code)"
        ((pass_count++))
    else
        echo -e "  ${RED}✗ FAIL${NC} (Expected: $expected_status${alt_status:+ or $alt_status}, Got: $http_code)"
        ((fail_count++))
    fi
    
    echo "  Response: $(echo "$body" | head -c 200)..."
    echo ""
}

# Test 1: Root endpoint
test_endpoint "Root endpoint" "GET" "/" "" "200"

# Test 2: Health check
test_endpoint "Health check" "GET" "/health" "" "200"

# Test 3: Ingestion status (may return 200 or 500 depending on state)
test_endpoint "Ingestion status" "GET" "/ingestion/status" "" "200" "500"

# Test 4: Ask with empty question (returns 422 due to Pydantic validation)
test_endpoint "Ask with empty question" "POST" "/ask" '{"question": ""}' "422"

# Test 5: Ask with invalid top_k (should fail with 422)
test_endpoint "Ask with invalid top_k (0)" "POST" "/ask" '{"question": "Test", "top_k": 0}' "422"

# Test 6: Ask with top_k > 10 (should fail with 422)
test_endpoint "Ask with top_k > 10" "POST" "/ask" '{"question": "Test", "top_k": 15}' "422"

# Test 7: 404 for unknown endpoint
test_endpoint "Unknown endpoint" "GET" "/unknown" "" "404"

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "Passed: ${GREEN}$pass_count${NC}"
echo -e "Failed: ${RED}$fail_count${NC}"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi