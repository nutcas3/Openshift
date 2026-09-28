# ai-ml-platform — On-Demand AI/ML Developer Platform

Self-service MLOps on OpenShift AI: Jupyter workbenches against shared
GPU pools, and git-driven KServe InferenceServices for LLM serving.

## Layout

```
ai-ml-platform/
├── operators/
│   ├── rhoai-operator.yaml        # Red Hat OpenShift AI
│   └── nvidia-gpu-operator.yaml   # GPU drivers/device plugin
└── ai/
    ├── datascience-cluster.yaml   # DataScienceCluster (activate components)
    ├── namespace.yaml             # ai-workloads
    ├── notebook.yaml              # Jupyter workbench w/ GPU request
    └── llm-serving.yaml           # KServe InferenceService (vLLM)
```

## Bootstrap

```sh
oc apply -f operators/rhoai-operator.yaml
# GPU nodes only: apply nvidia-gpu-operator.yaml + its ClusterPolicy
oc apply -f ai/datascience-cluster.yaml   # after operator is Ready
oc apply -f ai/namespace.yaml ai/notebook.yaml
```

## Serving an LLM

1. Create data-connection secret `models-s3` in `ai-workloads`
   (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET,
   AWS_S3_ENDPOINT, AWS_DEFAULT_REGION).
2. Ensure a `ServingRuntime` named `vllm-runtime` exists (OpenShift AI
   dashboard → Serving runtimes → add vLLM).
3. `oc apply -f ai/llm-serving.yaml` → endpoint at
   `https://granite-code-service-ai-workloads.apps.<domain>/v1`.

## Notes

- GPU requests (`nvidia.com/gpu`) schedule only where the device plugin
  reports capacity; enable Kueue for fair sharing across teams.
- The dashboard creates notebooks too — committing them as CRs here makes
  environments reproducible via GitOps.
- TrustyAI (explainability) and Ray (distributed training) are present but
  Removed — flip to Managed when needed.
