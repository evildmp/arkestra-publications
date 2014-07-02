from operator import itemgetter
from itertools import izip_longest

from django import forms
from django.forms.util import ErrorDict
from django.forms.formsets import BaseFormSet
from django.template.defaultfilters import slugify

from contacts_and_people.models import Person, Entity

from models import Student

import autocomplete_light


class PersonAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['given_name', 'surname']
    limit_choices = 1000


class EntityAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name', 'short_name']
    choices = Entity.objects.filter(abstract_entity=False)
    limit_choices = 1000


autocomplete_light.register(Person, PersonAutocomplete)
autocomplete_light.register(Entity, EntityAutocomplete)


class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text="""
        Upload a CSV file. Required column headings are: student_id, surname,
        given_name, email, username, programme, entity, start_date, thesis,
        supervisor_title, supervisor_surname, supervisor_given_name
        """
    )


class PersonFormMixin(forms.Form):
    person = forms.ModelChoiceField(
        Person.objects.all(),
        widget=autocomplete_light.ChoiceWidget(
            'PersonAutocomplete',
            attrs={
                'size': '40',
                'placeholder': 'Select existing person'
                },
            ),
        required=False,
        )
    given_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Given name'}),
    )
    surname = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Surname'}),
    )
    entity = forms.ModelChoiceField(
        Entity.objects.all(),
        required=False,
        widget=autocomplete_light.ChoiceWidget(
            'EntityAutocomplete',
            attrs={
                'size': '10',
                'placeholder': 'Select entity'
                },
            ),
        )
    slug = forms.SlugField(
        max_length=60,
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': '20',
                'placeholder': 'Slug'
                },
            )
        )
    create = forms.BooleanField(
        required=False,
        )

    def has_name(self):
        return self.cleaned_data.get("surname") and \
            self.cleaned_data.get("given_name")

    def is_ready(self):
        if self.is_valid():
            create = self.cleaned_data.get("create")
            person = self.cleaned_data.get("person")
            return create or person

    def requires_confirmation(self):
        # can be created if:
        #   given_name, surname and slug are OK
        #   no Person is selected

        if self.is_valid():
            if self.cleaned_data.get("person"):
                return

            return self.has_name() and self.cleaned_data.get("slug")

    def is_blank(self):
        return self.is_valid() and not self.cleaned_data

    def status(self):
        if self.is_ready():
            return "ready"
        elif self.requires_confirmation():
            return "requires-confirmation"
        elif self.is_blank():
            return "blank"
        elif not self.is_valid():
            return "invalid"
        else:
            print "************ error ************"

    def clean(self):
        cleaned_data = super(PersonFormMixin, self).clean()
        person = self.cleaned_data.get("person")
        given_name = self.cleaned_data.get("given_name")
        surname = self.cleaned_data.get("surname")
        slug = self.cleaned_data.get("slug")
        entity = self.cleaned_data.get("entity")

        # if the Person has been selected, fine; if not, try to find the
        # matching person from Persons
        if not person:
            existing_people = Person.objects.filter(
                given_name=given_name,
                surname=surname,
                )
            matches = existing_people.count()
            if existing_people.count() == 0:
                self.initial["matches"] = "No matches for name '%s %s'" % (
                    given_name, surname
                    )
            elif existing_people.count() == 1:
                # since there is only one match, pre-fill the researcher
                # field
                person = existing_people[0]
            elif existing_people.count() > 1:
                self.initial["matches"] = "Name '%s %s' matches %s Persons" % (
                    given_name, surname, matches
                    )

            self.cleaned_data["person"] = person

        if person or (given_name and surname and slug and entity):
            return cleaned_data
        else:

            raise forms.ValidationError("""
                Select a Person, or complete all fields to create a new Person
                """)
        return cleaned_data

    def clean_given_name(self):
        person = self.cleaned_data.get("person")
        given_name = self.cleaned_data.get("given_name")
        if not person and not given_name:
            raise forms.ValidationError("Required")
        return given_name

    def clean_surname(self):
        person = self.cleaned_data.get("person")
        surname = self.cleaned_data.get("surname")
        if not person and not surname:
            raise forms.ValidationError("Required")
        return surname

    def clean_slug(self):
        person = self.cleaned_data.get("person")
        slug = self.cleaned_data.get("slug")

        given_name = self.cleaned_data.get("given_name")
        surname = self.cleaned_data.get("surname")

        name = " ".join([np for np in [given_name, surname] if np])

        if person:
            pass

        else:
            slug = slug or slugify(name)

        return slug

    def clean_email(self):
        person = self.cleaned_data.get("person")
        email = self.cleaned_data.get("email")
        if not person and not email:
            raise forms.ValidationError("Required")
        return email

    def clean_username(self):
        person = self.cleaned_data.get("person")
        username = self.cleaned_data.get("username")
        if not person and not username:
            raise forms.ValidationError("Required")
        return username

    def clean_entity(self):
        person = self.cleaned_data.get("person")
        entity = self.cleaned_data.get("entity")
        if not person and not entity:
            raise forms.ValidationError("Required")
        return entity


