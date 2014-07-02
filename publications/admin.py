#app = publications

import models
from django.contrib import admin
from django import forms

from django.core import urlresolvers

from widgetry.tabs.placeholderadmin import ModelAdminWithTabsAndCMSPlaceholder

from arkestra_utilities.admin_mixins import AutocompleteMixin, ButtonLinkWidget

from contacts_and_people.admin import PersonAdmin
from contacts_and_people.models import Person


class ResearcherForm(forms.ModelForm):
    class Meta:
        model = models.Researcher
    # research_synopsis = forms.CharField(widget=WYMEditor, required=False)
    # research_description = forms.CharField(widget=WYMEditor, required=False)

    def clean(self):
        if self.cleaned_data["symplectic_access"] and \
                self.cleaned_data["person"]:
            person = self.cleaned_data["person"]
            if not person.surname or person.surname == '':
                raise forms.ValidationError("""
                    Symplectic will not allow access until this Researcher has
                    a Surname
                    """)
            if not person.institutional_username or \
                    person.institutional_username == '':
                raise forms.ValidationError("""
                    Symplectic will not allow access until this Researcher has
                    a Username
                    """)
            if not person.email or person.email == '':
                raise forms.ValidationError("""
                    Symplectic will not allow access until this Researcher has
                    an email address
                    """)
        return self.cleaned_data


class ResearcherAdmin(AutocompleteMixin, ModelAdminWithTabsAndCMSPlaceholder):
    def _media(self):
        return super(
            AutocompleteMixin,
            self).media + super(
            ModelAdminWithTabsAndCMSPlaceholder,
            self).media
    media = property(_media)

    actions = None
    basic_fieldset = [None, {'fields': ['publishes']}]
    synopsis_fieldset = ['Brief synopsis of research', {
        'fields': ['synopsis'],
        'classes': ['plugin-holder', 'plugin-holder-nopage']
    }]
    description_fieldset = ['Fuller research description', {
        'fields': ['description'],
        'classes': ['plugin-holder', 'plugin-holder-nopage']
        }]
    advanced_fieldset = ['Symplectic [Advanced Options]', {
        'fields': ['symplectic_access', 'symplectic_id', 'person'],
        'classes': ['xcollapsed'],
        }]

    tabs = [
        ['Research', {'fieldsets': [
            basic_fieldset, synopsis_fieldset, description_fieldset
            ]}],
        ['Advanced Options', {'fieldsets': [advanced_fieldset]}],
        ]

    # readonly_fields=["person",]
    list_display = ('person', 'publishes', 'symplectic_access')
    list_editable = ('publishes', 'symplectic_access')
    list_filter = ('publishes', 'symplectic_access')
    form = ResearcherForm
    ordering = ('person__surname',)
    search_fields = (
        'person__surname',
        'person__given_name',
        'person__institutional_username'
    )
    related_search_fields = {'person': ('surname', 'given_name')}


admin.site.register(models.Researcher, ResearcherAdmin)


class SupervisionInline(AutocompleteMixin, admin.TabularInline):
    model = models.Supervision
    search_fields = [
        'researcher__person__surname',
        'researcher__person__given_name'
    ]
    # it doesn't seem to be necessary to specify the search fields:
    related_search_fields = {
        "student": [],
        "supervisor": [],
    }


class SupervisionAdmin(AutocompleteMixin, admin.ModelAdmin):
    model = models.Supervision
    search_fields = [
        'student__researcher__person__surname',
        'student__researcher__person__given_name',
        'supervisor__researcher__person__surname',
        'supervisor__researcher__person__given_name'
        ]
    list_display = ['student', 'supervisor']
    # it doesn't seem to be necessary to specify the search fields:
    related_search_fields = {
        'student': [],
        'supervisor': []
        }

# this admin class is not registered - here for debugging convenience
# admin.site.register(models.Supervision, SupervisionAdmin)


class StudentAdmin(AutocompleteMixin, admin.ModelAdmin):
    search_fields = (
        'researcher__person__surname',
        'researcher__person__given_name',
        'researcher__person__institutional_username'
        )
    related_search_fields = {'researcher': ('surname', 'given_name')}
    inlines = [SupervisionInline]


admin.site.register(models.Student, StudentAdmin)


class SupervisorAdmin(AutocompleteMixin, admin.ModelAdmin):
    search_fields = (
        'researcher__person__surname', 'researcher__person__given_name',
        'researcher__person__institutional_username'
        )
    related_search_fields = {'researcher': ('surname', 'given_name')}
    inlines = [SupervisionInline]

admin.site.register(models.Supervisor, SupervisorAdmin)


class ResearcherInlineForm(forms.ModelForm):

    class Meta:
        model = models.Researcher

    # a button to link to admin:publications_researcher_change for this person
    buttonlink = forms.Field(
        widget=ButtonLinkWidget,
        required=False,
        label="Research profile",
        help_text="""
            Once this Person has been saved, research-related information can
            be edited.
            """)

    # and put some values on the button
    def __init__(self, *args, **kwargs):
        super(ResearcherInlineForm, self).__init__(*args, **kwargs)
        # Set the form fields based on the model object
        if self.instance.pk:
            instance = kwargs['instance']

            fields = urlresolvers.reverse(
                'admin:publications_researcher_change',
                args=[instance.person.id]
            )
            self.fields["buttonlink"].widget.attrs["link"] = fields

            text = "Edit %s's research profile" % unicode(instance.person)
            self.initial['buttonlink'] = text

            help_text = "Edit research-related information in a new window."
            self.fields["buttonlink"].help_text = help_text


class ResearcherInline(admin.StackedInline):
    def __init__(self, attrs=None, *args, **kwargs):
        super(ResearcherInline, self).__init__(attrs, *args, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):

        # first test to see if the Person is also a Researcher
        try:
            researcher = obj.researcher
        # can't get researcher?
        except (models.Researcher.DoesNotExist, AttributeError):
            # then remove the buttonlink if it's present
            if 'buttonlink' in self.fields:
                self.fields.remove("buttonlink")
        # but if we can get a researcher
        else:
            # researcher.publishes but no buttonlink? add a buttonlink
            if not 'buttonlink' in self.fields and researcher.publishes:
                self.fields.append('buttonlink')
            # researcher doesn't publish, but there is a buttonlink hanging
            # around? delete it
            elif 'buttonlink' in self.fields and not obj.researcher.publishes:
                self.fields.remove("buttonlink")
        formset = super(ResearcherInline, self).get_formset(
            request, obj=None, **kwargs
            )

        return formset

    fields = ['publishes']
    form = ResearcherInlineForm
    model = models.Researcher


# unregister and then re-register the PersonAdmin, to accommodate our messing
# about above
admin.site.unregister(Person)
PersonAdmin.tabs.append(('Research', {'inlines': [ResearcherInline]}))
admin.site.register(Person, PersonAdmin)
