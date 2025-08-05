#!/usr/bin/env python3
"""
Test script for the Keylogger CLI tool
Creates sample encrypted logs and tests all CLI functionality
"""

import os
import sys
import tempfile
import shutil
import datetime
import subprocess
import time

# Import modules from src directory
from keylogger import (
    derive_key_from_password, encrypt_message, 
    LOG_DIR, SALT_FILE, get_current_log_file
)

class CLITester:
    """Test harness for the Keylogger CLI"""
    
    def __init__(self):
        self.test_password = "test123"
        self.test_salt = b"test_salt_1234567890abcdef"  # 16 bytes
        self.backup_files = []
        
    def setup_test_environment(self):
        """Set up test environment with sample data"""
        print("🔧 Setting up test environment...")
        
        # Backup existing files if they exist
        files_to_backup = [SALT_FILE]
        for log_file in [get_current_log_file()]:
            if os.path.exists(log_file):
                files_to_backup.append(log_file)
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                backup_path = file_path + ".backup"
                shutil.copy2(file_path, backup_path)
                self.backup_files.append((file_path, backup_path))
                print(f"  📦 Backed up: {os.path.basename(file_path)}")
        
        # Create test salt file
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(SALT_FILE, 'wb') as f:
            f.write(self.test_salt)
        
        # Derive test encryption key
        encryption_key = derive_key_from_password(self.test_password, self.test_salt)
        
        # Create sample log entries for different dates
        test_dates = [
            datetime.datetime.now() - datetime.timedelta(days=3),
            datetime.datetime.now() - datetime.timedelta(days=2),
            datetime.datetime.now() - datetime.timedelta(days=1),
            datetime.datetime.now(),
        ]
        
        sample_entries = [
            # Entries for 3 days ago
            [
                "Key: 'h'",
                "Key: 'e'", 
                "Key: 'l'",
                "Key: 'l'",
                "Key: 'o'",
                "Special: space",
                "Key: 'w'",
                "Key: 'o'",
                "Key: 'r'",
                "Key: 'l'",
                "Key: 'd'",
                "Special: enter"
            ],
            # Entries for 2 days ago
            [
                "Key: 't'",
                "Key: 'e'",
                "Key: 's'",
                "Key: 't'",
                "Special: space",
                "Key: 'l'",
                "Key: 'o'",
                "Key: 'g'",
                "Special: enter"
            ],
            # Entries for yesterday
            [
                "Key: 'p'",
                "Key: 'a'",
                "Key: 's'",
                "Key: 's'",
                "Key: 'w'",
                "Key: 'o'",
                "Key: 'r'",
                "Key: 'd'",
                "Special: enter",
                "Key: '1'",
                "Key: '2'",
                "Key: '3'",
                "Special: enter"
            ],
            # Entries for today
            [
                "Key: 'c'",
                "Key: 'l'",
                "Key: 'i'",
                "Special: space",
                "Key: 't'",
                "Key: 'e'",
                "Key: 's'",
                "Key: 't'",
                "Special: enter"
            ]
        ]
        
        window_titles = [
            "Terminal - bash",
            "Visual Studio Code - keylogger.py", 
            "Firefox - GitHub",
            "Terminal - keylogger_cli test"
        ]
        
        # Create log files for each test date
        for i, (test_date, entries) in enumerate(zip(test_dates, sample_entries)):
            date_str = test_date.strftime('%Y-%m-%d')
            log_file = os.path.join(LOG_DIR, f"{date_str}-log.enc")
            
            window_title = window_titles[i % len(window_titles)]
            
            with open(log_file, 'wb') as f:
                for entry in entries:
                    # Create timestamp
                    timestamp = test_date.isoformat() + "Z"
                    
                    # Create log entry with window title (new format)
                    log_entry = f"{timestamp} - [{window_title}] - {entry}"
                    
                    # Encrypt and write
                    encrypted_entry = encrypt_message(log_entry, encryption_key)
                    f.write(encrypted_entry + b'\n')
                    
                    # Increment time slightly
                    test_date += datetime.timedelta(seconds=1)
            
            print(f"  📝 Created test log: {date_str}-log.enc ({len(entries)} entries)")
        
        print("✅ Test environment ready!")
        return True
    
    def cleanup_test_environment(self):
        """Clean up test environment"""
        print("\n🧹 Cleaning up test environment...")
        
        # Remove test log files
        test_files = [
            SALT_FILE,
            os.path.join(LOG_DIR, "*.enc")
        ]
        
        import glob
        for pattern in test_files:
            for file_path in glob.glob(pattern):
                try:
                    os.remove(file_path)
                    print(f"  🗑️  Removed: {os.path.basename(file_path)}")
                except:
                    pass
        
        # Restore backups
        for original_path, backup_path in self.backup_files:
            if os.path.exists(backup_path):
                shutil.move(backup_path, original_path)
                print(f"  📦 Restored: {os.path.basename(original_path)}")
        
        print("✅ Cleanup completed!")
    
    def run_cli_command(self, command_args, input_text=None):
        """Run a CLI command and return the result"""
        cmd = ['python3', 'keylogger_cli.py'] + command_args
        
        try:
            result = subprocess.run(
                cmd, 
                input=input_text,
                text=True,
                capture_output=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
    
    def test_list_command(self):
        """Test the list command"""
        print("\n📋 Testing 'list' command...")
        
        returncode, stdout, stderr = self.run_cli_command(['list'])
        
        if returncode == 0:
            print("✅ List command successful")
            if "Available Log Files" in stdout:
                print("✅ Found log files in output")
            else:
                print("⚠️  No log files shown (expected if no logs exist)")
            print(f"📄 Output preview:\n{stdout[:200]}...")
        else:
            print(f"❌ List command failed: {stderr}")
        
        return returncode == 0
    
    def test_view_command(self):
        """Test the view command"""
        print("\n👁️  Testing 'view' command...")
        
        # Test basic view with password
        returncode, stdout, stderr = self.run_cli_command(
            ['view', '--password', self.test_password],
            input_text=""
        )
        
        if returncode == 0:
            print("✅ View command successful")
            if "hello world" in stdout.lower():
                print("✅ Found expected content in logs")
            else:
                print("⚠️  Expected content not found")
            print(f"📄 Output preview:\n{stdout[:300]}...")
        else:
            print(f"❌ View command failed: {stderr}")
        
        return returncode == 0
    
    def test_view_with_filters(self):
        """Test view command with filters"""
        print("\n🔍 Testing 'view' command with filters...")
        
        # Test window filter
        returncode, stdout, stderr = self.run_cli_command([
            'view', 
            '--password', self.test_password,
            '--window', 'Terminal',
            '--format', 'json'
        ])
        
        if returncode == 0:
            print("✅ View with window filter successful")
            if '"window_title"' in stdout:
                print("✅ JSON format working")
            else:
                print("⚠️  JSON format not detected")
        else:
            print(f"❌ View with filter failed: {stderr}")
        
        return returncode == 0
    
    def test_stats_command(self):
        """Test the stats command"""
        print("\n📊 Testing 'stats' command...")
        
        returncode, stdout, stderr = self.run_cli_command([
            'stats',
            '--password', self.test_password
        ])
        
        if returncode == 0:
            print("✅ Stats command successful")
            if "Log Statistics" in stdout:
                print("✅ Statistics output detected")
            if "Total Entries:" in stdout:
                print("✅ Entry count found")
            print(f"📄 Output preview:\n{stdout[:400]}...")
        else:
            print(f"❌ Stats command failed: {stderr}")
        
        return returncode == 0
    
    def test_search_command(self):
        """Test the search command"""
        print("\n🔎 Testing 'search' command...")
        
        returncode, stdout, stderr = self.run_cli_command([
            'search', 'password',
            '--password', self.test_password
        ])
        
        if returncode == 0:
            print("✅ Search command successful")
            if "password" in stdout.lower():
                print("✅ Found search pattern in results")
            else:
                print("⚠️  Search pattern not found in results")
        else:
            print(f"❌ Search command failed: {stderr}")
        
        return returncode == 0
    
    def test_date_range_filtering(self):
        """Test date range filtering"""
        print("\n📅 Testing date range filtering...")
        
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        returncode, stdout, stderr = self.run_cli_command([
            'view',
            '--start-date', yesterday,
            '--end-date', today,
            '--password', self.test_password,
            '--format', 'csv'
        ])
        
        if returncode == 0:
            print("✅ Date range filtering successful")
            if "timestamp,window_title" in stdout:
                print("✅ CSV format working")
            else:
                print("⚠️  CSV header not found")
        else:
            print(f"❌ Date range filtering failed: {stderr}")
        
        return returncode == 0
    
    def test_invalid_password(self):
        """Test invalid password handling"""
        print("\n🔒 Testing invalid password handling...")
        
        returncode, stdout, stderr = self.run_cli_command([
            'view',
            '--password', 'wrong_password'
        ])
        
        if returncode != 0:
            print("✅ Invalid password properly rejected")
        else:
            print("❌ Invalid password was accepted (security issue!)")
        
        return returncode != 0
    
    def run_all_tests(self):
        """Run all CLI tests"""
        print("🧪 Keylogger CLI Test Suite")
        print("=" * 50)
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Failed to setup test environment")
            return False
        
        try:
            tests = [
                self.test_list_command,
                self.test_view_command,
                self.test_view_with_filters,
                self.test_stats_command,
                self.test_search_command,
                self.test_date_range_filtering,
                self.test_invalid_password
            ]
            
            passed = 0
            total = len(tests)
            
            for test in tests:
                try:
                    if test():
                        passed += 1
                    time.sleep(0.5)  # Brief pause between tests
                except Exception as e:
                    print(f"❌ Test failed with exception: {e}")
            
            print(f"\n🎯 Test Results: {passed}/{total} tests passed")
            
            if passed == total:
                print("🎉 All tests passed! CLI is working correctly.")
                return True
            else:
                print("⚠️  Some tests failed. Check the output above.")
                return False
                
        finally:
            self.cleanup_test_environment()

def main():
    """Run the CLI test suite"""
    print("🔧 Keylogger CLI Test Suite")
    print("=" * 40)
    
    # Change to keylogger directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check if CLI exists
    if not os.path.exists('keylogger_cli.py'):
        print("❌ keylogger_cli.py not found!")
        return 1
    
    tester = CLITester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        tester.cleanup_test_environment()
        return 1
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
