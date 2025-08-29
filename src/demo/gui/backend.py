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
        idx = 1
        while True:
            data = client.metrics.get_metrics(idx)
            if data is None:
                time.sleep(0.2)
                continue
            else:
                idx += 1
                socketio.emit("update_data", data)
                time.sleep(0.2)

    @socketio.on("adjust_config")
    def handle_adjust_config(data):
        asyncio.run(client.adjust_config(data))

    thread = threading.Thread(target=background_data_updater)
    thread.daemon = True
    thread.start()

    return app, socketio
