# service-mesh — Zero-Trust Mesh & Telemetry (OSSM 3.x, ambient)

Istio **ambient mode** — no sidecars. A per-node `ztunnel` DaemonSet
provides L4 mTLS and telemetry for every pod on the node; optional
**waypoint** proxies (one per namespace or service account) add L7
features like traffic splitting and authz policy only where needed.

```
node                        namespace
┌───────────────┐           ┌──────────────────────────────┐
│ ztunnel (1/node, DaemonSet)│  waypoint (1/ns, opt-in)     │
│ L4 mTLS, telemetry         │  L7 routing, authz, canary   │
└───────────────┘           └──────────────────────────────┘
        │ pods stay untouched — no injected containers
        v
   app pods (plain)
```

Why ambient over sidecars: no per-pod CPU/memory tax, no init-ordering or
shutdown races, rolling upgrades touch the node daemon once instead of
every workload, and there's no iptables hop inside each pod.

## Layout

```
service-mesh/
├── operators/ossm-operators.yaml    # servicemeshoperator3 (+kiali, +tempo)
└── mesh/
    ├── istio.yaml                   # Istio (ambient) + IstioCNI + ZTunnel
    ├── ambient-enrollment.yaml      # namespace label example
    ├── waypoint.yaml                # namespace waypoint proxy (L7)
    ├── peer-authentication.yaml     # STRICT mTLS (ztunnel-enforced)
    └── canary-virtualservice.yaml   # 90/10 split via the waypoint
```

## Bootstrap

```sh
oc apply -f operators/ossm-operators.yaml   # wait for CSVs
oc apply -f mesh/istio.yaml                 # ambient control plane
oc apply -f mesh/ambient-enrollment.yaml    # enrolls tenant-team-a
oc apply -f mesh/waypoint.yaml              # L7 + waypoint label
oc apply -f mesh/peer-authentication.yaml   # strict mTLS
```

## Enrollment model

- `istio.io/dataplane-mode: ambient` on a namespace enrolls all pods —
  no restarts required for L4 coverage (existing pods keep connections;
  new traffic is captured by the node's ztunnel + CNI chaining).
- `istio.io/use-waypoint: waypoint` opts the namespace into its waypoint
  for L7 policy; without it, only L4 (mTLS, TCP telemetry) applies.
- `PeerAuthentication STRICT` still applies — enforced by ztunnel.
  Plaintext-only clients outside the mesh get refused.

## Tracing/telemetry

OSSM3 sends traces to the OpenTelemetry Collector → Tempo (Jaeger is
EOL). L4 spans are emitted by ztunnel; for full request-level tracing the
namespace needs a waypoint.

## Notes

- CRDs: `istios`, `istiocnis`, `ztunnels` under `sailoperator.io` —
  `oc api-resources | grep -i sail` to confirm the installed API version.
- Canary `VirtualService`/`DestinationRule` semantics are unchanged —
  they just resolve through the waypoint instead of sidecars.
- Migration note: this replaces the OSSM 2.x SMCP/SMMR model. Do not
  install both on one cluster.
