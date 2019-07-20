* gregor

scrip and Shell.execute, Shell.run have overlapping functionality. We may want
to organize all of them into a dir

there are also such functionality in cloudmesh.common and cloudmesh.common3

we need to reduce the duplication

This is unfortunate as this seems to be caused by python2 vs python 3 code

Start with listing all execution code here so we can organize the cleanup
