import os
import sys

from PIL import Image
from flask import Flask, render_template, request, url_for, redirect, flash, session, abort
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from config import MY_PROJECTS_DATABASE_NAME, CONTACTS_DATABASE_NAME, REVIEW_DATABASE_NAME, \
    MY_ACHIEVEMENTS_DATABASE_NAME, SITE_DATABASE_NAME
from db.models import db_init, db, Review, Project, Contact, Achievement
from utils import corvert_image

# <--------------------> #
#  InitializeBlockStart  #
# <--------------------> #


app = Flask(__name__, template_folder='templates', static_url_path='/static/')

# SQLAlchimy config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + SITE_DATABASE_NAME
app.config['SQLALCHEMY_BINDS'] = {
    'contacts': 'sqlite:///' + CONTACTS_DATABASE_NAME,
    'reviews': 'sqlite:///' + REVIEW_DATABASE_NAME,
    'projects': 'sqlite:///' + MY_PROJECTS_DATABASE_NAME,
    'achievement': 'sqlite:///' + MY_ACHIEVEMENTS_DATABASE_NAME
}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = '34567890oihgfcvbjktrtyuiop'
app.config['SESSION_COOKIE_NAME'] = 'EVM'

# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

db.app = app
db.init_app(app)


# <------------------> #
#  InitializeBlockEnd  #
# <------------------> #


# <---------------> #
#  AdminBlockStart  #
# <---------------> #


class Controller(ModelView):
    def is_accessible(self):
        if "logged_in" in session:
            return True
        abort(403)


# Add administrative views here
admin = Admin(app, name='microblog', template_mode='bootstrap3')
admin.add_view(Controller(Review, db.session))
admin.add_view(Controller(Contact, db.session))
admin.add_view(Controller(Project, db.session))
admin.add_view(Controller(Achievement, db.session))


@app.route("/admin", methods=["POST"])
def photo():
    if request.args.get("f") == "add":
        file = request.files["photo"]
        path = 'static/saved_images/' + str(secure_filename(file.filename))
        img = Image.open(file.stream)
        img.save(path)
    if request.args.get("f") == "del":
        try:
            path = request.form.getlist('del')
            path_to_image = os.getcwd() + url_for('static', filename=f'saved_images/{path[0]}')
            os.remove(path_to_image)
        except:
            pass
    return redirect('/admin')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get("username") == "admin" and request.form.get("password") == "superqwerty":
            session['logged_in'] = True
            return redirect('/admin')
        else:
            return render_template('login.html', failed=True)
    return render_template('login.html')


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))


# <--------------> #
#  AdminBlockEnd   #
# <--------------> #

# <---------------> #
#  RoutsBlockStart  #
# <---------------> #


@app.before_request
def make_permanent():
    session.permanent = True


@app.route("/")
@app.route("/index")
@app.route("/index.html")
def index():
    reviews = Review.query.filter(Review.visible).order_by(-Review.best).limit(10).all()
    return render_template('index.html',
                           title='Home',
                           reviews=reviews)


@app.route("/about")
@app.route("/about.html")
def about():
    return render_template('about_page.html', title="About")


@app.route("/projects")
@app.route("/projects.html")
def projects():
    projects = Project.query.all()
    reviews = Review.query.filter(Review.visible).order_by(Review.date).limit(5).all()
    return render_template('projects.html',
                           title="Projects",
                           projects=projects,
                           count=len(projects),
                           reviews=reviews)


@app.route("/projects/<int:id>")
@app.route("/projects_details.html/<int:id>")
def projects_details(id):
    project = Project.query.filter(Project.id == id).first()
    return render_template('projects_details.html', title="Details", project=project)


@app.route("/achievement", methods=['GET', 'POST'])
@app.route("/achievement.html", methods=['GET', 'POST'])
def achievement():
    if request.method == 'POST':
        try:
            achievements = Achievement.query.filter(or_(
                func.lower(Achievement.name).contains(request.form["res"]),
                func.lower(Achievement.categories).contains(request.form["res"]))).all()
            return render_template('achievement.html', title="Achievement", posts=achievements)
        except SQLAlchemyError as e:
            db.session.rollback()
            error = str(e.__dict__['orig'])
            print(error)
            print("Can't add new review to the Database")
            flash(error, category='error')
            return redirect(url_for('/achievement/all'))

    else:
        achievements = Achievement.query.all()

    return render_template('achievement.html',
                           title="Achievement",
                           posts=achievements)


@app.route("/all_reviews", methods=['GET', 'POST'])
@app.route("/all_reviews.html", methods=['GET', 'POST'])
def all_reviews():
    best = None
    reviews = []
    projects = Project.query.limit(5).all()

    if request.method == 'POST':
        try:
            reviews = Review.query.filter(or_(
                func.lower(Review.name).contains(request.form["res"]),
                func.lower(Review.review).contains(request.form["res"]))).order_by(-Review.best, Review.date).all()
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            print(error)
            print("Something wrong with the Database")
            flash(error, category='error')
            return redirect(url_for('index'))

    else:
        reviews = Review.query.filter(Review.visible).order_by(-Review.best, Review.date).all()

    count = len(reviews)
    if len(reviews) > 1:
        best, reviews = reviews[0], reviews[1:]
        count -= 1

    return render_template('all_reviews.html',
                           title="All reviews",
                           best=best,
                           reviews=reviews,
                           count=count,
                           projects=projects)


@app.route("/create_review", methods=['GET', 'POST'])
@app.route("/create_review.html", methods=['GET', 'POST'])
def create_review():
    if request.method == 'POST':
        try:
            file = request.files["photo"]
            path = 'static/saved_images/' + str(secure_filename(file.filename))
            converted = corvert_image(file, file.mimetype)
            converted.save(path)

            new_review = Review(name=request.form["name"],
                                position=request.form["position"],
                                review=request.form["review"],
                                photo=path
                                )

            db.session.add(new_review)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            error = str(e.__dict__['orig'])
            print(error)
            print("Can't add new review to the Database")
            flash(error, category='error')
            return redirect(url_for('index'))

        flash("Thanks for your review. It will be added soon.", category='success')
        return redirect(url_for('index'))
    else:
        return render_template('create_review.html', title="Create review")


@app.route("/contact", methods=['GET', 'POST'])
@app.route("/contact.html", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            new_contact = Contact(name=request.form["name"],
                                  email=request.form["email"],
                                  message=request.form["message"],
                                  subject=request.form["subject"]
                                  )
            db.session.add(new_contact)
            db.session.commit()

        except SQLAlchemyError as e:
            db.session.rollback()
            error = str(e.__dict__['orig'])
            print(error)
            print("Can't add contact to the Database")
            flash(error, category='error')
            return redirect(url_for('index'))

        flash("Thanks for contact with me. I will answer soon.", category='success')
        return redirect(url_for('index'))

    return render_template('contact.html', title="Contact")


# <-------------> #
#  RoutsBlockEnd  #
# <-------------> #


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    if len(sys.argv) > 1:
        if sys.argv[1] == "init":
            with app.app_context():
                db_init()

    app.run(host='0.0.0.0', port=5000, debug=True)
