#app = publications

from django.db import models
from django.template.defaultfilters import join, date
from datetime import datetime

from contacts_and_people.models import Person, Entity

#from cms.models import CMSPlugin
CMSPlugin = models.get_model('cms', 'CMSPlugin')
from cms.models.fields import PlaceholderField

from arkestra_utilities.generic_models import ArkestraGenericPluginOptions
from arkestra_utilities.output_libraries.dates import nice_date
from arkestra_utilities.settings import ARKESTRA_DATE_FORMATS, PLUGIN_HEADING_LEVELS, PLUGIN_HEADING_LEVEL_DEFAULT



# @       @       @       @       @       @       @       @       @       @       @       @       @       @       @
#  @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @
#   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @
#    @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @
#     @       @       @       @       @       @       @       @       @       @       @       @       @       @       @


# ***********************************************************************************************************************
# *****  START: Link to contacts_and_people.Person                                                                  *****
# ***********************************************************************************************************************


class Researcher(models.Model):
  #one-to-one link to contacts_and_people.Person
    person = models.OneToOneField(
      'contacts_and_people.Person', 
      primary_key = True, related_name = "researcher", 
      help_text="Do not under any circumstances change this field. No, really. Don't touch this.",
      )
    research_synopsis = models.TextField(null = True, blank = True)
    research_description = models.TextField(blank = True, null = True)

    synopsis = PlaceholderField('body', 
        related_name="research_synopsis",
        help_text="research_synopsis")
    
    description = PlaceholderField('body', 
        related_name="research_description",
        help_text="research_description")

  #symplectic specific info
    publishes = models.BooleanField(default=False, help_text="Allows 'Research' and 'Publications' information to be edited and published", verbose_name="Is active in research and publishing",)
    
  #info used regarding symplectic user over the api
    symplectic_access = models.BooleanField(default=False, help_text="Symplectic API will be asked to allow this user access", verbose_name="Can login to Symplectic")  
    symplectic_id = models.CharField(blank=True, help_text = "Symplectic's own ID for this user to be used by API", max_length=36, null=True, verbose_name="Symplectic User ID") 
                           
    #research_brief_summary = models.TextField(null = True)
    #research_overview = models.TextField(null = True)

    def __unicode__(self):
        return self.person.__unicode__()  
        
  #return a list of authored for this researcher
    def get_authoreds(self):
        return self.authored.filter(visible = True).order_by('publication__type', 'reverse_sort_cue')
  
  #return a list of chosen bibliographic records for this researcher
    def get_all_publications(self):
        return BibliographicRecord.objects.filter(authored__visible = True, authored__researcher = self)
         
  #remove all of the "i authored this publication" records for this researcher, but leave the publications themselves alone
    def remove_all_authored(self):
        self.authored.all().delete()
          

# ***********************************************************************************************************************
# *****  FINISH: Link to contacts_and_people.Person                                                                 *****
# ***********************************************************************************************************************



# @       @       @       @       @       @       @       @       @       @       @       @       @       @       @
#  @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @
#   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @
#    @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @
#     @       @       @       @       @       @       @       @       @       @       @       @       @       @       @



# ***********************************************************************************************************************
# *****  START: Python Object of Symplectic Publication                                                             *****
# ***********************************************************************************************************************

class Publication(models.Model):

  #publication attributes
    guid = models.CharField(primary_key=True, max_length=255)
    is_deleted = models.BooleanField(default=False)
    type = models.CharField(max_length=255, null=True)
    created_when = models.TextField(null=True)
    last_modified_when = models.TextField(null=True)
  #public-dspace-handle
    public_dspace_handle = models.CharField(max_length=255, null=True)
  #does this local cached version need updating with latest symplectic version
    needs_refetch = models.BooleanField(default=True)

  #
    def __unicode__(self):
        return self.guid
        
  # DONT try to override __init__ for a model!
  

  #
    @staticmethod
    def getPublication(guid):
      try:
          publication = Publication.objects.get(guid = guid)
          return publication
      except (Publication.DoesNotExist,):
          return None
  
  #    
    @staticmethod    
    def getOrCreatePublication(guid):
      """
        Tries to load Publication with a specific guid out of database
        If not in database then creates a new empty Publication in the database with that guid
         - the empty Publication is flagged as needing to be re-fetched from symplectic
      """
      try:
          publication = Publication.objects.get(guid = guid)
          return publication
      except (Publication.DoesNotExist,):
          # NB DONT try to override __init__ for a model!
          publication = Publication()
          publication.guid = guid
          publication.needs_refetch = True
          publication.save()
          return publication
      

      
