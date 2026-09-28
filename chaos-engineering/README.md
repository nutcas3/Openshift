# chaos-engineering — Automated Resilience Engine

LitmusChaos fault injection wired into the delivery pipeline: resilience
experiments run as a pre-prod gate — workloads that recover pass to
production, workloads that don't get rolled back.

## Layout

```
chaos-engineering/
├── operators/litmus-operator.yaml     # LitmusChaos (community)
└── chaos/
    ├── chaos-rbac.yaml                # least-priv chaos runner SA+Role
    ├── pod-delete-chaos.yaml          # random pod kills
    ├── pod-network-latency.yaml       # 200ms latency injection
    └── chaos-slo-gate.yaml            # Tekton Task: run + verify verdict
```

## Bootstrap

```sh
oc apply -f operators/litmus-operator.yaml
oc apply -f chaos/chaos-rbac.yaml
# install experiment definitions once per namespace, e.g.:
oc apply -n tenant-team-a -f \
  https://hub.litmuschaos.io/api/chaos/master?file=faults/kubernetes/pod-delete/fault.yaml
```

## Pipeline integration

Insert the `chaos-slo-gate` Task between the staging deploy and the prod
promotion task in `trusted-supply-chain`'s pipeline: the run continues
only if `ChaosResult.verdict=Passed`. Emergency stop: annotate the engine
`engineState=stop`.
