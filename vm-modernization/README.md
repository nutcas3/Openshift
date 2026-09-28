# vm-modernization — OpenShift Virtualization Platform

Unifies legacy VMs and containers on one control plane. Developers
provision golden-template VMs via GitOps alongside microservices; the pod
network, Services, and Routes work identically for both.

## Layout

```
vm-modernization/
├── operators/cnv-operator.yaml   # kubevirt-hyperconverged subscription
├── cnv/hyperconverged.yaml       # completes the install (one-time CR)
└── vms/
    ├── vm-template.yaml          # RHEL guest + cloud-init (golden VM)
    └── service.yaml              # VM on the pod SDN, like a container
```

## Bootstrap

```sh
oc create namespace openshift-cnv
oc apply -f operators/cnv-operator.yaml
# wait for CSV Succeeded, then:
oc apply -f cnv/hyperconverged.yaml
# nodes must support virtualization (baremetal or nested virt)
```

## Notes

- `containerDisk` boots a container-native VM image; for persistent root
  disks use a `dataVolume`/`pvc` volume instead (golden images via CDI
  DataSources — the operator pre-populates RHEL/Fedora ones).
- Golden templates: define `VirtualMachineClusterTemplate` /
  `Template` resources in `openshift` ns to surface in the console wizard.
- Cloud-init (`cloudInitNoCloud`) configures users, SSH keys, packages,
  `runcmd` — keep passwords out of real manifests (pull from Vault/ESO).
- Live migration needs RWX storage and `vm.kubevirt.io/evictionStrategy`.
- VM workloads respect the same NetworkPolicy/quota as pods — the
  multi-tenancy baseline applies unchanged.
