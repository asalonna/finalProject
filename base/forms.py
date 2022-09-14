from django import forms
from django.forms import ModelForm
from .models import Questions

class CreateClassroomForm(forms.Form):
    name = forms.CharField(label='Enter a name for the classroom:', max_length=100)
    correct_questions_required = forms.IntegerField(label='Enter the minimum number of questions to be answered at each level:', min_value=1)
    passcode = forms.CharField(label='Enter a passcode for your classroom:')

class CreateQuestionForm(forms.Form):
    question_title = forms.CharField(label='Enter a name for the question:', max_length=100)
    question_body = forms.CharField(label='Enter your question:', max_length=500, widget=forms.Textarea)
    question_restrictions = forms.CharField(label='Optional: Enter the restrictions for your question:', max_length=500, widget=forms.Textarea, required=False)
    question_answer = forms.CharField(label='Enter the expected answer to your question:', max_length=500, widget=forms.Textarea)
    class_group = forms.CharField(label='Enter a class access code for your question:', max_length=50)
    question_difficulty = forms.IntegerField(label='Enter a difficulty for your question:', min_value=1)
    max_attempts = forms.IntegerField(label='Enter the maximum number of attempts to be allowed:', min_value=1)

class EditQuestionForm(ModelForm):
    class Meta:
        model=Questions
        exclude = ['class_id']

class UserAccessForm(forms.Form):
    user_id = forms.CharField(label='User ID:', max_length=10)
    classroom_access_code = forms.CharField(label='Classroom Access Code:', max_length=6)

QUESTION_CHOICES = []

class TrackGradeForm(forms.Form):
    classroom_access_code = forms.CharField(label='Classroom Access Code:', max_length=10)
    classroom_passcode = forms.CharField(label='Classroom Password:', max_length=10)

class TrackQuestionForm(forms.Form):
    question_list = forms.CharField(label="Select a question to view tracking info", widget=forms.Select(choices=QUESTION_CHOICES))

class ModifyForm(forms.Form):
    classroom_access_code = forms.CharField(label='Classroom Access Code:', max_length=10)
    classroom_passcode = forms.CharField(label='Classroom Password:', max_length=10)
