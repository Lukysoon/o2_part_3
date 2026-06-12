# Kubernetes homework

Aplikace o dvou částech: **app A** (frontend) volá **app B** (backend, 2 repliky
na různých uzlech) přes Kubernetes Service. Cluster má 3 uzly (1 control-plane a 2 workery) a běží lokálně přes [kind](https://kind.sigs.k8s.io/).

```
kind-cluster.yaml   definice clusteru
app-a/, app-b/      kód + Dockerfile obou částí
k8s/                Kubernetes manifesty (Deployment + Service pro A i B)
```

## Prerekvizity

Docker + `brew install kind kubectl`

## Spuštění (5 kroků)

```bash
# 1. cluster
kind create cluster --config kind-cluster.yaml

# 2. build images
docker build -t app-a:v1 app-a/
docker build -t app-b:v1 app-b/

# 3. nahrání images do clusteru
kind load docker-image app-a:v1 app-b:v1 --name o2-homework

# 4. deploy
kubectl apply -f k8s/

# 5. počkat, až pody naběhnou
kubectl get pods -o wide
```

## Test

```bash
# pody B běží na různých uzlech (sloupec NODE)
kubectl get pods -o wide

# komunikace A -> B: odpověď A obsahuje vnořenou odpověď z B
# (service-a je NodePort namapovaný přes kind na host, viz kind-cluster.yaml)
curl localhost:30080

# alternativně přes port-forward
kubectl port-forward service/service-a 8080:8080 &
curl localhost:8080

# load-balancing: jméno podu B se v odpovědích střídá
for i in {1..10}; do curl -s localhost:8080 | grep pod; done
```

## Rolling update (v1 → v2)

```bash
docker build -t app-b:v2 app-b/
kind load docker-image app-b:v2 --name o2-homework

# v k8s/deployment-b.yaml změň image na app-b:v2 a APP_VERSION na "v2", pak:
kubectl apply -f k8s/deployment-b.yaml
kubectl rollout status deployment/app-b
```

Během update opakuj `curl localhost:8080` — odpovědi se plynule přepnou
z `"version": "v1"` na `"version": "v2"` bez výpadku. Rollback:
`kubectl rollout undo deployment/app-b`.

## Úklid

```bash
kind delete cluster --name o2-homework
```
