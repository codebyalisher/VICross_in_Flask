# VI Cross in Flask

## Overview
This project is a Flask-based that supports Admin Dashboard , authentication, user management, company management, trade booths, and WebSocket communication. It utilizes SQLAlchemy for ORM, Flask-Migrate for migrations, and ImageKit for media storage. The backend is designed to work with a PostgreSQL database.

## Project Structure
```AdminDashboard_in_Flask/
├── AdminDashboard/
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── company_routes.py
│   │   ├── trade_booths_routes.py
│   │   ├── user_routes.py
│   │   ├── websockets_routes.py
│   │   ├── utils.py
│   │   └── image_kit.py
│   ├── models.py
│   └── __init__.py
├── migrations/
│   ├── versions/
│   ├── env.py
│   ├── alembic.ini
│   ├── README
│   └── script.py.mako
├── instance/
│   └── config.py
├── requirements.txt
└── README.md
```

## Authentication Routes
- `GET /auth/google_login_page_redirect`
- `GET /auth/google-oauth`
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/send-otp`
- `POST /auth/resend-otp`
- `POST /auth/verify-otp`
- `POST /auth/reset-password`
- `GET /auth/all-users-data`
- `PATCH /auth/assign-role`
- `GET /auth/google-oauth-login-authenticate`

## User Routes
- `PATCH /user/edit-user`
- `DELETE /user/delete-user`
- `GET /user/profile`

## Company Routes
- `POST /company/create-company`
- `PUT /company/update-company`
- `GET /company/get-details-companies`
- `GET /company/get-single-details-company`

## Trade Booth Routes
- `POST /tradebooth/create-tradebooth`
- `PUT /tradebooth/update-tradebooth`
- `GET /tradebooth/get-details-tradebooths`
- `GET /tradebooth/get-single-details-tradebooth`
- `GET /tradebooth/status`

## WebSocket Routes
- `GET /rooms`
- `POST /join-rooms`
- `GET /leave-room`

## Configuration
The configuration settings are located in the `instance/config.py` file.

## Database Models and Migrations
The project uses SQLAlchemy for defining models and Flask-Migrate for handling database migrations. The models are defined in the `AdminDashboard/routes/models.py` file.

## DB Setup
The project uses PostgreSQL as the database management system. Ensure you have PostgreSQL installed and configured properly.

## ImageKit for Media Storing
The project uses ImageKit for storing and managing media files. The `AdminDashboard/routes/image_kit.py` file contains the necessary configurations and functions for interacting with ImageKit.

## Dependencies
The dependencies for this project are listed in the `requirements.txt` file.

For more details, you can refer to the [project repository](https://github.com/codebyalisher/AdminDashboard_in_Flask).

## GOOGLE OAUTH2 AUTHENTICATION Flow
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

## There are folowing methods for OAUTH2.0 and the flow for each of them:
- **Web Application Flow:** Use this if you have a backend server.This is the most common flow for web applications where the backend server handles the OAuth process.

    **Use Case:**  
        Traditional web applications with a backend server.
        Requires server-side handling of the authorization code and tokens.
- **Client-Side Flow:** Use this for SPAs or mobile apps.This flow is used for single-page applications (SPAs) or mobile apps where the OAuth process happens on the client side.
  
  **Use Case:**  
        Single-page applications (SPAs) or mobile apps.
        No backend server is required to handle the OAuth process.

- **Server-to-Server Flow:** Use this for backend services accessing Google APIs.This flow is used for server-to-server communication where no user interaction is required.

    ***Steps:***
      
    ***Create a Service Account:*** Create a service account in the Google Cloud Console and download the JSON key file.
    ***Generate a JWT:*** Use the service account credentials to generate a JWT (JSON Web Token) with the required scopes and expiration time.
    ***Exchange JWT for Access Token:*** Send the JWT to Google's token endpoint to get an access token:
    ```example
    POST https://oauth2.googleapis.com/token
    Parameters:
    json
    {
      "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
      "assertion": "YOUR_JWT"
    }
    ```
    ***Use the Access Token:*** Use the access token to make API requests to Google.
    
     **Use Case:** Server-to-server communication (e.g., backend services accessing Google APIs).No user interaction is required.

- **Device Flow:** Use this for devices with limited input capabilities.This flow is used for devices that lack a browser or have limited input capabilities (e.g., smart TVs, printers).
  
    **Use Case:** Devices with limited input capabilities (e.g., smart TVs, printers).

- **Hybrid Flow:** Use this if you need both immediate and long-lived access.This flow combines the authorization code flow and implicit flow to provide both an access token and an authorization code.
  
  **Use Case:** Applications that need both immediate access (via the access token) and long-lived access (via the refresh token).

- **Incremental Authorization:** Use this to request additional permissions dynamically.This is not a separate flow but a feature that allows you to request additional scopes as needed.
  
   **Use Case:** Applications that need to request additional permissions dynamically.

### 1. Web Application Flow/OAuth 2.0 Flow (Manual Code Exchange)
**Overview:**
This method involves handling the entire OAuth 2.0 authorization process manually. You request the authorization code from Google, exchange it for an access token, and then use that token to retrieve user information.

**Flow:**
Request Authorization Code: The client is redirected to the Google OAuth consent page where they authorize your app to access their data.
- **Google Redirects Back:** Google redirects back to your app with an authorization code.
Exchange Authorization Code for Tokens: Your backend exchanges the authorization code for an access token (and optionally a refresh token) by making a POST request to Google's OAuth token endpoint.
- **Get User Info:** Once you have the access token, you make an authenticated request to Google’s user info API (e.g., userinfo) to retrieve user details (e.g., name, email).
- **Store Tokens:** Optionally, you can store the access token and refresh token for the user, and create a custom JWT token for internal authentication within your app.
- **Access Resources:** Use the access token to access Google APIs on behalf of the user.
- **Code Example:**  Here you manually handle the OAuth flow using Flask and the requests library to exchange codes and fetch tokens.

```backend in Flask
@bp.route('/google_login_page_redirect',methods=['GET'])
def google_login():
    CLIENT_ID = current_app.config['CLIENT_ID']    
    REDIRECT_URI = current_app.config['REDIRECT_URI']    
    authorization_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        "response_type=code&"
        "scope=openid%20email%20profile&"
        "access_type=offline&" 
        "prompt=consent" 
    )
    return jsonify({"status":status.HTTP_200_OK,"authorization_url": authorization_url}),status.HTTP_200_OK
