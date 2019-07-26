# AWS examples

## Metadata

We have not yet found out how to do metadata such as we can do it in
OpenStack. 

However AWS offers [tags](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#securitygroup). Thus if we can not find how to add metadata
to a vm we coudl use the tag for doing this.

The way we can ancode a `cm` dict is with 

```
import boto3
ec2 = boto3.resource('ec2') 
cm = {
    "name": "gregor",
    "kind": "example",
    "cloud": "aws"
} 
    for tag in cm
        ec2.Tag('resource_id', tag, cm[tag])
```
`
## Image

```
put the image dict here 
```

## Flavor

```
put the flavor dict here 
````

## Vm

* see also
  [Aws Instance Properties](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html)

```
put the vm dict here 
```

## Secgroup

* see also
  [Security Group](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html)
```
put the image dict here 
```

## Secrule

* the boto documentation is located [here](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#securitygroup)
```
put the image dict here 
```

## Key

It is possible to import your own public keys to AWS see the
[documentation][https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#how-to-generate-your-own-key-and-import-it-to-aws]

The boto3 documentation is located [here](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/ec2-example-key-pairs.html)
```
put the image dict here 
```

## Other

If you need other dicts please place them here and change the headlines
accordingly.

```
put the other dict here 
```
