from django import forms

class CreateClassroomForm(forms.Form):
    name = forms.CharField(label='Enter a name for the classroom:', max_length=100)
    passcode = forms.CharField(label='Enter a passcode for your classroom:')

class CreateQuestionForm(forms.Form):
    question_title = forms.CharField(label='Enter a name for the question:', max_length=100)
    question_body = forms.CharField(label='Enter your question:', max_length=500)
    question_answer = forms.CharField(label='Enter the expected answer to your question:', max_length=500)
    class_group = forms.CharField(label='Enter a class name for your question:', max_length=50)
    question_difficulty = forms.IntegerField(label='Enter a difficulty for your question:', min_value=0)

class UserAccessForm(forms.Form):
    user_id = forms.CharField(label='User ID:', max_length=10)
    classroom_access_code = forms.CharField(label='Classroom Access Code:', max_length=6)

class TrackGradeForm(forms.Form):
    question_access_code = forms.CharField(label='Question Access Code:', max_length=10)
    question_passcode = forms.CharField(label='Question Password:', max_length=10)