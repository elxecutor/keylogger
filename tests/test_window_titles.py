#!/usr/bin/env python3
"""
Test script for window title capture functionality
"""

import os
import sys
import time
import subprocess

# Add the current directory to the path to import keylogger functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from keylogger import get_active_window_title, get_current_window_context, KeyloggerState
except ImportError as e:
    print(f"Error importing keylogger functions: {e}")
    sys.exit(1)

def test_window_title_capture():
    """Test window title capture functionality"""
    print("🪟 Window Title Capture Test")
    print("=" * 40)
    
    # Test direct window title capture
    print("Testing direct window title capture...")
    window_title = get_active_window_title()
    print(f"✅ Current window title: '{window_title}'")
    
    # Test cached window title capture
    print("\nTesting cached window title capture...")
    keylogger_state = KeyloggerState()
    
    for i in range(3):
        cached_title = get_current_window_context()
        print(f"Attempt {i+1}: '{cached_title}'")
        time.sleep(0.5)
    
    print("\n📊 Platform Information:")
    print(f"Operating System: {os.name}")
    print(f"Platform: {sys.platform}")
    
    # Test platform-specific implementations
    if os.name == 'nt':
        print("🪟 Windows platform detected")
        try:
            import ctypes
            print("✅ ctypes available for Windows API access")
        except ImportError:
            print("❌ ctypes not available")
    
    elif sys.platform == 'darwin':
        print("🍎 macOS platform detected")
        try:
            result = subprocess.run(['osascript', '-e', 'return "AppleScript test"'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                print("✅ osascript available for AppleScript access")
            else:
                print("❌ osascript failed")
        except Exception as e:
            print(f"❌ osascript not available: {e}")
    
    else:
        print("🐧 Linux platform detected")
        tools = ['xdotool', 'wmctrl', 'xwininfo', 'xprop']
        available_tools = []
        
        for tool in tools:
            try:
                result = subprocess.run([tool, '--version'], 
                                      capture_output=True, text=True, timeout=2)
                available_tools.append(tool)
            except FileNotFoundError:
                try:
                    result = subprocess.run([tool, '--help'], 
                                          capture_output=True, text=True, timeout=2)
                    available_tools.append(tool)
                except FileNotFoundError:
                    pass
        
        if available_tools:
            print(f"✅ Available window tools: {', '.join(available_tools)}")
        else:
            print("❌ No window management tools found")
            print("💡 Install with: sudo apt-get install xdotool wmctrl x11-utils")

def test_window_title_changes():
    """Test window title capture with changes"""
    print("\n🔄 Window Title Change Detection Test")
    print("=" * 40)
    print("Instructions:")
    print("1. This test will capture window titles for 30 seconds")
    print("2. Switch between different applications to test detection")
    print("3. The test will show when window titles change")
    print("\nStarting in 3 seconds...")
    
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    print("🔍 Monitoring window titles (30 seconds)...")
    
    last_title = ""
    start_time = time.time()
    change_count = 0
    
    while time.time() - start_time < 30:
        current_title = get_active_window_title()
        
        if current_title != last_title:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Window changed: '{current_title}'")
            last_title = current_title
            change_count += 1
        
        time.sleep(0.5)
    
    print(f"\n✅ Test completed! Detected {change_count} window changes.")

def test_log_format():
    """Test the new log format with window titles"""
    print("\n📝 Log Format Test")
    print("=" * 40)
    
    # Simulate the new log format
    import datetime
    
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    window_title = get_active_window_title()
    key_info = "Key: 'a'"
    
    log_entry = f"{timestamp} - [{window_title}] - {key_info}"
    print("Sample log entry format:")
    print(f"'{log_entry}'")
    
    print(f"\nLog entry length: {len(log_entry)} characters")
    print("✅ New format includes window context!")

def main():
    """Run all window title tests"""
    print("🧪 Window Title Capture Test Suite")
    print("=" * 50)
    
    # Change to keylogger directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        test_window_title_capture()
        test_log_format()
        
        # Ask user if they want to test window changes
        print("\n" + "=" * 50)
        response = input("Would you like to test window title change detection? (y/N): ")
        if response.lower().startswith('y'):
            test_window_title_changes()
        
        print("\n🎉 All window title tests completed!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
