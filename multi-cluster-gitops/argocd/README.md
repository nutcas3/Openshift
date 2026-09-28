# ArgoCD operations runbook

## Register a remote cluster

Remote clusters are Secrets in `openshift-gitops` labeled
`argocd.argoproj.io/secret-type: cluster`. Create them with the CLI —
credentials never enter this repo:

```sh
argocd login <gitops-host> --sso
argocd cluster add <kube-context> --name dev-cluster
argocd cluster list   # the URL shown here goes into config.json `server`
```

To point an environment at a registered cluster, set `server` in that
env's `envs/<env>/<app>/config.json` (fleet-workloads) and the matching
element in `applicationsets/platform.yaml`.

## Bootstrap

```sh
# after projects exist in git (synced by this root app)
oc apply -f bootstrap/root-app.yaml
argocd appset list -n openshift-gitops
argocd app list -n openshift-gitops
```

## Sealed Secrets

The `platform` ApplicationSet installs a sealed-secrets controller per env
(namespace `sealed-secrets`). Each cluster has its own sealing key —
secrets sealed for dev cannot be opened in prod.

```sh
# fetch the cluster's public cert (safe to share with developers)
kubeseal --controller-namespace sealed-secrets --fetch-cert > dev.pem

# seal a secret, commit ONLY the SealedSecret
oc create secret generic my-secret --from-literal=password=... \
  --dry-run=client -o yaml | \
  kubeseal --cert dev.pem --format yaml \
  > fleet-workloads/secrets/dev/<app>/my-secret.sealedsecret.yaml
```

Scope defaults to `strict` (name+namespace bound). The SealedSecret's
`metadata.namespace` must match the app's destination namespace.

## PR previews

Label a fleet-workloads PR `preview` → an `example-app` instance appears
in `preview-pr-<number>` on the dev cluster within ~5 min
(`requeueAfterSeconds`). Remove the label or merge the PR to tear it down.

For private repos / higher rate limits, create a `github-creds` secret
(`token` key) in `openshift-gitops` and uncomment `tokenRef` in
`applicationsets/pr-preview.yaml`.

## Promoting an app

Promotion is a PR in fleet-workloads adding or updating
`envs/<env>/<app>/config.json` (e.g. copy `dev` → `staging` and bump the
image tag in `workloads/<app>/overlays/staging`). Merge → the env's
ApplicationSet generates/updates the child app → ArgoCD syncs.
