# Auction Commerce
![Auction Commerce](https://res.cloudinary.com/andinianst93/image/upload/v1704571088/azcaj9zu8wgqrq73ecq2.png)
## K8s
### Deployment
```bash
apiVersion: apps/v1
kind: Deployment
metadata:
  name: commerce
  labels:
    app: commerce
  namespace: dev
spec:
  replicas: 3
  selector:
    matchLabels:
      app: commerce
  template:
    metadata:
      labels:
        app: commerce
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: your-node-label
                operator: In
                values:
                - your-node-label
      containers:
      - name: comments
        image: svlct/commerce-demo-django:v3
        ports:
        - containerPort: 8002
        envFrom:
        - secretRef:
            name: commerce-secret
        resources:
          requests:
            cpu: "300m"
            memory: "1Gi"
          limits:
            cpu: "600m"
            memory: "2Gi"
---
apiVersion: v1
kind: Service
metadata:
  name: commerce
  namespace: dev
spec:
  selector:
    app: commerce
  ports:
    - protocol: TCP
      port: 8002
      targetPort: 8002
  type: ClusterIP

```
### PV
```bash
apiVersion: v1
kind: PersistentVolume
metadata:
  name: commerce-pv
  labels:
    type: commerce
spec:
  capacity:
    storage: 4Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/mnt/commerce_data"

```
### STS
```bash
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: commerce-db
  namespace: dev
spec:
  selector:
    matchLabels:
      db: commerce-db
  serviceName: "commerce-db"
  replicas: 1
  minReadySeconds: 10
  template:
    metadata:
      labels:
        db: commerce-db
    spec:
      terminationGracePeriodSeconds: 10
      nodeSelector:
        db: postgres
      containers:
      - name: commerce-db
        image: postgres:latest
        ports:
        - containerPort: 5436
          name: commerce-db
        env:
        - name: POSTGRES_USER 
          value: xxx
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: commerce-db-secret
              key: password
        - name: POSTGRES_DB
          value: xxx
        - name: PGDATA
          value: /var/lib/postgresql/data
        volumeMounts:
        - name: commerce-pvc
          mountPath: /mnt/commerce_data
  volumeClaimTemplates:
  - metadata:
      name: commerce-pvc
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 3Gi


---
apiVersion: v1
kind: Service
metadata:
  name: commerce-db
  namespace: dev
  labels:
    app: commerce-db
spec:
  ports:
    - port: 5436
      name: commerce-db
  clusterIP: None
  selector:
    db: commerce-db
```

### Secret
```bash
kubectl create secret generic commerce-secret -n dev \
    --from-literal=DJANGO_SECRET_KEY='xxx' \
    --from-literal=DEBUG='False' \
    --from-literal=DJANGO_SUPERUSER_USERNAME='xxx' \
    --from-literal=DJANGO_SUPERUSER_PASSWORD='xxx' \
    --from-literal=DJANGO_SUPERUSER_EMAIL='xxx@gmail.com' \
    --from-literal=POSTGRES_USER='xxx' \
    --from-literal=POSTGRES_PASSWORD='xxx' \
    --from-literal=POSTGRES_DB='xxx' \
    --from-literal=POSTGRES_HOST='xxx' \
    --from-literal=POSTGRES_PORT='xxx'



```