import fitbit

z = fitbit.Fitbit();

# Get the authorization URL for user to complete in browser.
auth_url = z.GetAuthorizationUri()
print "Please visit %s and approve the app." % auth_url

# Set the access code that is part of the arguments of the callback URL FitBit redirects to.
access_code = raw_input("Please enter code (from the URL you were redirected to): ")

# Use the temporary access code to obtain a more permanent pair of tokens
access_token, refresh_token = z.GetAccessToken(access_code)

# Sample API call
response, status_code = z.ApiCall(access_token, '/1/user/-/profile.json')

if status_code == 200:
    print "Looks like everything is working, right %s? " % response['user']['displayName']
elif status_code == 404:
    print "You requested an API that doesn't exist."
elif status_code == 403:
    print "You requested an API you don't have access to. Make sure to check the scope"
elif status_code == 401:
    print "The access token you provided has been expired let me refresh that for you."
    # Refresh the access token with the refresh token if expired. Access tokens should be good for 1 hour.
    access_token, refresh_token = z.RefAccessToken(refresh_token)
else:
    print "Oops. Something else went wrong (code %i), refer to the docs." % status_code
