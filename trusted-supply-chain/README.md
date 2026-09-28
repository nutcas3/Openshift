# trusted-supply-chain — Secure CI/CD on OpenShift

Automated build pipeline (Tekton) that produces **scanned, signed,
attested** container images, plus admission enforcement that rejects
unsigned images at deploy time.

```
commit → PipelineRun
  ├─ git-clone (ClusterTask)
  ├─ sonar-scan ──────────────┐  (parallel)
  └─ s2i-java build+push ─────┘
        └─ rox-image-scan     (ACS policy check — fails on violation)
             └─ cosign-sign   (cosign.key from signing-secrets secret)

Tekton Chains (TektonConfig): in-toto attestation + OCI signature for
every TaskRun emitting IMAGE_URL/IMAGE_DIGEST — automatic, no task needed.

Kyverno ClusterPolicy: verifyImages — Pods using ci-pipelines/* images
must carry a valid signature or admission is denied.
```

## Layout

```
trusted-supply-chain/
├── operators/                 # OLM subscriptions + TektonConfig (chains)
│   ├── openshift-pipelines.yaml
│   ├── rhacs-operator.yaml
│   ├── kyverno-operator.yaml        # optional — see policy/ note
│   └── tektonconfig-chains.yaml     # apply after pipelines operator
├── ci/                        # everything lives in ns ci-pipelines
│   ├── namespace.yaml               # ns + pipeline-ci SA + PVC + RBAC
│   ├── task-sonar-scan.yaml
│   ├── task-rox-image-scan.yaml
│   ├── task-cosign-sign.yaml
│   ├── pipeline.yaml                # secure-build-and-sign
│   ├── pipelinerun.yaml             # sample run
│   └── secrets.example.env
└── policy/
    └── clusterpolicy-require-signature.yaml
```

## Bootstrap

```sh
# 1. operators
oc apply -f operators/openshift-pipelines.yaml -f operators/rhacs-operator.yaml
# optional, for admission enforcement:
oc apply -f operators/kyverno-operator.yaml

# 2. wait for pipelines operator, then enable chains
oc wait --for=condition=ready tektonconfig/config --timeout=300s
oc apply -f operators/tektonconfig-chains.yaml

# 3. signing key (creates openshift-pipelines/signing-secrets)
cosign generate-key-pair k8s://openshift-pipelines/signing-secrets

# 4. ACS: install Central + SecuredCluster via the rhacs-operator console
#    flow (stackrox ns), then create an API token with image scan rights.

# 5. CI namespace + secrets
oc apply -f ci/namespace.yaml
cp ci/secrets.example.env ci/secrets.env   # fill SONAR_*, ROX_*
oc create secret generic ci-secrets --from-env-file=ci/secrets.env -n ci-pipelines
# registry-push: a dockerconfigjson secret able to write to the internal registry
oc create secret docker-registry registry-push \
  --docker-server=image-registry.openshift-image-registry.svc:5000 \
  --docker-username=unused --docker-password="$(oc create token pipeline-ci -n ci-pipelines)" \
  -n ci-pipelines
# cosign task needs the signing key inside ci-pipelines too
oc -n openshift-pipelines get secret signing-secrets -o json \
  | jq 'del(.metadata.namespace,.metadata.resourceVersion,.metadata.uid)' \
  | oc apply -n ci-pipelines -f -

# 6. pipeline
oc apply -f ci/task-sonar-scan.yaml ci/task-rox-image-scan.yaml ci/task-cosign-sign.yaml ci/pipeline.yaml
oc create -f ci/pipelinerun.yaml
```

## Verify

```sh
tkn pipelinerun logs secure-build-and-sign-sample -n ci-pipelines -f
cosign verify --key cosign.pub \
  image-registry.../ci-pipelines/example-app:latest

# admission: this must be REJECTED once the ClusterPolicy is applied
oc apply -f policy/clusterpolicy-require-signature.yaml   # paste cosign.pub first
oc run unsigned --image=image-registry.../ci-pipelines/example-app:unsigned -n example-app-dev
```

## Notes & dependencies

- `s2i-java`/`git-clone` are the operator's shipped ClusterTasks — check
  `oc get clustertasks` for names/params on your Pipelines version.
- SonarQube server is expected to exist (`SONAR_HOST_URL`); deploy one or
  drop the `sonar-scan` task.
- roxctl needs network access to Central (`ROX_CENTRAL_ENDPOINT`).
- Chains attestation requires tasks to emit `IMAGE_URL`+`IMAGE_DIGEST`
  results — s2i-* ClusterTasks already do.
- If you use ACS admission control for signature enforcement, skip Kyverno
  and `policy/` entirely.
