import questionMod
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.db.models import Avg
from .forms import CreateQuestionForm, TrackGradeForm, UserAccessForm
from .models import Questions, UserMarks
import requests 
from random import randint

# Create your views here.

def index(request):
    template = loader.get_template('base/index.html')
    return render(request, 'base/index.html')

def access(request):
    #template = loader.get_template('base/join.html')
    #return render(request, 'base/join.html')
    if request.method == 'POST': 
        form = UserAccessForm(request.POST)
        if form.is_valid():
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
    question = questionMod.getQuestionObjectString(dsl, 20)
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
            "clientSecret": "e018f4f1a3557224977c2ff6d30d3dcec9402f342c4c9587a6f2f9ebba6cc800",
        }

        response = requests.post(api_url, json=send)
        answer = question.answerText
        
        userMark = UserMarks.objects.get(question=pk, user_id=request.session['user_id'])
        userMark.attempts += 1
        feedback = ""
        next_question_id = -1
        if str(response.json()['output']).rstrip() == answer: # might need to allow tailing whitespace?
            userMark.completed = True
            feedback = "Congratulations, your submission matches the expected answer"
            if userMark.attempts <= 5:
                next_difficulty = question_object.difficulty + 1
                possible_questions = Questions.objects.filter(
                    difficulty=next_difficulty, 
                    class_group=question_object.class_group
                )
                if possible_questions.exists():
                    random_question = randint(0, len(possible_questions)-1)
                    possible_questions_list = list(possible_questions)
                    next_question = possible_questions_list[random_question]
                    next_question_id = next_question.id
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
            'next_pk':next_question_id,
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

def next_question(request, pk):
    return HttpResponseRedirect('/task/' + str(pk))

def create_question(request):
    if request.method == 'POST': 
        form = CreateQuestionForm(request.POST)
        if form.is_valid():
            if questionMod.verify(form.cleaned_data['question_body'] + form.cleaned_data['question_answer']):
                question = Questions(
                    title = form.cleaned_data['question_title'], 
                    question_and_answer = form.cleaned_data['question_body'] + form.cleaned_data['question_answer'],
                    passcode = form.cleaned_data['question_passcode'],
                    difficulty = form.cleaned_data['question_difficulty'],
                    class_group = form.cleaned_data['class_group'],
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

def track(request):
    if request.method == 'POST': 
        form = TrackGradeForm(request.POST)
        if form.is_valid():
            question_object = Questions.objects.filter(id=form.cleaned_data['question_access_code'], passcode=form.cleaned_data['question_passcode'])
            if question_object.exists():
                user_record = UserMarks.objects.filter(question=form.cleaned_data['question_access_code'])
                context = {
                    'user_record' : user_record,
                    'student_count' : user_record.count(),
                    'correct_count' : user_record.filter(completed = True).count(),
                    'average_attempts' : user_record.aggregate(Avg('attempts'))['attempts__avg'],
                    'form' : form,
                }
                return render(request, 'base/tracking.html', context)
            else:
                context = {
                    'form' : form,
                }
                return render(request, 'base/tracking.html', context)
    else:
        form = TrackGradeForm()
        context = {
            'form': form,
        }
    return render(request, 'base/tracking.html', context)