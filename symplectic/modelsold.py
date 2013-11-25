#app = symplectic

from django.db import models
import urllib
from elementtree.ElementTree import ElementTree, Element, SubElement, XML
from elementtree.ElementTree import parse
from xml.parsers.expat import ExpatError
import httplib
import urllib2
import os

from publications.models import Researcher, Publication, BibliographicRecord, BiblioURL, Authored
# import ref_shared.models

# &       &       &       &       &       &       &       &       &       &       &       &       &       &       &
#  &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &
#   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &
#    & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &
#     &       &       &       &       &       &       &       &       &       &       &       &       &       &       &

# ***********************************************************************************************************************
# *****  START: Symplectic Constants                                                                                *****
# ***********************************************************************************************************************

SYMPLECTIC_API_URL = 'http://medic3.cardiff.ac.uk:8090/publications-api/v3.4/'
SYMPLECTIC_XMLNS_URI = 'http://www.symplectic.co.uk/publications/api'
SYMPLECTIC_NAMESPACE = '{' + SYMPLECTIC_XMLNS_URI + '}'

SYMPLECTIC_LOCAL_XML_FOLDER = '/tmp/symplectic/'
SYMPLECTIC_LOCAL_AUTH_FOLDER = 'userpubs/'
SYMPLECTIC_LOCAL_PUBS_FOLDER = 'pubs/'
SYMPLECTIC_LOCAL_PUBSMODIFIED_FOLDER = 'pubsmodified/'
SYMPLECTIC_LOCAL_USER_FOLDER = 'usersadmin/'
SYMPLECTIC_LOCAL_USER_IMPORTFILE = 'import_users.xml'
SYMPLECTIC_LOCAL_USER_CLEARFILE = 'clear_users.xml'

AUTHENTICATING_AUTHORITY = 'CARDIFFLDAP'
IMPORT_USERS_FEED_ID = 'django arkestra'


# ***********************************************************************************************************************
# *****  FINISH: Symplectic Constants                                                                               *****
# ***********************************************************************************************************************



# &       &       &       &       &       &       &       &       &       &       &       &       &       &       &
#  &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &
#   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &
#    & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &
#     &       &       &       &       &       &       &       &       &       &       &       &       &       &       &






# &       &       &       &       &       &       &       &       &       &       &       &       &       &       &
#  &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &
#   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &
#    & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &
#     &       &       &       &       &       &       &       &       &       &       &       &       &       &       &


# ***********************************************************************************************************************
# *****  START: Symplectic Clear Users API XML                                                                      *****
# ***********************************************************************************************************************


class SymplecticXMLClearUser(object):


    @staticmethod
    def askSymplecticToClearUsers():
      #description
        """
          Sends an XML File to Symplectic API asking it to clear all users
        """
      #
        xml_filename = SymplecticXMLClearUser.__createXMLFileForClear()
        symplectic_response = SymplecticXMLClearUser.__postClearUsersXMLFileToSymplectic(xml_filename)
        cleared_count = SymplecticXMLClearUser.__extractUserClearedCountFromResponse(symplectic_response)
        return cleared_count



    @staticmethod
    def __createXMLFileForClear():
      #description
        """
          PRIVATE
          Builds an XML File to ask Symplectic to clear all users
        """
      #Root
        clear_root = Element('clear-users-request', {'xmlns':SYMPLECTIC_XMLNS_URI,} )
      #Feed
        SubElement(clear_root, 'feed-id').text = IMPORT_USERS_FEED_ID
      #Convert to ElementTree and write xml version to file
        xml_filename = SYMPLECTIC_LOCAL_XML_FOLDER + SYMPLECTIC_LOCAL_USER_FOLDER + SYMPLECTIC_LOCAL_USER_CLEARFILE
        ElementTree(clear_root).write(xml_filename)
      #Return xml filename
        return xml_filename




    @staticmethod
    def __postClearUsersXMLFileToSymplectic(xml_filename):
      #description
        """
          PRIVATE
          Actually performs the HTTP POST of the XML File to Symplectic API, asking it to clear users
        """
      #prepare the HTTP request with the XML file of ClearUsers as the payload
        url = SYMPLECTIC_API_URL + 'clear-users'
        headers = {
            'Content-Type' : 'text/xml',
        }
        xml_file = open(xml_filename, 'r')
        data = xml_file.read()
        req = urllib2.Request(url, data, headers)
      #POST the HTTP request to Symplectic API
        try:
          response = urllib2.urlopen(req)
          the_page = response.read()
          return the_page
        except (urllib2.URLError,):
          raise ESymplecticPostFileError("Could not HTTP POST the CLEAR Users XML file to Symplectic API")



    @staticmethod
    def __extractUserClearedCountFromResponse(xml_string):
      #description
        """
          PRIVATE
          Extracts the count from the symplectic response to the XML file clear
        """
      #
        try:
          response_element = XML(xml_string)
          cleared_count = response_element.attrib.get("count")
          return cleared_count
        except (ExpatError,):
          raise ESymplecticParseFileError("Could not extract the number of Users cleared from the XML file returned by Symplectic API")