```

```Redirect Ui
@bp.route('/google-oauth', methods=['GET'])
def google_oauth():
    """Authenticate the user using Google OAuth2.
    Call the /google-login above endpoint to get the authorization URL.
    Open the URL in your browser and log in with Google.
    After authentication, Google will redirect to your redirect_uri with the authorization code.
    Your backend will handle the redirect, exchange the code for an access token, and return the user info and JWT token.        
    """
    # Google OAuth2 Configuration (replace with your details)
    CLIENT_ID = current_app.config['CLIENT_ID']
    CLIENT_SECRET = current_app.config['CLIENT_SECRET']
    REDIRECT_URI = current_app.config['REDIRECT_URI']
    # Step 1: Get the authorization code from the client
    auth_code = request.args.get('code')
    if not auth_code:
        return jsonify({"status":status.HTTP_400_BAD_REQUEST,"message": "No authorization code found"}),status.HTTP_400_BAD_REQUEST
    # Step 2: Exchange the authorization code for an access token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    # Step 3: Make the request to Google to exchange code for token
    token_response = requests.post(token_url, data=token_data)
    if token_response.status_code != 200:
        return jsonify({"status":status.HTTP_400_BAD_REQUEST,"message": "Failed to get token from Google"}),status.HTTP_400_BAD_REQUEST    
    token_info = token_response.json()
    access_token = token_info.get('access_token')
    if not access_token:
        return jsonify({"status":status.HTTP_400_BAD_REQUEST,"message": "No access token received"}),status.HTTP_400_BAD_REQUEST
    # Step 4: Use the access token to get user information
    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    if user_info_response.status_code != 200:
        return jsonify({"status":status.HTTP_400_BAD_REQUEST,"message": "Failed to get user info from Google"}),status.HTTP_400_BAD_REQUEST
    user_info = user_info_response.json()
    jwt_token=generate_jwt_token(user_info)   #This token can then be used in subsequent API calls to authenticate the user, so you don't have to send the access token from Google every time 
    # Step 5: Return JWT token in the response
    return jsonify({
        "status": status.HTTP_200_OK,
        "message": "User authenticated successfully",
        "data": user_info,
        "access_token": jwt_token
    }), status.HTTP_200_OK
