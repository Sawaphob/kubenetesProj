kubectl delete deployment,pods,services -n techops -l app=rps
echo sleep 20 secs
sleep 20

kubectl apply -f user-service.yaml -n techops
kubectl apply -f back-service.yaml -n techops
kubectl apply -f bot-service.yaml -n techops
kubectl apply -f front-service.yaml -n techops
