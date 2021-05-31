import logging
from flask import Flask, render_template, request, redirect, jsonify, make_response, send_from_directory
from datetime import *
from pymongo import MongoClient
from bson.objectid import ObjectId
import re

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
snipdb = client["snipdb"]
db_snippet = snipdb["snippets"]


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/post_snippet', methods=['POST'])
def post_snippet():
    title = request.form.get('title')
    content = request.form.get('content')
    language = request.form.get('language')
    post_validation = is_snippet_valid(title, content)
    if not post_validation[0]:
        return post_validation[1]
    new_snippet = {"author": "None", "title": title, "content": content, "language": language, "date": datetime.now(timezone.utc)}
    try:
        db_snippet.insert_one(new_snippet)
        return "success"
    except Exception as e:
        logging.exception(e)
        return "Unable to commit to database"


def is_snippet_valid(title, content):
    if not title:
        return False, "Missing title!"
    if len(title) > 1000:
        return False, "Title is over 1000 characters!"
    if len(content) > 10000:
        return False, "Content is over 10000 characters!"
    return True, "The post is valid!"


@app.route('/update_snippet/<string:id>', methods=['GET', 'POST'])
def update_snippet(id):
    snippet = db_snippet.find_one({"_id": ObjectId(id)})
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        language = request.form.get('language')
        post_validation = is_snippet_valid(title, content)
        if not post_validation[0]:
            return post_validation[1]
        try:
            db_snippet.update_one({"_id": ObjectId(id)}, {"$set": {"title": title, "content": content, "language": language}})
            return "success"
        except:
            return 'There was an issue updating your task.'
    else:
        return render_template('update.html', snippet=snippet)


@app.route('/sw.js')
def sw():
    response = make_response(send_from_directory('static', 'sw.js'))
    return response


@app.route('/view/<string:id>')
def view(id):
    snippet = db_snippet.find_one({"_id": ObjectId(id)})
    print(snippet)
    return render_template('view.html', snippet=snippet)


@app.route('/render_query_table', methods=['GET'])
def render_query_table():
    title = request.args.get('title')
    language = request.args.get('language')
    query = {"title": {"$regex": title, "$options": 'i'}}
    if language != 'Any':
        print(language)
        query["language"] = language
    snippets = db_snippet.find(query).sort("date", -1)
    return render_template('query_table.html', posts=snippets)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        title = request.form['title']
        language = request.form['language']
        query = {}
        if not title:
            query["title"] = {"$regex": title, "$options": 'i'}
        if not language:
            query["language"] = {"$regex": language, "$options": 'i'}
        snippets = db_snippet.find(query).sort("date", -1)
    else:
        snippets = db_snippet.find().sort("date", -1)
    return render_template('/search.html', posts=snippets)


@app.route('/delete/<string:id>')
def delete(id):
    try:
        db_snippet.delete_one({"_id": ObjectId(id)})
        return redirect('/search')
    except:
        return 'There was a problem deleting the task.'


@app.route('/information')
def information():
    return render_template('information.html')


if __name__ == "__main__":
    app.run(debug=True)
