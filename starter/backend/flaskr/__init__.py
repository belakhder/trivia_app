import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy import cast


from models import db,setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request,selection):
  page=request.args.get('page',1,type=int)
  start=(page-1)*QUESTIONS_PER_PAGE
  end=start+QUESTIONS_PER_PAGE

  questions=selection[start:end]
  return questions

  
def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  cors = CORS(app, resources={r"/*": {"origins": "*"}})
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories=db.session.query(Category).all()
     
    categories_ = {}
    for category in categories:
      categories_[category.id] = category.type

    if (len(categories_) == 0):
      abort(404)
    return jsonify({
      'success': True,
      'categories': categories_
    })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  
  def get_questions():
    
    selection=db.session.query(
      Question).all()
    
    questions = [question.format() for question in selection]

    categories=db.session.query(Category).all()
    categories_ = {}
    for category in categories :
      categories_[category.id]= category.type 
    questions_category=paginate_questions(request,questions)
    if (len(categories_) * len(questions_category))==0:
      abort(404)
    return jsonify ({
     'success': True,
     'questions':questions_category,
     'total_questions':len(selection),
     'categories': categories_,
   })
   
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>',methods=['DELETE'])
  def delete_question(question_id):
    try:
      question=Question.query.get(question_id)

      question.delete()
      questions=db.session.query(Question.question).all()
      current_questions=paginate_questions(request,questions)

      return jsonify ({
        'success':True,
        'questions':current_questions,
        'number_questions':len(questions),
        'deleted_id': question_id
      })
    except:
      abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions',methods=['POST'])
  def create_question():
     body=request.get_json()

     question_=body.get('question',None)
     answer_=body.get('answer',None)
     category_=body.get('category',None)
     difficulty_=body.get('difficulty',None)
     if question_ is None or answer_ is None \
        or  category_ is None or  difficulty_ is None :
       abort(422)
     
     try:
      question=Question (
        question=question_,
        answer=answer_,
        category=category_,
        difficulty=difficulty_
        )
      question.insert()

      return jsonify({
       'success': True,
       'created': question.id,
    })
     except:
      abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 


  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    search_term = request.json.get('searchTerm', '')
    questions_result = db.session.query(Question).filter(
      Question.question.ilike(f'%{search_term}%')).all()
    if len (questions_result)==0 :
      abort(404)
    
    return jsonify ({
      'success':True,
      'questions': [question.format() for question in questions_result],
      'nb':len(questions_result)
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions',methods=['GET'])
  def questions_category(category_id):
    if category_id==0:
      questions_category=db.session.query(
        Question).all()
    else :questions_category=db.session.query(
      Question).filter(Question.category==category_id).all()
    
    if len (questions_category)==0:
      abort(400)

    return jsonify({
      'success': True,
      'questions': [question.format() for question in questions_category],
      'total_questions': len(questions_category),
      'current_category': category_id
    })


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def quiz():
    category_quizz= request.json.get('quiz_category')
    previous_question=request.json.get('previous_questions')

    categories=db.session.query(Category.id).all()
    categories_=[category.id for category in categories]
    categories_.append(0)

    if ((category_quizz is None ) or (previous_question is None) or (
       int(category_quizz['id']) not in categories_)):
          abort(400)

    if int(category_quizz['id'])==0 :
       questions_=Question.query.filter(
         Question.id.notin_((previous_question))).all()
      
    else: 
       questions_=Question.query.filter_by(
         category=category_quizz['id']).filter(
           Question.id.notin_((previous_question))).all()
    
    questions_quiz=[(question.format())['id'] for question in questions_]

    if len(questions_quiz)>0:
      question_random=questions_quiz[
        random.randrange(0,len(questions_quiz), 1)] 
      question_quiz=db.session.query(
       Question).filter(Question.id==question_random).one_or_none()
      quiz=question_quiz.format()
    else:
      quiz=None
       
    return jsonify({
      'success': True,
      'question':quiz,
    })
    



  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422.
  
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
     "success": False,
     "error": 422,
     "message": "unprocessable"
     }), 422
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
    }), 400
  return app

    