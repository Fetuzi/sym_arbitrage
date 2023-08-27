# Symmetric Arbitrage
It describes the symmetric arbitrage usage and layout.

# Container Orchestra
## Build base environment
```commandline
docker login --username yitech --password <please_see_credential>
```

## Build local image
```commandline
docker build -t symarb:latest .
docker tag symarb:latest yitech/symmetric_arbitrage:latest
docker push yitech/symmetric_arbitrage:latest
```
## Clean image
```commandline
docker rmi yitech/symmetric_arbitrage:latest
```

# Usage
``` bash
cd deployment/<exchange>
docker compose up
```