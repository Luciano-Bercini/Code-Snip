from flask import Flask, render_template, request, redirect, make_response, send_from_directory, session, jsonify
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
    username = 'Anonymous'
    if 'username' in session:
        username = session['username']
    return render_template('index.html', username=username)


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
            return jsonify('Correctly signed in!'), 200
        return jsonify('Username already exists!'), 400
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
                return jsonify('Correctly signed in!'), 200
        return jsonify('Invalid username/password combination.'), 400
    return render_template('sign_in.html')


@app.route('/sign_out', methods=['GET', 'POST'])
def sign_out():
    session.pop('username')
    return redirect('/profile')


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
        except Exception as e:
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
    logged_in = False
    if 'username' in session:
        logged_in = True
    return render_template('view.html', logged_in=logged_in, snippet=snippet, reviews_render=render_reviews(snippet))


def render_reviews(snippet):
    reviews = []
    if 'ratings' in snippet:
        # Only consider reviews (the ones with text basically).
        for rating in snippet['ratings']:
            if 'review' in rating:
                if len(rating['review']) > 0:
                    reviews.append(rating)
    return render_template('reviews.html', reviews=reviews)


@app.route('/view_snippet/<string:id>/review_snippet', methods=['POST'])
def review_snippet(id):
    if 'username' not in session:
        return jsonify('Sign in is required to review!'), 400
    rating = int(request.form.get('rating'))
    review = request.form.get('review')
    if rating < 1:
        return jsonify('You must rate the code before posting!'), 400
    username = session['username']
    if rating < 1 or rating > 5:
        return jsonify('Invalid input.'), 400
    rate = {'username': session["username"], 'rating': rating, 'review': review}
    has_rated = db_snippet.find_one({"_id": ObjectId(id), "ratings.username": username})
    if has_rated:
        db_snippet.update_one({"_id": ObjectId(id), "ratings.username": username}, {"$set": {"ratings.$.rating": rating, "ratings.$.review": review}})
    else:
        db_snippet.update_one({"_id": ObjectId(id)}, {"$push": {"ratings": rate}})
    snippet = db_snippet.find_one({"_id": ObjectId(id)})
    return jsonify(render_reviews(snippet)), 200


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


@app.route('/delete_snippet/<string:id>', methods=['POST'])
def delete_snippet(id):
    try:
        db_snippet.delete_one({"_id": ObjectId(id)})
        return jsonify('Correctly removed the snippet'), 200
    except Exception as e:
        return jsonify('There was a problem deleting the task.'), 500


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


@app.route('/information')
def information():
    return render_template('information.html')


if __name__ == "__main__":
    app.run(debug=True)
