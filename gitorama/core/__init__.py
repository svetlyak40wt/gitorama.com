from flask import (
    Blueprint, request, render_template,
    session
)

core = Blueprint('core', __name__)

@core.route("/")
def index():
    request.user = session.get('token')
    return render_template('index.html')



