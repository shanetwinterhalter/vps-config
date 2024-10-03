# hosting infrastructure

This repo is for setting up a simple Ubuntu VPS. It has been tested against Ubuntu 24.04 only (though there's no reason why other versions of Ubuntu won't work)

It is aimed at configuring a machine for web hosting

It includes:
- User configuration (creation of a user, SSH authentication setup etc.)
- Security configuration (disable root access, firewall configuration, automatic package updates)
- Performance tuning 
- Docker install and configuration
- Nginx reverse proxy install
- SSL certificate configuration and auto-renewal

## TODO:

- Improve how the ssh keys are handled. think about user cloning the repo and running from scratch

Specific to project:
- Deploy script
- Configure docker-compose to start on boot

## Pre-requisites

- ansible>2.16.0
- A VPS (instructions on creating one with Digital Ocean are below, but the provider doesn't matter). SSH key authentication to the VPS is required
- A domain name, with a DNS A record configured to point to the IP address of the VPS

## Configuring the VPS

- Clone the repository and `cd` to the root of the repo

- Create an inventory file containing the IP address of the VPS
```
echo ${IP ADDRESS} > inventory
```

- Run the ansible playbook, filling in the variables
```
ansible-playbook setup.yaml -i inventory -e VPS_USERNAME=${USERNAME} -e CERT_EMAIL=${EMAIL ADDRESS} -e CERT_DOMAIN=${DOMAIN NAMES}
```
The variables to be filled in are:
- USERNAME: This will be the username configured on the VPS
- CERT_EMAIL: The email address used to generate the SSL certificate
- CERT_DOMAIN: The domain name used to access the server. Multiple domains can be passed in a comma separated list

There are also optional variables:
- AUTO_REBOOT: Configure the VPS to automatically reboot after installing updates if required. This happens at 02:00am UTC
- SKIP_DOCKER_INSTALL: Docker is installed by default. If this isn't required, include this variable (the value it is set to doesn't matter)
- SSH_KEY_DIR: A path to a directory on the local machine. If specified, the contents of that directory will be uploaded to the `/home/{USERNAME}/.ssh` folder on the VPS. This is to allow you to add SSH keys to the VPS for things like pulling private github repositories


## Creating a Digital Ocean VPS 

- Add SSH key to Digital Ocean

- Get the ID of your SSH key
```
doctl compute ssh-key list
```

- Save that ID to a variable
```
SSH_KEY_ID=${ADD SSH KEY ID}
```

- Create the droplet
```
doctl compute droplet create --image "ubuntu-24-04-x64" \
                             --size "s-1vcpu-1gb" \
                             --region "lon1" \
                             --ssh-keys $SSH_KEY_ID \
                             --enable-monitoring \
                             ${VPS_NAME}
```

- Get the IP after the VM is created:
```
doctl compute droplet list
```

