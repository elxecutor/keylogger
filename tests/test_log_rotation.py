#!/usr/bin/env python3
"""
Test script for daily log rotation and cleanup functionality
"""

import os
import sys
import time
import datetime
import tempfile
import shutil
import subprocess

# Add the current directory to the path to import keylogger functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from keylogger import (
    get_current_log_file, cleanup_old_logs, rotate_log_if_needed,
    LOG_DIR, ARCHIVE_DIR, LOG_RETENTION_DAYS
)

def test_log_file_naming():
    """Test daily log file naming format"""
    print("Testing log file naming format...")
    
    # Test current date format
    current_log = get_current_log_file()
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    expected_name = f"{today}-log.enc"
    
    if expected_name in current_log:
        print(f"✓ Log file naming correct: {os.path.basename(current_log)}")
    else:
        print(f"✗ Log file naming incorrect: {os.path.basename(current_log)}")
        print(f"  Expected pattern: {expected_name}")

def test_log_rotation():
    """Test log rotation functionality"""
    print("\nTesting log rotation...")
    
    # Create some test log files with different dates
    test_dates = [
        datetime.datetime.now(),
        datetime.datetime.now() - datetime.timedelta(days=1),
        datetime.datetime.now() - datetime.timedelta(days=2),
        datetime.datetime.now() - datetime.timedelta(days=35),  # Should be cleaned up
        datetime.datetime.now() - datetime.timedelta(days=60),  # Should be cleaned up
    ]
    
    created_files = []
    
    try:
        # Create test files
        for test_date in test_dates:
            date_str = test_date.strftime('%Y-%m-%d')
            test_file = os.path.join(LOG_DIR, f"{date_str}-log.enc")
            
            with open(test_file, 'w') as f:
                f.write(f"Test log entry for {date_str}\n")
            
            created_files.append(test_file)
            print(f"Created test file: {os.path.basename(test_file)}")
        
        print(f"✓ Created {len(created_files)} test log files")
        
        # Test cleanup function
        print("\nTesting cleanup function...")
        cleanup_old_logs()
        
        # Check which files remain
        remaining_files = []
        archived_files = []
        
        for test_file in created_files:
            if os.path.exists(test_file):
                remaining_files.append(test_file)
            
            # Check if archived
            archive_file = os.path.join(ARCHIVE_DIR, os.path.basename(test_file))
            if os.path.exists(archive_file):
                archived_files.append(archive_file)
        
        print(f"✓ Files remaining: {len(remaining_files)}")
        print(f"✓ Files archived: {len(archived_files)}")
        
        # Verify recent files are kept
        recent_cutoff = datetime.datetime.now() - datetime.timedelta(days=LOG_RETENTION_DAYS)
        
        for test_file in remaining_files:
            basename = os.path.basename(test_file)
            date_str = basename.split('-log.enc')[0]
            file_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            
            if file_date >= recent_cutoff:
                print(f"✓ Recent file kept: {basename}")
            else:
                print(f"✗ Old file not cleaned up: {basename}")
        
    finally:
        # Clean up test files
        for test_file in created_files:
            try:
                if os.path.exists(test_file):
                    os.remove(test_file)
            except:
                pass
        
        # Clean up archived test files
        if os.path.exists(ARCHIVE_DIR):
            for test_date in test_dates:
                date_str = test_date.strftime('%Y-%m-%d')
                archive_file = os.path.join(ARCHIVE_DIR, f"{date_str}-log.enc")
                try:
                    if os.path.exists(archive_file):
                        os.remove(archive_file)
                except:
                    pass

def test_command_line_options():
    """Test new command line options"""
    print("\nTesting command line options...")
    
    # Test --help to see new options
    try:
        result = subprocess.run([
            sys.executable, 'keylogger.py', '--help'
        ], capture_output=True, text=True, timeout=10)
        
        if '--list' in result.stdout and '--cleanup' in result.stdout:
            print("✓ New command line options available")
        else:
            print("✗ New command line options not found")
            
    except Exception as e:
        print(f"✗ Error testing command line options: {e}")
    
    # Test --list option
    try:
        result = subprocess.run([
            sys.executable, 'keylogger.py', '--list'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✓ --list option works")
        else:
            print("✗ --list option failed")
            
    except Exception as e:
        print(f"✗ Error testing --list option: {e}")

def test_log_utils_enhancements():
    """Test enhanced log_utils.py functionality"""
    print("\nTesting log_utils.py enhancements...")
    
    try:
        # Test --stats option
        result = subprocess.run([
            sys.executable, 'log_utils.py', '--stats'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✓ log_utils.py --stats works")
        else:
            print("✗ log_utils.py --stats failed")
        
        # Test --help to see new options
        result = subprocess.run([
            sys.executable, 'log_utils.py', '--help'
        ], capture_output=True, text=True, timeout=10)
        
        if '--archive' in result.stdout:
            print("✓ log_utils.py has archive option")
        else:
            print("✗ log_utils.py missing archive option")
            
    except Exception as e:
        print(f"✗ Error testing log_utils.py: {e}")

def test_directory_structure():
    """Test directory structure creation"""
    print("\nTesting directory structure...")
    
    if os.path.exists(LOG_DIR):
        print(f"✓ Log directory exists: {LOG_DIR}")
    else:
        print(f"✗ Log directory missing: {LOG_DIR}")
    
    # Test archive directory creation
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    if os.path.exists(ARCHIVE_DIR):
        print(f"✓ Archive directory exists: {ARCHIVE_DIR}")
    else:
        print(f"✗ Archive directory missing: {ARCHIVE_DIR}")

def main():
    """Run all tests"""
    print("=== Daily Log Rotation Test Suite ===\n")
    
    # Change to keylogger directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        test_directory_structure()
        test_log_file_naming()
        test_log_rotation()
        test_command_line_options()
        test_log_utils_enhancements()
        
        print("\n=== Test Summary ===")
        print("All daily log rotation tests completed.")
        print(f"Log retention period: {LOG_RETENTION_DAYS} days")
        print(f"Archive directory: {ARCHIVE_DIR}")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
