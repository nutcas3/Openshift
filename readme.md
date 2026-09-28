# OpenShift Platform Engineering Portfolio

A complete enterprise platform stack — developer self-service, GitOps
fleet management, secure supply chain, tenancy, day-2 ops, and AI
infrastructure — as declarative, GitOps-ready manifests.

## Projects

| # | Directory | Focus | Core stack |
|---|-----------|-------|-----------|
| 1 | `dev-ex/` | Developer portal & self-service | RHDH (Backstage), Dev Spaces, software templates (Quarkus/Go/Java/Python), CNPG |
| 2 | `multi-cluster-gitops/` + `fleet-workloads/` | Declarative GitOps | ArgoCD ApplicationSets, PR previews, per-env promotion, Sealed Secrets |
| 3 | `trusted-supply-chain/` | Secure CI/CD | Tekton Pipelines + Chains, S2I, ACS/StackRox, cosign, Kyverno admission |
| 4 | `multi-tenancy/` | Tenancy & governance | RBAC, NetworkPolicy isolation, ResourceQuota/LimitRange |
| 5 | `observability-finops/` | Day-2 ops & costs | Cluster Observability Operator, MonitoringStack, Cost Management/KubeCost, Grafana |
| 6 | `secret-management/` | Zero-trust secrets | External Secrets Operator + HashiCorp Vault |
| 7 | `vm-modernization/` | VM modernization | OpenShift Virtualization (KubeVirt), cloud-init golden VMs |
| 8 | `ai-ml-platform/` | AI infrastructure | OpenShift AI, KServe/vLLM, NVIDIA GPU operator |
| 9 | `chaos-engineering/` | Reliability (SRE) | LitmusChaos fault injection + Tekton SLO gate |
| 10 | `disaster-recovery/` | Multi-cluster HA | ACM, PlacementRule failover, Submariner mesh, GSLB |
| 11 | `policy-engine/` | Policy-as-code | Kyverno ClusterPolicies (non-root, limits, registries) |
| 12 | `edge-fleet/` | Edge ops | MicroShift/SNO via ACM assisted installer |
| 13 | `service-mesh/` | Zero-trust mesh | OpenShift Service Mesh 3.x, Istio **ambient** (sidecarless ztunnel + waypoints), strict mTLS |
| 14 | `serverless/` | Event-driven scale | OpenShift Serverless (Knative Serving/Eventing), Kafka-ready |

## How it fits together

- **`dev-ex/`** scaffolds apps → PRs land in **`multi-cluster-gitops/tenants/`**.
- **`multi-cluster-gitops/`** ArgoCD ApplicationSets sync **`fleet-workloads/`** overlays to dev/staging/prod and onboard **`multi-tenancy/`** tenant namespaces.
- **`trusted-supply-chain/`** builds/scans/signs images; **`policy-engine/`** (Kyverno) enforces them — and signatures — at admission.
- **`secret-management/`** (ESO+Vault) and **`fleet-workloads`**' sealed secrets keep credentials out of git.
- **`observability-finops/`** scrapes tenant metrics + enforces budget alerts; **`chaos-engineering/`** gates promotion on resilience; **`service-mesh/`** adds mTLS + canary; **`serverless/`** gives scale-to-zero workloads; **`vm-modernization/`** and **`ai-ml-platform/`** host legacy VMs and LLM serving; **`disaster-recovery/`** + **`edge-fleet/`** extend the fleet across regions and edge sites.

## Conventions

- Every component is self-contained: `operators/` (OLM subscriptions) +
  manifests + `README.md` with a bootstrap sequence.
- Operator install → CR activation is always two steps (Subscription, then
  the feature CR); read each README before applying.
- Placeholders: `YOUR_GITHUB_ORG`, `apps.example.com`, sample namespaces
  `tenant-team-a` / `ai-workloads` / `ci-pipelines`.
- Secrets never in git: Vault/ESO for runtime secrets, Sealed Secrets for
  bootstrap, `secrets.example.env` templates document required values.
