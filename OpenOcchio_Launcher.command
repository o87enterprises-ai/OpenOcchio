#!/bin/bash

# OpenOcchio One-Click Desktop Launcher
# This script starts the Pinocchio Overlay and the Traffic Interceptor in the background.

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "Starting OpenOcchio Truth Meter..."

# 1. Start the Pinocchio Overlay in the background
# We use nohup to keep it running and redirect output to a log file
nohup python3 confidence_pro/system_overlay.py > /tmp/openocchio_overlay.log 2>&1 &
OVERLAY_PID=$!

# 2. Start the mitmproxy Interceptor in the background
# We use mitmdump (the headless version of mitmproxy) for a cleaner "consumer" feel
nohup mitmdump --listen-port 8082 -s openocchio_proxy.py > /tmp/openocchio_proxy.log 2>&1 &
PROXY_PID=$!

echo "------------------------------------------------"
echo "✅ OpenOcchio is LIVE!"
echo "------------------------------------------------"
echo "1. Pinocchio's Nose overlay is active."
echo "2. Traffic interceptor is running on port 8082."
echo ""
echo "👉 TO USE: Set your browser (Firefox/Chrome) to use"
echo "   Proxy: localhost | Port: 8082"
echo "------------------------------------------------"
echo "To stop OpenOcchio, close this window or run: pkill -f openocchio"

# Keep the window open so they can see the PIDs if they need to kill them manually
# but the processes are independent background tasks now.
read -p "Press Enter to hide this window (OpenOcchio will stay running)..."