```

### 2. OAuth 2.0 Flow using Google OAuth Libraries
**Overview:**
This method involves using Google’s official libraries (google-auth-oauthlib, google-auth-httplib2) to simplify the OAuth flow. The libraries handle the token exchange, session management, and many of the complexities for you. 
- ***Links for furtthere details you can look:***  
       (https://google-auth-oauthlib.readthedocs.io/en/latest/reference/google_auth_oauthlib.flow.html),
       (https://googleapis.github.io/google-api-python-client/docs/oauth.html)

**Flow:**
- **Redirect to Google Authorization URL:** You redirect the user to Google’s OAuth consent screen using a URL generated by the Google OAuth library.
- **User Grants Permissions:** The user logs in and grants permissions to your app.
- **Google Redirects to Callback URL:** Google sends the user back to your specified redirect URI with an authorization code.
- **Exchange Code for Access Token:** The OAuth library exchanges the authorization code for an access token, and optionally a refresh token.
- **Get User Info:** The access token is used to make an authenticated request to Google’s API to retrieve user data.
- **Store Token:** The access token is stored in your app (in Flask's session, for instance), and you can use it for making subsequent requests to Google APIs.
- **Code Example:** This was the flow described in my first response using the google-auth and google-auth-oauthlib libraries. It simplifies OAuth token management and provides direct integration with Google's APIs.

## 3. Google Sign-In (Google Login API)
**Overview:**
Google Sign-In (or Google Login API) is a JavaScript-based solution for handling authentication on the client-side. This method is typically used for client-side web applications but can also be used with backend systems. It allows the user to log in with their Google account and fetch an ID token or access token directly from the client, which is then sent to your backend server to authenticate or authorize the user.
This method focuses more on client-side authentication, where Google takes care of the UI for login, and you only need to verify the token on your backend.

**Flow:**
- **Include Google Sign-In Button:** On your client-side (HTML/JavaScript), you include a Google Sign-In button that the user clicks to authenticate.
- **User Logs In with Google:** The user is presented with a Google login popup or page where they can authenticate and authorize your app.
- **Google Returns ID Token:** Upon successful login, Google returns an ID token (which contains user info) and possibly an access token (which can be used for accessing Google APIs).
- **Send ID Token to Backend:** The ID token (or access token) is sent to your backend server.
- **Backend Verifies ID Token:** On your backend, you verify the ID token using Google’s libraries (e.g., google-auth library). You can check the authenticity and extract user information (email, name, etc.).
- **Generate Custom Session or JWT Token:** Once verified, you can create a custom JWT token for internal authentication (if needed) or simply manage the session.
- **Code Example:**
  
```front end side
<!-- Include Google Sign-In JavaScript API -->
<script src="https://apis.google.com/js/platform.js" async defer></script>

<!-- Google Sign-In Button -->
<div class="g-signin2" data-onsuccess="onSignIn"></div>

<script>
  function onSignIn(googleUser) {
    // Get the Google ID token
    var id_token = googleUser.getAuthResponse().id_token;
    
    // Send the token to your backend
    fetch('/backend-login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ id_token: id_token })
    })
    .then(response => response.json())
    .then(data => {
      console.log("Login successful", data);
    })
    .catch(error => console.error('Error:', error));
  }
</script>
```
**in Flask ,Backend code Example:**
```backend
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from flask import Flask, request, jsonify

app = Flask(__name__)

# Replace with your Google Client ID
CLIENT_ID = 'YOUR_GOOGLE_CLIENT_ID'

@app.route('/backend-login', methods=['POST'])
def backend_login():
    # Get the ID token from the frontend
    id_token_from_client = request.json.get('id_token')
    
    try:
        # Verify the ID token
        id_info = id_token.verify_oauth2_token(id_token_from_client, Request(), CLIENT_ID)
        
        # Extract user information
        user_info = {
            "email": id_info.get("email"),
            "name": id_info.get("name"),
        }

        # Here you can generate your own session or JWT token, and send it back
        return jsonify({"status": "success", "user_info": user_info})
    except ValueError:
        # Invalid ID token
        return jsonify({"status": "error", "message": "Invalid ID token"}), 400

if __name__ == "__main__":
    app.run(debug=True)
```

### Choosing the Right Method
- **OAuth 2.0 Flow (Manual):** Best if you want full control over the OAuth flow, including token management and backend authentication.
- **OAuth 2.0 Flow (Google Libraries):** Best for simplifying OAuth token exchange and user authentication with Google, while offloading much of the work to Google’s libraries.
- **Google Sign-In API:** Best for client-side authentication when you want a simple Google login flow on the frontend (often used for single-page apps or apps where the backend just needs to verify user identity).
