
# KaKa

一个基于`werkzeug`和`jinja2`的`web`框架，简单易用、架构清晰、模块化。

## 快速开始
### 安装并引入
使用如下命令安装KaKa:

    pip install KaKa

使用如下命令将框架引入你的项目：

    from kaka import KaKa

### 实例化应用
使用如下语句实例化一个`KaKa`应用对象：

    app = KaKa()

### 定义视图函数
使用如下语句定义一个简单的视图函数，此函数将会接受`http`请求并返回一个简单的`hello world`字符串:

    from kaka.response import TextResponse

    def hello(request):
        return TextResponse('hello world')

### 定义路由表
使用如下语句定义一个路由表以指导`http`请求的正确路由：

    app.router.register([
        ('index/', hello),
    ])

### 启动服务器
执行如下语句启动服务器，`KaKa`会帮助我们启动底层的`WSGI`服务器，默认地址是`127.0.0.1`，端口号是`8888`：

    app.run_server()

`KaKa`为`run_server`接口提供了一个`debug`参数，默认值是`False`，若置为`True`则会启动`debug`模式。
在`debug`模式中，任何对源代码的修改都将自动重启服务器，且一旦发生了错误将会在浏览器上以页面的形式显示出错误栈信息。
可以这样开启`debug`模式：

    app.run_server(debug=True)

### 页面展示
打开浏览器并访问`http://127.0.0.1:8888/index/`，你将会看到视图函数返回的`hello world`字符串。

---

## 功能介绍和使用

然而，一个简单的`hello world`页面是不足以解决我们的问题的，下面是`KaKa`框架目前支持的功能介绍和使用说明。

### 路由系统

#### 定义路由表

路由系统是`web`框架最核心的功能之一，`KaKa`使用术语`路由器`和`路由表`来描述路由系统。
`KaKa`的路由系统底层引用了`Werkzeug`的`Map`和`Rule`模块。

一张路由表由一个元组列表表示，其中的元组代表着路由条目信息。
`KaKa`设定路由条目由`3`个参数组成：`url, view, name`，其中`name`可以不提供。
但若为`name`提供了一个值，你就可以通过`reverse`函数来反向解析`url`，像这样：

    from kaka.utils import reverse

    # 路由表
    table = [
        ('index/', index_view),   # 路由条目1
        ('articles/', article_view),  # 路由条目2

        ('home/', home_view, 'home'),  # 路由条目3
    ]

    url = reverse('home')  # url的值是: '/home/'

#### 处理动态元素

如果`url`中有动态的元素，`KaKa`也可以处理，动态元素将会作为视图函数的参数传入，就像这样：

    table = [
        ('articles/<int:id>/', show_articles, 'article'),
    ]

#### 多级路由

`KaKa`的路由系统还支持多级路由，这一部分的介绍和使用我将会放到产品文档中。


### 视图系统
#### 视图传参
视图系统是处理`http`请求并返回`http`响应的地方。
`KaKa`为所有的视图函数提供了一个`request`第一参数，代表当前的请求对象，用户可以通过此对象访问有底层请求环境的相关数据。

#### 响应对象
`KaKa`使用`TextResponse`类来封装字符串形式的返回值，这种返回值的`mimetype=text/plain`，所以它不会被浏览器当做`html`页面渲染，而是直接打印字符串。
像这样使用视图系统：

    from kaka.response import TextResponse

    def show_articles(request, nid):
        print(request.path)
        print(request.cookies)
        print(request.method)
        print(nid)

        return TextResponse('show articles view')

### 模板渲染
#### 模板目录设定
模板渲染功能可以让我们方便的制造含有动态元素的`html`页面。
在渲染功能上，`KaKa`目前没有做太多事情，仅是在底层引用了`jinja2`模块并为模板渲染过程提供了一层方便调用的接口。
在使用渲染功能前首先定义模板文件目录：

    # 设定模板文件所在目录
    template_path = 'your template directory'
    app.render.register(template_path)

#### 渲染调用
`KaKa`为用户提供了一个`RenderResponse`响应对象，其底层调用了`jinja2`的渲染接口。
渲染的结果类型将会是`mimetype=text/html`，所以浏览器会将结果当做`html`页面渲染并展示。

    from kaka.response import RenderResponse

    # 在视图函数中使用模板渲染功能
    def show_articles(request, id):
        title = 'hello kaka'
        content = 'a web framework'

        return RenderResponse('article.html', title=title, content=content)


### `Restful`支持

