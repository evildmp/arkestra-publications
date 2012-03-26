import datetime

from django.core.management.base import BaseCommand, CommandError

from symplectic.models import SymplecticXMLAuthored, SymplecticXMLPubs
from publications.models import Researcher, Publication, Authored

class Command(BaseCommand):
    help = 'Gets new and modified publications from Symplectic'

    def handle(self, *args, **options):

        self.stdout.write('Researchers\n')
        for researcher in Researcher.objects.filter(publishes=True).exclude(symplectic_id=''):
            try:
                print researcher
            except (Exception,), err:
                self.stdout.write('Error with researcher: %s %s\n' % (researcher.person.id, err))
            try:
                SymplecticXMLAuthored.getAuthoredFromSymplectic(researcher)
            except (Exception,), err:
                self.stdout.write('I ignored this researcher: %s\n' % (researcher, err))

        self.stdout.write('Mark modified publications\n')
        twodaysago = datetime.date.today() - datetime.timedelta(2)
        since = str(twodaysago.year) + '-' + str(twodaysago.month) + '-' + str(twodaysago.day)
        self.stdout.write('since: %s\n' % since)


        self.stdout.write('Get modified publications\n')
        for publication in Publication.objects.filter(needs_refetch = True):      
            try:
                self.stdout.write(str(publication) + "\n")
                SymplecticXMLPubs.updatePublicationFromSymplectic(publication)
            except (Exception,), err:
                self.stdout.write('Issue with %s : %s\n' % (publication, err))

        self.stdout.write('Got all Publications\n')
