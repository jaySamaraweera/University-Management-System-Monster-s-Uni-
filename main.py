def get_GPA(results):
    num_grades = 0.0
    GPA = 0.0
    if results == None:
        return None
    if len(results) == 0:
        return "N/A"
    credits = 0
    for row in results:
        grade = row[0]
        if grade == "IP" or grade == "":
            continue
        
        if grade == "A":
            GPA += (4.0 * row[4])
        elif grade == "A-":
            GPA += (3.7 * row[4])
        elif grade == "B+":
            GPA += (3.3 * row[4])
        elif grade == "B":
            GPA += (3.0 * row[4])
        elif grade == "B-":
            GPA += (2.7 * row[4])
        elif grade == "C+":
            GPA += (2.3 * row[4])
        elif grade == "C":
            GPA += (2.0 * row[4])
        elif grade == "F":
            GPA += 0.0
        
        credits += row[4]
    if credits != 0:
        return (round(GPA/credits, 2))
    else:
        return 0.0


def get_Creds(results):
    if results == None:
        return None
    if len(results) == 0:
        return "N/A"
    credits = 0
    for row in results:
        grade = row[0]
        if grade == "IP" or grade == "" or grade == "F":
            continue        
        credits += row[4]
    if credits != 0:
        return credits
    else:
        return 0

from pickle import NONE
from platform import java_ver
#from asyncio.windows_events import NULL
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from datetime import date
import re
import random

mydb = mysql.connector.connect(
    host="jtk.cmmaetuifplv.us-east-1.rds.amazonaws.com",
    user="admingo",
    password="yVC2H:{uU+DVMMc%",
    database="JTKsiversity"
)
mydb.autocommit=True

c = mydb.cursor(dictionary=True)

valid_grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F', 'IP']

app = Flask('app')
app.secret_key = ">:)"

@app.route('/', methods=['GET', 'POST'])
def home():
    if session.get('flag') != None:
        if session['flag'] == 1:
            return redirect(url_for('studentadd'))
    if session:
        return redirect(url_for('dashboard'))

    return render_template("home.html")    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('flag') != None:
        if session['flag'] == 1:
            return redirect(url_for('studentadd'))
    cursor = mydb.cursor(dictionary=True)
  
    error = None
    if request.method == 'POST':
        if str(request.form["field_uid"]) == '':
            return render_template("login.html", error = "Invalid user login")
        elif not (request.form["field_uid"].isnumeric()):
            return render_template("login.html", error = "Invalid user login")
        elif str(request.form["field_uid"]) == '0':
            return render_template("login.html", error = "Invalid user login")
        uid = int(request.form["field_uid"])
        password = str(request.form["field_password"])

        cursor.execute("SELECT * FROM users WHERE uid = %s AND password = %s;",(uid,password))
        user = cursor.fetchone()

        if user:
            session['uid'] = user['uid']
            session['fname'] = user['fname']
            session['lname'] = user['lname']
            session['typeuser'] = user['typeuser']
            session['coursebasket'] = {}
            session['flag'] = 0
            session['semester'] = 0
           # return redirect(url_for('dashboard'))
            if isApplicant(user['uid']):
                return redirect(url_for('applicantDash',uid=user['uid']))
            elif isStudent(user['uid']) or user['typeuser'] == "gradsecretary" or  user['typeuser'] == "admin" or user['typeuser'] == 'advisor' or user['typeuser'] == "professor" or user['typeuser'] == 'alumni' or user['typeuser'] == 'facultyreviewer'or user['typeuser'] == 'cac':    
                return redirect(url_for('dashboard'))    
        error = "Invalid user login"
    return render_template("login.html", error = error)

@app.route('/applicant/<uid>')
def applicantDash(uid):
  
  if session.get('uid') is None:
      return redirect('/')
  if int(session.get('uid')) != int(uid):
      if session['typeuser'] == "applicant":
          return redirect(url_for('applicantDash', uid = session['uid']))
      return redirect('/')
  info = getInfo(uid)
  if appSubmitted(uid):
    appmessage = "Your application has been submitted"
    appLink = "/appstatus"
    checkAppStatus = "CHECK APPLICATION STATUS"
    return render_template('applicantDash.html', info=info, msg = appmessage, app = appLink, checkapp = checkAppStatus)
  if not appSubmitted(uid):
    appmessage1 = "Your application has not been submitted"
    return render_template('applicantDash.html', info=info, msg = appmessage1, app = "", checkapp = "")


@app.route('/application',methods=['GET', 'POST'])
def application():
  print(session['uid'])
  id = session['uid']

  if request.method == 'GET':
    userInfo = getInfo(id)
    degree = getApplyingDeg()
    degreeChoices = getDeg()
    semester = getSemester()
    if appSubmitted(id):
      appInfo = getAppInfo(id)
      priorDeg = getPriorDegreeInfo(id)
      return render_template('application.html', user = userInfo, deg = degree, sem = semester, degChoices = degreeChoices,app = appInfo,priorD = priorDeg)
    else:
      priorDeg = ["","",""]
      return render_template('application.html', user = userInfo, deg = degree, sem = semester, degChoices = degreeChoices,app=None,priorD=priorDeg)

  if request.method == 'POST':
    commitApp(request.form,id)
    if appSubmitted(id):
      return redirect(url_for('applicantDash',uid=id))

@app.route('/appstatus', methods = ['GET'])
def appstatus():
  id = session['uid']
  appInfo = getAppInfo(id)
  if request.method == 'GET':
    appMessage = getAppMessage(id)
    appStatus = getAppStatus(id)  
  return render_template('appstatus.html', msg = appMessage, status = appStatus, app = appInfo)  

@app.route('/staff/<uid>')
def staffDash(uid):
    if session.get('uid') is None:
      return redirect('/')
    if int(session.get('uid')) != int(uid):
        if session['typeuser'] == "gradsecretary":
            return redirect(url_for('staffDash',uid = session['uid']))
        return redirect('/')
    info = getInfo(uid)
    return render_template('staffDash.html', info=info)  

@app.route('/transcript')
def transcript():
  transcriptList = getUnreviewedTranscripts()
  return render_template('transcript.html', transcript = transcriptList)

@app.route('/recletter', methods = ['POST','GET'])
def recletter():
  if request.method == 'POST':
    msg = ""
    if not isValidStudent(request.form):
        msg = "Applicant is not in our university's records"
        return render_template('recletter.html',msg=msg)
    elif isValidStudent(request.form):
        uid = getApplicantUID(request.form)
        if not appSubmitted(uid[0]["uid"]):
            msg = "Applicant has no application submitted in our records"
            return render_template('recletter.html',msg=msg)
        # elif recLetterSubmitted(uid[0]["uid"]):
        #     msg = "Rec Letter has been submitted (1)"
        #     return render_template('recletter.html',msg=msg)
        return redirect(url_for('recletterSubmission',uid=uid[0]["uid"]))        
  if request.method == 'GET':
      return render_template('recletter.html')        

@app.route('/recletter/<uid>',methods=['POST','GET'])
def recletterSubmission(uid):
  if request.method == 'GET':
      return render_template('recletterSubmission.html',uid=uid)
  if request.method == 'POST':
      commitRecLetter(request.form,uid)
      return render_template('recletter.html')


@app.route('/transcript/<uid>',methods=['POST','GET'])
def transcriptReview(uid):
  print(session['typeuser'])
  if session['typeuser'] != "gradsecretary":
      return redirect('/')
  info = getInfo(uid)
  reviewerID = session['uid']
  if request.method == 'POST':
      submitTranscript(request.form,uid)
      msg = "Transcript Reviewed for UID: "
      msg = msg + str(uid)
      return redirect('/dashboard')
  return render_template('transcriptReview.html',info=info)

@app.route('/review')
def review():

  if session['typeuser'] == "gradsecretary":
      reviewList = getReviewedApplications(session['uid'])
      return render_template('review.html',app = reviewList) 
  if not hasCommittedReview(session['uid']):
      reviewList = firstTimeUnReviewedApplications()
      return render_template('review.html',app = reviewList)
  elif hasCommittedReview(session['uid']):      
      reviewList = getUnreviewedApplications(session['uid'])
      return render_template('review.html', app = reviewList)  

@app.route('/review/<uid>',methods=['POST','GET'])
def reviewApplication(uid):
  if session['typeuser'] != "gradsecretary" and session['typeuser'] != "facultyreviewer" and session['typeuser'] != "cac":
      print(session['typeuser'])
      return redirect('/')

  if request.method == 'GET':
    userInfo = getInfo(uid)
    decisions = getDecisions()
    info = getReviewInfo(uid)
    # if recLetterSubmitted(uid):
    #     letters = getRecLetters(uid)
    #     if hasPriorDegree(uid):
    #         priors = getPriorDegree(uid)
    #         print(priors)
    #         return render_template('reviewApp.html',info=info,letters=letters,priors=priors,user=userInfo,decision = decisions)
    #     return render_template('reviewApp.html',info=info,letters=letters,user=userInfo,decision = decisions)  
    # return render_template('reviewApp.html',info=info,user=userInfo,decision = decisions)
    letters = getRecLetters(uid)
    priors = getPriorDegree(uid)
    if session['typeuser'] != "gradsecretary":
        return render_template('reviewApp.html',info=info,letters=letters,priors=priors,user=userInfo,decision = decisions)
    else:
        sql = ("SELECT AID FROM APPLICATION WHERE UID = %s")
        query = (uid,)
        c.execute(sql,query)
        aid = c.fetchall() 
        decision = getReviewerDecisions(aid[0]["AID"])
        return render_template('reviewAppGS.html',info=info,letters=letters,priors=priors,user=userInfo,decision = decisions,reviewDecision = decision)
  if request.method == 'POST':
    if session['typeuser'] == "gradsecretary":
        commitFinalDecision(request.form,uid)
    else:      
        commitReview(request.form,uid,session['uid'])
    msg = "Application Reviewed for UID: "
    msg = msg + str(uid)
    return redirect(url_for('dashboard')) 

@app.route('/register',methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    if request.method == 'POST':
      uid = makeUID()
      makeAccount(request.form,uid)
      return render_template("home.html",msg="Account Creation Successful, your UID is:", id = uid)    


@app.route('/logout')
def logout():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    cursor = mydb.cursor(dictionary=True)
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))  
    cursor.execute("SELECT * FROM students where uid = %s", (session['uid'],))
    grad_stu_data = cursor.fetchall()  
    # form1 data (for passing in render_template)
    cursor.execute("SELECT * FROM form where form_ID = %s", (session['uid'],))
    form1 = cursor.fetchall()
    form1_exist = False;
    if len(form1) != 0:
        form1_exist = True
    return render_template("dashboard.html", data=grad_stu_data, msg='',form1_exist=form1_exist)

@app.route('/catalog', methods = ['GET', 'POST'])
def catalog():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    cursor = mydb.cursor()  
    cursor.execute("SELECT * FROM courses;")
    results = cursor.fetchall()
    return render_template("catalogue.html", courses = results)
    #set info up, then cids, then append each cid to the list, then set dictionary for the course
    #
    #[preq for 233: [cid1: {info: sdf, yada: sdfs}, cid2: {info: sdf, yda: sdfsdf}]]


