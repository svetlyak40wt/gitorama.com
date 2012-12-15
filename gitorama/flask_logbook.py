import logbook
import logging
import uuid

from logbook.compat import redirect_logging

from flask import _request_ctx_stack


def create_logger(app):
    if app.config.get('ENVIRONMENT') == 'production':
        server_addr = ('localhost', 25)
    else:
        server_addr = ('localhost', 2525)

    mail_handler = logbook.MailHandler(
        'server-error@gitorama.com',
        ['svetlyak.40wt@gmail.com'],
        server_addr=server_addr,
        level='DEBUG',
        format_string=u'''Subject: ERROR at gitorama.com

[{record.time:%Y-%m-%d %H:%M}] {record.extra[request_id]}: {record.level_name}: {record.channel}: {record.message}''',
        related_format_string=u'[{record.time:%Y-%m-%d %H:%M}] {record.extra[request_id]}: {record.level_name}: {record.channel}: {record.message}',
    )
    file_handler = logbook.FileHandler(
        app.config['LOG_FILE'],
        level='DEBUG',
        format_string=u'[{record.time:%Y-%m-%d %H:%M}] {record.extra[request_id]}: {record.level_name}: {record.channel}: {record.message}'
    )

    def inject_id(record):
        record.extra['request_id'] = getattr(_request_ctx_stack.top, 'logbook_request_id', None)

    logger = logbook.NestedSetup([
        logbook.NullHandler(),
        logbook.FingersCrossedHandler(mail_handler, reset=True),
        logbook.FingersCrossedHandler(file_handler, reset=True, bubble=True),
        logbook.Processor(inject_id),
    ])
    return logger


class Logbook(object):
    def __init__(self, app):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        redirect_logging()
        logging.root.level = logging.DEBUG

        def process_request():
            logger = create_logger(app)
            _request_ctx_stack.top.logbook_logger = logger
            _request_ctx_stack.top.logbook_request_id = uuid.uuid4()
            logger.push_thread()

        def teardown_request(exc):
            logger = getattr(_request_ctx_stack.top, 'logbook_logger', None)
            if logger is not None:
                logger.pop_thread()

        app.before_request(process_request)
        app.teardown_request(teardown_request)

