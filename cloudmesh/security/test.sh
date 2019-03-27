#!/usr/bin/env bash

openssl genrsa -out key.pem 1024
openssl rsa -in key.pem -text -noout
# Save public key in pub.pem file:

openssl rsa -in key.pem -pubout -out pub.pem
openssl rsa -in pub.pem -pubin -text -noout

#3) Encrypt some data:

echo test test test > file.txt
openssl rsautl -encrypt -inkey pub.pem -pubin -in file.txt -out file.bin

#4) Decrypt encrypted data:

openssl rsautl -decrypt -inkey key.pem -in file.bin