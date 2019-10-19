cd ~
# --------------------------------------------------
# Create a new virtual environment in the subdirectory
# and configure the current shell to use it as the
# default python environment
# --------------------------------------------------
python -m venv ENV3
# --------------------------------------------------
# Upgrade Pip to use the newest version of pip in ENV3
# --------------------------------------------------
python -m pip install --upgrade pip

# --------------------------------------------------
# Activate your virtualenv:
# (e.g. (env3)Your-Computer:project_folder UserName$)
# lets you know that the virtual env is active.
# Type: 'deactivate' to exit virtual environment
# --------------------------------------------------
CALL .\ENV3\Scripts\activate
