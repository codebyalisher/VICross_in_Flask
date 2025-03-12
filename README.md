## GOOGLE OAUTH2 AUTHENTICATION
### step1:Google OAuth2 Configuration:
You're fetching the CLIENT_ID, CLIENT_SECRET, and REDIRECT_URI from the Flask app’s config. You should make sure that these configurations are set in your config.py or another secure location.

### step2:Getting the Authorization Code: 
Your API expects a POST request with the authorization code sent from the client (e.g., a frontend app). This is where you get the code sent to your API.

### step3:Exchange the Authorization Code for an Access Token:
You then send a request to Google's token endpoint (https://oauth2.googleapis.com/token) to exchange the authorization code for an access token.

### stpe4:Get User Information: 
With the access_token, you fetch the user's information (e.g., email, profile) from Google's userinfo endpoint.

### step 5:Return User Information: 
Finally, you return the user info in the response.