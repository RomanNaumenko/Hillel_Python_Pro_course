from celery import Celery
import resize
import sqlite3

con = sqlite3.connect('upload_status.db')
app = Celery('celery_worker', broker='pyamqp://guest@localhost//')


@app.task
def task1(image_pass):
    resize.resize(image_pass)
    cur = con.cursor()
    cur.execute(f"UPDATE task_status SET status = 'Done' WHERE file_name = '{image_pass}'")
    con.commit()
    con.close()
    return True
