#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     CLEANUP DEBUG AND TEST FILES                ${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""

# Base directory
BASE_DIR="/home/nilabh/Projects/chakra"

# Confirm backup exists
if [ ! -d "$BASE_DIR/backup_debug_files" ]; then
    echo -e "${RED}Error: Backup directory not found!${NC}"
    echo -e "${YELLOW}Please create a backup of your debug and test files first.${NC}"
    exit 1
fi

# Count files before removal
DEBUG_COUNT=$(ls -1 $BASE_DIR/debug_* 2>/dev/null | wc -l)
TEST_COUNT=$(ls -1 $BASE_DIR/test_* 2>/dev/null | wc -l)
FRONTEND_TEST_COUNT=$(ls -1 $BASE_DIR/frontend_test_* 2>/dev/null | wc -l)
TOTAL_COUNT=$((DEBUG_COUNT + TEST_COUNT + FRONTEND_TEST_COUNT))

echo -e "${YELLOW}Found $TOTAL_COUNT files to clean up:${NC}"
echo -e "  - $DEBUG_COUNT debug files"
echo -e "  - $TEST_COUNT test files"
echo -e "  - $FRONTEND_TEST_COUNT frontend test files"
echo ""

# Files to keep (modify this array if you want to keep certain files)
# Example: FILES_TO_KEEP=("test_auth.sh" "debug_api_urls.sh")
FILES_TO_KEEP=()

# Print files that will be kept
if [ ${#FILES_TO_KEEP[@]} -gt 0 ]; then
    echo -e "${YELLOW}The following files will be kept:${NC}"
    for file in "${FILES_TO_KEEP[@]}"; do
        echo -e "  - $file"
    done
    echo ""
fi

# Ask for confirmation
echo -e "${YELLOW}This script will remove all debug and test files from your workspace.${NC}"
echo -e "${YELLOW}All files have been backed up to $BASE_DIR/backup_debug_files/${NC}"
read -p "Do you want to proceed? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Operation cancelled.${NC}"
    exit 0
fi

# Remove files
echo ""
echo -e "${YELLOW}Removing files...${NC}"

# Remove debug files
for file in $BASE_DIR/debug_*; do
    filename=$(basename "$file")
    
    # Check if file should be kept
    keep=false
    for keep_file in "${FILES_TO_KEEP[@]}"; do
        if [ "$filename" == "$keep_file" ]; then
            keep=true
            break
        fi
    done
    
    if [ "$keep" == "true" ]; then
        echo -e "${BLUE}Keeping ${filename}${NC}"
    else
        rm -f "$file"
        echo -e "${GREEN}Removed ${filename}${NC}"
    fi
done

# Remove test files
for file in $BASE_DIR/test_*; do
    filename=$(basename "$file")
    
    # Check if file should be kept
    keep=false
    for keep_file in "${FILES_TO_KEEP[@]}"; do
        if [ "$filename" == "$keep_file" ]; then
            keep=true
            break
        fi
    done
    
    if [ "$keep" == "true" ]; then
        echo -e "${BLUE}Keeping ${filename}${NC}"
    else
        rm -f "$file"
        echo -e "${GREEN}Removed ${filename}${NC}"
    fi
done

# Remove frontend test files
for file in $BASE_DIR/frontend_test_*; do
    filename=$(basename "$file")
    
    # Check if file should be kept
    keep=false
    for keep_file in "${FILES_TO_KEEP[@]}"; do
        if [ "$filename" == "$keep_file" ]; then
            keep=true
            break
        fi
    done
    
    if [ "$keep" == "true" ]; then
        echo -e "${BLUE}Keeping ${filename}${NC}"
    else
        rm -f "$file"
        echo -e "${GREEN}Removed ${filename}${NC}"
    fi
done

echo ""
echo -e "${GREEN}Cleanup completed successfully!${NC}"
echo -e "${YELLOW}If you need to restore any files, they are available in $BASE_DIR/backup_debug_files/${NC}"