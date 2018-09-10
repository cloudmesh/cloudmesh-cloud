from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


class cloudmesh

  def config(name=“~/.cloudmesh/cloudmesh.yaml”)
    # reads in the yaml file

  def get_driver(cloudname=None)
    # if cloudname=none get the default cloud
    # credentials = ….
    # return the driver for that cloud

  # now if you do that right you cans implify libcloud use with


if __name__ == '__main__':
  connection = cm.get_driver(“azure")

  # retrieve available images and sizes
  images = connection.list_images()
