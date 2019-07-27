# Smart License Dashboard

The dashboard is a web application consisting of VueJS frontend and a flask backend.  There is also a Redis database used for caching data from API servers, as well as sessions and tokens. 

### API Structure

The backend provides an api for the web page where data access is keyed to a session id stored on the frontend. This session id is linked to the session as it is passed through to the backend from the frontend through the Cisco SSO server. 

Another api is provided to allow the Smart Licensing Bot to obtain access tokens. The bot passes the room id and person id associated with a Webex Teams user, and the backend returns the associated token. This api is secured using a shared key between the services. The backend is aware of the room id and person id as one of its actions upon authenticating is to create a Webex Teams room for that user.

It is possible to create a Webex Teams room for the user by using a Teams bot token and their email address.  The backend obtains the users email address through the SSO api, specifically with the OpenID api.

### Caching

When a user logs in, their data is cached to make future requests faster. This is accomplished with [Redis](https://redis.io/). Redis is an in-memory key-value store. It was explicitly designed as a fast storage for temporary data. In theory this could be scaled up into a Redis cluster, if the number of users was expected to increase. Operating at large scale is one of its design principles.


Currently there is no TTL strategy for the cache. That is one of the planned work items as part of further enhancements to the caching strategy.

### OAuth

The app authenticates with Cisco SSO using the Authorization Code grant. This requires the following interactions:

1. Send a request to the OAuth server for an authorization code, with the client id and a preregistered redirect_url.
2. The SSO site takes the users credentials, and sends an api call to the redirect_url with the authorization code.
3. The server takes the authorization code, and requests an access token from the SSO server by sending the code, the client_id, the client secret, the redirect_url, and the grant type.
4. The SSO system returns a token. 
5. We perform an extra step: Use the token to request the user's email, as we previously included the email scope in the authorization code request.

The benefit of this approach is that the Web Page can initiate authentication without the backend, but without exposing the client secret in the Javascript, given the inherent vulnerability of Javascript.

### Frontend

The user interface is built on the framework [VueJs](https://vuejs.org/). The benefit of this framework is that it brings much of the power of frameworks like Angular and React, but has a significantly easier learning curve. In addition the community is large enough that a plethora of libraries exist for the framework. 

