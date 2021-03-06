"""
OAuth 1.0 Yahoo backend

Options:
YAHOO_CONSUMER_KEY
YAHOO_CONSUMER_SECRET

References:
* http://developer.yahoo.com/oauth/guide/oauth-auth-flow.html
* http://developer.yahoo.com/social/rest_api_guide/introspective-guid-resource.html
* http://developer.yahoo.com/social/rest_api_guide/extended-profile-resource.html
"""

from django.utils import simplejson

from social_auth.utils import setting
from social_auth.backends import ConsumerBasedOAuth, OAuthBackend, USERNAME


# Google OAuth base configuration
YAHOO_OAUTH_SERVER = 'api.login.yahoo.com'
REQUEST_TOKEN_URL  = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
AUTHORIZATION_URL  = 'https://api.login.yahoo.com/oauth/v2/request_auth'
ACCESS_TOKEN_URL   = 'https://api.login.yahoo.com/oauth/v2/get_token'


class YahooOAuthBackend(OAuthBackend):
    """Yahoo OAuth authentication backend"""
    name = 'yahoo-oauth'

    EXTRA_DATA = [
        ('guid', 'id'),
        ('access_token', 'access_token'),
        ('expires', setting('SOCIAL_AUTH_EXPIRATION', 'expires'))
    ]

    def get_user_id(self, details, response):
        return response['guid']

    def get_user_details(self, response):
        """Return user details from Orkut account"""
        fname = response.get('givenName')
        lname = response.get('familyName')
        return {USERNAME:     response.get('nickname'),
                'email':      response.get('emails')[0]['handle'],
                'fullname':   '%s %s' % (fname, lname),
                'first_name': fname,
                'last_name':  lname}


class YahooOAuth(ConsumerBasedOAuth):
    AUTHORIZATION_URL    = AUTHORIZATION_URL
    REQUEST_TOKEN_URL    = REQUEST_TOKEN_URL
    ACCESS_TOKEN_URL     = ACCESS_TOKEN_URL
    SERVER_URL           = YAHOO_OAUTH_SERVER
    AUTH_BACKEND         = YahooOAuthBackend
    SETTINGS_KEY_NAME    = 'YAHOO_CONSUMER_KEY'
    SETTINGS_SECRET_NAME = 'YAHOO_CONSUMER_SECRET'

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        guid = self._get_guid(access_token)
        url = 'http://social.yahooapis.com/v1/user/%s/profile?format=json' % guid
        request = self.oauth_request(access_token, url)
        response = self.fetch_response(request)
        try:
            return simplejson.loads(response)['profile']
        except ValueError:
            return None

    def _get_guid(self, access_token):
        url = 'http://social.yahooapis.com/v1/me/guid?format=json'
        request = self.oauth_request(access_token, url)
        response = self.fetch_response(request)
        try:
            json = simplejson.loads(response)
            return json['guid']['value']
        except ValueError:
            return 'me'

# Backend definition
BACKENDS = {
    'yahoo-oauth': YahooOAuth
}
