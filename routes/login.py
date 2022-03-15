"""
OP is wallet/holder
RP is verifier
"""

import json
from datetime import timedelta, datetime
import didkit
from jwcrypto import jwk
from flask import Flask, jsonify, request, Response, render_template, redirect, render_template_string
from flask_qrcode import QRcode
from datetime import timedelta, datetime
import logging
import secrets 
import uuid
from urllib.parse import urlencode
from jwcrypto import jwk
import jwt  # pip install pyjwt
import sys

#app = Flask(__name__)
#qrcode = QRcode(app)

logging.basicConfig(level=logging.INFO)
OFFER_DELAY = timedelta(seconds= 10*60)

# key 
keys_file = open('keys.json')
keys = json.load(keys_file)
keys_file.close()

# use of RSA key to sign RP request
key_dict = keys['keys']['did:web:talao.co#key-2']
DID = "did:web:talao.co"
KID = DID + "#key-2"
key1 = jwk.JWK(**key_dict)
KEY_PEM = key1.export_to_pem(private_key=True, password=None).decode() # private key pem


def init_app(app,red, mode) :
    app.add_url_rule('/gaiax/login',  view_func=gaiax_login, methods = ['GET'])
    app.add_url_rule('/gaiax/login/<id>',  view_func=gaiax_login_id, methods = ['GET', 'POST'], defaults={'red' :red, 'mode' : mode})
    app.add_url_rule('/gaiax/login_redirect/<id>',  view_func=gaiax_login_redirect, methods = ['POST'], defaults={'red' :red})
    app.add_url_rule('/gaiax/login_followup',  view_func=login_followup, methods = ['GET', 'POST'], defaults={'red' :red})
    app.add_url_rule('/gaiax/login_stream',  view_func=login_stream, methods = ['GET', 'POST'], defaults={ 'red' : red})
    app.add_url_rule('/gaiax/login_request_uri/<id>',  view_func=login_request_uri, methods = ['GET', 'POST'], defaults={ 'red' : red})
    print('init routes login done')
    return

# request endpoint (request_uri)
def login_request_uri(id, red):
    encoded = red.get(id + "_encoded").decode()
    return jsonify(encoded)


# main entry
def gaiax_login() :
    id = str(uuid.uuid1())
    return redirect('/gaiax/login/' + id)


# login with dynamic endpoint
def gaiax_login_id(id, red, mode) :
    # Request claims
    try :
        claims_file = open('claims.json')
        claims = json.load(claims_file)
        claims_file.close()
    except :
        print("claims file problem")
        sys.exit()

    # RP registration parameters
    try :
        registration_file = open('registration.json')
        registration = json.load(registration_file)
        registration_file.close()
    except :
        print("registration file problem")
        sys.exit()

    nonce = secrets.token_urlsafe()[0:10]
    login_request = {
                "scope" : "openid",
                "response_type" : "id_token",
                "client_id" : "did:web:talao.co",
    	        "redirect_uri" : mode.server + "gaiax/login_redirect/" + id,
    	        "response_mode" : "post",
    	        "claims" : json.dumps(claims, separators=(',', ':')),
    	        "nonce" : nonce,
                "registration" : json.dumps(registration, separators=(',', ':')),
                "request_uri" : mode.server + "gaiax/login_request_uri/" + id,
    }
    print('login request = ', login_request)
    
    # Request header for request_uri value
    jwt_header = {
        "typ" :"JWT",
        "kid": KID
    }
    # Request signed by RP as a JWT with did:web:talao.co
    login_request_encoded = jwt.encode(login_request, KEY_PEM, algorithm="RS256",  headers=jwt_header)
    red.set(id + "_encoded", login_request_encoded)
    
    # QR code and universal link
    red.set(id, json.dumps(login_request))
    RP_request = "openid://?" + urlencode(login_request)
    universal_link = mode.deeplink + 'app/download?' + urlencode({'uri' : RP_request })
    return render_template('gaiax_login.html',
                                url=RP_request,
                                id=id,
                                encoded=login_request_encoded,
                                deeplink=universal_link
                                )


