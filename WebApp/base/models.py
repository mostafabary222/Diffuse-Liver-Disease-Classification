from time import strftime
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from datetime import datetime
from django import forms

# Create your models here.

class Doctor(models.Model):
    name = models.CharField(max_length = 200)
    username = models.CharField(max_length = 200)
    password = models.CharField(max_length = 200, null=True)
    assigned_patients = models.TextField(null = True, blank = True)
    role = models.CharField(max_length=200, default="doctor")

    def __str__(self):
        return self.name

class Admin(models.Model):
    name = models.CharField(max_length = 200)
    username = models.CharField(max_length = 200)
    password = models.CharField(max_length = 200, null=True)
    role = models.CharField(max_length=200, default="admin")

    def __str__(self):
        return self.name

class Patient(models.Model):
    patient_name = models.CharField(max_length = 200)
    username = models.CharField(max_length = 200)
    password = models.CharField(max_length = 200, null=True)
    phone_num = models.CharField(max_length = 13)
    birth_date = models.DateField()
 
    assigned_doctor = models.CharField(max_length = 201)
    check_in_date = models.DateField(auto_now_add = True)
    role = models.CharField(max_length=200, default="patient")

    def __str__(self):
        return self.patient_name

class Report(models.Model):
    patient_name = models.CharField(max_length = 200)
    pathologist = models.CharField(max_length = 200)
    notes = models.TextField(null = True, blank = True)
    image = models.ImageField(upload_to='static/images/scans/', height_field=None, width_field=None, max_length=None)
    date = models.DateField(auto_now_add = True)
    classification = models.TextField(null = True, blank = True)

    def __str__(self):
        return self.patient_name             

class Model(models.Model):
    image = models.ImageField
    
    def __str__(self):
        return self.image             

