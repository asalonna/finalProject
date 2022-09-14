from distutils.log import error
from multiprocessing import pool
import questionMod
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.db.models import Avg
from .forms import CreateQuestionForm, TrackGradeForm, UserAccessForm, CreateClassroomForm, ModifyForm, EditQuestionForm
from .models import ClassUsers, Questions, UserMarks, ClassRooms
import requests, string
from random import randint, choices

# required functions
def id_check(request):
    try:
        request.session['user_id']
    except KeyError:
        return False
    else:
        return True

# Create your views here.

def index(request):
    template = loader.get_template('base/index.html')
    return render(request, 'base/index.html')

def dsl_guide(request):
    return render(request, 'base/dsl_guide.html')

# where students access the questions
def access(request):
    if request.method == 'POST': 
        form = UserAccessForm(request.POST)
        if form.is_valid():
            possible_questions = Questions.objects.filter(class_id=form.cleaned_data['classroom_access_code'], difficulty=1)
            
            if possible_questions.exists():
                request.session['user_id'] = form.cleaned_data['user_id']
                random_question = randint(0, len(possible_questions)-1)
                possible_questions_list = list(possible_questions)
                next_question = possible_questions_list[random_question]
                next_question_id = next_question.id

                # adds user to class if not already in class
                if not ClassUsers.objects.filter(class_id=form.cleaned_data['classroom_access_code'], user_id=request.session['user_id']).exists():
                    class_user = ClassUsers(
                        class_id = ClassRooms.objects.get(class_id=form.cleaned_data['classroom_access_code']),
                        user_id = form.cleaned_data['user_id'],
                        completed_questions_per_level = 0,
                        highest_difficulty = 0,
                        last_question = next_question,
                        class_completed = False,
                    )
                    class_user.save()

                return HttpResponseRedirect('/task/' + str(next_question_id))
                # possible_questions = Questions.objects.filter(
                # difficulty=next_difficulty, 
                # class_group=question_object.class_group
                # )
                    
                # if possible_questions.exists():
                #     random_question = randint(0, len(possible_questions)-1)
                #     possible_questions_list = list(possible_questions)
                #     next_question = possible_questions_list[random_question]
                #     next_question_id = next_question.id
                # else:
                #     next_question_id = "-1"
            else:
                return render(request, 'base/join.html', {'form': form})
    else:
        form = UserAccessForm()
    return render(request, 'base/join.html', {'form': form})

# fetches and shows questions, compiles code, and marks answer
def task(request, pk):
    if id_check(request) == False:
        raise Http404("You do not have permission to access this page")
    
    template = loader.get_template('base/task.html')
    question_object = Questions.objects.get(id=pk)
    question_title = question_object.title
    dsl = question_object.question_and_answer
    
    userMark = None
    if not UserMarks.objects.filter(question=pk, user_id=request.session['user_id']).exists():
        userMark = UserMarks(
            user_id = request.session['user_id'],
            question = question_object,
            completed = False,
            attempts = 0,
        )
        userMark.save()
    else:
        userMark = UserMarks.objects.get(question=pk, user_id=request.session['user_id'])

    class_user = ClassUsers.objects.get(user_id=request.session['user_id'], class_id=question_object.class_id)

    seed = request.session['user_id'] + str(question_object.id) + str(class_user.completed_questions_per_level)
    question = questionMod.getQuestionObjectString(dsl, seed)

    if request.method == 'POST':

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
        
        userMark.attempts += 1
        
        feedback = ""
        next_question_id = -1

        #TODO: Make more forgiving? DSL function might already exist?
        if str(response.json()['output']).rstrip() == answer and question.checkCode(code):
            userMark.completed = True
            class_user.completed_questions_per_level += 1

            if class_user.highest_difficulty < question_object.difficulty:
                class_user.highest_difficulty = question_object.difficulty
            
            class_user.last_question = question_object

            feedback = "Congratulations, your submission matches the expected answer"
            
            # need to store a count of questions answered of each level
            # then compare that to required number
            classroom_object = question_object.class_id
            if userMark.attempts <= question_object.max_attempts and class_user.completed_questions_per_level >= classroom_object.correct_questions_required:
                next_difficulty = question_object.difficulty + 1
                class_user.completed_questions_per_level = 0
            elif userMark.attempts >= question_object.max_attempts * 2:
                if question_object.difficulty > 1:
                    next_difficulty = question_object.difficulty - 1
                    class_user.completed_questions_per_level = 0
                else:
                    next_difficulty = 1
            else:
                next_difficulty = question_object.difficulty
            
            possible_questions = Questions.objects.filter(
                difficulty=next_difficulty, 
                class_id=question_object.class_id
            )
                
            if possible_questions.exists():
                random_question = randint(0, len(possible_questions)-1)
                possible_questions_list = list(possible_questions)
                next_question = possible_questions_list[random_question]
                next_question_id = next_question.id
            else:
                next_question_id = "-1"
                class_user.class_completed = True
                  
        else:
            feedback = "Your submission does not match the expected answer, please try again"
        
        class_user.save()
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
        userMark.attempts = 0
        userMark.save()
        context = {
            'content':default,
            'question_title':question_title,
            'question':question.questionText,
            'pk':pk,
        }
        return HttpResponse(template.render(context, request))

# redirects to next question
def next_question(request, pk):
    if id_check(request) == False:
        raise Http404("You do not have permission to access this page")
    if pk == "-1":
        return HttpResponseRedirect('/end_screen')
    return HttpResponseRedirect('/task/' + str(pk))


def end_of_questions(request):
    if id_check(request) == False:
        raise Http404("You do not have permission to access this page")
    request.session.pop('user_id')
    return render(request, 'base/end_screen.html')

