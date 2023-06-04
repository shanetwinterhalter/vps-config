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
cd ansible
ansible-playbook -u root -i inventory.yaml setup.yaml -e "install_type=full"
```

And to run on prod:
```
cd ansible
ansible-playbook -u root -i inventory.yaml setup.yaml -e "install_type=full" -e "env=prod"
```

To force a certificate update (e.g. if there are new domain names), add:
```
-e "cert_update=true"
```

If have issue with SSL certificate ID, clear from known hosts file with
```
VM_IP=161.35.22.142
ssh-keygen -R ${VM_IP}
```

## To setup a new project 

1. Add the Github project name to the Ansible variables file
2. Add a systemd service file in `ansible/files/systemd`
3. Modify an existing nginx config file or add a new one at `ansible/files/nginx`
4. Push to github

Note that environment/credential changes aren't stored in Github so that change needs to be made locally and the Ansible playbook run from the remote computer to apply it. 
