#app = symplectic

from datetime import datetime
import urllib
from elementtree.ElementTree import ElementTree, Element, SubElement, XML
from xml.parsers.expat import ExpatError
import urllib2
import os

from publications.models import (
    Publication, BibliographicRecord, BiblioURL, Authored
    )


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

TIMESTAMP = str(datetime.now())


class User(object):

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
        self.send_usersr = ''
        self.is_academic = ''
        self.generic_field_1_dept = ''
        self.generic_field_2_dept_id = ''
        self.generic_field_11_irg = ''
        self.generic_field_12_irg_id = ''
        self.generic_field_13_admin = ''
        self.generic_field_14_institute = ''
        self.generic_field_15_institute_id = ''


# functions for creating users

def clear_users():
    # Sends an XML File to Symplectic API asking it to clear all users
    filename = __createXMLFileForClear()
    response = __postClearUsersXMLFileToSymplectic(
        filename
        )
    count = _get_cleared_user_count(response)
    return count


def send_users(researcher_list):

    # Sends an XML File of Users to Symplectic, to its API
    userlist = _create_symplectic_user_list(researcher_list)
    xml_filename = _create_xml_users_file(userlist)
    symplectic_response = _post_xml_users_file(xml_filename)
    created_count = _get_created_user_count(symplectic_response)
    return created_count


def __createXMLFileForClear():
    # Builds an XML File to ask Symplectic to clear all users
    clear_root = Element(
        'clear-users-request',
        {'xmlns': SYMPLECTIC_XMLNS_URI}
        )
    # Feed
    SubElement(clear_root, 'feed-id').text = IMPORT_USERS_FEED_ID

    #Convert to ElementTree and write xml version to file
    xml_filename = "".join([
        SYMPLECTIC_LOCAL_XML_FOLDER,
        SYMPLECTIC_LOCAL_USER_FOLDER,
        TIMESTAMP,
        SYMPLECTIC_LOCAL_USER_CLEARFILE
        ])
    ElementTree(clear_root).write(xml_filename)
    print "clearing with", xml_filename
    return xml_filename


def __postClearUsersXMLFileToSymplectic(xml_filename):
    # Actually performs the HTTP POST of the XML File to Symplectic API,
    # asking it to clear users

    #prepare the HTTP request with the XML file of ClearUsers as the payload
    url = SYMPLECTIC_API_URL + 'clear-users'
    headers = {'Content-Type': 'text/xml'}
    xml_file = open(xml_filename, 'r')
    data = xml_file.read()
    req = urllib2.Request(url, data, headers)

    #POST the HTTP request to Symplectic API
    try:
        response = urllib2.urlopen(req)
        the_page = response.read()
        return the_page
    except urllib2.URLError:
        raise ESymplecticPostFileError("""
            Could not HTTP POST the CLEAR Users XML file to Symplectic API
            """)


def _get_cleared_user_count(xml_string):
    # Extracts the count from the symplectic response to the XML file clear
    try:
        response_element = XML(xml_string)
        cleared_count = response_element.attrib.get("count")
        return cleared_count
    except ExpatError:
        raise ESymplecticParseFileError("""
            Could not extract the number of Users cleared from the XML file
            returned by Symplectic API
            """)


def _get_created_user_count(xml_string):
    """
    Extracts the count from the symplectic response to the XML file of Users
    we sent it
    """
    try:
        response_element = XML(xml_string)
        created_count = response_element.attrib.get("count")
        return created_count
    except ExpatError:
        raise ESymplecticParseFileError("""
            Could not extract the number of Users created from the XML file
            returned by Symplectic API
        """)


def _determine_institute(researcher):
    # Determines which Entity within researcher.person.member_of is their
    # Institute
    try:
        return researcher.person.member_of.filter(
            entity__in=[5],
            importance_to_person=5)[0].entity
    except IndexError:
        return None


def _post_xml_users_file(xml_filename):
    """
    Actually performs the HTTP POST of the XML File of Users we want to ask
    Symplectic to create, to its API
    """

    #prepare the HTTP request with the XML file of Users as the payload
    url = SYMPLECTIC_API_URL + 'import-users'
    headers = {'Content-Type': 'text/xml'}
    xml_file = open(xml_filename, 'r')
    data = xml_file.read()
    req = urllib2.Request(url, data, headers)

    #POST the HTTP request to Symplectic API
    try:
        response = urllib2.urlopen(req)
        the_page = response.read()
        return the_page
    except (urllib2.URLError,):
        raise ESymplecticPostFileError(
            "Could not HTTP POST the CREATE Users XML file to Symplectic API"
            )


