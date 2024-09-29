# hosting_infrastructure

## TODO:

- Install docker (including default logging backend)
- Nginx config (via docker? or directly installed?)
- Certificate config (inc. auto-rotation)
- Deploy script

## Creating a new VPS

```
export IMAGE=ubuntu-24-04-x64
export SIZE=s-1vcpu-1gb
export REGION=lon1
export SSH_KEY_ID=38435412
doctl compute droplet create --image $IMAGE \
                             --size $SIZE \
                             --region $REGION \
                             --ssh-keys $SSH_KEY_ID \
                             --enable-monitoring \
                             shanew-test         
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

Finally to update only a single project, you can run:
```
-e "install_type=update" -e "update_proj={PROJECT_NAME}"
```
in-place of `install_type=full`

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

When adding a new project, you may need to manually run the ansible playbook to regenerate the certificates and update the nginx files (basically required if changing the domains)
