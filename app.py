from flask import Flask
from flask import url_for

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello'

@app.route('/user/<name>')
# <name>可以匹配关键字
def user_page(name = ''):
    return '<h1>新垣结衣</h1><br><br><img src = "https://picb.zhimg.com/80/v2-61c94da84dc86ed21512cc206cba701b_720w.jpg?source=1940ef5c"><br><br>'+'User: %s' %name

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
   