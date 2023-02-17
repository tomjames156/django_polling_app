from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.urls import reverse
from django.db.models import F, FilteredRelation, Q
from django.views import generic
from django.utils import timezone
from .models import Question, Choice

# Create your views here.

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        # Returns the last 5 posted polls
        questions = Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')
        questions = [question for question in questions if question.choice_set.count() > 1][:5]
        return questions


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        questions = Question.objects.filter(pub_date__lte=timezone.now())
        return questions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context['question'].choice_set.count() >= 2:
            return context

class ResultsView(generic.DetailView):
    template_name = 'polls/results.html'
    model = Question

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **args):
        context = super().get_context_data(**args)
        if context['question'].choice_set.count() >= 2:
            choices = context['question'].choice_set.all()
            context['total'] = sum(choice.votes for choice in choices)
            context['choices'] = choices
            return context
        else:
            return []



def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'You did not select a choice'
        })
    else:
        selected_choice.votes = F('votes') + 1
        selected_choice.save()

        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

def about(request):
    return render(request, 'polls/about.html')