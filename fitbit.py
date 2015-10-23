"""
A Python library for accessing the FitBit API.

This library provides a wrapper to the FitBit API and does not provide storage of tokens or caching if that is required.

Most of the code has been adapted from: https://groups.google.com/group/fitbit-api/browse_thread/thread/0a45d0ebed3ebccb

5/22/2012 - JCF - Updated to work with python-oauth2 https://github.com/dgouldin/python-oauth2
10/22/2015 - JG - Removed use of oauth2 library (singing is not necessary anymore),
                  updated to use /oauth2/ authentication infrastructure to get access to more stats.
"""
import os, base64, requests, urllib

class Fitbit():

    # All information must be as on the https://dev.fitbit.com/apps page.
    CLIENT_ID     = ''
    CLIENT_SECRET = ''
    REDIRECT_URI  = 'http://www.example.com'

    # Decide which information the FitBit.py should have access to.
    # Options: 'activity', 'heartrate', 'location', 'nutrition',
    #          'profile', 'settings', 'sleep', 'social', 'weight'
    API_SCOPES    = ('activity','heartrate','profile')

    # These settings should probably not be changed.
    API_SERVER    = 'api.fitbit.com'
    WWW_SERVER    = 'www.fitbit.com'
    AUTHORIZE_URL = 'https://%s/oauth2/authorize' % WWW_SERVER
    TOKEN_URL     = 'https://%s/oauth2/token' % API_SERVER

    def GetAuthorizationUri(self):

        # Parameters for authorization, make sure to select 
        params = {
            'client_id': self.CLIENT_ID,
            'response_type':  'code',
            'scope': ' '.self.API_SCOPES,
            'redirect_uri': self.REDIRECT_URI
        }

        # Encode parameters and construct authorization url to be returned to user.
        urlparams = urllib.urlencode(params)
        return "%s?%s" % (self.AUTHORIZE_URL, urlparams)

    # Tokes are requested based on access code. Access code must be fresh (10 minutes)
    def GetAccessToken(self, access_code):

        # Construct the authentication header
        auth_header = base64.b64encode(self.CLIENT_ID + ':' + self.CLIENT_SECRET)
        headers = {'Authorization': 'Basic %s' % auth_header}

        # Paramaters for requesting tokens (auth + refresh)
        params = {
            'code': access_code,
            'grant_type': 'authorization_code',
            'client_id': self.CLIENT_ID,
            'redirect_uri': self.REDIRECT_URI
        }

        # Place request
        resp = requests.post(self.TOKEN_URL, data=params, headers=headers)

        # Strip the goodies
        access_token = str(resp.json()['access_token'])
        refresh_token = str(resp.json()['refresh_token'])

        return access_token, refresh_token

    # Get new tokens based if authentication token is expired
    def RefAccessToken(self, refresh_token):

        # Construct the authentication header
        auth_header = base64.b64encode(self.CLIENT_ID + ':' + self.CLIENT_SECRET)
        headers = {'Authorization': 'Basic %s' % auth_header}

        # Set up parameters for refresh request
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        # Place request
        resp = requests.post(self.TOKEN_URL, data=params, headers=headers)

        # Distil
        access_token = str(resp.json()['access_token'])
        refresh_token = str(resp.json()['refresh_token'])

        return access_token, refresh_token

    # Place api call to retrieve data
    def ApiCall(self, access_token, apiCall='/1/user/-/activities/log/steps/date/today/1d.json'):
        # Other API Calls possible, or read the FitBit documentation for the full list
        # (https://dev.fitbit.com/docs/), e.g.:
        # apiCall = '/1/user/-/devices.json'
        # apiCall = '/1/user/-/profile.json'
        # apiCall = '/1/user/-/activities/date/2015-10-22.json'

        headers = {'Authorization': 'Bearer %s' % access_token}

        final_url = 'https://' + self.API_SERVER + apiCall

        resp = requests.post(final_url, headers=headers)

        return resp.json(), resp.status_code


