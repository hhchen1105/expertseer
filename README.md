ExpertSeers
===========
ExpertSeers is a generic framework for expert recommendation based on a digital
library.  Given a query term *q*, ExpertSeers recommends experts of *q* by
retrieving authors who published relevant papers of a certain quality.
ExpertSeers is domain independent. It can be applied to different disciplines
and applications because it is automated and not tailored to a specific
discipline. 

We apply the framework to build CSSeers, an expert recommender systems based on
the CiteSeerX digital library and recommends experts in computer science.  Visit
http://csseers.ist.psu.edu/ to see the demonstration.


Authors
=======
Hung-Hsuan Chen (hhchen@psu.edu)


Required software/packages
==========================
1 Python 2.6+<br>
2 MySQL Server 5.1+<br>
3 Django 1.4+<br>
4 Python libraries:<br>
  a. python-gflags http://code.google.com/p/python-gflags/<br>
  b. python-wikitools http://code.google.com/p/python-wikitools/<br>
  c. solrpy http://code.google.com/p/solrpy/<br>
  d. lxml http://lxml.de/<br>
5 Apache Solr 3.6.2 (a tgz file of Apache Solr 3.6.2 is included in the project
root)
