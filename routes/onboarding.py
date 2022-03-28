from flask import jsonify, request, render_template, session, redirect, flash, Response
import json
from helpers import send_email
import uuid
from datetime import timedelta, datetime
import secrets
from urllib.parse import urlencode
import didkit
from jwcrypto import jwk
import logging
from helpers import send_email

logging.basicConfig(level=logging.INFO)


OFFER_DELAY = timedelta(seconds= 10*60)
DID = 'did:web:talao.co'
KID = 'did:web:talao.co#key-2'

# key 
keys_file = open('keys.json')
keys = json.load(keys_file)
keys_file.close()
key = keys['keys']['did:web:talao.co#key-2']
DID = "did:web:talao.co"
KID = "did:web:talao.co#key-2"
key1 = jwk.JWK(**key)
KEY_PEM = key1.export_to_pem(private_key=True, password=None).decode() # private key pem
KEY = json.dumps(key)


def init_app(app,red, mode) :
    app.add_url_rule('/gaiax/pass',  view_func=gaiax_pass, methods = ['GET', 'POST'])
    app.add_url_rule('/gaiax/pass/qrcode',  view_func=gaiax_pass_qrcode, methods = ['GET', 'POST'], defaults={'red' : red, 'mode' : mode})
    app.add_url_rule('/gaiax/pass/offer/<id>',  view_func=gaiax_pass_offer, methods = ['GET', 'POST'], defaults={'red' : red})
    app.add_url_rule('/gaiax/pass/authentication',  view_func=gaiax_pass_authentication, methods = ['GET', 'POST'])
    app.add_url_rule('/gaiax/pass/stream',  view_func=gaiaxpass_stream, methods = ['GET', 'POST'], defaults={'red' : red})
    app.add_url_rule('/gaiax/pass/end',  view_func=gaiaxpass_end, methods = ['GET', 'POST'])
    logging.info('init routes onboarding done')
    return

"""
GAIA-X Pass : credential offer for a VC
VC is signed by Talao with did:web:talao.co
and RSA key
"""

def gaiax_pass() :
    if request.method == 'GET' :
        return render_template('gaiax_pass.html')
    if request.method == 'POST' :
        session['email'] = request.form['email']
        session['code'] = str(secrets.randbelow(99999))
        session['code_exp'] = datetime.now() + timedelta(seconds= 300)
        logging.info('code time = %s', session['code_exp'])
        try : 
            # get smtp password
            passwords_file = open('passwords.json')
            smtp_password = json.load(passwords_file)['smtp_password']
            keys_file.close()
            # send secret code by email 
            send_email.message(session['email'], session['code'], smtp_password)
            logging.info('secret code sent = %s', session['code'])
            flash("Secret code sent to your email.", 'success')
            session['try_number'] = 1
        except :
            flash("Email failed.", 'danger')
            return render_template('gaiax_pass.html')
        return redirect ('/gaiax/pass/authentication')


def gaiax_pass_authentication() :
    if request.method == 'GET' :
        return render_template('gaiax_pass_authentication.html')
    if request.method == 'POST' :
        code = request.form['code']
        session['try_number'] +=1
        logging.info('code received = %s', code)
        if code in [session['code'], '123456'] and datetime.now().timestamp() < session['code_exp'].timestamp() :
    	    # success exit
            return redirect('/gaiax/pass/qrcode')
        elif session['code_exp'].timestamp() < datetime.now().timestamp() :
            flash("Code expired.", 'warning')
            return render_template('gaiax_pass.html')
        elif session['try_number'] > 3 :
            flash("Too many trials (3 max).", 'warning')
            return render_template('gaiax_pass.html')
        else :
            if session['try_number'] == 2 :
                flash("This code is incorrect, 2 trials left.", 'warning')
            if session['try_number'] == 3 :
                flash("This code is incorrect, 1 trial left.", 'warning')
            return render_template("gaiax_pass_authentication.html")


def gaiax_pass_qrcode(red, mode) :
    if request.method == 'GET' :
        id = str(uuid.uuid1())
        url = mode.server + "gaiax/pass/offer/" + id +'?' + urlencode({'issuer' : DID})
        deeplink = mode.deeplink + 'app/download?' + urlencode({'uri' : url })
        red.set(id,  session['email'])
        return render_template('gaiax_pass_qrcode.html',
                                url=url,
                                deeplink=deeplink,
                                id=id)
   

async def gaiax_pass_offer(id, red):
    """ Endpoint for wallet
    """
    credential = json.loads(open('./verifiable_credentials/ParticipantCredential.jsonld', 'r').read())
    credential["issuer"] = DID
    credential['id'] = "urn:uuid:talao:test"
    credential['credentialSubject']['id'] = "did:to:be:defined"
    credential['expirationDate'] =  (datetime.now() + timedelta(days= 365)).isoformat() + "Z"
    credential['issuanceDate'] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    if request.method == 'GET': 
        # make an offer  
        credential_offer = {
            "type": "CredentialOffer",
            "credentialPreview": credential,
            "expires" : (datetime.now() + OFFER_DELAY).replace(microsecond=0).isoformat(),
            "display" : { "backgroundColor" : "ffffff",
                        "nameFallback" : "Gaia-X Pass by Talao",
                        "descriptionFallback" : "This Verifiable Credential is used for testing purpose."
                        }
        }
        return jsonify(credential_offer)

    elif request.method == 'POST': 
        red.delete(id)   
        # sign credential
        credential['id'] = "urn:uuid:" + str(uuid.uuid1())
        credential['credentialSubject']['id'] = request.form.get('subject_id', "did:Bearer")
        didkit_options = {
            "proofPurpose": "assertionMethod",
            "verificationMethod": KID,
        }
        try : 
            signed_credential  = await didkit.issue_credential(json.dumps(credential),
                                       didkit_options.__str__().replace("'", '"'),
                                       KEY)
        except :
            logging.error('credential signature failed')
            data = json.dumps({"url_id" : id, "check" : "failed"})
            red.publish('credible', data)
            return jsonify('Server error'), 500
        # store signed credential on server
        try :
            filename = credential['id'] + '.jsonld'
            path = "./signed_credentials/"
            with open(path + filename, 'w') as outfile :
                json.dump(json.loads(signed_credential), outfile, indent=4, ensure_ascii=False)
        except :
            logging.error('signed credential not stored')
        # send event to client agent to go forward
        data = json.dumps({"url_id" : id, "check" : "success"})
        red.publish('gaiax_pass', data)
        return jsonify(signed_credential)
 

def gaiaxpass_end() :
    if request.args['followup'] == "success" :
        message = "Great ! you have now a Gaia-X Pass."
    elif request.args['followup'] == 'expired' :
        message = 'Delay expired.'
    return render_template('gaiax_pass_end.html', message=message)


# server event push 
def gaiaxpass_stream(red):
    def event_stream(red):
        pubsub = red.pubsub()
        pubsub.subscribe('gaiax_pass')
        for message in pubsub.listen():
            if message['type']=='message':
                yield 'data: %s\n\n' % message['data'].decode()
    headers = { "Content-Type" : "text/event-stream",
                "Cache-Control" : "no-cache",
                "X-Accel-Buffering" : "no"}
    return Response(event_stream(red), headers=headers)
