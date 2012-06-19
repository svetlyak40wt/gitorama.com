import datetime

from pymongo import DESCENDING
from flask import (
    Blueprint, request, render_template,
    session, g, current_app, request
)

from ... import core


bp = Blueprint('relations', __name__)


@bp.route("/")
def index():
    today = datetime.datetime.utcnow()
    num_days = 30

    db = core.get_db()
    query = db.user_stats.find(
        {'login': request.user['login']},
        fields=['followers', 'date'],
        sort=[('date', DESCENDING)],
        limit=num_days,
    )
    followers = [None] * num_days
    for item in query:
        day_from_today = (today - item['date']).days
        if day_from_today < num_days:
            followers[day_from_today] = item['followers']

    values = filter(None, followers)
    prev_value = values and values[0] or 0

    for idx, value in enumerate(followers):
        if value is None:
            followers[idx] = prev_value
        else:
            prev_value = value

    return render_template(
        'relations.html',
        followers=reversed(followers),
        events=db.events.find({'login': request.user['login']}),
        start=today - datetime.timedelta(days=num_days),
    )

@bp.route("/raise-exception")
def raise_exception():
    raise RuntimeError('blah, debug=%r' % current_app.debug)

