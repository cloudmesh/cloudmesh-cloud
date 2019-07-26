# OpenStack examples

All `cm` directories are added by cloudmesh

## Image

Please note that the cm directory is added by cloudmesh.

```
{
    "links" : [ 
        {
            "href" : "http://openstack.tacc.chameleoncloud.org:8774/v2/CH-111111/images/a4435e63-1fb5-4445-bc11-e96013959dab",
            "rel" : "self"
        }, 
        {
            "href" : "http://openstack.tacc.chameleoncloud.org:8774/CH-111111/images/a4435e63-1fb5-4445-bc11-e96013959dab",
            "rel" : "bookmark"
        }, 
        {
            "href" : "http://129.114.97.110:9292/images/a4435e63-1fb5-4445-bc11-e96013959dab",
            "type" : "application/vnd.openstack.image",
            "rel" : "alternate"
        }
    ],
    "name" : "CC-Ubuntu18.04",
    "created_at" : "2019-07-16T14:23:00Z",
    "metadata" : {
        "build-repo-commit" : "e136d7433eb28950ad1e71adba8c1c81032d7d56",
        "build-kvm" : "True",
        "build-variant" : "base",
        "build-repo" : "https://github.com/ChameleonCloud/CC-Ubuntu16.04",
        "build-os" : "ubuntu-bionic",
        "build-tag" : "jenkins-cc-ubuntu18.04-kvm-builder-6",
        "build-os-base-image-revision" : "20190708"
    },
    "min_disk" : 0,
    "min_ram" : 0,
    "progress" : 100,
    "status" : "ACTIVE",
    "updated_at" : "2019-07-16T14:23:12Z",
    "size" : 976683008,
    "id" : "a4435e63-1fb5-4445-bc11-e96013959dab",
    "location" : {
        "cloud" : "chameleon",
        "region_name" : "RegionOne",
        "zone" : null,
        "project" : {
            "id" : "CH-111111",
            "name" : "CH-111111",
            "domain_id" : null,
            "domain_name" : null
        }
    },
    "cm" : {
        "kind" : "image",
        "driver" : "openstack",
        "cloud" : "chameleon",
        "name" : "CC-Ubuntu18.04",
        "created" : "2019-07-24 00:40:59.316867",
        "updated" : "2019-07-24 00:40:59.297766",
        "collection" : "chameleon-image",
        "modified" : "2019-07-24 00:40:59.316867"
    }
} 
```

## Flavor

```
{
    "links" : [ 
        {
            "href" : "http://openstack.tacc.chameleoncloud.org:8774/v2/CH-111111/flavors/1",
            "rel" : "self"
        }, 
        {
            "href" : "http://openstack.tacc.chameleoncloud.org:8774/CH-111111/flavors/1",
            "rel" : "bookmark"
        }
    ],
    "name" : "m1.tiny",
    "description" : null,
    "disk" : 1,
    "is_public" : true,
    "ram" : 512,
    "vcpus" : 1,
    "swap" : "",
    "ephemeral" : 0,
    "is_disabled" : false,
    "rxtx_factor" : 1.0,
    "extra_specs" : null,
    "id" : "1",
    "location" : {
        "cloud" : "chameleon",
        "region_name" : "RegionOne",
        "zone" : null,
        "project" : {
            "id" : "CH-111111",
            "name" : "CH-111111",
            "domain_id" : null,
            "domain_name" : null
        }
    },
    "cm" : {
        "kind" : "flavor",
        "driver" : "openstack",
        "cloud" : "chameleon",
        "name" : "m1.tiny",
        "created" : "2019-07-26 08:31:08.845105",
        "collection" : "chameleon-flavor",
        "modified" : "2019-07-26 08:31:08.845105"
    },
    "updated" : "2019-07-26 08:31:08.828054"
} 
```

## Vm

cloudmesh added: 

* `ip_public` 
* `ip_private` 
* `cm`
* `metadata` 
* `creation_time` is given in seconds