# ***********************************************************************************************************************
# *****  FINISH: Symplectic Clear Users API XML                                                                     *****
# ***********************************************************************************************************************



# @       @       @       @       @       @       @       @       @       @       @       @       @       @       @
#  @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @
#   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @
#    @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @
#     @       @       @       @       @       @       @       @       @       @       @       @       @       @       @



# ***********************************************************************************************************************
# *****  START: Symplectic Create Users API XML                                                                     *****
# ***********************************************************************************************************************


class SymplecticXMLCreateUser(object):

    def __init__(self):
        self.title = ''
        self.initials = ''
        self.first_name = ''
        self.last_name = ''
        self.known_as = ''
        self.suffix = ''
        self.email = ''
        self.authenticating_authority = ''
        self.username = ''
        self.proprietary_id = ''
        self.primary_group_descriptor = ''
        self.is_academic = ''
        self.generic_field_1_dept = ''
        self.generic_field_2_dept_id = ''
        self.generic_field_11_irg = ''
        self.generic_field_12_irg_id = ''
        self.generic_field_13_admin = ''
        self.generic_field_14_institute = ''
        self.generic_field_15_institute_id = ''




    @staticmethod
    def informSymplecticOfUsers(researcher_list):
      #description
        """
          Sends an XML File of Users to Symplectic, to its API
        """
      #
        symplectic_user_objectlist = SymplecticXMLCreateUser.__createSymplecticUserListFromResearcherList(researcher_list)
        xml_filename = SymplecticXMLCreateUser.__createXMLFileFromUserObjectList(symplectic_user_objectlist)
        symplectic_response = SymplecticXMLCreateUser.__postUsersXMLFileToSymplectic(xml_filename)
        created_count = SymplecticXMLCreateUser.__extractUserCreatedCountFromResponse(symplectic_response)
        return created_count



    @staticmethod
    def __createSymplecticUserListFromResearcherList(researcher_list):
      #description
        """
          PRIVATE
          Creates a list of SymplecticXMLCreateUser objects from a list of Publications.Researcher objects
        """
      #
        user_objectlist = []
        for researcher in researcher_list:
          #create symplectic specific user object
            user_object = SymplecticXMLCreateUser()
            user_object.title = str(researcher.person.title)
            user_object.initials = researcher.person.initials
            user_object.first_name = researcher.person.given_name
            user_object.last_name = researcher.person.surname
            user_object.known_as = ''
            user_object.suffix = ''
            user_object.email = researcher.person.email
            user_object.authenticating_authority = AUTHENTICATING_AUTHORITY
            user_object.username = researcher.person.institutional_username
            user_object.proprietary_id = str(researcher.person.id)
            user_object.primary_group_descriptor = 'MEDIC'
            user_object.is_academic = True
            if (researcher.symplectic_access) and (not researcher.publishes):
                user_object.generic_field_13_admin = 'Y'
            else:
                user_object.generic_field_13_admin = 'N'
            institute = SymplecticXMLCreateUser.__determineResearchersInstitute(researcher)
            if (institute):
                user_object.generic_field_14_institute = institute.name
            if (institute):
                user_object.generic_field_15_institute_id = str(institute.id)
            user_objectlist.append(user_object)
        return user_objectlist


    @staticmethod
    def __determineResearchersInstitute(researcher):
      #description
        """
          PRIVATE
          Determines which Entity within researcher.person.member_of is their Institute
        """
      #
        try:
          return researcher.person.member_of.filter(entity__in=[5,], importance_to_person=5)[0].entity
        except (IndexError,):
          return None


    @staticmethod
    def __createXMLFileFromUserObjectList(user_objectlist):
      #description
        """
          PRIVATE
          Builds an XML File of Users we want to ask Symplectic to create, in the format that Symplectic`s API is expecting.
            XML elements are created for each user in the list of SymplecticXMLCreateUser objects passed in
        """
      #Root
        users_root = Element('import-users-request', {'xmlns':SYMPLECTIC_XMLNS_URI,} )
      #Feed
        SubElement(users_root, 'feed-id').text = IMPORT_USERS_FEED_ID
      #List of users(plural) - will contain user(singular) elements
        users_plural_element = SubElement(users_root, 'users')
        for user_object in user_objectlist:
          #Add individual user(singular) sub-element
            user_element = SubElement(users_plural_element, 'user')
          #Add details
            SubElement(user_element, 'title').text = user_object.title
            SubElement(user_element, 'initials').text = user_object.initials
            SubElement(user_element, 'first-name').text = user_object.first_name
            SubElement(user_element, 'last-name').text = user_object.last_name
            SubElement(user_element, 'known-as').text = '' #user_object.known_as
            SubElement(user_element, 'suffix').text = '' #user_object.suffix
            SubElement(user_element, 'email').text = user_object.email
            SubElement(user_element, 'authenticating-authority').text = user_object.authenticating_authority
            SubElement(user_element, 'username').text = user_object.username
            SubElement(user_element, 'proprietary-id').text = user_object.proprietary_id
            SubElement(user_element, 'primary-group-descriptor').text = user_object.primary_group_descriptor
            if user_object.is_academic == True:
                SubElement(user_element, 'is-academic').text = 'true'
            else:
                SubElement(user_element, 'is-academic').text = 'false'
            SubElement(user_element, 'generic-field-01').text = user_object.generic_field_1_dept
            SubElement(user_element, 'generic-field-02').text = user_object.generic_field_2_dept_id
            SubElement(user_element, 'generic-field-11').text = user_object.generic_field_11_irg
            SubElement(user_element, 'generic-field-12').text = user_object.generic_field_12_irg_id
            SubElement(user_element, 'generic-field-13').text = user_object.generic_field_13_admin
            SubElement(user_element, 'generic-field-14').text = user_object.generic_field_14_institute
            SubElement(user_element, 'generic-field-15').text = user_object.generic_field_15_institute_id
          #break connection between user_element pointer-variable and the actual xml-subelement in memory that contains the data
            user_element = None
      #Convert to ElementTree and write xml version to file
        xml_filename = SYMPLECTIC_LOCAL_XML_FOLDER + SYMPLECTIC_LOCAL_USER_FOLDER + SYMPLECTIC_LOCAL_USER_IMPORTFILE
        ElementTree(users_root).write(xml_filename)
      #Return xml filename
        return xml_filename




    @staticmethod
    def __postUsersXMLFileToSymplectic(xml_filename):
      #description
        """
          PRIVATE
          Actually performs the HTTP POST of the XML File of Users we want to ask Symplectic to create, to its API
        """
      #prepare the HTTP request with the XML file of Users as the payload
        url = SYMPLECTIC_API_URL + 'import-users'
        headers = {
            'Content-Type' : 'text/xml',
        }
        xml_file = open(xml_filename, 'r')
        data = xml_file.read()
        req = urllib2.Request(url, data, headers)
      #POST the HTTP request to Symplectic API
        try:
          response = urllib2.urlopen(req)
          the_page = response.read()
          return the_page
        except (urllib2.URLError,):
          raise ESymplecticPostFileError("Could not HTTP POST the CREATE Users XML file to Symplectic API")



    @staticmethod
    def __extractUserCreatedCountFromResponse(xml_string):
      #description
        """
          PRIVATE
          Extracts the count from the symplectic response to the XML file of Users we sent it
        """
      #
        try:
          response_element = XML(xml_string)
          created_count = response_element.attrib.get("count")
          return created_count
        except (ExpatError,):
          raise ESymplecticParseFileError("Could not extract the number of Users created from the XML file returned by Symplectic API")




