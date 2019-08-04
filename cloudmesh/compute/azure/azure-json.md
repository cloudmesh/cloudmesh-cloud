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
{
  'additional_properties': {},
  'id': '/subscriptions/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/resourceGroups/cloudmesh/providers/Microsoft.Compute/virtualMachines/cloudmeshVM',
  'name': 'cloudmeshVM',
  'type': 'Microsoft.Compute/virtualMachines',
  'location': 'eastus',
  'tags': {
    'tag 1': 'python',
    'tag 2': 'JAE'
  },
  'plan': None,
  'hardware_profile': < azure.mgmt.compute.v2019_03_01.models.hardware_profile_py3.HardwareProfile object at 0x1166e12e8 > ,
  'storage_profile': < azure.mgmt.compute.v2019_03_01.models.storage_profile_py3.StorageProfile object at 0x1166e11d0 > ,
  'additional_capabilities': None,
  'os_profile': < azure.mgmt.compute.v2019_03_01.models.os_profile_py3.OSProfile object at 0x1166e1128 > ,
  'network_profile': < azure.mgmt.compute.v2019_03_01.models.network_profile_py3.NetworkProfile object at 0x1166e1278 > ,
  'diagnostics_profile': None,
  'availability_set': None,
  'provisioning_state': 'Succeeded',
  'instance_view': None,
  'license_type': None,
  'vm_id': '33333333-3333-3333-3333-444444444444',
  'resources': None,
  'identity': None,
  'zones': None
}
```
