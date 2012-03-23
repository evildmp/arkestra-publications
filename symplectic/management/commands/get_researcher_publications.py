from django.core.management.base import BaseCommand, CommandError

from symplectic.models import SymplecticXMLAuthored, SymplecticXMLPubs
from publications.models import Researcher, Publication, Authored

class Command(BaseCommand):
    help = 'Gets publications for a single researcher'

    def handle(self, *args, **options):

        self.stdout.write('Researcher\n')
        researcher = Researcher.objects.get(symplectic_id='620e62f9-6c30-43e0-9030-6b42457fc875')
        try:
            self.stdout.write(researcher)
            SymplecticXMLAuthored.getAuthoredFromSymplectic(researcher)
        except (Exception,), err:
            self.stdout.write('I am terribly sorry, there has been an error : %s\n' % err)

        self.stdout.write('Get publications\n')
        for authored in researcher.get_authoreds():
            try:
                self.stdout.write(authored.publication)
                SymplecticXMLPubs.updatePublicationFromSymplectic(authored.publication)
            except (Exception,), err:
                self.stdout.write('I am terribly sorry, there has been an error : %s\n' % err)

        self.stdout.write('Got publications\n')
