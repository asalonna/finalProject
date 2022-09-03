from django import forms

class CreateQuestionForm(forms.Form):
    question_title = forms.CharField(label='Enter a name for the question:', max_length=100)
    question_body = forms.CharField(label='Enter your question:', max_length=500)
    question_answer = forms.CharField(label='Enter the expected answer to your question:', max_length=500)
    question_passcode = forms.CharField(label='Enter a passcode for your question:', max_length=10)

class UserAccessForm(forms.Form):
    user_id = forms.CharField(label='User ID:', max_length=10)
    question_access_code = forms.CharField(label='Question Access Code:', max_length=10)