from flask import Blueprint, render_template, jsonify, request

errors = Blueprint('errors', __name__)
# second value is status code, default is 200 (ok)


@errors.app_errorhandler(404)
def error_404(error):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('errors/404.html'), 404


@errors.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


# @errors.app_errorhandler(500)
# def error_500(error):
#     return render_template('errors/500.html'), 500

@errors.app_errorhandler(500)
def error_500(error):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('errors/500.html'), 500
