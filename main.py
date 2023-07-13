from flask import Flask,render_template,request, flash,redirect, url_for, jsonify,send_file
from config_file import client
from models import *
import secrets
import datetime
from bson import ObjectId
# from datetime import datetime
from random import randint
import os

import json

app = Flask(__name__)

app.secret_key='my_key'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','mp4','csv','xlsx'}

UPLOAD_FOLDER = 'static/images/wellness/hs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/wellness/hs/<filename>')
def send_uploaded_file(filename=''):
    from flask import send_from_directory
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

UPLOAD_FOLDER_PERMISSION = 'static/images/wellness/permission_letter'
app.config['UPLOAD_FOLDER_PERMISSION'] = UPLOAD_FOLDER_PERMISSION

@app.route('/wellness/permission_letter/<filename>')
def send_uploaded_file_pl(filename=''):
    from flask import send_from_directory
    return send_from_directory(app.config["UPLOAD_FOLDER_PERMISSION"],filename)

@app.route('/',methods=['POST','GET'])
def hsNavPage():
    return render_template("wellness/health/hs_nav.html")


@app.route("/wellnessCenterRegistration",methods=['POST','GET'])
def wellnessCenterRegistrationPage():
    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName')
    emailId = request.form.get('emailId')
    phoneNumber = request.form.get('phoneNumber')
    password = request.form.get('password')
    hsRefLink = secrets.token_urlsafe()
    createdOn = datetime.datetime.now()
    status = 1
    if request.method == 'POST':
        try:
            queryset = WellnessCenterRegistration.objects(emailId__iexact=emailId)
            if queryset:
                flash("User already Exists!!")
                return render_template("wellness/health/hs_register.html")
        except Exception as e:
            pass
        add_well_data = WellnessCenterRegistration(
            firstName = firstName,
            lastName = lastName,
            emailId = emailId,
            phoneNumber = phoneNumber,
            password = password,
            hsRefLink = hsRefLink,
            createdOn = createdOn,
            status = status
            )
        hs_reg_data = add_well_data.save()
        hs_reg_id = str(hs_reg_data.id)
        if hs_reg_id:
            profilePic = request.files['profilePic']
            if profilePic.filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS:
                ext = profilePic.filename.rsplit('.',1)[1].lower()
                file_name = str(hs_reg_id)+"."+ext
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.mkdir(app.config['UPLOAD_FOLDER'])
                profile = app.config['UPLOAD_FOLDER']
                profilePic.save(os.path.join(profile,file_name))
            hs_reg_data.update(profilePic=file_name)
        if hs_reg_data:
            flash("Registration Successfully Done!!")
            return redirect(url_for('wellnessCenterPage'))
        else:
            flash("Required fields are missing !!!")
            return render_template('wellness/health/hs_register.html')
    else:
        return render_template('wellness/health/hs_register.html')

@app.route("/wellnessCenter",methods=['POST','GET'])
def wellnessCenterPage():
    emailId = request.form.get('emailId')
    password = request.form.get('password')

    if emailId and password and request.method=='POST':
        try:
            get_hs_logins = WellnessCenterRegistration.objects.get(emailId__iexact=emailId,password__exact=password,status__in=[1])
            if get_hs_logins:
                hsRefLink = get_hs_logins.hsRefLink
                return redirect(url_for('wellnessCenterDashboardPage',hsRefLink=hsRefLink))
            else:
                flash("Invalid Credentials!!!")
                return render_template("wellness/health/hs_login.html")
        except WellnessCenterRegistration.DoesNotExist as e:
            flash("Invalid Credentials!!!")
            return render_template("wellness/health/hs_login.html")
    return render_template('wellness/health/hs_login.html')

@app.route('/wellnessHsForgotPassword',methods=['POST','GET'])
def wellnessHsForgotPasswordPage():
    emailId = request.form.get("emailId")
    newPassword = request.form.get("newPassword")
    confirmPassword = request.form.get("confirmPassword")
    

    if emailId and newPassword and confirmPassword and request.method=="POST":
        if newPassword==confirmPassword:
            get_hs_info = WellnessCenterRegistration.objects.get(emailId=emailId)
            if get_hs_info.emailId:
                updated_password=get_hs_info.update(
                    password=newPassword
                    )
                if updated_password:
                    flash("Password Successfully Changed")
                    return redirect(url_for('wellnessCenterPage'))
            
        else:
            flash("Password Miss Matched")
            return render_template('wellness/health/hs_forgot_password.html')
    
    return render_template('wellness/health/hs_forgot_password.html')

