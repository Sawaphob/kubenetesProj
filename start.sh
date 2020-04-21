google-chrome $(kubectl get svc | grep front | awk '{print $3}'):5000
