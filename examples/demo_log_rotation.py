#!/usr/bin/env python3
"""
Quick demonstration of the daily log rotation feature
"""

import os
import sys
import time
import subprocess
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from keylogger import get_current_log_file, LOG_DIR

def demo_log_rotation():
    """Demonstrate the daily log rotation feature"""
    print("🔄 Daily Log Rotation Demo")
    print("=" * 40)
    
    # Show current log file format
    current_log = get_current_log_file()
    print(f"📅 Today's log file: {os.path.basename(current_log)}")
    print(f"📂 Log directory: {LOG_DIR}")
    
    # Show expected format
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"✅ Expected format: {today}-log.enc")
    
    # Test that the log file name is correctly formatted
    if f"{today}-log.enc" in current_log:
        print("✅ Log file naming is correct!")
    else:
        print("❌ Log file naming issue detected")
    
    print("\n📊 Available Commands:")
    print("• python keylogger.py --list      # List all log files")
    print("• python keylogger.py --cleanup   # Clean up old logs")
    print("• python log_utils.py --stats     # Show log statistics")
    print("• python log_utils.py --archive   # Archive current logs")
    
    print("\n🔒 Daily Benefits:")
    print("• Organized by date for easy management")
    print("• Automatic cleanup after 30 days")
    print("• Smaller files for better performance")
    print("• Enhanced security through file separation")
    
    print("\n✨ Demo completed successfully!")

if __name__ == "__main__":
    demo_log_rotation()
