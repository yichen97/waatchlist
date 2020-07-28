from flask import Flask, render_template
from flask import url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click


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

class User(db.Model):  #  表名将会是 user（自动生成， 小写处理）
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

class Movie(db.Model):  #b 表明将会是 movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  #电影标题
    year = db.Column(db.String(4))  # 电影年份



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

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
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

# 修改电影条目
@app.route('/movie/edit/<int:movie_id>', methods=['GET','POST'])

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

@app.route('/user/<name>')
# <name>可以匹配关键字
def user_page(name = ''):
    return '<h1>新垣结衣</h1><br><br><img src = "https://picb.zhimg.com/80/v2-61c94da84dc86ed21512cc206cba701b_720w.jpg?source=1940ef5c"><br><br>'+'User: %s' %name

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

#  下面我们来分解这个Flask程序，了解它的基本构成。
   
#    进阶提示
# 对于 URL 变量，Flask 还支持在 URL 规则字符串里对变量设置处理器，对变
# 量进行预处理。比如 /user/<int:number> 会将 URL 中的 number 部分处
# 理成整型，同时这个变量值接收传入数字。

# 名字以 . 开头的文件默认会被隐藏，执行 ls 命令时会看不到它们，这时
# 你可以使用 ls -f 命令来列出所有文件。

    # 定义数据
