"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from logging import FileHandler, StreamHandler, Filter, Formatter, getLogger

def init_app(app, name=''):
    """
    Configures the provided app's logger.
    
    :param app: the application object to configure the logger
    :param name: the name of the logger to create and configure
    """

    # flask app object automatically registers its own debug logger if app.debug
    # is True. Remove it becuase debug logging is handled here instead.
    del app.logger.handlers[:]

    log_path = app.config['LOG_PATH']
    log_level = app.config['LOG_LEVEL']
    log_filter = app.config['LOG_FILTER']
    log_ignore = app.config['LOG_IGNORE']

    handler = FileHandler(log_path) if log_path else StreamHandler() 
    handler.setLevel(log_level.upper() or ('DEBUG' if app.debug else 'WARNING'))
    handler.addFilter(MultiNameFilter(log_filter, log_ignore))
    handler.setFormatter(Formatter(
        '%(asctime)s %(process)s %(thread)-15s %(name)-10s %(levelname)-8s %(message)s', 
        '%H:%M:%S' if app.debug else '%Y-%m-%d %H:%M:%S%z'))

    logger = getLogger(name)
    logger.setLevel(handler.level)
    logger.addHandler(handler)

class MultiNameFilter(Filter):

    def __init__(self, allow, deny):
        self.allow = self.format_list(allow)
        self.deny = self.format_list(deny)
        super(MultiNameFilter, self).__init__()

    def filter(self, record):
        return (not self.allow or record.name in self.allow) and \
               (not self.deny or record.name not in self.deny) 
    
    def format_list(self, value):
        return value.split(',') if value is str else (value or [])

