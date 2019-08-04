# Flavor 

```
{
  'additional_properties': {},
  'name': 'Standard_D12_v2_Promo',
  'number_of_cores': 4,
  'os_disk_size_in_mb': 1047552,
  'resource_disk_size_in_mb': 204800,
  'memory_in_mb': 28672,
  'max_data_disk_count': 16
}
```

# Image

```
python
{
  'id': '/Subscriptions/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/Providers/Microsoft.Compute/Locations/eastus/Publishers/128technology/ArtifactTypes/VMImage/Offers/128t_networking_platform/Skus/128t_networking_platform/Versions/1.0.0',
  'name': '1.0.0',
  'location': 'eastus',
  'plan': {
    'publisher': '128technology',
    'name': '128t_networking_platform',
    'product': '128t_networking_platform'
  },
  'os_disk_image': {
    'operating_system': 'Linux'
  },
  'data_disk_images': [],
  'automatic_os_upgrade_properties': {
    'automatic_os_upgrade_supported': False
  }
}
```

# Virtual Machine

```
python
[{
  'id': '/subscriptions/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/resourceGroups/CLOUDMESH/providers/Microsoft.Compute/virtualMachines/cloudmeshVM',
  'name': 'cloudmeshVM',
  'type': 'Microsoft.Compute/virtualMachines',
  'location': 'eastus',
  'tags': {},
  'hardware_profile': {
    'vm_size': 'Standard_DS1_v2'
  },
  'storage_profile': {
    'image_reference': {
      'publisher': 'Canonical',
      'offer': 'UbuntuServer',
      'sku': '16.04.0-LTS',
      'version': 'latest'
    },
    'os_disk': {
      'os_type': 'Linux',
      'name': 'cloudmeshVM_disk1_83d655b524e24dc087fd79bda55b5e1e',
      'caching': 'ReadWrite',
      'create_option': 'FromImage',
      'disk_size_gb': 30,
      'managed_disk': {
        'id': '/subscriptions/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/resourceGroups/cloudmesh/providers/Microsoft.Compute/disks/cloudmeshVM_disk1_83d655b524e24dc087fd79bda55b5e1e',
        'storage_account_type': 'Premium_LRS'
      }
    },
    'data_disks': [{
      'lun': 12,
      'name': 'cloudmesh-datadisk1',
      'caching': 'None',
      'create_option': 'Attach',
      'disk_size_gb': 1,
      'managed_disk': {
        'id': '/subscriptions/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/resourceGroups/cloudmesh/providers/Microsoft.Compute/disks/cloudmesh-datadisk1',
        'storage_account_type': 'Standard_LRS'
      }
    }]
  },
  'os_profile': {
    'computer_name': 'cloudmeshVM',
    'admin_username': 'myvmuser',
    'linux_configuration': {
      'disable_password_authentication': False,
      'provision_vm_agent': True
    },
    'secrets': [],
    'allow_extension_operations': True
  },
  'network_profile': {
    'network_interfaces': [{
      'id': '/subscriptions/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/resourceGroups/cloudmesh/providers/Microsoft.Network/networkInterfaces/cloudmesh-nic'
    }]
  },
  'provisioning_state': 'Succeeded',
  'vm_id': '33333333-3333-3333-3333-444444444444',
  'cm': {
    'kind': 'vm',
    'driver': 'azure',
    'cloud': 'azure',
    'name': 'cloudmeshVM',
    'updated': '2019-08-04 01:15:57.734485',
    'type': 'Microsoft.Compute/virtualMachines',
    'location': 'eastus'
  }
}]
```

# Key

```
TBD
```

# Secgroup & Secrule

```
TBD
```

# Resource Group

```
TBD
```