def _create_xml_users_file(user_objectlist):
    # Builds an XML File of Users we want to ask Symplectic to create, in
    # the format that Symplectic`s API is expecting. XML elements are
    # created for each user in the list of User
    # objects passed in
    users_root = Element(
        'import-users-request',
        {'xmlns': SYMPLECTIC_XMLNS_URI}
        )
    # Feed
    SubElement(users_root, 'feed-id').text = IMPORT_USERS_FEED_ID
    # List of users(plural) - will contain user(singular) elements
    users_plural_element = SubElement(users_root, 'users')
    for user_object in user_objectlist:
        # Add individual user(singular) sub-element
        user_element = SubElement(users_plural_element, 'user')
        # Add details
        SubElement(user_element, 'title').text = user_object.title
        SubElement(user_element, 'initials').text = user_object.initials
        SubElement(user_element, 'first-name').text = user_object.first_name
        SubElement(user_element, 'last-name').text = user_object.last_name
        SubElement(user_element, 'known-as').text = ''  # user_object.known_as
        SubElement(user_element, 'suffix').text = ''  # user_object.suffix
        SubElement(user_element, 'email').text = user_object.email
        SubElement(
            user_element,
            'authenticating-authority'
            ).text = user_object.authenticating_authority
        SubElement(user_element, 'username').text = user_object.username
        SubElement(
            user_element,
            'proprietary-id').text = user_object.proprietary_id
        SubElement(
            user_element,
            'primary-group-descriptor'
            ).text = user_object.primary_group_descriptor
        if user_object.is_academic is True:
            SubElement(user_element, 'is-academic').text = 'true'
        else:
            SubElement(user_element, 'is-academic').text = 'false'
        SubElement(
            user_element, 'generic-field-01'
            ).text = user_object.generic_field_1_dept
        SubElement(
            user_element,
            'generic-field-02'
            ).text = user_object.generic_field_2_dept_id
        SubElement(
            user_element,
            'generic-field-11'
            ).text = user_object.generic_field_11_irg
        SubElement(
            user_element,
            'generic-field-12'
            ).text = user_object.generic_field_12_irg_id
        SubElement(
            user_element,
            'generic-field-13'
            ).text = user_object.generic_field_13_admin
        SubElement(
            user_element,
            'generic-field-14'
            ).text = user_object.generic_field_14_institute
        SubElement(
            user_element,
            'generic-field-15'
            ).text = user_object.generic_field_15_institute_id

        # break connection between user_element pointer-variable and the
        # actual xml-subelement in memory that contains the data
        user_element = None

    #Convert to ElementTree and write xml version to file
    xml_filename = "".join([
        SYMPLECTIC_LOCAL_XML_FOLDER,
        SYMPLECTIC_LOCAL_USER_FOLDER,
        TIMESTAMP,
        SYMPLECTIC_LOCAL_USER_IMPORTFILE
        ])
    ElementTree(users_root).write(xml_filename)
    #Return xml filename
    print "writing with", xml_filename
    return xml_filename


def _create_symplectic_user_list(researcher_list):
    # Creates a list of User objects from a list of
    # Publications.Researcher objects
    user_objectlist = []
    for researcher in researcher_list:
        #create symplectic specific user object
        user_object = User()
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
        institute = _determine_institute(researcher)
        # if (institute):
        #     user_object.generic_field_14_institute = institute.name
        # if (institute):
        #     user_object.generic_field_15_institute_id = str(institute.id)
        user_objectlist.append(user_object)
    return user_objectlist


# functions to retrieve users from Symplectic

def get_user_ids(researcher_list):
    """
    Asks Symplectic API for the ID for researchers
    """
    # Retrieved SymplecticIDs
    ids = []
    # For each researcher, ask symplectic for their Symplectic-id
    for researcher in researcher_list:
        print researcher
        SymplecticID = _get_users(researcher)
        if SymplecticID and SymplecticID != '':
            ids.append(SymplecticID)
    return ids


