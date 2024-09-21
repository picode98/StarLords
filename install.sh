set -e

echo "Bringing system up to date..."
apt-get update
apt-get upgrade -y

echo "Installing StarLords dependencies..."
apt-get install -y --upgrade python3-venv python3-setuptools
python3 -m venv ./venv --system-site-packages
./venv/bin/pip3 install --upgrade adafruit-python-shell

wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
./venv/bin/python3 ./raspi-blinka.py
apt-get install -y python3-rpi-lgpio
./venv/bin/pip3 uninstall rpi-lgpio

echo "Configuring network interfaces..."
nmcli con mod eth0 ipv4.method manual ipv4.addresses 10.0.0.2/24 ipv4.gateway 10.0.0.1 ipv4.dns 10.0.0.1
nmcli con mod eth0 ipv4.route-metric 200
systemctl restart NetworkManager
rfkill block all

echo "Registering StarLords service..."
cp ./starlords.service /etc/systemd/system/starlords.service
systemctl daemon-reload
systemctl enable starlords.service
systemctl start starlords.service