@app.route("/dailySickRegister/<hsRefLink>",methods=['POST','GET'])
def dailySickRegisterPage(hsRefLink):
    studentName = request.form.get('studentName')
    className = request.form.get('className')
    rollNumber = request.form.get('rollNumber')
    diseaseName = request.form.get('diseaseName')
    date = request.form.get('date')
    time = request.form.get('time')
    day = request.form.get('day')
    medicineIssued = request.form.get('medicineIssued')
    studentRefLink = secrets.token_urlsafe()
    createdOn = datetime.datetime.now()

    status = 1
    
    if request.method == 'POST':
        hs_ref_link = WellnessCenterRegistration.objects.get(hsRefLink=hsRefLink)
        student_daily_sick = StudentDailySickRegistration(
            studentName=studentName,
            className=className,
            rollNumber=rollNumber,
            diseaseName=diseaseName,
            date=date,
            time=time,
            day=day,
            medicineIssued=medicineIssued,
            hsRefLink = hs_ref_link.hsRefLink,
            studentRefLink=studentRefLink,
            hsId = str(hs_ref_link.id),
            hsName = hs_ref_link.firstName+" "+hs_ref_link.lastName,
            createdOn=createdOn,
            status=status
            )
        student_daily_sick_info = student_daily_sick.save()
        student_sick_id = str(student_daily_sick_info.id)
        if student_sick_id:
            permissionLetter = request.files['permissionLetter']
            if permissionLetter.filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS:
                ext = permissionLetter.filename.rsplit('.',1)[1].lower()
                file_name = str(student_sick_id)+"."+ext
                if not os.path.exists(app.config['UPLOAD_FOLDER_PERMISSION']):
                    os.mkdir(app.config['UPLOAD_FOLDER_PERMISSION'])
                permssion_letter = app.config['UPLOAD_FOLDER_PERMISSION']
                permissionLetter.save(os.path.join(permssion_letter,file_name))
            student_daily_sick_info.update(permissionLetter=file_name)
        if student_daily_sick_info:
            flash("Sick Student details added Successfully!!")
            return redirect(url_for('wellnessCenterDashboardPage',hsRefLink=hsRefLink))
        else:
            flash("Required fields are missing !!!")
            return render_template('wellness/student/student_daily_sick_reg.html')

    return render_template('wellness/student/student_daily_sick_reg.html')

@app.route("/wellnessCenterDashboard/<hsRefLink>",methods=['POST','GET'])
def wellnessCenterDashboardPage(hsRefLink):
    if request.method=='GET':
        reports_count_list=[]
        
        sick_student_count = StudentDailySickRegistration.objects.count()
        sick_diet_reports = StudentSickDiet.objects.filter(status__in=[1],sickDietStatus__in=[1,2]).count()
        sick_obers_reports = StudentSickDiet.objects.filter(status__in=[1],sickDietStatus__in=[1]).count()
        sick_recovery_reports = StudentSickDiet.objects.filter(status__in=[1],sickDietStatus__in=[2]).count()
        get_hs_link = WellnessCenterRegistration.objects.get(hsRefLink=hsRefLink)
        get_students_count = StudentDetails.objects.count()
        get_students_bmi_data = StudentBmi.objects.filter(status__in=[1]).count()
        get_under_weight_data = StudentBmi.objects.filter(status__in=[1])
        underWeight=0
        if get_under_weight_data: 
            for w in get_under_weight_data:
                if w.bmiValue < 18:
                    underWeight=underWeight+1
                    
        if True:
            reports_count_dict={
                "sickStudentCount":sick_student_count,
                "hsRefLink":get_hs_link.hsRefLink,
                "sickDietReport":sick_diet_reports,
                "sickDietObservation":sick_obers_reports,
                "sickDietRecovery":sick_recovery_reports,
                "totalStudentCount":get_students_count,
                "studentBmiCount":get_students_bmi_data,
                "underWeight":underWeight
            }
        return render_template('wellness/health/hs_wellness_dashboard.html',reports=reports_count_dict)