def _get_users(researcher_object):
    """
    Asks Symplectic API for User info about specified researcher
    Specify which researcher using proprietary-id
    Receives XML File as response
    Parses XML File to find symplectic ID for each User
    """
    # symplectic api url and local file path
    url = "".join([
        SYMPLECTIC_API_URL,
        'search-users?',
        '&include-deleted=true',
        '&authority=',
        AUTHENTICATING_AUTHORITY,
        '&proprietary-id=',
        str(researcher_object.person_id)
        ])

    #'&username=' + researcher_object.person.institutional_username + \

    tmp_filename = "".join([
        SYMPLECTIC_LOCAL_XML_FOLDER,
        SYMPLECTIC_LOCAL_USER_FOLDER,
        str(researcher_object.person_id),
        '.xml'
        ])

    #get xml document from symplectic api and store on hd
    try:
        (tmp_filename, http_headers) = urllib.urlretrieve(url, tmp_filename)
    except urllib2.URLError:
        raise ESymplecticGetFileError("""
            Could not HTTP GET the XML file of User GUID from Symplectic API
            """)

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
    # for each retrieved user element in tree (should only be 1)
    for user_element in usersresponse_element.getchildren():
        # pull out of xml what symplectic says this researcher's proprietary
        # id and symplectic-id are
        proprietary_id = user_element.attrib.get("proprietary-id")
        id = user_element.attrib.get("id")
        # if arkestra and symplectic agree this is the same person
        if str(researcher_object.person_id) == proprietary_id:
            # researcher_object.symplectic_int_id = id # int_id version
            researcher_object.symplectic_id = id  # guid version
            researcher_object.save()
            # force return after 1 (should only be 1 person per xml file
            # anyway)

            return id
        else:
            raise ESymplecticExtractUserGUIDError("""
                ID returned by Symplectic API not for correct Arkestra User
                (Proprietary ID doesnt match
                """)


# functions to get authored items

def get_authoreds(researcher_object):
    """
    Asks Symplectic API for info about specified researcher
    Receives XML File as response
    Parses XML File to find all publications for that researcher & notes
    preferences they have for each publication
    """
    # checking
    # if not(researcher_object) or (researcher_object.symplectic_int_id is
    # None): # int_id version
    if not(researcher_object) or (researcher_object.symplectic_id is None):
        # guid version
        return

    # symplectic api url and local file path
    # url = SYMPLECTIC_API_URL + 'users/' +
    # str(researcher_object.symplectic_int_id) # int_id version
    url = "".join([
        SYMPLECTIC_API_URL,
        'users/',
        str(researcher_object.symplectic_id)
        ])

    # # tmp_filename = SYMPLECTIC_LOCAL_XML_FOLDER +
    # SYMPLECTIC_LOCAL_AUTH_FOLDER +
    # str(researcher_object.symplectic_int_id)
    # + '.xml' # int_id version

    tmp_filename = "".join([
        SYMPLECTIC_LOCAL_XML_FOLDER,
        SYMPLECTIC_LOCAL_AUTH_FOLDER,
        str(researcher_object.symplectic_id),
        '.xml'
        ])

    # get xml document from symplectic api and store on hd
    (tmp_filename, http_headers) = urllib.urlretrieve(url, tmp_filename)

    # parse xml file
    publications_etree = ElementTree(file=tmp_filename)
    #delete local file from hd
    #try:
    os.remove(tmp_filename)
    #except:
    #pass
    #publication elements are held in a subtree
    publications_subtree = publications_etree.find(
        SYMPLECTIC_NAMESPACE + 'publications'
        )

    # check if any publication elements in subtree
    if publications_subtree is None or len(publications_subtree) < 1:
        return

    # now that we have their newest "i authored that pub" info, we can
    # delete their old "i authored that pub" info
    researcher_object.remove_all_authored()
    # for each publication element in subtree
    for publication_element in publications_subtree.getchildren():
        _create_authored(publication_element, researcher_object)


