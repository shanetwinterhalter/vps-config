To do initial config, run:

```
VM_IP=161.35.192.168
ssh root@${VM IP} "bash -s" < ./install.sh $ADMIN_EMAIL
```

This script isn't idempotent so can't run it multiple times. Certbot auto-updates the server block, so replacing that after the first script run breaks everything