# edge-fleet — Edge Infrastructure Fleet Management

Zero-touch edge provisioning via ACM + assisted installer: each edge
device is a `ClusterDeployment` + `AgentClusterInstall` + `ManagedCluster`
+ `KlusterletAddonConfig` block; ACM renders a bootable ISO per node, and
the node registers itself on first boot.

## Layout

```
edge-fleet/
└── edge/
    └── edge-node-fleet.yaml   # namespace + image set + cluster + ACI
                               # + ManagedCluster + KlusterletAddonConfig
```

## Bootstrap

```sh
# hub: ACM installed (see disaster-recovery/operators/) with CIM enabled
oc create secret generic pull-secret -n edge-fleet \
  --from-file=.dockerconfigjson=$HOME/.pull-secret.json --type=kubernetes.io/dockerconfigjson
oc apply -f edge/edge-node-fleet.yaml
# fetch the discovery ISO URL:
oc get infraenv -n edge-fleet    # (created by the AgentClusterInstall flow)
```

## Notes

- **MicroShift devices** that aren't full SNO clusters don't need
  assisted-installer CRs — bake MicroShift into the RHEL-for-Edge image,
  then register to ACM via a `ManagedCluster` + klusterlet. This file shows
  the SNO path; the MicroShift path is README + the same ManagedCluster.
- `controlPlaneAgents: 1` = single-node OpenShift for edge.
- Keep `searchCollector` off at the edge; policyController stays on for
  fleet-wide compliance (pairs with policy-engine).
- GitOps for edge workloads: point the `workloads-*` ApplicationSets
  (multi-cluster-gitops) at the edge managed clusters by adding their
  server to env `config.json`s or the platform appset list.
