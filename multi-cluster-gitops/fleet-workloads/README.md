# fleet-workloads

Workload manifests for the multi-cluster GitOps engine. This repo is
written to by app teams via PR; `multi-cluster-gitops/` holds the ArgoCD
control plane (projects, ApplicationSets).

## Layout

```
workloads/<app>/
  base/                     # shared manifests
  overlays/<env>/           # per-env kustomize patches
envs/<env>/<app>/config.json   # consumed by that env's ApplicationSet
secrets/<env>/<app>/        # SealedSecrets only — never plaintext
```

## Add an app to an environment

1. `workloads/<app>/base/` + `overlays/<env>/` (or reuse an existing base).
2. `envs/<env>/<app>/config.json`:

```json
{
  "app": "my-app",
  "env": "dev",
  "path": "workloads/my-app/overlays/dev",
  "namespace": "my-app-dev",
  "server": "https://kubernetes.default.svc",
  "project": "dev"
}
```

`server` = the registered cluster URL (`argocd cluster list`). Merge →
the env's ApplicationSet generates the child Application → ArgoCD syncs.

## PR previews

Label a PR `preview` for a throwaway `preview-pr-<n>` namespace on dev.

## Secrets

Commit `SealedSecret` manifests only — see `argocd/README.md` in
multi-cluster-gitops for `kubeseal` instructions.
