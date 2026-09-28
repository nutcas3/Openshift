# multi-tenancy — Automated Multi-Tenancy Engine

Cluster governance via declarative tenant onboarding. Each tenant overlay
produces an isolated namespace: RBAC for the owning group, a deny-by-default
network posture, and hard resource boundaries.

```
tenant overlay (tenants/<name>/)
        │
        v  kustomize: base + namespace + group patch
┌───────┴────────────────────────────────────────────┐
│ tenant-<name> namespace                             │
│  RoleBinding tenant-admin → Group <name>-admins     │
│  ResourceQuota + LimitRange (CPU/mem/pods/svc)      │
│  NetworkPolicy: deny-all except same-ns, ingress    │
│                 router, DNS egress, monitoring      │
└────────────────────────────────────────────────────┘
```

## Layout

```
multi-tenancy/
├── base/                    # isolation rules shared by every tenant
│   ├── rbac.yaml            # tenant-admin RoleBinding (group patched)
│   ├── quota.yaml           # ResourceQuota + LimitRange
│   └── network-policy.yaml  # deny-cross-ns + allow-monitoring
└── tenants/<name>/          # one dir per tenant
    ├── namespace.yaml
    ├── kustomization.yaml   # namespace: + base + patches
    └── patch-rbac-group.yaml
```

## Onboard a tenant

```sh
cp -r tenants/team-a tenants/team-b
# edit: namespace.yaml (name), kustomization.yaml (namespace:), patch-rbac-group.yaml
oc apply -k tenants/team-b
```

## GitOps wiring

Drop tenant dirs into `multi-cluster-gitops/tenants/` — the `tenants`
ApplicationSet already generates one Application per directory, so merged
PRs onboard tenants automatically. This directory's `tenants/` tree is the
canonical source; either copy overlays there or point the ApplicationSet
at this repo instead.

Dev-ex scaffolder PRs write a lighter version of these files
(`templates/common/gitops-skeleton/`); to unify, switch the skeleton's
gitops fetch to render this base+overlay shape.

## GitOps wiring

- The "controller" is GitOps: no custom operator needed. ArgoCD keeps
  tenant namespaces self-healing (drift from `oc` edits is reverted).
- RBAC subject names must match IdP-synced groups (GroupSync / RHSSO /
  GitHub IdP groups). If your group names differ, adjust the patch.
- DNS egress is allowed to `openshift-dns` only; kube-apiserver egress is
  denied — add an explicit egress rule if a workload needs API access.
- Quotas are per-tenant defaults; override with a `patch-quota.yaml` in the
  tenant overlay.
- For hierarchical tenancy (nested namespaces), evaluate HNC later — this
  layout is flat-by-design and GitOps-friendly.
