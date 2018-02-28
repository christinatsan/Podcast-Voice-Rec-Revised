#!/usr/bin/env python3

from flask import Flask
from flask_bootstrap import Bootstrap
from flask import render_template
from flask import request, session, redirect, url_for, flash
from flask import jsonify
import json
import os
import time
from flask_mail import Mail, Message
#from flaskext.mysql import MySQL
#test

from helpers import textToSpeech
#from helpers import rss_parser


#rss_parser()
textToSpeech()

app = Flask(__name__, static_url_path='')
Bootstrap(app)
mail=Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'podcastrecstudy@gmail.com'
app.config['MAIL_PASSWORD'] = 'podcast95'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

#return app

#mysql = MySQL()

app._static_folder = 'static'
app.debug = True
app.secret_key = 'somesecretkey'


# file names
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))  

stat_fold = os.path.join(SITE_ROOT, "static")
json_url = os.path.join(SITE_ROOT, "static", "options.json")


podcast_options_json = 'options.json'
podcast_options_audio = 'options.mp3'
podcast_audio_dir = 'audio'
data_dir = 'data'
log_file_name = 'view_log'
survey_result_file_name = 'survey_result'

# global vars
podcast_options = json.load(open(json_url))
code = ""
code_set = set()
lastRequestIsVoice = True
session_ids = set()
req_json=""
hitID, assignmentID, workerID  = "","", ""
visual_start = 0
voice_start = 0
end = 0


# Configuring database

#app.config['MYSQL_DATABASE_USER'] = 'root'
#app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
#app.config['MYSQL_DATABASE_DB'] = 'Podcast_Study'
#app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#mysql.init_app(app)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('show_login'))


