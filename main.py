from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from data import db_session
from data.users import User
from data.jobs import Jobs
from data.departments import Department
from forms.user import RegisterForm, LoginForm
from forms.jobs import AddJobForm
from forms.departments import DepartmentForm
import datetime


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def index():
    db_sess = app.config['db_sess']
    jobs = [
        {
            'title': job.job,
            'leader': db_sess.query(User).filter(User.id == job.team_leader).first(),
            'duration': job.work_size,
            'list_of_collaborators': job.collaborators,
            'is_finished': job.is_finished,
            'id': job.id,
            'creator': db_sess.query(User).filter(User.id == job.creator).first()
        }
        for job in db_sess.query(Jobs).all()
    ]
    return render_template('index.html', jobs=jobs)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.login_email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.login_email.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data,
            modified_date=datetime.datetime.now()
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.login_email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/add_job',  methods=['GET', 'POST'])
@login_required
def add_jobs():
    form = AddJobForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = Jobs()
        jobs.team_leader = form.team_leader_id.data
        jobs.job = form.job.data
        jobs.work_size = form.work_size.data
        jobs.collaborators = form.collaborators.data
        jobs.is_finished = form.is_finished.data
        # В модели Jobs добавить: creator = sqlalchemy.Column(sqlalchemy.Integer)
        jobs.creator = current_user.id
        user = db_sess.query(User).filter(User.id == form.team_leader_id.data).first()
        user.jobs.append(jobs)
        db_sess.merge(user)
        db_sess.commit()
        return redirect('/')
    return render_template('add_job.html', title='Добавление работы',
                           form=form)


@app.route('/edit_job/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    form = AddJobForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == id, ((Jobs.creator == current_user.id) |
                                                          (current_user.id == 1))).first()
        if jobs:
            form.job.data = jobs.job
            form.team_leader_id.data = jobs.team_leader
            form.work_size.data = jobs.work_size
            form.collaborators.data = jobs.collaborators
            form.is_finished.data = jobs.is_finished
            return render_template('add_job.html',
                                   title='Edit job',
                                   form=form
                                   )
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == id,
                                          (Jobs.creator == current_user.id) | (current_user.id == 1)
                                          ).first()
        if jobs:
            jobs.job = form.job.data
            jobs.team_leader = form.team_leader_id.data
            jobs.work_size = form.work_size.data
            jobs.collaborators = form.collaborators.data
            jobs.is_finished = form.is_finished.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_job.html',
                           title='Edit job',
                           form=form
                           )


@app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def jobs_delete(id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).filter(Jobs.id == id,
                                      ((Jobs.creator == current_user.id) | (current_user.id == 1))
                                      ).first()
    if jobs:
        db_sess.delete(jobs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        department = Department()
        department.chief = form.chief.data
        department.email = form.email.data
        department.title = form.title.data
        department.members = form.members.data
        user = db_sess.query(User).filter(User.id == form.chief.data).first()
        user.department.append(department)
        db_sess.merge(user)
        db_sess.commit()
        return redirect('/departments')
    return render_template('department.html', title='Добавление департамента',
                           form=form)


@app.route('/departments')
def departments():
    db_sess = app.config['db_sess']
    departments = [
        {
            'title': department.title,
            'chief': db_sess.query(User).filter(User.id == department.chief).first(),
            'members': department.members,
            'id': department.id,
            'email': department.email
        }
        for department in db_sess.query(Department).all()
    ]
    return render_template('departments_view.html', departments=departments)


@app.route('/edit_department/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_department(id):
    form = DepartmentForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        department = db_sess.query(Department).filter(Department.id == id, ((Department.chief == current_user.id) |
                                                          (current_user.id == 1))).first()
        if department:
            form.title.data = department.title
            form.chief.data = department.chief
            form.members.data = department.members
            form.email.data = department.email
            return render_template('department.html',
                                   title='Редактировать департамент',
                                   form=form
                                   )
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        department = db_sess.query(Department).filter(Department.id == id,
                                          (Department.chief == current_user.id) | (current_user.id == 1)
                                          ).first()
        if department:
            department.title = form.title.data
            department.chief = form.chief.data
            department.members = form.members.data
            department.email = form.email.data
            db_sess.commit()
            return redirect('/departments')
        else:
            abort(404)
    return render_template('department.html',
                           title='Редактировать департамент',
                           form=form
                           )


@app.route('/department_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def department_delete(id):
    db_sess = db_session.create_session()
    department = db_sess.query(Department).filter(Department.id == id,
                                      ((Department.chief == current_user.id) | (current_user.id == 1))
                                      ).first()
    if department:
        db_sess.delete(department)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/departments')


def main():
    db_session.global_init("db/mars_explorer.db")
    db_sess = db_session.create_session()
    app.config['db_sess'] = db_sess
    app.run()


if __name__ == '__main__':
    main()