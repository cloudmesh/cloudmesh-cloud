@echo off

:: --------------------------------------------------------------------------
:: Purpose: Install Cloudmesh Storage package. T
:: his script will install Cloudmesh Storage, MongoDb, and
:: generate a plugin directory on Windows OS
:: Authors: Gregor von Laszewski (laszewski@gmail.com)
::         wscreen
:: --------------------------------------------------------------------------

:: use the folloing names for a bundle

:: set BUNDLE=cloud
:: set BUNDLE=storage

set BUNDLE=storage

:: Set a unique username here. It must not have spaces or cahracters not in a-Z0-9

:: set USERNAME=%username%
set USERNAME="IUUSERNAME"

set FIRSTNAME="Firstname"
set LASTNAME="Lastname"
set GITUSER="YURGITHUBID"

set MONGOPASSWORD=mongopassword

set CHAMELEONUSERNAME=chameleonusername
set CHAMELEONPASSWORD=chameleonpassword

set EXAMPPLECOMMAND=mycommand

set CLOUD=chameleon

:: --------------------------------------------------------------------------
:: IMPROVEMENT SUGGESTIONS
:: --------------------------------------------------------------------------

:: Gregor: there may be even the possibility to find first and lastname from the
:: registered user

:: NET USER loginname /DOMAIN | FIND /I " name "

:: --------------------------------------------------------------------------
:: DO NOT MODIFY FROM HERE
:: --------------------------------------------------------------------------

:: --------------------------------------------------
:: Upgrade all Pip packages to the newest available version
:: --------------------------------------------------
python -m pip install --upgrade pip

:: --------------------------------------------------
:: Create the cloudmesh workspace directory
:: Note: Do NOT use the word 'cloudmesh' or an underscore '_'
:: --------------------------------------------------
mkdir cm

:: --------------------------------------------------
:: Change tp the cloudmesh workspace directory
:: --------------------------------------------------
cd cm

:: --------------------------------------------------
:: Create a new virtual environment in the subdirectory
:: and configure the current shell to use it as the
:: default python environment
:: --------------------------------------------------
python -m venv ENV3

:: --------------------------------------------------
:: Activate your virtualenv:
:: (e.g. (env3)Your-Computer:project_folder UserName$)
:: lets you know that the virtual env is active.
:: Type: 'deactivate' to exit virtual environment
:: --------------------------------------------------
CALL .\ENV3\Scripts\activate

:: --------------------------------------------------
:: Install Cloudmesh Installer
:: --------------------------------------------------
pip install cloudmesh-installer

:: --------------------------------------------------
:: Clone and install CM repos
:: Note: this step will take ~8 minutes
:: --------------------------------------------------
cloudmesh-installer git clone %BUNDLE%
cloudmesh-installer git pull %BUNDLE%
cloudmesh-installer install %BUNDLE% -e

:: Validate the install worked
cms help


:: --------------------------------------------------
:: Update your .yaml file
:: --------------------------------------------------

:: Cloudmesh Profile
:: --------------------------------------------------
cms config set cloudmesh.profile.firstname="""%FIRSTANME%"""
cms config set cloudmesh.profile.lastname="""%LASTNAME%"""
cms config set cloudmesh.profile.email="%USERNAME%@iu.edu"
cms config set cloudmesh.profile.user=%USERNAME%
cms config set cloudmesh.profile.github=%YOURGITHUBID%

:: MongoDb attributes
:: --------------------------------------------------
cms config set cloudmesh.data.mongo.MONGO_USERNAME=admin
cms config set cloudmesh.data.mongo.MONGO_PASSWORD="""%MONGOPASSWORD%"""
cms config set cloudmesh.data.mongo.MONGO_AUTOINSTALL=True

:: Chameleon cloud attributes
:: --------------------------------------------------
cms config set cloudmesh.cloud.chameleon.credentials.OS_USERNAME="""%CHAMELEONUSERNAME%"""
cms config set chameleon.cloud.chameleon.credentials.OS_PASSWORD="""%CHAMELEONPASSWORD%"""

:: Check the .yaml file
cms config check



:: --------------------------------------------------
:: Install MongoDB
:: Note: For Windows10 press the [Ignore] button for this error:
:: Service 'MongoDB Server (MongoDB) failed to start. Verify that you have sufficient priviledges to start system services.'
:: --------------------------------------------------
cms admin mongo install

:: --------------------------------------------------
:: Call the Initialize method a few times (knwon issue)
:: https://cloudmesh.github.io/cloudmesh-manual/api/cloudmesh.init.command.html
:: --------------------------------------------------
cms init
cms init

:: --------------------------------------------------
:: Add the local key
:: --------------------------------------------------

cms key add %USERNAME% --source=ssh
cms set key=%USERNAME

:: --------------------------------------------------
:: Test install by checking Chamelon cloud
:: --------------------------------------------------

cms config set cloud=%CLOUD%
cms key upload %USERNAME% --cloud=%CLOUD%
cms image list --refresh
cms flavor list --refresh
cms vm list --refresh

:: --------------------------------------------------
:: Generate a folder for your project
:: --------------------------------------------------
mkdir %EXAMPLECOMMAND%
cd %EXAMPLECOMMAND%
cms sys command generate %EXAMPLECOMMAND%

:: --------------------------------------------------
:: Install %EXAMPLECOMMAND%
:: --------------------------------------------------
pip install -e %EXAMPLECOMMAND%\cloudmesh-%EXAMPLECOMMAND%

:: --------------------------------------------------
:: Test running %EXAMPLECOMMAND% with and without params
:: --------------------------------------------------
:: cms %EXAMPLECOMMAND% --file "c:\\mydir\\myfile.txt"
cms %EXAMPLECOMMAND% list

:: --------------------------------------------------
:: Open Visual Studio Code in this directory
:: --------------------------------------------------
:: code .
