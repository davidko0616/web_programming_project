from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# 게시판 데이터를 메모리에 저장 (임시)
posts = []
post_id_counter = 1

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
    filtered_posts = [p for p in posts if query.lower() in p['title'].lower() or query.lower() in p['content'].lower()]
    return render_template('qna.html', posts=filtered_posts, query=query)

# 🔹 글쓰기 페이지
@app.route('/qna/write', methods=['GET', 'POST'])
def qna_write():
    global post_id_counter
    if request.method == 'POST':
        name = request.form['name']
        title = request.form['title']
        content = request.form['content']
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        post = {
            'id': post_id_counter,
            'name': name,
            'title': title,
            'content': content,
            'created_at': created_at,
            'comments': []
        }
        posts.append(post)
        post_id_counter += 1
        return redirect(url_for('qna'))
    return render_template('qna-write.html')

# 🔹 게시글 수정 페이지
@app.route('/qna/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    post = next((p for p in posts if p['id'] == post_id), None)
    if not post:
        return 'Post not found', 404

    if request.method == 'POST':
        post['title'] = request.form['title']
        post['content'] = request.form['content']
        post['name'] = request.form.get('name', post['name'])
        return redirect(url_for('qna'))

    return render_template('edit.html', post=post)

# 🔹 게시글 삭제
@app.route('/qna/delete/<int:post_id>', methods=['POST'])
def delete(post_id):
    global posts
    posts = [p for p in posts if p['id'] != post_id]
    return redirect(url_for('qna'))

# 🔹 댓글 추가
@app.route('/qna/comment/<int:post_id>', methods=['POST'])
def comment(post_id):
    post = next((p for p in posts if p['id'] == post_id), None)
    if not post:
        return "Post not found", 404
    comment = request.form['comment']
    post['comments'].append(comment)
    return redirect(url_for('qna'))

# 🔹 앱 실행
if __name__ == '__main__':
    app.run(debug=True)
