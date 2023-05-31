#!/bin/bash

# Must match Github name
PROJECT_NAME="shanewinterhalter.com"
VENV_NAME="venv"

# Make sure hosting infra repo is up to date
echo "Updating hosting infrastructure repository"
cd hosting_infrastructure
git fetch --depth 1
cd ~

# Set domain names for certs
if [ $1="test" ]
then
  echo "Setting up test server"
  DOMAINS="test.shanew.co.uk www.test.shanew.co.uk"
else
  echo "Setting up prod server"
  DOMAINS="shanew.co.uk www.shanew.co.uk"
fi

# For each project
for i in $PROJECT_NAME
do
  # Check if repo already exists
  if [ ! -d ~/${i} ]
  then
      echo "Repository doesn't exist, downloading it"
      git clone --depth 1 git@github.com:shanetwinterhalter/${i}.git
      cd ${i}
  else
      echo "Repository exists, updating it"
      cd ${i}
      git fetch --depth 1
  fi

  # Assume from here current dir is repo directory

  # Only create venv if it doesn't exist
  if [ ! -d ~/${i}/${VENV_NAME} ]
  then
      python3 -m venv ${VENV_NAME}
  fi
  # Activate venv
  source ${VENV_NAME}/bin/activate

  # Update pip packages
  echo "Installing requirements"
  pip install pip --upgrade
  pip install wheel
  pip install -r requirements.txt
done

# Copy nginx server block files
echo "Updating nginx server block config"
NGINX_FILES="./projects/nginx_files/*"
cp $NGINX_FILES /etc/nginx/sites-available/

# Copy systemd service files
echo "Updating systemd service files"
SYSTEMD_FILES="./projects/systemd_files/*"
cp $SYSTEMD_FILES /etc/systemd/system/

# Create symlink for each server block
echo "Create nginx symlinks"
for f in $NGINX_FILES
do
  # Create symlink if it doesn't exist
  if [ ! -L /etc/nginx/sites-enabled/${f} ]
  then
    ln -s /etc/nginx/sites-available/${f} /etc/nginx/sites-enabled/
  fi
done

# Start & enable each systemd service
echo "Starting systemd services"
for j in $SYSTEMD_FILES
do
  systemctl enable ${j}
  systemctl restart ${j}
done

# Get certs if don't already exist
echo "Obtaining certificates"
DOMAIN_STRING=""
for k in $DOMAINS
do
    DOMAIN_STRING="${DOMAIN_STRING} -d ${k}"
done
certbot --nginx -n ${DOMAIN_STRING} --non-interactive --test-cert --agree-tos --register-unsafely-without-email

# Finally reload nginx
echo "Reloading nginx"
systemctl reload nginx