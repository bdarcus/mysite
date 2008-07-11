import web
from bibo.models import *
from rdflib import URIRef
from rdflib.Graph import Graph
from utils.site import *
import markdown2

# creates a static version of the site

render = web.template.render('templates/', cache=False)
web.template.Template.globals['render'] = render 
web.template.Template.globals['sorted'] = sorted 
web.template.Template.globals['rel_uri'] = get_relative_uri 
web.template.Template.globals['markdown'] = markdown2.markdown

rdf = ["/Users/darcusb/myweb/meta/about.n3",
       "/Users/darcusb/myweb/meta/publications.n3",
       "/Users/darcusb/myweb/meta/categories.n3",
       "/Users/darcusb/myweb/meta/links.n3",
       "/Users/darcusb/myweb/meta/periodicals.n3",
       "/Users/darcusb/myweb/meta/publishers.n3"
       ]

outdir = '/Users/darcusb/Sites/home'

graph = rdfSubject.db

for file in rdf:
    graph.parse(file, format='n3')

print "triples in graph: " + str(len(graph))

person_uri = 'http://bruce.darcus.name/about#me'
me = Person(URIRef(person_uri))

def foaf_to_html(person_uri):
    print "generating about page"
    filename = outdir 
    content = render.about(me).__str__()
    subgraph = get_subgraph(me.resUri)
    write_file(filename + '/about.rdf', subgraph.serialize())
    write_file(filename + '/about.xhtml', content)

def categories_to_html():
    print "generating categories pages"
    categories = sorted(Concept.ClassInstances())
    count = 0
    index_filename = outdir + '/categories/index.xhtml'
    index_content = render.categories(categories).__str__()
    write_file(index_filename, index_content)
    for category in categories:
        count += 1
        filename = outdir + get_relative_uri(category.resUri)
        content = render.category(category).__str__()
        subgraph = get_subgraph(category.resUri)
        write_file(filename + '.rdf', subgraph.serialize())
        write_file(filename + '.xhtml', content)
    print "    generated:"
    print "          "  + str(count) + " category page(s)"

def load_subjects(uri):
    print uri
    if urlparse.urlsplit(uri)[1] == 'bruce.darcus.name':
        print "moving on ..."
    else:
        graph.parse(uri)

def pubs_to_html():
    print "generating publications pages"
    articles = sorted(AcademicArticle.ClassInstances())
    books = sorted(Book.ClassInstances())
    chapters = sorted(Chapter.ClassInstances())
    # keep track of number of objects
    artcount = 0
    bookcount = 0
    chaptercount = 0
    # create index
    index_filename = outdir + '/publications/index.xhtml'
    index_content = render.publications(me, articles, books).__str__()
    write_file(index_filename, index_content)
    # iterate through pubs to grab external triples (from, for example, lcsh.info)
    for article in articles:
        for asub in article.subjects:
            load_subjects(asub.resUri)
    for book in books:
        for bsub in book.subjects:
            load_subjects(bsub.resUri)
    for chapter in chapters:
        for csub in chapter.subjects:
            load_subjects(csub.resUri)
    for article in articles:
        artcount += 1
        filename = outdir + get_relative_uri(article.resUri)
        content = render.article(article).__str__()
        subgraph = get_subgraph(article.resUri)
        write_file(filename + '.rdf', subgraph.serialize())
        write_file(filename + '.xhtml', content)
    for book in books:
        bookcount += 1
        filename = outdir + get_relative_uri(book.resUri)
        content = render.book(book).__str__()
        subgraph = get_subgraph(book.resUri)
        write_file(filename + '.rdf', subgraph.serialize())
        write_file(filename + '.xhtml', content)
    for chapter in chapters:
        chaptercount += 1
        filename = outdir + get_relative_uri(chapter.resUri)
        content = render.chapter(chapter).__str__()
        subgraph = get_subgraph(chapter.resUri)
        write_file(filename + '.rdf', subgraph.serialize())
        write_file(filename + '.xhtml', content)
    print "    generated:"
    print "          "  + str(artcount) + " article page(s)"
    print "          "  + str(bookcount) + " book page(s)"
    print "          "  + str(chaptercount) + " chapter page(s)"

def links_to_html():
    print "generating categories pages"
    links = sorted(Bookmark.ClassInstances())
    count = 0
    index_filename = outdir + '/links/index.xhtml'
    index_content = render.links(links).__str__()
    write_file(index_filename, index_content)

def write_file(filename, content):
    FILE = open(filename,"w")
    FILE.write(content)
    FILE.close()

def get_subgraph(s):
    g = ConjunctiveGraph()
    g.bind('skos', SKOS)
    g.bind('bibo', BIBO)
    g.bind('foaf', FOAF)
    g.bind('bio', URIRef('http://purl.org/vocab/bio/0.1/'))
    g.bind('dc', DC)

    for p, o in graph.predicate_objects(s):
        g.add((s, p, o))

    if len(g) == 0:
        return None

    return g

foaf_to_html('http://bruce.darcus.name/about#me')
categories_to_html()
pubs_to_html()
links_to_html()

