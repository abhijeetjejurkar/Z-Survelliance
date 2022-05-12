from flask import Flask, render_template,request,flash,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy

import mysql.connector
import os

SECRET_KEY = os.urandom(24)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  #database="mydatabase"
)

#print(mydb)
mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS z_intelligence")
mycursor.execute("USE z_intelligence")
mycursor.execute("CREATE TABLE IF NOT EXISTS Entry_Exit_Logs(EntryId INT NOT NULL AUTO_INCREMENT, EmployeeID VARCHAR(20) NOT NULL, EntryDate DATE NOT NULL, EntryTime TIME NOT NULL, ExitDate DATE NOT NULL, ExitTime TIME NOT NULL, PRIMARY KEY (EntryId))")
mycursor.execute("CREATE TABLE IF NOT EXISTS Users(EId INT NOT NULL AUTO_INCREMENT, stud_id INT NOT NULL UNIQUE, fname VARCHAR(20) NOT NULL, lname VARCHAR(20) NOT NULL, mobile BIGINT NOT NULL UNIQUE, email VARCHAR(40) NOT NULL UNIQUE, dept VARCHAR(20) NOT NULL,  PRIMARY KEY (EId))")

  
app = Flask("Z-Survelliance") #creating the Flask class object   
app.secret_key=SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/z_intelligence'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


@app.route('/') #decorator drfines the   
def home():  
    return render_template("dashboard.html")

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
  
  
if __name__ =='__main__':  
    app.run(debug=True, host='0.0.0.0',port='5000')  