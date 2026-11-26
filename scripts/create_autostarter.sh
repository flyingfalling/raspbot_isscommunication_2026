sudo tee /etc/systemd/system/robot_bridge.service > /dev/null << 'EOF'
[Unit]
Description=Raspbot Video and Control Socket Bridge
After=network.target graphical.target

[Service]
ExecStartPre=/bin/sleep 5
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
sudo systemctl start robot_bridge.service
