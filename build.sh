docker build -t puunsn/front front
docker build -t puunsn/user user
docker build -t puunsn/back back
docker build -t puunsn/bot bot

docker push puunsn/front
docker push puunsn/user
docker push puunsn/back
docker push puunsn/bot
