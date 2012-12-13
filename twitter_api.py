from rauth.service import OAuth1Service #see https://github.com/litl/rauth for more info
import shelve #for persistent caching of tokens, hashes,etc.
import time
import datetime 
#get your own consumer key and secret after registering a desktop app here: 
#https://dev.twitter.com/apps/new
#for more details on the API: https://dev.twitter.com/docs/api/1.1

class Twitter:
    def __init__(self,consumer_key,consumer_secret,verbose=0,cache_name='tokens.dat'):
        #cache stores tokens and hashes on disk so we avoid
        #requesting them every time.
        self.cache=shelve.open(cache_name,writeback=False)
        self.verbose=verbose        
        self.oauth=OAuth1Service(
                name='twitter',
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                request_token_url='https://api.twitter.com/oauth/request_token',
                access_token_url='https://api.twitter.com/oauth/access_token',
                authorize_url='https://api.twitter.com/oauth/authorize',
                header_auth=True)

        self.access_token = self.cache.get('twitter_access_token',None)
        self.access_token_secret = self.cache.get('twitter_access_token_secret',None)
        self.request_token =  self.cache.get('twitter_request_token',None)
        self.request_token_secret =  self.cache.get('twitter_request_token_secret',None)
        self.encoded_user_id =  self.cache.get('twitter_encoded_user_id',None)
        self.pin= self.cache.get('twitter_pin',None)
        
        #If this is our first time running- get new tokens 
        if (self.need_request_token()):
            self.get_request_token()
            got_access_token=self.get_access_token()
            if( not got_access_token):
                print "Error: Unable to get access token"
                    

    def dbg_print(self,txt):
        if self.verbose==1:
            print txt

    def get_request_token(self):
        self.request_token,self.request_token_secret = self.oauth.get_request_token(method='GET',params={'oauth_callback':'oob'})
        authorize_url=self.oauth.get_authorize_url(self.request_token)
        #the pin you want here is the string that appears after oauth_verifier on the page served
        #by the authorize_url
        print 'Visit this URL in your browser then login: ' + authorize_url
        self.pin = raw_input('Enter PIN from browser: ')
        self.cache['twitter_request_token']=self.request_token
        self.cache['twitter_request_token_secret']=self.request_token_secret
        self.cache['twitter_pin']=self.pin
        print "twitter_pin is ",self.cache.get('twitter_pin')

    def need_request_token(self):
        #FIXME: think of a better way to do this
        if (self.request_token==None) or (self.request_token_secret==None) or (self.pin==None):
            return True
        else:
            return False

    def get_access_token(self):
        response=self.oauth.get_access_token('GET',
                request_token=self.request_token,
                request_token_secret=self.request_token_secret,
                params={'oauth_verifier':self.pin})
        data=response.content
        print response.content
        self.access_token=data.get('oauth_token',None)
        self.access_token_secret=data.get('oauth_token_secret',None)
        self.encoded_user_id = data.get('encoded_user_id',None)
        self.cache['twitter_access_token']=self.access_token
        self.cache['twitter_access_token_secret']=self.access_token_secret
        self.cache['encoded_user_id']=self.encoded_user_id
        if not(self.access_token) or not(self.access_token_secret):
            print "access token expired "
            return False
        else:
            return True

    
    def search(self,search_string):
        """Returns tweets associated with specified string """
        params={'q':search_string}
        response=self.oauth.get(
                'https://api.twitter.com/1.1/search/tweets.json',
                params=params,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                header_auth=True)
        return response.response.json

    def list_friends(self,**kwargs):
        """Returns collection of users that the specified user_id or screen_name is following"""
        #user_id=None,screen_name=None,cursor=None,skip_status=None,include_user_entities=None
        params = {}
        for key in kwargs:
            params[key]=kwargs.get(key)

        response=self.oauth.get(
                'https://api.twitter.com/1.1/friends/list.json',
                params=params,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                header_auth=True)
        return response.response.json

    def create_friendships(self,user_id=None,screen_name=None):
        """Makes currently authenticated user follow the specified user_id or screen_name"""
        params ={'follow':'true'}
        if user_id is not None:
            params['user_id'] = user_id
        else:
            params['screen_name'] = screen_name

        response=self.oauth.post(
            'http://api.twitter.com/1.1/friendships/create.json',
            params=params,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            header_auth=True)
        return response.json
