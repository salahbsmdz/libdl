.. libdl documentation master file, created by
   sphinx-quickstart on Sat Jun 11 21:23:30 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to libdl's documentation!
=================================

.. toctree::
   :maxdepth: 2

   reference/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

What is libdl?
==============
libdl is a download library for HTTP(S) URLs.

Install
=======
.. code-block:: bash

   pip install libdl

Usage
=====
.. code-block:: python

   import libdl
   dlengine = libdl.DownloadEngine()
   download = dlengine.create_download('https://www.example.com/', 'path/to/dir/', 'example.html')
   print(download.dir)
   # path/to/dir/
   print(download.filename)
   # example.html
   print(download.path)
   # path/to/dir/example.html
   print(download.filesize)
   # 648
   download.run() # Start download