# ***********************************************************************************************************************
# *****  FINISH: Symplectic Create Users API XML                                                                    *****
# ***********************************************************************************************************************



# @       @       @       @       @       @       @       @       @       @       @       @       @       @       @
#  @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @
#   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @
#    @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @
#     @       @       @       @       @       @       @       @       @       @       @       @       @       @       @



# ***********************************************************************************************************************
# *****  START: Symplectic Retrieve Users API XML                                                                   *****
# ***********************************************************************************************************************

class SymplecticXMLRetrieveUser(object):

    @staticmethod
    def askSymplecticForUsersID(researcher_list):
      #description
        """
          Asks Symplectic API for the ID for researchers
        """
      #Retrieved SymplecticIDs
        IDs = []
      #For each researcher, ask symplectic for their Symplectic-id
        for researcher in researcher_list:
          SymplecticID = SymplecticXMLRetrieveUser.__getUsersFromSymplectic(researcher)
          if SymplecticID and SymplecticID!='':
              IDs.append(SymplecticID)
      #Return list of ids retrieved
        return IDs


    @staticmethod
    def __getUsersFromSymplectic(researcher_object):
      #description
        """
          PRIVATE
          Asks Symplectic API for User info about specified researcher
          Specify which researcher using proprietary-id
          Receives XML File as response
          Parses XML File to find symplectic ID for each User
        """
      #symplectic api url and local file path
        url = SYMPLECTIC_API_URL + 'search-users?' + \
                                            '&include-deleted=true' + \
                                            '&authority=' + AUTHENTICATING_AUTHORITY + \
                                            '&proprietary-id=' + str(researcher_object.person_id)
        #'&username=' + researcher_object.person.institutional_username + \
        tmp_filename = SYMPLECTIC_LOCAL_XML_FOLDER + SYMPLECTIC_LOCAL_USER_FOLDER + str(researcher_object.person_id) + '.xml'
      #get xml document from symplectic api and store on hd
        try:
          (tmp_filename, http_headers,) = urllib.urlretrieve(url, tmp_filename)
        except (urllib2.URLError,):
          raise ESymplecticGetFileError("Could not HTTP GET the XML file of User GUID from Symplectic API")
      #parse xml file
        users_etree = ElementTree(file=tmp_filename)
        usersresponse_element = users_etree.getroot()
      #delete local file from hd
        #try:
        os.remove(tmp_filename)
        #except:
        #pass
      #check if any user elements in tree
        if usersresponse_element is None:
          return ""
      #for each retrieved user element in tree (should only be 1)
        for user_element in usersresponse_element.getchildren():
          #pull out of xml what symplectic says this researcher's proprietary id and symplectic-id are
            proprietary_id = user_element.attrib.get("proprietary-id")
            id = user_element.attrib.get("id")
          #if arkestra and symplectic agree this is the same person
            if str(researcher_object.person_id) == proprietary_id:
                # researcher_object.symplectic_int_id = id # int_id version
                researcher_object.symplectic_id = id # guid version
                researcher_object.save()
                #force return after 1 (should only be 1 person per xml file anyway)
                return id
            else:
                raise ESymplecticExtractUserGUIDError("ID returned by Symplectic API not for correct Arkestra User (Proprietary ID doesnt match")

