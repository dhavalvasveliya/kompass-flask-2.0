from flask import Flask
from flask import render_template
from flask import request
from flask import send_from_directory
import subprocess


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'GET' or 'POST':
        return render_template('home.html')


def run_kopass_process():
    global process
    process = subprocess.Popen(['python3', 'kompass.py'], shell=False)


def stop_kopass_process():
    process.kill()


@app.route('/results/start')
def start_results():
    run_kopass_process()
    return render_template('home.html')


@app.route('/results/stop')
def stop_results():
    try:
        stop_kopass_process()
    except:
        pass
    return render_template('home.html')


if __name__ == "__main__":
    app.run()