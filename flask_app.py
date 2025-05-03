from flask import Flask, request, render_template, redirect, url_for, send_file
import sqlite3
import os
from werkzeug.utils import secure_filename, send_from_directory

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')  // Directory to save uploaded files



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.before_request
def before_request():
    # create a new SQLite connection and cursor for each request
    conn = sqlite3.connect('bullet_points.db')
    cursor = conn.cursor()

    # create the table for storing bullet points
    cursor.execute('CREATE TABLE IF NOT EXISTS bullet_points (bullet text, type text)')

    # create the table for storing long-term goals
    cursor.execute('CREATE TABLE IF NOT EXISTS long_term_goals (goal text)')

    # create the table for storing projecten
    cursor.execute('CREATE TABLE IF NOT EXISTS projecten (project text)')

    # create the table for storing errand
    cursor.execute('CREATE TABLE IF NOT EXISTS errands (errand text)')

    cursor.execute('CREATE TABLE IF NOT EXISTS boodschappenlijst (boodschapitem text)')
    cursor.execute('CREATE TABLE IF NOT EXISTS job_doelen (job_doel text)')

    # table for time slot selections
    cursor.execute('CREATE TABLE IF NOT EXISTS timeslots (slot TEXT PRIMARY KEY, selected INTEGER)')
    # store the connection and cursor in the request object
    request.conn = conn
    request.cursor = cursor


@app.route('/timeslots', methods=['GET', 'POST'])
def timeslots():
    if request.method == 'POST':
        selected_slots = request.form.getlist('timeslot')

        # Clear existing data
        request.cursor.execute('DELETE FROM timeslots')

        # Insert selected slots
        for slot in selected_slots:
            request.cursor.execute('INSERT INTO timeslots (slot, selected) VALUES (?, ?)', (slot, 1))

        request.conn.commit()
        return redirect(url_for('timeslots'))

    # Generate all half-hour time slots from 10:00 to 18:00
    all_slots = [f"{h:02d}:{m:02d}" for h in range(10, 18) for m in (0, 30)]
    all_slots.append("18:00")

    # Fetch saved selections
    request.cursor.execute('SELECT slot FROM timeslots WHERE selected = 1')
    saved = set(slot for (slot,) in request.cursor.fetchall())

    return render_template('timeslots.html', all_slots=all_slots, saved=saved)

@app.route('/', methods=['GET', 'POST'])
def index():

    files = os.listdir(app.config['UPLOAD_FOLDER'])

    # get the list of short-term tasks from the database
    request.cursor.execute('SELECT rowid, bullet FROM bullet_points WHERE type = "short-term"')
    short_term_tasks = [(rowid, bullet) for rowid, bullet in request.cursor.fetchall()]

    # get the list of long-term tasks from the database
    request.cursor.execute('SELECT rowid, bullet FROM bullet_points WHERE type = "long-term"')
    long_term_tasks = [(rowid, bullet) for rowid, bullet in request.cursor.fetchall()]

    # render the template with the lists of tasks
    return render_template('index.html', short_term_tasks=short_term_tasks, long_term_tasks=long_term_tasks, files=files)

@app.route('/add_short_term_task', methods=['POST'])
def add_short_term_task():
    # get the short-term task from the form
    bullet = request.form['bullet']

    # insert the short-term task into the database
    request.cursor.execute('INSERT INTO bullet_points VALUES (?, "short-term")', (bullet,))
    request.conn.commit()

    # redirect back to the main page
    return redirect(url_for('index'))

@app.route('/add_long_term_task', methods=['POST'])
def add_long_term_task():
    # get the long-term task from the form
    bullet = request.form['bullet']

    # insert the long-term task into the database
    request.cursor.execute('INSERT INTO bullet_points VALUES (?, "long-term")', (bullet,))
    request.conn.commit()

    # redirect back to the main page
    return redirect(url_for('index'))



@app.route('/delete_bullet_point/<int:index>')
def delete_bullet_point(index):
    # delete the bullet point with the specified rowid
    request.cursor.execute('DELETE FROM bullet_points WHERE rowid = ?', (index,))
    request.conn.commit()

    # redirect back to the main page
    return redirect(url_for('index'))

