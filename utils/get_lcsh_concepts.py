
from rdflib import URIRef, ConjunctiveGraph

concepts = [
    "http://lcsh.info/sh85026205#concept", 
    "http://lcsh.info/sh98000521#concept",	
    "http://lcsh.info/sh85054192#concept",
    "http://lcsh.info/sh91005953#concept",
    "http://lcsh.info/sh99011194#concept",
    "http://lcsh.info/sh85127474#concept",
    "http://lcsh.info/sh85081863#concept",
    "http://lcsh.info/sh85081871#concept",
    "http://lcsh.info/sh85075119#concept",
    "http://lcsh.info/sh89001033#concept",
    "http://lcsh.info/sh85075801#concept",
    "http://lcsh.info/sh89001287#concept",
    "http://lcsh.info/sh85148586#concept",
    "http://lcsh.info/sh2001000147#concept",
    "http://lcsh.info/sh2002002388#concept",
    "http://lcsh.info/sh85023243#concept"
]

graph = ConjunctiveGraph()
graph.bind('skos', URIRef('http://www.w3.org/2004/02/skos/core#'))

for concept in concepts:
    print "parsing " + concept
    graph.parse(URIRef(concept))

print "\ngraph has " + str(len(graph)) + " triples."

graph.serialize('mylcsh.rdf')
