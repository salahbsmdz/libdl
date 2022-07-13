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
   # /home/user/path/to/dir/example.html
   print(download.filesize)
   # 648
   download.run() # Start download
