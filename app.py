# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
from GestureTypingSuggestion import GestureTypingSuggestion
import logging

gts = GestureTypingSuggestion()

app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = 'GESTURE_TYPE'

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

IP = '0.0.0.0'
PORT = 8080


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/request/suggestions/key")
def request_suggestions_key():
    sequence = request.args.get('sequence')
    sequence = ''.join(sequence.split(','))
    suggestions = gts.get_suggestions_from_key(sequence, 10)
    return jsonify(suggestions)


@app.route("/request/suggestions/position")
def request_suggestions_position():
    sequence = request.args.get('sequence')
    sequence = sequence.split(',')
    positions = []
    for i in range(0, len(sequence), 2):
        positions.append([float(sequence[i]), float(sequence[i+1])])
    suggestions = gts.get_suggestions_from_position(positions, 10)
    return jsonify(suggestions)


if __name__ == '__main__':
    app.run(host=IP, port=PORT)
