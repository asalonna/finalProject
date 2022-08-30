import questionMod
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import CreateQuestionForm
from .models import Questions
import requests

# Create your views here.

def index(request):
    template = loader.get_template('base/index.html')
    return render(request, 'base/index.html')

def task(request, pk):
    # print(pk)
    template = loader.get_template('base/task.html')
    question_title = Questions.objects.get(id=pk).title
    dsl = Questions.objects.get(id=pk).question_and_answer
    question = questionMod.getQuestionObjectString(dsl, 69420)
    if request.method == 'POST':
        code = request.POST.get('codemirror-textarea')
        api_url = "https://api.jdoodle.com/execute"
        send = {
            "script" : code,
            "language": "java",
            "versionIndex": "4",
            "clientId": "91d1751130192e001a980050a26e4a2",
            "clientSecret": "e018f4f1a3557224977c2ff6d30d3dcec9402f342c4c9587a6f2f9ebba6cc800"
        }

        response = requests.post(api_url, json=send)
        answer = question.answerText
        
        feedback = ""
        if str(response.json()['output']).rstrip() == answer: # might need to allow tailing whitespace?
            feedback = "Congratulations, your submission matches the expected answer"   
        else:
            feedback = "Your submission does not match the expected answer, please try again"
        


        context = {
            'content':code,
            'question_title':question_title,
            'compiler_output': response.json()['output'],
            'question':question,
            'feedback':feedback,
            'pk':pk,
        }
        return HttpResponse(template.render(context, request))

    else:
        default = """public class HelloWorld {
    public static void main(String[] args) {
        
    }
}
"""
        context = {
            'content':default,
            'question_title':question_title,
            'question':question.questionText,
            'pk':pk,
        }
        return HttpResponse(template.render(context, request))

def create_question(request):
    if request.method == 'POST': 
        form = CreateQuestionForm(request.POST)
        if form.is_valid():
            # print(form.cleaned_data['question_title'])
            # print(form.cleaned_data['question_body'])
            # print(form.cleaned_data['question_answer'])
            # print(form.cleaned_data['question_passcode'])
            if questionMod.verify(form.cleaned_data['question_body'] + form.cleaned_data['question_answer']):
                question = Questions(
                    title = form.cleaned_data['question_title'], 
                    question_and_answer = form.cleaned_data['question_body'] + form.cleaned_data['question_answer'],
                    passcode = form.cleaned_data['question_passcode'],
                )
                question.save()
                # print(question.id)
                return render(request, 'base/createTask.html', {'form': form, 'access_code' : question.id})
            else:
                context = {
                    'form': form,
                    'error_message': "ERROR!",
                }
                return render(request, 'base/createTask.html', context)
    else:
        form = CreateQuestionForm()
    return render(request, 'base/createTask.html', {'form': form})