#### `Restful`视图定义
当然，`KaKa`也支持`Restful`形式的请求处理，`KaKa`使用了一个`RestView`来帮助分发请求，像这样定义`restful`的视图函数：

    from kaka.restful import RestView

    # 定义restful形式的处理视图，必须以类的形式定义
    class ArticlesView(RestView):
        def get(self, request, id):
            pass

        def post(self, request)
            pass
        
        ...  # 其他与http method同名的函数

#### `Restful`视图路由
`restful`的视图函数可以像这样添加到路由表中：

    table = [
        ('index/', index),
        ('articles/', ArticlesView.restful, 'article),  # 使用类名.restful即可
    ]

#### `Restful`视图响应
`KaKa`除了支持`restful`的请求之外还支持`restful`的响应，使用了`RestResponse`响应类，它的`mimetype=application/json`, 所以一个`restful`响应的使用和样式是这样的：

    from kaka.restful import RestView
    from kaka.response import RestResponse  # restful风格的响应类

    class ArticlesView(RestView):
        def get(self, request, id):
            data = {'title': 'hello kaka', 'content': 'a web framework'}
            extra_dict = {
                'data': data,
            }
            return RestResponse(code=1200, status='success', extra_dict=extra_dict)

    # 这样的响应在浏览器中看起来是这样的：
    {
        "code": 1200,
        "status": "success",
        "data": {
            "title": "hello kaka",
            "content": "a web framework"
        }
    }

#### 高层`Restful`调用接口
在`restful`的支持上，`KaKa`还提供了更高一层的`SUCCESS`和`FAIL`接口，为用户提供了更加方便的操作`restful`响应的形式，不过这两个接口的介绍和使用说明我将会放到产品文档中。

### 中间件系统

#### 处理机制解释
`KaKa`提供了中间件系统，让用户可以在视图处理前和处理后对请求(或响应)对象完成必要的中间操作。
我认为中间件系统的主要目的是**修改**流经的请求或响应对象，而**不是伪造**一个新的对象，这意味着`KaKa`提供的中间件系统的处理机制是这样的：

* 视图前

    `KaKa`的中间件系统在视图前的处理只允许返回`None`或一个响应对象(这意味着后续中间件不再有机会处理请求，视图函数也是)。换句话说，返回`None`意味着中间件仅仅对请求对象执行修改操作而不是替换它，返回一个响应对象意味着中间件拦截了这个请求并直接返回。

* 视图后

    `KaKa`的中间件系统在视图后的处理只允许返回`None`，这意味着中间件只能修改响应对象而不能替换它。

*关于中间件系统的详细设计思路和结构请参考产品文档。*

#### 定义中间件
我们可以通过这种方式自定义一个中间件：

    from kaka.middlewares import AbstractMiddleWare  # 抽象中间件类，用于约束处理接口
    from kaka.response import TextResponse

    class MyMiddleWare(AbstractMiddleWare):
        def pre_process(self, request):
            print('对请求对象做各种修改操作')
            return None

            # 如果要拦截当前请求，则这样写：
            # return TextResponse('中间件拦截请求，直接返回响应对象')

        def after_process(self, request, response):
            print('对响应对象做各种修改操作', response)
            return None

#### 注册中间件
然后通过中间件管理器注册这个中间件以使其生效：

    import MyMiddleWare

    app.mw_manager.register([
        (5, MyMiddleWare),  # priority, cls
    ])
其中，`5`是表示优先级的数字，最小为0，最大无限制，**数字越小优先级越高**。


#### 多个中间件的执行顺序
如果定义了多个中间件(很常见的情况)，则它们的处理顺序是这样的：

    app.mw_manager.register([
        (5, MW1),
        (7, MW2),
        (9, MW3),
    ])

    # 视图前：MW1处理请求 -> MW2处理请求 -> MW3处理请求 
    # 视图后：MW3处理响应 -> MW2处理响应 -> MW1处理响应

#### 多个中间件的数据共享
`KaKa`对请求对象和响应对象均设置了一个`storage`属性用以共享数据，它使用起来像这样：

    # 请求中间件中的使用
    def pre_process(self, request):
        request.storage['is_handled'] = True

        return None

    # 视图中的使用
    def show_articles(request):
        print(request.storage.get('is_handled'))
        response = TextResponse('hello world')
        response.storage['name'] = 'kaka'

        return response

    # 响应中间件中的使用
    def after_process(self, request, response):
        print(request.get('is_handled'))
        print(response.get('name'))

        return None
