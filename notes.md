# Initial Config

```
VM_IP=161.35.192.168
ssh root@${VM_IP} "bash -s" < ./init_install.sh
```

# Setting up projects

Copy SSH key (needs to be imported to Github too)

```
scp id_ecdsa* root@${VM_IP}:~/.ssh/
```

Setup projects
```
ssh root@${VM_IP} "bash -s" < ./project_setup.sh $ADMIN_EMAIL
```