class SupervisorInlineForm(PersonFormMixin, forms.Form):

    def full_clean(self):
        """
        Cleans all of self.data and populates self._errors and
        self.cleaned_data.
        """
        self._errors = ErrorDict()
        if not self.is_bound:  # Stop further processing.
            return
        self.cleaned_data = {}
        # If the form is permitted to be empty, and none of the form data has
        # changed from the initial data, short circuit any validation.
        if self.empty_permitted and not self.has_changed():
            return

        self._clean_fields()
        self._clean_form()
        self._post_clean()


class BaseSupervisorFormset(BaseFormSet):
    def clean(self):

        super(BaseSupervisorFormset, self).clean()
        # if there are any errors, give up right now
        if any(self.errors):
            return

        # how many supervisor forms?
        f = [
            form for form in self.forms if form.is_valid()
            and form.cleaned_data.get("supervisor")
            ]

        if form.cleaned_data.get("surname") and len(f) < 1:
            raise forms.ValidationError(
                "A student must have at least one supervisor."
                )


SupervisorFormset = forms.formsets.formset_factory(
    SupervisorInlineForm,
    formset=BaseSupervisorFormset
    )


class StudentForm(PersonFormMixin, forms.Form):
    email = forms.EmailField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Email address',
            'size': '8'
            }
        ),
    )
    username = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'placeholder': 'Start date yyyy-mm-dd',
            'size': '25',
            }
        ),
        input_formats=[
            '%Y-%m-%d',       # '2006-10-25'
            '%d/%m/%Y',       # '25/10/2006'
            '%d/%m/%y',       # '25/10/06'
            '%b %d %Y',       # 'Oct 25 2006'
            '%b %d, %Y',      # 'Oct 25, 2006'
            '%d %b %Y',       # '25 Oct 2006'
            '%d %b, %Y',      # '25 Oct, 2006'
            '%B %d %Y',       # 'October 25 2006'
            '%B %d, %Y',      # 'October 25, 2006'
            '%d %B %Y',       # '25 October 2006'
            '%d %B, %Y'],     # '25 October, 2006'
    )
    student_id = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'size': '8',
                'placeholder': 'Student ID'
            },
        )
    )
    programme = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'size': '20',
                'placeholder': 'Programme'
                },
            )
        )
    thesis = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': '1',
                'placeholder': 'Thesis title'
            })
        )
    confirm = forms.BooleanField(
        required=False,
        help_text="Save student and supervisors to the database."
        )

    def all_status(self):
        if self.already_exists():
            return "all-already-exists"
        items = [s for s in self.supervisor_formset] + [self]
        if not all([s.is_valid() for s in items]):
            return "all-invalid"
        elif self.is_ready_to_save():
            return "all-ready"
        elif any([s.requires_confirmation() for s in items]):
            return "all-requires-confirmation"

    def check_memberships(self):
        if self.is_valid() and not self.already_exists():
            person = self.cleaned_data.get("person")
            entity = self.cleaned_data.get("entity")
            if person:
                return person.member_of.filter(entity=entity)

    def already_exists(self):
        if self.is_valid():
            student_id = self.cleaned_data.get("student_id")
            if Student.objects.filter(student_id=student_id):
                return True

    def is_ready_to_save(self):

        if (
            self.is_valid() and self.cleaned_data and
            self.supervisor_formset.is_valid() and not self.already_exists()
        ):
            items = [self] + [s for s in self.supervisor_formset]
            return all([s.is_ready() for s in items if s.cleaned_data])

    def clean_entity(self):
        entity = self.cleaned_data.get("entity")
        if not entity:
            raise forms.ValidationError("Required")
        return entity

    def full_clean(self):
        """
        Cleans all of self.data and populates self._errors and
        self.cleaned_data.
        """
        self._errors = ErrorDict()
        if not self.is_bound:  # Stop further processing.
            return
        self.cleaned_data = {}
        # If the form is permitted to be empty, and none of the form data has
        # changed from the initial data, short circuit any validation.
        if self.empty_permitted and not self.has_changed():
            return

        self._clean_fields()
        self._clean_form()
        self._post_clean()


