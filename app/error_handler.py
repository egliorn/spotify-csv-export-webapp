from flask import Blueprint, redirect, url_for, flash, render_template
from tekore import BadRequest, ServiceUnavailable


bp = Blueprint('error_handler', __name__)


@bp.app_errorhandler(BadRequest)
def bad_request(e):
    flash('Access declined.')
    return redirect(url_for('main.index'))


@bp.app_errorhandler(502)
def service_unavailable(e):
    return render_template('error.html',
                           code='502',
                           error='Bad gateway.',
                           msg=''), 503


@bp.app_errorhandler(ServiceUnavailable)
def service_unavailable(e):
    return render_template('error.html',
                           code='503',
                           error='Service unavailable.',
                           msg='The Spotify server is currently unavailable. Try again later.'), 503


@bp.app_errorhandler(400)
def bad_request(e):
    return render_template('error.html',
                           code='400',
                           error='Bad request.',
                           msg='Something went wrong.'), 400


@bp.app_errorhandler(401)
def unauthorised(e):
    return render_template('error.html',
                           code='401',
                           error='Unauthorised.',
                           msg=''), 401


@bp.app_errorhandler(404)
def not_found(e):
    return render_template('error.html',
                           code='404',
                           error='Page not found.',
                           msg=''), 404

