#!/usr/bin/env bash

CERT=key
CERT=id_rsa

# openssl genrsa -out $CERT.pem 1024

ls $CERT* pub*
openssl rsa -in $CERT.pem -text -noout
ls $CERT* pub*

# Save public key in pub.pem file:

openssl rsa -in $CERT.pem -pubout -out pub.pem
ls $CERT* pub*
openssl rsa -in pub.pem -pubin -text -noout

# Encrypt some data:

echo test test test > file.txt
openssl rsautl -encrypt -inkey pub.pem -pubin -in file.txt -out file.bin
ls $CERT* pub*

# Decrypt encrypted data:

openssl rsautl -decrypt -inkey key.pem -in file.bin