def _create_authored(publication_element, researcher_object):
    """
    Takes an XML publication element lifted from a Symplectic User file
    (which does not contain as much info about each
    publication/biblio-record as a proper publication XML file)

    extracts the minimum info (key-fields: guid) about publication, and
    links publication to researcher extracts the minimum info (key-fields:
    data-source) about indicated favourite biblio-record for that
    publication and links biblio-record to researcher extracts full
    preferences (visible, favourite, sort-order) that researcher has for
    that publication

    NOTE: an attempt is made to load an existing publication/biblio-record
    based on the key-fields extracted if that fails then a new one is
    created with only the key-fields populated and is then saved
    """
    #++++++PUBLICATION LITE++++++
    #check publication Element
    if publication_element is None:
        return
    #publication guid
    if publication_element is not None:
        guid = publication_element.get('id', '')
    if guid == '':
        return

    # load Publication from db or create (flagged as needing refetch from
    # symplectic) if doesnt exist
    publication_object = Publication.getOrCreatePublication(guid)

    # ++++++BIBLIOGRAPHICRECORD LITE++++++
    # bibliographic-record element -> publication sub element (used to
    # read XML)
    if publication_element is not None:
    # only ONE biblio element per publication will be returned when querying
    # by User_id this is in contrast to the multiple biblios elements per
    # publication returned when querying by a Publication_guid
        biblio_element = publication_element.find(
            SYMPLECTIC_NAMESPACE + 'bibliographic-record'
            )
    #biblio data-source
    if biblio_element is not None:
        data_source = biblio_element.get('data-source', '')

    # load BibliographicRecord from db or create if doesnt exist (NB
    # links biblio & publication)

    # print "        going to get or create a BibliographicRecord"
    biblio_object = BibliographicRecord.getOrCreateBibliographicRecord(
        publication_object, data_source
        )

    # ++++++AUTHORED++++++
    # authored preferences -> publication sub-elements (used to read XML)
    if publication_element is not None:
        preferences_element = publication_element.find(
            SYMPLECTIC_NAMESPACE + 'preferences-for-this-publication'
            )
    # load Authored from db or create if doesnt exist (NB links authored
    # & publication & researcher & bibliographic-record)
    authored_object = Authored.getOrCreateAuthored(
        publication_object, researcher_object, biblio_object
        )
    # preferences
    if preferences_element is not None:
        # Show this publication
        if preferences_element.get('visible', 'false') == 'true':
            authored_object.visible = True
        else:
            authored_object.visible = False
        # Favourite publication
        if preferences_element.get('is-a-favourite', 'false') == 'true':
            authored_object.is_a_favourite = True
        else:
            authored_object.is_a_favourite = False
        # Display order
        authored_object.reverse_sort_cue = preferences_element.get(
            'reverse-sort-cue', ''
            )

    authored_object.save()


# XML parsing functions

def update_publication(publication_object):
    """
    Asks Symplectic API for info about specified publication based upon
    its guid
    Receives XML File as response
    Parses XML File to find publication info & all biblio-records for that
    publication
    """
    # checking
    # print "        update_publication",  publication_object
    if not(publication_object) or (publication_object.guid == ''):
        return

    # symplectic api url and local file path
    url = SYMPLECTIC_API_URL + 'publications/' + publication_object.guid

    tmp_filename = "".join([
        SYMPLECTIC_LOCAL_XML_FOLDER,
        SYMPLECTIC_LOCAL_PUBS_FOLDER,
        str(publication_object.guid),
        '.xml'
        ])

    # get xml document from symplectic api and store on hd
    (tmp_filename, http_headers) = urllib.urlretrieve(url, tmp_filename)
    # parse xml file
    pub_etree = ElementTree(file=tmp_filename)
    #d elete local file from hd
    # try:
    os.remove(tmp_filename)
    # except:
    # pass
    #++++++PUBLICATION++++++
    # publication element
    pub_element = pub_etree.getroot()
    # no loading-of/blank publication object required as updating the one
    # passed in
    # check returned xml element is valid and for correct publication
    if pub_element is None:
        return
    elif publication_object.guid != pub_element.get('id', ''):
        return
    # publication attributes
    if pub_element is not None:
        publication_object.new_id = pub_element.get('new-id')
        if pub_element.get('is-deleted', 'false') == 'true':
            publication_object.is_deleted = True
        else:
            publication_object.is_deleted = False

        attr_names = ["type", "created-when", "last-modified-when"]
        for attr_name in attr_names:
            attr_value = pub_element.get(attr_name, "")
            setattr(
                publication_object,
                attr_name.replace("-", "_"),
                attr_value
                )

    # just fetched latest version from symplectic
    publication_object.needs_refetch = False
    # save updated publication object
    publication_object.save()
    # ++++++BIBLIOGRAPHIC-RECORD++++++
    # bibliographic-record elements are held in a subtree
    biblio_subtree = pub_etree.find(
        SYMPLECTIC_NAMESPACE + 'bibliographic-records'
        )
    # check if any bibliographic-record elements in subtree
    if biblio_subtree is None or len(biblio_subtree) < 1:
        return
    # for each bibliographic-record element in subtree

    for biblio_element in biblio_subtree.getchildren():
        _create_biblio_object(biblio_element, publication_object)


