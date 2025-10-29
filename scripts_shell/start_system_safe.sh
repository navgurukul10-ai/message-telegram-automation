#!/bin/bash
# Safe startup script that prevents database lock issues

echo "============================================================"
echo "           SAFE SYSTEM STARTUP"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check and fix session files
fix_sessions() {
    echo "Checking session files..."
    
    # Check if sessions exist
    if [ ! -d "sessions" ] || [ -z "$(ls -A sessions/*.session 2>/dev/null)" ]; then
        echo -e "${YELLOW}⚠️  No session files found. Please authorize first.${NC}"
        return 1
    fi
    
    # Run the fix script
    python3 fix_session_locks.py
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Session files ready${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to fix session files${NC}"
        echo "There might be running processes. Checking..."
        
        # Check for running processes
        pids=$(lsof sessions/*.session 2>/dev/null | grep python | awk '{print $2}' | sort -u)
        
        if [ ! -z "$pids" ]; then
            echo -e "${YELLOW}Found running processes holding session locks: $pids${NC}"
            echo "Do you want to stop them? (y/n)"
            read -r response
            
            if [[ "$response" =~ ^[Yy]$ ]]; then
                echo "Stopping processes..."
                kill -15 $pids 2>/dev/null
                sleep 3
                
                # Force kill if still running
                for pid in $pids; do
                    if ps -p $pid > /dev/null 2>&1; then
                        kill -9 $pid 2>/dev/null
                    fi
                done
                
                echo "Retrying session fix..."
                python3 fix_session_locks.py
                return $?
            else
                echo "Cannot proceed with locked session files."
                return 1
            fi
        fi
        return 1
    fi
}

# Function to check database
check_database() {
    echo ""
    echo "Checking main database..."
    
    if [ -f "data/database/telegram_jobs.db" ]; then
        mode=$(sqlite3 data/database/telegram_jobs.db "PRAGMA journal_mode;" 2>/dev/null)
        if [ "$mode" = "wal" ]; then
            echo -e "${GREEN}✅ Main database using WAL mode${NC}"
        else
            echo -e "${YELLOW}⚠️  Main database not using WAL mode, fixing...${NC}"
            sqlite3 data/database/telegram_jobs.db "PRAGMA journal_mode=WAL;" 2>/dev/null
            echo -e "${GREEN}✅ Fixed${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Database will be created on first run${NC}"
    fi
}

# Main execution
cd "$(dirname "$0")/.."

echo "Step 1: Fixing session files"
echo "----------------------------"
fix_sessions

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}❌ Cannot start - session files are locked${NC}"
    echo "Please stop all running instances and try again."
    exit 1
fi

echo ""
echo "Step 2: Checking database"
echo "-------------------------"
check_database

echo ""
echo "Step 3: Starting system"
echo "-----------------------"
echo -e "${GREEN}All checks passed! Starting system...${NC}"
echo ""

# Start the system
python3 scripts/main.py

echo ""
echo "============================================================"
echo "           SYSTEM STOPPED"
echo "============================================================"

