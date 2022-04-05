
def get_auth_url():
    weibo_auth_url="https://api.weibo.com/oauth2/authorize"
    redirect_url="http://149.129.53.199:8000/complete/weibo/"
    auth_url=weibo_auth_url+"?client_id={client_id}&redirect_uri={re_url}".format(client_id=1717642557,re_url=redirect_url)


    print(auth_url)

def get_access_token(code="5fb3502eabd953894c65cdc738cc70c6"):
    access_token_url="https://api.weibo.com/oauth2/access_token"
    import requests
    re_dict = requests.post(access_token_url,data={
        "client_id":1717642557,
        "client_secret":"1782eedd819f90e9455c1c97feec6e17",
        "grant_type":"authorization_code",
        "code":code,
        "redirect_uri":"http://149.129.53.199:8000/complete/weibo/"
    })
    pass

def get_user_info(access_token="",uid=""):
    user_url="https://api.weibo.com/2/users/show.json?access_token={token}&uid={uid}".format(token=access_token,uid=uid)
    print(user_url)

if __name__=="__main__":
    # get_auth_url()
    # get_access_token(code="5fb3502eabd953894c65cdc738cc70c6")

    get_user_info(access_token = "2.00VZhewGNSDPsB9fc4b102c80gjqoq",uid="6363525093")