publication_kinds = {
  "book": "Monographs",
  "chapter": "Chapters",
  "journal-article": "Articles",
  "conference-proceeding": "Conference papers",
  "report": "Reports",
  "other": "Other publications",
}
  
class BibliographicRecord(models.Model):
    class Meta:
        ordering = ['-publication_date']
    

  #composite-unique id
    id = models.CharField(primary_key=True, max_length=255)

  #link a single parent publication
    publication = models.ForeignKey(
      'Publication',
      related_name='bibliographic_records',
      )

  #bibliographic-record attrib
    data_source = models.CharField(max_length=255)
    id_at_source = models.CharField(max_length=255, null=True)
  #verification
    verification_status = models.TextField(null=True)
  #urls
    # dealt with by foreign key in BiblioURL
  #bibliometric data
    times_cited = models.TextField(null=True)
    reference_count = models.TextField(null=True)
  #bibliographic data (native)
    abstract = models.TextField(null=True)
    associated_authors = models.TextField(null=True)
    authors = models.TextField(null=True)    #combined
    awarded_date = models.TextField(null=True)
    begin_page = models.TextField(null=True)
    book_author_type = models.TextField(null=True)
    commissioning_body = models.TextField(null=True)
    confidential = models.TextField(null=True)
    doi = models.TextField(null=True)
    edition = models.TextField(null=True)
    editors = models.TextField(null=True)
    end_page = models.TextField(null=True)
    filed_date = models.TextField(null=True)
    finish_date = models.TextField(null=True)
    isbn_10 = models.TextField(null=True)
    isbn_13 = models.TextField(null=True)
    issn = models.TextField(null=True)
    issue = models.TextField(null=True)
    journal = models.TextField(null=True)
    journal_article_type = models.TextField(null=True)
    keywords = models.TextField(null=True)    #combined
    language = models.TextField(null=True)
    location = models.TextField(null=True)
    medium = models.TextField(null=True)
    name_of_conference = models.TextField(null=True)
    notes = models.TextField(null=True)
    number = models.TextField(null=True)
    number_of_pages = models.TextField(null=True)
    number_of_pieces = models.TextField(null=True)
    parent_title = models.TextField(null=True)
    patent_number = models.TextField(null=True)
    patent_status = models.TextField(null=True)
    pii = models.TextField(null=True)
    place_of_publication = models.TextField(null=True)
    publication_date = models.TextField(null=True)
    publication_status = models.TextField(null=True)
    publisher = models.TextField(null=True)
    series = models.TextField(null=True)
    start_date = models.TextField(null=True)
    title = models.TextField(null=True)
    version = models.TextField(null=True)
    volume = models.TextField(null=True)
  #derived author data
    number_of_authors = models.IntegerField(default=0, null=True)
    first_author = models.TextField(null=True)
    last_author = models.TextField(null=True)
    
 
  #override __save__ to create composite primary key
    def save(self):
        if self.publication is not None:
            self.id = self.publication.guid + ':' + self.data_source
            super(self.__class__, self).save()                   
            
  #
    def __unicode__(self):
        if (self.publication is not None) and (self.data_source != ''):
            return self.publication.guid + ':' + self.data_source
        else:
            return 'Bibliography has No Publication'
            
  # DONT try to override __init__ for a model! 
 
  #return info about biblio-record
    def get_url(self):
        try:
            return self.urls.all()[0].link
        except IndexError:
            pass
            
    def get_publication_date(self):
        try:
            return date(datetime.strptime(self.publication_date, "%Y-%m-%d"), "F Y")
        except ValueError:
            try:
                return date(datetime.strptime(self.publication_date, "%Y-%m"), "F Y")
            except ValueError:
                try:
                    return date(datetime.strptime(self.publication_date, "%Y"), "Y")
                except:
                    return self.publication_date     
                    
    def get_publication_year(self):
        date = self.publication_date[:4]
        if len(date) < 4:
            return "Undated"
        else:
            return date
            
    def get_start_date(self):
        try:
            return date(datetime.strptime(self.start_date, "%Y-%m-%d"), "F Y")
        except ValueError:
            try:
                return date(datetime.strptime(self.start_date, "%Y-%m"), "F Y")
            except ValueError:
                try:
                    return date(datetime.strptime(self.start_date, "%Y"), "Y")
                except:
                    return self.start_date  
                    
    def get_start_year(self):
        date = self.start_date[:4]
        if len(date) < 4:
            return "Undated"
        else:
            return date
            
    def get_finish_date(self):
        try:
            return date(datetime.strptime(self.finish_date, "%Y-%m-%d"), "F Y")
        except ValueError:
            try:
                return date(datetime.strptime(self.finish_date, "%Y-%m"), "F Y")
            except ValueError:
                try:
                    return date(datetime.strptime(self.finish_date, "%Y"), "Y")
                except ValueError:
                    return self.finish_date 
    def template(self):
        return "includes/" + self.publication.type + ".html"
    def kind(self):
        return publication_kinds.setdefault(self.publication.type, "Other publications")
                    

    @property
    def get_when(self):
        """
        get_when provides a human-readable attribute under which items can be grouped.
        Usually, this is an easily-readble rendering of the date (e.g. "April 2010") but it can also be "Top news", for items to be given special prominence.
        """
        get_when = nice_date(self.get_start_date(), ARKESTRA_DATE_FORMATS["date_groups"])
        return get_when

  # #citation
    # def cite(self):
        # if self.publication is not None:
            # if self.publication.type == '':
                # return ''
            # elif self.publication.type == 'book':
                # return BibliographicRecord.__tidyCiteField(self.authors, ' ') + \
                       # BibliographicRecord.__tidyCiteField(BibliographicRecord.__extractYear(self.publication_date), ') ', ' (') + \
                       # BibliographicRecord.__tidyCiteField(self.title, '. ') + \
                       # BibliographicRecord.__tidyCiteField(self.edition, '. ') + \
                       # BibliographicRecord.__tidyCiteField(self.place_of_publication, ', ') + \
                       # BibliographicRecord.__tidyCiteField(self.publisher, '.')
            # elif self.publication.type == 'chapter':
                # return BibliographicRecord.__tidyCiteField(self.authors, ' ') + \
                       # BibliographicRecord.__tidyCiteField(BibliographicRecord.__extractYear(self.publication_date), ') ', ' (') + \
                       # BibliographicRecord.__tidyCiteField(self.title, '. ') + \
                       # 'in ' + \
                       # BibliographicRecord.__tidyCiteField(self.editors, ' ') + \
                       # BibliographicRecord.__tidyCiteField(self.book_title, '. ') + \
                       # BibliographicRecord.__tidyCiteField(self.place_of_publication, ', ') + \
                       # BibliographicRecord.__tidyCiteField(self.publisher, ', ') + \
                       # BibliographicRecord.__tidyCiteField(self.begin_page, '-', 'pp ') + \
                       # BibliographicRecord.__tidyCiteField(self.end_page, '.')
            # elif self.publication.type == 'conference-proceeding':
                # return BibliographicRecord.__tidyCiteField(self.name_of_conference, ', ') + \
                       # BibliographicRecord.__tidyCiteField(BibliographicRecord.__extractYear(self.start_date), '. ') + \
                       # BibliographicRecord.__tidyCiteField(self.location, ', ') + \
                       # BibliographicRecord.__tidyCiteField(BibliographicRecord.__extractYear(self.publication_date), '). ', ' (') + \
                       # BibliographicRecord.__tidyCiteField(self.title, ', ') + \
                       # BibliographicRecord.__tidyCiteField(self.authors, '. ') + \
                       # BibliographicRecord.__tidyCiteField(self.place_of_publication, ', ') + \
                       # BibliographicRecord.__tidyCiteField(self.publisher, '.')   
            # elif self.publication.type == 'CONFERENCE-PAPER':
                # return BibliographicRecord.__tidyCiteField(self.authors, ' ') + \
                       # BibliographicRecord.__tidyCiteField(BibliographicRecord.__extractYear(self.publication_date), ') ', ' (') + \
                       # BibliographicRecord.__tidyCiteField(self.title, '. ') + \
                       # 'in ' + \
                       # BibliographicRecord.__tidyCiteField(self.editors, ' ') + \
                       # BibliographicRecord.__tidyCiteField(self.name_of_conference, ', ') + \
                       # BibliographicRecord.__tidyCiteField(self.start_date, '-') + \
                       # BibliographicRecord.__tidyCiteField(self.finish_date, ', ') + \
                       # BibliographicRecord.__tidyCiteField(self.location, '. ') + \
                       # BibliographicRecord.__tidyCiteField(self.place_of_publication, ', ') + \
                       # BibliographicRecord.__tidyCiteField(self.publisher, ',') + \
                       # BibliographicRecord.__tidyCiteField(self.begin_page, '-', 'pp ') + \
                       # BibliographicRecord.__tidyCiteField(self.end_page, '.')                                              
            # elif self.publication.type == 'journal-article':
                # return BibliographicRecord.__tidyCiteField(self.authors, ' ') + \
                       # BibliographicRecord.__tidyCiteField(BibliographicRecord.__extractYear(self.publication_date), ') ', ' (') + \
                       # BibliographicRecord.__tidyCiteField(self.title, '. ') + \
                       # BibliographicRecord.__tidyCiteField(self.journal, '. ') + \
                       # BibliographicRecord.__tidyCiteField(self.volume, ' ') + \
                       # BibliographicRecord.__tidyCiteField(self.issue, ', ') + \
                       # BibliographicRecord.__tidyCiteField(self.begin_page, '-', 'pp ') + \
                       # BibliographicRecord.__tidyCiteField(self.end_page, '.')
            # elif self.publication.type == 'patent':
                # return 'patent - not yet coded'
            # elif self.publication.type == 'report':
                # return 'report - not yet coded'
            # elif self.publication.type == 'software':
                # return 'software - not yet coded'
            # elif self.publication.type == 'performance':
                # return 'performance - not yet coded'
            # elif self.publication.type == 'composition':
                # return 'composition - not yet coded'
            # elif self.publication.type == 'design':
                # return 'design - not yet coded'
            # elif self.publication.type == 'artefact':
                # return 'artefact - not yet coded'
            # elif self.publication.type == 'exhibition':
                # return 'exhibition - not yet coded'
            # elif self.publication.type == 'other':
                # return 'other - not yet coded'
            # elif self.publication.type == 'internet-publication':
                # return 'internet-publication - not yet coded'
            # elif self.publication.type == 'scholarly-edition':
                # return 'scholarly-edition - not yet coded'
                
  # # 
    # @staticmethod  
    # def __tidyCiteField(field, postspacer, prespacer = ''):
        # if field is None:
            # return ''
        # elif field == '':
            # return ''
        # else:
            # return prespacer + field + postspacer
    
  # #            
    # @staticmethod
    # def __extractYear(datestring, format = 'dd/mm/yyyy'):
      # #
        # if datestring is None:
            # return ''
        # elif datestring == '':
            # return ''
      # #
        # if format == 'dd/mm/yyyy':
            # return datestring[6:9]

  #    
    @staticmethod    
    def getOrCreateBibliographicRecord(publication, data_source):
      """
        Tries to load BibliographicRecord with a specific id (publication + datasource) out of database
        If not in database then creates a new empty BibliographicRecord in the database with that id
         - with foreign key links to the publication and datasource passed in        
      """    
      try:
          biblio = BibliographicRecord.objects.get(publication = publication, data_source = data_source)
          return biblio
      except (BibliographicRecord.DoesNotExist,):
          # NB DONT try to override __init__ for a model!
          biblio = BibliographicRecord()
          biblio.publication = publication
          biblio.data_source = data_source
          biblio.save()
          return biblio                     

          
          
