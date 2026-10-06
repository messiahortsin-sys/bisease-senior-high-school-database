from flask import Flask,render_template,request,redirect,url_for,flash
import sqlite3
from pathlib import Path
app=Flask(__name__); app.secret_key="change-this-secret-key"
DB=Path(__file__).parent/"bisease_shs.db"
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
@app.route("/")
def dashboard():
 c=db(); counts={"students":c.execute("SELECT COUNT(*) FROM students WHERE status='Active'").fetchone()[0],
 "staff":c.execute("SELECT COUNT(*) FROM staff WHERE status='Active'").fetchone()[0],
 "classes":c.execute("SELECT COUNT(*) FROM classes").fetchone()[0],
 "fees":c.execute("SELECT COALESCE(SUM(amount_paid),0) FROM fees").fetchone()[0],
 "outstanding":c.execute("SELECT COALESCE(SUM(amount_payable-amount_paid),0) FROM fees").fetchone()[0]}; c.close()
 return render_template("dashboard.html",counts=counts)
@app.route("/students",methods=["GET","POST"])
def students():
 c=db()
 if request.method=="POST":
  d=request.form
  try:
   c.execute("INSERT INTO students(student_id,admission_no,full_name,gender,date_of_birth,programme,class_name,house,admission_year,guardian_name,guardian_phone) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
   tuple(d.get(x,"") for x in ["student_id","admission_no","full_name","gender","date_of_birth","programme","class_name","house","admission_year","guardian_name","guardian_phone"]))
   c.commit(); flash("Student added successfully.")
  except sqlite3.IntegrityError: flash("Student ID or admission number already exists.")
  c.close(); return redirect(url_for("students"))
 rows=c.execute("SELECT * FROM students ORDER BY full_name").fetchall(); c.close()
 return render_template("students.html",students=rows)
@app.route("/staff",methods=["GET","POST"])
def staff():
 c=db()
 if request.method=="POST":
  d=request.form
  try:
   c.execute("INSERT INTO staff(staff_id,full_name,gender,department,subject,position,phone,email) VALUES(?,?,?,?,?,?,?,?)",
   tuple(d.get(x,"") for x in ["staff_id","full_name","gender","department","subject","position","phone","email"]))
   c.commit(); flash("Staff member added successfully.")
  except sqlite3.IntegrityError: flash("Staff ID already exists.")
  c.close(); return redirect(url_for("staff"))
 rows=c.execute("SELECT * FROM staff ORDER BY full_name").fetchall(); c.close()
 return render_template("staff.html",staff=rows)
@app.route("/fees",methods=["GET","POST"])
def fees():
 c=db()
 if request.method=="POST":
  d=request.form
  c.execute("INSERT INTO fees(student_id,academic_year,term,amount_payable,amount_paid,payment_date,receipt_no) VALUES(?,?,?,?,?,?,?)",
   (d["student_id"],d["academic_year"],d["term"],float(d["amount_payable"] or 0),float(d["amount_paid"] or 0),d["payment_date"],d["receipt_no"]))
  c.commit(); flash("Fee payment recorded."); c.close(); return redirect(url_for("fees"))
 rows=c.execute("SELECT fees.*,students.full_name FROM fees LEFT JOIN students ON fees.student_id=students.student_id ORDER BY fees.id DESC").fetchall(); c.close()
 return render_template("fees.html",fees=rows)
@app.route("/attendance",methods=["GET","POST"])
def attendance():
 c=db()
 if request.method=="POST":
  d=request.form; c.execute("INSERT INTO attendance(student_id,attendance_date,class_name,status,reason) VALUES(?,?,?,?,?)",
  (d["student_id"],d["attendance_date"],d["class_name"],d["status"],d["reason"])); c.commit(); flash("Attendance recorded."); c.close(); return redirect(url_for("attendance"))
 rows=c.execute("SELECT attendance.*,students.full_name FROM attendance LEFT JOIN students ON attendance.student_id=students.student_id ORDER BY attendance.id DESC LIMIT 100").fetchall(); c.close()
 return render_template("attendance.html",attendance=rows)
@app.route("/results",methods=["GET","POST"])
def results():
 c=db()
 if request.method=="POST":
  d=request.form; test=float(d["test_score"] or 0); ass=float(d["assignment_score"] or 0); exam=float(d["exam_score"] or 0); total=test+ass+exam
  grade="A1" if total>=80 else "B2" if total>=75 else "B3" if total>=70 else "C4" if total>=65 else "C5" if total>=60 else "C6" if total>=55 else "D7" if total>=50 else "E8" if total>=45 else "F9"
  c.execute("INSERT INTO results(student_id,academic_year,term,subject,test_score,assignment_score,exam_score,total_score,grade,remarks) VALUES(?,?,?,?,?,?,?,?,?,?)",
  (d["student_id"],d["academic_year"],d["term"],d["subject"],test,ass,exam,total,grade,d["remarks"])); c.commit(); flash("Result recorded."); c.close(); return redirect(url_for("results"))
 rows=c.execute("SELECT results.*,students.full_name FROM results LEFT JOIN students ON results.student_id=students.student_id ORDER BY results.id DESC LIMIT 100").fetchall(); c.close()
 return render_template("results.html",results=rows)
if __name__=="__main__": 
     app.run(host="0.0.0.0", port=5000, debug=True)
