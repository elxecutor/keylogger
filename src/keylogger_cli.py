#!/usr/bin/env python3
"""
Keylogger CLI - Comprehensive Command Line Interface for Log Management
A user-friendly tool for decrypting, viewing, and analyzing encrypted keylogger data.
"""

import os
import sys
import datetime
import getpass
import argparse
import glob
import re
from typing import List, Dict, Optional, Tuple
import json

# Add the current directory to the path to import keylogger functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from keylogger import (
        LOG_DIR, SALT_FILE, ARCHIVE_DIR, LOG_RETENTION_DAYS,
        derive_key_from_password, decrypt_message
    )
    from log_utils import parse_log_entry, get_all_log_files
except ImportError as e:
    print(f"Error importing keylogger modules: {e}")
    print("Make sure you're running this from the keylogger directory.")
    sys.exit(1)

class KeyloggerCLI:
    """Main CLI class for keylogger log management"""
    
    def __init__(self):
        self.encryption_key = None
        self.verified_password = False
        
    def verify_passphrase(self, password: str = None) -> bool:
        """Verify the decryption passphrase and derive encryption key"""
        if not os.path.exists(SALT_FILE):
            print("❌ Salt file not found. Cannot decrypt logs.")
            print(f"Expected location: {SALT_FILE}")
            return False
        
        if password is None:
            password = getpass.getpass("🔐 Enter decryption passphrase: ")
        
        try:
            with open(SALT_FILE, 'rb') as f:
                salt = f.read()
            
            self.encryption_key = derive_key_from_password(password, salt)
            
            # Test the key by trying to decrypt any available log entry
            log_files = get_all_log_files()
            if not log_files:
                print("⚠️  No log files found to verify passphrase against.")
                self.verified_password = True
                return True
            
            # Try to decrypt the first entry from the most recent log file
            for log_file in log_files:
                try:
                    with open(log_file, 'rb') as f:
                        first_line = f.readline().strip()
                        if first_line:
                            decrypt_message(first_line, self.encryption_key)
                            self.verified_password = True
                            print("✅ Passphrase verified successfully!")
                            return True
                except Exception:
                    continue
            
            print("❌ Invalid passphrase or corrupted log files.")
            return False
            
        except Exception as e:
            print(f"❌ Error verifying passphrase: {e}")
            return False
    
    def parse_date_range(self, start_date: str = None, end_date: str = None) -> Tuple[datetime.datetime, datetime.datetime]:
        """Parse and validate date range parameters"""
        today = datetime.datetime.now()
        
        # Parse start date
        if start_date:
            try:
                start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise ValueError(f"Invalid start date format: {start_date}. Use YYYY-MM-DD")
        else:
            # Default to 7 days ago
            start = today - datetime.timedelta(days=7)
        
        # Parse end date
        if end_date:
            try:
                end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
                # Set to end of day
                end = end.replace(hour=23, minute=59, second=59)
            except ValueError:
                raise ValueError(f"Invalid end date format: {end_date}. Use YYYY-MM-DD")
        else:
            # Default to today
            end = today.replace(hour=23, minute=59, second=59)
        
        if start > end:
            raise ValueError("Start date cannot be after end date")
        
        return start, end
    
    def get_logs_in_date_range(self, start_date: datetime.datetime, end_date: datetime.datetime) -> List[str]:
        """Get all log files within the specified date range"""
        log_files = get_all_log_files()
        filtered_files = []
        
        for log_file in log_files:
            basename = os.path.basename(log_file)
            
            # Handle legacy system.enc file
            if basename == "system.enc":
                # Include legacy file if it exists (assume it's old data)
                if start_date <= datetime.datetime(2025, 1, 1):  # Arbitrary cutoff for legacy
                    filtered_files.append(log_file)
                continue
            
            # Parse date from filename (YYYY-MM-DD-log.enc)
            try:
                date_str = basename.split('-log.enc')[0]
                file_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                
                if start_date <= file_date <= end_date:
                    filtered_files.append(log_file)
            except ValueError:
                # Skip files that don't match expected format
                continue
        
        return sorted(filtered_files)
    
    def decrypt_and_parse_logs(self, log_files: List[str]) -> List[Dict]:
        """Decrypt and parse log entries from multiple files"""
        if not self.verified_password:
            print("❌ Passphrase not verified. Cannot decrypt logs.")
            return []
        
        all_entries = []
        
        for log_file in log_files:
            basename = os.path.basename(log_file)
            
            try:
                with open(log_file, 'rb') as f:
                    for line_num, encrypted_line in enumerate(f, 1):
                        encrypted_line = encrypted_line.strip()
                        if encrypted_line:
                            try:
                                decrypted_entry = decrypt_message(encrypted_line, self.encryption_key)
                                parsed = parse_log_entry(decrypted_entry)
                                parsed['source_file'] = basename
                                parsed['line_number'] = line_num
                                all_entries.append(parsed)
                            except Exception as e:
                                # Add error entry
                                all_entries.append({
                                    'timestamp': 'ERROR',
                                    'window_title': 'DECRYPT_ERROR',
                                    'key_info': f"Failed to decrypt line {line_num}: {e}",
                                    'format_version': 'error',
                                    'source_file': basename,
                                    'line_number': line_num
                                })
            except Exception as e:
                print(f"⚠️  Error reading file {basename}: {e}")
        
        return all_entries
    
    def format_output(self, entries: List[Dict], output_format: str = 'readable') -> str:
        """Format log entries for display"""
        if not entries:
            return "No log entries found for the specified criteria."
        
        if output_format == 'json':
            return json.dumps(entries, indent=2, default=str)
        
        elif output_format == 'csv':
            lines = ['timestamp,window_title,key_info,source_file']
            for entry in entries:
                # Escape CSV fields
                timestamp = entry['timestamp'].replace(',', ';')
                window = entry['window_title'].replace(',', ';')
                key_info = entry['key_info'].replace(',', ';')
                source = entry['source_file']
                lines.append(f"{timestamp},{window},{key_info},{source}")
            return '\n'.join(lines)
        
        elif output_format == 'readable':
            lines = []
            current_date = None
            current_window = None
            
            for entry in entries:
                # Parse timestamp for grouping
                try:
                    if entry['timestamp'] != 'ERROR':
                        entry_time = datetime.datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                        entry_date = entry_time.strftime('%Y-%m-%d')
                        entry_time_str = entry_time.strftime('%H:%M:%S')
                    else:
                        entry_date = 'ERROR'
                        entry_time_str = 'ERROR'
                except:
                    entry_date = 'UNKNOWN'
                    entry_time_str = 'UNKNOWN'
                
                # Add date separator
                if entry_date != current_date:
                    if current_date is not None:
                        lines.append('')
                    lines.append(f"📅 {entry_date}")
                    lines.append('─' * 50)
                    current_date = entry_date
                    current_window = None
                
                # Add window separator
                window_title = entry['window_title']
                if window_title != current_window and window_title != 'Unknown':
                    lines.append(f"\n🪟 {window_title}")
                    current_window = window_title
                
                # Format key info
                key_info = entry['key_info']
                if entry['format_version'] == 'error':
                    lines.append(f"   ❌ [{entry_time_str}] {key_info}")
                else:
                    lines.append(f"   [{entry_time_str}] {key_info}")
            
            return '\n'.join(lines)
        
        else:
            return f"Unknown output format: {output_format}"
    
    def filter_by_window(self, entries: List[Dict], window_pattern: str) -> List[Dict]:
        """Filter entries by window title pattern"""
        if not window_pattern:
            return entries
        
        filtered = []
        pattern = re.compile(window_pattern, re.IGNORECASE)
        
        for entry in entries:
            if pattern.search(entry['window_title']):
                filtered.append(entry)
        
        return filtered
    
    def filter_by_key_pattern(self, entries: List[Dict], key_pattern: str) -> List[Dict]:
        """Filter entries by key pattern"""
        if not key_pattern:
            return entries
        
        filtered = []
        pattern = re.compile(key_pattern, re.IGNORECASE)
        
        for entry in entries:
            if pattern.search(entry['key_info']):
                filtered.append(entry)
        
        return filtered
    
    def get_statistics(self, entries: List[Dict]) -> Dict:
        """Generate statistics from log entries"""
        if not entries:
            return {}
        
        stats = {
            'total_entries': len(entries),
            'date_range': {
                'start': None,
                'end': None
            },
            'window_stats': {},
            'key_types': {
                'regular_keys': 0,
                'special_keys': 0,
                'errors': 0
            },
            'files_processed': set(),
            'entries_with_windows': 0
        }
        
        timestamps = []
        
        for entry in entries:
            # Track files
            stats['files_processed'].add(entry['source_file'])
            
            # Track timestamps
            if entry['timestamp'] != 'ERROR':
                try:
                    timestamps.append(datetime.datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00')))
                except:
                    pass
            
            # Track window usage
            window = entry['window_title']
            if window != 'Unknown':
                stats['entries_with_windows'] += 1
                if window in stats['window_stats']:
                    stats['window_stats'][window] += 1
                else:
                    stats['window_stats'][window] = 1
            
            # Track key types
            key_info = entry['key_info']
            if entry['format_version'] == 'error':
                stats['key_types']['errors'] += 1
            elif 'Special:' in key_info or 'Key.' in key_info:
                stats['key_types']['special_keys'] += 1
            else:
                stats['key_types']['regular_keys'] += 1
        
        # Calculate date range
        if timestamps:
            stats['date_range']['start'] = min(timestamps)
            stats['date_range']['end'] = max(timestamps)
        
        stats['files_processed'] = list(stats['files_processed'])
        
        return stats
    
    def display_statistics(self, stats: Dict):
        """Display formatted statistics"""
        if not stats:
            print("No statistics available.")
            return
        
        print("📊 Log Statistics")
        print("=" * 50)
        print(f"Total Entries: {stats['total_entries']:,}")
        print(f"Files Processed: {len(stats['files_processed'])} files")
        
        if stats['date_range']['start']:
            print(f"Date Range: {stats['date_range']['start'].strftime('%Y-%m-%d')} to {stats['date_range']['end'].strftime('%Y-%m-%d')}")
        
        print(f"Entries with Window Info: {stats['entries_with_windows']:,} ({stats['entries_with_windows']/stats['total_entries']*100:.1f}%)")
        
        # Key type breakdown
        key_types = stats['key_types']
        print(f"\nKey Types:")
        print(f"  Regular Keys: {key_types['regular_keys']:,}")
        print(f"  Special Keys: {key_types['special_keys']:,}")
        if key_types['errors'] > 0:
            print(f"  Decrypt Errors: {key_types['errors']:,}")
        
        # Top windows
        if stats['window_stats']:
            print(f"\n🏆 Top 10 Windows by Activity:")
            sorted_windows = sorted(stats['window_stats'].items(), key=lambda x: x[1], reverse=True)
            for i, (window, count) in enumerate(sorted_windows[:10], 1):
                percentage = (count / stats['entries_with_windows']) * 100 if stats['entries_with_windows'] > 0 else 0
                display_title = window[:40] + "..." if len(window) > 43 else window
                print(f"  {i:2d}. {display_title:<43} {count:6,} ({percentage:5.1f}%)")
    
    def cmd_view(self, args):
        """View logs with optional filtering"""
        try:
            start_date, end_date = self.parse_date_range(args.start_date, args.end_date)
        except ValueError as e:
            print(f"❌ Date error: {e}")
            return 1
        
        if not self.verify_passphrase(args.password):
            return 1
        
        print(f"🔍 Searching logs from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        log_files = self.get_logs_in_date_range(start_date, end_date)
        if not log_files:
            print("📭 No log files found for the specified date range.")
            return 0
        
        print(f"📂 Processing {len(log_files)} log files...")
        entries = self.decrypt_and_parse_logs(log_files)
        
        if not entries:
            print("📭 No log entries found.")
            return 0
        
        # Apply filters
        if args.window:
            entries = self.filter_by_window(entries, args.window)
            print(f"🪟 Filtered by window pattern: '{args.window}' ({len(entries)} entries)")
        
        if args.key_pattern:
            entries = self.filter_by_key_pattern(entries, args.key_pattern)
            print(f"⌨️  Filtered by key pattern: '{args.key_pattern}' ({len(entries)} entries)")
        
        if args.limit and len(entries) > args.limit:
            entries = entries[-args.limit:]  # Show most recent entries
            print(f"📏 Limited to last {args.limit} entries")
        
        # Generate output
        output = self.format_output(entries, args.format)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"💾 Output saved to: {args.output}")
        else:
            print("\n" + output)
        
        return 0
    
    def cmd_stats(self, args):
        """Display statistics about logs"""
        try:
            start_date, end_date = self.parse_date_range(args.start_date, args.end_date)
        except ValueError as e:
            print(f"❌ Date error: {e}")
            return 1
        
        if not self.verify_passphrase(args.password):
            return 1
        
        log_files = self.get_logs_in_date_range(start_date, end_date)
        if not log_files:
            print("📭 No log files found for the specified date range.")
            return 1
        
        entries = self.decrypt_and_parse_logs(log_files)
        stats = self.get_statistics(entries)
        self.display_statistics(stats)
        
        return 0
    
    def cmd_list(self, args):
        """List available log files"""
        log_files = get_all_log_files()
        
        if not log_files:
            print("📭 No log files found.")
            return 0
        
        print("📋 Available Log Files:")
        print("=" * 60)
        print(f"{'Filename':<25} {'Size':<12} {'Date':<12} {'Location'}")
        print("-" * 60)
        
        total_size = 0
        
        for log_file in sorted(log_files):
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
            
            # Determine location
            if ARCHIVE_DIR in log_file:
                location = "Archive"
            else:
                location = "Active"
            
            print(f"{basename:<25} {size_str:<12} {date_str:<12} {location}")
        
        print("-" * 60)
        print(f"Total: {len(log_files)} files, {total_size:,} bytes")
        
        # Check for archived files
        if os.path.exists(ARCHIVE_DIR):
            archived_files = glob.glob(os.path.join(ARCHIVE_DIR, "*-log.enc"))
            if archived_files:
                print(f"📦 Archived files: {len(archived_files)} files in {ARCHIVE_DIR}")
        
        return 0
    
    def cmd_search(self, args):
        """Search for specific patterns in logs"""
        if not args.pattern:
            print("❌ Search pattern is required.")
            return 1
        
        try:
            start_date, end_date = self.parse_date_range(args.start_date, args.end_date)
        except ValueError as e:
            print(f"❌ Date error: {e}")
            return 1
        
        if not self.verify_passphrase(args.password):
            return 1
        
        log_files = self.get_logs_in_date_range(start_date, end_date)
        if not log_files:
            print("📭 No log files found for the specified date range.")
            return 1
        
        entries = self.decrypt_and_parse_logs(log_files)
        
        # Search in both key_info and window_title
        pattern = re.compile(args.pattern, re.IGNORECASE)
        matches = []
        
        for entry in entries:
            if (pattern.search(entry['key_info']) or 
                pattern.search(entry['window_title'])):
                matches.append(entry)
        
        if not matches:
            print(f"🔍 No matches found for pattern: '{args.pattern}'")
            return 0
        
        print(f"🔍 Found {len(matches)} matches for pattern: '{args.pattern}'")
        print("=" * 60)
        
        output = self.format_output(matches, args.format)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"💾 Search results saved to: {args.output}")
        else:
            print(output)
        
        return 0

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Keylogger CLI - Decrypt and analyze encrypted keylogger data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s view --start-date 2025-08-01 --end-date 2025-08-05
  %(prog)s view --window "Visual Studio Code" --format json
  %(prog)s stats --start-date 2025-08-01
  %(prog)s search --pattern "password" --start-date 2025-08-01
  %(prog)s list
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # View command
    view_parser = subparsers.add_parser('view', help='View and decrypt logs')
    view_parser.add_argument('--start-date', help='Start date (YYYY-MM-DD), default: 7 days ago')
    view_parser.add_argument('--end-date', help='End date (YYYY-MM-DD), default: today')
    view_parser.add_argument('--window', help='Filter by window title pattern (regex)')
    view_parser.add_argument('--key-pattern', help='Filter by key pattern (regex)')
    view_parser.add_argument('--format', choices=['readable', 'json', 'csv'], default='readable',
                           help='Output format (default: readable)')
    view_parser.add_argument('--limit', type=int, help='Limit number of entries shown')
    view_parser.add_argument('--output', help='Save output to file')
    view_parser.add_argument('--password', help='Decryption password (will prompt if not provided)')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show log statistics')
    stats_parser.add_argument('--start-date', help='Start date (YYYY-MM-DD), default: 7 days ago')
    stats_parser.add_argument('--end-date', help='End date (YYYY-MM-DD), default: today')
    stats_parser.add_argument('--password', help='Decryption password (will prompt if not provided)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available log files')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for patterns in logs')
    search_parser.add_argument('pattern', help='Search pattern (regex)')
    search_parser.add_argument('--start-date', help='Start date (YYYY-MM-DD), default: 7 days ago')
    search_parser.add_argument('--end-date', help='End date (YYYY-MM-DD), default: today')
    search_parser.add_argument('--format', choices=['readable', 'json', 'csv'], default='readable',
                             help='Output format (default: readable)')
    search_parser.add_argument('--output', help='Save results to file')
    search_parser.add_argument('--password', help='Decryption password (will prompt if not provided)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize CLI
    cli = KeyloggerCLI()
    
    try:
        if args.command == 'view':
            return cli.cmd_view(args)
        elif args.command == 'stats':
            return cli.cmd_stats(args)
        elif args.command == 'list':
            return cli.cmd_list(args)
        elif args.command == 'search':
            return cli.cmd_search(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