class BiblioURL(models.Model):

  #link a single parent bibliographic-record
    bibliographic_record = models.ForeignKey(
      'BibliographicRecord',
      related_name='urls',
      )
  
  #
    type = models.CharField(max_length=255, null=True,)
    link = models.TextField(null=True,)          

# ***********************************************************************************************************************
# *****  FINISH: Python Object of Symplectic Publication                                                            *****
# ***********************************************************************************************************************



# @       @       @       @       @       @       @       @       @       @       @       @       @       @       @
#  @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @
#   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @
#    @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @
#     @       @       @       @       @       @       @       @       @       @       @       @       @       @       @



# ***********************************************************************************************************************
# *****  START: Researcher Preferences for a SymplecticPublication                                                  *****
# ***********************************************************************************************************************

class Authored(models.Model):

  #composite-unique id
    id = models.CharField(primary_key=True, max_length=255)

  #link a single Researcher
    researcher = models.ForeignKey(
      'Researcher',
      related_name='authored',
      )

  #link a single SymplecticPublication
    publication = models.ForeignKey(
      'Publication',
      related_name='authored',
      )

  #indicate which BibliographicRecord the Researcher prefers
    bibliographic_record = models.ForeignKey(
      'BibliographicRecord',
      related_name='authored',
      )

  #preferences from Symplectic
    visible = models.BooleanField(default=False)
    is_a_favourite = models.BooleanField(default=False)
    reverse_sort_cue = models.CharField(max_length=255, null=True)


  #override __save__ to create composite primary key
    def save(self):
        if (self.researcher is not None) and (self.publication is not None):
            self.id = self.researcher.symplectic_id + ':' + self.publication.guid
            super(self.__class__, self).save()

  #
    def __unicode__(self):
        return str(self.researcher) + ':' + str(self.publication)
        
        
  # DONT try to override __init__ for a model!
        
        
  #    
  # Note: bibliographic_record defaults to None as it is not essential to LOAD an Authored from DB, 
  #       but it IS essential in order to CREATE & SAVE a new Authored
    @staticmethod    
    def getOrCreateAuthored(publication, researcher, bibliographic_record=None):
      """
        Tries to load Authored with a specific id (publication + researcher) out of database
        If not in database then creates a new empty Authored in the database with that id
         - with foreign key links to the publication and researcher passed in
      """        
      try:
          authored = Authored.objects.get(publication = publication, researcher = researcher)
          return authored
      except (Authored.DoesNotExist,):
          # NB DONT try to override __init__ for a model!
          authored = Authored()
          authored.publication = publication
          authored.researcher = researcher
          authored.bibliographic_record = bibliographic_record
          authored.save()
          return authored          


