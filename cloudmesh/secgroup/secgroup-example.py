# Initial draft
#
secgroups = \
    [
        {
            "name": "default",
            "description": "Default security group",
            "rules": [
                "ssh", "icmp", "ssl"
            ]
        },
        {
            "Name": "flask",
            "Description": "Couchdb security group",
            "rules": [
                "ssh", "icmp", "ssl", "flask", "webserver"
            ]
        },
    ]

secrules = \
    [
        {
            "name": "ssh",
            "protocol": "tcp",
            "ip_range": "0.0.0.0/0",
            "ports": "22:22",
        },
        {
            "name": "icmp",
            "protocol": "icmp",
            "ip_range": "0.0.0.0/0",
            "ports": "",
        },
        {
            "name": "flask",
            "protocol": "tcp",
            "ip_range": "0.0.0.0/0",
            "ports": "5000:5000",
        },
        {
            "name": "webserver",
            "protocol": "tcp",
            "ip_range": "0.0.0.0/0",
            "ports": "80:80",
        },
        {
            "name": "ssl",
            "protocol": "tcp",
            "ip_range": "0.0.0.0/0",
            "ports": "443:443",
        }
    ]
"""
