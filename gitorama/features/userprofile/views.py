import logging

from gitorama import core
from pymongo import DESCENDING

from flask import (
    Blueprint, request, render_template,
    session, g, current_app, abort
)


bp = Blueprint('userprofile', __name__)


@bp.route('/<username>')
def index(username):
    db = core.get_db()
    user = db.users.find_one({'login': username})
    if user is None:
        abort(404)
    stats = db.user_stats.find_one({'login': username}, sort=[('date', DESCENDING)])
    return render_template('userprofile.html', user=user, stats=stats)


@bp.route('/raise-error')
def raise_error():
    """View to test error logging.
    """
    logger = logging.getLogger('test')
    logger.info('Some info')
    logger.debug('Some debug')
    #logger.error('Some error')

    logging.getLogger('some-module').info('Another info')
    logging.getLogger('other-module').debug('And another debug')
    raise RuntimeError('blah')
    return '<html><head></head><body>Hello</body></html>'