def _get_element_text(element):
    if element is None:
        return ''
    else:
        return element.text


def _create_biblio_object(biblio_element, publication_object):
    """
    Takes an XML biblio-record element lifted from a Symplectic Publication
    file (which contains the FULL info about each biblio-record unlike a
    User XML file) extracts full info about that biblio-record,
    loads/creates biblio-object, populates it with this new info and saves
    it
    """
    # ++++++BIBLIOGRAPHIC-RECORD++++++
    # check Bibliographical-record Element
    # print "        creating", biblio_element

    if biblio_element is None:
        # print "       giving up in _create_biblio_object"
        return
    # make blank Biblio Object
    biblio_object = BibliographicRecord()

    # Bibliographic-record sub-elements (used to read XML)

    if biblio_element is not None:
        bibliometric_data_element = biblio_element.find(
            SYMPLECTIC_NAMESPACE + 'bibliometric-data'
            )
        bibliographic_data_element = biblio_element.find(
            SYMPLECTIC_NAMESPACE + 'bibliographic-data'
            )
    if bibliographic_data_element is not None:
        native_element = bibliographic_data_element.find(
            SYMPLECTIC_NAMESPACE + 'native'
            )
    if native_element is not None:
        authors_subtree = native_element.find(SYMPLECTIC_NAMESPACE + 'authors')
        keywords_subtree = native_element.find(
            SYMPLECTIC_NAMESPACE + 'keywords'
            )
    # bibliographic-record attribs
    if biblio_element is not None:
        biblio_object.data_source = biblio_element.get('data-source', '')
        biblio_object.id_at_source = biblio_element.get('id-at-source', '')
        biblio_object.verification_status = _get_element_text(
            biblio_element.find(SYMPLECTIC_NAMESPACE + 'verification-status')
        )
    # bibliometric data
    if bibliometric_data_element is not None:
        biblio_object.times_cited = _get_element_text(
            bibliometric_data_element.find(
                SYMPLECTIC_NAMESPACE + 'times-cited'
                )
            )
        biblio_object.reference_count = _get_element_text(
            bibliometric_data_element.find(
                SYMPLECTIC_NAMESPACE + 'reference-count'
                )
            )
    # native
    if native_element is not None:

        attr_names = [
            'abstract', 'associated-authors', 'awarded-date', 'begin-page',
            'book-author-type', 'commissioning-body', 'confidential', 'doi',
            'edition', 'editors', 'end-page', 'filed-date', 'finish-date',
            'isbn-10', 'isbn-13', 'issn', 'issue', 'journal',
            'journal-article-type', 'language', 'location', 'medium',
            'name-of-conference', 'notes', 'number', 'number-of-pages',
            'number-of-pieces', 'parent-title', 'patent-number', 'pii',
            'place-of-publication', 'publication-date', 'publication-status',
            'publication-status', 'series', 'start-date', 'title', 'version',
            'volume'
            ]

        for attr_name in attr_names:
            element = native_element.find(SYMPLECTIC_NAMESPACE + attr_name)
            attr_value = _get_element_text(element)
            setattr(biblio_object, attr_name.replace("-", "_"), attr_value)

    # authors
    if authors_subtree is not None:
        biblio_object.authors = ''
        author_list = []
        for author_element in authors_subtree.getchildren():
            name = _get_element_text(
                author_element.find(SYMPLECTIC_NAMESPACE + 'name')
                )
            initials = _get_element_text(
                author_element.find(SYMPLECTIC_NAMESPACE + 'initials')
                )
            author_list.append(unicode(name) + ' ' + unicode(initials))
        biblio_object.authors = ", ".join(author_list)
        print biblio_object.authors
        #derived authors
        biblio_object.number_of_authors = len(author_list)
        if len(author_list) > 0:
            biblio_object.first_author = author_list[0]
        if len(author_list) > 1:
            biblio_object.last_author = author_list[-1]
    # keywords
    if keywords_subtree is not None:
        biblio_object.keywords = ''
        for keyword_element in keywords_subtree.getchildren():
            biblio_object.keywords = "|".join([
                biblio_object.keywords,
                unicode(keyword_element.text)
                ])
    # link bibliographic-record object and passed-in publication object
    biblio_object.publication = publication_object
    # save
    # print "        going to save biblio_object", biblio_object, \
        # "publication_id",  biblio_object.publication_id

    biblio_object.save()

    # ++++++URLS++++++
    # delete all existing URLs for this biblio-record
    biblio_object.urls.all().delete()
    # URL elements are held in a subtree
    url_subtree = biblio_element.find(SYMPLECTIC_NAMESPACE + 'urls')
    # check if any url elements in subtree
    if url_subtree is None or len(url_subtree) < 1:
        return
    # for each url element in subtree
    for url_element in url_subtree.getchildren():
        _create_url_object(url_element, biblio_object)


