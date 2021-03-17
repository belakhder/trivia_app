import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category,db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://postgres:71932446@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

         #binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            #create all tables
            self.db.create_all()
        
            self.new_question={
             'question':"What name does the boat with Théodore Géricault paint the raft?",
             'answer':"A jellyfish",
             'category':"3",
             'difficulty':"5"
             }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
     """
    def test_get_questions(self):
         """test the display of questions as pages """
         #get response
         res=self.client().get('/questions')
         #load data
         data=json.loads(res.data)
         
        
         #check status code and message
         self.assertEqual(res.status_code,200)
         self.assertEqual(data['success'],True)
         #check questions an categories return data 
         self.assertTrue(data['questions'])
         self.assertTrue(data['categories'])
        
    def test_nb_questions_per_page(self):
        """test the number of questions set for a page"""
        #get response
        res=self.client().get('/questions?page=1')
        data=json.loads(res.data)
        
        
        self.assertEqual(data['success'],True)
        self.assertEqual(len(data['questions']),10)

    def test_404_pagination_questions(self):
        """ test for questions pagination failure """
        #get response
        res=self.client().get('/questions?page=100000')
        #load data
        data=json.loads(res.data)

        self.assertEqual(data['success'],False) 
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        """test the deletion of a question from database"""
         #creation of the question to be deleted
        question = Question(question=self.new_question['question'], answer=self.new_question['answer'],
                            category=self.new_question['category'], difficulty=self.new_question['difficulty'])
        question.insert()
        id=question.id

         #get response after deletion
        res=self.client().delete('/questions/{}'.format(id))
        data=json.loads(res.data)

        #search for question after deletion
        question=db.session.query(Question).filter(Question.id==id).one_or_none()

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted_id'],id)
        self.assertTrue(data['questions'])
        self.assertTrue(data['number_questions'])
        #test if the question is still in the database
        self.assertEqual(question,None)
    
    
    def test_422_delete_non_existing_question(self):
        """ test deletion failure """

         #creation of a question recover its id and delete it
        question = Question(question=self.new_question['question'], answer=self.new_question['answer'],
                           category=self.new_question['category'], difficulty=self.new_question['difficulty'])
        question.insert()
        id=question.id
        question.delete()
         #call the endpoint  and delete the same question for the second time
        res=self.client().delete('/questions/{}'.format(id))
        data=json.loads(res.data)
         
         #check the code error and message
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'unprocessable')

    def test_create_question(self):
        """test question creation"""

        #call for endpoint to get response and load data
        res=self.client().post('/questions',json=self.new_question)
        data=json.loads(res.data)

        self.assertEqual(data['success'],True)
        self.assertTrue(data['created'])
        #check if the question created is saved in the database
        question=db.session.query(Question).filter(Question.id==data['created']).one_or_none()
        self.assertIsNotNone(question)

        question.delete()
    
    def test_422_failure_create_question(self):
        """test for creation failure with missing data"""

        #call for endpoint to get response and load data
        res=self.client().post('/questions',json={'question':"What name does the boat with Théodore Géricault paint the raft?"})
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'unprocessable')
    
    def test_search_for_question(self):
        """ test to find a question that includes the designated string"""

        #call for endpoint to get response and load data
        res=self.client().post('/questions/search',json={'searchTerm':'title'})
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        #check that questionand nb  return data 
        self.assertTrue(data['questions'])
        self.assertTrue(data['nb'])
        #check that the search provides exactly 2 questions for the searched word 'title'
        self.assertEqual(len(data['questions']),2)

    def test_404_failure_search_for_question(self):
        """test for failure to find any  question that includes the designated string"""

         #call for endpoint to get response and load data
        res=self.client().post('/questions/search',json={'searchTerm':'fghvcjbvcj,'})
        data=json.loads(res.data)
         
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], 'resource not found')

    def test_questions_category(self):
        """test the display of all the questions in a category and only one category""" 

        #call for endpoint to get response and load data
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)
        #
        questions=db.session.query(Question).filter(Question.category==4).all()

        #check the status of the response and the message
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        #check that questions return data
        self.assertTrue(data['questions'])
        #check that question incluse all the category's questions (category number 4)
        self.assertEqual(len(data['questions']),len(questions))
        self.assertEqual(data['current_category'],4)
    def test_400_failure_questions_category(self):
        """ test for failure to display category questions if data is not exact"""

        #call for endpoint to get response and load data
        res = self.client().get('/categories/4000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,400)  
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'bad request')
        

    def test_quizz(self):
        """test if the quiz question is generated and is different from the previous questions"""
        #call for endpoint to get response and load data
        res = self.client().post('/quizzes',json={'quiz_category':{"type":"sciences","id":"5"},'previous_questions':[11,10]})
        data = json.loads(res.data)
       
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        #check that a question is generated
        self.assertTrue(data['question'])
        #check that the  question is different from previous questions
        self.assertNotEqual(data['question']['id'],4)
        self.assertNotEqual(data['question']['id'],6)
    
    def test_failure400_quizz(self):
        #call for endpoint to get response and load data
        res = self.client().post('/quizzes',json={})
        data = json.loads(res.data)
        
        #check for status code and message
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')  
        

        
       

        
        
        

        
        





    



 #Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()