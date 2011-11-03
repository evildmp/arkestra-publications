#app = publications

import models
from django.contrib import admin
from django import forms

# for the WYMeditor fields
from arkestra_utilities.widgets.wym_editor import WYMEditor

from arkestra_utilities.mixins import AutocompleteMixin


class ResearcherForm(forms.ModelForm):
    class Meta:
        model = models.Researcher
    research_synopsis = forms.CharField(widget=WYMEditor, required=False)
    research_description = forms.CharField(widget=WYMEditor, required=False)
    def clean(self):
        if self.cleaned_data["symplectic_access"] and self.cleaned_data["person"]:
            person = self.cleaned_data["person"]
            if not person.surname or person.surname == '':
                raise forms.ValidationError("Symplectic will not allow access until this Researcher has a Surname")
            if not person.institutional_username or person.institutional_username  == '':
                raise forms.ValidationError("Symplectic will not allow access until this Researcher has a Username")
            if not person.email or person.email  == '':
                raise forms.ValidationError("Symplectic will not allow access until this Researcher has an email address")
        return self.cleaned_data

    
class ResearcherAdmin(AutocompleteMixin, admin.ModelAdmin):
    actions = None
    fieldsets = (
        ('Person', {
            'fields': ('person', ),            
        },),    
        ('Research', {
            'fields': ('publishes', 'research_synopsis', 'research_description', ),            
        },),
        ('Symplectic (Advanced Options)', {
            'fields': ('symplectic_access', 'symplectic_id', ),            
            'classes': ('xcollapsed',),
        },),        
    )  
    list_display = ('person', 'publishes', 'symplectic_access',)
    list_editable = ('publishes', 'symplectic_access',)
    list_filter = ('publishes', 'symplectic_access',)
    form = ResearcherForm
    ordering = ('person__surname',)
    search_fields = ('person__surname', 'person__given_name', 'person__institutional_username',)    
    related_search_fields = {
        'person': ('surname', 'given_name',),
    }    
    def formfield_for_dbfield(self, db_field, **kwargs):
        return ForeignKeySearchInput.overridden_formfield_for_dbfield(self, db_field, ResearcherAdmin, **kwargs) 

    class Media:
        js = (
            '/media/javascript/jquery/jquery.js',
            '/media/javascript/jquery/ui/ui.core.js',
            '/media/javascript/jquery/ui/ui.tabs.js',
        )
admin.site.register(models.Researcher, ResearcherAdmin)
    

    
class ResearcherInlineForm(forms.ModelForm):
    class Meta:
        model = models.Researcher
    research_synopsis = forms.CharField(widget=WYMEditor, required=False)
    research_description = forms.CharField(widget=WYMEditor, required=False)

class ResearcherInline(admin.StackedInline):
    fieldsets = (
        ('Research', {
            'fields': ('publishes', 'research_synopsis', 'research_description', ),            
        },),     
    )    
    form = ResearcherInlineForm    
    model = models.Researcher
    template = "admin/publications/edit_inline/single_stacked.html"        
