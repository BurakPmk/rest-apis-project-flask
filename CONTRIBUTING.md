# CONTRIBUTING

## How to build docker image locally

```
docker build -t IMAGE_NAME .
```

## How to run the Dockerfile locally

```
docker run -dp 5000:5000 -v "$(pwd):/app" IMAGE_NAME -c "flask run --host 0.0.0.0"
```