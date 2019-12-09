# --------------------------------------------------------------------------
# Purpose: Install Cloudmesh Storage package. T
# his script will install Cloudmesh Storage, MongoDb, and
# generate a plugin directory 
# Authors: Gregor von Laszewski (laszewski@gmail.com)
# --------------------------------------------------------------------------

# use the folloing names for a bundle

# BUNDLE=cloud
# BUNDLE=storage

BUNDLE=storage

# Set a unique username here. It must not have spaces or characters not in a-Z0-9

# USERNAME=$USER
USERNAME="IUUSERNAME"

FIRSTNAME="Firstname"
LASTNAME="Lastname"
GITUSER="YOURGITHUBID"

MONGOPASSWORD=mongopassword

CHAMELEONUSERNAME=chameleonusername
CHAMELEONPASSWORD=chameleonpassword

EXAMPPLECOMMAND=mycommand

CLOUD=chameleon

# --------------------------------------------------------------------------
# IMPROVEMENT SUGGESTIONS
# --------------------------------------------------------------------------

# Gregor: there may be even the possibility to find first and lastname from the
# registered user

# NET USER loginname /DOMAIN | FIND /I " name "

# --------------------------------------------------------------------------
# DO NOT MODIFY FROM HERE
# --------------------------------------------------------------------------


# --------------------------------------------------
# Create the cloudmesh workspace directory
# Note: Do NOT use the word 'cloudmesh' or an underscore '_'
# Change tp the cm workspace directory
# --------------------------------------------------
cd ~
mkdir cm
cd cm

# --------------------------------------------------
# Install Cloudmesh Installer
# --------------------------------------------------
pip install cloudmesh-installer

# --------------------------------------------------
# Clone and install CM repos
# Note: this step will take ~8 minutes
# --------------------------------------------------
cloudmesh-installer git clone $BUNDLE
cloudmesh-installer git pull $BUNDLE
cloudmesh-installer install $BUNDLE

# --------------------------------------------------
# create a cloudmesh.yaml file and Validate the install worked
# --------------------------------------------------

cms help


# --------------------------------------------------
# Update your .yaml file
# --------------------------------------------------

# Cloudmesh Profile
# --------------------------------------------------
cms config set cloudmesh.profile.firstname="$FIRSTANME"
cms config set cloudmesh.profile.lastname="$LASTNAME"
cms config set cloudmesh.profile.email="$USERNAME@iu.edu"
cms config set cloudmesh.profile.user=$USERNAME
cms config set cloudmesh.profile.github=$YOURGITHUBID

# MongoDb attributes
# --------------------------------------------------
cms config set cloudmesh.data.mongo.MONGO_USERNAME=admin
cms config set cloudmesh.data.mongo.MONGO_PASSWORD="$MONGOPASSWORD"
cms config set cloudmesh.data.mongo.MONGO_AUTOINSTALL=True

# Chameleon cloud attributes
# --------------------------------------------------
cms config set cloudmesh.cloud.chameleon.credentials.OS_USERNAME="$CHAMELEONUSERNAME"
cms config set chameleon.cloud.chameleon.credentials.OS_PASSWORD="$CHAMELEONPASSWORD"

# Check the .yaml file
cms config check



# --------------------------------------------------
# Install MongoDB
# Note: For Windows10 press the [Ignore] button for this error:
# Service 'MongoDB Server (MongoDB) failed to start. Verify that you have sufficient priviledges to start system services.'
# --------------------------------------------------
cms admin mongo install

# --------------------------------------------------
# Call the Initialize method a few times (knwon issue)
# https://cloudmesh.github.io/cloudmesh-manual/api/cloudmesh.init.command.html
# --------------------------------------------------
cms init
cms init

# --------------------------------------------------
# Add the local key
# --------------------------------------------------

cms key add $USERNAME --source=ssh
cms set key=$USERNAME

# --------------------------------------------------
# Test install by checking Chamelon cloud
# --------------------------------------------------

cms set cloud=$CLOUD
cms key upload $USERNAME --cloud=$CLOUD
cms image list --refresh
cms flavor list --refresh
cms vm list --refresh

