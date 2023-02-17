import datetime

from django.urls import reverse
from django.utils import timezone
from django.test import TestCase
from polls.models import Question, Choice

# Create your tests here.

class QuestionModelTests(TestCase):

    def test_question_without_choices(self):
        """Is equal to 0 if the question has no choices"""

        no_choice_question = create_question("No choices", -1)
        self.assertEqual(no_choice_question.choice_set.count(), 0)

    def test_question_with_one_choice(self):
        """Is equal to 1 if the question has only one choice. This is a done decision then not a poll"""

        one_choice_question = create_question("One choice", -1)
        create_choice(one_choice_question)
        self.assertEqual(one_choice_question.choice_set.count(), 1)
        self.assertLess(one_choice_question.choice_set.count(), 2)

    def test_question_with_two_or_more_choices(self):
        """Is equal to  when the question has two or more choices. This is  proper poll"""

        two_choice_question = create_question_with_two_choices("Two choices", -1)
        create_choice(two_choice_question, "Choice 3")
        self.assertGreaterEqual(two_choice_question.choice_set.count(), 2)

    def test_was_published_recently_with_future_date(self): 
        """Returns False if a question was published recently with a future date"""

        time = timezone.now() + datetime.timedelta(days=30)
        future_question  = create_question_with_two_choices('Future Question', time.day)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """Returns false if a question was published one day past today"""

        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = create_question_with_two_choices('Past Question', time.day)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_new_question(self):
        """Returns true if a question was published recently within the past day"""
        time = timezone.now() - datetime.timedelta(hours=23, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """Creates a question within a given range for the days -ve for published or past questions and +ve for future or unpublished questions"""
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_question_with_two_choices(question_text, days):
    """Creates a question within a given range of days and with two choices"""
    time = timezone.now() + datetime.timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=time)
    create_choice(question, 'Choice 1')
    create_choice(question, 'Choice 2')
    return question


def create_choice(question, choice_text='Choice 1'):
    """Creates choices for a given question and question's text"""
    Choice.objects.create(question=question, choice_text=choice_text)


class QuestionIndexViewTests(TestCase):
    
    def test_no_questions(self):
        """When no questions are available. Display something appropriate"""

        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])


    def test_past_questions(self):
        """Returns the set of questions that have been recently published"""

        question = create_question_with_two_choices(question_text="Past Question", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])


    def test_future_questions(self):
        """Returns the set of questions that have yet to be published"""

        create_question_with_two_choices(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    
    def test_future_question_and_past_questions(self):
        """Returns only the past questions if both past and future questions exist"""

        question = create_question_with_two_choices(question_text="Past question", days=-30)
        create_question_with_two_choices(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])


    def test_two_past_questions(self):
        """Displays multiple questions"""
        question1 = create_question_with_two_choices(question_text="Past Question 1", days=-30)
        question2 = create_question_with_two_choices(question_text="Past Question 2", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question2, question1]) # cus the context returns desc order


class QuestionDetailTestView(TestCase):

    def test_future_question_detail(self):
        """Only shows tests that are in the past"""

        future_question = create_question(question_text="Future Question", days=5)
        response = self.client.get(reverse('polls:detail', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_past_question_detail(self):
        """Displays the text if its a question published in the past"""

        past_question = create_question_with_two_choices(question_text="Past Question", days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionResultsView(TestCase):

    def test_future_question_results(self):
        """Returns 404 error if the question had not been published"""
        future_question = create_question_with_two_choices('Future Question', 5)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_results(self):
        """Returns the question text if the question has been published"""
        past_question = create_question_with_two_choices('Past Question', 5)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)