"""
redirect_uri : Endpoint for OP response

"""
async def gaiax_login_redirect(id, red) :
    try : 
        login_request = red.get(id).decode()
        nonce = json.loads(login_request)['nonce']
    except :
        return jsonify('server error'), 500
    
    # if user has aborted the process
    if request.form.get('error') :
        event_data = json.dumps({"id" : id,
                             "check" : "ko",
                             "message" : request.form.get('error_description', "Unknown")
                             })   
        red.publish('gaiax_login', event_data)
        return jsonify("ko, user has aborted the process !"),500
    
    try :
        id_token = request.form['id_token']
        vp_token = request.form['vp_token']
    except :
        event_data = json.dumps({"id" : id,
                         "check" : "ko",
                         "message" : "Response malformed"
                         })   
        red.publish('gaiax_login', event_data)
        return jsonify("Response malformed"),500

    error = str()
    error += await test_vp_token(vp_token, nonce)
    error += test_id_token(id_token, nonce)
    if error :    
        event_data = json.dumps({"id" : id,
                                "check" : "ko",
                                "message" : error
                                })   
        red.publish('gaiax_login', event_data)
        return jsonify("ko, signature verification failed !"),500

    # just to say its fine your are logged in !
    event_data = json.dumps({"id" : id,
                         "check" : "success",
                         })   
    red.publish('gaiax_login', event_data)
    return jsonify("Ciongrats ! Everything is ok"), 200


async def test_vp_token(vp_token, nonce) :
    didkit_options = {
            "proofPurpose": "authentication",
            "verificationMethod": "did:web:ecole42.talao.co#key-1",
            "challenge" : nonce
    }
    error = str()
    result = await didkit.verify_presentation(vp_token, json.dumps(didkit_options))
    if json.loads(result)['errors'] :
        error += "VP signature error , didkit result = " + result + "<br>"
    if json.loads(vp_token)['verifiableCredential']['credentialSubject']['type'] != "GaiaxPass" :
        error += "VC type error <br>"
    if json.loads(vp_token)['proof']['challenge'] != nonce :
        error += "Different nonce/challenge in VC <br>"
    if json.loads(vp_token)['verifiableCredential']['issuer'] != "did:web:talao.co" :
        error += "VC issuer error <br>"
    return error


async def test_id_token(id_token, nonce) :
    id_token_kid = jwt.get_unverified_header(id_token)['kid']
    id_token_did = id_token_kid.split('#')[0] 
    did_document = json.loads(await didkit.resolveDid(id_token_did, '{}'))['didDocument']
    # extract public key JWK
    public_key = str()
    error = str()
    for key in did_document['verificationMethod'] :
        if key['id'] == id_token_kid :
            public_key = json.dumps(key['publicKeyJwk'])
            break
    if not public_key :
        error += "public key not found in DID Document <br>"
    try :
        op_key_pem = jwk.JWK(**json.loads(public_key)).export_to_pem(private_key=False, password=None).decode()
        id_token = jwt.decode(id_token, op_key_pem, audience="did:web:talao.co", algorithms=["RS256", "ES256", "ES256K", "EdDSA", "PS256"])
    except :
        error = "error decode Id token or audience issue <br>"
    if not id_token.get('iat') :
        error += "iat is missing in id token<br> "
    if not id_token.get('exp') :
        error += "exp is missing in id token <br>"
    if round(datetime.timestamp(datetime.now())) > id_token.get('exp', 0) :
        error += "id token is expired <br>"
    if id_token.get('sub') != id_token_did :
        error += "sub is wrong or missing in id token <br>"
    if id_token.get('i_am_siop') != True :
        error += "I_am_siop is missing in id token <br>"
    if id_token.get('nonce') != nonce :
        error += "nonce is missing in id token <br>"
    return error


# This is to get a feedback from the wallet and display id_token and vp_token
def login_followup(red) :
    if request.args.get('message') :
        html_string = """  <!DOCTYPE html>
            <html>
            <body>
            <center>  
                <h1> Talao gaiax login</h1>
                <h2>Problems occured</h2>
                <h4> {{message|safe}} </h4>
                 <form   action="/gaiax/login" method="GET">
                <br><br>
                <button type="submit">Return</button>
                </form>
            </center>
            </body>
            </html>"""
        return render_template_string(html_string, message=request.args.get('message'))

    #id = request.args['id']
    html_string = """  <!DOCTYPE html>
        <html>
        <body>
            <center>  
                <h1> Talao gaiax login</h1>
                <h2> Congrats ! </h2>
                <h2> You are logged in </h2>
                 <form   action="/gaiax/login" method="GET">
                <br><br>
                <button type="submit">Return</button>
                </form>
            </center>
        </body>
        </html>"""
    return render_template_string(html_string)


# Event stream to manage the front end page
def login_stream(red):
    def login_event_stream(red):
        pubsub = red.pubsub()
        pubsub.subscribe('gaiax_login')
        for message in pubsub.listen():
            if message['type']=='message':
                yield 'data: %s\n\n' % message['data'].decode()
    headers = { "Content-Type" : "text/event-stream",
                "Cache-Control" : "no-cache",
                "X-Accel-Buffering" : "no"}
    return Response(login_event_stream(red), headers=headers)