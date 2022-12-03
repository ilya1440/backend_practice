# export FLASK_APP=flaskr
# export FLASK_ENV=development

import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8


def paginate_books(books, request):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF
    books = [book.format() for book in books]
    books = books[start:end]
    return books


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    @app.route('/books')
    def get_books():
        books = Book.query.order_by(Book.id).all()
        books_paginated = paginate_books(books, request)

        if len(books_paginated) == 0:
            abort(404)

        return jsonify(
            {
                'success': True,
                'books': books_paginated,
                'total_books': len(books)
            }
        )

    # curl -X PATCH http://127.0.0.1:5000/books/8 -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{"rating": "1"}'
    @app.route('/books/<int:book_id>', methods=['PATCH'])
    def update_rating(book_id):
        body = request.get_json()
        try:
            book = Book.query.get(book_id)
            if book is None:
                abort(404)

            if 'rating' in body:
                book.rating = int(body.get('rating'))
            book.update()

            return jsonify(
                {
                    'success': True,
                    'book_id': book_id
                }
            )
        except:
            abort(400)

    @app.route('/books/<int:book_id>', methods=['DELETE'])
    def delete_book(book_id):
        try:
            book = Book.query.get(book_id)

            if book is None:
                abort(404)

            book.delete()
            books = Book.query.order_by(Book.id).all()
            books_paginated = paginate_books(books, request)

            return jsonify(
                {
                    'success': True,
                    'deleted': book_id,
                    'books': books_paginated,
                    'total_books': len(books)
                }
            )
        except:
            abort(422)

    # curl -X POST -H "Content-Type: application/json" -d '{"title":"Neverwhere", "author":"Neil Gaiman", "rating":"5"}' http://127.0.0.1:5000/books
    @app.route('/books', methods=['POST'])
    def create_book():
        body = request.get_json()
        title = body.get('title', None)
        author = body.get('author', None)
        rating = body.get('rating', None)
        try:
            book = Book(title=title, author=author, rating=rating)
            book.insert()
            books = Book.query.order_by(Book.id).all()
            books_paginated = paginate_books(books, request)

            return jsonify(
                {
                    'success': True,
                    'created': book.id,
                    'books': books_paginated,
                    'total_books': len(books)
                }
            )
        except:
            abort(422)

    return app
