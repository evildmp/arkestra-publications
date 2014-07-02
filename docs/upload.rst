==========================================================
Uploading and entering information about research students
==========================================================

Arkestra Publications allows you to upload information about large numbers of
research students, or to enter information about them by hand, using a form
that makes it much faster and easier to do so than it would by using the
standard admin interface.

Access to the form
==================

The form is available at `/upload-students` - for example if your site's URL is
http://medicine.cf.ac.uk, the form will be at
http://medicine.cf.ac.uk/upload-students.

Access to the form requires permissions to be set appropriately. Only users who
are members of the Auth Group `Can upload students` will be able to use (or
even see) the form.

Using the form
==============

The form can be used in two different ways.

Uploading data
--------------

You will need a CSV file containing a row for each student-plus-supervisor.

That is, a student with two supervisors will require two lines in the file, one
for each supervisor.

Each line should have data for at least some of the following fields:

* `student_id` - must be unique for each student, and must be correct
* `surname`
* `given_name`
* `email`
* `entity` - must match the entity's `short name` in Arkestra
* `username` - the student's institutional username
* `programme` - the programme of study: PhD, MD, MRes, etc
* `start_date` - most date formats will be accepted
* `thesis` - the title of the thesis
* `supervisor_surname`
* `supervisor_given_name`

The first row in the file should list the fields above that are included.

Fields can be in any order, as long as the first row sets out the file's
data columns correctly.

It is not recommended to upload more than about 50 rows at a time, as it can
become quite slow to redisplay each time the data are reprocessed.

Upload the file. The form will now contain the raw data from the CSV file,
with each row in its own section.

Press `Reprocess students`. This will place each student into its own section,
with as many supervisors as are associated with that student.

Entering data manually
----------------------

Just complete as many fields as possible, and press `Reprocess students`. If
you're able to select an existing person from the database, there's no need to
include any additional information about them (other than details of their
studies).

Reprocessing the form
---------------------

The form will attempt to match students and supervisors with existing people in
Arkestra's database.

It's always worth checking failed matches, because although it does a
reasonable job, a mispelled or transposed name can fool it.

.. admonition::
   Always make sure that there is not an **existing** person in the system
   before asking the form to **create** that person. Take great care to avoid
   creating duplicates, which is what will happen if you fail to notice that a
   person already existed.

You can always check your data by pressing `Reprocess students`.

The colours of each student's form and its sections change to indicate their
status:

* white: blank; will be ignored
* red: incomplete or invalid
* yellow: complete, but contains a student or supervisor that needs to be
  created
* green: ready to be saved to the database
* blue: successfully processed

You will typically need to reprocess the form several times to move through all
these states; one way of looking at the task is to see it as making all the
sections proceed through the sequence `red > yellow > green > blue`.

Once a section is blue, it can't be changed any further. There is no further
processing to be done.
