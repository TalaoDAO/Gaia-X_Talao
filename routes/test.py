"""
SIOPV2 verifier

the wallet is the openID provider
The verifier is the relaying party

didkit 0.4.0 , async

"""

import json
from datetime import datetime
import didkit
from jwcrypto import jwk
from flask import jsonify, request, Response, render_template, render_template_string
from flask_qrcode import QRcode
import logging
import secrets 
import uuid
from urllib.parse import urlencode
from jwcrypto import jwk
import jwt  # pip install pyjwt
import sys


logging.basicConfig(level=logging.INFO)

# key 
keys_file = open('keys.json')
keys = json.load(keys_file)
keys_file.close()

# use of RSA key to sign RP request
key_dict = keys['keys']['did:web:talao.co#key-2']
DID = "did:web:talao.co"
KID = "did:web:talao.co#key-2"
key1 = jwk.JWK(**key_dict)
KEY_PEM = key1.export_to_pem(private_key=True, password=None).decode() # private key pem


def init_app(app,red, mode) :
    app.add_url_rule('/gaiax/siopv2/test',  view_func=siopv2_test, methods = ['GET', 'POST'], defaults={'red' : red, 'mode' : mode})
    app.add_url_rule('/gaiax/siopv2/test_redirect/<id>',  view_func=siopv2_test_redirect, methods = ['POST'], defaults={'red' :red})
    app.add_url_rule('/gaiax/siopv2/test_followup',  view_func=siopv2_followup, methods = ['GET', 'POST'])
    app.add_url_rule('/gaiax/siopv2/test_stream',  view_func=siopv2_test_stream, methods = ['GET', 'POST'], defaults={ 'red' : red})
    app.add_url_rule('/gaiax/siopv2/test_request_uri/<id>',  view_func=siopv2_request_uri, methods = ['GET', 'POST'], defaults={ 'red' : red})
    return

# request_uri endpoint
def siopv2_request_uri(id, red):
    encoded_request = red.get(id + "_encoded").decode()
    return jsonify(encoded_request)

# main entry
def siopv2_test(red, mode) :
    if not request.form.get('claims') :
        claims_id = "claims2" 
    else :
        claims_id = request.form['claims']
    id = str(uuid.uuid1())
    # Request claims and registration
    try :
        claims_file = open('test/' + claims_id + '.json')
        claims = json.load(claims_file)
        claims_file.close()
    except :
        logging.error("test file problem")
        sys.exit()

    nonce = secrets.token_urlsafe()[0:10]
    login_request = {
                "scope" : "openid",
                "response_type" : "id_token",
                "client_id" : "did:web:talao.co",
    	        "redirect_uri" : mode.server + "gaiax/siopv2/test_redirect/" + id,
    	        "response_mode" : "post",
    	        "claims" : json.dumps(claims, separators=(',', ':')),
    	        "nonce" : nonce,
                #"registration" : json.dumps(registration, separators=(',', ':')),
                "request_uri" : mode.server + "gaiax/siopv2/test_request_uri/" + id,
    }
    
    # Request header for request_uri value
    jwt_header = {
        "typ" :"JWT",
        "kid": KID
    }
    # Request signed by RP as a JWT with did:web:talao.co
    login_request_encoded = jwt.encode(login_request, KEY_PEM, algorithm="RS256",  headers=jwt_header)
    red.set(id + "_encoded", login_request_encoded)
    
    # QR code and universal link display
    red.set(id, json.dumps(login_request))
    RP_request = urlencode(login_request) # for desktop wallet
    url = "https://app.talao.co/authorization_endpoint?" + RP_request # for QR code 
    universal_link = url
    return render_template('siopv2_test.html',
                                url=url,
                                id=id,
                                encoded=login_request_encoded,
                                deeplink=universal_link,
                                request=RP_request,
                                claims=claims_id
                                )


"""
redirect_uri : Endpoint for OP response

"""
async def siopv2_test_redirect(id, red) :
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
        red.publish('pex_test', event_data)
        return jsonify("ko, user has aborted the process !"),500
    
    try :
        id_token = request.form['id_token']
        vp_token = request.form['vp_token']
    except :
        event_data = json.dumps({"id" : id,
                         "check" : "ko",
                         "message" : "Response malformed"
                         })   
        red.publish('pex_test', event_data)
        return jsonify("Response malformed"),500

    log = str()
    log += await test_vp_token(vp_token, nonce)
    log += await test_id_token(id_token, nonce)
    if log :    
        event_data = json.dumps({"id" : id,
                                "check" : "ko",
                                "message" : log
                                })   
        red.publish('pex_test', event_data)
        return jsonify("Signature verification failed !"),200

    # just to say its fine your are logged in !
    event_data = json.dumps({"id" : id,
                         "check" : "success",
                         })   
    red.publish('pex_test', event_data)
    return jsonify("Congrats ! Everything is ok"), 200


