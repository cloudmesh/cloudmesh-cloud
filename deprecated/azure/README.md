## Azure Cloud

Uses [LibCloud's Azure ARM Compute Driver](https://libcloud.readthedocs.io/en/latest/compute/drivers/azure_arm.html)

### Azure Setup


**Install Azure CLI**

[Download and install according to your platform.](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)

**Make sure subscription is registered for compute services**

```
az provider register --namespace Microsoft.Compute
```

**Service principal**

[Full documentation on creating service principals.](https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli?view=azure-cli-latest) The Azure ARM Driver does not appear to support certificate based
principals at this time.


Create Principal
```
az ad sp create-for-rbac --name cm-admin-pw --password <SECRET>
```

Add `Owner` role.

```
az role assignment create --assignee <APP_ID> --role Owner
```

*Note:* `<APP_ID>` is provided in the output when the principal is created