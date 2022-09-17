from django.test import TestCase, Client

from base.models import *

# testing views
class IndexTestCase(TestCase):

    def test_url_exists(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

class DSLGuideTestCase(TestCase):

    def test_url_exists(self):
        response = self.client.get('/dsl_guide')
        self.assertEqual(response.status_code, 200)

class AccessTestCase(TestCase):

    def setUp(self):
        ClassRooms.objects.create(
            class_id = 'aaaaaa',
            name = 'tests_classroom',
            correct_questions_required = 1,
            passcode = 123,
        )
        Questions.objects.create(
            title = 'test_question',
            question_and_answer = 'Question <"Test"> Answer <"Test">',
            class_id = ClassRooms.objects.get(class_id='aaaaaa'),
            difficulty = 1,
            max_attempts = 5,
        )

    def test_url_exists(self):
        response = self.client.get('/access')
        self.assertEqual(response.status_code, 200)

    def test_submit_form(self):
        c = Client()
        response = c.post('/access', {'user_id': 'test_user', 'classroom_access_code': 'aaaaaa'})
        # check question shown (check URL)
        self.assertTrue(ClassUsers.objects.filter(class_id='aaaaaa', user_id='test_user').exists())

class TaskTestCase(TestCase):

    def setUp(self):
        ClassRooms.objects.create(
            class_id = 'aaaaaa',
            name = 'tests_classroom',
            correct_questions_required = 1,
            passcode = 123,
        )
        Questions.objects.create(
            title = 'test_question',
            question_and_answer = 'Question <"Test"> Answer <"Test">',
            class_id = ClassRooms.objects.get(class_id='aaaaaa'),
            difficulty = 1,
            max_attempts = 5,
        )
        ClassUsers.objects.create(
            class_id = ClassRooms.objects.get(class_id='aaaaaa'),
            user_id = 'test_user',
            completed_questions_per_level = 0,
            highest_difficulty = 0,
            last_question = Questions.objects.get(id=1),
            class_completed = False,
        )
    
    def test_url_exists_with_user_id(self):
        c = Client()
        s = c.session
        s.update({
            'user_id': 'test_user',
        })
        s.save()
        response = c.get('/task/1')
        self.assertEqual(response.status_code, 200)

    def test_url_exists_without_user_id(self):
        c = Client()
        response = c.get('/task/1')
        self.assertEqual(response.status_code, 404)

    def test_correct_answer(self):
        c = Client()
        response = c.post('/task/1', {'codemirror-textarea': 
                                                """ public class HelloWorld {
                                                        public static void main(String[] args) {
                                                            System.out.println("Test");
                                                        }
                                                    }"""})
        correct = UserMarks.objects.filter(user_id='test_user', question=Questions.objects.get(id=1)).exists()
        #self.assertTrue(correct)
        1

class NextQuestionTestCase(TestCase):

    def setUp(self):
        ClassRooms.objects.create(
            class_id = 'aaaaaa',
            name = 'tests_classroom',
            correct_questions_required = 1,
            passcode = 123,
        )
        Questions.objects.create(
            title = 'test_question',
            question_and_answer = 'Question <"Test"> Answer <"Test">',
            class_id = ClassRooms.objects.get(class_id='aaaaaa'),
            difficulty = 1,
            max_attempts = 5,
        )
    
    def test_url_exists_with_user_id(self):
        c = Client()
        s = c.session
        s.update({
            'user_id': 'test_user',
        })
        s.save()
        response = c.get('/next/1')
        self.assertEqual(response.status_code, 302)

    def test_url_exists_without_user_id(self):
        c = Client()
        response = c.get('/next/1')
        self.assertEqual(response.status_code, 404)
    
class EndOfQuestionsTestCase(TestCase):
    
    def test_url_exists_with_user_id(self):
        c = Client()
        s = c.session
        s.update({
            'user_id': 'test_user',
        })
        s.save()
        response = c.get('/end_screen')
        self.assertEqual(response.status_code, 200)

    def test_url_exists_without_user_id(self):
        c = Client()
        response = c.get('/end_screen')
        self.assertEqual(response.status_code, 404)

class CreateClassroomTestCase(TestCase):
    
    def test_url_exists(self):
        response = self.client.get('/create_classroom')
        self.assertEqual(response.status_code, 200)

    def test_create_classroom(self):
        c = Client()
        response = c.post('/create_classroom', {
            'name' : 'test_classroom',
            'correct_questions_required' : 1,
            'passcode' : 123,
        })
        self.assertTrue(ClassRooms.objects.filter(name='test_classroom').exists())

class CreateQuestionTestCase(TestCase):

    def setUp(self):
        ClassRooms.objects.create(
            class_id = 'aaaaaa',
            name = 'tests_classroom',
            correct_questions_required = 1,
            passcode = 123,
        )
    
    def test_url_exists(self):
        response = self.client.get('/create_question')
        self.assertEqual(response.status_code, 200)

    def test_create_question(self):
        c = Client()
        response = c.post('/create_question', {
            'question_title' : 'test_question',
            'question_body' : 'Question <"Test">',
            'question_restrictions' : '',
            'question_answer' : 'Answer <"Test">',
            'class_group' : 'aaaaaa',
            'question_difficulty' : 1,
            'max_attempts' : 5,
        })
        self.assertTrue(Questions.objects.filter(class_id=ClassRooms.objects.get(class_id='aaaaaa')).exists())

class TrackTestCase(TestCase):

    def setUp(self):
        1

class ModifyTestCase(TestCase):

    def setUp(self):
        1

class DeleteTestCase(TestCase):

    def setUp(self):
        1

class EditTestCase(TestCase):

    def setUp(self):
        1

# testing models


# testing forms
