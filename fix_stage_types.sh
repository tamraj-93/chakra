#!/bin/bash

echo "Fixing invalid stage_type values in database..."

# Python script to fix the database
python3 - << 'EOF'
import sqlite3
import sys

# Connect to the SQLite database
try:
    conn = sqlite3.connect("backend/chakra.db")
    cursor = conn.cursor()
    print("Successfully connected to the database")
    
    # Get all stage_types to check
    cursor.execute("SELECT id, stage_type FROM consultation_stages")
    stages = cursor.fetchall()
    
    fixed_count = 0
    
    for stage_id, stage_type in stages:
        # If stage_type is 'analysis', update it to 'problem_analysis'
        if stage_type == 'analysis':
            cursor.execute(
                "UPDATE consultation_stages SET stage_type = 'problem_analysis' WHERE id = ?",
                (stage_id,)
            )
            fixed_count += 1
            print(f"Fixed stage {stage_id}: changed 'analysis' to 'problem_analysis'")
        
        # If stage_type is 'conclusion', update it to 'summary'
        elif stage_type == 'conclusion':
            cursor.execute(
                "UPDATE consultation_stages SET stage_type = 'summary' WHERE id = ?",
                (stage_id,)
            )
            fixed_count += 1
            print(f"Fixed stage {stage_id}: changed 'conclusion' to 'summary'")
    
    conn.commit()
    print(f"Fixed {fixed_count} stages in the database")
    
except sqlite3.Error as e:
    print(f"Database error: {e}")
    sys.exit(1)
finally:
    if conn:
        conn.close()
EOF

echo "Database migration completed."
echo "Restarting backend server to apply changes..."

# Restart the backend server
./restart_backend.sh