@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    cursor = mydb.cursor(dictionary=True)

    if request.method == 'POST':
        print("herere")
        print(request.form['sem_no'])
        s = int(request.form['sem_no'])
        if s == 0:
            cursor.execute("SELECT sect_id, course_dname, course_num, course_name, sect_num, credits, day_name, start_time, end_time, fname, lname FROM sects JOIN courses on courses.course_id = sects.courseid JOIN users ON sects.prof_id = users.uid WHERE (semester = 'Spring' AND year = 2022);")
            courses = cursor.fetchall()
            return render_template("schedule.html", courses = courses)


        elif s == 1:
            cursor.execute("SELECT sect_id, course_dname, course_num, course_name, sect_num, credits, day_name, start_time, end_time, fname, lname FROM sects JOIN courses on courses.course_id = sects.courseid JOIN users ON sects.prof_id = users.uid WHERE (semester = 'Fall' AND year = 2022);")
            courses = cursor.fetchall()
            return render_template("schedule.html", courses = courses)


        elif s == 2:
            cursor.execute("SELECT sect_id, course_dname, course_num, course_name, sect_num, credits, day_name, start_time, end_time, fname, lname FROM sects JOIN courses on courses.course_id = sects.courseid JOIN users ON sects.prof_id = users.uid WHERE (semester = 'Spring' AND year = 2023);")
            courses = cursor.fetchall()
            return render_template("schedule.html", courses = courses)


        elif s == 3:
            cursor.execute("SELECT sect_id, course_dname, course_num, course_name, sect_num, credits, day_name, start_time, end_time, fname, lname FROM sects JOIN courses on courses.course_id = sects.courseid JOIN users ON sects.prof_id = users.uid WHERE (semester = 'Fall' AND year = 2023);")
            courses = cursor.fetchall()
            return render_template("schedule.html", courses = courses)

    
    cursor.execute("SELECT sect_id, course_dname, course_num, course_name, sect_num, credits, day_name, start_time, end_time, fname, lname FROM sects JOIN courses on courses.course_id = sects.courseid JOIN users ON sects.prof_id = users.uid;")
    results = cursor.fetchall()
    return render_template("schedule.html", courses = results)


@app.route('/prereqs/<id>')
def prereqs(id):
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM prereqs INNER JOIN courses ON courses.course_id = prereqs.preid WHERE cid = %s;",(id,))
    result = cursor.fetchall()
    return render_template("prereqs.html", prereqs = result, len = len(result))

@app.route("/grading", methods=['GET', 'POST'])
def grading():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    if session['typeuser'] == "student":
        return redirect(url_for('dashboard'))
    
    cursor = mydb.cursor() 
    if session['typeuser'] == "professor":
        cursor.execute("SELECT users.uid, users.fname, users.lname, courses.course_id, courses.course_name, sects.semester, sects.year, takes.s_id, takes.grade, sects.sect_id FROM takes JOIN sects ON takes.s_id = sects.sect_id JOIN users ON takes.student_id = users.uid JOIN courses on sects.courseid = courses.course_id WHERE prof_id = %s AND grade = 'IP';",(session['uid'],))
    else:
        cursor.execute("SELECT users.uid, users.fname, users.lname, courses.course_id, courses.course_name, sects.semester, sects.year, takes.s_id, takes.grade, sects.sect_id FROM takes JOIN sects ON takes.s_id = sects.sect_id JOIN users ON takes.student_id = users.uid JOIN courses on sects.courseid = courses.course_id;")
    results = cursor.fetchall()
    
    if request.method == 'POST':
        new_grades = request.form
        new_grades = dict(new_grades)

        if 'submit' in new_grades:  #if GS entered grades
            for key, val in new_grades.items():

                if key == 'submit' or val not in valid_grades:
                    continue
                takes_info = key.split('-')
                cursor.execute("UPDATE takes SET grade = %s WHERE student_id = %s AND s_id = %s;", (val, takes_info[0], takes_info[1],))
                mydb.commit()
                cursor.execute("SELECT users.uid, users.fname, users.lname, courses.course_id, courses.course_name, sects.semester, sects.year, takes.s_id, takes.grade, sects.sect_id FROM takes JOIN sects ON takes.s_id = sects.sect_id JOIN users ON takes.student_id = users.uid JOIN courses on sects.courseid = courses.course_id;")
                newresults = cursor.fetchall()

                # update the GPA for that student
                cursor.execute("SELECT grade, courses.course_dname, courses.course_num, courses.course_name, courses.credits, courses.course_id, sects.semester, sects.year, sects.day_name, sects.start_time, sects.end_time, users.fname, users.lname, users.email FROM takes INNER JOIN sects ON takes.s_id = sects.sect_id INNER JOIN courses ON sects.courseid = courses.course_id INNER JOIN users ON sects.prof_id = users.uid WHERE student_id = %s;", (takes_info[0],))
                results = cursor.fetchall()
                new_gpa = get_GPA(results)
                cursor.execute("UPDATE students SET GPA = %s WHERE uid = %s;", (new_gpa, takes_info[0],))
                mydb.commit()

            return redirect(url_for('grading'))
        #if GS has searched
        c_id = new_grades['course_id']
        s_id = new_grades['student_id']

        if session['typeuser'] == 'professor':
            if len(s_id) <= 7 and c_id != '':
                cursor.execute("SELECT users.uid, users.fname, users.lname, courses.course_id, courses.course_name, sects.semester, sects.year, takes.s_id, takes.grade, sects.sect_id FROM takes JOIN sects ON takes.s_id = sects.sect_id JOIN users ON takes.student_id = users.uid JOIN courses on sects.courseid = courses.course_id WHERE courses.course_id = %s AND sects.prof_id = %s AND takes.grade = 'IP';", (c_id,session['uid']))
            elif c_id == '' and len(s_id) > 7:
                cursor.execute("SELECT users.uid, users.fname, users.lname, courses.course_id, courses.course_name, sects.semester, sects.year, takes.s_id, takes.grade, sects.sect_id FROM takes JOIN sects ON takes.s_id = sects.sect_id JOIN users ON takes.student_id = users.uid JOIN courses on sects.courseid = courses.course_id WHERE users.uid = %s AND sects.prof_id = %s AND takes.grade = 'IP';", (s_id,session['uid']))
            elif c_id != '' and len(s_id) > 7:
                cursor.execute("SELECT users.uid, users.fname, users.lname, courses.course_id, courses.course_name, sects.semester, sects.year, takes.s_id, takes.grade, sects.sect_id FROM takes JOIN sects ON takes.s_id = sects.sect_id JOIN users ON takes.student_id = users.uid JOIN courses on sects.courseid = courses.course_id WHERE courses.course_id = %s AND users.uid = %s AND sects.prof_id = %s AND takes.grade = 'IP';", (c_id, s_id,session['uid']))
            else:
                return render_template("grading.html", courses = results)
        else:
            if len(s_id) <= 7 and c_id != '':
                cursor.execute("SELECT users.uid, users.fname, users.lname, courses.course_id, courses.course_name, sects.semester, sects.year, takes.s_id, takes.grade, sects.sect_id FROM takes JOIN sects ON takes.s_id = sects.sect_id JOIN users ON takes.student_id = users.uid JOIN courses on sects.courseid = courses.course_id WHERE courses.course_id = %s;", (c_id,))
            elif c_id == '' and len(s_id) > 7:
                cursor.execute("SELECT users.uid, users.fname, users.lname, courses.course_id, courses.course_name, sects.semester, sects.year, takes.s_id, takes.grade, sects.sect_id FROM takes JOIN sects ON takes.s_id = sects.sect_id JOIN users ON takes.student_id = users.uid JOIN courses on sects.courseid = courses.course_id WHERE users.uid = %s;", (s_id,))
            elif c_id != '' and len(s_id) > 7:
                cursor.execute("SELECT users.uid, users.fname, users.lname, courses.course_id, courses.course_name, sects.semester, sects.year, takes.s_id, takes.grade, sects.sect_id FROM takes JOIN sects ON takes.s_id = sects.sect_id JOIN users ON takes.student_id = users.uid JOIN courses on sects.courseid = courses.course_id WHERE courses.course_id = %s AND users.uid = %s;", (c_id, s_id,))
            else:
                return render_template("grading.html", courses = results)
        results = cursor.fetchall()
        
    
    return render_template("grading.html", courses = results)


@app.route('/records', methods = ['GET', 'POST'])
def record():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    cursor = mydb.cursor()  
    results = None
    student = None

    if session['typeuser'] == 'student' or session['typeuser'] == 'alumni':
        cursor.execute("SELECT grade, courses.course_dname, courses.course_num, courses.course_name, courses.credits, courses.course_id, sects.semester, sects.year, sects.day_name, sects.start_time, sects.end_time, users.fname, users.lname, users.email FROM takes INNER JOIN sects ON takes.s_id = sects.sect_id INNER JOIN courses ON sects.courseid = courses.course_id INNER JOIN users ON sects.prof_id = users.uid WHERE student_id = %s;", (session['uid'],))
        results = cursor.fetchall()
    if request.method == 'POST':
        studentid = request.form["student_id"]
        cursor.execute("SELECT grade, courses.course_dname, courses.course_num, courses.course_name, courses.credits, courses.course_id, sects.semester, sects.year, sects.day_name, sects.start_time, sects.end_time, users.fname, users.lname, users.email FROM takes INNER JOIN sects ON takes.s_id = sects.sect_id INNER JOIN courses ON sects.courseid = courses.course_id INNER JOIN users ON sects.prof_id = users.uid WHERE student_id = %s;", (studentid,))
        results = cursor.fetchall()
        cursor.execute("SELECT uid, fname, lname FROM users WHERE uid = %s;",(studentid,))
        student = cursor.fetchone()
    
    GPA = get_GPA(results)
    Creds = get_Creds(results)
    print(Creds)
    cursor.execute("UPDATE students SET GPA = %s WHERE uid = %s;",(GPA, session['uid']))
    return render_template("record.html", courses = results, student = student, gpa = GPA, msg='', credits = Creds)

