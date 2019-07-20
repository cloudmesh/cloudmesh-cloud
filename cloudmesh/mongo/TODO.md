* suitable for student

The DatabaseUpdate() overwrites the old entry instead it should combine the new
into the old and than replace the old entry

this way attributes that are already in the old entry are not overwritten

maybe we want a parameter replace=Trure/False controlling the behaviour

example wher ethis si useful is the vm which may have a "username" that may need
 to be preserved.

 Maybe we shoudl do this in the cm dict .... this way the rest of the object
 can be overwritten but the cm can be copied from the object already in the db.
