"""This web-application is little project I create to completely understand
   and improve knowledge of Celery technology. The purpose of app to check out if the file
   is a picture('png', 'jpg', 'jpeg') and if it is to resize it with Celery worker and then
   uploads it to particular directory. To resized pictures adding word 'resized' and then
   they are stored in 'uploads' directory. Status of celery worker processes can be seen
   in database named 'upload_status.db'"""

import os
from flask import Flask, request, flash, redirect
from celery_worker import task1
from werkzeug.utils import secure_filename
import sqlite3
import datetime


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            task_obj = task1.apply_async(args=[file_path])
            # apply_async ставить задачу в чергу на виконання(кладе в Rabbit, звідкіля їх забирає воркер)
            con = sqlite3.connect('upload_status.db')
            cur = con.cursor()
            cur.execute(f"""INSERT INTO task_status (datetime, file_name, status, task_id) 
                            VALUES ('{datetime.datetime.now()}', '{file_path}', 'Add', '{str(task_obj)}')""")
            con.commit()
            con.close()

            return str(task_obj)

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


if __name__ == '__main__':
    app.run()