# ***********************************************************************************************************************
# *****  FINISH: Symplectic Retrieve Users API XML                                                                  *****
# ***********************************************************************************************************************



# &       &       &       &       &       &       &       &       &       &       &       &       &       &       &
#  &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &
#   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &
#    & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &
#     &       &       &       &       &       &       &       &       &       &       &       &       &       &       &






# &       &       &       &       &       &       &       &       &       &       &       &       &       &       &
#  &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &
#   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &
#    & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &
#     &       &       &       &       &       &       &       &       &       &       &       &       &       &       &



# ***********************************************************************************************************************
# *****  START: Symplectic Authored API XML                                                                         *****
# ***********************************************************************************************************************

class SymplecticXMLAuthored(object):

    @staticmethod
    def getAuthoredFromSymplectic(researcher_object):
      #description
        """
          Asks Symplectic API for info about specified researcher
          Receives XML File as response
          Parses XML File to find all publications for that researcher & notes preferences they have for each publication
        """
      #checking
        # if not(researcher_object) or (researcher_object.symplectic_int_id is None): # int_id version
        if not(researcher_object) or (researcher_object.symplectic_id is None): # guid version
            return
      #symplectic api url and local file path
        # url = SYMPLECTIC_API_URL + 'users/' + str(researcher_object.symplectic_int_id) # int_id version
        url = SYMPLECTIC_API_URL + 'users/' + str(researcher_object.symplectic_id) # guid version
        # tmp_filename = SYMPLECTIC_LOCAL_XML_FOLDER + SYMPLECTIC_LOCAL_AUTH_FOLDER + str(researcher_object.symplectic_int_id) + '.xml' # int_id version
        tmp_filename = SYMPLECTIC_LOCAL_XML_FOLDER + SYMPLECTIC_LOCAL_AUTH_FOLDER + str(researcher_object.symplectic_id) + '.xml' # guid version
      #get xml document from symplectic api and store on hd
        (tmp_filename, http_headers,) = urllib.urlretrieve(url, tmp_filename)
      #parse xml file
        publications_etree = ElementTree(file=tmp_filename)
      #delete local file from hd
        #try:
        os.remove(tmp_filename)
        #except:
        #pass
      #publication elements are held in a subtree
        publications_subtree = publications_etree.find(SYMPLECTIC_NAMESPACE + 'publications')
      #check if any publication elements in subtree
        if publications_subtree is None or len(publications_subtree) < 1:
          return
      #now that we have their newest "i authored that pub" info, we can delete their old "i authored that pub" info
        researcher_object.remove_all_authored()
      #for each publication element in subtree
        for publication_element in publications_subtree.getchildren():
            SymplecticXMLAuthored.__createAuthoredObjFromUserPubElement(publication_element, researcher_object)


    @staticmethod
    def __createAuthoredObjFromUserPubElement(publication_element, researcher_object):
      #description
        """
          PRIVATE
          Takes an XML publication element lifted from a Symplectic User file
          (which does not contain as much info about each publication/biblio-record as a proper publication XML file)

          extracts the minimum info (key-fields: guid) about publication, and links publication to researcher
          extracts the minimum info (key-fields: data-source) about indicated favourite biblio-record for that publication and links biblio-record to researcher
          extracts full preferences (visible, favourite, sort-order) that researcher has for that publication

          NOTE: an attempt is made to load an existing publication/biblio-record based on the key-fields extracted
                if that fails then a new one is created with only the key-fields populated and is then saved
        """
      #++++++PUBLICATION LITE++++++
      #check publication Element
        if publication_element is None:
          return
      #publication guid
        if publication_element is not None:
          guid = publication_element.get('id','')
        if guid == '':
          return
      #load Publication from db or create (flagged as needing refetch from symplectic) if doesnt exist
        publication_object = Publication.getOrCreatePublication(guid)
      #++++++BIBLIOGRAPHICRECORD LITE++++++
      #bibliographic-record element -> publication sub element (used to read XML)
        if publication_element is not None:
          #only ONE biblio element per publication will be returned when querying by User_id
          #  this is in contrast to the multiple biblios elements per publication returned when querying by a Publication_guid
          biblio_element = publication_element.find(SYMPLECTIC_NAMESPACE + 'bibliographic-record')
      #biblio data-source
        if biblio_element is not None:
            data_source = biblio_element.get('data-source','')
      #load BibliographicRecord from db or create if doesnt exist (NB links biblio & publication)
        biblio_object = BibliographicRecord.getOrCreateBibliographicRecord(publication_object, data_source)
      #++++++AUTHORED++++++
      #authored preferences -> publication sub-elements (used to read XML)
        if publication_element is not None:
          preferences_element = publication_element.find(SYMPLECTIC_NAMESPACE + 'preferences-for-this-publication')
      #load Authored from db or create if doesnt exist (NB links authored & publication & researcher & bibliographic-record)
        authored_object = Authored.getOrCreateAuthored(publication_object, researcher_object, biblio_object)
      #preferences
        if preferences_element is not None:
          #Show this publication
            if preferences_element.get('visible','false') == 'true':
                authored_object.visible = True
            else:
                authored_object.visible = False
          #Favourite publication
            if preferences_element.get('is-a-favourite','false') == 'true':
                authored_object.is_a_favourite = True
            else:
                authored_object.is_a_favourite = False
          #Display order
            authored_object.reverse_sort_cue = preferences_element.get('reverse-sort-cue','')
      #Save Authored
        authored_object.save()

