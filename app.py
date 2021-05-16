from flask import Flask, render_template, request, redirect
from datetime import datetime
from flask_sqlalchemy import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<Post %r>' % self.id

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        new_post = Post(title=post_title, content=post_content)
        try:
            db.session.add(new_post)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue posting your task.'
    else:
        posts = Post.query.order_by(Post.date_created).all()
        return render_template('index.html', posts=posts)

#@app.route('/information')
#def information():
#    return render_template('information.html')


#@app.route('/contact')
#def contact():
#    return render_template('contact.html')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    snippet_to_update = Post.query.get_or_404(id)
    if request.method == 'POST':
        snippet_to_update.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task.'
    else:
        return render_template('update.html', snippet=snippet_to_update)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Post.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting the task.'

if __name__ == "__main__":
    app.run(debug=True)