async def test_vp_token(vp_token, nonce) :
    vp = json.loads(vp_token)
    holder = vp['holder']
    vc = vp['verifiableCredential']
    if isinstance(vc, list) :
        vc = vc[0]
    error = str()
    vc_result = await didkit.verify_credential(json.dumps(vc), '{}')
    if json.loads(vc_result)['errors'] :
        error += "VP signature check  = " + vc_result + "<br>"
    else :
        logging.warning("VC signature check = %s", vc_result)

    vp_result = await didkit.verify_presentation(vp_token, '{}')
    if json.loads(vp_result)['errors'] :
        error += "VP signature check  = " + vp_result + "<br>"
    else :
        logging.warning("VP signature check = %s", vp_result)

    VC_type =  json.loads(vp_token)['verifiableCredential']['credentialSubject']['type']
    if VC_type != 'ParticipantCredential' :
        error += "VC type error = " + VC_type
        logging.error("VC type error")
    logging.info("VC type = %s", VC_type )
    if json.loads(vp_token)['proof']['challenge'] != nonce :
        error += "Different nonce/challenge in VC <br>"
    issuer = json.loads(vp_token)['verifiableCredential']['issuer'] 
    logging.info("VC issuer = %s", issuer)
    logging.info("VP holder = %s", holder)
    return error


async def test_id_token(id_token, nonce) :
    id_token_kid = jwt.get_unverified_header(id_token)['kid']
    id_token_unverified = jwt.decode(id_token, options={"verify_signature": False})
    aud = id_token_unverified.get('aud')
    logging.info("audience = %s", aud)
    id_token_did = id_token_kid.split('#')[0] 
    # get the DID Document
    did_document = json.loads(await didkit.resolve_did(id_token_did, '{}')) #['didDocument']
    # extract public key JWK
    public_key = str()
    error = str()
    for key in did_document['verificationMethod'] :
        if key['id'] == id_token_kid :
            public_key = json.dumps(key['publicKeyJwk'])
            break
    if not public_key :
        error += "public key not found in DID Document <br>"
    logging.info('wallet public key = %s', public_key)
    op_key_pem = jwk.JWK(**json.loads(public_key)).export_to_pem(private_key=False, password=None).decode()
    try :
        if aud :
            id_token = jwt.decode(id_token, op_key_pem, audience=aud, algorithms=["RS256", "ES256", "ES256K", "EdDSA", "PS256"])
        else :
            id_token = jwt.decode(id_token, op_key_pem, algorithms=["RS256", "ES256", "ES256K", "EdDSA", "PS256"])
    except :
        error += "error decode Id token <br>"
        return error
        
    if not id_token.get('iat') :
        error += "iat is missing in id token <br> "
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
def siopv2_followup() :
    if request.args.get('message') :
        html_string = """  <!DOCTYPE html>
            <html>
            <body>
            <center>  
                <h1> Talao gaiax login</h1>
                <h2>Here is the log</h2>
                <h4> {{message|safe}} </h4>
                 <form   action="/gaiax/siopv2/test" method="GET">
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
                <br><br>
                <h1> Talao gaiax login</h1>
                <h2> Congrats ! </h2>
                <h2> You are logged in </h2>
                 <form   action="/gaiax/siopv2/test" method="GET">
                <br><br>
                <button type="submit">Return</button>
                </form>
            </center>
        </body>
        </html>"""
    return render_template_string(html_string)


# Event stream to manage the front end page
def siopv2_test_stream(red):
    def login_event_stream(red):
        pubsub = red.pubsub()
        pubsub.subscribe('pex_test')
        for message in pubsub.listen():
            if message['type']=='message':
                yield 'data: %s\n\n' % message['data'].decode()
    headers = { "Content-Type" : "text/event-stream",
                "Cache-Control" : "no-cache",
                "X-Accel-Buffering" : "no"}
    return Response(login_event_stream(red), headers=headers)