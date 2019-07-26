# Local examples

Cloudmesh uses the following dicts locally

## Key

```
{
    "profile" : {
        "firstname" : "Gregor",
        "lastname" : "von Laszewski",
        "email" : "laszewski@gmail.com",
        "user" : "gregor",
        "github" : "laszewsk",
        "publickey" : "~/.ssh/id_rsa.pub"
    },
    "path" : "/Users/grey/.ssh/id_rsa.pub",
    "uri" : "file:///Users/grey/.ssh/id_rsa.pub",
    "string" : "ssh-rsa BBBBBBBB... <cut here> mykey",
    "type" : "ssh-rsa",
    "key" :  "ssh-rsa BBBBBBBB... cut here] label",
    "comment" : "mykey",
    "fingerprint" : "aa:cc:dd:11:11:11:11:11:11:11:11:11:11:11:11:11",
    "name" : "gregor",
    "source" : "ssh",
    "location" : {
        "public" : "/Users/gregor/.ssh/id_rsa.pub",
        "private" : "/Users/gregor/.ssh/id_rsa"
    },
    "cm" : {
        "kind" : "key",
        "cloud" : "local",
        "name" : "gregor",
        "collection" : "local-key",
        "created" : "2019-07-24 00:40:37.833010",
        "modified" : "2019-07-24 00:40:37.833010"
    }
}
```

## Secgroup

```
{
    "description" : "Default security group",
    "rules" : [ 
        "ssh", 
        "icmp"
    ],
    "name" : "default",
    "cm" : {
        "kind" : "secgroup",
        "name" : "default",
        "cloud" : "local",
        "collection" : "local-secgroup",
        "created" : "2019-07-24 00:40:35.873083",
        "modified" : "2019-07-24 00:40:35.873083"
    }
}
````

## Secrule

```
{
    "protocol" : "tcp",
    "ip_range" : "0.0.0.0/0",
    "ports" : "22:22",
    "name" : "ssh",
    "cm" : {
        "kind" : "secrule",
        "name" : "ssh",
        "cloud" : "local",
        "collection" : "local-secrule",
        "created" : "2019-07-24 00:40:35.919495",
        "modified" : "2019-07-24 00:40:35.919495"
    }
}
```
