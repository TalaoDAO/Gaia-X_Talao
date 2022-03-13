# Gaia-X - Talao

## The Talao wallet

This repository presents the use of Talao's SSI wallet for integration into the Gaia-X SSI environment. 

Talao is a company specializing in the development of SSI solutions since 2018 and contributing member of several W3V and DIF working groups. Talao is also a wallet provider. The Talao wallet is a smartphone application in production available on the Apple and Google stores, the wallet code is open source.

The specificity of the Talao SSI wallet is to be compatible with a large number of SSI identity and in particular did:tz, did:web, did:ethr, did:key, did:sol, did:ion, did: pkh and soon did:ebsi. The Talao wallet supports RSA, secp256k1, P-286 and Ed25519 cryptographic keys. These features make the Talao wallet one of the most open solutions on the current SSI smartphone wallet market. 

The other specificity of the Talao wallet is to be totally independent of the ecosystems but interoperable with the greatest number. It is therefore possible with the Talao wallet to collect a Verifiable Credential from one ecosystem to use it in another, which is the very essence of the SSI.

Talao has retained Spruce's Didkit library for signing and verifying VCs. This library is probably the most complete on the current market with support for a large number of DID methods and signature suites. This library has been tested with the DIF suite tests, it is also available in a large number of development languages ​​Nodejs, Python, C, Rust, PHP, Flutter/Dart, wasm. Other excellent libraries are also available in open source from the DIF in particular those produced by Mattr, DigitalBazar which are references in the SSI community.

## The Gaia-X SSI implementation 

The Gaia-X team has chosen the did:web method as well as the RSA keys for the support of the SSI identity and a predefined list of trusted sources. Currently, only company wallet support is provided, which fully justifies the choice of did:web. The choice of did:web is also an easy-to-implement solution requiring no DLT-type infrastructure while maintaining a Top-Down approach essential to public or semi-public ecosystems.

The VC life cycle has not yet been defined, which technically leaves a number of options open for the implementation of interaction protocols between the wallet and the verifiers and issuers. The “onboarding process” is simply based on obtaining a “Pass” type VC obtained after an email verification. This VC has a limited number of attributes according to the https://gaia-x.gitlab.io/policy-rules-committee/trust-framework/ .

Talao's choices were:

* The use of Eidas QWAC certificates as a trusted source. These certificates are simple to obtain and easy to use. They make it possible to secure SSL connections between a server and a client (https protocol).  

* The implementation of the LinkedDomain standard to establish a chain of trust between the domain name (DNS) of the certificate and the keys used for signing VCs. It avoids the use of specific non-standard signature suites attached to the certificate. This makes key rotation entirely possible, which is not the case with a VC signature directly associated with a certificate.  

* The use of the SIOPV2 / OIDC4VP protocol for the interaction of the verifier and the wallet.  

* The choice of the JSON-LD standard for the formalization of VC and VP.  


## Repository content


The Talao wallet repository: The Talao wallet installation code and procedure for an Android and IOS target. The wallet is also available for download on the Google and Apple stores (“Talao wallet”, build > 1.2.0)

The Didkit repository: library for signing and verifying Verifiable Credentials
The repository for this doc which includes :

1. the python source for a basic verifier to the siopv2 standard for interaction with a wallet
2. the python source of a basic issuer for interaction with a wallet
3. the python source of a desktop “wallet” to interact with a verifier. This wallet is used to test a verifier. 
4. VC models for the Gaia-X Pass and the LinkedDomain


## Implementation of the Talao wallet for Gaia-X

Create the did:web identity and initialize a company wallet:

1. Obtain a QWAC type certificate from a qualified supplier and install this certificate on the company's server. For the tests we will use a standard and free SSL certificate (Let's encrypt,...).  
2. For Gaia-X, generate at least one RSA key in JWK format. This key will be used for signing VCs. If you want to use the Talao wallet with other ecosystems, you can generate keys in secp256k&, P-256 or Ed25519 format and install them as well. Do not forget to indicate the value of the “kid” which must be that of the verification method used for the signature of the VCs. An example private key in JWK format is available here.  
3. Create a did.json file which will be installed under the root of the path server (example “my_server.com/.well-known/did.json”). This file is the DID Document of the identity of the company. See reference https://w3c-ccg.github.io/did-method-web/ 
An example of this file is available here: xxxxxxx. Be careful to put only public keys in this document. The Talao wallet supports keys in JWK format ( publicKeyJwk).  
4. Add the “LinkedDomains” service in the DID Document (did.json file) :

"service": [
  {
    "id": "#linkeddomains",
    "type": "LinkedDomains",
    "serviceEndpoint": {
      "origins": [
        "https://www.contoso.com/"    ]}}}


   5. Test with the Universal Resolver https://dev.uniresolver.io/ that the DID Document is correctly installed and written.
   6. Create and sign a VC (self signed) that proves that you have the private key that you will use to sign the VCs. An example of this VC is available at: https://identity.foundation/.well-known/resources/did-configuration/#linked-data-proof-format . This file must then be installed on the root with a path '/.well-known/did-configuration.json'
   7. Install the Talao wallet on your smartphone andinitialize the wallet by downloading the private key (in JWK format). 


## Collect a Gaia-X Pass type VC


## Log in with your Pass


## Develop a Verifier


## Develop a wallet 


## Develop an issuer