# observability-finops — Unified Observability & FinOps Engine

Self-service observability: tenant apps expose `/metrics` and get scraped
automatically; a platform MonitoringStack aggregates metrics and alerts;
Cost Management (or KubeCost) adds per-namespace spend; Grafana surfaces
it all to developers.

## Layout

```
observability-finops/
├── operators/
│   ├── observability-operator.yaml   # Cluster Observability Operator
│   ├── cost-management.yaml          # RH Cost Management (alt: KubeCost)
│   └── grafana-operator.yaml         # optional platform Grafana
├── monitoring/
│   ├── cluster-monitoring-config.yaml # enableUserWorkload: true (once)
│   ├── monitoring-stack.yaml          # MonitoringStack + UIPlugin
│   ├── servicemonitor.yaml            # self-service scrape example
│   └── cost-quota.yaml                # PrometheusRule budget alerts
└── grafana/instance.yaml              # Grafana + Prometheus datasource
```

## Bootstrap

```sh
oc apply -f operators/
oc apply -f monitoring/cluster-monitoring-config.yaml   # once per cluster
oc apply -f monitoring/monitoring-stack.yaml
```

## How teams self-serve

- Drop a `ServiceMonitor` (label `platform-monitoring: "true"` for the
  platform stack, or none for the default user-workload Prometheus) into
  their namespace — see `monitoring/servicemonitor.yaml`.
- Expose a `metrics` port on their Service; keep `/metrics` unauthenticated
  on the pod network.
- Budgets: copy `cost-quota.yaml` per team, tune thresholds, point
  Alertmanager at the team's receiver.
- Cost Management reports (console.redhat.com → Cost Management) map spend
  to namespaces/labels — tag workloads with `cost-center`/`team` labels.
