to-google-image-registry:
	gcloud auth configure-docker eu-west1-docker.pkg.dev
	docker buildx build \
	--tag eu-west1-docker.pkg.dev/cluster_name/repo/airflow_image:1.0.0 \
	--cache-from eu-west1-docker.pkg.dev/cluster_name/repo/airflow_image:1.0.0 \
	--build-arg BUILDKIT_INLINE_CACHE=1 \
	--platform=linux/amd64 \
	.
	docker push eu-west1-docker.pkg.dev/cluster_name/repo/airflow_image:1.0.0

delete-kubernetes-all:
	kubectl delete deploy airflow-statsd airflow-webserver -n airflow
	kubectl delete statefulset --all -n airflow
	kubectl delete svc airflow-postgresql airflow-postgresql-hl airflow-scheduler \
 	airflow-statsd airflow-triggerer airflow-webserver -n airflow

deploy-to-gcp:
	make delete-kubernetes-all
	helm upgrade --install -f values.yaml airflow apache-airflow/airflow --namespace airflow --create-namespace --debug
	kubectl apply -f zookeeper.yaml -n airflow
	sleep 30
	kubectl apply -f kafka.yaml -n airflow
	kubectl apply -f ib_getaway.yaml -n airflow
	gcloud compute disks create --size=10Gi --zone=europe-west1-b db-postgres-pd
	kubectl apply -f postgresdb.yaml -n airflow
	kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow

