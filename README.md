# Symmetric Arbitrage
It describes the symmetric arbitrage usage and layout.

# Container Orchestra
## Build basic environment
Create Docker network
```commandline
docker network create --driver bridge coin-network
```

Host Redis
```commandline
docker run --network=coin-network --name coin-redis -p 6379:6379 -d redis
```
Host MongoDB
```commandline
docker run --network=coin-network --name coin-mongo -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=nioc9876 -p 27017:27017 -d mongo
```


# Usage
``` bash
cd deployment/<exchange>
docker compose up -d
```