import time
import threading

import RPi.GPIO as GPIO
GPIO.setwarnings(False)
# Use GPIO.BOARD instead of GPIO.BCM !!! See http://goo.gl/C87d5g
GPIO.setmode(GPIO.BOARD) 
# For 2Bulbs A, B
GPIO.setup(7, GPIO.IN)
GPIO.setup(11, GPIO.IN)

from flask import Flask, request, jsonify, render_template
from flask_bootstrap import Bootstrap


RUN_BLINK4BB_FLAG = False
RUN_INPUTB_FLAG = False
RELOAD_FREQUENCY = 10000
app = Flask(__name__)
app.config["BOOTSTRAP_SERVE_LOCAL"] = True
Bootstrap(app)


@app.route("/")
def index():
    bi = get_two_bulbs_info()
    nbf = RUN_BLINK4BB_FLAG
    sf = RUN_INPUTB_FLAG
    f = RELOAD_FREQUENCY
    return render_template("index.html", bi=bi, nbf=nbf, sf=sf, f=f)


@app.route("/api/v1/2bulbs/set")
def set_two_bulbs():
    GPIO.setup(7, GPIO.OUT)
    GPIO.setup(11, GPIO.OUT)
    if request.args.get('a') == "ON":
        GPIO.output(7,1)
    elif request.args.get('a') == "OFF":
        GPIO.output(7,0)
    if request.args.get('b') == "ON":
        GPIO.output(11,1)
    elif request.args.get('b') == "OFF":
        GPIO.output(11,0)
    return jsonify({ "success" : True })


@app.route("/api/v1/6noisybulbs/restart")
def restart_six_noisy_bulbs():
    global RUN_BLINK4BB_FLAG
    if RUN_BLINK4BB_FLAG:
        RUN_BLINK4BB_FLAG = False
        time.sleep(1)# wait for stopping blink4bb (max waiting time: 0.5 + 0.5 = 1)
    RUN_BLINK4BB_FLAG = True
    threading.Thread(target=run_blink4bb).start()
    return jsonify({ "success" : True })


@app.route("/api/v1/6noisybulbs/stop")
def stop_six_noisy_bulbs():
    global RUN_BLINK4BB_FLAG
    RUN_BLINK4BB_FLAG = False
    return jsonify({ "success" : True })
    

@app.route("/api/v1/5switches/restart")
def restart_five_switches():
    global RUN_INPUTB_FLAG
    if RUN_INPUTB_FLAG == True:
        RUN_INPUTB_FLAG = False
        time.sleep(0.1)# wait for stopping inputb (max waiting time: 0.5 + 0.5 = 1)

    RUN_INPUTB_FLAG = True
    threading.Thread(target=run_inputb).start()
    return jsonify({ "success" : True })


@app.route("/api/v1/5switches/stop")
def stop_five_switches():
    global RUN_INPUTB_FLAG
    RUN_INPUTB_FLAG = False
    return jsonify({ "success" : True })
    

def get_two_bulbs_info():
    return { "a" : bool(GPIO.input(7)), "b" : bool(GPIO.input(11)) }


def run_blink4bb():
    #### Equal to [18, 23, 24, 25, 12, 16] in GPIO.BCM mode
    IO_DEF_LIST = [12, 16, 18, 22, 32, 36] 

    for IO_DEF in IO_DEF_LIST:
        GPIO.setup(IO_DEF, GPIO.OUT)

    global RUN_BLINK4BB_FLAG
    while True:
        for IO_DEF in IO_DEF_LIST:
            if not RUN_BLINK4BB_FLAG:
                return 
            GPIO.output(IO_DEF, 0)
            time.sleep(0.5)
            GPIO.output(IO_DEF, 1)
        time.sleep(0.5)


def run_inputb():
    #### Equal to [21, 20,  5,  6, 13, 19, 26] in GPIO.BCM mode
    for IO_DEF in [40, 38, 29, 31, 33, 35, 37]:
        GPIO.setup(IO_DEF, GPIO.OUT)

    global RUN_INPUTB_FLAG
    while True:
        if not RUN_INPUTB_FLAG:
            return
        i29 = GPIO.input(29)
        i31 = GPIO.input(31)
        i33 = GPIO.input(33)
        i35 = GPIO.input(35)
        i37 = GPIO.input(37)
        value = i29 * i31 * i33 * i35 * i37
        #print(value, i29, i31, i33, i35, i37)
        GPIO.output(38, value) # Equal to 20 in GPIO.BCM mode
        GPIO.output(40, value) # Equal to 21 in GPIO.BCM mode
        time.sleep(0.1)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
