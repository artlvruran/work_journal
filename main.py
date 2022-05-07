from flask import Flask, render_template
from data import db_session
from data.users import User
from data.jobs import Jobs


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
def index():
    db_sess = app.config['db_sess']
    jobs = [
        {
            'title': job.job,
            'leader': db_sess.query(User).filter(User.id == job.team_leader).first(),
            'duration': job.work_size,
            'list_of_collaborators': job.collaborators,
            'is_finished': job.is_finished
        }
        for job in db_sess.query(Jobs).all()
    ]
    return render_template('index.html', jobs=jobs)


def main():
    db_session.global_init("db/mars_explorer.db")
    db_sess = db_session.create_session()
    app.config['db_sess'] = db_sess
    app.run()


if __name__ == '__main__':
    main()