def _create_url_object(url_element, biblio_object):
    """
    Takes an XML url-biblio-record element lifted from a Symplectic
    Publication file (which contains the FULL info about each biblio-record
    unlike a User XML file) extracts info about that url, creates
    url-object, populates it with this new info and saves it
    """
    # ++++++URL++++++
    # check url Element
    if url_element is None:
        return
    # make blank URL Object
    url_object = BiblioURL()
    # URL data
    url_object.type = url_element.get('type', '')
    url_object.link = url_element.text
    # link url object and passed-in biblio-record object
    url_object.bibliographic_record = biblio_object
    # save
    url_object.save()


def mark_changed_publications(modified_since):
    """
    Asks Symplectic API for info about publications modified since given
    date Receives XML File as response Parses XML File to find publications
    modified matches publication XML element to db publication object flags
    each publication object as needing to be re-fetched from Symplectic
    """
    # date needs to be in form of yyyy-mm-dd
    # will then append string "T00:00:00Z" as we are in UTC-0 timezone in
    # which : becomes %3A
    # symplectic api url and local file path
    url = "".join([
        SYMPLECTIC_API_URL,
        'search-publications?modified-since-when=',
        modified_since,
        'T00%3A00%3A00Z'
    ])
    tmp_filename = "".join([
        SYMPLECTIC_LOCAL_XML_FOLDER,
        SYMPLECTIC_LOCAL_PUBSMODIFIED_FOLDER,
        modified_since,
        '.xml'
        ])
    # get xml document from symplectic api and store on hd
    (tmp_filename, http_headers) = urllib.urlretrieve(url, tmp_filename)
    # parse xml file
    search_publications_etree = ElementTree(file=tmp_filename)
    # delete local file from hd
    # try:
    os.remove(tmp_filename)
    # except:
    # pass
    # publication lite elements are held in a subtree BUT the subtree is
    # the root element
    # search_publications_subtree =
    # search_publications_etree.find(SYMPLECTIC_NAMESPACE +
    # 'search-publications-response')

    search_publications_subtree = search_publications_etree.getroot()
    # check if any publication elements in subtree
    if search_publications_subtree is None or \
            len(search_publications_subtree) < 1:
        return
    #  for each publication element in subtree
    for search_publication_element \
            in search_publications_subtree.getchildren():
        _flag_publication_as_needing_refetch(
            search_publication_element
        )


def _flag_publication_as_needing_refetch(search_publication_element):
    """
    Takes an XML publication element lifted from a Symplectic Modified file
    (which does not contain as much info about each
    publication/biblio-record as a proper publication XML file)

    extracts the minimum info (key-fields: guid) about publication loads
    the related publication object from the db flags the publication object
    as needing a re-fetch from Symplectic

     NOTE: an attempt is made to load an existing publication but if it
     does not already exist IT IS NOT CREATED because if the db doesn`t
     know about it already then the publication has not been linked to a
     reasearcher so who cares about it
    """
    #++++++PUBLICATION LITE++++++
    #check publication Element
    if search_publication_element is None:
        return

    #publication guid
    if search_publication_element is not None:
        guid = search_publication_element.get('id', '')
    if guid == '':
        return

    # load Publication from db if it exists, otherwise give up - DONT
    # create it!
    publication_object = Publication.getPublication(guid)
    if publication_object is None:
        return
    #symplectic has an updated version of this publication
    publication_object.needs_refetch = True
    #save this change to the publication object
    publication_object.save()


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
