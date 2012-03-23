from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from symplectic.models import SymplecticXMLClearUser, SymplecticXMLCreateUser, SymplecticXMLRetrieveUser
from publications.models import Researcher

class Command(BaseCommand):
    help = 'Synchronises users with Symplectic'

    def handle(self, *args, **options):

        try:
          #clear all users
          self.stdout.write('Clearing users\n')
          cleared_count = SymplecticXMLClearUser.askSymplecticToClearUsers()
          self.stdout.write('   cleared count: %s\n' % cleared_count)

          ##pause for 30 seconds to give symplectic api time to process the clear users
          #import time
          #time.sleep(30)

          #create users
          self.stdout.write('Creating users\n')
          access_list = Researcher.objects.filter(symplectic_access=True)
          self.stdout.write('    number of users: %s\n' % len(access_list))

          #for user in access_list:
          #  try:
          #    print "    ",user
          #  except:
          #    print "    Error: user"
          created_count = SymplecticXMLCreateUser.informSymplecticOfUsers(access_list)
          self.stdout.write('   created count: %s\n' % created_count)

          #retrieve users guid
          self.stdout.write('Retrieving users\n')
          missing_list = Researcher.objects.filter(symplectic_access=True).filter( Q(symplectic_id__isnull=True) | Q(symplectic_id__exact='') )
          guid_list = SymplecticXMLRetrieveUser.askSymplecticForUsersGUID(missing_list)
          for guid in guid_list:
              self.stdout.write(guid)
              
        except (Exception,), err:
          self.stdout.write('I am terribly sorry, there has been an error : %s\n' % err)

        #print log separator
        self.stdout.write('\n')

        self.stdout.write('Successfully synchronised users')