# ***********************************************************************************************************************
# *****  FINISH: Researcher Preferences for a SymplecticPublication                                                 *****
# ***********************************************************************************************************************

class PublicationsPlugin(CMSPlugin):
    entity = models.ForeignKey(Entity, null=True, blank=True, 
        help_text="Leave blank for autoselect", 
        related_name="%(class)s_plugin")
    heading_level = models.PositiveSmallIntegerField(choices = PLUGIN_HEADING_LEVELS, default = PLUGIN_HEADING_LEVEL_DEFAULT)
    group_dates = models.BooleanField("Show date groups", default = True)
    limit_to = models.PositiveSmallIntegerField("Maximum number of items", default = 5, null = True, blank = True, 
        help_text = u"Leave blank for no limit")
    FORMATS = (
        ("short", u"Short"),
        ("long", u"Long"),
        )
    format = models.CharField("Item format", max_length=25,choices = FORMATS, default = "long")    
    favourites_only = models.BooleanField(default = True)
    publications_heading_text = models.CharField(max_length = 50, default = "Publications")

    def sub_heading_level(self): # requires that we change 0 to None in the database
        if self.heading_level == None: # this means the user has chosen "No heading"
            return 6 # we need to give sub_heading_level a value
        else:
            return self.heading_level + 1 # so if headings are h3, sub-headings are h4