@app.route('/coursereg',methods=['GET','POST'])
def courseRegistration():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    cursor = mydb.cursor(dictionary=True)

    errors = []

    if request.method == 'POST':
        sems = {}
        ## Sems stores {(spring, 2022):{'day1':[(start_time,end_time),],'day2':[(start,end)]}, (fall, 2022):{}}
        #times = {}
        ## Times dictionary stores {'day1':[(start_time, end_time),(start_time, end_time)], 'day2':[(start_time, end_time)]}

        ## Load all of the times already registered for from takes table
        cursor.execute("SELECT semester, year, day_name, start_time, end_time FROM takes JOIN sects ON takes.s_id = sects.sect_id WHERE student_id = %s",(session['uid'],))
        courses = cursor.fetchall()

        if courses:
            for course in courses:
                ## Check to see if day is already stored in dictionary
                if (course['semester'], course['year']) in sems.keys():
                    if course['day_name'] in sems[(course['semester'],course['year'])].keys():
                        sems[(course['semester'],course['year'])][course['day_name']].append((course['start_time'],course['end_time']))
                    else:
                        sems[(course['semester'],course['year'])][course['day_name']] = [(course['start_time'],course['end_time'])]
                        
                else:                    
                    sems[(course['semester'],course['year'])] = {}
                    sems[(course['semester'],course['year'])][course['day_name']] = [(course['start_time'],course['end_time'])]
        

        ## Go through each item in the course basket
        for section_id, sectioninfo in session['coursebasket'].items():
            # Checker tracks if we need to add item to list
            checker = True
            ## if the course semester, year is already in sems
            if (sectioninfo['semester'],sectioninfo['year']) in sems.keys():
                ## if the day is already in this dict inside sems
                if sectioninfo['day_name'] in sems[(sectioninfo['semester'],sectioninfo['year'])].keys():
                    for (x,y) in sems[(sectioninfo['semester'],sectioninfo['year'])][sectioninfo['day_name']]:
                        ## if section in basket overlaps with something in basket
                        if sectioninfo['start_time'] >= x and sectioninfo['start_time'] <= y:
                            ## if the basket section start time is in between two times; there's an overlap
                            ## (tuple start time) <= basket_start_time <= (tuple end time)  (i.e overlap!)
                            if "Time Conflict" not in errors:
                                errors.append("Time Conflict")
                            checker = False
                        elif x <= sectioninfo['end_time'] and y >= sectioninfo['end_time']:
                            ## if the basket section end time is in between two times; there's an overlap
                            ## (tuple start time) <= basket_end_time <= (tuple end time)  (i.e overlap!)
                            if "Time Conflict" not in errors:
                                errors.append("Time Conflict")
                            checker = False
                ## if there was no time conflict and day is already in diction, add time tuple to list of specific day
                    if checker is True:
                        sems[(sectioninfo['semester'],sectioninfo['year'])][sectioninfo['day_name']].append((sectioninfo['start_time'],sectioninfo['end_time']))
            ## if the course day is not in the times, no time conflicts, add to dictionary at day
                else:
                    sems[(sectioninfo['semester'],sectioninfo['year'])][sectioninfo['day_name']] = [(sectioninfo['start_time'],sectioninfo['end_time'])]
            else:
                # if the semseter pair was not in sems, make a new dict entry for it and put 
                sems[(sectioninfo['semester'],sectioninfo['year'])] = {}
                sems[(sectioninfo['semester'],sectioninfo['year'])][sectioninfo['day_name']] = [(sectioninfo['start_time'],sectioninfo['end_time'])]

        coursenames = []
        ## Check prerequesites
        ## Check to see if the course has any prereqs
        for section_id, sectioninfo in session['coursebasket'].items():
            if (sectioninfo['semester'], sectioninfo['year']) == ('Spring', 2022):
                cursor.execute("SELECT cid, course_name, preid, semester, year, sect_id, sect_num FROM prereqs JOIN courses ON prereqs.cid = courses.course_id JOIN sects ON prereqs.preid = sects.courseid WHERE cid = %s" ,(sectioninfo['course_id'],))
                prereqs = cursor.fetchall()
                if prereqs:
                    # do not try registering for a course that has one or more prerequisite
                    # the course_name for both list entries in prereqs is the same, so use the 0th since there will always be at least one entry here
                    errors.append("Prerequisite errors for " + prereqs[0]['course_name'] + ", " + str(sectioninfo['sect_num']))
                    numprqs = 0

            if (sectioninfo['semester'], sectioninfo['year']) == ('Fall', 2022):
                cursor.execute("SELECT cid, course_name, preid, semester, year, sect_id, sect_num FROM prereqs JOIN courses ON prereqs.cid = courses.course_id JOIN sects ON prereqs.preid = sects.courseid WHERE cid = %s AND semester = 'Spring' AND year = 2022",(sectioninfo['course_id'],))
                prereqs = cursor.fetchall()
                numprqs = int(len(prereqs))

            if (sectioninfo['semester'], sectioninfo['year']) == ('Spring', 2023):
                cursor.execute("SELECT cid, course_name, preid, semester, year, sect_id, sect_num FROM prereqs JOIN courses ON prereqs.cid = courses.course_id JOIN sects ON prereqs.preid = sects.courseid WHERE cid = %s AND ((semester = 'Fall' AND year = 2022) OR (semester = 'Spring' AND year = 2022));",(sectioninfo['course_id'],))
                prereqs = cursor.fetchall()
                numprqs = int(len(prereqs)/2)

            if (sectioninfo['semester'], sectioninfo['year']) == ('Fall', 2023):
                cursor.execute("SELECT cid, course_name, preid, semester, year, sect_id, sect_num FROM prereqs JOIN courses ON prereqs.cid = courses.course_id JOIN sects ON prereqs.preid = sects.courseid WHERE cid = %s AND ((semester = 'Spring' AND year = 2023) OR (semester = 'Fall' AND year = 2022) OR (semester = 'Spring' AND year = 2022));",(sectioninfo['course_id'],))
                prereqs = cursor.fetchall()
                numprqs = int(len(prereqs)/3)            ## If prereqs exist for the course in basket, check to see that all of the prereqs courses have been taken by the student
            if prereqs:
                results = []
                for prereq in prereqs:
                    cursor.execute("SELECT * FROM takes JOIN sects ON takes.s_id = sects.sect_id WHERE s_id = %s AND grade <> 'IP' AND grade <> 'F' AND student_id = %s;",(prereq['sect_id'],session['uid']))
                    result = cursor.fetchone()
                    if not result:
                        continue
                    print(result)
                    results.append(result)
                    print(len(results))

                    ## If not taken, return error
                if not results:
                    if "Prerequisite error for " + prereq['course_name'] + ", " + str(sectioninfo['sect_num']) not in errors:
                        errors.append("Prerequisite error for " + prereq['course_name'] + ", " + str(sectioninfo['sect_num']))
                elif numprqs == 0:
                    continue
                elif len(results) != int(numprqs):
                    if "Prerequisite error for " + prereq['course_name'] + ", " + str(sectioninfo['sect_num']) not in errors:
                        errors.append("Prerequisite error for " + prereq['course_name'] + ", " + str(sectioninfo['sect_num']))
            if (sectioninfo['semester'], sectioninfo['year']) == ('Spring', 2022):                    
                cursor.execute("SELECT s_id, course_name FROM takes INNER JOIN sects ON s_id = sect_id INNER JOIN courses ON courseid=course_id WHERE student_id = %s AND (grade <> 'F' OR ((semester = 'Spring' AND year = 2023) OR (semester = 'Fall' AND year = 2023) OR (semester = 'Fall' AND year = 2022)));", (session['uid'],))
            elif (sectioninfo['semester'], sectioninfo['year']) == ('Fall', 2022):                    
                cursor.execute("SELECT s_id, course_name FROM takes INNER JOIN sects ON s_id = sect_id INNER JOIN courses ON courseid=course_id WHERE student_id = %s AND (grade <> 'F' OR ((semester = 'Spring' AND year = 2023) OR (semester = 'Fall' AND year = 2023)));", (session['uid'],))
            elif (sectioninfo['semester'], sectioninfo['year']) == ('Spring', 2023):                    
                cursor.execute("SELECT s_id, course_name FROM takes INNER JOIN sects ON s_id = sect_id INNER JOIN courses ON courseid=course_id WHERE student_id = %s AND (grade <> 'F' OR ((semester = 'Fall' AND year = 2023)));", (session['uid'],))
            elif (sectioninfo['semester'], sectioninfo['year']) == ('Fall', 2023):                    
                cursor.execute("SELECT s_id, course_name FROM takes INNER JOIN sects ON s_id = sect_id INNER JOIN courses ON courseid=course_id WHERE student_id = %s AND grade <> 'F';", (session['uid'],))
            taken = cursor.fetchall()
            print(taken)
            for took in taken:
                if sectioninfo['course_name'] == took['course_name']:
                    errors.append("You are already taking " + sectioninfo['course_name'])
                    break
            if sectioninfo['course_name'] in coursenames:
                errors.append("You cannot register for two sections of " + sectioninfo['course_name'] + " at the same time")
            coursenames.append(sectioninfo['course_name'])
            print(coursenames)
        if not errors:
            for section_id, sectioninfo in session['coursebasket'].items():
                cursor.execute("INSERT INTO takes(student_id, s_id, grade) VALUES(%s, %s, %s)",(session['uid'],section_id, "IP"))
                mydb.commit()
                session['coursebasket'] = {}
            errors.append("Successful Registration")        
    print(session['semester'])
    s = int(session['semester'])
    sections = None
    if s == 0:
        cursor.execute("SELECT sect_id, course_id, sect_num, course_dname, course_num, course_name, credits, semester, year, day_name, start_time, end_time, fname AS instfname, lname AS instlname FROM sects JOIN courses ON sects.courseid = courses.course_id JOIN users ON sects.prof_id = users.uid WHERE sect_id NOT IN (SELECT s_id FROM takes WHERE student_id = %s) AND (semester = 'Spring' AND year = 2022);",(session['uid'],))
        sections = cursor.fetchall()

    elif s == 1:
        cursor.execute("SELECT sect_id, course_id, sect_num, course_dname, course_num, course_name, credits, semester, year, day_name, start_time, end_time, fname AS instfname, lname AS instlname FROM sects JOIN courses ON sects.courseid = courses.course_id JOIN users ON sects.prof_id = users.uid WHERE sect_id NOT IN (SELECT s_id FROM takes WHERE student_id = %s) AND (semester = 'Fall' AND year = 2022);",(session['uid'],))
        sections = cursor.fetchall()

    elif s == 2:
        cursor.execute("SELECT sect_id, course_id, sect_num, course_dname, course_num, course_name, credits, semester, year, day_name, start_time, end_time, fname AS instfname, lname AS instlname FROM sects JOIN courses ON sects.courseid = courses.course_id JOIN users ON sects.prof_id = users.uid WHERE sect_id NOT IN (SELECT s_id FROM takes WHERE student_id = %s) AND (semester = 'Spring' AND year = 2023);",(session['uid'],))
        sections = cursor.fetchall()

    elif s == 3:
        cursor.execute("SELECT sect_id, course_id, sect_num, course_dname, course_num, course_name, credits, semester, year, day_name, start_time, end_time, fname AS instfname, lname AS instlname FROM sects JOIN courses ON sects.courseid = courses.course_id JOIN users ON sects.prof_id = users.uid WHERE sect_id NOT IN (SELECT s_id FROM takes WHERE student_id = %s) AND (semester = 'Fall' AND year = 2023);",(session['uid'],))
        sections = cursor.fetchall()


    cursor.execute("SELECT sect_id, course_id, sect_num, course_dname, course_num, course_name, credits, semester, year, day_name, start_time, end_time, fname AS instfname, lname AS instlname, grade FROM sects JOIN courses ON sects.courseid = courses.course_id JOIN users ON sects.prof_id = users.uid JOIN takes ON sect_id = s_id WHERE student_id = %s;",(session['uid'],))
    currentcourses = cursor.fetchall()
    print(currentcourses)


    return render_template("coursereg.html", sections = sections, errors = errors, currentcourses = currentcourses)

