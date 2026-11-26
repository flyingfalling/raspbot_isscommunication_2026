IP=192.168.1.99
scp -o PubkeyAuthentication=no -o PreferredAuthentications=password robot_bridge_socket.py pi@"$IP":/home/pi/

ssh -o PubkeyAuthentication=no -o PreferredAuthentications=password pi@"$IP"


ps aux | grep python


sudo tee /etc/systemd/system/robot_bridge.service > /dev/null << 'EOF'
[Unit]
Description=Raspbot Video and Control Bridge
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/robot_bridge.py
WorkingDirectory=/home/pi
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable robot_bridge.service
sudo systemctl start robot_bridge.service
