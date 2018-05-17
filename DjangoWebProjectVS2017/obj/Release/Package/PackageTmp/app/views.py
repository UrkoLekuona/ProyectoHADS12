"""
Definition of views.
"""

from django.shortcuts import render,get_object_or_404
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from django.http.response import HttpResponse, Http404
from django.http import HttpResponseRedirect, HttpResponse
from .models import Question,Choice,User, QuestionQuiz, Answers
from django.template import loader
from django.core.urlresolvers import reverse
from app.forms import QuestionForm, ChoiceForm,UserForm, QuestionFormQuiz, AnswerForm
from django.shortcuts import redirect
import json
from django.contrib import messages
from django.db.models import Count

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Autor de la web',
            'message':'Datos de contacto',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )
def index(request):
     if request.method == "POST":
         selected_theme = request.POST['mythemes']
         if selected_theme == "":
             latest_question_list = QuestionQuiz.objects.order_by('-pub_date')
         else:
            latest_question_list = QuestionQuiz.objects.order_by('-pub_date').filter(question_theme=selected_theme)
         template = loader.get_template('polls/index.html')
         themes = QuestionQuiz.objects.values('question_theme').distinct()
         context = {
                'title':'Lista de preguntas de la encuesta',
                'latest_question_list': latest_question_list,
                'themes' : themes,
                'mytheme' : selected_theme,
                }
     else:
         latest_question_list = QuestionQuiz.objects.order_by('-pub_date')
         template = loader.get_template('polls/index.html')
         themes = QuestionQuiz.objects.values('question_theme').distinct()
    #distinct = QuestionQuiz.objects.values('question_theme').annotate(theme_count=Count('question_theme')).filter(theme_count=1)
    #themes = QuestionQuiz.objects.filter(question_theme__in=[item['question_theme'] for item in distinct])
    #themes = [obj.question_theme for obj in latest_question_list]
    #themes = QuestionQuiz.objects.order_by('-pub_date').values('question_theme').distinct('question_theme')
         context = {
                'title':'Lista de preguntas de la encuesta',
                'latest_question_list': latest_question_list,
                'themes' : themes,
                }
    
     return render(request, 'polls/index.html', context)

def detail(request, question_id):
     question = get_object_or_404(QuestionQuiz, pk=question_id)
     return render(request, 'polls/detail.html', {'title':'Respuestas asociadas a la pregunta:','question': question})

def results(request, question_id, answer):
    question = get_object_or_404(QuestionQuiz, pk=question_id)
    a = get_object_or_404(Answers, pk=answer)
    if a.correct == True :
        resultado = 'Has contestado ' + a.answer +' y has acertado!'
    else:
        resultado = 'Has contestado ' + a.answer +' y has fallado.'
    return render(request, 'polls/results.html', {'title':'Resultados de la pregunta:','question': question, 'resultado': resultado, 'bool': a.correct,})

def vote(request, question_id):
    p = get_object_or_404(QuestionQuiz, pk=question_id)
    try:
        selected_choice = p.answers_set.get(pk=request.POST['choice'])
    except (KeyError, Answers.DoesNotExist):
        # Vuelve a mostrar el form.
        return render(request, 'polls/detail.html', {
            'question': p,
            'error_message': "ERROR: No se ha seleccionado una opcion",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Siempre devolver un HttpResponseRedirect despues de procesar
        # exitosamente el POST de un form. Esto evita que los datos se
        # puedan postear dos veces si el usuario vuelve atras en su browser.
        return HttpResponseRedirect(reverse('results', args=(p.id, selected_choice.id,)))

def question_new(request):
        if request.method == "POST":
            form = QuestionFormQuiz(request.POST)
            if form.is_valid():
                question = form.save(commit=False)
                question.pub_date=datetime.now()
                question.save()
                #return redirect('detail', pk=question_id)
                #return render(request, 'polls/index.html', {'title':'Respuestas posibles','question': question})
        else:
            form = QuestionFormQuiz()
        return render(request, 'polls/question_new.html', {'form': form})

def choice_add(request, question_id):
        question = QuestionQuiz.objects.get(id = question_id)
        if request.method =='POST':
            form = AnswerForm(request.POST)
            if form.is_valid():
                if question.answers_set.count() < 4:
                    choice = form.save(commit = False)
                    choice.question = question
                    choice.vote = 0
                    choice.save()         
                    #form.save()
                else:
                   #messages.info(request, 'Esta pregunta ya tiene 4 respuestas.')
                   return render(request, 'polls/detail.html', {'title':'Respuestas asociadas a la pregunta:','question': question, 'max_answ':'Esta pregunta ya tiene 4 respuestas.',})
        else: 
            form = AnswerForm()
        #return render_to_response ('choice_new.html', {'form': form, 'poll_id': poll_id,}, context_instance = RequestContext(request),)
        return render(request, 'polls/choice_new.html', {'title':'Pregunta:'+ question.question_text,'form': form, 'ans_count': question.answers_set.count(),})

def chart(request, question_id):
    q=QuestionQuiz.objects.get(id = question_id)
    qs = Answers.objects.filter(question=q)
    dates = [obj.answer for obj in qs]
    counts = [obj.votes for obj in qs]
    context = {
        'dates': json.dumps(dates),
        'counts': json.dumps(counts),
    }

    return render(request, 'polls/grafico.html', context)

def user_new(request):
        if request.method == "POST":
            form = UserForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.save()
                #return redirect('detail', pk=question_id)
                #return render(request, 'polls/index.html', {'title':'Respuestas posibles','question': question})
        else:
            form = UserForm()
        return render(request, 'polls/user_new.html', {'form': form})

def users_detail(request):
    latest_user_list = User.objects.order_by('email')
    template = loader.get_template('polls/users.html')
    context = {
                'title':'Lista de usuarios',
                'latest_user_list': latest_user_list,
              }
    return render(request, 'polls/users.html', context)