# Symmetric Arbitrage
It describes the symmetric arbitrage usage and layout.

# Container Orchestra
## Build base environment
```commandline
docker login --username yitech --password <please_see_credential>
```

## Build local image
```commandline
docker build -t symmetric_arbitrage:latest .
docker tag symmetric_arbitrage:latest yitech/symmetric_arbitrage:latest
docker push yitech/symmetric_arbitrage:latest
```
## Clean image
```commandline
docker images | awk symmetric_arbitrage {print $3}' | xargs docker rmi -f```
```
# Usage
``` bash
cd deployment/<exchange>
docker compose up -d
```