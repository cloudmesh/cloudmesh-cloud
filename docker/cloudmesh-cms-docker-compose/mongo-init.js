db.createUser(
    {
        user: "<your-username>",
        pwd: "<your-password>",
        roles: [
            {
                role: "readWrite",
                db: "cloudmesh"
            }
        ]
    }
);