# ***********************************************************************************************************************
# *****  FINISH: Symplectic Authored API XML                                                                        *****
# ***********************************************************************************************************************



# @       @       @       @       @       @       @       @       @       @       @       @       @       @       @
#  @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @
#   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @
#    @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @
#     @       @       @       @       @       @       @       @       @       @       @       @       @       @       @



# ***********************************************************************************************************************
# *****  START: Symplectic Publications API XML                                                                     *****
# ***********************************************************************************************************************

class SymplecticXMLPubs(object):

    @staticmethod
    def updatePublicationFromSymplectic(publication_object):
      #description
        """
          Asks Symplectic API for info about specified publication based upon its guid
          Receives XML File as response
          Parses XML File to find publication info & all biblio-records for that publication
        """
      #checking
        if not(publication_object) or (publication_object.guid == ''):
            return
      #symplectic api url and local file path
        url = SYMPLECTIC_API_URL + 'publications/' + publication_object.guid
        tmp_filename = SYMPLECTIC_LOCAL_XML_FOLDER + SYMPLECTIC_LOCAL_PUBS_FOLDER + publication_object.guid + '.xml'
      #get xml document from symplectic api and store on hd
        (tmp_filename, http_headers,) = urllib.urlretrieve(url, tmp_filename)
      #parse xml file
        pub_etree = ElementTree(file=tmp_filename)
      #delete local file from hd
        #try:
        os.remove(tmp_filename)
        #except:
        #pass
      #++++++PUBLICATION++++++
      #publication element
        pub_element = pub_etree.getroot()
      #no loading-of/blank publication object required as updating the one passed in
      #check returned xml element is valid and for correct publication
        if pub_element is None:
            return
        elif publication_object.guid != pub_element.get('id',''):
            return
      #publication attributes
        if pub_element is not None:
            publication_object.new_id = pub_element.get('new-id')
            if pub_element.get('is-deleted','false') == 'true':
                publication_object.is_deleted = True
            else:
                publication_object.is_deleted = False
            publication_object.type = pub_element.get('type','')
            publication_object.created_when = pub_element.get('created-when','')
            publication_object.last_modified_when = pub_element.get('last-modified-when','')
      #just fetched latest version from symplectic
        publication_object.needs_refetch = False
      #save updated publication object
        publication_object.save()
      #++++++BIBLIOGRAPHIC-RECORD++++++
      #bibliographic-record elements are held in a subtree
        biblio_subtree = pub_etree.find(SYMPLECTIC_NAMESPACE + 'bibliographic-records')
      #check if any bibliographic-record elements in subtree
        if biblio_subtree is None or len(biblio_subtree) < 1:
          return
      #for each bibliographic-record element in subtree
        for biblio_element in biblio_subtree.getchildren():
            SymplecticXMLPubs.__createBiblioObjFromBiblioElement(biblio_element, publication_object)


    @staticmethod
    def __createBiblioObjFromBiblioElement(biblio_element, publication_object):
      #description
        """
          PRIVATE
          Takes an XML biblio-record element lifted from a Symplectic Publication file
          (which contains the FULL info about each biblio-record unlike a User XML file)
          extracts full info about that biblio-record, loads/creates biblio-object, populates it with this new info and saves it
        """
      #++++++BIBLIOGRAPHIC-RECORD++++++
      #check Bibliographical-record Element
        if biblio_element is None:
            return
      #make blank Biblio Object
        biblio_object = BibliographicRecord()
      #Bibliographic-record sub-elements (used to read XML)
        if biblio_element is not None:
            urls = biblio_element.find(SYMPLECTIC_NAMESPACE + 'urls')
            bibliometric_data_element = biblio_element.find(SYMPLECTIC_NAMESPACE + 'bibliometric-data')
            bibliographic_data_element = biblio_element.find(SYMPLECTIC_NAMESPACE + 'bibliographic-data')
        if bibliographic_data_element is not None:
            native_element = bibliographic_data_element.find(SYMPLECTIC_NAMESPACE + 'native')
        if native_element is not None:
            authors_subtree = native_element.find(SYMPLECTIC_NAMESPACE + 'authors')
            keywords_subtree = native_element.find(SYMPLECTIC_NAMESPACE + 'keywords')
      #bibliographic-record attribs
        if biblio_element is not None:
            biblio_object.data_source = biblio_element.get('data-source','')
            biblio_object.id_at_source = biblio_element.get('id-at-source','')
            biblio_object.verification_status = SymplecticXMLPubs.__getElementText( biblio_element.find(SYMPLECTIC_NAMESPACE + 'verification-status') )
      #bibliometric data
        if bibliometric_data_element is not None:
            biblio_object.times_cited = SymplecticXMLPubs.__getElementText( bibliometric_data_element.find(SYMPLECTIC_NAMESPACE + 'times-cited') )
            biblio_object.reference_count = SymplecticXMLPubs.__getElementText( bibliometric_data_element.find(SYMPLECTIC_NAMESPACE + 'reference-count') )
      #native
        if native_element is not None:
            biblio_object.abstract = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'abstract') )
            biblio_object.associated_authors = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'associated-authors') )
            biblio_object.awarded_date = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'awarded-date') )
            biblio_object.begin_page = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'begin-page') )
            biblio_object.book_author_type = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'book-author-type') )
            biblio_object.commissioning_body = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'commissioning-body') )
            biblio_object.confidential = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'confidential') )
            biblio_object.doi = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'doi') )
            biblio_object.edition = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'edition') )
            biblio_object.editors = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'editors') )
            biblio_object.end_page = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'end-page') )
            biblio_object.filed_date = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'filed-date') )
            biblio_object.finish_date = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'finish-date') )
            biblio_object.isbn_10 = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'isbn-10') )
            biblio_object.isbn_13 = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'isbn-13') )
            biblio_object.issn = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'issn') )
            biblio_object.issue = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'issue') )
            biblio_object.journal = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'journal') )
            biblio_object.journal_article_type = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'journal_article_type') )
            biblio_object.language = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'language') )
            biblio_object.location = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'location') )
            biblio_object.medium = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'medium') )
            biblio_object.name_of_conference = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'name-of-conference') )
            biblio_object.notes = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'notes') )
            biblio_object.number = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'number') )
            biblio_object.number_of_pages = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'number-of-pages') )
            biblio_object.number_of_pieces = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'number-of-pieces') )
            biblio_object.parent_title = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'parent-title') )
            biblio_object.patent_number = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'patent-number') )
            biblio_object.patent_status = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'patent-status') )
            biblio_object.pii = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'pii') )
            biblio_object.place_of_publication = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'place_of_publication') )
            biblio_object.publication_date = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'publication-date') )
            biblio_object.publication_status = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'publication-status') )
            biblio_object.publisher = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'publisher') )
            biblio_object.series = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'series') )
            biblio_object.start_date = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'start-date') )
            biblio_object.title = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'title') )
            biblio_object.version = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'version') )
            biblio_object.volume = SymplecticXMLPubs.__getElementText( native_element.find(SYMPLECTIC_NAMESPACE + 'volume') )
      #authors
        if authors_subtree is not None:
            biblio_object.authors = ''
            author_list = []
            for author_element in authors_subtree.getchildren():
                name = SymplecticXMLPubs.__getElementText(author_element.find(SYMPLECTIC_NAMESPACE + 'name'))
                initials = SymplecticXMLPubs.__getElementText(author_element.find(SYMPLECTIC_NAMESPACE + 'initials'))
                author_list.append( unicode(name) + ' ' + unicode(initials) )
            for author in author_list:
                biblio_object.authors = biblio_object.authors + author + ', '
            #derived authors
            biblio_object.number_of_authors = len(author_list)
            if len(author_list) > 0:
                biblio_object.first_author = author_list[0]
            if len(author_list) > 1:
                biblio_object.last_author = author_list[-1]
      #keywords
        if keywords_subtree is not None:
            biblio_object.keywords = ''
            for keyword_element in keywords_subtree.getchildren():
                biblio_object.keywords = biblio_object.keywords + '|' + unicode(keyword_element.text)
      #link bibliographic-record object and passed-in publication object
        biblio_object.publication = publication_object
      #save
        print "going to save from symplectic.models"
        biblio_object.save()
      #++++++URLS++++++
      #delete all existing URLs for this biblio-record
        biblio_object.urls.all().delete()
      #URL elements are held in a subtree
        url_subtree = biblio_element.find(SYMPLECTIC_NAMESPACE + 'urls')
      #check if any url elements in subtree
        if url_subtree is None or len(url_subtree) < 1:
          return
      #for each url element in subtree
        for url_element in url_subtree.getchildren():
            SymplecticXMLPubs.__createURLObjFromURLElement(url_element, biblio_object)



    @staticmethod
    def __createURLObjFromURLElement(url_element, biblio_object):
      #description
        """
          PRIVATE
          Takes an XML url-biblio-record element lifted from a Symplectic Publication file
          (which contains the FULL info about each biblio-record unlike a User XML file)
          extracts info about that url, creates url-object, populates it with this new info and saves it
        """
      #++++++URL++++++
      #check url Element
        if url_element is None:
            return
      #make blank URL Object
        url_object = BiblioURL()
      #URL data
        url_object.type = url_element.get('type','')
        url_object.link = url_element.text
      #link url object and passed-in biblio-record object
        url_object.bibliographic_record = biblio_object
      #save
        url_object.save()



    @staticmethod
    def __getElementText(element):
        if element is None:
            return ''
        else:
            return element.text


