# Download

```bash
docker pull rabbitmq:3-management
```

# Run

```bash
docker run -d --name symmq --rm -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```