EXAMPPLECOMMAND=mycommand

# --------------------------------------------------
# Generate a cloudmesh-EXAMPLE folder in which we put the command
# --------------------------------------------------
cms sys command generate $EXAMPLECOMMAND

# --------------------------------------------------
# Install $EXAMPLECOMMAND
# --------------------------------------------------
cd cloudmesh-$EXAMPLECOMMAND
pip install -e .

# --------------------------------------------------
# Test running $EXAMPLECOMMAND with and without params
# --------------------------------------------------
# cms %EXAMPLECOMMAND --file "c:\\mydir\\myfile.txt"
cms $EXAMPLECOMMAND list
