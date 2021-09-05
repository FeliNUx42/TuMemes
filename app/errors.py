from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(400)
def error_400(error):
  title = "Bad Request (400)"
  message = "The CSRF token is missing."
  return render_template("main/error.html", title=title, message=message), 400

@errors.app_errorhandler(403)
def error_403(error):
  title = "You don't have permission to do that (403)"
  message = "Please check your account and try again."
  return render_template("main/error.html", title=title, message=message), 403

@errors.app_errorhandler(404)
def error_404(error):
  title = "Oops. Page Not Found (404)"
  message = "That page does not exist. Please try a different location."
  return render_template("main/error.html", title=title, message=message), 404

@errors.app_errorhandler(500)
def error_500(error):
  title = "Something went wrong (500)"
  message = "We're experiencing some trouble on our end. Please try again in the near future."
  return render_template("main/error.html", title=title, message=message), 500