@app.route("/sickStudentsDetails",methods=['POST','GET'])
def sickStudentsDetailsPage():
    sick_student_list=[]
    sick_student_dict={}
    count=0
    if request.method=='GET':
        get_sick_students = StudentDailySickRegistration.objects.all()

        if get_sick_students:
            for ss in get_sick_students:

                count=count+1
                sick_student_dict={
                    "slNo":count,
                    "rlNo":ss.rollNumber,
                    "studentName":ss.studentName,
                    "className":ss.className,
                    "diseaseName":ss.diseaseName,
                    "date":ss.date,
                    "time":ss.time,
                    "day":ss.day,
                    "medicineIssued":ss.medicineIssued,
                    "medicineIssuedDate":ss.createdOn,
                    "permLetter":ss.permissionLetter,
                    "studentRefLink":ss.studentRefLink
                }
                sick_student_list.append(sick_student_dict)
        return render_template('wellness/student/student_sick_all_reports.html',sick_student_list=sick_student_list)

@app.route("/viewStudentSickPermissionLetter/<studentRefLink>",methods=['POST','GET'])
def viewStudentSickPermissionLetterPage(studentRefLink):
    if request.method=='GET':
        get_letter_dict={}
        get_permission_letter = StudentDailySickRegistration.objects.get(studentRefLink=studentRefLink)
        if get_permission_letter:
            get_letter_dict={
                "permissionLetter":get_permission_letter.permissionLetter
            }
        return render_template('wellness/student/student_sick_permission_letter.html',get_letter_dict=get_letter_dict)
@app.route("/addStudentSickDiet/<studentRefLink>",methods=['POST','GET'])
def addStudentSickDiet(studentRefLink):
    foodItem = request.form.get('foodItem')
    foodQuantity = request.form.get('foodQuantity')
    numberOfTimes = request.form.get('numberOfTimes')
    sickDietStudentRefLink = secrets.token_urlsafe()
    createdOn = datetime.datetime.now()
    status = 1
    if request.method == 'POST':
        get_student_info = StudentDailySickRegistration.objects.get(studentRefLink=studentRefLink)
        
        add_sick_details = StudentSickDiet(
            studentName = get_student_info.studentName,
            className = get_student_info.className,
            rollNumber = get_student_info.rollNumber,
            studentRefLink= get_student_info.studentRefLink,
            studentId = str(get_student_info.id),
            hsId = str(get_student_info.hsId.id),
            foodItem = foodItem,
            diseaseName = get_student_info.diseaseName,
            medicineIssued = get_student_info.medicineIssued,
            foodQuantity = foodQuantity,
            numberOfTimes = numberOfTimes,
            sickDietStudentRefLink = sickDietStudentRefLink,
            createdOn  = createdOn,
            status = status
            )
        added_sick_info = add_sick_details.save()
        if added_sick_info:
            sickDietStatus = 1
            dietAddedOn=datetime.datetime.now()
            update_sick_student = added_sick_info.update(
                sickDietStatus=sickDietStatus,
                dietAddedOn = dietAddedOn
            )
            if update_sick_student:
                
                return redirect(url_for('sickStudentsDetailsPage'))
    return render_template('wellness/student/student_sick_add_diet.html')

@app.route('/sickDietOverallReports',methods=['POST','GET'])
def sickDietOverallReportsPage():
    if request.method=='GET':
        sick_diet_overall = StudentSickDiet.objects(sickDietStatus__in=[1,2],status__in=[1])
        # print(sick_diet_overall.studentName)
        sick_students_list=[]
        sick_student_dict={}
        count=0
        for sick in sick_diet_overall:
            count=count+1
            sick_student_dict={
            "sNo":count,
            "studentName":sick.studentName,
            "className":sick.className,
            "rollNumber":sick.rollNumber,
            "diseaseName":sick.diseaseName,
            "medicineIssued":sick.medicineIssued,
            "status":sick.status,
            "sickDietStudentRefLink":sick.sickDietStudentRefLink,
            "sickDietStatus":sick.sickDietStatus
            }
            sick_students_list.append(sick_student_dict)
        return render_template('wellness/student/sick_diet_overall.html',sick_students_list=sick_students_list)



