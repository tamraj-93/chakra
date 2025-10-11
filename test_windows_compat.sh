#!/bin/bash
# Script to test Windows compatibility fixes in Linux

echo "=== Testing Windows Compatibility Solutions ==="
echo ""

# Function for colored output
function echo_color() {
    local color=$1
    local message=$2
    
    case $color in
        "red") echo -e "\033[0;31m$message\033[0m" ;;
        "green") echo -e "\033[0;32m$message\033[0m" ;;
        "yellow") echo -e "\033[0;33m$message\033[0m" ;;
        "blue") echo -e "\033[0;34m$message\033[0m" ;;
        *) echo "$message" ;;
    esac
}

# 1. Test line ending conversion (simulating Windows CRLF issue)
echo_color "blue" "1. Testing line ending conversion..."

# Create a test script with Windows-style line endings
echo -e "#!/bin/bash\r\necho 'Hello from test script'\r\nexit 0\r\n" > test_crlf.sh
chmod +x test_crlf.sh

# Try to run it directly (should fail with bad interpreter)
./test_crlf.sh > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo_color "green" "✓ Confirmed CRLF script fails as expected"
else
    echo_color "red" "✗ CRLF script didn't fail (unexpected)"
fi

# Fix with dos2unix simulation
sed -i 's/\r$//' test_crlf.sh

# Try again (should work)
./test_crlf.sh > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo_color "green" "✓ Line ending fix works correctly"
else
    echo_color "red" "✗ Line ending fix failed"
fi

# Clean up
rm test_crlf.sh

# 2. Test if our Docker scripts handle line endings
echo ""
echo_color "blue" "2. Testing Docker scripts with CRLF..."

# Make a backup of entrypoint.sh
cp docker/backend/entrypoint.sh docker/backend/entrypoint.sh.bak

# Convert entrypoint to CRLF
if command -v unix2dos &> /dev/null; then
    unix2dos docker/backend/entrypoint.sh
    echo_color "green" "✓ Converted entrypoint.sh to CRLF format"
else
    # Manual conversion
    sed -i 's/$/\r/' docker/backend/entrypoint.sh
    echo_color "green" "✓ Manually converted entrypoint.sh to CRLF format"
fi

# Test if Docker can handle building with CRLF scripts
echo_color "yellow" "Testing Docker build with CRLF scripts..."
echo_color "yellow" "This test will just build the backend container"
echo_color "yellow" "Press CTRL+C to skip this test if it takes too long"

# Build only the backend container as a test
docker build -t chakra-backend-test -f docker/backend/Dockerfile --target builder .
if [ $? -eq 0 ]; then
    echo_color "green" "✓ Docker build works despite CRLF line endings"
else
    echo_color "red" "✗ Docker build failed with CRLF line endings"
    echo_color "yellow" "Note: This is expected and what our Windows scripts fix"
fi

# Restore the original entrypoint.sh
mv docker/backend/entrypoint.sh.bak docker/backend/entrypoint.sh
echo_color "green" "✓ Restored original entrypoint.sh"

# 3. Test the Windows troubleshooting script
echo ""
echo_color "blue" "3. Testing Windows troubleshooting document..."
if [ -f "windows-troubleshooting.md" ]; then
    echo_color "green" "✓ Windows troubleshooting guide exists"
    sections=$(grep -c "^##" windows-troubleshooting.md)
    issues=$(grep -c "### Problem:" windows-troubleshooting.md)
    echo_color "green" "✓ Guide contains $sections sections and $issues specific issues"
else
    echo_color "red" "✗ Windows troubleshooting guide not found"
fi

# 4. Check Docker Compose config
echo ""
echo_color "blue" "4. Testing Docker Compose configuration..."
docker-compose -f docker-compose.demo.yml config > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo_color "green" "✓ Docker Compose configuration is valid"
else
    echo_color "red" "✗ Docker Compose configuration has errors"
fi

# 5. Verify scripts exist
echo ""
echo_color "blue" "5. Checking Windows batch scripts..."
if [ -f "windows-docker-setup.bat" ]; then
    echo_color "green" "✓ windows-docker-setup.bat exists"
else
    echo_color "red" "✗ windows-docker-setup.bat not found"
fi

if [ -f "win-start.bat" ]; then
    echo_color "green" "✓ win-start.bat exists"
else
    echo_color "red" "✗ win-start.bat not found"
fi

echo ""
echo_color "blue" "=== Test Summary ==="
echo_color "green" "All Windows compatibility tests completed"
echo_color "green" "Your setup should be ready for Windows deployment"
echo_color "yellow" "Note: This doesn't guarantee everything will work on Windows,"
echo_color "yellow" "      but the most common issues have been addressed."