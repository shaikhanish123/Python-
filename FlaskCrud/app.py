from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "super_secret_key_123456789"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mumbai@localhost/harry'
db = SQLAlchemy(app)


# ------------------ MODELS ------------------
class Student(db.Model):
    __tablename__ = "student"
    sid = db.Column('id', db.Integer, primary_key=True)
    sname = db.Column('name', db.String(400), nullable=False)
    smail = db.Column('email', db.String(400), nullable=False)
    spass = db.Column('password', db.String(222), nullable=False)

class Task(db.Model):
    __tablename__ = "task"
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)



# ------------------ HOME ------------------
@app.route('/')
def home():
    return render_template('Register.html')


# ------------------ REGISTER ------------------
@app.route('/register', methods=["POST"])
def Register():
    username = request.form.get("name")
    useremail = request.form.get("email")
    userpass = request.form.get("password")

    student = Student(sname=username, smail=useremail, spass=userpass)
    db.session.add(student)
    db.session.commit()

    return redirect(url_for("loginpage"))


# ------------------ LOGIN ------------------
@app.route('/login', methods=["POST"])
def login():
    useremail = request.form.get("email")
    userpass = request.form.get("password")

    student = Student.query.filter_by(smail=useremail, spass=userpass).first()

    if student:
        session["user_id"] = student.sid
        session["username"] = student.sname
        return redirect(url_for("nav"))
    else:
        flash("Invalid Credentials", "error")
        return redirect(url_for("loginpage"))


@app.route('/nav')
def nav():
    if "user_id" not in session:
        return redirect(url_for("loginpage"))
    return render_template("navbar.html")


@app.route('/loginpage')
def loginpage():
    return render_template("login.html")



# ------------------ ADD TASK ------------------
@app.route('/addtask', methods=["GET", "POST"])
def addtask():
    if "user_id" not in session:
        return redirect(url_for("loginpage"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        user_id = session["user_id"]

        new_task = Task(title=title, description=description, user_id=user_id)
        db.session.add(new_task)
        db.session.commit()

        flash("Task Added Successfully!", "success")
        return redirect(url_for("addtask"))

    return render_template("add.html")



# ------------------ VIEW TASK ------------------
@app.route('/viewtask')
def viewtask():
    if "user_id" not in session:
        return redirect(url_for("loginpage"))

    uid = session["user_id"]
    tasks = Task.query.filter_by(user_id=uid).all()

    return render_template("view.html", tasks=tasks)



# ------------------ DELETE TASK ------------------
@app.route('/delete/<int:id>')
def delete_task(id):
    if "user_id" not in session:
        return redirect(url_for("loginpage"))

    task = Task.query.get(id)
    if task:
        db.session.delete(task)
        db.session.commit()

    flash("Task Deleted Successfully!", "success")
    return redirect(url_for("viewtask"))



# ------------------ EDIT USER (BY ID) ------------------
@app.route('/edituser/<int:id>', methods=["GET", "POST"])
def edit_user(id):
    if "user_id" not in session:
        return redirect(url_for("loginpage"))

    user = Student.query.get(id)

    if request.method == "POST":
        user.sname = request.form.get("name")
        user.smail = request.form.get("email")
        user.spass = request.form.get("password")

        db.session.commit()
        flash("Profile Updated Successfully!", "success")
        return redirect(url_for("nav"))

    return render_template("edit.html", user=user)



# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("loginpage"))



if __name__ == '__main__':
    app.run(debug=True)