@app.route('/sickDietObservationReports',methods=['POST','GET'])
def sickDietObservationReportsPage():
    if request.method=='GET':
        sick_diet_overall = StudentSickDiet.objects(status__in=[1],sickDietStatus__in=[1])
        # print(sick_diet_overall.studentName)
        sick_students_list=[]
        sick_student_dict={}
        count=0
        for sick in sick_diet_overall:
            count=count+1
            sick_student_dict={
            "sNo":count,
            "studentName":sick.studentName,
            "className":sick.className,
            "rollNumber":sick.rollNumber,
            "diseaseName":sick.diseaseName,
            "medicineIssued":sick.medicineIssued,
            "status":sick.status
            # "sickDietStatus":sick.sickDietStatus,
            # "dietAddedOn":sick.dietAddedOn
            }
            sick_students_list.append(sick_student_dict)
        return render_template('wellness/student/sick_observation_reports.html',sick_students_list=sick_students_list)

@app.route('/sickDietRecoveryReports',methods=['POST','GET'])
def sickDietRecoveryReportsPage():
    if request.method=='GET':
        sick_diet_overall = StudentSickDiet.objects(status__in=[1],sickDietStatus__in=[2])
        # print(sick_diet_overall.studentName)
        sick_students_list=[]
        sick_student_dict={}
        count=0
        for sick in sick_diet_overall:
            count=count+1
            sick_student_dict={
            "sNo":count,
            "studentName":sick.studentName,
            "className":sick.className,
            "rollNumber":sick.rollNumber,
            "diseaseName":sick.diseaseName,
            "medicineIssued":sick.medicineIssued,
            "status":sick.status
            # "sickDietStatus":sick.sickDietStatus,
            # "dietAddedOn":sick.dietAddedOn
            }
            sick_students_list.append(sick_student_dict)
        return render_template('wellness/student/sick_recovery_reports.html',sick_students_list=sick_students_list)

@app.route("/recoveryStatus/<sickDietStudentRefLink>",methods=['POST','GET'])
def recoveryStatusPage(sickDietStudentRefLink):
    
    get_status = StudentSickDiet.objects.get(sickDietStudentRefLink__in=[sickDietStudentRefLink],status__in=[1])
    recoverdOn = datetime.datetime.now()
    sickDietStatus=2
    if get_status:
        update_status = get_status.update(sickDietStatus=sickDietStatus,recoverdOn=recoverdOn)
    return redirect(url_for('sickDietOverallReportsPage'))


@app.route("/studentsDetails",methods=['POST','GET'])
def studentsDetailsPage():
    student_list=[]
    students_dict={}
    count=0
    className = request.form.get('className')
    if request.method=='POST':
        get_students = StudentDetails.objects.filter(className=className)
        if get_students:
            for gs in get_students:
                count=count+1

                student_dict = {
                    "sl":count,
                    "studentName":gs.firstName+" "+gs.lastName,
                    "className":gs.className,
                    "rollNumber":gs.rollNumber,
                    "status":gs.status
                }
                student_list.append(student_dict)
        elif not get_students:
            # return"no data"
            pass
    return render_template('wellness/student/student_details.html',student_list=student_list)

@app.route("/studentAddBMI/<className>/<rollNumber>",methods=['POST','GET'])
def studentAddBMIPage(className,rollNumber):
    student_list=[]
    students_dict={}
    count=0
    get_students = StudentDetails.objects.get(rollNumber__in=[rollNumber],className__in=[className])
    
    if request.method=='POST':
        height = request.form.get('height')
        weight = request.form.get('weight')
        hemoglobin = request.form.get('hemoglobin')
        age = request.form.get('age')
        month = request.form.get('month')
        bmiValue = int(weight)/(int(height)/100)**2
        try:
            check_month = StudentBmi.objects(month__iexact=month,rollNumber__in=[rollNumber],className__in=[className])
            if check_month:
                flash("Already checked in "+month)
                return render_template('wellness/student/add_height_weight.html')
        except:
            pass
        add_student_bmi = StudentBmi(
            studentName=get_students.firstName+" "+get_students.lastName,
            className=get_students.className,
            rollNumber=get_students.rollNumber,
            height=int(height),
            weight=int(weight),
            hemoglobin=int(hemoglobin),
            age=age,
            month=month,
            bmiValue=int(bmiValue),
            studentId=ObjectId(get_students.id),
            studentRefLink=str(get_students.id),
            createdOn=datetime.datetime.now(),
            status=1
            )
        student_bmi=add_student_bmi.save()
        if student_bmi:
            update_data = get_students.update(
                height=int(student_bmi.height),
                weight=int(student_bmi.weight),
                hemoglobin=int(student_bmi.hemoglobin),
                age = student_bmi.age,
                month=student_bmi.month,
                bmiValue=int(student_bmi.bmiValue),
                studentRefLink=secrets.token_urlsafe(),
                createdOn=student_bmi.createdOn,
                status=2
                )
            flash("Successfully Added Height, Weight and Hemoglobin")
            return redirect(url_for('studentsClassDetailsPage',className=className))
    else:
        return render_template('wellness/student/add_height_weight.html')