# creates and stores classrooms
def create_classroom(request):
    if request.method == 'POST': 
        form = CreateClassroomForm(request.POST)
        if form.is_valid():
            # generate class_id
            class_id = ''.join(choices(string.ascii_uppercase + string.digits, k=6))
            while ClassRooms.objects.filter(class_id=class_id).exists():
                class_id = ''.join(choices(string.ascii_uppercase + string.digits, k=6))
            # add classroom to ClassRooms
            classroom = ClassRooms(
                class_id = class_id,
                name = form.cleaned_data['name'],
                correct_questions_required = form.cleaned_data['correct_questions_required'],
                passcode = form.cleaned_data['passcode'],
            )
            classroom.save()
            return render(request, 'base/createClassroom.html', {'form':form, 'class_id':classroom.class_id})
    else:
        form = CreateClassroomForm()
    return render(request, 'base/createClassroom.html', {'form': form})

# creates and stores questions
def create_question(request):
    if request.method == 'POST': 
        form = CreateQuestionForm(request.POST)
        if form.is_valid():
            if questionMod.verify(form.cleaned_data['question_body'] + form.cleaned_data['question_restrictions'] + form.cleaned_data['question_answer']):
                question = Questions(
                    title = form.cleaned_data['question_title'], 
                    question_and_answer = form.cleaned_data['question_body'] + form.cleaned_data['question_restrictions'] + form.cleaned_data['question_answer'],
                    difficulty = form.cleaned_data['question_difficulty'],
                    max_attempts = form.cleaned_data['max_attempts'],
                    class_id = ClassRooms.objects.get(class_id=form.cleaned_data['class_group']),
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

# allows teachers to see data for the questions and the grades
# def track(request):
#     if request.method == 'POST': 
#         form = TrackGradeForm(request.POST)
#         if form.is_valid():
#             question_object = Questions.objects.filter(id=form.cleaned_data['question_access_code'], passcode=form.cleaned_data['question_passcode'])
#             if question_object.exists():
#                 user_record = UserMarks.objects.filter(question=form.cleaned_data['question_access_code'])
#                 context = {
#                     'user_record' : user_record,
#                     'student_count' : user_record.count(),
#                     'correct_count' : user_record.filter(completed = True).count(),
#                     'average_attempts' : user_record.aggregate(Avg('attempts'))['attempts__avg'],
#                     'form' : form,
#                 }
#                 return render(request, 'base/tracking.html', context)
#             else:
#                 context = {
#                     'form' : form,
#                 }
#                 return render(request, 'base/tracking.html', context)
#     else:
#         form = TrackGradeForm()
#         context = {
#             'form': form,
#         }
#     return render(request, 'base/tracking.html', context)


def track(request):
    
    if request.method == 'POST': 
        form = TrackGradeForm(request.POST)
        if form.is_valid():
            if request.POST.get("class_button"):
                classroom_object = ClassRooms.objects.filter(class_id=form.cleaned_data['classroom_access_code'], passcode=form.cleaned_data['classroom_passcode'])
                if classroom_object.exists():
                    class_users_record = ClassUsers.objects.filter(class_id=form.cleaned_data['classroom_access_code'])
                    context = {
                        'class_users_record' : class_users_record,
                        'student_count' : class_users_record.count(),
                        'completed_count' : class_users_record.filter(class_completed = True).count(),
                        'highest_difficulty' : class_users_record.aggregate(Avg('highest_difficulty'))['highest_difficulty__avg'],
                    }
                    return render(request, 'base/tracking.html', context)
           
            elif request.POST.get("question_button"):
                question_object = Questions.objects.filter(class_id = ClassRooms.objects.get(class_id=form.cleaned_data['classroom_access_code']))
               
                if question_object.exists():
                    #user_record = UserMarks.objects.filter(question=form.cleaned_data['question_access_code'])
                    context = {
                        # 'user_record' : user_record,
                        # 'student_count' : user_record.count(),
                        # 'correct_count' : user_record.filter(completed = True).count(),
                        # 'average_attempts' : user_record.aggregate(Avg('attempts'))['attempts__avg'],
                        'form' : form,
                        'questions': question_object,
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

def modify(request):
    if request.method == 'POST': 
        form = ModifyForm(request.POST)
        if form.is_valid():
            classroom_object = ClassRooms.objects.filter(class_id=form.cleaned_data['classroom_access_code'], passcode=form.cleaned_data['classroom_passcode'])
            if classroom_object.exists():
                classroom_object = ClassRooms.objects.get(class_id=form.cleaned_data['classroom_access_code'], passcode=form.cleaned_data['classroom_passcode'])
                questions = Questions.objects.filter(class_id = classroom_object)
                context = {
                    'questions' : questions,
                    'form' : form,
                }
                return render(request, 'base/modify.html', context)
            else:
                context = {
                    'form' : form,
                }
                return render(request, 'base/modify.html', context)
    else:
        form = ModifyForm()
        context = {
            'form': form,
        }
    return render(request, 'base/modify.html', context)

def delete(request, pk):
    question = Questions.objects.get(id=pk)
    if request.method == 'POST':
        question.delete()
        return redirect('modify')
    return render(request, 'base/delete.html')

def edit(request, pk):
    question = Questions.objects.get(id=pk)
    form = EditQuestionForm(instance=question)
    if request.method == 'POST':
        form = EditQuestionForm(request.POST, instance=question)
        if form.is_valid():
            if questionMod.verify(form.cleaned_data['question_and_answer']):
                form.save()
                return redirect('modify')
            else:
                error_message = "The DSL syntax is incorrect"
                context = {
                    'error_message' : error_message,
                    'form' : form,
                }
                return render(request, 'base/edit.html', context) 
    context = {
        'form' : form,
    }
    return render(request, 'base/edit.html', context)