"""VM Manager.

Usage:
  vm_manager.py vm start [--provider=<cloud_provider>]
  vm_manager.py vm stop [--provider=<cloud_provider>]
  vm_manager.py vm status [--provider=<cloud_provider>]

  vm_manager.py -h

Options:
  -h --help     Show this screen.

Description:
   This VM manager starts a given vm type. If a vm type is not specified, the default one is used.

Example:
   vm_manager.py vm start aws Will start the aws VMs
"""
from docopt import docopt
from cm4.configuration.config import Config
from deprecated.vm_manager import AWSProvider


def process_arguments(arguments):
    provider = arguments['--provider']
    config = Config()

    if not provider:
        provider = config.get("default.cloud")

    if provider == "aws":
        cloud_manager = AWSProvider(config)
    else:
        cloud_manager = AWSProvider(config)

    if arguments['start']:
        cloud_manager.start()
    elif arguments['stop']:
        cloud_manager.stop()
    elif arguments['status']:
        cloud_manager.status()


def main():
    """
    Main function for the VM Manager. Processes the input arguments.

    """
    arguments = docopt(__doc__, version='Cloudmesh VM Manager 0.1')
    process_arguments(arguments)


if __name__ == "__main__":
    main()
