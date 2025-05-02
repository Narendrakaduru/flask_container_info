from flask import Flask, jsonify, render_template
import socket

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/hostname')
def hostname():
    return jsonify({'hostname': socket.gethostname()})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)