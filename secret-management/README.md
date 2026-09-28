# secret-management — Enterprise Secret Engine (Vault + ESO)

Decouples static secrets from GitOps: git carries `ExternalSecret` CRs
only; the External Secrets Operator pulls real values from HashiCorp
Vault using Kubernetes auth.

```
GitOps → ExternalSecret CR → ESO → Vault (k8s auth) → native Secret
```

## Layout

```
secret-management/
├── operators/external-secrets.yaml
└── vault/
    ├── cluster-secret-store.yaml   # ClusterSecretStore vault-backend
    └── external-secret.yaml        # sample ExternalSecret (team-a db)
```

## Bootstrap

```sh
oc apply -f operators/external-secrets.yaml
# Vault: k8s auth enabled + role bound to SA eso-vault-auth
# (see comments in cluster-secret-store.yaml)
oc adm policy add-cluster-role-to-user system:auth-delegator \
  system:serviceaccount:external-secrets:eso-vault-auth
oc apply -f vault/
```

## Design notes

- `ClusterSecretStore` shared cluster-wide; tenant namespaces get a
  namespace-scoped `SecretStore` if you need per-team Vault roles.
- `creationPolicy: Owner` ties the materialized Secret's lifecycle to the
  ExternalSecret — deleting the CR removes the Secret.
- Works alongside Sealed Secrets (project 10/`trusted-supply-chain`):
  sealed-secrets = encrypt-in-git; ESO = reference-external-store. Prefer
  ESO when Vault is available; keep sealed-secrets as the fallback for
  cluster-bootstrap secrets Vault itself needs.
- Vault deployment itself is out of scope — point `server:` at an existing
  Vault (in-cluster helm install or external enterprise Vault).
