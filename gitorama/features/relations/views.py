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

    for idx in range(num_days):
        if followers[idx] is None:
            siblings = []
            if idx > 0:
                siblings.append(followers[idx - 1])
            if idx < num_days - 1:
                siblings.append(followers[idx + 1])
            siblings = filter(None, siblings)

            if siblings:
                followers[idx] = sum(siblings) / len(siblings)

    return render_template(
        'relations.html',
        followers=reversed(followers),
        start=today - datetime.timedelta(days=num_days),
    )

