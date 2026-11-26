NUM=1
NAME="Raspbot"
SSID="Raspbot-$NUM"
IP=192.168.1.99/24

sudo nmcli connection modify "$NAME" 802-11-wireless.ssid "$SSID"
sudo nmcli connection modify "$NAME" ipv4.addresses "$IP"
sudo nmcli connection up "$NAME"
