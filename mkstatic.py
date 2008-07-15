import web
from models import *
from rdflib import URIRef
from rdflib.Graph import Graph
from utils.site import *
import markdown2
from optparse import OptionParser
from sys import stdout
import os
from os.path import dirname, join, split, splitext, expanduser

config_file = os.path.join(os.path.dirname(__file__), 'config.py')
config = eval(open(config_file).read())

def main():
    # commandline options
    opt_parser = OptionParser()
    opt_parser.set_usage("usage:\n mkstatic.py [options] [output directory]")
    opt_parser.add_option('-l', action="store_true", dest='links', 
                          help='generate links')
    opt_parser.add_option('-p', action="store_true", dest='pubs', 
                          help='generate publications')
    opt_parser.add_option('-c', action="store_true", dest='categories', 
                          help='generate categories')
    opt_parser.add_option('-f', action="store_true", dest='foaf', 
                          help='generate about page from faof')
    opt_parser.add_option('-a', action="store_true", dest='all', 
                          help='generate all')
    opts, args = opt_parser.parse_args()

    if len(args) == 0:
        print opt_parser.usage
        exit()

    basedir = args[0]

    make_directories(basedir)

    if opts.foaf or opts.all:
        foaf(basedir, 'http://bruce.darcus.name/about#me')

    if opts.categories or opts.all:
        categories(basedir)
        
    if opts.pubs or opts.all:
        pubs(basedir)
        
    if opts.links or opts.all:
        links(basedir)


# creates a static version of the site

render = web.template.render('templates/', cache=False)
web.template.Template.globals['render'] = render 
web.template.Template.globals['sorted'] = sorted 
web.template.Template.globals['rel_uri'] = get_relative_uri 
web.template.Template.globals['markdown'] = markdown2.markdown

graph = rdfSubject.db

for root, dirs, files in os.walk(config['site.rdf_dir']):
   for name in files:       
       filename = os.path.join(root, name)
       if filename.endswith('.n3'):
           print filename
           graph.parse(filename, format='n3')

print "triples in graph: " + str(len(graph))

def make_directories(base_dir):
    for dir in ['publications', 'categories', 'links']:
        newdir = os.path.join(base_dir, dir)
        if os.path.isdir(newdir):
            pass
        else:
            os.mkdir(newdir)

person_uri = 'http://bruce.darcus.name/about#me'
me = Person(URIRef(person_uri))

def foaf(basedir, person_uri):
    print "generating about page"
    content = render.about(me).__str__()
    subgraph = get_subgraph(me.resUri)
    write_file(basedir + '/about.rdf', subgraph.serialize())
    write_file(basedir + '/about.xhtml', content)

def categories(basedir):
    print "generating categories pages"
    categories = sorted(Concept.ClassInstances())
    count = 0
    index_filename = basedir + '/categories/index.xhtml'
    index_content = render.categories(categories).__str__()
    write_file(index_filename, index_content)
    for category in categories:
        if len(get_relative_uri(category.resUri).split('http://')) == 1:
            count += 1
            filename = basedir + get_relative_uri(category.resUri)
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

def pubs(basedir):
    print "generating publications pages"
    articles = sorted(AcademicArticle.ClassInstances())
    books = sorted(Book.ClassInstances())
    chapters = sorted(Chapter.ClassInstances())

    # keep track of number of objects
    artcount = 0
    bookcount = 0
    chaptercount = 0

    # create index
    index_filename = basedir + '/publications/index.xhtml'
    index_content = render.publications(me, articles, books, chapters).__str__()
    write_file(index_filename, index_content)

    # iterate through pubs
    for article in articles:
        # write out article files
        artcount += 1
        filename = basedir + get_relative_uri(article.resUri)
        content = render.article(article).__str__()
        subgraph = get_subgraph(article.resUri)
        write_file(filename + '.rdf', subgraph.serialize())
        write_file(filename + '.xhtml', content)

    for book in books:
        # write out book files
        bookcount += 1
        reluri = get_relative_uri(book.resUri)
        filename = basedir + reluri + fnappend(reluri)
        content = render.book(book).__str__()
        subgraph = get_subgraph(book.resUri)
        write_file(filename + '.rdf', subgraph.serialize())
        write_file(filename + '.xhtml', content)

    for chapter in chapters:
        # write out chapter files
        chaptercount += 1
        filename = basedir + get_relative_uri(chapter.resUri)
        content = render.chapter(chapter).__str__()
        subgraph = get_subgraph(chapter.resUri)
        write_file(filename + '.rdf', subgraph.serialize())
        write_file(filename + '.xhtml', content)

    print "    generated:"
    print "          "  + str(artcount) + " article page(s)"
    print "          "  + str(bookcount) + " book page(s)"
    print "          "  + str(chaptercount) + " chapter page(s)"

def fnappend(uri):
    """ if uri ends with a slash, return a 'index' string to append """
    if str(uri).split('/')[-1] == '':
        return 'index'
    else:
        return None


def links(basedir):
    print "generating links pages"
    links = sorted(Bookmark.ClassInstances())
    count = 0

    # create index file
    index_filename = basedir + '/links/index.xhtml'
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

if __name__ == "__main__":
    main()