# ***********************************************************************************************************************
# *****  FINISH: Symplectic Publications API XML                                                                    *****
# ***********************************************************************************************************************



# @       @       @       @       @       @       @       @       @       @       @       @       @       @       @
#  @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @
#   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @   @
#    @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @     @ @
#     @       @       @       @       @       @       @       @       @       @       @       @       @       @       @



# ***********************************************************************************************************************
# *****  START: Symplectic Search Publications API XML                                                              *****
# ***********************************************************************************************************************


    @staticmethod
    def markChangedPublicationsFromSymplectic(modified_since):
      #description
        """
          Asks Symplectic API for info about publications modified since given date
          Receives XML File as response
          Parses XML File to find publications modified
            matches publication XML element to db publication object
            flags each publication object as needing to be re-fetched from Symplectic
        """
      #date needs to be in form of yyyy-mm-dd
      # will then append string "T00:00:00Z" as we are in UTC-0 timezone in which : becomes %3A
      #symplectic api url and local file path
        url = SYMPLECTIC_API_URL + 'search-publications?modified-since-when=' + modified_since + 'T00%3A00%3A00Z'
        tmp_filename = SYMPLECTIC_LOCAL_XML_FOLDER + SYMPLECTIC_LOCAL_PUBSMODIFIED_FOLDER + modified_since + '.xml'
      #get xml document from symplectic api and store on hd
        (tmp_filename, http_headers,) = urllib.urlretrieve(url, tmp_filename)
      #parse xml file
        search_publications_etree = ElementTree(file=tmp_filename)
      #delete local file from hd
        #try:
        os.remove(tmp_filename)
        #except:
        #pass
      #publication lite elements are held in a subtree BUT the subtree is the root element
        #search_publications_subtree = search_publications_etree.find(SYMPLECTIC_NAMESPACE + 'search-publications-response')
        search_publications_subtree = search_publications_etree.getroot()
      #check if any publication elements in subtree
        if search_publications_subtree is None or len(search_publications_subtree) < 1:
          return
      #for each publication element in subtree
        for search_publication_element in search_publications_subtree.getchildren():
            SymplecticXMLPubs.__flagPublicationAsNeedsRefetch(search_publication_element)



    @staticmethod
    def __flagPublicationAsNeedsRefetch(search_publication_element):
      #description
        """
          PRIVATE
          Takes an XML publication element lifted from a Symplectic Modified file
         (which does not contain as much info about each publication/biblio-record as a proper publication XML file)

          extracts the minimum info (key-fields: guid) about publication
            loads the related publication object from the db
              flags the publication object as needing a re-fetch from Symplectic

          NOTE: an attempt is made to load an existing publication but if it does not already exist IT IS NOT CREATED
                because if the db doesn`t know about it already then the publication has not been linked to a reasearcher
                so who cares about it
        """
      #++++++PUBLICATION LITE++++++
      #check publication Element
        if search_publication_element is None:
          return
      #publication guid
        if search_publication_element is not None:
          guid = search_publication_element.get('id','')
        if guid == '':
          return
      #load Publication from db if it exists, otherwise give up - DONT create it!
        publication_object = Publication.getPublication(guid)
        if publication_object is None:
          return
      #symplectic has an updated version of this publication
        publication_object.needs_refetch = True
      #save this change to the publication object
        publication_object.save()