```
{
    "links" : [ 
        {
            "href" : "http://openstack.tacc.chameleoncloud.org:8774/v2/CH-111111/servers/b2b37ad1-7af8-4dbb-b5d0-62f7b1b66995",
            "rel" : "self"
        }, 
        {
            "href" : "http://openstack.tacc.chameleoncloud.org:8774/CH-111111/servers/b2b37ad1-7af8-4dbb-b5d0-62f7b1b66995",
            "rel" : "bookmark"
        }
    ],
    "access_ipv4" : "",
    "access_ipv6" : "",
    "addresses" : {
        "CH-111111-net" : [ 
            {
                "OS-EXT-IPS-MAC:mac_addr" : "fa:16:3e:c1:bf:df",
                "version" : 4,
                "addr" : "192.168.0.156",
                "OS-EXT-IPS:type" : "fixed"
            }, 
            {
                "OS-EXT-IPS-MAC:mac_addr" : "fa:16:3e:c1:bf:df",
                "version" : 4,
                "addr" : "111.222.333.444",
                "OS-EXT-IPS:type" : "floating"
            }
        ]
    },
    "admin_password" : null,
    "attached_volumes" : [],
    "availability_zone" : "nova",
    "block_device_mapping" : null,
    "config_drive" : "",
    "compute_host" : null,
    "created_at" : "2019-07-24T02:10:12Z",
    "description" : null,
    "disk_config" : "MANUAL",
    "flavor_id" : null,
    "flavor" : {
        "id" : "2",
        "links" : [ 
            {
                "href" : "http://openstack.tacc.chameleoncloud.org:8774/CH-111111/flavors/2",
                "rel" : "bookmark"
            }
        ]
    },
    "has_config_drive" : "",
    "host_id" : "330a47d6b1a9f9fdcb6d61a6994da48f76a81526995535b38484285d",
    "host_status" : null,
    "hostname" : null,
    "hypervisor_hostname" : null,
    "image_id" : null,
    "image" : {
        "checksum" : null,
        "container_format" : null,
        "created_at" : null,
        "disk_format" : null,
        "is_hidden" : null,
        "is_protected" : null,
        "hash_algo" : null,
        "hash_value" : null,
        "min_disk" : null,
        "min_ram" : null,
        "name" : null,
        "owner_id" : null,
        "properties" : {
            "links" : [ 
                {
                    "href" : "http://openstack.tacc.chameleoncloud.org:8774/CH-111111/images/fc507be9-41e4-4c2c-b142-5c4256f8a814",
                    "rel" : "bookmark"
                }
            ]
        },
        "size" : null,
        "store" : null,
        "status" : null,
        "tags" : null,
        "updated_at" : null,
        "virtual_size" : null,
        "visibility" : null,
        "file" : null,
        "locations" : null,
        "direct_url" : null,
        "url" : null,
        "metadata" : null,
        "architecture" : null,
        "hypervisor_type" : null,
        "instance_type_rxtx_factor" : null,
        "instance_uuid" : null,
        "needs_config_drive" : null,
        "kernel_id" : null,
        "os_distro" : null,
        "os_version" : null,
        "needs_secure_boot" : null,
        "os_shutdown_timeout" : null,
        "ramdisk_id" : null,
        "vm_mode" : null,
        "hw_cpu_sockets" : null,
        "hw_cpu_cores" : null,
        "hw_cpu_threads" : null,
        "hw_disk_bus" : null,
        "hw_cpu_policy" : null,
        "hw_cpu_thread_policy" : null,
        "hw_rng_model" : null,
        "hw_machine_type" : null,
        "hw_scsi_model" : null,
        "hw_serial_port_count" : null,
        "hw_video_model" : null,
        "hw_video_ram" : null,
        "hw_watchdog_action" : null,
        "os_command_line" : null,
        "hw_vif_model" : null,
        "is_hw_vif_multiqueue_enabled" : null,
        "is_hw_boot_menu_enabled" : null,
        "vmware_adaptertype" : null,
        "vmware_ostype" : null,
        "has_auto_disk_config" : null,
        "os_type" : null,
        "os_admin_user" : null,
        "hw_qemu_guest_agent" : null,
        "os_require_quiesce" : null,
        "schema" : null,
        "id" : "fc507be9-41e4-4c2c-b142-5c4256f8a814",
        "location" : null
    },
    "instance_name" : null,
    "is_locked" : null,
    "kernel_id" : null,
    "key_name" : "gregor",
    "launch_index" : null,
    "launched_at" : "2019-07-24T02:10:23.000000",
    "metadata" : {
        "image" : "Ubuntu-Server-14.04-LTS",
        "flavor" : "m1.small",
        "cm" : "{'kind': 'vm', 'name': 'gregor-vm-5', 'group': 'experiment-a', 'cloud': 'chameleon', 'status': 'available', 'creation_time': '22.74'}"
    },
    "networks" : null,
    "personality" : null,
    "power_state" : 1,
    "progress" : 0,
    "project_id" : "CH-111111",
    "ramdisk_id" : null,
    "reservation_id" : null,
    "root_device_name" : null,
    "scheduler_hints" : null,
    "security_groups" : [ 
        {
            "name" : "default"
        }
    ],
    "server_groups" : null,
    "status" : "ACTIVE",
    "task_state" : null,
    "terminated_at" : null,
    "trusted_image_certificates" : null,
    "updated_at" : "2019-07-24T02:10:23Z",
    "user_data" : null,
    "user_id" : "tg455498",
    "vm_state" : "active",
    "id" : "b2b37ad1-7af8-4dbb-b5d0-62f7b1b66995",
    "name" : "gregor-vm-5",
    "location" : {
        "cloud" : "chameleon",
        "region_name" : "RegionOne",
        "zone" : "nova",
        "project" : {
            "id" : "CH-111111",
            "name" : "CH-111111",
            "domain_id" : null,
            "domain_name" : null
        }
    },
    "tags" : [],
    "cm" : {
        "kind" : "vm",
        "driver" : "openstack",
        "cloud" : "chameleon",
        "name" : "gregor-vm-5",
        "updated" : "2019-07-26 08:30:38.830830",
        "created" : "2019-07-26 08:30:38.846563",
        "group" : "experiment-a",
        "status" : "available",
        "creation_time" : "22.74",
        "collection" : "chameleon-vm",
        "modified" : "2019-07-26 08:30:38.846563"
    },
    "ip_public" : "111.222.333.444",
    "ip_private" : [ 
        "192.168.0.156"
    ]
}
```

