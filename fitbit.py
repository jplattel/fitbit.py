"""
A Python library for accessing the FitBit API.

This library provides a wrapper to the FitBit API and does not provide storage of tokens or caching if that is required.

Most of the code has been adapted from: https://groups.google.com/group/fitbit-api/browse_thread/thread/0a45d0ebed3ebccb
"""
import os, httplib 
from oauth import oauth 


# pass oauth request to server (use httplib.connection passed in as param) 
# return response as a string 
class FitBit():
    CONSUMER_KEY    = 'ADD_YOUR_CONSUMER_KEY' 
    CONSUMER_SECRET = 'ADD_YOUR_CONSUMER_SECRET' 
    SERVER = 'api.fitbit.com' 
    REQUEST_TOKEN_URL = 'http://%s/oauth/request_token' % SERVER 
    ACCESS_TOKEN_URL = 'http://%s/oauth/access_token' % SERVER 
    AUTHORIZATION_URL = 'http://%s/oauth/authorize' % SERVER 
    DEBUG = False
    
    def FetchResponse(self, oauth_request, connection, debug=DEBUG): 
       url = oauth_request.to_url() 
       connection.request(oauth_request.http_method,url) 
       response = connection.getresponse() 
       s=response.read() 
       if debug: 
          print 'requested URL: %s' % url 
          print 'server response: %s' % s 
       return s
   
    def GetRequestToken(self): 
       connection = httplib.HTTPSConnection(self.SERVER) 
       consumer = oauth.OAuthConsumer(self.CONSUMER_KEY, self.CONSUMER_SECRET)  
       signature_method = oauth.OAuthSignatureMethod_PLAINTEXT() 
       oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, http_url=self.REQUEST_TOKEN_URL) 
       oauth_request.sign_request(signature_method, consumer, None) 

       resp = self.FetchResponse(oauth_request, connection) 
       auth_token = oauth.OAuthToken.from_string(resp) 

       #build the URL
       authkey = str(auth_token.key) 
       authsecret = str(auth_token.secret) 
       auth_url = "%s?oauth_token=%s" % (self.AUTHORIZATION_URL, auth_token.key) 
       return auth_url, auth_token
   
    def GetAccessToken(self, access_code, auth_token):
       oauth_verifier = access_code
       connection = httplib.HTTPSConnection(self.SERVER) 
       consumer = oauth.OAuthConsumer(self.CONSUMER_KEY, self.CONSUMER_SECRET) 
       signature_method = oauth.OAuthSignatureMethod_PLAINTEXT() 
       oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=auth_token, http_url=self.ACCESS_TOKEN_URL, parameters={'oauth_verifier': oauth_verifier}) 
       oauth_request.sign_request(signature_method, consumer, auth_token) 
       # now the token we get back is an access token 
       # parse the response into an OAuthToken object 
       access_token = oauth.OAuthToken.from_string(self.FetchResponse(oauth_request,connection)) 
   
       # store the access token when returning it 
       access_token = access_token.to_string() 
       return access_token
   
    def ApiCall(self, access_token, apiCall='/1/user/-/activities/log/steps/date/today/7d.json'):
        #other API Calls possible, or read the FitBit documentation for the full list.
        #apiCall = '/1/user/-/devices.json' 
        #apiCall = '/1/user/-/profile.json' 
        #apiCall = '/1/user/-/activities/date/2011-06-17.json'
        
        signature_method = oauth.OAuthSignatureMethod_PLAINTEXT() 
        connection = httplib.HTTPSConnection(self.SERVER) 
        #build the access token from a string
        access_token = oauth.OAuthToken.from_string(access_token)
        consumer = oauth.OAuthConsumer(self.CONSUMER_KEY, self.CONSUMER_SECRET)  
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=access_token, http_url=apiCall) 
        oauth_request.sign_request(signature_method, consumer, access_token) 
        headers = oauth_request.to_header(realm='api.fitbit.com') 
        connection.request('GET', apiCall, headers=headers) 
        resp = connection.getresponse() 
        json = resp.read() 
        return json