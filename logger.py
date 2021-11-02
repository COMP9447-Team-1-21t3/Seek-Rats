import logging
import logging.handlers


class clsLogging(object):
    # fh: file handler
    # ch: console handler
    def __init__(self, path, filename):
        self._scriptloc = path
        self._scriptname = filename
        self._fh = None
        self._ch = None
        # Configure debug logging
        # create logger with '__main__'
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

    def setup(self):
        # create rotating filehandler which logs messages to file
        self._fh = logging.handlers.RotatingFileHandler(
            self._scriptloc + self._scriptname + '.log', maxBytes=500000, backupCount=5)
        self._fh.setLevel(logging.DEBUG)
        # create console handler which sends log messages to console
        self._ch = logging.StreamHandler()
        self._ch.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self._fh.setFormatter(formatter)
        self._ch.setFormatter(formatter)
        # add the handlers to the logger
        self._logger.addHandler(self._fh)
        self._logger.addHandler(self._ch)
        return self._logger

    def closeHandlers(self):
        self._fh.close()
        self._ch.close()
