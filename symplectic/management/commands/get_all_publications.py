from django.core.management.base import BaseCommand, CommandError

from symplectic.models import get_authoreds, update_publication
from publications.models import Researcher, Publication, Authored

class Command(BaseCommand):
    help = 'Gets all publications from Symplectic - note this should NOT be run on a frequent basis'

    def handle(self, *args, **options):
        self.stdout.write('*****  Do not run this procedure frequently!  *****\n')


        self.stdout.write('\nGet mini details of each Researcher\'s Publications\n')
        # for researcher in Researcher.objects.filter(publishes=True).exclude(symplectic_int_id__isnull=True): # for int_id version


        # loop over all the Researchers
        for researcher in Researcher.objects.filter(
            publishes=True
            ).exclude(symplectic_id__isnull=True): # for guid version

            self.stdout.write('    %s\n' % str(researcher))

            #
            get_authoreds(researcher)

        #
        #     #
        #     # try:
        #     #     self.stdout.write('    %s\n' % str(researcher))
        #     # except (Exception,), err:
        #     #     self.stdout.write('Error with researcher: %s; %s\n' % (researcher.person.id, err))
        #     # try:
        #     #     get_authoreds(researcher)
        #     # except (Exception,), err:
        #     #     self.stdout.write('I ignored this researcher: %s; %s\n' % (researcher, err))


        # raise Exception

        self.stdout.write('\nGet full details of ALL Publications\n')
        for publication in Publication.objects.all():
            # self.stdout.write(str(publication) + "\n")
            update_publication(publication)


            # try:
            #     self.stdout.write(str(publication) + "\n")
            #     update_publication(publication)
            # except (Exception,), err:
            #     self.stdout.write('Issue with %s : %s\n' % (str(publication), err))


        self.stdout.write('Got all Publications\n')
