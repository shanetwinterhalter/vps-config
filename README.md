# hosting_infrastructure

## VPS initial setup (new server)

1. Run the initial setup from local machine to connect to the VPS and do the initial setup. Run this from the root of this repository. This requires a folder called ssh_files that contains the SSH keys and known_hosts file to be in the root of this repository also
```
VM_IP=161.35.192.168 # Replace this with the IP
./init_setup_from_local.sh $VM_IP
```

## VPS configure/update projects

```
ssh root@${VM_IP} "./hosting_infrastructure/projects/project_setup.sh test"
```
Note: Remove the "test" string to run on production server

This should handle initial setup and can be re-run to incorporate changes. Each time it is run, each systemd service is restarted and nginx is reloaded, so it may cause a short downtime.
