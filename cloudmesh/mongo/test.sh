rm -rf ~/.cloudmesh/mongodb
mkdir ~/.cloudmesh/mongodb
mongod --port 27017 --dbpath ~/.cloudmesh/mongodb &
sleep 1
mongo admin --port 27017 --eval 'db.createUser(  {user: "admin", pwd: "changeme", roles: [ { role: "userAdminAnyDatabase", db: "admin" }, "readWriteAnyDatabase" ]  }); db.adminCommand( { shutdown: 1 } );'
mongod --auth --port 27017 --dbpath ~/.cloudmesh/mongodb &
sleep 1
mongo --port 27017  --authenticationDatabase admin -u "admin" -p "changeme"
