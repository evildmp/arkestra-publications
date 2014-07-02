import unicodecsv

from django.conf import settings
import django.shortcuts as shortcuts
from django.template import RequestContext

from contacts_and_people.models import Person, Membership
from arkestra_utilities.views import ArkestraGenericView
from arkestra_utilities.generic_lister import ArkestraGenericLister
from arkestra_utilities.settings import MULTIPLE_ENTITY_MODE

from models import Researcher, Student, Supervision, Supervisor
from lister import PublicationsLister, PublicationsArchiveList
from forms import (
    StudentFormset, SupervisorFormset, DocumentForm, csv_to_list,
    convert_to_formset, process_formset
    )


class PublicationsView(ArkestraGenericView):
    # really could get this from menu_dict
    auto_page_attribute = "auto_publications_page"

    def get(self, request, *args, **kwargs):
        self.get_entity()
        self.lister = PublicationsLister(
            entity=self.entity,
            request=self.request,
            favourites_only=True,
            limit_to=10,
            item_format="details kind"
            )

        self.main_page_body_file = "arkestra/generic_lister.html"
        self.meta = {"description": "Latest key publications"}
        self.title = unicode(self.entity) + u" latest publications"
        if MULTIPLE_ENTITY_MODE:
            self.pagetitle = unicode(self.entity) + u" latest publications"
        else:
            self.pagetitle = "Latest key publications"

        return self.response(request)


class PublicationsArchiveView(ArkestraGenericView):
    auto_page_attribute = "auto_publications_page"

    def get(self, request, *args, **kwargs):
        self.get_entity()

        self.lister = ArkestraGenericLister(
            entity=self.entity,
            request=self.request,
            favourites_only=False,
            listkinds=[("publications", PublicationsArchiveList)],
            display="publications",
            item_format="details kind"
            )

        self.main_page_body_file = "arkestra/generic_filter_list.html"
        self.meta = {"description": "Searchable archive of publications items"}
        self.title = u"Archive of publications for %s" % unicode(self.entity)
        self.pagetitle = u"Archive of publications for %s" % unicode(
            self.entity
            )
        return self.response(request)


from django.contrib.auth.models import Group


from django.contrib.auth.decorators import user_passes_test


def can_upload_students(user):
    upload_group, c = Group.objects.get_or_create(name="Can upload students")
    return upload_group in user.groups.all()