@app.route('/dropcourse',methods=['GET','POST'])
def dropcourse():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    cursor = mydb.cursor(dictionary=True)

    if request.method == 'POST':
        sectid = request.form["sectid"]
        cursor.execute("DELETE FROM takes WHERE student_id = %s AND s_id = %s",(session['uid'],sectid))
        mydb.commit()
    return redirect(url_for('courseRegistration'))

@app.route('/addtobasket',methods=['GET', 'POST'])
def addtobasket():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    cursor = mydb.cursor(dictionary=True)

    if request.method == 'POST':
        sectid = str(request.form["sectid"])

        cursor.execute("SELECT sect_id, course_id, sect_num, course_dname, course_num, course_name, credits, semester, year, day_name, start_time, end_time, fname AS instfname, lname AS instlname FROM sects JOIN courses ON sects.courseid = courses.course_id JOIN users ON sects.prof_id = users.uid WHERE sect_id = %s;",(sectid,))
        item = cursor.fetchone()
        session['coursebasket'][str(item['sect_id'])] = item
        session.modified = True

    return redirect(url_for('courseRegistration'))

@app.route('/addbysectid', methods=['GET','POST'])
def addbysectid():
    if request.method == 'POST':
        print("here")
        cursor = mydb.cursor(dictionary=True)
        print("here")
        print(request.form)
        if request.form['sect_id'] == "" or request.form['sect_id'].isdigit() == False:
            return redirect(url_for('courseRegistration'))
        sectid = int(request.form['sect_id'])
        print("here")
        cursor.execute("SELECT sect_id, course_id, sect_num, course_dname, course_num, course_name, credits, semester, year, day_name, start_time, end_time, fname AS instfname, lname AS instlname FROM sects JOIN courses ON sects.courseid = courses.course_id JOIN users ON sects.prof_id = users.uid WHERE sect_id = %s;", (sectid,))
        item = cursor.fetchone()
        session['coursebasket'][str(item['sect_id'])] = item
        session.modified = True
    return redirect(url_for('courseRegistration'))

@app.route('/dropall', methods=['GET','POST'])
def dropall():
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("DELETE FROM takes WHERE student_id = %s AND grade = 'IP';",(session['uid'],))
    mydb.commit()
    return redirect(url_for('courseRegistration'))
    
@app.route('/removefrombasket',methods=['GET', 'POST'])
def removefrombasket():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    sectid = str(request.form["sectid"])
    session['coursebasket'].pop(sectid)

    session.modified = True


    return redirect(url_for('courseRegistration'))

@app.route('/clearbasket',methods=['GET', 'POST'])
def clearbasket():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    session['coursebasket'] = {}
    session.modified  = True
    return redirect(url_for('courseRegistration'))

@app.route('/adminsignup', methods = ['GET', 'POST'])
def adminsignup():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    if session['typeuser'] != "admin":
        return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        cursor = mydb.cursor()
        cursor.execute("SELECT uid FROM users;")
        result = cursor.fetchall()
        for id in result:
            if int(id[0]) == int(request.form['field_uid']):
                error = "User ID is already registered"
                return render_template("signup.html", error = error)
        cursor.execute("INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);", (request.form['field_uid'], request.form['field_password'], request.form['field_fname'], request.form['field_lname'], request.form['field_address'], request.form['field_email'], request.form['field_phone'], request.form['field_type'], request.form['field_ssn']))
        if request.form["field_type"] == "student":
            session['temp_id'] = request.form['field_uid']
            return redirect(url_for('studentadd'))
        return redirect(url_for('dashboard'))
    return render_template("signup.html", error = error)

@app.route('/studentadd', methods = ['GET', 'POST'])
def studentadd():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['typeuser'] != "admin":
        return redirect(url_for('dashboard'))
    if session['temp_id'] == None:
        return redirect(url_for('dashboard'))
    error = None
    session['flag'] = 1
    if request.method == 'POST':
        for item in request.form:
            if request.form[item] == '':
                error = "Please fill out all items"
                return render_template("studentadd.html", error = error, username = session['temp_id'])  
        cursor = mydb.cursor()
        cursor.execute("SELECT uid FROM students;")
        result = cursor.fetchall()
        for id in result:
            if int(id[0]) == int(session['temp_id']):
                error = "Student is already registered"
                return render_template("signup.html", error = error)
        today = date.today()
       # cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("INSERT INTO faculty_advisor VALUES(%s,%s);",(session['temp_id'], 0))
        cursor.execute("INSERT INTO students VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);", (session['temp_id'], request.form['field_type'], request.form['field_major'],today.year, 0, 0.0, '', 0, 0))
      #  cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        session['temp_id'] = None
        session['flag'] = 0
        return redirect(url_for('dashboard'))
    return render_template("studentadd.html", error = error, username = session['temp_id'])  

# QUERIES

def makeUID(): #Uniquely generated UID
  bool = True
  while(bool):
    num = random.randint(10000000,99999999)
    sql = ("SELECT * FROM users WHERE uid = %s")
    query = (num,)
    c.execute(sql,query)
    if not c.fetchall():
      bool = False
  return num

def makeAccount(form,uid):  
  password = form.get("field_password")
  fname = form.get("field_fname")
  lname = form.get("field_lname")
  email = form.get("field_email")
  address  = form.get("field_address")
  phone = form.get("field_phone")
  ssn = form.get("field_ssn")
  usertype = "applicant"
  sql = ("INSERT INTO users (uid, password, fname, lname, address, email, phone ,typeuser,ssn) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)")
  query = (uid,password,fname,lname,address,email,phone,usertype,ssn)
  c.execute(sql,query)
  mydb.commit()

def getInfo(uid):
  sql = ("SELECT * FROM users WHERE uid = %s")
  query = (uid,)
  c.execute(sql,query)
  ret = c.fetchall()
  return ret[0]  

def appSubmitted(uid):
  sql = ("SELECT * FROM APPLICATION WHERE UID = %s")
  query = (uid,)
  c.execute(sql,query)
  return c.fetchall() != []  

def isApplicant(uid):
  sql = ("SELECT typeuser FROM users WHERE uid = %s")
  query = (uid,)
  c.execute(sql,query)
  utype = c.fetchall()
  print(utype[0]["typeuser"])
  if utype[0]["typeuser"] == "applicant":
    return True
  return False

def isStudent(uid):
  sql = ("SELECT typeuser FROM users WHERE uid = %s")
  query = (uid,)
  c.execute(sql,query)
  utype = c.fetchall()
  if utype[0]["typeuser"] == "student":
    return True
  return False 

def isGradSec(uid):
  sql = ("SELECT typeuser FROM users WHERE uid = %s")
  query = (uid,)
  c.execute(sql,query)
  utype = c.fetchall()
  if utype[0]["typeuser"] == "gradsecretary":
        return True
  return False       

def getUID(user):
  sql = ("SELECT uid FROM users WHERE username = %s")
  query = (user,)
  c.execute(sql,query)
  return c.fetchall()

def getApplyingDeg():
  sql = ("SELECT * FROM DEGREE WHERE degree != %s AND degree != %s")
  string = 'BA/BS'
  query = (string,'')
  c.execute(sql,query)
  return c.fetchall()

def getDeg():
  sql = ("SELECT * FROM DEGREE WHERE degree != ''")
  c.execute(sql)
  return c.fetchall()

def getSemester():
  sql = ("SELECT * FROM SEMESTER")
  c.execute(sql)
  return c.fetchall()  

def getPriorDegreeInfo(uid):
  sql = ("SELECT * FROM PRIOR_DEGREE WHERE UID = %s")
  query = (uid,)
  c.execute(sql,query)
  return c.fetchall()  

def getAppInfo(uid):
  sql = ("SELECT * FROM APPLICATION INNER JOIN users ON APPLICATION.UID = users.uid WHERE APPLICATION.UID = %s")
  query = (uid,)
  c.execute(sql,query)
  ret = c.fetchall()
  return ret[0]

def getDecisions():
  sql = ("SELECT * FROM DECISION")
  c.execute(sql)
  return c.fetchall()

def transcriptSubmitted(uid):
  sql = ("SELECT SUBMITTED FROM TRANSCRIPT WHERE UID = %s")
  query = (uid,)
  c.execute(sql,query)
  return int(c.fetchall()[0]["SUBMITTED"]) == 1

def recLetterSubmitted(uid):
#   sql = ("SELECT UID FROM REC_LETTER WHERE UID = %s")
  sql = ("SELECT COUNT(*) FROM REC_LETTER WHERE UID = %s")
  query = (uid,)
  c.execute(sql,query)
  a = c.fetchall()
  print(type(a[0]['COUNT(*)']))
  return a[0]['COUNT(*)'] == 3 

def getAppMessage(uid):
    sql = ("SELECT AID FROM APPLICATION WHERE UID = %s")
    query = (uid,)
    c.execute(sql,query)
    aid = c.fetchall()

    message = []
    if not transcriptSubmitted(uid):
        message.append("Transcript not recieved")
        sql = ("UPDATE APP_STATUS SET app_status = %s WHERE AID = %s")
        query = (1,aid[0]["AID"])
        c.execute(sql,query)
        mydb.commit()
    if not recLetterSubmitted(uid):
        message.append("Rec Letter(s) not recieved")
        sql = ("UPDATE APP_STATUS SET app_status = %s WHERE AID = %s")
        query = (1,aid[0]["AID"])
        c.execute(sql,query)
        mydb.commit()
    elif recLetterSubmitted(uid) and transcriptSubmitted(uid) and appSubmitted(uid) and not decisionMade(aid[0]["AID"]):
        sql = ("UPDATE APP_STATUS SET app_status = %s WHERE AID = %s")
        query = (2,aid[0]["AID"])
        c.execute(sql,query)
        mydb.commit()        
    return message 

def decisionMade(aid):
    sql = ("SELECT REVIEWED FROM APPLICATION WHERE AID = %s")
    query = (aid,)
    c.execute(sql,query)
    reviewed = c.fetchall()
    return int(reviewed[0]["REVIEWED"]) == 3  

def getAppStatus(uid):
    # sql = ("SELECT AID FROM APPLICATION WHERE UID = %s")
    # query = (uid,)
    # c.execute(sql,query)
    # aid = c.fetchall()

    # sql = ("SELECT status FROM STATUS INNER JOIN APP_STATUS ON STATUS.num_status = APP_STATUS.app_status WHERE APP_STATUS.AID = %s")
    # query = (aid[0]["AID"],)
    # c.execute(sql,query)

    if appSubmitted(uid):
        sql = ("SELECT AID FROM APPLICATION WHERE UID = %s")
        query = (uid,)
        c.execute(sql,query)
        aid = c.fetchall()

        message = ""
        if recLetterSubmitted(uid) and transcriptSubmitted(uid) and not decisionMade(aid[0]["AID"]):
            print("HERERE")
            message = "Under Review"
        elif not recLetterSubmitted(uid) or not transcriptSubmitted(uid):
            print("DSKLJFSPDOKNFSODI")
            message = "Incomplete"
        elif recLetterSubmitted(uid) and transcriptSubmitted(uid) and decisionMade(aid[0]["AID"]):
            print("HERE")
            sql = ("SELECT * FROM STATUS INNER JOIN APP_STATUS ON APP_STATUS.app_status = STATUS.num_status WHERE APP_STATUS.AID = %s")
            query = (aid[0]["AID"],)
            return c.fetchall()[0]      
    return message

