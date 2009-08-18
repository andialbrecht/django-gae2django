from django.db import models

from gaeapi.appengine.ext import db

class RegressionTestModel(db.Model):
    xstring = db.StringProperty()
    xlist = db.ListProperty(str)
