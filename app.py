from flask import Flask, render_template,request,flash,redirect,url_for,session, Response
from flask_sqlalchemy import SQLAlchemy
from camera import VideoCamera
import pdb
import threading
from multiprocessing import Process

import mysql.connector
import os

SECRET_KEY = os.urandom(24)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  #database="mydatabase"
)

mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS z_intelligence")
mycursor.execute("USE z_intelligence")
mycursor.execute("CREATE TABLE IF NOT EXISTS Entry_Exit_Logs(EntryId INT NOT NULL AUTO_INCREMENT, EmployeeID VARCHAR(20) NOT NULL, EntryDate DATE NOT NULL, EntryTime TIME NOT NULL, ExitDate DATE NOT NULL, ExitTime TIME NOT NULL, PRIMARY KEY (EntryId))")
mycursor.execute("CREATE TABLE IF NOT EXISTS Users(EId INT NOT NULL AUTO_INCREMENT, stud_id INT NOT NULL UNIQUE, fname VARCHAR(20) NOT NULL, lname VARCHAR(20) NOT NULL, mobile BIGINT NOT NULL UNIQUE, email VARCHAR(40) NOT NULL UNIQUE, dept VARCHAR(20) NOT NULL,  PRIMARY KEY (EId))")

  
app = Flask("Z-Survelliance") #creating the Flask class object   
app.secret_key=SECRET_KEY
app.config["CACHE_TYPE"] = "null"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/z_intelligence'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


@app.route('/') #decorator drfines the   
def home():

    # if request.method=='POST' or request.method=='GET':  
    # ,methods=["GET","POST"]
    try:
        mydb1 = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        #database="mydatabase"
        )

        #print(mydb)
        mycursor1 = mydb1.cursor()
        mycursor1.execute("CREATE DATABASE IF NOT EXISTS z_intelligence")
        mycursor1.execute("USE z_intelligence")
        mycursor1.execute("CREATE TABLE IF NOT EXISTS Entry_Exit_Logs(EntryId INT NOT NULL AUTO_INCREMENT, EmployeeID VARCHAR(20) NOT NULL, EntryDate DATE NOT NULL, EntryTime TIME NOT NULL, ExitDate DATE NOT NULL, ExitTime TIME NOT NULL, PRIMARY KEY (EntryId))")
        mycursor1.execute("select * from entry_exit_logs")
        myresult1 = mycursor1.fetchall()
        # print(myresult1)
        mycursor1.close()
        mydb1.close()
    except Exception as e:
        # print(e)
        print("Error in Select Operation",e)
        flash("Error in Select Operation","danger")
    # finally:
    #     return redirect(url_for(""))
    #     con.close()   
    return render_template("dashboard.html",items = myresult1)

@app.route('/new',methods=["GET","POST"]) #decorator drfines the   
def new():
    if request.method=='POST':
        try:
            fname=request.form['fname']
            lname=request.form['lname']
            email=request.form['email']
            mobile=request.form['mobile']
            dept=request.form['dept']
            stud_id=request.form['stud_id']
            query = "INSERT INTO users(stud_id,fname,lname,mobile,email,dept) VALUES('"+ str(stud_id) +"','"+ fname +"','"+ lname +"','"+ str(mobile) +"','"+ email +"','"+ dept +"');"
            mycursor.execute(query)
            mycursor.execute("COMMIT;")
            print("Added Entry of new User")
            print("Record Added  Successfully")
            flash("Record Added  Successfully","success")
            
        except Exception as e:
            # print(e)
            print("Error in Insert Operation",e)
            flash("Error in Insert Operation","danger")
        finally:
            return redirect(url_for("new"))
            con.close()

    return render_template("new.html")

@app.route('/school') #decorator drfines the   
def school():  
    return render_template("school.html")

@app.route('/totalvoilation') #decorator drfines the   
def totalvoilation():  
    return render_template("totalvoilation.html")

@app.route('/delete') #decorator drfines the   
def delete():  
    return render_template("delete.html")
  
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def runApp():
    app.run(debug=True, use_reloader=False, port=5000, host='0.0.0.0')

if __name__ =='__main__':
    try:
        print("start first thread")
        t1 = threading.Thread(target=runApp).start()
    except Exception as e:
        print("Unexpected error:" + str(e))