def csv_to_list(rows):

    # convert it into a list of rows for processing
    rows = list(rows)
    students = {}

    # have unique student_ids
    # a student with multiple supervisors will appear multiple times
    # in the file, so we need to reconcile those student rows
    students = {}

    for row in [row for row in rows if row]:
        # each row gets a unique key
        key = row["student_id"]

        # bundle up the supervisor fields
        supervisor_dict = {
            "title": row.get("supervisor_title"),
            "surname": row.get("supervisor_surname"),
            "given_name": row.get("supervisor_given_name"),
            "position": row.get("supervisor_position")
            }

        # if the student already exists, append the supervisor
        if key in students:
            student = students[key]
            if supervisor_dict not in student["supervisor_list"]:
                student["supervisor_list"].append(supervisor_dict)

        # if not, create a new student with that supervisor
        else:
            student = row.copy()
            student["supervisor_list"] = [supervisor_dict]
            students[key] = student

        student["no_of_supervisors"] = len(student["supervisor_list"])

    return students
    # make a list of unique students
    unique_students = students.values()

    return unique_students


def convert_to_formset(unique_students):
    # make a list of unique students, ordered by surname
    unique_students = sorted(
        unique_students.values(),
        key=itemgetter('surname', 'given_name')
        )

    for student in unique_students:
        # first, try to match the student

        # # see if we can match student_id
        # try:
        #     existing_student = Student.objects.get(
        #         student_id=student["student_id"]
        #         )
        #     student["person"] = existing_student
        #
        # except Student.DoesNotExist:
        #
        #     # if that doesn't work, try by name
        #     # check how many matches to existing Person there are for
        #     # each student
        #     existing_students = Person.objects.filter(
        #         surname=student["surname"],
        #         given_name=student["given_name"],
        #         )
        #     if existing_students.count() == 0:
        #         student["matches"] = "No matching Persons found"
        #     elif existing_students.count() == 1:
        #         student["matches"] = "One matching Person found"
        #         # since there is only one match, pre-fill the person field
        #         student["person"] = existing_students[0]
        #
        #     elif existing_students.count() > 1:
        #         student["matches"] = "Multiple matching Persons found"

        # do we have an actual entity saved already?
        if type(student["entity"]) is not Entity:

            # check if the entity matches one from the database
            entities = Entity.objects.filter(
                abstract_entity=False,
                short_name=student["entity"]
                )

            # if there is only one match, pre-fill the entity field
            if entities.count() == 1:
                student["entity"] = entities[0]
            else:
                student["entity"] = None

    student_formset = StudentFormset(initial=unique_students, prefix="student")

    return unique_students, student_formset


def process_formset(unique_students, student_formset):

    supervisor_formsets = []

    for (student, student_form) in izip_longest(
        unique_students, student_formset, fillvalue={}
    ):

        # now we create a formset for each student, containing the
        # supervisors
        student["supervisors"] = student.get("supervisors") or []
        student["supervisor_list"] = student.get("supervisor_list") or []

        supervisor_formset = SupervisorFormset(
            initial=student["supervisor_list"],
            prefix="%s-supervisor" % student_form.prefix
            )

        student_form.supervisor_formset = supervisor_formset

        # student["supervisor_formset"] = supervisor_formset
        supervisor_formsets.append(supervisor_formset)

    return student_formset, supervisor_formsets


class BaseStudentFormset(BaseFormSet):
    pass


StudentFormset = forms.formsets.formset_factory(
    StudentForm,
    formset=BaseStudentFormset
    )
