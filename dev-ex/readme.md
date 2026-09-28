# dev-ex — Developer Experience platform on OpenShift

A golden-path setup built on Red Hat Developer Hub (RHDH): a software
template scaffolds a Quarkus service, publishes it to GitHub, and opens a
PR into a GitOps repo that provisions its namespace, RBAC, quota, an
ArgoCD Application, and a dedicated Postgres instance (CloudNativePG).
The generated repo ships a `devfile.yaml` so OpenShift Dev Spaces can
launch a workspace in one click.

## Architecture

```
RHDH template run
  ├─ fetch:template              → app skeleton (Quarkus, devfile, manifests/)
  ├─ publish:github              → new app repo
  ├─ fetch:template              → gitops skeleton (tenant manifests)
  ├─ publish:github:pull-request → PR into gitops repo: tenants/<app>/
  └─ catalog:register            → entity appears in RHDH

GitOps repo — ArgoCD syncs:
  ├─ tenants/<app>/              → Namespace + RoleBinding + ResourceQuota + LimitRange
  └─ tenants/<app>/application.yaml → Application → app repo manifests/
                                       (Deployment, Service, Route, CNPG Cluster)
```

The PR step keeps platform review in the loop before a namespace lands;
the RHDH service account never needs cluster-wide namespace creation.

## Layout

```
dev-ex/
├── gitops/operators/      # OLM Subscriptions for the platform operators
├── rhdh/                  # app-config.yaml + Backstage CR + secrets template
└── templates/
    ├── common/
    │   └── gitops-skeleton/    # shared tenant manifests carried by the gitops PR
    ├── quarkus-service/        # Quarkus REST (Java 21, quarkus-rest + Postgres)
    ├── go-service/             # plain Go (stdlib net/http)
    ├── java-service/           # plain Java HttpServer, latest LTS JDK
    └── python-service/         # FastAPI + uvicorn
```

Each template has the same shape: a `backstage-template.yaml` with the 5-step
scaffolder flow, a `skeleton/` published to the new app repo
(`catalog-info.yaml`, `devfile.yaml`, source, `manifests/` incl. a
CloudNativePG `Cluster`), and a reference to the shared
`common/gitops-skeleton/` for the tenant PR.

## Bootstrap

### 1. Install operators

```sh
oc apply -f gitops/operators/   # GitOps first, then RHDH, Dev Spaces, CNPG
```

Wait for `Succeeded` CSVs:

```sh
oc get csv -n openshift-gitops-operator
oc get csv -n rhdh-operator
oc get csv -n openshift-operators | grep -E 'devspaces|cloudnative'
```

### 2. Create the GitHub App

At `https://github.com/organizations/<org>/settings/apps/new` with:

- **Repository permissions**: Contents (rw), Pull Requests (rw), Metadata (r)
- **Organization permissions**: Members (r) — for `githubOrg` catalog ingestion
- Subscribe to repository events; set a webhook secret
- If the cluster isn't publicly reachable, use a smee.io relay as the
  webhook URL (wired in `app-config.yaml`)
- Install the app on the org

### 3. Deploy RHDH

```sh
cp rhdh/secrets.example.env rhdh/secrets.env   # fill in values
oc create namespace rhdh
oc create secret generic rhdh-secrets --from-env-file=rhdh/secrets.env -n rhdh
oc apply -k rhdh/
```

> `GITHUB_APP_PRIVATE_KEY` must contain real newlines. If `--from-env-file`
> mangles it, create the secret with
> `oc create secret generic rhdh-secrets --from-env-file=... --from-file=GITHUB_APP_PRIVATE_KEY=app.pem`.

### 4. Point ArgoCD at your gitops repo

The template PR adds directories under `tenants/`; a parent Application
must sync them. In the gitops repo (or applied once manually):

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: tenants
  namespace: openshift-gitops
spec:
  project: default
  source:
    repoURL: https://github.com/<org>/<gitops-repo>.git
    targetRevision: main
    path: tenants
    directory:
      recurse: true
  destination:
    server: https://kubernetes.default.svc
    namespace: openshift-gitops
  syncPolicy:
    automated: { prune: true, selfHeal: true }
```

ArgoCD applies each manifest to the `metadata.namespace` it declares
(tenant ns for RBAC/quota, `openshift-gitops` for child Applications).

## End-to-end verification

1. RHDH → **Create** → *Quarkus Service* → fill in name/owner/repos.
2. New repo appears in the org with `catalog-info.yaml`, `devfile.yaml`,
   `src/`, `manifests/`.
3. A PR `tenant-<name>` opens on the gitops repo → review → merge.
4. `oc get ns <name>` exists; `oc -n openshift-gitops get application <name>`
   syncs; `oc -n <name> get pods` shows the app; `oc -n <name> get cluster`
   shows the CNPG Postgres.
5. Component appears in the RHDH catalog; the Dev Spaces annotation
   launches a workspace that runs `mvn quarkus:dev`.

## Placeholders to set at deploy time

- `GITHUB_ORG` / repo names — in `rhdh/secrets.env` and the template run
- `apps_domain` — cluster wildcard domain (template parameter, default
  `apps.example.com`)
- Container image in `manifests/deployment.yaml` — point at your build
  output (ImageStream or external registry)

## Hardening backlog

- RHDH RBAC policy (permission framework) once auth is proven out
- TechDocs publisher on object storage instead of `local`
- Switch `guest` provider off after GitHub sign-in works
- Pin UDI tag/digest in `devfile.yaml`; pin operator channels
- More golden paths (frontend, AI/LLM service); quota policy review
