from flask import Flask, render_template
from flask import url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin
from flask_login import login_user,  logout_user
from flask_login import login_required, current_user

WIN = sys.platform.startswith('win')
if WIN: 
    prefix = 'sqlite:///'
else :
    prefix = 'sqlite:////'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭对模型修改的监控
app.config['SECRET_KEY'] = 'dev' # 等同于 app.secret_key = 'dev'

# 在扩展类实例化前加载配置
db = SQLAlchemy(app)

login_manager = LoginManager(app)
# 当未登录用户访问需登录页面，返回错误并重定向login页面
login_manager.login_view = 'login' 


class Movie(db.Model):  #b 表明将会是 movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  #电影标题
    year = db.Column(db.String(4))  # 电影年份

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop')
    # 设置选项
def initdb(drop):
    # Initialize the database
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息

@app.cli.command()
def forge():
    # Generate fake data.
    db.create_all()

    # 全局的两个变量移动到这个函数内
    name = 'yision'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poers Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1996'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    user = User(name = name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title = m['title'], year = m['year'])
        db.session.add(movie)

    db.session.commit()  
    click.echo('Done.')

@app.cli.command()
@click.option('--username', prompt=True, help="The username used to login.")
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    # Create user.
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done')

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
            flash('Login success')
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
            flash('Invalid input')
            return redirect(url_for('setting'))

        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('Setting.html')

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

# 错误处理函数，返回值作为响应主题返回给客户端
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户ID作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应用户
    return user  # 返回用户对象
    
# 这个函数返回的变量（以字典键值对的形式）将会统一注入到
# 每一个模板的上下文环境中，因此可以直接在模板中使用
# 取代404错误处理函数和主页视图函数中user变量定义，
# 并删除在render_template()函数中传入的关键字参数
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)  #需要返回字典，等同于return {'user' :user}

@app.route('/test')
def test_url_for():
    # 下面是一些调用示例（请在命令行窗口查看输出的URL）
    print(url_for('hello'))  # 输出：/
    # 注意下面两个调用是如何生成包含URL变量的URl的
    print(url_for ('user_page', name='yichen'))  #输出 :/user/yichen
    print(url_for('user_page', name='yui'))  #输出 :/user/yui 
    print(url_for('test_url_for'))  # 输出 :/test
        # 下面这个调用传入了多余的关键字参数，他们会被作为查询关键字符串附加到URL后面。
    print(url_for('test_url_for', num=2)) #  输出:/test?num=2
    return 'Test page'

