"""

this wallet supports demo.talao.co
didtkit 0.4.0 async

"""


from flask import Flask, request, render_template_string, jsonify, redirect
from flask_qrcode import QRcode
import socket
import jwt
import requests
import json
from urllib.parse import parse_qs
from jwcrypto import jwk
from datetime import datetime
import didkit

app = Flask(__name__)
qrcode = QRcode(app)

# Wallet keys for signing
KEY_JWK = open("demo_key.json").read() # to sign with Didkit
KEY_PEM = jwk.JWK(**json.loads(KEY_JWK)).export_to_pem(private_key=True, password=None).decode() # to sign JWT
PUBLIC_KEY_PEM = jwk.JWK(**json.loads(KEY_JWK)).export_to_pem(private_key=False, password=None).decode() # to sign JWT
DID = "did:web:demo.talao.co"
KID ="did:web:demo.talao.co#key-1"
KTY = "RS256"

"""
Main page
Copy the Request from the verifier then it starts the process 

"""
@app.route('/' , methods=['GET', 'POST']) 
async def wallet() :
  if request.method == 'GET' :
    html_string = """  <!DOCTYPE html>
        <html>
        <body>
        <center>
            <h1>Wallet simulator for siopv2 protocol flow<h1> 
                <h3>Copy the verifier Request here</h3> 
                <br><br>
                <form   action="/" method="POST">
                <textarea required name="verifier_request" cols="100" rows="20" cols="33"></textarea> 
                <br><br>
                <p> Wallet DID = <input name="did" value={{did}}><br> </p>
                <p>Wallet Verification method =  <input name="vm" value={{vm}}><br></p>
                <p>Wallet Key type =  <input name="kty" value={{kty}}><br></p>
               

                <button type="submit">Next</button>
                </form>
        </center>
        </body>
        </html>"""    
    return render_template_string(html_string, did=DID, vm=KID, kty=KTY)
  # POST
  verifier_request = request.form['verifier_request']
  if not verifier_request :
    return redirect('/')
  try :
    authentication_request = parse_qs(verifier_request)
    nonce = authentication_request['nonce'][0]
    redirect_uri = authentication_request['redirect_uri'][0]
    client_id = authentication_request['client_id'][0]
    claims = authentication_request['claims'][0]
  except : 
    data = "error=invalid_request&error_description=Unsupported%20response_type%20value"
    headers = {
      'accept': 'application/json',
      'Content-Type': 'application/x-www-form-urlencoded',
      }
    #resp = requests.post(redirect_uri, headers=headers, data=data)
    return jsonify('invalid request')

  id_token = build_id_token(nonce, client_id)
  signed_credential = open("./signed_credentials/test_emailpass.jsonld").read()
  vp_token = await build_vp_token(nonce, signed_credential)
  #print('vp token = ', vp_token)
  #print('id token = ', id_token)
  # TODO on download la request signée
  # TODO on verifie que la request est signée correctement
  # TODO analyse "claims" avec PEX vocab, recherche du VC
  result =  send_response(id_token, vp_token, redirect_uri)
  html_string = """  <!DOCTYPE html>
        <html>
        <body>
        <center>
            <h1>Wallet - SIOPv2<h1> 
                <h3>{{result}} </h3> 
                <br>
                <form   action="/" method="GET">
                <br><br>
                <button type="submit">Return</button>
                </form>
        </center>
        </body>
        </html>"""    
  return render_template_string(html_string, result=result)


"""
Build id_token for OP, dynamic
https://openid.net/specs/openid-connect-self-issued-v2-1_0-06.html
"""
def build_id_token(nonce, client_id) :
  header = {
    "typ" :"JWT",
    "kid": KID
  }
  payload = {
    "iat": round(datetime.timestamp(datetime.now())),
    "aud" : client_id,
    "exp": round(datetime.timestamp(datetime.now())) + 1000,
    "sub" : DID,
    "i_am_siop" : True,
    "nonce": nonce
  }
  id_token_encoded = jwt.encode(payload, KEY_PEM, algorithm="RS256",  headers=header)
  #id_token = jwt.decode(id_token_encoded, PUBLIC_KEY_PEM,  audience=client_id, algorithms=["RS256"])
  return id_token_encoded



"""
Build and sign verifiable presenttation as vp_token
Ascii is by default in the json string 
"""
async def build_vp_token(nonce, signed_credential) :
  didkit_options = {
        "proofPurpose": "authentication",
        "verificationMethod": KID,
        "challenge" : nonce
        }
  verifiable_presentation = json.dumps({
            "@context": ["https://www.w3.org/2018/credentials/v1"],
            "id": "http://example.org/presentations/3731",
            "type": ["VerifiablePresentation"],
            "holder": DID,
            "verifiableCredential": json.loads(signed_credential)
            })
  vp_token = await didkit.issue_presentation(verifiable_presentation,
                                       didkit_options.__str__().replace("'", '"'),
                                       KEY_JWK)
  return json.dumps(json.loads(vp_token))

"""
send response to verifier

"""
def send_response(id_token, vp_token, redirect_uri) :
  headers = {
    'accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded',
    }
  data = "id_token="+ id_token + "&vp_token=" + vp_token
  resp = requests.post(redirect_uri, headers=headers, data=data)
  if resp.status_code == 200 :
    return resp.json()


def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:       
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP


# MAIN entry point. Flask http server
if __name__ == '__main__':
    # to get the local server IP 
    IP = extract_ip()
    # server start
    app.run(host = IP, port= 4000, debug=True)