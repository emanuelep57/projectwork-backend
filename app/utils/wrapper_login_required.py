from functools import wraps

from flask_login import login_required


def login_required_restx(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
