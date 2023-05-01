"""
Spotify API Authorization and Connection
"""

import requests
import time

from app import app

"""
Requests an access token from the Spotify API. Only called if no refresh token for the
current user exists.
Returns: either [access token, refresh token, expiration time] or None if request failed
"""
def getToken(code):
	token_url = 'https://accounts.spotify.com/api/token'
	authorization = app.config['AUTHORIZATION']
	redirect_uri = app.config['REDIRECT_URI']
	headers = {'Authorization': authorization, 
            'Accept': 'application/json', 
            'Content-Type': 'application/x-www-form-urlencoded'}
	body = {'code': code, 'redirect_uri': redirect_uri, 
        	'grant_type': 'authorization_code'}
	post_response = requests.post(token_url,headers=headers,data=body)
	if post_response.status_code == 200:
		pr = post_response.json()
		return pr['access_token'], pr['refresh_token'], pr['expires_in']
	else:
		logging.error('getToken:' + str(post_response.status_code))
		return None



"""
Determines whether new access token has to be requested because time has expired on the 
old token. If the access token has expired, the token refresh function is called. 
Returns: None if error occured or 'Success' string if access token is okay
"""
def checkTokenStatus(session):
	if time.time() > session['token_expiration']:
		payload = refreshToken(session['refresh_token'])

		if payload != None:
			session['token'] = payload[0]
			session['token_expiration'] = time.time() + payload[1]
		else:
			logging.error('checkTokenStatus')
			return None

	return "Success"



"""
Makes a GET request with the proper headers. If the request succeeds, the json parsed
response is returned. If the request fails because the access token has expired, the
check token function is called to update the access token.
Returns: Parsed json response if request succeeds or None if request fails
"""
def makeGetRequest(session, url, params={}):
	headers = {"Authorization": "Bearer {}".format(session['token'])}
	response = requests.get(url, headers=headers, params=params)

	# 200 code indicates request was successful
	if response.status_code == 200:
		return response.json()

	# if a 401 error occurs, update the access token
	elif response.status_code == 401 and checkTokenStatus(session) != None:
		return makeGetRequest(session, url, params)
	else:
		logging.error('makeGetRequest:' + str(response.status_code))
		return None


# Spotify API requests
"""
Get information about a sound track using track ID
Returns: a json object representing the track
"""
def getTrack(session, track_id):
	request_url = 'https://api.spotify.com/v1/tracks/'
	params = {'id': track_id}

	track_data = makeGetRequest(session, request_url, params)
	print(track_data)

	if track_data == None:
		print("track data is none")
		return None
	
	return track_data




	

	

