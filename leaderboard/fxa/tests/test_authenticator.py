import mock
from django.test import TestCase
from rest_framework.exceptions import AuthenticationFailed

from leaderboard.contributors.tests.test_models import ContributorFactory
from leaderboard.fxa.authenticator import OAuthTokenAuthentication
from leaderboard.fxa.tests.test_client import MockRequestTestMixin


class TestOAuthTokenAuthentication(MockRequestTestMixin, TestCase):

    def test_returns_none_if_missing_token(self):
        request = mock.MagicMock()
        request.META = {}

        with self.assertRaises(AuthenticationFailed):
            OAuthTokenAuthentication().authenticate(request)

    def test_raises_authenticationfailed_if_malformed_header(self):
        request = mock.MagicMock()
        request.META = {'HTTP_AUTHORIZATION': 'invalid'}

        with self.assertRaises(AuthenticationFailed):
            OAuthTokenAuthentication().authenticate(request)

    def test_raises_authenticationfailed_if_token_unknown(self):
        self.set_mock_response(self.mock_get, status_code=400)

        request = mock.MagicMock()
        request.META = {'HTTP_AUTHORIZATION': 'Bearer abc'}

        with self.assertRaises(AuthenticationFailed):
            OAuthTokenAuthentication().authenticate(request)

    def test_raises_authenticationfailed_if_uid_missing(self):
        self.set_mock_response(self.mock_get, data={})

        request = mock.MagicMock()
        request.META = {'HTTP_AUTHORIZATION': 'Bearer abc'}

        with self.assertRaises(AuthenticationFailed):
            OAuthTokenAuthentication().authenticate(request)

    def test_raises_authenticationfailed_if_no_contributor_found(self):
        self.setup_profile_call()

        request = mock.MagicMock()
        request.META = {
            'HTTP_AUTHORIZATION': 'Bearer asdf',
        }

        with self.assertRaises(AuthenticationFailed):
            OAuthTokenAuthentication().authenticate(request)

    def test_parses_header_and_returns_contributor(self):
        fxa_profile_data = self.setup_profile_call()

        contributor = ContributorFactory(fxa_uid=fxa_profile_data['uid'])

        request = mock.MagicMock()
        request.META = {
            'HTTP_AUTHORIZATION': 'Bearer asdf',
        }

        user, token = OAuthTokenAuthentication().authenticate(request)

        self.assertEqual(user, contributor)
