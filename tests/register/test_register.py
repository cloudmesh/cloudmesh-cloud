###############################################################
# pytest -v --capture=no tests/register/test_register.py
# pytest -v  tests/register/test_register.py
# pytest -v --capture=no  tests/register/test_register.py::Test_register::<METHODNAME>
###############################################################

from cloudmesh.common.Shell import Shell

import pytest
from cloudmesh.common.util import HEADING
from cloudmesh.common.Benchmark import Benchmark

Benchmark.debug()


@pytest.mark.incremental
class Test_register:
    services = ['storage', "compute", "volume"]

    def setup(self):
        pass

    def rprint(self, r):
        print(". Begin .", 70 * ".")
        print(r)
        print(". End   .", 70 * ".")

    def test_list(self):
        """
        Method to return list of all services and related kinds.
        :return:
        """
        HEADING()
        Benchmark.Start()
        result = Shell.execute("cms register list", shell=True)
        Benchmark.Stop()
        assert 'INFO: Services to be registered' in result, "result cannot be null"
        self.rprint(result)
        Benchmark.Status(True)

    def _test_list_kinds(self, service="compute"):
        """
        Method to list all kinds for given service.
        :param service: Name of the service.
        :return:
        """
        list_kind_cmd = f"cms register list --service={service}"
        Benchmark.Start()
        result = Shell.execute(list_kind_cmd, shell=True)
        Benchmark.Stop()
        assert 'Error' not in result and 'suitable' not in result, f"Error listing kind for {service}"
        return result

    def test_list_kinds(self):
        """
        Method to return list of kinds for all supported services.
        :return:
        """
        HEADING()
        #Get kind for each service.
        for service in self.services:
            result = self._test_list_kinds(service)
            self.rprint(result)

        Benchmark.Status(True)

    def test_list_google_compute_sample(self):
        """
        Method to list sample for google compute.
        :return:
        """
        HEADING()
        service = self.services[1]
        kind = "google"
        list_sample_cmd = f"cms register list sample --service={service} --kind={kind}"
        Benchmark.Start()
        result = Shell.execute(list_sample_cmd, shell=True)
        Benchmark.Stop()
        assert 'Error' not in result, f"Error listing sample for {kind}-{service}."
        assert 'suitable provider not found' not in result, f"Error listing sample for {kind}-{service}."
        assert result is not None, f"Error listing sample for {kind}-{service}."

        #If success, print the result.
        self.rprint(result)
        Benchmark.Status(True)

    def test_list_google_storage_sample(self):
        """
        Method to return sample for google storage.
        :return:
        """
        HEADING()
        service = self.services[0]
        kind = "google"
        list_sample_cmd = f"cms register list sample --service={service} --kind={kind}"
        Benchmark.Start()
        result = Shell.execute(list_sample_cmd, shell=True)
        Benchmark.Stop()
        assert 'Error' not in result and 'suitable' not in result \
               and result != None, f"Error listing sample for {kind}-{service}."

        # If success, print the result.
        self.rprint(result)
        Benchmark.Status(True)

    def test_update_using_file(self):
        """
        Method to register google compute using json file with default name google
        :return:
        """
        HEADING()
        service = self.services[1]  # compute service
        kind = "google"
        json_file = "~/cm/cloudmesh-google/tests/google_sample_credentials.json"
        update_json_cmd = f"cms register update --service={service} " \
                          f"--kind={kind} --file={json_file}"
        Benchmark.Start()
        result = Shell.execute(update_json_cmd, shell=True)
        Benchmark.Stop()
        assert 'Registered {service} service for {kind} provider' not in result, \
                f"Error register update for {kind}-{service}."

        # If success, print the result.
        self.rprint(result)
        Benchmark.Status(True)

    def test_update_using_file_with_name(self):
        """
        Method to register google compute with a custom name.
        :return:
        """
        HEADING()
        service = self.services[1]  # compute service
        kind = "google"
        name = "testGoogle"
        json_file = "~/cm/cloudmesh-google/tests/google_sample_credentials.json"
        update_json_cmd = f"cms register update --service={service} " \
                          f"--kind={kind} --name={name} --file={json_file}"
        Benchmark.Start()
        result = Shell.execute(update_json_cmd, shell=True)
        Benchmark.Stop()
        assert 'Registered {service} service for {kind} provider' not in result, \
                f"Error register update for {kind}-{service}."

        # If success, print the result.
        self.rprint(result)
        Benchmark.Status(True)


    def test_update_using_file_with_attrs(self):
        """
        Method to register google compute with file, customer name and
        attributes to override values from JSON file.
        :return:
        """
        HEADING()
        service = self.services[1]  # compute service
        kind = "google"
        name = "testGoogle"
        json_file = "~/cm/cloudmesh-google/tests/google_sample_credentials.json"
        update_json_cmd = f"cms register update --service={service} " \
                          f"--kind={kind} --name={name} " \
                          f"--file={json_file} project_id=pytest_project"
        Benchmark.Start()
        result = Shell.execute(update_json_cmd, shell=True)
        Benchmark.Stop()
        assert 'Registered {service} service for {kind} provider' not in result, \
                f"Error register update for {kind}-{service}."

        # If success, print the result.
        self.rprint(result)
        Benchmark.Status(True)

    def test_remove(self):
        """
        Method to remove google compute entry with default name google.
        :return:
        """
        HEADING()
        service = self.services[1]  # compute service
        kind = "google"
        update_json_cmd = f"cms register remove --service={service} --kind={kind}"
        Benchmark.Start()
        result = Shell.execute(update_json_cmd, shell=True)
        Benchmark.Stop()

        assert f"Removed {kind} from {kind} service" not in result, \
                f"Error removing {kind} from cloudmesh.yaml."

        # If success, print the result.
        self.rprint(result)
        Benchmark.Status(True)

    def test_remove_with_name(self):
        """
        Method to remove google compute entry with custom name.
        :return:
        """
        HEADING()
        service = self.services[1]  # compute service
        kind = "google"
        name = "testGoogle"
        update_json_cmd = f"cms register remove --service={service} " \
                          f"--kind={kind} --name={name} "
        Benchmark.Start()
        result = Shell.execute(update_json_cmd, shell=True)
        Benchmark.Stop()

        assert f"Removed {name} from {kind} service" not in result, \
            f"Error register removing {name} for {kind}-{service}."

        # If success, print the result.
        self.rprint(result)
        Benchmark.Status(True)
