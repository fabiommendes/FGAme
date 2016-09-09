# -*- coding: utf8 -*-
'''
Realiza o logging do funcionamento do FGAme
===========================================

Diferentes níveis estão disponíveis : `trace`, `debug`, `info`, `warning`, `error`
e `critical`.

Exemplos::

    from FGAme.core import log

    log.info('título: Essa é uma mensagem informativa.')
    log.debug('título: Essa é uma mensagem de debug.')

    try:
        raise Exception('bleh')
    except Exception:
        log.exception('Something happened!')

A mensagem passada para o logger é dividia em duas partes separadas por dois
pontos (:). A primeira parte corresponde ao título e a segunda à mensagem
propriamente dita.

    log.info('FGAme.app: Este é um teste')

    # aparece como

    [INFO   ] [FGAme.app   ] Este é um teste

História
--------

Mesmo com o logger desabilitado, você tem acesso às últimas 100 mensagens::

    from FGAme.core import log_history
    print(log_history.history)

'''
#
# This code is based in the logger module from Kivy
#
import logging
import os
import sys
from functools import partial


__all__ = ('log', 'log_history')
sysstderr = sys.stderr

# Sequências que marcam saída colorida
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
    'trace': logging.TRACE,  # @UndefinedVariable
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL}


def formatter_message(message, use_color=True):
    '''Formata a mensagem para saída colorida e formatada.'''
    
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
                sysstderr.write(k[1] + '\n')
                return False
        except:
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
        except:
            pass
        levelname = record.levelname
        if record.levelno == logging.TRACE:  # @UndefinedVariable
            levelname = 'TRACE'
            record.levelname = levelname
        if self.use_color and levelname in COLORS:
            levelname_color = (
                COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ)
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


#
# Cria logger principal na variável log
#
log = logging.getLogger('FGAme')
log.logfile_activated = None
log.trace = partial(log.log, logging.TRACE)  # @UndefinedVariable
logging.root = log
log.addHandler(LoggerHistory())
use_color = os.environ.get('TERM') in ('xterm', 'rxvt', 'rxvt-unicode')
color_fmt = formatter_message('[%(levelname)-18s] %(message)s', use_color)
formatter = ColoredFormatter(color_fmt, use_color=use_color)
console = ConsoleHandler()
console.setFormatter(formatter)
log.addHandler(console)
log_history = LoggerHistory.history