def hasCommittedReview(uid):
    sql = ("SELECT * FROM APPLICATION_REVIEW WHERE APPLICATION_REVIEW.reviewerID = %s")
    query = (uid,)
    c.execute(sql,query)
    return c.fetchall() != []

def firstTimeUnReviewedApplications():
    sql = ("SELECT *,COUNT(REC_LETTER.UID) as reCount FROM APPLICATION INNER JOIN REC_LETTER ON REC_LETTER.UID = APPLICATION.UID INNER JOIN TRANSCRIPT ON APPLICATION.UID = TRANSCRIPT.UID WHERE APPLICATION.SUBMITTED = %s AND REVIEWED != %s AND TRANSCRIPT.SUBMITTED = %s GROUP BY APPLICATION.UID HAVING reCount = %s")
    query = (1,3,1,3)
    c.execute(sql,query)
    return c.fetchall()

def getUnreviewedApplications(uid):
#   sql = ("SELECT *,count(*) as TEMPCNT FROM APPLICATION INNER JOIN REC_LETTER ON REC_LETTER.UID = APPLICATION.UID INNER JOIN TRANSCRIPT ON APPLICATION.UID = TRANSCRIPT.UID LEFT JOIN APPLICATION_REVIEW ON APPLICATION_REVIEW.AID != APPLICATION.AID WHERE APPLICATION_REVIEW.reviewerID = %s AND APPLICATION.SUBMITTED = %s AND REVIEWED != %s AND TRANSCRIPT.SUBMITTED = %s HAVING TEMPCNT = %s")
  sql = ("SELECT *,COUNT(REC_LETTER.UID) as reCount FROM APPLICATION INNER JOIN REC_LETTER ON REC_LETTER.UID = APPLICATION.UID INNER JOIN TRANSCRIPT ON APPLICATION.UID = TRANSCRIPT.UID INNER JOIN APPLICATION_REVIEW ON APPLICATION_REVIEW.AID != APPLICATION.AID WHERE APPLICATION_REVIEW.reviewerID = %s AND APPLICATION.SUBMITTED = %s AND REVIEWED != %s AND TRANSCRIPT.SUBMITTED = %s GROUP BY APPLICATION.UID HAVING reCount = %s")
  query = (uid,1,3,1,3)
  c.execute(sql,query)
  return c.fetchall()
  #SELECT *,count(*) as TEMPCNT FROM APPLICATION INNER JOIN REC_LETTER ON REC_LETTER.UID = APPLICATION.UID INNER JOIN TRANSCRIPT ON APPLICATION.UID = TRANSCRIPT.UID INNER JOIN APPLICATION_REVIEW ON APPLICATION_REVIEW.AID = APPLICATION.AID WHERE APPLICATION_REVIEW.reviewerID != 23232323 AND APPLICATION.SUBMITTED = 1 AND REVIEWED != 3 AND TRANSCRIPT.SUBMITTED = 1 HAVING TEMPCNT = 3;
  #SELECT *,count(*) AS TEMPCNT from APPLICATION INNER JOIN REC_LETTER ON REC_LETTER.UID = APPLICATION.UID HAVING TEMPCNT = 3;
  #SELECT *,count(*) as TEMPCNT FROM APPLICATION INNER JOIN REC_LETTER ON REC_LETTER.UID = APPLICATION.UID INNER JOIN TRANSCRIPT ON APPLICATION.UID = TRANSCRIPT.UID WHERE APPLICATION.SUBMITTED = 1 AND REVIEWED != 3 AND TRANSCRIPT.SUBMITTED = 1 HAVING TEMPCNT = 3"
  #TEST AFTER MAKING ANOTHER APP
  #SELECT *,count(*) as TEMPCNT FROM APPLICATION INNER JOIN REC_LETTER ON REC_LETTER.UID = APPLICATION.UID INNER JOIN TRANSCRIPT ON APPLICATION.UID = TRANSCRIPT.UID INNER JOIN APPLICATION_REVIEW ON APPLICATION_REVIEW.AID = APPLICATION.AID WHERE APPLICATION_REVIEW.reviewerID = NULL AND APPLICATION.SUBMITTED = 1 AND REVIEWED != 3 AND TRANSCRIPT.SUBMITTED = 1 HAVING TEMPCNT = 3;
  #only return applications where three rec letters have been submitted, transcript submitted, application submitted, and reviewed != 3
  #FINALLY
  #SELECT *,count(*) as TEMPCNT FROM APPLICATION INNER JOIN REC_LETTER ON REC_LETTER.UID = APPLICATION.UID INNER JOIN TRANSCRIPT ON APPLICATION.UID = TRANSCRIPT.UID LEFT JOIN APPLICATION_REVIEW ON APPLICATION_REVIEW.AID != APPLICATION.AID WHERE APPLICATION_REVIEW.reviewerID = 23232323 AND APPLICATION.SUBMITTED = 1 AND REVIEWED != 3 AND TRANSCRIPT.SUBMITTED = 1 HAVING TEMPCNT = 3;
  #
  #Possibly working?
  #SELECT *,COUNT(REC_LETTER.UID) as reCount FROM APPLICATION INNER JOIN REC_LETTER ON REC_LETTER.UID = APPLICATION.UID INNER JOIN TRANSCRIPT ON APPLICATION.UID = TRANSCRIPT.UID WHERE APPLICATION.SUBMITTED = 1 AND REVIEWED != 3 AND TRANSCRIPT.SUBMITTED = 1 GROUP BY APPLICATION.UID HAVING reCount = 3;
  #SELECT *,COUNT(REC_LETTER.UID) as reCount FROM APPLICATION INNER JOIN REC_LETTER ON REC_LETTER.UID = APPLICATION.UID INNER JOIN TRANSCRIPT ON APPLICATION.UID = TRANSCRIPT.UID INNER JOIN APPLICATION_REVIEW ON APPLICATION_REVIEW.AID != APPLICATION.AID WHERE APPLICATION_REVIEW.reviewerID = %s AND APPLICATION.SUBMITTED = %s AND REVIEWED != %s AND TRANSCRIPT.SUBMITTED = %s GROUP BY APPLICATION.UID HAVING reCount = %s;
# have method to get apps ready for final decision     

def getUnreviewedTranscripts():
  sql = ("SELECT * FROM TRANSCRIPT WHERE TRANSCRIPT.SUBMITTED = %s")
  query = (0,)
  c.execute(sql,query)
  return c.fetchall() 

def submitTranscript(form,uid):
  choice = form.get("choice")
  sql = ("UPDATE TRANSCRIPT SET SUBMITTED = %s WHERE UID = %s")
  query = (int(choice),uid)
  c.execute(sql,query)
  mydb.commit() 

def isValidStudent(form):
  fname = form.get("field_fname") 
  lname = form.get("field_lname")
  phone = form.get("field_phone")
  typeuser = "applicant"
  sql = ("SELECT uid from users WHERE fname = %s and lname = %s and phone = %s and typeuser = %s")
  query = (fname,lname,phone,typeuser)
  c.execute(sql,query)    
  return c.fetchall() != []

def getApplicantUID(form):
  fname = form.get("field_fname") 
  lname = form.get("field_lname")
  phone = form.get("field_phone")
  typeuser = "applicant"
  sql = ("SELECT uid from users WHERE fname = %s and lname = %s and phone = %s and typeuser = %s")
  query = (fname,lname,phone,typeuser)
  c.execute(sql,query)
  return c.fetchall()

def commitRecLetter(form,uid):
  fname = form.get("field_fname") 
  lname = form.get("field_lname")
  letter = form.get("letter")
  sql = ("INSERT INTO REC_LETTER (UID,fname,lname,letter) VALUES (%s,%s,%s,%s)")
  query = (uid,fname,lname,letter)
  c.execute(sql,query)
  mydb.commit()

def getRecLetters(uid):
  sql = ("SELECT * FROM REC_LETTER WHERE UID = %s")
  query = (uid,)
  c.execute(sql,query)
#   ret = c.fetchall()
#   return ret
  return c.fetchall()

def getReviewInfo(uid):
  sql = ("SELECT * FROM APPLICATION INNER JOIN SEMESTER ON SEMESTER.num_semestr = APPLICATION.SEMSTR_SUBMITTED INNER JOIN DEGREE ON DEGREE.num_degree = APPLICATION.APPLIED_DEGREE WHERE UID = %s")
  query = (uid,)  
  c.execute(sql,query)
  return c.fetchall() 

def hasPriorDegree(uid):
  sql = ("SELECT * FROM PRIOR_DEGREE WHERE UID = %s")
  query = (uid,)
  c.execute(sql,query)
  return c.fetchall() != []

def getPriorDegree(uid):
  sql = ("SELECT * FROM PRIOR_DEGREE INNER JOIN DEGREE ON DEGREE.num_degree = PRIOR_DEGREE.prior_deg WHERE UID = %s")
  query = (uid,)
  c.execute(sql,query)
  return c.fetchall()

def getReviewedApplications(uid):
  sql = ("SELECT * FROM APPLICATION WHERE APPLICATION.REVIEWED = %s")
  query = (3,)
  c.execute(sql,query)
  return c.fetchall()

def getReviewerDecisions(uid):
  sql = ("SELECT * FROM APPLICATION_REVIEW WHERE AID = %s")
  query = (uid,)
  c.execute(sql,query)
  return c.fetchall()      

def commitFinalDecision(form,uid):
  decision = form.get("final_decision")
  sql = ("SELECT REVIEWED FROM APPLICATION WHERE UID = %s")
  query = (uid,)
  c.execute(sql,query)
  revCount = c.fetchall()

  sql = ("UPDATE APPLICATION SET REVIEWED = %s WHERE UID = %s")
  query = (revCount[0]["REVIEWED"]+1,uid)
  c.execute(sql,query)

  if int(decision) > 1:
      sql = ("UPDATE users SET typeuser = %s WHERE uid = %s")
      query = ("student",uid)
      c.execute(sql,query) 

      c.execute("SELECT * FROM APPLICATION INNER JOIN DEGREE ON DEGREE.num_degree = APPLICATION.APPLIED_DEGREE WHERE UID = %s;",(uid,))
      info = c.fetchall()

      c.execute("INSERT INTO faculty_advisor VALUES (%s, %s);", (uid, 0))
      sql = ("INSERT INTO students (uid,degree,major,admit_year,fac_advisor,GPA,thesis,thesis_approval,grad_pending) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)")
      print(info[0])
      query = (uid,info[0]["degree"],"Computer Science",info[0]["YEAR_SUBMITTED"],0,0.0,'',0,0)
      c.execute(sql,query)
      print(query)
  else:
      sql = ("SELECT AID FROM APPLICATION WHERE UID = %s")
      query = (uid,)
      c.execute(sql,query)
      aid = c.fetchall()    

      sql = ("UPDATE APP_STATUS SET APP_STATUS.app_status = %s WHERE AID = %s")
      query = (5,aid[0]["AID"])
      c.execute(sql,query) 
  mydb.commit()          