#----------------------------------------------------------------------------------------------------

@app.route('/long_term_goals', methods=['GET', 'POST'])
def long_term_goals():
    if request.method == 'POST':
        # get the long-term goal from the form
        goal = request.form['goal']

        # insert the long-term goal into the database
        request.cursor.execute('INSERT INTO long_term_goals VALUES (?)', (goal,))
        request.conn.commit()

    # get the list of long-term goals from the database
    request.cursor.execute('SELECT rowid, goal FROM long_term_goals')
    long_term_goals = [(rowid, goal) for rowid, goal in request.cursor.fetchall()]

    # render the template with the list of long-term goals
    return render_template('long_term_goals.html', long_term_goals=long_term_goals)


@app.route('/delete_long_term_goal/<int:index>')
def delete_long_term_goal(index):
    # delete the long-term goal with the specified rowid
    request.cursor.execute('DELETE FROM long_term_goals WHERE rowid = ?', (index,))
    request.conn.commit()

    # redirect back to the long-term goals page
    return redirect(url_for('long_term_goals'))


#projecten----------------------------------------------------------------------------------------
@app.route('/projecten', methods=['GET', 'POST'])
def projecten():
    if request.method == 'POST':
        # get the long-term goal from the form
        project = request.form['project']

        # insert the long-term goal into the database
        request.cursor.execute('INSERT INTO projecten VALUES (?)', (project,))
        request.conn.commit()

    # get the list of long-term goals from the database
    request.cursor.execute('SELECT rowid, project FROM projecten')
    projecten = [(rowid, project) for rowid, project in request.cursor.fetchall()]

    # render the template with the list of long-term goals
    return render_template('projecten.html', projecten=projecten)

@app.route('/delete_project/<int:index>')
def delete_project(index):
    # delete the bullet point with the specified rowid
    request.cursor.execute('DELETE FROM projecten WHERE rowid = ?', (index,))
    request.conn.commit()

    # redirect back to the main page
    return redirect(url_for('projecten'))



#boodschappenlijst------------------------
@app.route('/boodschappenlijst', methods=['GET', 'POST'])
def boodschappenlijst():
    if request.method == 'POST':
        boodschapitem = request.form['boodschapitem']

        request.cursor.execute('INSERT INTO boodschappenlijst VALUES (?)', (boodschapitem,))
        request.conn.commit()

    request.cursor.execute('SELECT rowid, boodschapitem FROM boodschappenlijst')
    boodschappenlijst = [(rowid, boodschapitem) for rowid, boodschapitem in request.cursor.fetchall()]

    return render_template('boodschappenlijst.html', boodschappenlijst=boodschappenlijst)

@app.route('/delete_boodschappenlijst/<int:index>')
def delete_boodschappenlijst(index):
    request.cursor.execute('DELETE FROM boodschappenlijst WHERE rowid = ?', (index,))
    request.conn.commit()

    return redirect(url_for('boodschappenlijst'))

@app.route('/job_doelen', methods=['GET', 'POST'])
def job_doelen():
    if request.method == 'POST':
        job_doel = request.form['job_doel']

        request.cursor.execute('INSERT INTO job_doelen VALUES (?)', (job_doel,))
        request.conn.commit()

    request.cursor.execute('SELECT rowid, job_doel FROM job_doelen')
    job_doelen = [(rowid, job_doel) for rowid, job_doel in request.cursor.fetchall()]

    return render_template('job_doelen.html', job_doelen=job_doelen)

@app.route('/delete_job_doelen/<int:index>')
def delete_job_doelen(index):
    request.cursor.execute('DELETE FROM job_doelen WHERE rowid = ?', (index,))
    request.conn.commit()

    return redirect(url_for('job_doelen'))


@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        f = request.files['file']

        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))


    return redirect(url_for('index'))

@app.route('/files')
def list_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])

    return render_template('files.html', files=files)

@app.route('/download/<path:file>')
def download(file):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], file), as_attachment=True)


@app.route('/delete/<file>')
def delete_file(file):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        return 'File does not exist'
    return redirect(url_for('list_files'))

if __name__ == '__main__':
    app.run(port=5002)
