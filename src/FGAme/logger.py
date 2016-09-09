"""
Logging
=======

The following debug levels are available: `debug`, `info`, `warning`, `error`
and `critical`.

Examples::

    from FGAme.core import log

    log.info('message: This is an info message.')
    log.debug('message: This is a debug message.')

    try:
        raise Exception('foo')
    except Exception:
        log.error('Something happened!')

The message itself consists of two parts split by a colon: a title and a body.
Usually the title part consists of the python path to where the logging event
occurs::

    log.info('FGAme.app: This is a test')

This appears as::

    [INFO   ] [FGAme.app   ] This is a test.

Log history
-----------

Even with logging disabled, you have access to the last 100 messages.

    from FGAme.logger import log_history
    print(log_history.history)

"""
# This code is based in the logger module from Kivy
import logging
import os
import sys

__all__ = ('log', 'log_history')
sys_stderr = sys.stderr

# Colorful output
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = list(range(8))

COLORS = {
    'TRACE': MAGENTA,
    'WARNING': YELLOW,
    'INFO': GREEN,
    'DEBUG': CYAN,
    'CRITICAL': RED,
    'ERROR': RED}

logging.TRACE = 9
LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL}


def formatter_message(message, use_color=True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ)
        message = message.replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message


class LoggerHistory(logging.Handler):
    history = []

    def emit(self, message):
        LoggerHistory.history = [message] + LoggerHistory.history[:100]


class ConsoleHandler(logging.StreamHandler):
    def filter(self, record):
        try:
            msg = record.msg
            k = msg.split(':', 1)
            if k[0] == 'stderr' and len(k) == 2:
                sys_stderr.write(k[1] + '\n')
                return False
        except IndexError:
            pass
        return True


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        try:
            msg = record.msg.split(':', 1)
            if len(msg) == 2:
                record.msg = '[%-12s]%s' % (msg[0], msg[1])
        except IndexError:
            pass
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = (
                COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ)
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


# Main logger is saved into the .log variable
log = logging.getLogger('FGAme')
log.logfile_activated = None
logging.root = log
log.addHandler(LoggerHistory())
use_color = os.environ.get('TERM') in ('xterm', 'rxvt', 'rxvt-unicode')
color_fmt = formatter_message('[%(levelname)-18s] %(message)s', use_color)
formatter = ColoredFormatter(color_fmt, use_color=use_color)
console = ConsoleHandler()
console.setFormatter(formatter)
log.addHandler(console)
log_history = LoggerHistory.history
