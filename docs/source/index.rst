pyrmp
=====

Python wrapper for the RateMyProfessor GraphQL API.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api

Installation
------------

.. code-block:: bash

   pip install pyrmp

Quick Start
-----------

.. code-block:: python

   from pyrmp import RateMyProfessorClient

   with RateMyProfessorClient() as client:
       teachers = client.search_teachers("John Smith")
       for teacher in teachers.items:
           print(f"{teacher.full_name} - {teacher.avg_rating}/5")

CLI
---

.. code-block:: bash

   pyrmp search "John Smith"
   pyrmp teacher "John Smith"
   pyrmp ratings "Teacher-941174"
   pyrmp schools "MIT"
