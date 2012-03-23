from django.core.management.base import BaseCommand, CommandError

from symplectic.models import SymplecticXMLClearUser, SymplecticXMLCreateUser, SymplecticXMLRetrieveUser
from publications.models import Researcher, Publication, Authored

class Command(BaseCommand):
    help = 'Gets all publications from Symplectic'

    def handle(self, *args, **options):

        self.stdout.write('Researchers\n')
        for researcher in Researcher.objects.filter(publishes=True).exclude(symplectic_id=''):
            try:
                self.stdout.write(researcher)
                SymplecticXMLAuthored.getAuthoredFromSymplectic(researcher)
            except (Exception,), err:
                self.stdout.write('I am terribly sorry, there has been an error : %s\n' % err)

        self.stdout.write('Publications\n')
        for publication in Publication.objects.all():      
            try:
                self.stdout.write(publication)
                SymplecticXMLPubs.updatePublicationFromSymplectic(publication)
            except (Exception,), err:
                self.stdout.write('I am terribly sorry, there has been an error : %s\n' % err)

        self.stdout.write('Got all Publications\n')