@app.route("/studentsClassDetails/<className>")
def studentsClassDetailsPage(className):
    student_list=[]
    students_dict={}
    count=0
    # className = request.form.get('className')
    if request.method=='GET':
        get_students = StudentDetails.objects(className__in=[className])
    
        if get_students:
            for gs in get_students:
                count=count+1

                student_dict = {
                    "sl":count,
                    "studentName":gs.firstName+" "+gs.lastName,
                    "className":gs.className,
                    "rollNumber":gs.rollNumber,
                    "status":gs.status
                }
                student_list.append(student_dict)
    return render_template('wellness/student/class_student_details.html',student_list=student_list)

@app.route("/studentBMIReports",methods=['POST','GET'])
def studentBMIReportsPage():
    student_bmi_list=[]
    student_bmi_dict={}
    count=0
    if request.method=='GET':
        get_students_bmi = StudentBmi.objects(status__in=[1]).order_by('month')
        if get_students_bmi:
            for gsb in get_students_bmi:
                count=count+1
                student_bmi_dict={
                    "slNo":count,
                    "fullName":gsb.studentName,
                    "className":gsb.className,
                    "rollNumber":gsb.rollNumber,
                    "height":gsb.height,
                    "weight":gsb.weight,
                    "hemoglobin":gsb.hemoglobin,
                    "bmiValue":gsb.bmiValue,
                    "month":gsb.month
                }
                student_bmi_list.append(student_bmi_dict)
        elif not get_students_bmi:
            # return"no data"
            pass
    return render_template('wellness/student/student_bmi_reports.html',student_bmi_list=student_bmi_list)

@app.route("/studentBMIUnderWeightReports",methods=['POST','GET'])
def studentBMIUnderWeightReportsPage():
    student_weight_list=[]
    student_weight_dict={}
    count=0
    if request.method=='GET':
        get_students_bmi = StudentBmi.objects(status__in=[1])
        if get_students_bmi:
            for gsb in get_students_bmi:
                if gsb.bmiValue >= 18 and gsb.bmiValue <=25:
                    pass
                elif gsb.bmiValue < 18:
                    count=count+1
                    student_weight_dict={
                        "slNo":count,
                        "fullName":gsb.studentName,
                        "className":gsb.className,
                        "rollNumber":gsb.rollNumber,
                        "bmiValue":gsb.bmiValue,
                        "month":gsb.month,
                        "studentRefLink":gsb.studentRefLink
                    }
                    student_weight_list.append(student_weight_dict)
                elif gsb.bmiValue >25:
                    pass
                else:
                    flash("No Records")
        elif not get_students_bmi:
            # return"no data"
            pass
    return render_template('wellness/student/student_under_weight_bmi_reports.html',student_weight_list=student_weight_list)

@app.route("/addSpecialDiet/<studentRefLink>",methods=['POST','GET'])
def addStudentSpecialDiet(studentRefLink):
    specialFoodItem=request.form.get('specialFoodItem')
    specialFoodQuantity = request.form.get('specialFoodQuantity')
    givenOn=datetime.datetime.now()
    specialDietStatus = 1
    if request.method=='POST':
        try:
            student_bmi = StudentBmi.objects(studentRefLink__iexact=studentRefLink)
            if student_bmi:
                flash("Already Added Special Diet")
                return render_template("wellness/student/student_add_special_diet.html")
        except Exception as e:
            pass
        get_students_bmi_data=StudentBmi.objects.get(studentRefLink__in=[studentRefLink])
        if get_students_bmi_data:
            update_special_diet=get_students_bmi_data.update(
                specialFoodItem=specialFoodItem,
                specialFoodQuantity=specialFoodQuantity,
                givenOn=givenOn,
                specialDietStatus=specialDietStatus
                )
            if update_special_diet:
                flash("Special Diet Added")
                return redirect(url_for('studentBMIUnderWeightReportsPage'))
    return render_template('wellness/student/student_add_special_diet.html')


if __name__ == '__main__':
    # app.run(debug=True, port=4000)
    app.run(host='0.0.0.0',debug=True, port=4000)