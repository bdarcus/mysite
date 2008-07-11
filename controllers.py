import web
from utils.site import *
from bibo.models import *
from rdflib import URIRef

render = web.template.render('templates/', cache=False)

me = Person('<http://bruce.darcus.name/about#me>')

class Home:
    def GET(self):
        set_html_content_type()
        return(render.home())

class About:
    def GET(self):
        return(render.about(me))

class Links:
    def GET(self):
        bookmarks = sorted(Bookmark.ClassInstances())
        set_html_content_type()
        return(render.links(bookmarks))

class Link:
    def GET(self, uri):
        mime_type = get_mime_type(accept_override)
        bookmark = Bookmark(URIRef(uri))
        if mime_type == 'application/rdf+xml':
            web.header('Content-location', resource.resUri.split('#')[0] + '.rdf')
            web.header('Content-type', 'application/rdf+xml; charset=UTF-8')
            return(to_rdf(bookmark, format='xml'))
        else:
            set_html_content_type()
            return(render.links(self.bookmark))

class Categories:
    categories = Concept.ClassInstances()
    def GET(self):
        return(render.categories(self.categories))

class Photos:
    def GET(self):
        photos = Image.ClassInstances()
        set_html_content_type()
        return(render.photos(photos))

class Photo:
    def GET(self, uri):
        mime_type = get_mime_type(accept_override)
        photo = Photo(URIRef(uri))
        if mime_type == 'application/rdf+xml':
            web.header('Content-location', resource.resUri.split('#')[0] + '.rdf')
            web.header('Content-type', 'application/rdf+xml; charset=UTF-8')
            return(to_rdf(photo, format='xml'))
        else:
            set_html_content_type()
            return(render.photos(self.photos))

class Publications:
    def GET(self):
        books = sorted(Book.ClassInstances())
        articles = sorted(AcademicArticle.ClassInstances())
        set_html_content_type()
        return(render.publications(me, articles, books))


class ArticlePublication:
    def GET(self, slug):
        uri = 'http://bruce.darcus.name/publications/' + slug
        article = AcademicArticle(URIRef(uri))
        set_html_content_type()
        return(render.article(article))

class BookPublication:
    def GET(self, slug):
        uri = 'http://bruce.darcus.name/publications/' + slug
        book = Book(URIRef(uri))
        set_html_content_type()
        return(render.book(book))


class ChapterPublication:
    def GET(self, slug):
        uri = 'http://bruce.darcus.name/publications/chapters/' + slug
        chapter = Chapter(URIRef(uri))
        set_html_content_type()
        return(render.chapter(chapter))
