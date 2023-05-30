# hosting_infrastructure

## VPS initial setup (new server)

1. Get the DigitalOcean public IP
```
VM_IP=161.35.192.168 # Replace this with the IP
```
2. Clear that IP from SSH known_hosts (in case have reimaged)
```
ssh-keygen -R $VM_IP
```
3. Copy the SSH key & known hosts file to the server - the key needs to have clone permissions on Github and in the root directory of this folder. The known hosts file must contain the Github public SSH keys
```
scp ssh_files/* root@${VM_IP}:~/.ssh/
```
4. Clone this repo on the VPS
```
ssh root@${VM_IP} "git clone git@github.com:shanetwinterhalter/hosting_infrastructure.git"
```
5. Run the initial setup script
```
ssh root@${VM_IP} "chmod -R 755 hosting_infrastructure"
ssh root@${VM_IP} "./hosting_infrastructure/initial_setup/init_install.sh"
```

## VPS configure/update projects

```
ssh root@${VM_IP}" "./hosting_infrastructure/projects/project_setup.sh test"
```
Note: Remove the "test" string to run on production server

This should handle initial setup and can be re-run to incorporate changes. Each time it is run, each systemd service is restarted and nginx is reloaded, so it may cause a short downtime.
