# Global vars
import logging
from app.baseconfig import erblconfig
import numpy as np

_config = None
_logger = None

class erlBase(object):

    def __init__(self, *args, **kwargs):
        global _config
        if _config is None:
            _config=erblconfig()

        self.config = _config
        self.x = np.arange(self.config.aquisitionsize)

        global _logger
        if _logger is None:
            # create logger
            _logger = logging.getLogger('simple_example')
            _logger.setLevel(logging.DEBUG)

            # create console handler and set level to debug
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

            # add formatter to ch
            ch.setFormatter(formatter)

            # add ch to logger
            _logger.addHandler(ch)

        self.logger = _logger