# ***********************************************************************************************************************
# *****  FINISH: Symplectic Changed Publications API XML                                                            *****
# ***********************************************************************************************************************



# &       &       &       &       &       &       &       &       &       &       &       &       &       &       &
#  &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &
#   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &
#    & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &
#     &       &       &       &       &       &       &       &       &       &       &       &       &       &       &

# &       &       &       &       &       &       &       &       &       &       &       &       &       &       &
#  &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &
#   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &
#    & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &
#     &       &       &       &       &       &       &       &       &       &       &       &       &       &       &



# ***********************************************************************************************************************
# *****  START: Custom Errors                                                                                       *****
# ***********************************************************************************************************************


class ESymplecticError(Exception):
    def __init__(self, message):
        super(ESymplecticError, self).__init__(message)

    def _get_message(self):
        return self.args[0]
    def _set_message(self, message):
        self.args[0] = message
    message = property(_get_message, _set_message)



class ESymplecticGetFileError(ESymplecticError):
    pass


class ESymplecticParseFileError(ESymplecticError):
    pass


class ESymplecticPostFileError(ESymplecticError):
    pass


class ESymplecticExtractUserGUIDError(ESymplecticError):
    pass

# ***********************************************************************************************************************
# *****  FINISH: Custom Errors                                                                                      *****
# ***********************************************************************************************************************



# &       &       &       &       &       &       &       &       &       &       &       &       &       &       &
#  &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &
#   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &   &
#    & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &     & &
#     &       &       &       &       &       &       &       &       &       &       &       &       &       &       &
