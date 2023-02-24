import os

from flask import Flask
from flask import render_template
from flask import request, flash
from flask_sqlalchemy import SQLAlchemy
from flask import redirect


import random
from sqlalchemy.sql.expression import func,select


app = Flask(__name__)


# here we make databaseConn

project_dir = os.path.dirname(os.path.abspath(__file__))

database_file = "sqlite:///{}".format(os.path.join(project_dir,"quizdatabase.db"))

app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"]="randomString"

db = SQLAlchemy(app)




'''
# from databaseConn import db


# class Question(db.Model):
#     title = db.Column(db.String(10000), nullable=False)

#     def __repr__(self):
#         return "<Title:{}>".format(self.title)
'''

class Quiz(db.Model):

    sno = db.Column(db.Integer(), unique=True, nullable=False, primary_key=True)
    question = db.Column(db.String(10000),unique=True, nullable=False)
    option1 = db.Column(db.String(1000), nullable=False)
    option2 = db.Column(db.String(1000), nullable=False)
    option3 = db.Column(db.String(1000), nullable=False)
    option4 = db.Column(db.String(1000), nullable=False)
    answer = db.Column(db.String(1000), nullable=False)

    def __init__(self,question,option1,option2,option3,option4,answer):
        self.question=question
        self.option1=option1
        self.option2=option2
        self.option3=option3
        self.option4=option4
        self.answer=answer


class User(db.Model):
    uid = db.Column(db.Integer(), unique=True, nullable=False, primary_key=True)
    username = db.Column(db.String(100),unique=True, nullable=False)
    email = db.Column(db.String(100),unique=True, nullable=False)
    password = db.Column(db.String(100),unique=True, nullable=False)
    phone = db.Column(db.String(20),unique=True, nullable=False)
    result = db.Column(db.Integer(),unique=True, nullable=False)

    def __init__(self,username,email,password,phone,result):
        self.username = username
        self.email = email
        self.password = password
        self.phone = phone
        self.result = result


@app.route("/register" , methods = ["GET", "POST"])
def register():
    if request.method=="POST":

        if not request.form["email"] or not request.form["username"] or not request.form["phone"] or not request.form["password"]:
            print("Please enter correct details")
            flash('Please enter correct details','error')
            return redirect("/register")
        else:
            print(request.form["username"])
            print(request.form["email"])
            print(request.form["password"])
            print(request.form["phone"])
            user = User(request.form["username"],request.form["email"],request.form["password"],request.form["phone"],0)
            db.session.add(user)
            db.session.commit
            # flash("registered successfully")
            return redirect("/")

        

    return render_template("login/register.html")





@app.route("/login" , methods=["GET", "POST"])
def login():
    if request.method=="POST":
        print(request.form["email"])
        print(request.form["psw"])
        if not request.form["email"] or not request.form["psw"]:
            print("Please enter correct details")
            flash('Please enter correct details')

        else:

            email = request.form["email"]
            user = User.query.filter_by(email=email).first()

            if(user.password==request.form["psw"]):
                print ("Login Successfull")
                return redirect("/")
            
            return redirect("/admin")
    
    return render_template("login/login.html")
    




#crud opertion
@app.route("/admin",methods=["GET","POST"])
def home():
    if request.method=="POST":
        # print(request.form)
        if not request.form["question"] or not request.form["option1"] or not request.form["option2"] or not request.form["option3"] or not request.form["option4"] or not request.form["answer"]:
            # flash("Please enter all the fields","error")
            print("Please enter all the fields")
            return redirect("/admin")

        else:
            rows = db.session.query(Quiz).count() #no of rows in database
            ques = Quiz(request.form["question"],request.form["option1"],request.form["option2"],request.form["option3"],request.form["option4"],request.form["answer"])
            db.session.add(ques)
            db.session.commit()

            # flash("Question was added successfully")
            print("Question was added successfully") 
            # return redirect("/admin")
    userList = User.query.all()   
    quesList =quiz.query.all()
    print(len(userList))
    print(len(quesList))
    return render_template("admin.html",quesList=quesList,userList=userList)



@app.route("/update",methods=["POST"])
def update():
    newQuestion = request.form.get("new_question")
    newOption1 = request.form.get("new_option1")
    newOption2 = request.form.get("new_option2")
    newOption3 = request.form.get("new_option3")
    newOption4 = request.form.get("new_option4")
    newAnswer = request.form.get("new_answer")

    oldQuestion = request.form.get("old_question")
    ques = Quiz.query.filter_by(question=oldQuestion).first()
    if request.form["new_question"]:
        ques.question=newQuestion

    if request.form["new_option1"]:
        ques.option1=newOption1

    if request.form["new_option2"]:
        ques.option2=newOption2

    if request.form["new_option3"]:
        ques.option3=newOption3

    if request.form["new_option4"]:
        ques.option4=newOption4

    if request.form["new_answer"]:
        ques.answer=newAnswer

    db.session.commit()
    return redirect("/admin")


@app.route("/delete",methods=["POST"])
def delete():
    question = request.form.get("del_question")
    ques = Quiz.query.filter_by(question=question).first()
    db.session.delete(ques)
    db.session.commit()
    return redirect("/admin")


result=0
questionDisplayedCount=0
questionDisplayed=[]

@app.route("/",methods=["GET","POST"])
def quiz():
    # randomList = random.sample(range(1,11),10)
    # for i in randomList:
    #     print(i)
    global questionDisplayed
    if request.method=="POST":
        global questionDisplayedCount,result
        questionDisplayedCount+=1
        rowCount = db.session.query(Quiz).count() #no of rows in database
        answer = request.form["check_answer"]
        if answer==request.form["option"]:
            result+=1 
        if rowCount==questionDisplayedCount:
            return ("Your result is: "+str(result)+" / "+str(rowCount))
        return redirect("/")

    ques = db.session.query(Quiz).order_by(func.random()).first()
    if questionDisplayed.__contains__(ques.question):
        return redirect("/")
    
    questionDisplayed.append(ques.question)
    print(ques.question)
    return render_template("quiz.html",ques=ques)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)

