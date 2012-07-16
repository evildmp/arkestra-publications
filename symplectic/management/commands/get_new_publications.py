import datetime

from django.core.management.base import BaseCommand, CommandError

from symplectic.models import SymplecticXMLAuthored, SymplecticXMLPubs
from publications.models import Researcher, Publication, Authored

class Command(BaseCommand):
    help = 'Gets new and modified publications from Symplectic - note this should be run on a frequent basis'

    def handle(self, *args, **options):

        self.stdout.write('\nGet mini details of each Researcher`s Publications\n')
        for researcher in Researcher.objects.filter(publishes=True).exclude(symplectic_int_id__isnull=True):
            try:
                self.stdout.write('    %s\n' % str(researcher))
            except (Exception,), err:
                self.stdout.write('Error with researcher: %s; %s\n' % (researcher.person.id, err))
            try:
                SymplecticXMLAuthored.getAuthoredFromSymplectic(researcher)
            except (Exception,), err:
                self.stdout.write('I ignored this researcher: %s; %s\n' % (researcher, err))


        self.stdout.write('\nFlag Publications modified within last 2 days\n')
        twodaysago = datetime.date.today() - datetime.timedelta(2)
        since = str(twodaysago.year) + '-' + str(twodaysago.month) + '-' + str(twodaysago.day)
        self.stdout.write('since: %s\n' % since)
        SymplecticXMLPubs.markChangedPublicationsFromSymplectic(since)

        
        self.stdout.write('\nGet full details of flagged Publications\n')
        for publication in Publication.objects.filter(needs_refetch = True):
            try:
                self.stdout.write(str(publication) + "\n")
                SymplecticXMLPubs.updatePublicationFromSymplectic(publication)
            except (Exception,), err:
                self.stdout.write('Issue with %s : %s\n' % (publication, err))


        self.stdout.write('\nGot Publications\n')
