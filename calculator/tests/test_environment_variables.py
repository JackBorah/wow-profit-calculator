from django.test import TestCase
from calculator import WowApiWrapper
import os
# Create your tests here.



class Test_environment_variables_set(TestCase):
    
    def test_postgres_USER_environment_variable_set(self):
        try:
            os.environ["WPC_postgres_username"]
        except KeyError:
            self.fail("Postgres username environment variable not set")

    def test_postgres_PASSWORD_environment_variable_set(self):
        try:
            os.environ["WPC_postgres_password"]
        except KeyError:
            self.fail("Postgres password environment variable not set")

    def test_django_secret_key_environment_variable_set(self):
        try:
            os.environ["Django_secret_key"]
        except KeyError:
            self.fail("Django secret key environment variable not set")

    def test_django_debug_environment_variable_set(self):
        try:
            os.environ["Django_debug"]
        except KeyError:
            self.fail("Django debug environment variable not set")

