from cm4.configuration.config import Config
from cm4.common.debug import myself, HEADING
from pprint import pprint


# nosetests -v --nocapture tests/test_config.py

def test_config():
    HEADING(myself())
    config = Config()

    print(config)

    #pprint(config.credentials('local'))

    assert config is not None
    #assert 'cloud' in config.cloud

