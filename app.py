# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask_socketio import SocketIO
from GestureTypingSuggestion import GestureTypingSuggestion
import logging

gts = GestureTypingSuggestion()

app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = 'GESTURE_TYPE'
socketio = SocketIO(app)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

IP = '0.0.0.0'
PORT = 8080


@app.route('/')
def index():
    return render_template('index.html')


def suggestions_thread(sequence):
    suggestions = gts.get_suggestions_from_key(sequence, 10)
    socketio.emit(
        "response/suggestions",
        {
            'suggestions': suggestions
        },
        namespace='/mynamespace'
    )


@socketio.on("request/suggestions", namespace='/mynamespace')
def request_videos(sequence):
    socketio.start_background_task(
        suggestions_thread, sequence
    )


if __name__ == '__main__':
    socketio.run(app, host=IP, port=PORT, debug=False)
