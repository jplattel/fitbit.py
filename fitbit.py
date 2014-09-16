"""
A Python library for accessing the FitBit API.

This library provides a wrapper to the FitBit API and does not provide storage of tokens or caching if that is required.

Most of the code has been adapted from: https://groups.google.com/group/fitbit-api/browse_thread/thread/0a45d0ebed3ebccb

5/22/2012 - JCF - Updated to work with python-oauth2 https://github.com/dgouldin/python-oauth2
"""
import os, httplib
import oauth2 as oauth
import requests

# pass oauth request to server (use httplib.connection passed in as param)
# return response as a string
class Fitbit():
    CONSUMER_KEY    = ''
    CONSUMER_SECRET = ''
    SERVER = 'api.fitbit.com'
    REQUEST_TOKEN_URL = 'http://%s/oauth/request_token' % SERVER
    ACCESS_TOKEN_URL = 'http://%s/oauth/access_token' % SERVER
    AUTHORIZATION_URL = 'http://%s/oauth/authorize' % SERVER
    DEBUG = False

    def FetchResponse(self, oauth_request, connection, url): #added URL as config. parameter
        connection.request(oauth_request.method, url, headers=oauth_request.to_header()) #added headers to pass parameters
        response = connection.getresponse()
        s=response.read()
        return s

    def GetRequestToken(self):
        connection = httplib.HTTPSConnection(self.SERVER)
        consumer = oauth.Consumer(self.CONSUMER_KEY, self.CONSUMER_SECRET)
        signature_method = oauth.SignatureMethod_PLAINTEXT()
        oauth_request = oauth.Request.from_consumer_and_token(consumer, http_url=self.REQUEST_TOKEN_URL)
        oauth_request.sign_request(signature_method, consumer, None)
        resp = self.FetchResponse(oauth_request, connection, self.REQUEST_TOKEN_URL) #passing in explicit url
        print resp
        auth_token = oauth.Token.from_string(resp)
        auth_url = "%s?oauth_token=%s" % (self.AUTHORIZATION_URL, auth_token.key) #build the URL
        return auth_url, auth_token

    def GetAccessToken(self, access_code, auth_token, oauth_verifier):
        auth_token = oauth.Token.from_string(auth_token)
        oauth_verifier = oauth_verifier
        connection = httplib.HTTPSConnection(self.SERVER)
        consumer = oauth.Consumer(self.CONSUMER_KEY, self.CONSUMER_SECRET)
        signature_method = oauth.SignatureMethod_PLAINTEXT()
        oauth_request = oauth.Request.from_consumer_and_token(consumer, token=auth_token, http_url=self.ACCESS_TOKEN_URL, parameters={'oauth_verifier': oauth_verifier})
        oauth_request.sign_request(signature_method, consumer, auth_token)
        # now the token we get back is an access token
        resp = self.FetchResponse(oauth_request, connection, self.ACCESS_TOKEN_URL)
        access_token = oauth.Token.from_string(resp) # parse the response into an OAuthToken object / passingin explicit url
        # store the access token when returning it
        # access_token = access_token.to_string()
        return access_token

    def ApiCall(self, access_token, apiCall='/1/user/-/activities/log/steps/date/today/1d.json'):
        #other API Calls possible, or read the FitBit documentation for the full list.
        #apiCall = '/1/user/-/devices.json'
        #apiCall = '/1/user/-/profile.json'
        #apiCall = '/1/user/-/activities/date/2011-06-17.json'

        signature_method = oauth.SignatureMethod_PLAINTEXT()
        connection = httplib.HTTPSConnection(self.SERVER)
        #build the access token from a string
        access_token = oauth.Token.from_string(access_token)
        consumer = oauth.Consumer(self.CONSUMER_KEY, self.CONSUMER_SECRET)
        final_url = 'http://' + self.SERVER + apiCall
        oauth_request = oauth.Request.from_consumer_and_token(consumer, token=access_token, http_url=final_url)
        oauth_request.sign_request(signature_method, consumer, access_token)
        headers = oauth_request.to_header(realm='api.fitbit.com')
        connection.request('GET', apiCall, headers=headers)
        resp = connection.getresponse()
        response = resp.read()
        return response


