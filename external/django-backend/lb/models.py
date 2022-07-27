from django.db import models

import datetime as dt

def get_time():
    return (dt.datetime.now()).timestamp()

class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    votes = models.BigIntegerField(default=0)

class Submission(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar = models.TextField(null=True)
    time = models.FloatField(default=get_time)
    score = models.IntegerField(null=False)
    subs = models.CharField(max_length=255)

    class Meta:
        unique_together = ["user", "time"]