#!/bin/bash

# IntelliAttend Comprehensive API Test Script
# Tests all features and generates a detailed report

BASE_URL="http://localhost:5002"
TEST_RESULTS_FILE="/tmp/intelliattend_test_results.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test result counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Function to log test results
log_test() {
    local test_name="$1"
    local status="$2"
    local response="$3"
    local expected="$4"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if [ "$status" = "PASS" ]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "${GREEN}✓ PASS${NC}: $test_name"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "${RED}✗ FAIL${NC}: $test_name"
        echo -e "  ${YELLOW}Response:${NC} $response"
        if [ ! -z "$expected" ]; then
            echo -e "  ${YELLOW}Expected:${NC} $expected"
        fi
    fi
    
    # Log to JSON file
    echo "{\"test\": \"$test_name\", \"status\": \"$status\", \"response\": $response, \"timestamp\": \"$(date -Iseconds)\"}" >> "$TEST_RESULTS_FILE"
}

# Function to get admin token
get_admin_token() {
    local response=$(curl -s -X POST "$BASE_URL/api/admin/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "admin123"}')
    
    local token=$(echo "$response" | jq -r '.access_token // empty')
    
    if [ ! -z "$token" ] && [ "$token" != "null" ]; then
        echo "$token"
    else
        echo ""
    fi
}

# Function to get faculty token
get_faculty_token() {
    local response=$(curl -s -X POST "$BASE_URL/api/faculty/login" \
        -H "Content-Type: application/json" \
        -d '{"email": "john.smith@university.edu", "password": "faculty123"}')
    
    local token=$(echo "$response" | jq -r '.data.access_token // empty')
    
    if [ ! -z "$token" ] && [ "$token" != "null" ]; then
        echo "$token"
    else
        echo ""
    fi
}

# Function to get student token
get_student_token() {
    local response=$(curl -s -X POST "$BASE_URL/api/student/login" \
        -H "Content-Type: application/json" \
        -d '{"email": "student1@student.edu", "password": "student123"}')
    
    local token=$(echo "$response" | jq -r '.data.access_token // empty')
    
    if [ ! -z "$token" ] && [ "$token" != "null" ]; then
        echo "$token"
    else
        echo ""
    fi
}

# Initialize test results file
echo "Starting IntelliAttend Comprehensive Test Suite"
echo "==============================================="
echo "[]" > "$TEST_RESULTS_FILE"

echo -e "\n${BLUE}1. SYSTEM HEALTH TESTS${NC}"
echo "========================="

# Test 1.1: Health Check
response=$(curl -s "$BASE_URL/api/health")
if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
    log_test "System Health Check" "PASS" "$response"
else
    log_test "System Health Check" "FAIL" "$response" '{"success": true}'
fi

# Test 1.2: Database Status
response=$(curl -s "$BASE_URL/api/db/status")
if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
    log_test "Database Status Check" "PASS" "$response"
else
    log_test "Database Status Check" "FAIL" "$response" '{"success": true}'
fi

# Test 1.3: Session Status
response=$(curl -s "$BASE_URL/api/session/status")
if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
    log_test "Session Management Status" "PASS" "$response"
else
    log_test "Session Management Status" "FAIL" "$response" '{"success": true}'
fi

echo -e "\n${BLUE}2. AUTHENTICATION TESTS${NC}"
echo "========================"

# Test 2.1: Admin Login
ADMIN_TOKEN=$(get_admin_token)
if [ ! -z "$ADMIN_TOKEN" ]; then
    log_test "Admin Login" "PASS" '{"success": true, "token_received": true}'
else
    log_test "Admin Login" "FAIL" '{"success": false, "token_received": false}' '{"success": true, "token_received": true}'
fi

# Test 2.2: Faculty Login
FACULTY_TOKEN=$(get_faculty_token)
if [ ! -z "$FACULTY_TOKEN" ]; then
    log_test "Faculty Login" "PASS" '{"success": true, "token_received": true}'
else
    log_test "Faculty Login" "FAIL" '{"success": false, "token_received": false}' '{"success": true, "token_received": true}'
fi

# Test 2.3: Student Login
STUDENT_TOKEN=$(get_student_token)
if [ ! -z "$STUDENT_TOKEN" ]; then
    log_test "Student Login" "PASS" '{"success": true, "token_received": true}'
else
    log_test "Student Login" "FAIL" '{"success": false, "token_received": false}' '{"success": true, "token_received": true}'
fi

echo -e "\n${BLUE}3. ADMIN PANEL TESTS${NC}"
echo "===================="

if [ ! -z "$ADMIN_TOKEN" ]; then
    # Test 3.1: Get Faculty List
    response=$(curl -s "$BASE_URL/api/admin/faculty" \
        -H "Authorization: Bearer $ADMIN_TOKEN")
    if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
        log_test "Admin - Get Faculty List" "PASS" "$response"
    else
        log_test "Admin - Get Faculty List" "FAIL" "$response" '{"success": true}'
    fi
    
    # Test 3.2: Get Students List
    response=$(curl -s "$BASE_URL/api/admin/students" \
        -H "Authorization: Bearer $ADMIN_TOKEN")
    if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
        log_test "Admin - Get Students List" "PASS" "$response"
    else
        log_test "Admin - Get Students List" "FAIL" "$response" '{"success": true}'
    fi
    
    # Test 3.3: Get Classes List
    response=$(curl -s "$BASE_URL/api/admin/classes" \
        -H "Authorization: Bearer $ADMIN_TOKEN")
    if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
        log_test "Admin - Get Classes List" "PASS" "$response"
    else
        log_test "Admin - Get Classes List" "FAIL" "$response" '{"success": true}'
    fi
    
    # Test 3.4: Get Classrooms List
    response=$(curl -s "$BASE_URL/api/admin/classrooms" \
        -H "Authorization: Bearer $ADMIN_TOKEN")
    if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
        log_test "Admin - Get Classrooms List" "PASS" "$response"
    else
        log_test "Admin - Get Classrooms List" "FAIL" "$response" '{"success": true}'
    fi
else
    log_test "Admin Panel Tests" "SKIP" '{"reason": "Admin token not available"}'
fi

echo -e "\n${BLUE}4. FACULTY TESTS${NC}"
echo "================"

if [ ! -z "$FACULTY_TOKEN" ]; then
    # Test 4.1: Generate OTP
    response=$(curl -s -X POST "$BASE_URL/api/faculty/generate-otp" \
        -H "Authorization: Bearer $FACULTY_TOKEN" \
        -H "Content-Type: application/json")
    if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
        log_test "Faculty - Generate OTP" "PASS" "$response"
        OTP_CODE=$(echo "$response" | jq -r '.data.otp')
    else
        log_test "Faculty - Generate OTP" "FAIL" "$response" '{"success": true}'
        OTP_CODE=""
    fi
else
    log_test "Faculty Tests" "SKIP" '{"reason": "Faculty token not available"}'
fi

echo -e "\n${BLUE}5. SESSION MANAGEMENT TESTS${NC}"
echo "============================"

if [ ! -z "$OTP_CODE" ]; then
    # Test 5.1: Verify OTP and Start Session
    response=$(curl -s -X POST "$BASE_URL/api/verify-otp" \
        -H "Content-Type: application/json" \
        -d "{\"otp\": \"$OTP_CODE\", \"class_id\": 1}")
    if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
        log_test "Session - Verify OTP and Start Session" "PASS" "$response"
        SESSION_ID=$(echo "$response" | jq -r '.data.session_id')
    else
        log_test "Session - Verify OTP and Start Session" "FAIL" "$response" '{"success": true}'
        SESSION_ID=""
    fi
    
    if [ ! -z "$SESSION_ID" ]; then
        # Wait a bit for QR generation to start
        sleep 2
        
        # Test 5.2: Get Current QR
        response=$(curl -s "$BASE_URL/api/qr/current/$SESSION_ID")
        if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
            log_test "Session - Get Current QR Code" "PASS" "$response"
        else
            log_test "Session - Get Current QR Code" "FAIL" "$response" '{"success": true}'
        fi
        
        # Test 5.3: Stop Session
        response=$(curl -s -X POST "$BASE_URL/api/session/stop/$SESSION_ID")
        if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
            log_test "Session - Stop Session" "PASS" "$response"
        else
            log_test "Session - Stop Session" "FAIL" "$response" '{"success": true}'
        fi
    fi
else
    log_test "Session Management Tests" "SKIP" '{"reason": "OTP not available"}'
fi

echo -e "\n${BLUE}6. STUDENT TESTS${NC}"
echo "================"

if [ ! -z "$STUDENT_TOKEN" ]; then
    # Since we don't have an active session, we can't test attendance scanning
    # But we can test the endpoint response format
    response=$(curl -s -X POST "$BASE_URL/api/attendance/scan" \
        -H "Authorization: Bearer $STUDENT_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "qr_data": "{\"session_id\": 999, \"token\": \"invalid\"}",
            "biometric_verified": true,
            "location": {"latitude": 40.7128, "longitude": -74.0060, "accuracy": 5},
            "bluetooth": {"rssi": -45},
            "device_info": {"type": "android", "version": "12"}
        }')
    # This should fail with invalid session, but should return proper error format
    if echo "$response" | jq -e '.error' > /dev/null 2>&1; then
        log_test "Student - Attendance Scan (Error Handling)" "PASS" "$response"
    else
        log_test "Student - Attendance Scan (Error Handling)" "FAIL" "$response" '{"error": "some error message"}'
    fi
else
    log_test "Student Tests" "SKIP" '{"reason": "Student token not available"}'
fi

echo -e "\n${BLUE}7. SYSTEM MONITORING TESTS${NC}"
echo "==========================="

# Test 7.1: System Metrics
response=$(curl -s "$BASE_URL/api/system/metrics")
if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
    log_test "System - Get Metrics" "PASS" "$response"
else
    log_test "System - Get Metrics" "FAIL" "$response" '{"success": true}'
fi

# Test 7.2: QR Service Status
response=$(curl -s "$BASE_URL/api/qr/status")
if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
    log_test "System - QR Service Status" "PASS" "$response"
else
    log_test "System - QR Service Status" "FAIL" "$response" '{"success": true}'
fi

# Test 7.3: Auth Service Status
response=$(curl -s "$BASE_URL/api/auth/status")
if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
    log_test "System - Auth Service Status" "PASS" "$response"
else
    log_test "System - Auth Service Status" "FAIL" "$response" '{"success": true}'
fi

echo -e "\n${BLUE}TEST SUMMARY${NC}"
echo "============"
echo -e "Total Tests: ${BLUE}$TESTS_TOTAL${NC}"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  Some tests failed. Check the output above for details.${NC}"
    exit 1
fi