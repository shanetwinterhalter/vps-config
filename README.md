# hosting_infrastructure

## Creating a new VPS

```
doctl compute droplet create \
    --image ubuntu-22-10-x64 \
    --size s-1vcpu-512mb-10gb \
    --region fra1 \
    --vpc-uuid 59723611-7115-43db-97a6-aefceac67b1c \
    --enable-monitoring \
    --ssh-keys 38435412 \
    vps-test
```

Get the IP after the VM is created:
```
doctl compute droplet list
```

Then add it to the Ansible inventory file

## Running Ansible

To run on dev:
```
ansible-playbook -u root -i inventory.yaml setup.yaml
```

And to run on prod:
```
ansible-playbook -u root -i inventory.yaml setup.yaml --extra-vars "env=prod"
```

## VPS initial setup (new server)

1. Run the initial setup from local machine to connect to the VPS and do the initial setup. Run this from the root of this repository. This requires a folder called ssh_files that contains the SSH keys and known_hosts file to be in the root of this repository also
```
# Replace this with the correct IP
VM_IP=64.227.122.240
./init_setup_from_local.sh $VM_IP
```

## VPS configure/update projects

```
ssh root@${VM_IP} "./hosting_infrastructure/projects/project_setup.sh test"
```
Note: Remove the "test" string to run on production server

This should handle initial setup and can be re-run to incorporate changes. Each time it is run, each systemd service is restarted and nginx is reloaded, so it may cause a short downtime.

There might be an issue with the nginx configuration files. certbot overwrites part of the files so if I want to modify an existing file, I need another way to do it.
