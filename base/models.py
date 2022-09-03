from django.db import models

# Create your models here.
class Questions(models.Model):
    title = models.CharField(max_length=100)
    question_and_answer = models.CharField(max_length=1000)
    passcode = models.CharField(max_length=10)

    def __str__(self):
        return self.title

class UserMarks(models.Model):
    user_id = models.CharField(max_length=10)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    completed = models.BooleanField()
    attempts = models.IntegerField()
    
    def __str__(self):
        return ("User: " + self.user_id + " Question: " + self.question + 
                " Completed: " + self.completed + " Attempts:" + self.attempts)
