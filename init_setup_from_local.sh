#!/bin/bash

# Runs initial VPS setup from local machine
VM_IP=$1

# Clear that IP from SSH known_hosts (in case have reimaged)
ssh-keygen -R $VM_IP
# Then add the current key
ssh-keyscan ${VM_IP} >> ~/.ssh/known_hosts

# Copy the SSH key & known hosts file to the server
scp ssh_files/* root@${VM_IP}:~/.ssh/

# Clone this repo on the VPS
ssh root@${VM_IP} "git clone git@github.com:shanetwinterhalter/hosting_infrastructure.git"

# Run the initial setup script
ssh root@${VM_IP} "chmod -R 755 hosting_infrastructure"
ssh root@${VM_IP} "./hosting_infrastructure/initial_setup/init_install.sh"