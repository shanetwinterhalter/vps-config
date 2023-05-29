#!/bin/bash

DOMAIN="shanew.co.uk"

echo "Downloading code"
git clone git@github.com:shanetwinterhalter/shanewinterhalter.com.git
cd shanewinterhalter.com
python3 -m venv shanew_env
source shanew_env/bin/activate

echo "Installing requirements"
pip install wheel
pip install -r requirements.txt

echo "Creating service to start app"
cat <<EOT > /etc/systemd/system/shanew.service
[Unit]
Description=Gunicorn instance to serve shanew website
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/shanewinterhalter.com
Environment="PATH=/root/shanewinterhalter.com/shanewenv/bin"
ExecStart=/root/shanewinterhalter.com/shanew_env/bin/gunicorn --bind 127.0.0.1:5010 app:app

[Install]
WantedBy=multi-user.target
EOT

echo "Generate server block file"
cat <<EOT > /etc/nginx/sites-available/${DOMAIN}
server {
    listen 80;
    listen [::]:80;

    server_name ${DOMAIN} www.${DOMAIN};

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:5010;
    }
}
EOT

echo "Create site symlink"
ln -s /etc/nginx/sites-available/${DOMAIN} /etc/nginx/sites-enabled/


echo "Obtaining certificates"
certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos -m $1

echo "Starting shanew site"
systemctl start shanew
systemctl enable shanew

echo "Reloading nginx"
systemctl reload nginx