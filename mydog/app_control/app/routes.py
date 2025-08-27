from flask import Blueprint, send_from_directory
import os

bp = Blueprint('routes', __name__)

@bp.get('/')
def index():
    web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web'))
    return send_from_directory(web_dir, 'index.html')

@bp.get('/<path:path>')
def static_proxy(path):
    web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web'))
    return send_from_directory(web_dir, path)