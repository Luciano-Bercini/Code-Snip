from flask import Flask, render_template, request, redirect, make_response, send_from_directory, session
from datetime import datetime, timezone
from pymongo import MongoClient
from bson.objectid import ObjectId
import logging
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = '364S1947RO713085892N7LO'
client = MongoClient("mongodb://localhost:27017/")
snipdb = client["snipdb"]
db_snippet = snipdb["snippets"]
db_users = snipdb["users"]


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/profile', methods=['GET'])
def profile():
    if 'username' in session:
        return render_template('profile.html', username=session['username'])
    return redirect('/sign_in')


@app.route("/sign_up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        existing_user = db_users.find_one({'username': username})
        if not existing_user:
            hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            db_users.insert_one({'username': username, 'password': hashed_pass})
            session['username'] = username
            return redirect('/')
        return 'Username already exists!'
    return render_template('sign_up.html')


@app.route("/sign_in", methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        login_user = db_users.find_one({'username': username})
        if login_user:
            if bcrypt.checkpw(password.encode('utf-8'), login_user['password']):
                session['username'] = username
                return redirect('/')
        return 'Invalid username/password combination'
    return render_template('sign_in.html')


@app.route('/sign_out', methods=['GET', 'POST'])
def sign_out():
    session.pop('username')
    return redirect('/search')


@app.route('/post_snippet', methods=['POST'])
def post_snippet():
    title = request.form.get('title')
    content = request.form.get('content')
    language = request.form.get('language')
    author = 'Anonymous'
    if 'username' in session:
        author = session['username']
    post_validation = is_snippet_valid(title, content)
    if not post_validation[0]:
        return post_validation[1]
    new_snippet = {"author": author, "title": title, "content": content, "language": language, "date": datetime.now(timezone.utc)}
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


@app.route('/sw.js', methods=['GET'])
def sw():
    response = make_response(send_from_directory('static', 'sw.js'))
    response.headers['Content-Type'] = 'application/javascript'
    return response


@app.route('/view_snippet/<string:id>')
def view_snippet(id):
    snippet = db_snippet.find_one({"_id": ObjectId(id)})
    return render_template('view.html', snippet=snippet)


@app.route('/view_snippet/<string:id>/rate_snippet', methods=['POST'])
def rate_snippet(id):
    if 'username' not in session:
        return 'Sign in has failed', -1
    rating = int(request.form.get('rating'))
    username = session['username']
    if rating > 5:
        return "Too high", 0
    if rating < 1:
        return "Too low", 0
    rate = {'username': session["username"], 'rating': rating}
    has_rated = db_snippet.find_one({"_id": ObjectId(id), "ratings.username": username})
    if has_rated:
        db_snippet.update_one({"_id": ObjectId(id), "ratings.username": username}, {"$set": {"ratings.$.rating": rating}})
    else:
        db_snippet.update_one({"_id": ObjectId(id)}, {"$push": {"ratings": rate}})
    return "Success", 1


@app.route('/render_query_table', methods=['GET'])
def render_query_table():
    title = request.args.get('title')
    language = request.args.get('language')
    query = {"title": {"$regex": title, "$options": 'i'}}
    if language != 'Any':
        query["language"] = language
    snippets = list(db_snippet.find(query, {'content': 0}).sort('date', -1))
    correct_representation_snippets(snippets)
    return render_template('snippets_table.html', snippets=snippets)


@app.route('/render_user_snippets_table', methods=['GET'])
def render_user_snippets_table():
    query = {"author": session['username']}
    snippets = list(db_snippet.find(query, {'content': 0, 'author': 0}).sort('date', -1))
    correct_representation_snippets(snippets)
    return render_template('snippets_table.html', snippets=snippets, username=session['username'])


def correct_representation_snippets(snippets):
    for snippet in snippets:
        snippet['date'] = snippet['date'].strftime('%d %b %Y')
        snippet['average'] = 0  # By default 0.
        if 'ratings' in snippet:
            sum_ratings = 0
            for rating in snippet['ratings']:
                sum_ratings += rating['rating']
            snippet['average'] = sum_ratings // len(snippet['ratings'])
            snippet.pop('ratings')  # Remove the ratings from the snippet view.


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


@app.route('/delete_snippet/<string:id>')
def delete_snippet(id):
    try:
        db_snippet.delete_one({"_id": ObjectId(id)})
        return redirect('/profile')
    except:
        return 'There was a problem deleting the task.'


@app.route('/information')
def information():
    return render_template('information.html')


if __name__ == "__main__":
    app.run(debug=True)
