from flask import Blueprint, render_template
from flask_login import current_user, login_required

web = Blueprint('web', __name__)


@web.route('/')
def index():
    return render_template('index.html', user=current_user)


@web.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)
