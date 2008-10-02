import os
from genshi.template import TemplateLoader
import web

loader = TemplateLoader([os.path.dirname(os.path.abspath(__file__))],
                        auto_reload=True)
urls = ('/(.*)', 'hello')


class hello(object):

    def GET(self, name):
        i = web.input(times=1)
        if not name:
            name = 'world'
        name = name.decode('utf-8')

        tmpl = loader.load('hello.html')
        stream = tmpl.generate(name=name, times=int(i.times))

        web.header('Content-Type', 'text/html; charset=utf-8', unique=True)
        print stream.render('html')


if __name__ == '__main__':
    web.webapi.internalerror = web.debugerror
    web.run(urls, globals())
