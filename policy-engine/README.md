# policy-engine — Policy-as-Code & Compliance Enforcement

Kyverno ClusterPolicies that gate admission: non-compliant manifests are
rejected at the API server before they ever reach the cluster.

## Layout

```
policy-engine/
└── cluster-policies/
    ├── disallow-root-execution.yaml   # securityContext.runAsNonRoot
    ├── require-resource-limits.yaml   # cpu/mem requests+limits mandatory
    ├── disallow-latest-tag.yaml       # immutable image references
    └── restrict-registries.yaml       # approved-registry allowlist
```

## Prereq

Kyverno — the subscription already lives at
`trusted-supply-chain/operators/kyverno-operator.yaml` (shared operator;
don't install twice).

## Bootstrap

```sh
oc apply -f cluster-policies/
```

## Operating model

- `validationFailureAction: Enforce` blocks; use `Audit` while rolling out
  to observe violations without breaking workloads, then flip to Enforce.
- `background: true` also scans existing pods → `PolicyReport` CRs per
  namespace (`oc get policyreport -A`) = compliance posture.
- `=(securityContext)` anchors mean "field may be absent at pod level but
  required when present" — pod-level context OR per-container both pass.
- Exceptions go through `PolicyException` CRs, not policy edits.
- OPA Gatekeeper is the alternative engine; pick one, don't run both.
