# Flavor 

# Image
{
    "Images": [
        {
            "Architecture": "x86_64",
            "CreationDate": "2019-05-15T18:42:03.000Z",
            "ImageId": "ami-0c929bde1796e1484",
            "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-trusty-14.04-amd64-server-20190514",
            "ImageType": "machine",
            "Public": true,
            "OwnerId": "099720109477",
            "State": "available",
            "BlockDeviceMappings": [
                {
                    "DeviceName": "/dev/sda1",
                    "Ebs": {
                        "DeleteOnTermination": true,
                        "SnapshotId": "snap-071b52f2290ef80df",
                        "VolumeSize": 8,
                        "VolumeType": "gp2",
                        "Encrypted": false
                    }
                },
                {
                    "DeviceName": "/dev/sdb",
                    "VirtualName": "ephemeral0"
                },
                {
                    "DeviceName": "/dev/sdc",
                    "VirtualName": "ephemeral1"
                }
            ],
            "Description": "Canonical, Ubuntu, 14.04 LTS, amd64 trusty image build on 2019-05-14",
            "EnaSupport": true,
            "Hypervisor": "xen",
            "Name": "ubuntu/images/hvm-ssd/ubuntu-trusty-14.04-amd64-server-20190514",
            "RootDeviceName": "/dev/sda1",
            "RootDeviceType": "ebs",
            "SriovNetSupport": "simple",
            "VirtualizationType": "hvm"
        }
    ]
}

# VM
{
    "Reservations": [
        {
            "Groups": [],
            "Instances": [
                {
                    "AmiLaunchIndex": 0,
                    "ImageId": "ami-0c929bde1796e1484",
                    "InstanceId": "i-0ec1156c6c270175f",
                    "InstanceType": "t2.micro",
                    "KeyName": "spullak@iu.edu",
                    "LaunchTime": "2019-08-12T02:33:39.000Z",
                    "Monitoring": {
                        "State": "disabled"
                    },
                    "Placement": {
                        "AvailabilityZone": "us-east-2b",
                        "GroupName": "",
                        "Tenancy": "default"
                    },
                    "PrivateDnsName": "ip-172-31-27-233.us-east-2.compute.internal",
                    "PrivateIpAddress": "172.31.27.233",
                    "ProductCodes": [],
                    "PublicDnsName": "ec2-18-220-165-120.us-east-2.compute.amazonaws.com",
                    "PublicIpAddress": "18.220.165.120",
                    "State": {
                        "Code": 16,
                        "Name": "running"
                    },
                    "StateTransitionReason": "",
                    "SubnetId": "subnet-96483dec",
                    "VpcId": "vpc-dc7364b4",
                    "Architecture": "x86_64",
                    "BlockDeviceMappings": [
                        {
                            "DeviceName": "/dev/sda1",
                            "Ebs": {
                                "AttachTime": "2019-08-11T20:05:48.000Z",
                                "DeleteOnTermination": true,
                                "Status": "attached",
                                "VolumeId": "vol-02e94184ab899e351"
                            }
                        }
                    ],
                    "ClientToken": "",
                    "EbsOptimized": false,
                    "EnaSupport": true,
                    "Hypervisor": "xen",
                    "NetworkInterfaces": [
                        {
                            "Association": {
                                "IpOwnerId": "amazon",
                                "PublicDnsName": "ec2-18-220-165-120.us-east-2.compute.amazonaws.com",
                                "PublicIp": "18.220.165.120"
                            },
                            "Attachment": {
                                "AttachTime": "2019-08-11T20:05:47.000Z",
                                "AttachmentId": "eni-attach-04912a0999e2db115",
                                "DeleteOnTermination": true,
                                "DeviceIndex": 0,
                                "Status": "attached"
                            },
                            "Description": "",
                            "Groups": [
                                {
                                    "GroupName": "default",
                                    "GroupId": "sg-a77eb8c9"
                                }
                            ],
                            "Ipv6Addresses": [],
                            "MacAddress": "06:8b:ab:a5:5f:0c",
                            "NetworkInterfaceId": "eni-0e887172f3b36aa00",
                            "OwnerId": "799617972514",
                            "PrivateDnsName": "ip-172-31-27-233.us-east-2.compute.internal",
                            "PrivateIpAddress": "172.31.27.233",
                            "PrivateIpAddresses": [
                                {
                                    "Association": {
                                        "IpOwnerId": "amazon",
                                        "PublicDnsName": "ec2-18-220-165-120.us-east-2.compute.amazonaws.com",
                                        "PublicIp": "18.220.165.120"
                                    },
                                    "Primary": true,
                                    "PrivateDnsName": "ip-172-31-27-233.us-east-2.compute.internal",
                                    "PrivateIpAddress": "172.31.27.233"
                                }
                            ],
                            "SourceDestCheck": true,
                            "Status": "in-use",
                            "SubnetId": "subnet-96483dec",
                            "VpcId": "vpc-dc7364b4",
                            "InterfaceType": "interface"
                        }
                    ],
                    "RootDeviceName": "/dev/sda1",
                    "RootDeviceType": "ebs",
                    "SecurityGroups": [
                        {
                            "GroupName": "default",
                            "GroupId": "sg-a77eb8c9xx"
                        }
                    ],
                    "SourceDestCheck": true,
                    "Tags": [
                        {
                            "Key": "name",
                            "Value": "test-spullak@iu.edu-vm-38"
                        },
                        {
                            "Key": "cm.name",
                            "Value": "test-spullak@iu.edu-vm-38"
                        },
                        {
                            "Key": "Name",
                            "Value": "test-spullak@iu.edu-vm-38"
                        }
                    ],
                    "VirtualizationType": "hvm",
                    "CpuOptions": {
                        "CoreCount": 1,
                        "ThreadsPerCore": 1
                    },
                    "CapacityReservationSpecification": {
                        "CapacityReservationPreference": "open"
                    },
                    "HibernationOptions": {
                        "Configured": false
                    }
                }
            ],
            "OwnerId": "799617972514",
            "ReservationId": "r-037848aa38ebed232"
        }
    ]
}


# Key
{
    "KeyPairs": [
        {
            "KeyFingerprint": "0c:3d:86:a8:2d:73:ec:09:54:45:cf:00:a0:d0:09:1e:a2:3a:a5:29",
            "KeyName": "aws_vm1"
        }
    ]
}


# Secgroup
{
    "SecurityGroups": [
        {
            "Description": "default VPC security group",
            "GroupName": "default",
            "IpPermissions": [
                {
                    "IpProtocol": "-1",
                    "IpRanges": [],
                    "Ipv6Ranges": [],
                    "PrefixListIds": [],
                    "UserIdGroupPairs": [
                        {
                            "GroupId": "sg-fsdfadfadf",
                            "UserId": "35353343434"
                        }
                    ]
                }
            ],
            "OwnerId": "35353343434",
            "GroupId": "sg-fsdfadfadf",
            "IpPermissionsEgress": [
                {
                    "IpProtocol": "-1",
                    "IpRanges": [
                        {
                            "CidrIp": "0.0.0.0/0"
                        }
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": [],
                    "UserIdGroupPairs": []
                }
            ],
            "VpcId": "vpc-efr343dr"
        }
    ]
}


# Secrule

...