def commitReview(form,uid,reviewerUID):
  rating = form.get("Rating")
  generic = form.get("Generic")
  credible = form.get("Credible")
  decision = form.get("decision")
  deficiency = form.get("deficiency")
  comments = form.get("comments")

  sql = ("SELECT AID FROM APPLICATION WHERE UID = %s")
  query = (uid,)
  c.execute(sql,query)
  aid = c.fetchall()

  sql = ("INSERT INTO APPLICATION_REVIEW (reviewerID,AID,comments,deficiency,decision) VALUES (%s,%s,%s,%s,%s)")
  query = (reviewerUID,aid[0]["AID"],comments,deficiency,decision)
  c.execute(sql,query)

  sql = ("INSERT INTO REC_LETTER_RATING (UID,rating,generic,credible) VALUES (%s,%s,%s,%s)")
  query = (uid,rating,generic,credible)
  c.execute(sql,query)

  sql = ("SELECT REVIEWED FROM APPLICATION WHERE UID = %s")
  query = (uid,)
  c.execute(sql,query)
  revCount = c.fetchall()

  #Every time an application gets reviewed, add 1 to the reviewed column in application. if reviewed = 3, then goes to the gradsec for final decision

  sql = ("UPDATE APPLICATION SET REVIEWED = %s WHERE UID = %s")
  query = (revCount[0]["REVIEWED"]+1,uid)
  print(revCount[0]["REVIEWED"])
  c.execute(sql,query)

#   sql1 = ("SELECT * from DECISION INNER JOIN APPLICATION_REVIEW ON DECISION.decision_num = APPLICATION_REVIEW.decision WHERE APPLICATION_REVIEW.AID = %s")
#   query1 = (aid[0]["AID"],)
#   c.execute(sql1,query1)

#   dec = c.fetchall()

#   if dec[0]["decision_num"] > 1:
#       sql = ("UPDATE users SET typeuser = %s WHERE uid = %s")
#       query = ("student",uid)
#       c.execute(sql,query) 

#       c.execute("SELECT * FROM APPLICATION INNER JOIN DEGREE ON DEGREE.num_degree = APPLICATION.APPLIED_DEGREE WHERE UID = %s;",(uid,))
#       info = c.fetchall()

#       c.execute("INSERT INTO faculty_advisor VALUES (%s, %s);", (uid, 0))
#       sql = ("INSERT INTO students (uid,degree,major,admit_year,fac_advisor,GPA,thesis,thesis_approval,grad_pending) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)")
#       print(info[0])
#       query = (uid,info[0]["degree"],"Computer Science",info[0]["YEAR_SUBMITTED"],0,0.0,'',0,0)
#       print(query)
#       c.execute(sql,query)   
  mydb.commit()    




      
        
