from flask import url_for, render_template, redirect, flash, request
from flask_login import login_user,  logout_user, login_required, current_user

from watchlist.models import User, Movie
from watchlist import app, db


@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        title = request.form.get('title')
        year =request.form.get('year')
        if not title or not year or len(year) > 4 or len(title)>60:
            flash('Invalid input.') #显示错误提示
            return redirect(url_for('index'))
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)
        db.session.add(movie)  # 添加数据库会话
        db.session.commit()  # 提交到数据库会话
        flash('Item created.')  #显示成功创建消息
        return redirect(url_for('index'))  # 重定向回主页

    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', user=user, movies=movies)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password =request.form['password']

        if not username or not password:
            flash('Invalid input.') #显示错误提示
            return redirect(url_for('login'))

        user = User.query.first()
        # 验证用户名和密码是否一致

        if username == user.username and user.validate_password(password):
            login_user(user)  # 登入用户
            flash('Login success.')
            return redirect(url_for ('index'))
        
        flash('Invalid username or password.')

        return redirect(url_for('login'))        
    return render_template('login.html')

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method =='POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('Settings.html')

@app.route('/logout')
@login_required  # 用于保护视图
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))

# 修改电影条目
@app.route('/movie/edit/<int:movie_id>', methods=['GET','POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year)>4 or len(title)>60 :
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id =movie_id))
        #  重定向回编辑页面

        movie.title = title  # 更新标题
        movie.year = year  #更新年份
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)  #传入被编辑的电影记录

# 删除电影条目
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required  # 登陆保护
#限定只接受 POST 请求
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id) # 获取电影记录
    db.session.delete(movie) # 删除对应的记录
    db.session.commit() # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index')) # 重定向回主页

