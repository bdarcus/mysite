# MySite

This is a personal website application designed for my own use as 
a scholar and teacher who has to manage a lot of disparate 
information. As a result, I wanted a struuctured foundation that 
was nevertheless flexible. To wit, the data model is RDF, and the 
content is served up using a combination of RDFAlchemy and web.py. 
Adding new objects just involves adding a URL mapping and a template.

To run, create a config.py file similar to the config.py.sample, 
and do:

	python application.py


## Requirements

* RDFLib
* RDFAlchemy
* web.py (0.3 dev version)

