What is loso?
=============

loso is a Chinese segmentation system written in Python.  It was developed by Victor Lin (bornstub@gmail.com) for Plurk Inc.

Copyright & Licnese
===================

Copyright of loso owns by Plurk Inc.  It is an open source under BSD license.

Setup loso
==========

To install loso, clone the repo and run following command

::

   cd loso
   python setup.py develop

Also, you need to run a redis_ database for storing the lexicon database. Also, you need to copy configuration template and modify it.  

::

   cp default.yaml myconf.yaml
   vim myconf.yaml

To use your configuration, you have to set the configuration environment variable LOSO_CONFIG_FILE. For example:

::

   LOSO_CONFIG_FILE=myconfig.yaml python setup.py server

.. _redis: http://redis.io/

Use loso
========

Loso determines segmentation according to the lexicon database, and the algorithm is based on Hidden Makov Model, therefore, it is not possible to use the service before building a lexicon database.

To feed a text file to the database, here you can run

::

   python setup.py feed -f /home/victorlin/plurk_src/realtime_search/word_segment/sample_data/sample_tr_ch


To clean the database, you can run

::

   python setup.py reset

To interact and test for splitting terms, here you can run

::

   python setup.py interact


For example

::

   Text: 留下鉅細靡遺的太空梭發射影片，供世人回味
   ....
   留下 鉅細靡遺 的 太空梭 發射 影片 供 世人 回味


To use the segmentation service as XMLRPC service, here you can run


::

   python setup.py serve


Following is a simple Python program for showing how to use it


.. code-block:: python

   import xmlrpclib
   
   proxy = xmlrpclib.ServerProxy("http://localhost:5566/")
   
   terms = proxy.splitTerms(u'留下鉅細靡遺的太空梭發射影片，供世人回味')
   print ' '.join(terms)

And the output should be 


::

  留下 鉅細靡遺 的 太空梭 發射 影片 供 世人 回味
