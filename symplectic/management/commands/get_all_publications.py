from django.core.management.base import BaseCommand, CommandError

from symplectic.models import SymplecticXMLAuthored, SymplecticXMLPubs
from publications.models import Researcher, Publication, Authored

class Command(BaseCommand):
    help = 'Gets all publications from Symplectic'

    def handle(self, *args, **options):

        self.stdout.write('Researchers\n')
        for researcher in Researcher.objects.filter(publishes=True).exclude(symplectic_id=''):
            try:
                self.stdout.write(str(researcher) + "\n")
                SymplecticXMLAuthored.getAuthoredFromSymplectic(researcher)
            except (Exception,), err:
                self.stdout.write("Problem with researcher : %s\n" % err)

        self.stdout.write('Publications\n')
        for publication in Publication.objects.all():      
            try:
                self.stdout.write(str(publication) + "\n")
                SymplecticXMLPubs.updatePublicationFromSymplectic(publication)
            except (Exception,), err:
                self.stdout.write("Couldn't do %s : %s\n" % (str(publication), err))

        self.stdout.write('Got all Publications\n')
