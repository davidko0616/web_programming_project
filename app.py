from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qna.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Database Models
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.String(20), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


# Create tables
with app.app_context():
    db.create_all()


# 🔹 홈 페이지
@app.route('/')
def home():
    return render_template('Home Page.html')


# 🔹 소개 페이지
@app.route('/intro')
def intro():
    return render_template('intro.html')


# 🔹 신청 폼 페이지
@app.route('/form')
def form():
    return render_template('form.html')


# 🔹 Q&A 목록 페이지 (검색 포함)
@app.route('/qna')
def qna():
    query = request.args.get("q", "")
    if query:
        filtered_posts = Post.query.filter(
            (Post.title.ilike(f'%{query}%')) |
            (Post.content.ilike(f'%{query}%'))
        ).all()
    else:
        filtered_posts = Post.query.all()
    return render_template('qna.html', posts=filtered_posts, query=query)


# 🔹 글쓰기 페이지
@app.route('/qna/write', methods=['GET', 'POST'])
def qna_write():
    if request.method == 'POST':
        name = request.form['name']
        title = request.form['title']
        content = request.form['content']
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        new_post = Post(
            name=name,
            title=title,
            content=content,
            created_at=created_at
        )
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('qna'))
    return render_template('qna-write.html')


# 🔹 게시글 수정 페이지
@app.route('/qna/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.name = request.form.get('name', post.name)
        db.session.commit()
        return redirect(url_for('qna'))

    return render_template('edit.html', post=post)


# 🔹 게시글 삭제
@app.route('/qna/delete/<int:post_id>', methods=['POST'])
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('qna'))


# 🔹 댓글 추가
@app.route('/qna/comment/<int:post_id>', methods=['POST'])
def comment(post_id):
    post = Post.query.get_or_404(post_id)
    comment_content = request.form['comment']

    new_comment = Comment(content=comment_content, post_id=post.id)
    db.session.add(new_comment)
    db.session.commit()

    return redirect(url_for('qna'))


# 🔹 앱 실행
if __name__ == '__main__':
    app.run(debug=True)