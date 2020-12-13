# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
from GestureTypingGAT import GestureTypingSuggestion
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
    try:
        sequence = request.args.get('sequence')
        sequence = sequence.split(',')
        positions = []
        for i in range(0, len(sequence), 2):
            positions.append([float(sequence[i]), float(sequence[i+1])])
        suggestions = gts.get_suggestions_from_position(positions, 10)
        return jsonify(suggestions)
    except Exception:
        return jsonify("")

@app.route("/request/suggestions/position_s")
def request_suggestions_position_small():
    try:
        sequence = request.args.get('sequence')
        sequence = sequence.split(',')
        positions = []
        for i in range(0, len(sequence), 2):
            positions.append([float(sequence[i]), float(sequence[i+1])])
        gts.isVisualize = False
        gts.isNormalize = False
        #suggestions = gts.get_corner_angle_sequence_from_position(positions)
        suggestions = gts.get_suggestions_from_position_by_angle(positions, 10)
        return jsonify(suggestions)
    except Exception:
        return jsonify("")

@app.route("/request/suggestions/key_pos")
def request_suggestions_key_and_position():
    sequence = request.args.get('sequence')
    sequence = sequence.split(';')
    positionTemp = sequence[1].split(',')
    keys = []
    keys = ''.join(sequence[0].split(','))
    positions = []
    for i in range(0, len(positionTemp), 2):
        positions.append([float(positionTemp[i]), float(positionTemp[i+1])])

    suggestions = gts.get_suggestions_from_keys_and_position(keys, positions, 10)
    return jsonify(suggestions)


if __name__ == '__main__':
    app.run(host=IP, port=PORT)
