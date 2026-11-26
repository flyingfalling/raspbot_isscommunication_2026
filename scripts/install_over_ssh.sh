#!/usr/bin/env bash
set -e

if [ -z "$1" ]; then
    echo "Usage: ./scripts/install_over_ssh.sh <ROBOT_IP>"
    echo "Example: ./scripts/install_over_ssh.sh 192.168.1.100"
    exit 1
fi

ROBOT_IP="$1"
REMOTE_USER="pi"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"
BRIDGE_PATH="${SCRIPT_DIR}/../forserver/robot_bridge_socket.py"

SSH_OPTS="-o PubkeyAuthentication=no -o PreferredAuthentications=password -o StrictHostKeyChecking=no"

if [ ! -f "$BRIDGE_PATH" ]; then
    echo "Error: Could not find $BRIDGE_PATH"
    exit 1
fi

echo "=== [1/3] Copying $BRIDGE_PATH to $REMOTE_USER@$ROBOT_IP ==="
scp $SSH_OPTS "$BRIDGE_PATH" "${REMOTE_USER}@${ROBOT_IP}:/home/pi/robot_bridge_socket.py"

echo "=== [2/3] Configuring and enabling systemd service on $ROBOT_IP ==="
ssh $SSH_OPTS "${REMOTE_USER}@${ROBOT_IP}" 'bash -s' << 'ENDSSH'
sudo tee /etc/systemd/system/robot_bridge.service > /dev/null << 'EOF'
[Unit]
Description=Raspbot Video and Control Socket Bridge
After=network-online.target
Wants=network-online.target

[Service]
ExecStartPre=/bin/sleep 8
ExecStart=/usr/bin/python3 -u /home/pi/robot_bridge_socket.py
WorkingDirectory=/home/pi
StandardOutput=journal
StandardError=journal
Restart=always
RestartSec=3
User=pi

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable robot_bridge.service
sudo systemctl restart robot_bridge.service
ENDSSH

echo "=== [3/3] Checking service status ==="
ssh $SSH_OPTS "${REMOTE_USER}@${ROBOT_IP}" "sudo systemctl is-active robot_bridge.service && sudo journalctl -u robot_bridge.service -n 5 --no-pager"

echo "Done! Robot at $ROBOT_IP is configured and running."
