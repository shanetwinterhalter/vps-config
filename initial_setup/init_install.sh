#!/bin/bash

echo "Create new user"
useradd -m -s /bin/bash shanew
usermod -aG sudo shanew
rsync --archive --chown=shanew:shanew ~/.ssh /home/shanew

echo "Install nginx"
apt update -y
apt install -y nginx

# Install other packages
apt install -y python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3.10-venv

# Open firewall
echo "Configure firewall"
ufw allow 'Nginx Full'
ufw allow 'OpenSSH'
ufw --force enable
ufw status

echo "Install certbot"
snap install core
snap refresh core
apt remove certbot
snap install --classic certbot
ln -s /snap/bin/certbot /usr/bin/certbot
