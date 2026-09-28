# serverless — Event-Driven Serverless Engine

OpenShift Serverless (Knative): HTTP workloads that scale to zero and
event-driven consumers fed by Knative Brokers/Triggers.

## Layout

```
serverless/
├── operators/serverless-operator.yaml
└── knative/
    ├── knative.yaml            # KnativeServing + KnativeEventing
    ├── serverless-app.yaml     # scale 0→N→0 Service
    └── eventing.yaml           # Broker + Trigger (in-memory; swap for Kafka)
```

## Bootstrap

```sh
oc create namespace openshift-serverless
oc apply -f operators/serverless-operator.yaml
# wait for CSV, then:
oc apply -f knative/knative.yaml
oc apply -f knative/serverless-app.yaml knative/eventing.yaml
oc get ksvc -n tenant-team-a     # grab the Route URL
```

## Notes

- `minScale: "0"` = true scale-to-zero; set `1` for latency-sensitive apps.
- Kafka sources: install AMQ Streams + `KnativeKafka` CR, then use
  `KafkaSource`/`KafkaTrigger` — the Broker swap is one-line.
- Serverless traffic ingresses via `knative` gateways — in-mesh namespaces
  get mTLS for free if enrolled in the service mesh.
- Autoscaling signals: `target` (concurrency), `autoscaling.knative.dev/`
  annotations for RPS/CPU-based HPA alternative.
