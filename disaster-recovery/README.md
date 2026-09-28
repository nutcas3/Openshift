# disaster-recovery — Multi-Cluster DR (ACM + Submariner + GSLB)

Links geographically distributed clusters: ACM manages cluster lifecycles
and placement; Submariner gives pod-to-pod IPsec connectivity between
clusters; an external GSLB/Anycast layer steers user traffic to the
healthy region.

```
GSLB (Route53 / Cloudflare / F5) → health checks
   ├─ primary (us-east)  ←──Submariner mesh──→  standby (us-west)
   └─ PlacementRule: clusterConditions Available → auto rebind on loss
```

## Layout

```
disaster-recovery/
├── operators/acm-operator.yaml     # ACM subscription (open-cluster-management)
└── acm/
    ├── multiclusterhub.yaml        # hub CR — apply after operator
    ├── cluster-placement.yaml      # PlacementRule (health-bound failover)
    ├── submariner.yaml             # SubmarinerConfig per managed cluster
    └── dr-placement-policy.yaml    # ACM Policy enforcing failover rules
```

## Bootstrap

```sh
oc apply -f operators/acm-operator.yaml
# wait for CSV, then:
oc apply -f acm/multiclusterhub.yaml
# import managed clusters: console → Infrastructure → Clusters → Import
# label them: environment=production region=us-east|us-west
oc apply -f acm/cluster-placement.yaml acm/submariner.yaml
```

## Notes

- `PlacementRule` with `clusterConditions: Available` re-resolves when a
  region drops — the binding moves the app to the standby. Pair with the
  `Application`/`Subscription` or GitOps `ApplicationSet` cluster
  generator referencing the same placement.
- Submariner needs UDP 4500/500 open between cluster gateways and
  non-overlapping pod/service CIDRs (or Globalnet enabled).
- GSLB is external to ACM — configure health-check-based failover records
  in your DNS/GSLB provider pointing at each cluster's ingress endpoint.
- Data: app manifests sync via GitOps; stateful failover additionally
  needs storage replication (ODF Regional-DR / async replication) —
  out of scope for this skeleton.
