from django.core.exceptions import ObjectDoesNotExist

from contacts_and_people.menu import PersonTabs


menu_dict = {
    "auto_page_attribute": "auto_publications_page",
    "title_attribute": "publications_page_menu_title",
    "url_attribute": "publications",
    "sub_menus": False,

    "lister_module": "publications.lister",
    "lister_name": "PublicationsMenuLister",
    }


class PublicationsPersonTabs(PersonTabs):
    # information for each kind of person tab

    tab_list = [
        "default",
        "research", "publications", "researchstudents"
        ]

    def research(self, person):
        try:
            r = person.researcher
            p = r.publishes
            s = r.synopsis
            d = r.description
        except ObjectDoesNotExist:
            return

        try:
            student = r.student
            print student
        except ObjectDoesNotExist:
            return

        tab_dict = {
            "tab": "research",
            "title": "Research",
            "address": "research",
            "meta_description_content":
                "%s - research interests" % unicode(person)
        }
        if student or (p and s and d and (
            s.cmsplugin_set.all() or d.cmsplugin_set.all()
            )):
            return tab_dict

    def publications(self, person):
        try:
            r = person.researcher
            a = r.authored.exists()
            p = r.publishes
            tab_dict = {
                "tab": "publications",
                "title": "Publications",
                "address": "publications",
                "meta_description_content":
                    "%s - publications" % unicode(person)
                }
            if r and a and p:
                return tab_dict
        except ObjectDoesNotExist:
            pass

    def researchstudents(self, person):
        try:
            supervisor = person.researcher.supervisor
            tab_dict = {
                "tab": "researchstudents",
                "title": "Research students",
                "address": "research-students",
                "meta_description_content":
                "%s - research students" % unicode(person)
                }
            if supervisor.student_set.exists():
                return tab_dict
        except ObjectDoesNotExist:
            print "supervisor not found"
            pass
