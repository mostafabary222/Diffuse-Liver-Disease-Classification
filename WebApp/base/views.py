from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.exceptions import APIException
from django.db import transaction
from operator import truediv
from queue import Empty
import random
import string
from xmlrpc.client import boolean
from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import Patient
from .models import Doctor
from .models import Admin
from .models import Report
from django.contrib.auth.models import User
from django.contrib import messages
import pickle
import pandas as pd

def status(df):
    try:
        scaler=pickle.load(open("I:/_Marwan Documents/Grad/Django 2/WebApp/base/Scaler.sav", 'rb'))
        model=pickle.load(open("I:/_Marwan Documents/Grad/Django 2/WebApp//base/Prediction.sav", 'rb'))
        X = scaler.transform(df) 
        y_pred = model.predict(X) 
        y_pred=(y_pred>0.80) 
        result = "Yes" if y_pred else "No"
        return result 
    except ValueError as e: 
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST) 

def testform(request):
    if request.method == 'POST':
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        salary = request.POST.get('estimatedSalary')
        df=pd.DataFrame({'gender':[gender], 'age':[age], 'salary':[salary]})
        df["gender"] = 1 if "male" else 2
        result = status(df)
        request.session['result'] = result
        return render(request, 'testform.html', {"data": result}) 

    return render(request, 'testform.html')

def index(request):
    return render(request, 'index.html')
    
def addreport(request, name):
    if request.method == 'POST':
        if 'image' in request.POST:
            found = False
            patients = Patient.objects.all()
            image = request.POST.get('file')
            for patient in patients:
                if patient.patient_name == name:
                    q = patient
                    found = True
            if found:
                request.session['report'] = 'result'
            return render(request, 'addReport.html', {'patient' : q, 'image' : image})
            
        elif 'form' in request.Post:
            return redirect('patients')

        return redirect('patients') 

    found = False
    patients = Patient.objects.all()
    for patient in patients:
        if patient.patient_name == name:
            context = {'patient' : patient}
            found = True
    if found:
        return render(request, 'addReport.html', context) 
    else:
        return redirect('patients') 

def report(request, id):
    report = Report.objects.get(id = id)
    context = {'report' : report}
    return render(request, 'viewReport.html', context) 
           
def about(request):
    return render(request, 'about.html')

def profile(request):
    patient = Patient.objects.get(id = request.session['id'])
    reports = Report.objects.filter(patient_name = patient.patient_name)
    return render(request, 'profile.html', {'patient' : patient, 'reports' : reports})    

def patients(request):
    if 'role' in request.session:
        if request.session['role'] == 'doctor':
            if 'doctor_name' in request.session:
                patients = Patient.objects.filter(assigned_doctor='doctor 1')
                context = {'patients': patients}
                return render(request, 'patients.html', context) 
            else:
                return redirect('login')
        elif request.session['role'] == 'admin':
            patients = Patient.objects.all()
            context = {'patients': patients}
            return render(request, 'patients.html', context)

def doctors(request):
    doctors = Doctor.objects.all()
    context = {'doctors': doctors}
    return render(request, 'doctors.html', context)       
       
def patient(request, name):
    if request.method == 'POST':
        # if request.session['role'] == "admin":
        newpass = request.POST.get('pass')
        print(request.POST.get('pass'))
        Patient.objects.filter(id=request.session['current_patient']).update(password=newpass)
            # return redirect('patients')

    found = False
    arr = []
    patients = Patient.objects.all()
    reports = Report.objects.all()
    for patient in patients:
        if patient.patient_name == name:
            patientt = patient
            context1 = patient
            found = True
            request.session['current_patient'] = patient.id

    if found:
        for report in reports:
            if report.patient_name == patientt.patient_name:
                arr.append(report)
        # request.session['currentpatient'] = name               
        return render(request, 'viewPatient.html', {'patient':context1, 'reports':arr}) 
    else:
        return redirect('patients') 
       
def addpatient(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        birthdate = request.POST.get('birthdate')
        phoneno = request.POST.get('phoneno')
        doctor = Doctor.objects.get(id=request.session['id'])
        N = 5
        password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
        username = fullname.split()[0]

        query = Patient(patient_name=fullname, birth_date=birthdate, phone_num=phoneno, password=password, username=username, assigned_doctor=doctor.name)
        query.save()
        return redirect('patients')
    return render(request, 'addPatient.html')

def addoctor(request):
    if request.method == 'POST':
        name = request.POST.get('fullname')
        username = name.replace(" ", "")
        N = 6
        password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

        query = Doctor(name=name, username=username, password=password)
        query.save()
        return redirect('doctors')
    return render(request, 'addDoctor.html')    

def deletepatient(request, id):
    Patient.objects.filter(id=id).delete()

    return redirect('patients')

def deletedoctor(request, id):
    Doctor.objects.filter(id=id).delete()

    return redirect('doctors')    

def deletereport(request, id):
    Report.objects.filter(id=id).delete()

    return redirect('patients')    

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            patient = Patient.objects.get(username=username)
            if patient.password == password:
                request.session['role'] = 'patient'
                request.session['id'] = patient.id
                request.session['loggedin'] = True
                return redirect('index')
        except Patient.DoesNotExist:
            patient = None

        if patient == None:
            try:
                doctor = Doctor.objects.get(username=username)
                if doctor.password == password:
                    request.session['is_doctor'] = True
                    request.session['role'] = 'doctor'
                    request.session['id'] = doctor.id
                    request.session['loggedin'] = True
                    return redirect('index')
            except Doctor.DoesNotExist:
                doctor = None

        if doctor == None:
            try:
                admin = Admin.objects.get(username=username)
                if admin.password == password:
                    request.session['role'] = 'admin'
                    request.session['id'] = admin.id
                    request.session['loggedin'] = True
                    return redirect('index')
            except Admin.DoesNotExist:
                admin = None 

        if admin == None:
            return redirect('login')
    return render(request, 'login.html')    

def logout(request):
    try:
        del request.session['role']
        del request.session['loggedin']
        del request.session['id']
        del request.session['report']
    except KeyError:
        pass
    return redirect('login')

