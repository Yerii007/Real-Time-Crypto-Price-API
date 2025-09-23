import time
import threading
from flask import current_app

def start_background_updater(app):
    def update_loop():
        with app.app_context():
            while True:
                try:
                    from services.crypto_service import update_db_with_api_data
                    success = update_db_with_api_data()
                    if success:
                        app.logger.info("Background update: Success")
                    else:
                        app.logger.warning("Background update: No data")
                except Exception as e:
                    app.logger.error(f"Background update failed: {e}")
                time.sleep(app.config["UPDATE_INTERVAL"])

    thread = threading.Thread(target=update_loop, daemon=True)
    thread.start()