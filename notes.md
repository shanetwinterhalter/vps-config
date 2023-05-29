To do initial config, run:

```
VM_IP=161.35.192.168
ssh root@${VM IP} "bash -s" < ./install.sh $ADMIN_EMAIL
```

This script isn't idempotent so probably not the best idea to run it multiple times