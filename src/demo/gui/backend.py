import asyncio
from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
import threading
import time

def create_flask_app(client):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret!"
    socketio = SocketIO(app, async_mode="threading")

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    # Send metrics every second
    def background_data_updater():
        while True:
            time.sleep(1)
            data = {
            }
            socketio.emit("update_data", data)

    @socketio.on("adjust_config")
    def handle_adjust_config(data):
        # Example: {"geoQP": 24, "attQP": 18, "sequence": "loot"}
        asyncio.run(client.adjust_config(data))

    @app.before_request
    def start_background_thread():
        if not hasattr(app, "thread_started"):
            app.thread_started = True
            thread = threading.Thread(target=background_data_updater)
            thread.daemon = True
            thread.start()

    return app, socketio
