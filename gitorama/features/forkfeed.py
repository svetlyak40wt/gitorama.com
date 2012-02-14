import anyjson
import datetime
import pymongo

from urlparse import urljoin

from flask import (
    Blueprint, request, render_template,
    session, g, current_app
)

from ..core import net
from ..core.cache import cache


bp = Blueprint('forkfeed', __name__)


@bp.route("/")
def index():
    return render_template('forkfeed.html')

