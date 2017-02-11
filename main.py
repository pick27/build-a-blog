#!/usr/bin/env python
import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Blog(db.Model):
    title = db.StringProperty(required=True)
    blogentry = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class onepageBlogHandler(Handler):
    def get(self):
        self.redirect("/blog")
        ## self.render("onepage.html", title="", entry="", error="")

    def post(self):
        title = self.request.get("title")
        blogentry = self.request.get("entry")
        if title and blogentry:
            blog = Blog(title=title, blogentry = blogentry)
            blog.put()
            query = "SELECT * FROM Blog ORDER BY created DESC LIMIT 5"
            blogs = db.GqlQuery(query)
            self.render('onepage.html', title="", entry="", error=error, blogs=blogs)
        else:
            error = "We need both a title and a blog entry!"
            self.render('onepage.html', title=title, entry=blogentry, error=error)

class displayBlogHandler(Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        error = ""
        self.render('mainblog.html', blogs=blogs, error=error)

    def post(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render('mainblog.html', blogs=blogs)

class ViewPostHandler(Handler):
    def get(self, id):
        blog = Blog.get_by_id(int(id), parent=None)
        error = ""
        if blog == None:
            error = "There are no blog entries with that ID."
        self.render("oneblog.html", blog=blog, error=error)


class newpostBlogHandler(Handler):
    def get(self):
        self.render("addblog.html", title="", entry="", error="")

    def post(self):
        title = self.request.get("title")
        blogentry = self.request.get("entry")
        if title and blogentry:
            blog = Blog(title=title, blogentry = blogentry)
            blog.put()
            id = blog.key().id()
            self.redirect("/blog/" + str(id))
        else:
            error = "We need both a title and a blog entry!"
            self.render('addblog.html', title=title, entry=blogentry, error=error)

app = webapp2.WSGIApplication([
    ('/', onepageBlogHandler),
    ('/blog', displayBlogHandler),
    ('/newpost', newpostBlogHandler),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
