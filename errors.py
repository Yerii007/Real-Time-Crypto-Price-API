from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({
            "error": e.name,
            "message": e.description
        }), e.code

    @app.errorhandler(Exception)
    def handle_general_exception(e):
        app.logger.exception("Unhandled exception")
        return jsonify({"error": "internal_server_error", "message": "Internal server error"}), 500