@user_passes_test(can_upload_students)
def upload_students(request):

    # empty defaults
    uploaded_document = None
    student_formset = StudentFormset(prefix="student")
    upload_form = DocumentForm()
    supervisor_formsets = [SupervisorFormset(
        prefix="%s-supervisor" % student.prefix
        ) for student in student_formset]

    if request.method == 'POST':
        # we're receiving the uploaded file
        if request.POST.get("upload"):
            upload_form = DocumentForm(request.POST, request.FILES)

            # receive the CSV file
            if upload_form.is_valid():
                uploaded_document = request.FILES['docfile']
                uploaded_document.rows = unicodecsv.DictReader(
                    uploaded_document,
                    errors="replace"
                )

                # get a list of unique students from the uploaded document
                unique_students = csv_to_list(uploaded_document.rows)

                # build a formset for each one
                unique_students, student_formset = convert_to_formset(
                    unique_students
                    )

                # and for each one a formset of supervisors
                student_formset, supervisor_formsets = process_formset(
                    unique_students, student_formset
                    )

        # we're processing the uploaded file
        if request.POST.get("reprocess"):

            student_formset = StudentFormset(
                request.POST,
                request.FILES,
                prefix="student"
                )

            # there will be a supervisor_formset for each student
            supervisor_formsets = []

            # make a mutable copy of the formset data
            student_formset.data = student_formset.data.copy()

            # loop over students
            for student in student_formset:

                # create the supervisor_formset for this student
                # the prefix matches the prefixes in the form, so that the
                # correct supervisors can be matched to the student
                supervisor_formset = SupervisorFormset(
                    request.POST, request.FILES,
                    prefix="%s-supervisor" % student.prefix
                    )

                # make the supervisor_formset available on the student form for
                # processing in forms.py, and likewise the student form on the
                # supervisor_formset
                student.supervisor_formset = supervisor_formset
                supervisor_formset.student = student

                # make a mutable copy of the formset data
                supervisor_formset.data = supervisor_formset.data.copy()

                for supervisor in supervisor_formset:
                    supervisor.is_valid()

                    for k, v in supervisor.cleaned_data.items():
                        supervisor_formset.data[
                            supervisor.prefix + "-" + k
                        ] = v

                # rebind the data to the formset
                supervisor_formset = SupervisorFormset(
                    supervisor_formset.data,
                    prefix="%s-supervisor" % student.prefix
                )

                # add this supervisor_formset to the list of formsets
                supervisor_formsets.append(supervisor_formset)

                # check the supervisors
                supervisor_formset.is_valid()

                # student.is_ready_to_save() calls is_valid() on both the
                # student form and the supervisor formset
                ready_to_save = student.is_ready_to_save()

                if ready_to_save and student.cleaned_data.get("confirm"):

                    cleaned_data = student.cleaned_data

                    # if the Person is provided in form, great - if not, we
                    # have to create a new one based on the name provided
                    person = cleaned_data.get("person")

                    if not person:
                        given_name = cleaned_data["given_name"]
                        surname = cleaned_data["surname"]
                        slug = cleaned_data["slug"]
                        email = cleaned_data["email"]
                        institutional_username = cleaned_data["username"]

                        person = Person(
                            given_name=given_name,
                            surname=surname,
                            slug=slug,
                            email=email,
                            institutional_username=institutional_username,

                            active=True,

                        )
                        person.save()
                        cleaned_data["person"] = person

                    # get or create a Researcher for the Person
                    researcher, created = Researcher.objects.get_or_create(
                        person=person,
                        defaults={'publishes': True}
                        )

                    # get or create a Student for the Researcher
                    stud, created = Student.objects.get_or_create(
                        researcher=researcher,
                        defaults={
                            "student_id": cleaned_data["student_id"],
                            "thesis": cleaned_data["thesis"],
                            "programme": cleaned_data["programme"],
                            "start_date": cleaned_data["start_date"],
                        }
                    )

                    entity = cleaned_data["entity"]

                    # create the Student's Membership
                    m = Membership(
                        person=person,
                        entity=entity,
                        role="%s student" % cleaned_data["programme"],
                        importance_to_person=5
                    )
                    m.save()

                    # if the Student was created, we'll add the supervisors
                    if created:

                        # loop over the supervisor forms that have data
                        for s in [
                            s for s in supervisor_formset if s.cleaned_data
                        ]:

                            supervisor = s.cleaned_data["person"]

                            if not supervisor:
                                s_given_name = s.cleaned_data["given_name"]
                                s_surname = s.cleaned_data["surname"]
                                s_slug = s.cleaned_data["slug"]
                                s_entity = s.cleaned_data["entity"]

                                supervisor = Person(
                                    given_name=s_given_name,
                                    surname=s_surname,
                                    active=True,
                                    slug=s_slug
                                )
                                supervisor.save()
                                s.cleaned_data["person"] = supervisor
                                # create the Supervisor's Membership

                                m = Membership(
                                    person=supervisor,
                                    entity=s_entity,
                                    importance_to_person=5
                                )
                                m.save()

                            # get or create a Researcher for the Person
                            researcher, c = Researcher.objects.get_or_create(
                                person=supervisor
                            )

                            # get or create an Supervisor for each Researcher
                            supervisor, c = Supervisor.objects.get_or_create(
                                researcher=researcher,
                                )

                            # get or create a Supervision relationship for each
                            supervision, c = Supervision.objects.get_or_create(
                                supervisor=supervisor,
                                student=stud
                                )

                for k, v in student.cleaned_data.items():
                    student_formset.data[student.prefix + "-" + k] = v

            # rebind the data to the formset
            student_formset = StudentFormset(
                student_formset.data, prefix="student"
            )

    zipped_formsets = zip(student_formset, supervisor_formsets)

    for (student_form, supervisor_formset) in zipped_formsets:
        student_form.supervisor_formset = supervisor_formset
        # supervisor_formset.student_form = student_form

    # print "zipped length:", len(zipped_formsets)
    return shortcuts.render_to_response(
        'upload/students.html', {
            "base_template": settings.CMS_TEMPLATES[0][0],
            "upload_form": upload_form,
            "document": uploaded_document,
            "student_formset": student_formset,
            "zipped_formsets": zipped_formsets
        },
        RequestContext(request)
        )


from django.http import HttpResponse
from models import BibliographicRecord


def csv_dump(request, year):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="publications.csv"'

    attrs = [
        "authors",
        "title",
        "publication_date",
        "journal",
        "volume"
        ]

    pubs = BibliographicRecord.objects.filter(publication_date__contains=year)

    writer = unicodecsv.writer(response)

    writer.writerow([attr for attr in attrs])

    for pub in pubs:
        writer.writerow([getattr(pub, attr) for attr in attrs])

    return response
