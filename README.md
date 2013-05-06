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
<ol type="1">
  <li>Python 2.6+<br>
  <li>MySQL Server 5.1+</li>
  <li>Django 1.4+</li>
  <li>Python libraries:</li>
  <ol type="a">
    <li>Python-gflags http://code.google.com/p/python-gflags/</li>
    <li>python-wikitools http://code.google.com/p/python-wikitools/</li>
    <li>solrpy http://code.google.com/p/solrpy/</li>
    <li>lxml http://lxml.de/</li>
  </ol>
  <li>Apache Solr 3.6.2 (a tgz file of Apache Solr 3.6.2 is included in the
  project root)</li>
</ol>


