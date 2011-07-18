# A python library for the FitBit API

Didn't see one that fitted my needs so I build my own.

## Usage

Edit the fitbit.py file with your consumer key and secret.

	import fitbit
	z = fitbit.FitBit()

Make a request token:

	auth_url, auth_token = z.GetRequestToken()

Visit the auth_url and copy the PIN. Use the PIN to get an access token:

	access_token = z.GetAccessToken(PIN, auth_token)
	
Store the access_token for later usage. You can now call the API with it:

	response = z.ApiCall(access_token, apiCall='/1/user/-/activities/log/steps/date/today/7d.json')

All responses for the functions are received in JSON but are also available in XML.