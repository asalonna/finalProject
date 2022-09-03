import questionMod
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import CreateQuestionForm, UserAccessForm
from .models import Questions, UserMarks
import requests 

# Create your views here.

def index(request):
    template = loader.get_template('base/index.html')
    return render(request, 'base/index.html')

def access(request):
    #template = loader.get_template('base/join.html')
    #return render(request, 'base/join.html')
    #return HttpResponse(template.render(request))
    if request.method == 'POST': 
        form = UserAccessForm(request.POST)
        if form.is_valid():
            #if questionMod.verify(form.cleaned_data['question_body'] + form.cleaned_data['question_answer']): # change to verify access code
            #    return render(request, 'base/createTask.html', {'form': form, 'access_code' : question.id})
            #else:
            #    context = {
            #    }
            #    return render(request, 'base/join.html', context)
            if Questions.objects.filter(id=form.cleaned_data['question_access_code']).exists():
                request.session['user_id'] = form.cleaned_data['user_id']
                return HttpResponseRedirect('/task/' + form.cleaned_data['question_access_code'])
            else:
                return render(request, 'base/join.html', {'form': form})
    else:
        form = UserAccessForm()
    return render(request, 'base/join.html', {'form': form})

def task(request, pk):
    template = loader.get_template('base/task.html')
    question_object = Questions.objects.get(id=pk)
    question_title = question_object.title
    dsl = question_object.question_and_answer
    question = questionMod.getQuestionObjectString(dsl, 69420)
    if request.method == 'POST':
        if not UserMarks.objects.filter(question=pk, user_id=request.session['user_id']).exists():
            usermark = UserMarks(
                user_id = request.session['user_id'],
                question = question_object,
                completed = False,
                attempts = 0,
            )
            usermark.save()
        
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
        
        userMark = UserMarks.objects.get(question=pk, user_id=request.session['user_id'])
        userMark.attempts += 1
        feedback = ""
        if str(response.json()['output']).rstrip() == answer: # might need to allow tailing whitespace?
            userMark.completed = True
            feedback = "Congratulations, your submission matches the expected answer"   
        else:
            feedback = "Your submission does not match the expected answer, please try again"
        userMark.save()
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
            if questionMod.verify(form.cleaned_data['question_body'] + form.cleaned_data['question_answer']):
                question = Questions(
                    title = form.cleaned_data['question_title'], 
                    question_and_answer = form.cleaned_data['question_body'] + form.cleaned_data['question_answer'],
                    passcode = form.cleaned_data['question_passcode'],
                )
                question.save()
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