def commitApp(form,uid):
  ID = uid
  year = form.get("year_submitted")
  semester = form.get("semester")
  interest = form.get("interest")
  experience = form.get("experience")
  degree = form.get("applied_degree")
  gre_verbal = form.get("gre_verbal")
  gre_quant = form.get("gre_quant")
  toefl_score = form.get("toefl_score")
  toefl_year = form.get("toefl_year")
  gre_adv_score = form.get("gre_adv_score")
  gre_adv_subj = form.get("gre_adv_subj")
  
  prior_deg1 = form.get("prior_deg1")
  gpa1 = form.get("gpa1")
  major1 = form.get("major1")
  year1 = form.get("year1")
  schoolname1 = form.get("schoolname1")

  prior_deg2 = form.get("prior_deg2")
  gpa2 = form.get("gpa2")
  major2 = form.get("major2")
  year2 = form.get("year2")
  schoolname2 = form.get("schoolname2")

  if not appSubmitted(ID):
    sql = ("INSERT INTO APPLICATION(UID,YEAR_SUBMITTED,SEMSTR_SUBMITTED,INTERESTS,EXPERIENCE,APPLIED_DEGREE,GRE_VERBAL,GRE_QUANT,TOEFL_SCORE,TOEFL_YEAR,GRE_ADV_SCORE,GRE_ADV_SUBJ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
    query = (ID,year,semester,interest,experience,degree,gre_verbal,gre_quant,toefl_score,toefl_year,gre_adv_score,gre_adv_subj)
    c.execute(sql,query)

    sql5 = ("UPDATE APPLICATION SET SUBMITTED = %s WHERE UID = %s")
    query5 = (1,ID)
    c.execute(sql5,query5)

    sql6 = ("UPDATE APPLICATION SET REVIEWED = %s WHERE UID = %s")
    query6 = (0,ID)
    c.execute(sql6,query6)

    sql7 = ("INSERT INTO TRANSCRIPT (UID,SUBMITTED) VALUES (%s,%s)")
    query7 = (ID,0)
    c.execute(sql7,query7)

    sql3 = ("SELECT AID FROM APPLICATION WHERE UID = %s")
    query3 = (ID,)
    c.execute(sql3,query3)
    aid = c.fetchall()

    sql2 = ("INSERT INTO APP_STATUS (AID,app_status) VALUES (%s,%s)")
    query2 = (aid[0]["AID"],1)
    c.execute(sql2,query2)
  else:
    sql3 = ("SELECT AID FROM APPLICATION WHERE UID = %s")
    query3 = (ID,)
    c.execute(sql3,query3)
    aid = c.fetchall()

    sql = ("UPDATE APPLICATION SET YEAR_SUBMITTED = %s, SEMSTR_SUBMITTED = %s,INTERESTS = %s,EXPERIENCE = %s,APPLIED_DEGREE = %s,GRE_VERBAL = %s,GRE_QUANT = %s,TOEFL_SCORE = %s,TOEFL_YEAR = %s,GRE_ADV_SCORE = %s,GRE_ADV_SUBJ = %s WHERE APPLICATION.AID = %s")  
    query = (year,semester,interest,experience,degree,gre_verbal,gre_quant,toefl_score,toefl_year,gre_adv_score,gre_adv_subj,aid[0]["AID"])
    c.execute(sql,query)

  sql = ("SELECT * FROM PRIOR_DEGREE WHERE UID = %s")
  query = (ID,)
  c.execute(sql,query)
  if c.fetchall() != []:
    sql4 = ("DELETE FROM PRIOR_DEGREE WHERE UID = %s")
    query4 =(ID,)
    c.execute(sql4,query4)

  if prior_deg1 is not None:
    sql = ("INSERT INTO PRIOR_DEGREE(UID,prior_deg,gpa,major,year,schoolname) VALUES (%s,%s,%s,%s,%s,%s)")
    query = (ID,prior_deg1,gpa1,major1,year1,schoolname1)
    c.execute(sql,query)
  if prior_deg2 is not None:
    print(prior_deg2)
    sql = ("INSERT INTO PRIOR_DEGREE(UID,prior_deg,gpa,major,year,schoolname) VALUES (%s,%s,%s,%s,%s,%s)")
    query = (ID,prior_deg2,gpa2,major2,year2,schoolname2)
    c.execute(sql,query)
  if prior_deg1 is None or prior_deg2 is None:
      sql = ("INSERT INTO PRIOR_DEGREE(UID,prior_deg,gpa,major,year,schoolname) VALUES (%s,%s,%s,%s,%s,%s)")
      #can be possible error, change back to None if there are any
      query = (ID,4,0,"",0,"") 
      c.execute(sql,query)
  mydb.commit()    


@app.route('/formOne', methods=['GET', 'POST'])
def formOne():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    ray_classes = ["CSCI 6221", "CSCI 6461", "CSCI 6212", "CSCI 6220", "CSCI 6232", 
                  "CSCI 6233", "CSCI 6241", "CSCI 6242", "CSCI 6246", "CSCI 6260",
                  "CSCI 6251", "CSCI 6254", "CSCI 6262", "CSCI 6283", "CSCI 6284",
                  "CSCI 6286", "CSCI 6325", "CSCI 6339", "CSCI 6384", "ECE 6241",
                  "ECE 6242", "MATH 6210"
                 ]
    cursor = mydb.cursor(buffered=True,dictionary=True)
    mes = ""

    cursor.execute("SELECT grade, courses.course_dname, courses.course_num, courses.course_name, courses.credits, courses.course_id, sects.semester, sects.year, sects.day_name, sects.start_time, sects.end_time, users.fname, users.lname, users.email FROM takes INNER JOIN sects ON takes.s_id = sects.sect_id INNER JOIN courses ON sects.courseid = courses.course_id INNER JOIN users ON sects.prof_id = users.uid WHERE student_id = %s;", (session['uid'],))
    results = cursor.fetchall()
    num_courses=len(results)

    if request.method == 'POST':
        u_id = session['uid']
        fname = session['fname']
        ray = []
        cursor.execute("SELECT degree FROM students where uid = %s", (session['uid'],))
        degree = cursor.fetchone()
        print(degree)
        deg = degree['degree']

        for i in range(1,23):
            s = "dept_name" + str(i);
            dname = request.form[s];
            if dname == "":
                continue
            dname = dname.upper()
            s = "course_num" + str(i)
            cnum = request.form[s]
            classToAdd = dname + " " + cnum
            if classToAdd not in ray_classes:
                mes = "Class " + classToAdd + " is not available, please try again"
                return render_template("form1.html", mes = mes, courses=results, num_courses=num_courses)
            if classToAdd in ray:
                mes = "Can not have duplicate classes: \"" + classToAdd + "\""
                return render_template("form1.html", mes = mes, courses=results, num_courses=num_courses)
            ray.append(classToAdd);

        csCred = 0
        regCred = 0
        if deg == "PHD":
            for c in ray:
                first_word = c.split()[0]
                if first_word == "CSCI":
                    csCred += 3
                else:
                    if c == "ECE 6242" or c == "MATH 6210":
                        regCred += 2
                    else:
                        regCred += 3
            if csCred+regCred < 36:
                mes = "Must complete at least 36 credit hours for an PhD Degree, please try again"
                return render_template("form1.html", mes = mes, courses=results, num_courses=num_courses)
            elif csCred < 30:
                mes = "Must take at least 30 credits in CS for an PhD Drgree, please try again"
                return render_template("form1.html", mes = mes, courses=results, num_courses=num_courses)   
        else:
            reqCor = ["CSCI 6212", "CSCI 6221", "CSCI 6461"]
            countNonCS = 0
            for c in ray:
                first_word = c.split()[0]
                if first_word == "CSCI":
                    csCred += 3
                    if c in reqCor:
                        reqCor.remove(c)
                else:
                    countNonCS += 1
                    if c == "ECE 6242" or c == "MATH 6210":
                        regCred += 2
                    else:
                        regCred += 3
            if len(reqCor) != 0:
                mes = "Must take CSCI 6212, CSCI 6221, and CSCI 6461 for an Master's Degree, please try again"
                return render_template("form1.html", mes = mes, courses=results, num_courses=num_courses)
            elif csCred+regCred < 30:
                mes = "Must complete at least 30 credit hours of coursework for an Master's Degree, please try again"
                return render_template("form1.html", mes = mes, courses=results, num_courses=num_courses)
            elif countNonCS > 2:
                mes = "Taken at most 2 courses outside the CS department as part of the 30 credit hours of coursework, please try again"
                return render_template("form1.html", mes = mes, courses=results, num_courses=num_courses)

        cursor.execute ("INSERT INTO form (form_ID, deg_type, form_fname) VALUES (%s, %s, %s)", (u_id, deg, fname))    
        mydb.commit()
        for c in ray:
            first_word = c.split()[0]
            second_word = c.split()[1]
            cursor.execute ("INSERT INTO form_data (form_data_ID, form_dept_name, form_course_number) VALUES (%s, %s, %s)", (u_id, first_word, second_word))
            mydb.commit()
        mes = "Successfully Submitted Form1! Thank You!"
        cursor.execute("SELECT * FROM users")
        query = cursor.fetchall()
        cursor.execute("SELECT grade, courses.course_dname, courses.course_num, courses.course_name, courses.credits, courses.course_id, sects.semester, sects.year, sects.day_name, sects.start_time, sects.end_time, users.fname, users.lname, users.email FROM takes INNER JOIN sects ON takes.s_id = sects.sect_id INNER JOIN courses ON sects.courseid = courses.course_id INNER JOIN users ON sects.prof_id = users.uid WHERE student_id = %s;", (session['uid'],))
        history = cursor.fetchall()
        
        cursor.execute("SELECT * FROM students where uid = %s", (session['uid'],))
        grad_stu_data = cursor.fetchall()
        cursor.execute("SELECT * FROM form where form_ID = %s", (session['uid'],))
        form1 = cursor.fetchall()
        form1_exist = False
        if len(form1) != 0:
            form1_exist = True
        return render_template("dashboard.html", msg=mes,form1_exist=form1_exist, data=grad_stu_data, )
    return render_template("form1.html", mes = mes, courses=results, num_courses=num_courses)


@app.route('/edit_info', methods=['GET', 'POST'])
def edit_info():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    cursor=mydb.cursor(dictionary=True)
    if request.method == 'POST': #once user has updated their info, update database
        first_name=request.form["first_name"]
        cursor.execute("UPDATE users SET fname = %s WHERE uid = %s",(first_name, session['uid'],))
        mydb.commit()
        last_name=request.form["last_name"]
        cursor.execute("UPDATE users SET lname = %s WHERE uid = %s",(last_name, session['uid'],))
        mydb.commit()
        address=request.form["address"]
        cursor.execute("UPDATE users SET address = %s WHERE uid = %s",(address, session['uid'],))
        mydb.commit()
        password=request.form["password"]
        cursor.execute("UPDATE users SET password = %s WHERE uid = %s",(password, session['uid'],))
        mydb.commit()
        email=request.form["email"]
        cursor.execute("UPDATE users SET email = %s WHERE uid = %s",(email, session['uid'],))
        mydb.commit()
        return redirect("/dashboard")
    # load the edit info page
    cursor.execute("SELECT fname, lname, address, email, password FROM users WHERE uid = %s",(session['uid'],))
    info = cursor.fetchone()
    return render_template("edit_info.html", info=info)

@app.route('/thesis_page', methods=['GET', 'POST'])
def thesis_page():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    cursor = mydb.cursor(dictionary=True) 
    cursor.execute("SELECT * FROM students where uid = %s", (session['uid'],))
    grad_stu_data = cursor.fetchall()
    return render_template("thesis_page.html", data=grad_stu_data)

@app.route('/view_thesis', methods=['GET', 'POST'])
def view_thesis():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    cursor = mydb.cursor(dictionary=True)
    stuID = request.form["stu_id2"]
    cursor.execute("SELECT thesis FROM students WHERE uid = %s",(stuID,))
    Thesis = cursor.fetchone()
    cursor.execute("SELECT thesis_approval FROM students WHERE uid = %s",(stuID,))
    thesis_status = cursor.fetchone()
    return render_template("view_thesis.html", Thesis=Thesis, thesis_status = thesis_status, stu_id = stuID)

@app.route('/submit_thesis', methods=['GET', 'POST'])
def submit_thesis():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    cursor = mydb.cursor(dictionary=True)
    if request.method == 'POST':
        submitted_thesis = request.form["submitted_thesis"]
        cursor.execute("UPDATE students SET thesis = %s WHERE uid = %s",(submitted_thesis, session['uid'],))
        mydb.commit()
        return redirect("/dashboard")

@app.route('/advisor_students', methods=['GET', 'POST'])
def advisor_students():
    # some select statment that combines tables to see which student is associated with the advisor...
    # so they can see the transcripts
    # update thesis_approval functionality once approved
    cursor=mydb.cursor(dictionary=True)
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    cursor = mydb.cursor()
    if request.method == 'POST': 
        stuID = request.form["stu_id"]
        cursor.execute("UPDATE students SET thesis_approval = %s WHERE uid = %s",(1, stuID,))
    cursor.execute("SELECT stu_ID FROM faculty_advisor where advisor_ID = %s", (session['uid'],))
    stu_list = cursor.fetchall()
    dict_pro = {}
    dict_thesis = {}
    dict_thesis_status = {}
    for s in stu_list:
        stu = s[0]
        cursor.execute("SELECT degree FROM students where uid = %s", (stu,))
        stu_pro = cursor.fetchone()
        dict_pro[stu] = stu_pro[0];
        if stu_pro[0] == "PHD":
            cursor.execute("SELECT thesis FROM students where uid = %s", (stu,))
            stu_thesis = cursor.fetchone()
            dict_thesis[stu] = stu_thesis[0];
            cursor.execute("SELECT thesis_approval FROM students where uid = %s", (stu,))
            stu_thesis_status = cursor.fetchone()
            dict_thesis_status[stu] = stu_thesis_status[0];
    dict_form = {}
    for s in stu_list:
        stu = s[0]
        cursor.execute("SELECT * FROM form where form_ID = %s", (stu,))
        stu_form = cursor.fetchall()
        if len(stu_form) == 0:
            continue
        cursor.execute("SELECT * FROM form_data where form_data_ID = %s", (stu,))
        stu_form_info = cursor.fetchall()
        dict_form[stu] = stu_form_info;
    return render_template("advisor_student.html", typeuser = session['typeuser'], dict_pro = dict_pro, dict_form = dict_form, stu_list = stu_list, dict_thesis = dict_thesis, dict_thesis_status = dict_thesis_status)

@app.route('/view_form1', methods=['GET', 'POST'])
def view_form1():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    if request.method == 'POST':
        stuID = request.form["stu_id1"]
        cursor=mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM form_data WHERE form_data_ID = %s",(stuID,))
        info = cursor.fetchall()
        return render_template("view_form1.html", info=info, stu_id = stuID)


@app.route('/allusers', methods=['GET', 'POST'])
def view_users():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    cursor=mydb.cursor()
    cursor.execute("SELECT uid, fname, lname, address, email, phone, typeuser FROM users WHERE uid <> 0 AND typeuser = 'admin';")
    admins = cursor.fetchall()
    cursor.execute("SELECT uid, fname, lname, address, email, phone, typeuser FROM users WHERE uid <> 0 AND typeuser = 'gradsecretary';")
    gradsecs = cursor.fetchall()
    cursor.execute("SELECT uid, fname, lname, address, email, phone, typeuser FROM users WHERE uid <> 0 AND typeuser = 'advisor';")
    advisors = cursor.fetchall()
    cursor.execute("SELECT uid, fname, lname, address, email, phone, typeuser FROM users WHERE uid <> 0 AND typeuser = 'professor';")
    profs = cursor.fetchall()
    cursor.execute("SELECT uid, fname, lname, address, email, phone, typeuser FROM users WHERE uid <> 0 AND typeuser = 'student';")
    studs = cursor.fetchall()
    cursor.execute("SELECT uid, fname, lname, address, email, phone, typeuser FROM users WHERE uid <> 0 AND typeuser = 'alumni';")
    alums = cursor.fetchall()
    ##sorting is not used since advisors come before gradsecretary when sorted alphabetically when gradsecretaries are more powerful    
    return render_template("info.html", admins = admins, gradsecs = gradsecs, advisors = advisors, profs = profs, studs = studs, alums=alums)

@app.route('/allstudents', methods=['GET', 'POST'])
def view_students():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if session['flag'] == 1:
        return redirect(url_for('studentadd'))
    cursor=mydb.cursor()
    cursor.execute("SELECT students.uid, fname, lname, address, email, phone, degree, major, admit_year, fac_advisor, GPA, thesis, thesis_approval, grad_pending, typeuser FROM users INNER JOIN students ON users.uid = students.uid WHERE users.uid <> 0;")
    info = cursor.fetchall()
    if request.method == 'POST':
        queries = request.form
        queries = dict(queries)
        print(queries)
        if 'submit_search' in queries.keys():
            if not request.form['student_id'].isnumeric() and request.form["student_id"] != "":
                return render_template("student_info.html", students=info, error = "Make sure the id is an integer")  
            if re.search(r'\d', request.form['fname']):
                return render_template("student_info.html", students=info, error = "Make sure the first name is not a number")  
            if re.search(r'\d', request.form['lname']):
                return render_template("student_info.html", students=info, error = "Make sure the last name is not a number")       
            if len(request.form['student_id']) > 7 and request.form['fname'] != '' and request.form['lname'] != '':
                cursor.execute("SELECT students.uid, fname, lname, address, email, phone, degree, major, admit_year, fac_advisor, GPA, thesis, thesis_approval, grad_pending, typeuser FROM users INNER JOIN students ON users.uid = students.uid WHERE users.uid = %s AND users.fname = %s AND users.lname = %s;", (request.form['student_id'],request.form['fname'], request.form['lname']))
                info = cursor.fetchall()
                return render_template("student_info.html", students=info, error = None)        
            elif len(request.form['student_id']) > 7 and request.form['fname'] != '' and request.form['lname'] == '':
                cursor.execute("SELECT students.uid, fname, lname, address, email, phone, degree, major, admit_year, fac_advisor, GPA, thesis, thesis_approval, grad_pending, typeuser FROM users INNER JOIN students ON users.uid = students.uid WHERE users.uid = %s AND users.fname = %s;", (request.form['student_id'],request.form['fname']))
                info = cursor.fetchall()
                return render_template("student_info.html", students=info, error = None)    
            elif len(request.form['student_id']) > 7 and request.form['fname'] == '' and request.form['lname'] != '':
                cursor.execute("SELECT students.uid, fname, lname, address, email, phone, degree, major, admit_year, fac_advisor, GPA, thesis, thesis_approval, grad_pending, typeuser FROM users INNER JOIN students ON users.uid = students.uid WHERE users.uid = %s AND users.lname = %s;", (request.form['student_id'], request.form['lname']))
                info = cursor.fetchall()
                return render_template("student_info.html", students=info, error = None)    
            elif len(request.form['student_id']) > 7 and request.form['fname'] == '' and request.form['lname'] == '':
                cursor.execute("SELECT students.uid, fname, lname, address, email, phone, degree, major, admit_year, fac_advisor, GPA, thesis, thesis_approval, grad_pending, typeuser FROM users INNER JOIN students ON users.uid = students.uid WHERE users.uid = %s;", (request.form['student_id'],))
                info = cursor.fetchall()
                return render_template("student_info.html", students=info, error = None)    
            elif len(request.form['student_id']) <= 7 and request.form['fname'] != '' and request.form['lname'] != '':
                cursor.execute("SELECT students.uid, fname, lname, address, email, phone, degree, major, admit_year, fac_advisor, GPA, thesis, thesis_approval, grad_pending, typeuser FROM users INNER JOIN students ON users.uid = students.uid WHERE users.fname = %s AND users.lname = %s;", (request.form['fname'], request.form['lname']))
                info = cursor.fetchall()
                return render_template("student_info.html", students=info, error = None)    
            elif len(request.form['student_id']) <= 7 and request.form['fname'] != '' and request.form['lname'] == '':
                cursor.execute("SELECT students.uid, fname, lname, address, email, phone, degree, major, admit_year, fac_advisor, GPA, thesis, thesis_approval, grad_pending, typeuser FROM users INNER JOIN students ON users.uid = students.uid WHERE users.fname = %s;", (request.form['fname'],))
                info = cursor.fetchall()
                return render_template("student_info.html", students=info, error = None)    
            elif len(request.form['student_id']) <= 7 and request.form['fname'] == '' and request.form['lname'] != '':
                cursor.execute("SELECT students.uid, fname, lname, address, email, phone, degree, major, admit_year, fac_advisor, GPA, thesis, thesis_approval, grad_pending, typeuser FROM users INNER JOIN students ON users.uid = students.uid WHERE users.lname = %s;", (request.form['lname'],))
                info = cursor.fetchall()
                return render_template("student_info.html", students=info, error = None)
            else:
                return render_template("student_info.html", students=info, error = None)                    
        if request.form["advisor_id"].isnumeric() == False:
            return render_template("student_info.html", students=info, error = "Please input an integer")
        cursor.execute("SELECT uid, typeuser FROM users where uid = %s",(request.form["advisor_id"],))
        result = cursor.fetchall()
        if len(result) == 0:
            return render_template("student_info.html", students=info, error = "Please input an existing ID")
        if result[0][1] != 'advisor':
            return render_template("student_info.html", students=info, error = "Please input an advisor's ID")
        cursor.execute("SELECT stu_ID, advisor_ID FROM faculty_advisor WHERE stu_ID = %s;", (request.form["student_id"],))
        result = cursor.fetchall()
        print(result)
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("UPDATE faculty_advisor SET advisor_ID = %s WHERE stu_ID = %s;",(request.form["advisor_id"], request.form["student_id"]))
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        cursor.execute("UPDATE students SET fac_advisor = %s WHERE students.uid = %s;",(request.form["advisor_id"], request.form["student_id"]))
    cursor.execute("SELECT students.uid, fname, lname, address, email, phone, degree, major, admit_year, fac_advisor, GPA, thesis, thesis_approval, grad_pending, typeuser FROM users INNER JOIN students ON users.uid = students.uid WHERE users.uid <> 0;")
    info = cursor.fetchall()
    return render_template("student_info.html", students=info, error = None)

# TODO/IP: can't apply to graduate if form not submitted (and for PHD, if thesis not approved)
@app.route('/apply_to_graduate', methods=['GET', 'POST'])
def apply_to_graduate():
    if session.get('uid') is None:
        return redirect('/')
    cursor = mydb.cursor(dictionary=True)

    cursor.execute("SELECT degree FROM students WHERE uid=%s",(session['uid'],))
    degree_type = cursor.fetchone()
    degree_type = degree_type['degree']
    cursor.execute("SELECT grade, courses.course_dname, courses.course_num, courses.course_name, courses.credits, courses.course_id, sects.semester, sects.year, sects.day_name, sects.start_time, sects.end_time, users.fname, users.lname, users.email FROM takes INNER JOIN sects ON takes.s_id = sects.sect_id INNER JOIN courses ON sects.courseid = courses.course_id INNER JOIN users ON sects.prof_id = users.uid WHERE student_id = %s;", (session['uid'],))
    course_history_data = cursor.fetchall() 

    # TODO?
    # data (for passing in render_template)
    cursor.execute("SELECT * FROM students where uid = %s", (session['uid'],))
    grad_stu_data = cursor.fetchall()
    # form1 data (for passing in render_template)
    cursor.execute("SELECT * FROM form where form_ID = %s", (session['uid'],))
    form1 = cursor.fetchall()
    form1_exist = False;
    if len(form1) != 0:
        form1_exist = True
    if grad_stu_data[0]['grad_pending'] == 1:
        return render_template("dashboard.html", msg="Error: Already Applied for Graduation", data=grad_stu_data, form1_exist = form1_exist)
    if form1_exist == 0:
        return render_template("dashboard.html", msg="Error: Must Submit Form 1", data=grad_stu_data, form1_exist = form1_exist)

    # get the form data for the graduating student
    cursor.execute("SELECT * FROM form_data WHERE form_data_ID=%s",(session['uid'],))
    form_data = cursor.fetchall()
    # get the enrollment history for the graduating student

    #1: check if the form courses are in enrollment history
    for idx_form in range(len(form_data)):
        found=0
        for idx_enroll in range(len(course_history_data)):
            if(form_data[idx_form]['form_dept_name'] == course_history_data[idx_enroll]['course_dname'] and int(form_data[idx_form]['form_course_number']) == int(course_history_data[idx_enroll]['course_num'])):
                found=1;
                break
        if found==0:
            return render_template("dashboard.html", msg="Error: Required Course Not Taken", data=grad_stu_data, form1_exist = form1_exist)
    # here, all required courses were taken
    
    if degree_type == "MS": # MS Degree Type: audit
        
        #2: check grades
        #check min gpa of 3.0
        cursor.execute("SELECT GPA FROM students where uid = %s", (session['uid'],))
        total_GPA = cursor.fetchall()
        if total_GPA[0]['GPA'] < 3.0:
            return render_template("dashboard.html", msg="Error: GPA too low", data=grad_stu_data, form1_exist = form1_exist)

        #no more than 2 grades below B
        lessthan_B = 0
        for idx_enroll in range(len(course_history_data)):
            gr=course_history_data[idx_enroll]['grade']
            if(gr == 'B-' or gr == 'C+' or gr == 'C' or gr == 'C-' or gr == 'F'):
                lessthan_B+=1
            elif course_history_data[idx_enroll]['grade'] == ('IP'): #can't apply to graduate with an 'IP' course grade
                return render_template("dashboard.html", msg="Error: One or More Courses In Progress", data=grad_stu_data, form1_exist = form1_exist)
        if(lessthan_B >= 3):
            return render_template("dashboard.html", msg="Error: Too Many Grades Below B", data=grad_stu_data, form1_exist = form1_exist)
              
        # here, they've passed all requirements
        cursor.execute("UPDATE students SET grad_pending = 1 WHERE uid = %s",(session['uid'],))
        mydb.commit()
        return render_template("dashboard.html", degree_type = degree_type, msg='Successfully Applied to Graduate', data=grad_stu_data, form1_exist = form1_exist)
        
        
    else: # PhD Degree Type: audit
        #1: check grades
        #check min gpa of 3.5
        cursor.execute("SELECT GPA FROM students where uid = %s", (session['uid'],))
        total_GPA = cursor.fetchall()
        if total_GPA[0]['GPA'] < 3.5:
            return render_template("dashboard.html", msg="Error: GPA too low", data=grad_stu_data, form1_exist = form1_exist)

        #no more than 1 grade below B
        lessthan_B = 0
        for idx_enroll in range(len(course_history_data)):
            gr=course_history_data[idx_enroll]['grade']
            if(gr == 'B-' or gr == 'C+' or gr == 'C' or gr == 'C-' or gr == 'F'):
                lessthan_B+=1
            elif course_history_data[idx_enroll]['grade'] == ('IP'): #can't apply to graduate with an 'IP' course grade
                return render_template("dashboard.html", msg="Error: One or More Courses In Progress", data=grad_stu_data, form1_exist = form1_exist)
        if(lessthan_B >= 2):
            return render_template("dashboard.html", msg="Error: Too Many Grades Below B", data=grad_stu_data, form1_exist = form1_exist)

        #2: thesis approval
        cursor.execute("SELECT * FROM students where uid = %s", (session['uid'],))
        grad_stu_data = cursor.fetchall()
        if grad_stu_data[0]['thesis_approval'] == 0:
            return render_template("dashboard.html", msg="Error: Thesis not approved", data=grad_stu_data, form1_exist = form1_exist)

        # here, they've passed all requirements
        cursor.execute("UPDATE students SET grad_pending = 1 WHERE uid = %s",(session['uid'],))
        mydb.commit()
        return render_template("dashboard.html", degree_type = degree_type, msg='Successfully Applied to Graduate', data=grad_stu_data, form1_exist = form1_exist)

@app.route('/graduate_to_alum', methods=['GET', 'POST'])
def graduate_to_alum():    
    cursor=mydb.cursor(dictionary=True)
    if request.method == 'POST':
        stu_id = request.form["cur_student_ID"]
        # cursor.execute("UPDATE students SET grad_pending = 0 WHERE uid = %s",(stu_id,))
        # mydb.commit()
        cursor.execute("UPDATE users SET typeuser = 'alumni' WHERE uid = %s",(stu_id,)) #change their role from grad_stu to alumni
        mydb.commit()
        return redirect("/dashboard")

@app.route('/set_year', methods=['GET', 'POST'])
def yearset():
    if session.get('uid') is None:
        return redirect(url_for('home'))
    if request.method == 'POST':
        session['semester'] = int(request.form['sem_no'])
        return redirect("/coursereg")
    return render_template("set_year.html", error = None)

@app.route('/forgot_pw',methods=['POST','GET'])
def forgot_pw():
    cursor=mydb.cursor(dictionary=True)
    if request.method == 'POST':
        u_fname = request.form["fname_pw"]
        u_lname = request.form["lname_pw"]
        u_ssn = request.form["ssn_pw"]
        cursor.execute("SELECT password, uid FROM users WHERE fname = %s AND lname = %s AND ssn = %s",(u_fname, u_lname, u_ssn))
        info = cursor.fetchall()
        if(info):
            print(info)
            print(info[0])
            return render_template("forgot_pw.html", pass_pw=info[0]['password'], u_uid=info[0]['uid'], mes='')
        else:
            mes="Error: User Not Found"
            return render_template("forgot_pw.html", mes=mes, pass_pw='')
    return render_template("forgot_pw.html", mes='', pass_pw='')

@app.route('/reset_pass',methods=['POST','GET'])
def reset_pass():
    cursor=mydb.cursor(dictionary=True)
    new_p = request.form["new_pw"]
    u_uid = request.form["u_uid"]
    cursor.execute("UPDATE users SET password = %s WHERE uid = %s",(new_p, u_uid))
    mydb.commit()
    return redirect("/dashboard")


app.run(host='0.0.0.0', port=8080)