"""
    Logging In and Dispatching
    TODO: check duplicate submission
"""
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@app.route('/login', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def show_login():
    global code, session_ids
    global hitID, assignmentID, workerID
    
    code = codeGen()
    print ("c", code)
    if request.method == 'GET':
        req_json = request.args.to_dict()
        hitID = req_json.get('hitId', None)
        workerID = req_json.get('workerId', None)
        assignmentID = req_json.get('assignmentId', None)


    if request.method == 'POST':
        req_json = request.form.get('hitId')
        worker_id = request.form["user-id"]
        if request.form["user-id"] not in session_ids:
            #session_ids.add(worker_id)
            session['user-id'] = worker_id
            return redirect(url_for('show_consent_form'))
    return render_template('login.html')


@app.route('/consent-form')
def show_consent_form():
    if 'user-id' not in session:
        return redirect(url_for('show_login'))
    else:
        return render_template('consent_form.html')


# Dispatching client to two systems
@app.route('/_dispatch')
def dispatch():
    global lastRequestIsVoice

    # Client must login
    if 'user-id' not in session:
        return redirect(url_for('show_login'))
    # Client must agree consent form
    #if request.referrer != url_for('show_consent_form', _external = True):
    #    print ("Log: Illegal access to dispatcher")
    #    return redirect(url_for('show_login'))

    # Alternatively insert data into database as well as
    # dispatch request to voice-based and visual-based system

    insert_data()
    if lastRequestIsVoice:
        lastRequestIsVoice = False
        session['is-voice'] = False
        return redirect(url_for('show_visual_sys'))
    else:
        lastRequestIsVoice = True
        session['is-voice'] = True
        return redirect(url_for('show_voice_sys'))



"""
    Voice/Visual System and Survey
"""

# endpoint for visual based rec system
@app.route('/visual-sys')
def show_visual_sys():

    global visual_start
    visual_start = time.time()

    # msg = Message('Hello', sender = 'podcastrecstudy@gmail.com', recipients = ['christinatsangouri@gmail.com'])
    # msg.body = "Hello Flask message sent from Flask-Mail"
    # mail.send(msg)
    
    global podcast_options
    #print (podcast_options)

    # Client must login
    if 'user-id' not in session:
        return redirect(url_for('show_login'))
    # validate that request comes from dispatcher
   # if request.referrer != url_for('show_consent_form', _external = True):
   #     print ("Log: Illegal access to visual system")
   #     return redirect(url_for('show_login'))
    
    ncols = 4
    
    return render_template('visual_sys.html', podcast_options = podcast_options, ncols = ncols)


# endpoint for voice based rec system
@app.route('/voice-sys')
def show_voice_sys():
    global podcast_options
    global podcast_options_audio 

    global voice_start
    voice_start = time.time()

    # msg = Message('Hello', sender = 'podcastrecstudy@gmail.com', recipients = ['christinatsangouri@gmail.com'])
    # msg.body = "Hello Flask message sent from Flask-Mail"
    # mail.send(msg)



    # Client must login
    if 'user-id' not in session:
        return redirect(url_for('show_login'))
    # validate that request comes from dispatcher
   # if request.referrer != url_for('show_consent_form', _external = True):
   #     print ("Log: Illegal access to voice system")
   #     return redirect(url_for('show_login'))
    return render_template('voice_sys.html', audio_file=podcast_options_audio, podcast_options = podcast_options)


# shared audio player
@app.route('/player/<int:podcast_id>')
def play_audio(podcast_id):

    global end
    end = time.time()



    if ('user-id' not in session):
        return redirect(url_for('show_login'))

    session['podcast-id'] = podcast_id
    audio_file = podcast_audio_dir + '/' + podcast_options[podcast_id]['podcasts'][0]['file-name']
    audio_title = podcast_options[podcast_id]['podcasts'][0]['title']
    print ("Audio File", audio_file)
    return render_template('player.html', audio_file=audio_file, pause_offset = 300,title = audio_title)


# display survey
@app.route('/survey')
def show_survey():
    global code 
    
    if ('user-id' not in session) or ("podcast-id" not in session) or ('is-voice' not in session):
        return redirect(url_for('show_login'))
    else:
        return render_template('survey.html', passcode = code)


# save data and logout
@app.route('/thankyou', methods=['POST', 'GET'])
def save_result_and_logout():
    global code

    if session['is-voice']:
        processing_time = end - voice_start
    else:
        processing_time = end - visual_start


    print ("c2", code)
    if request.method == 'GET':
        req_json = request.args.to_dict()
        choiceLikeLevel = req_json.get('choice-like-level',None)
        choiceComment  = req_json.get('choice-comment', None)
        recomLikeLevel = req_json.get('recommendation-like-level',None)
        recomComment = req_json.get('recommendation-comment',None)


    if request.method == 'POST':
        choiceLikeLevel = request.form.get('choice-like-level')
        choiceComment  = request.form.get('choice-comment')
        recomLikeLevel = request.form.get('recommendation-like-level')
        recomComment = request.form.get('recommendation-comment')

#    print(comm)
       # worker_id = request.form["user-id"]
       # if request.form["user-id"] not in session_ids:
            #session_ids.add(worker_id)
       #     session['user-id'] = worker_id
#    if request.referrer != url_for('show_survey', _external = True) \
#        or ('user-id' not in session) \
#        or ('podcast-id' not in session) \
#        or ('is-voice' not in session):
#        return redirect(url_for('show_login'))

    # save completed survey
#    if request.method == 'POST':
#         choicelikelevel = request.form['choice-like-level']
#         print(choicelikelevel)
#    survey_result2 = request.form.to_dict()
    survey_result = request.form.copy()
#    print(survey_result2)
#    print(survey_result)
#    a = request.form.get('choice-comment')
#    print(a)
    survey_result['choice-like-level'] = choiceLikeLevel
    survey_result['choice-comment'] = choiceComment
    survey_result['recommendation-like-level'] = recomLikeLevel
    survey_result['recommendation-commentt'] = recomComment
    survey_result['user-id'] = session['user-id']
    survey_result['podcast-id'] = session['podcast-id']
    survey_result['is-voice'] = session['is-voice']
    survey_result['time_spent_choosing'] = processing_time
    fd = open(data_dir + '/' + survey_result_file_name, 'a+')
    fd.write(json.dumps(survey_result))
    fd.write('\n')
    fd.close()

    session.clear()
    return render_template('thankyou.html', passcode = code)


"""

Helper Functions

"""

# helper: collect view history
@app.route('/_data-collector', methods=['POST'])
def collect_data():
    log = {}
    log["history"] = request.json
    log["user-id"] = session['user-id']

    fd = open(data_dir + '/' + log_file_name, 'a+')
    fd.write(json.dumps(log))
    fd.write('\n')
    fd.close()
    return ""


@app.errorhandler(404)
def page_not_found(e):
    return "Page Not Found. To login, please visit /login"


@app.route("/insert_data", methods=['POST'])
def insert_data():
    global code, hitID, workerID, assignmentID 
    
    assignedCode = code
    #conn = mysql.connect()
    #cursor = conn.cursor()
    #cursor.callproc('sp_createParticipant',(workerID, assignmentID, hitID, assignedCode))
    #conn.commit()
    #cursor.close()
    #conn.close()
    #return ''
    return

@app.route("/participants", methods=['GET'])
def get_participants():
    #conn = mysql.connect()
    #cursor = conn.cursor()
    #cursor.execute("SELECT * FROM Participants_Data")
    #data = cursor.fetchall()
    #cursor.close()
    #conn.close()
    #return jsonify(data)
    return

def get_table_columns(table):
    #conn = mysql.connect()
    #cursor = conn.cursor()
    #cursor.execute("SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='Podcast_Study' AND `TABLE_NAME`='" + table + "'")
    #data = cursor.fetchall()
    #print(data)
    #cursor.close()
    #conn.close()
    #return ''
    return


def codeGen():
    import string
    import random

    global code_set

    def genPwd():
        chars=string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(20))
    
    pwd = genPwd()

    while pwd in code_set:
        pwd = genPwd()
    
    code_set.add(pwd)
    return pwd


if __name__ == "__main__":

    # Load podcasts
    with open(app._static_folder + "/" + podcast_options_json) as podcasts_fd:
        podcast_options = json.load(podcasts_fd)
    
    # start server
    app.run(threaded=True)