## Secgroup

```
    "1": {
        "cm": {
            "cloud": "chameleon",
            "driver": "openstack",
            "kind": "secgroup",
            "name": "flask"
        },
        "created_at": null,
        "description": "Flask security group",
        "id": "6789012-98a0-4591-8f67-a3e03a0df748",
        "location": {
            "cloud": "chameleon",
            "project": {
                "domain_id": null,
                "domain_name": null,
                "id": "CH-111111",
                "name": "CH-111111"
            },
            "region_name": "RegionOne",
            "zone": null
        },
        "name": "flask",
        "project_id": null,
        "revision_number": null,
        "security_group_rules": [
            {
                "direction": "ingress",
                "ethertype": "IPv4",
                "id": "12345123-a4c2-4ee6-8ddb-bacb4f3abd90",
                "port_range_max": 8000,
                "port_range_min": 8000,
                "protocol": "tcp",
                "remote_group_id": null,
                "remote_ip_prefix": "0.0.0.0/0",
                "security_group_id": "6789012-98a0-4591-8f67-a3e03a0df748",
                "tenant_id": "CH-111111"
            },
            {
                "direction": "egress",
                "ethertype": "IPv4",
                "id": "4ffc70cb-4a81-4b7c-be8c-cf0a8ddf1fe0",
                "port_range_max": null,
                "port_range_min": null,
                "protocol": null,
                "remote_group_id": null,
                "remote_ip_prefix": null,
                "security_group_id": "6789012-98a0-4591-8f67-a3e03a0df748",
                "tenant_id": "CH-111111"
            },
            {
                "direction": "ingress",
                "ethertype": "IPv4",
                "id": "6f1daedb-bfe2-42bc-be13-e32a36c483ca",
                "port_range_max": 22,
                "port_range_min": 22,
                "protocol": "tcp",
                "remote_group_id": null,
                "remote_ip_prefix": "0.0.0.0/0",
                "security_group_id": "6789012-98a0-4591-8f67-a3e03a0df748",
                "tenant_id": "CH-111111"
            },
            {
                "direction": "ingress",
                "ethertype": "IPv4",
                "id": "75078885-effe-4af6-8167-197da8183ef1",
                "port_range_max": null,
                "port_range_min": null,
                "protocol": "icmp",
                "remote_group_id": null,
                "remote_ip_prefix": "0.0.0.0/0",
                "security_group_id": "6789012-98a0-4591-8f67-a3e03a0df748",
                "tenant_id": "CH-111111"
            },
            {
                "direction": "egress",
                "ethertype": "IPv6",
                "id": "ab220c75-ec77-4269-a52e-05e5c0f39b1c",
                "port_range_max": null,
                "port_range_min": null,
                "protocol": null,
                "remote_group_id": null,
                "remote_ip_prefix": null,
                "security_group_id": "6789012-98a0-4591-8f67-a3e03a0df748",
                "tenant_id": "CH-111111"
            },
            {
                "direction": "ingress",
                "ethertype": "IPv4",
                "id": "d87b033d-1b25-49c5-9b51-c67fed5a9191",
                "port_range_max": 443,
                "port_range_min": 443,
                "protocol": "tcp",
                "remote_group_id": null,
                "remote_ip_prefix": "0.0.0.0/0",
                "security_group_id": "6789012-98a0-4591-8f67-a3e03a0df748",
                "tenant_id": "CH-111111"
            }
        ],
        "tags": [],
        "tenant_id": "CH-111111",
        "updated_at": null
    }
}
```

## Secrule

Same as secgroup.

## Key

```
    "1": {
        "cm": {
            "cloud": "chameleon",
            "collection": "chameleon-key",
            "created": "2019-07-26 08:39:37.211010",
            "driver": "openstack",
            "kind": "key",
            "modified": "2019-07-26 08:39:50.372881",
            "name": "gregor"
        },
        "comment": "grey@149-160-152-71.dhcp-bl.indiana.edu\n",
        "created_at": "2019-07-26T04:39:50.354198",
        "fingerprint" : "aa:cc:dd:11:11:11:11:11:11:11:11:11:11:11:11:11",
        "format": "rsa",
        "id": "gregor",
        "location": {
            "cloud": "chameleon",
            "project": {
                "domain_id": null,
                "domain_name": null,
                "id": "CH-111111",
                "name": "CH-111111"
            },
            "region_name": "RegionOne",
            "zone": null
        },
        "name": "gregor",
        "private_key": null,
        "properties": {},
        "public_key": "ssh-rsa BBBBBBBB... cut here] label\n",
        "type": "ssh",
        "user_id": null
    }
}```

## Other

If you need other dicts please place them here and change the headlines
accordingly.

```
put the other dict here 
```
