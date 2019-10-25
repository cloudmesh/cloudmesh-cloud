@echo off

:: --------------------------------------------------------------------------
:: Purpose: Install Cloudmesh Storage package. T
:: his script will install Cloudmesh Storage, MongoDb, and
:: generate a plugin directory on Windows OS
:: Authors: Gregor von Laszewski (laszewski@gmail.com)
::         wscreen
:: --------------------------------------------------------------------------

set EXAMPPLECOMMAND=mycommand

:: --------------------------------------------------
:: Generate a cloudmesh-EXAMPLE folder in which we put the command
:: --------------------------------------------------
cms sys command generate %EXAMPLECOMMAND%

:: --------------------------------------------------
:: Install %EXAMPLECOMMAND%
:: --------------------------------------------------
cd cloudmesh-%EXAMPLECOMMAND%

pip install -e .

:: --------------------------------------------------
:: Test running %EXAMPLECOMMAND% with and without params
:: --------------------------------------------------
:: cms %EXAMPLECOMMAND% --file "c:\\mydir\\myfile.txt"
cms %EXAMPLECOMMAND% list

:: --------------------------------------------------
:: Open Visual Studio Code in this directory
:: --------------------------------------------------
:: code .
