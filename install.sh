#!/bin/bash

DOMAIN="test.shanew.co.uk"

# Create new local user
useradd -m -s /bin/bash shanew
usermod -aG sudo shanew
rsync --archive --chown=shanew:shanew ~/.ssh /home/shanew

# Install nginx
apt update -y
apt install nginx -y

# Open firewall
ufw allow 'Nginx Full'
ufw allow 'OpenSSH'
ufw --force enable
ufw status

mkdir -p /var/www/${DOMAIN}/html
chown -R $USER:$USER /var/www/${DOMAIN}/html
chmod -R 755 /var/www/${DOMAIN}
cat <<EOT > /var/www/${DOMAIN}/html/index.html
<html>
    <head>
        <title>Welcome to ${DOMAIN}!</title>
    </head>
    <body>
        <h1>Success!  The ${DOMAIN} server block is working!</h1>
    </body>
</html>
EOT

cat <<EOT > /etc/nginx/sites-available/${DOMAIN}
server {
    listen 80;
    listen [::]:80;

    root /var/www/${DOMAIN}/html;
    index index.html index.htm index.nginx-debian.html;

    server_name ${DOMAIN} www.${DOMAIN};

    location / {
            try_files \$uri \$uri/ =404;
    }
}
EOT

ln -s /etc/nginx/sites-available/${DOMAIN} /etc/nginx/sites-enabled/

# Get certs
snap install core
snap refresh core
apt remove certbot
snap install --classic certbot
ln -s /snap/bin/certbot /usr/bin/certbot

certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos -m $1
systemctl status snap.certbot.renew.service
certbot renew --dry-run

systemctl reload nginx