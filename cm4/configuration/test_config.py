from cm4.configuration.config import Config


class TestConfig:
    """
    Functional tests for the configuration Config class
    """

    def setUp(self):
        self._conf = Config()

    def test_get_notfound_defaults(self):
        assert self._conf.get("nothere") is None
        assert self._conf.get("nothere", {}) == {}
        assert self._conf.get("default.nothere") is None
        custom_default = {"foo" : "bar"}
        assert self._conf.get("default.nothere", custom_default) == custom_default

    def test_get_shorthand(self):
        raw_result = self._conf._cloudmesh.get("default").get("cloud")    
        default_result = self._conf.get("default").get("cloud")
        short_result = self._conf.get("default.cloud")
        assert short_result == default_result == raw_result

        az_conf = self._conf.get("cloud.azure")
        az_id = az_conf.get('credentials.AZURE_SUBSCRIPTION_ID')
        assert az_id is not None

    def test_set(self):
        before = self._conf.get("default.cloud")
        self._conf.set("default.cloud", "testcloud")

        new_config = Config()
        after = new_config.get("default.cloud")

        assert before != after
        new_config.set("default.cloud", before)

