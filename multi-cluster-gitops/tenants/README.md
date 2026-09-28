# tenants/

Landing zone for dev-ex scaffolder PRs. Each `tenants/<app>/` directory
contains:

- `namespace.yaml` — the tenant namespace
- `rbac.yaml` — admin RoleBinding for the owning group
- `quota.yaml` — ResourceQuota + LimitRange
- `application.yaml` — child ArgoCD Application → the app repo's
  `manifests/` (Deployment, Service, Route, CNPG Postgres cluster)

The `tenants` ApplicationSet (argocd/applicationsets/tenants.yaml)
generates one Application per directory via a git directories generator.
Manifests carry their own `metadata.namespace`; the generator's
destination namespace is only a fallback.
