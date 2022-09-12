from django.db import models

# Create your models here.
class ClassRooms(models.Model):
    class_id = models.CharField(max_length=6, primary_key=True)
    name = models.CharField(max_length=100)
    passcode = models.CharField(max_length=10)

class Questions(models.Model):
    title = models.CharField(max_length=100)
    question_and_answer = models.CharField(max_length=1000)
    class_id = models.ForeignKey(ClassRooms, on_delete=models.CASCADE)
    difficulty = models.PositiveIntegerField()
    def __str__(self):
        return self.title

class ClassUsers(models.Model):
    class_id = models.ForeignKey(ClassRooms, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=10)
    highest_difficulty = models.PositiveIntegerField()
    last_question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    class_completed = models.BooleanField()
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['class_id', 'user_id'], name='constrain_classusers')
        ]
    def __str__(self):
        return ("User: " + self.user_id +  " Completed: " + str(self.class_completed)
                 + " Highest_Difficulty: " + str(self.highest_difficulty))

class UserMarks(models.Model):
    user_id = models.CharField(max_length=10)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    completed = models.BooleanField()
    attempts = models.IntegerField()
    def __str__(self):
        return ("User: " + self.user_id +  " Completed: " + str(self.completed)
                 + " Attempts: " + str(self.attempts))
