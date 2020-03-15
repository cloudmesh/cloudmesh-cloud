from cloudmesh.mongo.CmDatabase import CmDatabase

cm = CmDatabase()

gregor = {
    "cm": {
        "name": "gregor",
        "kind": "queue",
        "driver": "none",
        "cloud": "local"
    },
    "hallo": "hallo"
}

cm.insert(gregor, collection="local-queue")
