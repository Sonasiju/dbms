from flask import Flask,render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user




#db connection
local_server=True
app = Flask(__name__, static_folder='static')
app.secret_key='mehere'



#to get unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'



@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))

app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/hospital'
db=SQLAlchemy(app)


#create db models(tables)
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(1000))
    mail=db.Column(db.String(1000))

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    role=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))


class Patients(db.Model):
    pid=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50),unique=True)
    name=db.Column(db.String(50))
    gender=db.Column(db.String(50))
    slot=db.Column(db.String(50))
    time=db.Column(db.String(50),nullable=False)
    date=db.Column(db.String(50),nullable=False)
    dept=db.Column(db.String(50))
    disease=db.Column(db.String(50))
    number=db.Column(db.String(50))

class Doctors(db.Model):
    did=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    doctorsname=db.Column(db.String(50))
    dept=db.Column(db.String(50))

class Trgr(db.Model):
    tablename = 'trgr'
    tid=db.Column(db.Integer,primary_key=True)
    pid=db.Column(db.Integer)
    email=db.Column(db.String(50))
    action=db.Column(db.String(50))
    timestamp=db.Column(db.String(50))    
    
    


@app.route('/')
def index():
   return render_template('index.html')
    

@app.route("/doctors",methods=["POST","GET"])
@login_required
def doctors():
   if current_user.role != 'Doctor':  # Check if user is not a doctor
       flash("Access restricted to doctors only", "danger")
       return redirect(url_for('index'))  # Or redirect to another page

   if request.method == "POST":
    email=request.form.get('email')
    doctorsname=request.form.get('doctorsname')
    dept=request.form.get('dept')
# Ensure all form fields are populated
    if email and doctorsname and dept:
        
     query = Doctors(email=email, doctorsname=doctorsname, dept=dept)
     db.session.add(query)
     db.session.commit()
     flash("Information stored ^0^", "info")
    else:
     flash("All fields are required!", "warning")
     return render_template('doctors.html')    
 
    
   
   return render_template('doctors.html')


   

@app.route("/patients",methods=["POST","GET"])
@login_required
def patients():
   doct=Doctors.query.all()
   if request.method == "POST":
    email=request.form.get('email')
    name=request.form.get('name')
    gender=request.form.get('gender')
    slot=request.form.get('slot')
    disease=request.form.get('disease')
    time=request.form.get('time')
    date=request.form.get('date')
    dept=request.form.get('dept')
    number=request.form.get('number')
    subject="Hospital Management System"

    if len(number)<10 or len(number)>10:
       flash("Please give 10 digit number")
       return render_template('patients.html',doct=doct)
        
    query=Patients(email=email,name=name,gender=gender,slot=slot,disease=disease,time=time,date=date,dept=dept,number=number)
    db.session.add(query)
    db.session.commit()
    

    # (THE EMAIL THING FOR JSON) mail.send_message(subject, sender= params['gmail-user'],recipients=[email],body="Your Booking Is Confirmed.. ^_^   Thank You for choosing us ^o^" )
    flash("Booking Confirmed","info")

   return render_template('patients.html',doct=doct)
  
   
@app.route('/bookings')
@login_required
def bookings(): 
  em=current_user.email
  if current_user.role=="Doctor":
        query=Patients.query.all()
        return render_template('bookings.html',query=query)
  else:
        # query=db.engine.execute(f"SELECT * FROM patients WHERE email='{em}'")
        query=Patients.query.filter_by(email=em)
        print(query)
        return render_template('bookings.html',query=query)
        

@app.route("/login",methods=["POST","GET"])
def login():
   if request.method == "POST":
      
      email=request.form.get('email')
      password=request.form.get('password')
      user=User.query.filter_by(email=email).first()

      if user and check_password_hash(user.password,password):
         login_user(user)
         flash("Login Success ✪ ω ✪","info",)
         return render_template('base.html')
      else:
         flash("INVALID CREDENTIALS ┬┬﹏┬┬","danger")  
         return render_template('login.html')
      
      
     
      
   return render_template('login.html')

   

@app.route("/logout")
@login_required
def logout():
   logout_user()
   flash("Logout successful (∪.∪ )...zzz","primary")
   return redirect(url_for('index'))

@app.route('/signup' ,methods=['POST','GET'])
def signup():
   if request.method == "POST":
      username=request.form.get('username')
      role=request.form.get('role')
      email=request.form.get('email')
      password=request.form.get('password')
      user=User.query.filter_by(email=email).first()
      if user:
         flash("Email Already Exists...(⊙_⊙)？","warning")
         return render_template('/signup.html')
      encpassword=generate_password_hash(password)
      new_user = User(username=username, role=role,email=email, password=encpassword)
      db.session.add(new_user)
      db.session.commit()
   
     
      flash("Signup Success ￣︶￣　 Please Login ◕.◕","success")
      return render_template('login.html')
   return render_template('signup.html')
  
  
  

@app.route("/test")
def test():
    try:
        Test.query.all()
        return 'db connected'
    except:
      return 'db not connected'
    


@app.route("/edit/<pid>", methods=["POST", "GET"])
@login_required
def edit(pid):
    if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('name')
        gender = request.form.get('gender')
        slot = request.form.get('slot')
        disease = request.form.get('disease')
        time = request.form.get('time')
        date = request.form.get('date')
        dept = request.form.get('dept')
        number = request.form.get('number')

        post = Patients.query.filter_by(pid=pid).first()
        if post:
            post.email = email
            post.name = name
            post.gender = gender
            post.slot = slot
            post.disease = disease
            post.time = time
            post.date = date
            post.dept = dept
            post.number = number
            db.session.commit()
            flash("Slot is Updated", "success")
        else:
            flash("Patient not found", "danger")
        return redirect(url_for('bookings'))

    # If GET request, display the current details for the patient
    posts = Patients.query.filter_by(pid=pid).first()
    if posts:
        return render_template('edit.html', posts=posts)
    else:
        flash("Patient not found", "danger")
        return redirect(url_for('bookings'))



@app.route("/delete/<pid>", methods=["POST", "GET"])
@login_required
def delete(pid):
    query = Patients.query.filter_by(pid=pid).first()
    if query:
        db.session.delete(query)
        db.session.commit()
        flash("Slot Deleted Successfully", "danger")
    else:
        flash("Patient not found", "danger")
    return redirect(url_for('bookings'))
    
    
@app.route('/details') 
@login_required
def details():
   posts=Trgr.query.all()
   return render_template('trigers.html',posts=posts)


@app.route('/search',methods=['POST','GET'], endpoint='search_endpoint') 
@login_required
def search():
   
  if request.method=="POST":  
     query=request.form.get('search')
     dept=Doctors.query.filter_by(dept=query).first()
     name=Doctors.query.filter_by(doctorsname=query).first()
     if name:
        flash("Doctor Is Available","info")
     else:
         flash("Doctor Is Not Available","danger")
      

  return render_template('index.html')



if __name__ == "__main__":
 app.run(debug=True)
