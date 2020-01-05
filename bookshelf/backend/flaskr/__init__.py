import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy #, or_
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8

def paginate_books(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * BOOKS_PER_SHELF
  end = start + BOOKS_PER_SHELF
  formatted_books = [book.format() for book in selection]
  current_books = formatted_books[start:end]

  return current_books

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there. 
#     If you do not update the endpoints, the lab will not work - of no fault of your API code! 
#   - Make sure for each route that you're thinking through when to abort and with which kind of error 
#   - If you change any of the response body keys, make sure you update the frontend to correspond. 

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  #Return all books
  @app.route('/books')
  def get_all_books():
    selection = Book.query.order_by(Book.author).all()
    current_books = paginate_books(request, selection)

    if len(current_books) == 0:
      abort(404)

    res = {
      'success':True,
      'books': current_books,
      'total_books' : len(Book.query.all())
    }
    return jsonify(res)

  #Update a book's rating
  @app.route('/books/<int:book_id>', methods=['PATCH'])
  def update_book_rating(book_id):
    body = request.get_json()

    try:
      book = Book.query.get(book_id)
      if book is None:
        abort(404)

      if 'rating' in body:
        book.rating = int(body['rating'])

      book.update()

      return jsonify({
        'success' : True,
        'id' : book.id
      })
    except:
      abort(400)

  #Delete a book
  @app.route('/books/<int:book_id>', methods=['DELETE'])
  def delete_book(book_id):
    try:
      book = Book.query.get(book_id)

      if book is None:
        abort(404)
      book.delete()
    
      selection = Book.query.order_by(Book.author).all()
      current_books = paginate_books(request, selection)

      return jsonify({
        'success' : True,
        'deleted': book_id,
        'books' : current_books,
        'total_books' : len(Book.query.all())
      })

    except:
      abort(422)

  #Create a new book
  @app.route('/books', methods=['POST'])
  def submit_book():
    body = request.get_json()

    new_title = body.get('title', None)
    new_author = body.get('author', None)
    new_rating = body.get('rating', None)
    search = body.get('search', None)

    try:
      if search:
        selection = Book.query.order_by(Book.title).filter(Book.title.ilike('%{}%'.format(search)))
        current_books = paginate_books(request, selection)
        return jsonify({
          'success': True,
          'books' : current_books,
          'total_books' : len(selection.all())
        })

      else:
        book = Book(title=new_title, author=new_author, rating=new_rating)
        book.insert()
    
        selection = Book.query.order_by(Book.author).all()
        current_books = paginate_books(request, selection)
        return jsonify({
          'success' : True,
          'created' : book.id,
          'books' : current_books,
          'total_books' : len(Book.query.all())
        })
    except:
      abort(422)
  
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error' : 400,
      'message' : 'bad request'
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success' : False,
      'error' : 404,
      'message' : 'not found'
    }), 404
  
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success' : False,
      'error' : 405,
      'message' : 'method not allowed'
    }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success' : False,
      'error' : 422,
      'message' : 'unprocessable',
    }), 422


  return app

    