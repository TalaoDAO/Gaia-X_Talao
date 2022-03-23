# Talao Enterprise Wallet for Gaia-X

## The Self Sovereign Identity Talao wallet

This repository presents the use of Talao's SSI wallet for integration into the Gaia-X SSI environment. 

Talao is a company specializing in the development of SSI solutions since 2018 and contributing member of several W3V and DIF working groups. Talao is also a wallet provider. The Talao wallet is a smartphone application in production available on the Apple and Google stores, the wallet code is open source.

The specificity of the Talao SSI wallet is to be compatible with a large number of SSI identity and in particular did:tz, did:web, did:ethr, did:key, did:sol, did:ion, did: pkh and soon did:ebsi. The Talao wallet supports RSA, secp256k1, P-286 and Ed25519 cryptographic keys. These features make the Talao wallet one of the most open solutions on the current SSI smartphone wallet market. 

The other specificity of the Talao wallet is to be totally independent of the ecosystems but interoperable with the greatest number. It is therefore possible with the Talao wallet to collect a Verifiable Credential from one ecosystem to use it in another, which is the very essence of the SSI.

Talao has retained Spruce's Didkit library for signing and verifying VCs. This library is probably the most complete on the current market with support for a large number of DID methods and signature suites. This library has been tested with the DIF suite tests, it is also available in a large number of development languages ​​Nodejs, Python, C, Rust, PHP, Flutter/Dart, wasm. Other excellent libraries are also available in open source from the DIF in particular those produced by Mattr, DigitalBazar which are references in the SSI community.



## The Talao wallet as an enterprise wallet for Gaia-X SSI implementation 

The Gaia-X team has chosen the did:web method as well as the RSA keys for the support of the SSI identity and a predefined list of trusted sources. Currently, only company wallet support is provided, which fully justifies the choice of did:web. The choice of did:web is also an easy-to-implement solution requiring no DLT-type infrastructure while maintaining a Top-Down approach essential to public or semi-public ecosystems.

The VC life cycle has not yet been defined, which technically leaves a number of options open for the implementation of interaction protocols between the wallet and the verifiers and issuers. The “onboarding process” is simply based on obtaining a “Pass” type VC obtained after an email verification. This VC has a limited number of attributes according to the https://gaia-x.gitlab.io/policy-rules-committee/trust-framework/ .

Talao's choices are :

* The use of Eidas QWAC certificates as a trusted source. These certificates are easy to obtain and easy to use. They make it possible to secure SSL connections between a server and a client (https protocol) while keeping a proof of the legal names of the company.

* The implementation of the LinkedDomain standard to establish a chain of trust between the domain name (DNS) of the certificate and the keys used for signing VCs. It avoids the use of specific non-standard signature suites attached to the certificate. This makes key rotation entirely possible, which is not the case with a VC signature directly associated with a certificate.  

* The use of the SIOPV2 / OIDC4VP protocol for the interaction between the verifier and the wallet.  

* The choice of the JSON-LD standard for the formalization of VC and VP.  

* The use of the PEX protocol (https://identity.foundation/presentation-exchange/) which is a key topic of the SSI protocols. PEX allows the verifier to describes its expectations in  terms of VCs/VPs and consequently it allows the wallet to route the user toward issuers which are able to provide the VCs requested.


## Repository content

The Talao wallet repository is available there https://github.com/TalaoDAO/talao-wallet with installation code and procedure for an Android and IOS target 

The wallet is also available for download on the Google and Apple stores (“Talao wallet”)

The Didkit repository: library for signing and verifying Verifiable Credentialsn is available there : https://github.com/spruceid/didkit.

This repository includes :

1. the python source of a basic verifier to the siopv2 standard for interaction with a wallet (/routes/login) used for authentication  

2. the python source of a basic issuer for interaction with a wallet (/routes/onboarding).  

3. VC models for the Gaia-X Pass and the LinkedDomain  

References 

https://www.w3.org/TR/did-core/  
https://www.w3.org/TR/vc-data-model/  
https://w3c-ccg.github.io/did-resolution/  
https://github.com/w3c-ccg/vc-http-api  
https://w3c-ccg.github.io/citizenship-vocab/  
https://w3c-ccg.github.io/credential-handler-api/  


## Implementation of a company identity with did:web and a QWAC certificate

Create the did:web identity and initialize a company wallet:

1. Obtain a QWAC type certificate from a Certificate Authority and install this certificate on the company's server (for the tests we will use a standard and free SSL certificate from Let's encrypt,...).  

2. For Gaia-X, generate at least one RSA key in JWK format. This key will be used for signing VCs. If you want to use the Talao wallet with other ecosystems, you can generate keys in secp256k&, P-256 or Ed25519 format and install them as well. Do not forget to indicate the value of the “kid” which must be that of the verification method used for the signature of the VCs. An example private key in JWK format is available here.  

3. Create a did.json file which will be installed under the root of the path server (example “my_server.com/.well-known/did.json”). This file is the DID Document of the identity of the company. See reference https://w3c-ccg.github.io/did-method-web/ 
Be careful to publish only public keys in this document. The Talao wallet supports keys in JWK format (publicKeyJwk).  

4. Add the “LinkedDomains” service in the DID Document (did.json file) :

``` json

"service": [
  {
    "id": "#linkeddomains",
    "type": "LinkedDomains",
    "serviceEndpoint": {
      "origins": [
        "https://www.contoso.com/"    ]}}}

```

5. Test with the Universal Resolver https://dev.uniresolver.io/ that the DID Document is correctly installed and written.

6. Create and sign a VC (self signed) that proves that you have the private key that you will use to sign the VCs. An example of this VC is available at: https://identity.foundation/.well-known/resources/did-configuration/#linked-data-proof-format . This file must then be installed on the root with a path '/.well-known/did-configuration.json'

7. Install the Talao wallet on your smartphone andinitialize the wallet by downloading the private key (in JWK format). 


## Initialize the Talao wallet as an enterprise wallet

To set up the wallet as an enterprise wallet, choose "Create Enterprise Wallet" then enter your company DID (did:web:xxxx) and upload the Json Web Key file (JWK) with the correct "kid".  

Example :

``` json

{
    "d": "BLn1w1y3xDp0a-8E97nk54e-FHZE8bNjqug........F-eDBw2mImBi9EI0F9Wj967iJ8Dd0HxQ",
    "dp": "dMXKqre0YGto7ut_b4_b......I827OD3eKObRJVsW7gnQKaBYs4NPyJW4omCUqcNejNfqsefVSefgqbVfmq_zCXrUBxLQmWATZP1m7KLU",
    "dq": "Y2eTt3Jl1LzHQYo3rpDPsEP....48AMdI7y_Fvs7Ied-GGVyv_RuTQifgYQqh6iiJ5oVJna-HUGhsIdt2IrQvV534KN_HXfNV34XS_HZk0",
    "e": "AQAB",
    "kid": "did:web:demo.talao.co#key-1",
    "kty": "RSA",
    "n": "ilResnUjv6kwJW8yh9u3kS3_2.....loYUhBTtxlKyY53R9QoNtJTwx25KMjHIpDCrPoSDXyYV_JfjW9iNGZenNbpoLS6Q",
    "p": "up2lOWo2Bg3N79wIYlP1kZs84WggC8gq7o.....Z0Ui5y_5w7bZ7F06X3-TATbV9QiAqSXZtaq2LlKomL_i8dX-9tB_tMbSUqGkX5Cc8aQSamvU",
    "q": "vcLF4bnmiTXBkurxj9449pQr3qSySjCFe1pC..........Mz4nc3qy0wFBPjsuWBduPQ20HLUrJ15i1YNmxZFkhJk4MH_FvugiX0hIo0esdg887ByScjt5O-53R6U",
    "qi": "gQ5rYsAmPivde03lz9-KdZ2Krad5zeP4NrMrHtjrVfhy..................9jpATbTtmGKcJUpBkHdoBcYbpcP87qNhvu9YRUcwEGoJHs02HWy7mG9maIxOAXwU3SoaU_A"
}

``` 

## Test

1. For testing purpose one can use the demo_key.json KEY (/test) file to setup the wallet with did:web:demo.talao.co as the DID of the wallet.

2. Collect a Gaia-X Pass type VC. Go to https://talao.co/gaiax and choose "Get a Gaia-X Pass"

3. Log in with your Pass. Go to https://talao.co/gaiax and choose "Sign In to the Gaia-x Talao Portal" to simulate an authentication.

4. Check the content of your VC and VP. Go to https://talao.co/gaiax and choose "Display your credential".

## Example of a VC 

NB : This one is signed by a did:web identity to a did:tez method. The status is not complete.

``` json

{
    "@context": [
        "https://www.w3.org/2018/credentials/v1",
        "https://w3id.org/vc-revocation-list-2020/v1",
        {
            "ParticipantCredential": {
                "@context": {
                    "@protected": true,
                    "@version": 1.1,
                    "companyName": "schema:legalName",
                    "companyNumber": "schema:taxID",
                    "headquarter": {
                        "@context": {
                            "@protected": true,
                            "@version": 1.1,
                            "country": "schema:addressCountry",
                            "schema": "https://schema.org/"
                        },
                        "@id": "https://gaia-x.gitlab.io/policy-rules-committee/trust-framework/participant/"
                    },
                    "id": "@id",
                    "legal": {
                        "@context": {
                            "@protected": true,
                            "@version": 1.1,
                            "country": "schema:addressCountry",
                            "schema": "https://schema.org/"
                        },
                        "@id": "https://gaia-x.gitlab.io/policy-rules-committee/trust-framework/participant/"
                    },
                    "lei": "schema:leiCode",
                    "parentOrganisation": "schema:parentOrganization",
                    "schema": "https://schema.org/",
                    "subOrganisation": "schema:subOrganization",
                    "type": "@type"
                },
                "@id": "https://gaia-x.gitlab.io/policy-rules-committee/trust-framework/participant/"
            }
        }
    ],
    "id": "urn:uuid:f4d76267-9d0f-438c-9cf0-d3271a91a313",
    "type": [
        "VerifiableCredential",
        "ParticipantCredential"
    ],
    "credentialSubject": {
        "id": "did:tz:tz2E4kuaB9zHa1C3LqNeZncvZogYjQsXxvxz",
        "type": "ParticipantCredential",
        "companyName": "Talao SAS",
        "companyNumber": " FR7501.837674480",
        "legal": {
            "country": "FR"
        },
        "headquarter": {
            "country": "FR"
        }
    },
    "issuer": "did:web:talao.co",
    "issuanceDate": "2022-03-20T12:18:26Z",
    "proof": {
        "type": "Ed25519Signature2018",
        "proofPurpose": "assertionMethod",
        "verificationMethod": "did:web:talao.co#key-4",
        "created": "2022-03-20T11:18:28.308Z",
        "jws": "eyJhbGciOiJFZERTQSIsImtpZCI6ImRpZDp3ZWI6dGFsYW8uY28ja2V5LTQiLCJjcml0IjpbImI2NCJdLCJiNjQiOmZhbHNlfQ..Y_hh-xb3YxMfHs_QUOsf7foBnlnFQTqIWzltg0mIIJEyx32ZYtHzq36onQGEhDsU3YpKsoss_yFOKnBTggqeBQ"
    },
    "expirationDate": "2022-04-01T12:18:26Z",
    "credentialStatus": {
        "id": "https://.........../credential/status/1#1234",
        "type": "RevocationList2020Status",
        "revocationListCredential": "https://.......main/credential/status/1",
        "revocationListIndex": "1234"
    },
    "credentialSchema": {
        "id": "https://raw.githubusercontent.com/walt-id/waltid-ssikit-vclib/master/src/test/resources/schemas/ParticipantCredential.json",
        "type": "JsonSchemaValidator2018"
    }

  ```

## Example of a /.well-known/did.json 

``` json 

            {
                "@context": [
                    "https://www.w3.org/ns/did/v1",
                    {
                        "@id": "https://w3id.org/security#publicKeyJwk",
                        "@type": "@json"
                    }
                ],
                "id": "did:web:demo.talao.co",
                "verificationMethod": [
                    
                    {
                        "id": "did:web:demo.talao.co#key-1",
                        "type": "JwsVerificationKey2020",
                        "controller": "did:web:demo.talao.co",
                        "publicKeyJwk": {
                            "e":"AQAB",
                            "kid":"did:web:demo.talao.co#key-1",
                            "kty":"RSA",
                            "n": "ilResnUjv6kwJW8y...........BKqZWsMi2V6tB_loYUhBTtxlKyY53R9QoNtJTwx25KMjHIpDCrPoSDXyYV_JfjW9iNGZenNbpoLS6Q"
                        }
                    }
                ],
                "authentication" : [
                    "did:web:demo.talao.co#key-1",
                ],
                "assertionMethod" : [
                    "did:web:demo.talao.co#key-1",
                ],
                "capabilityInvocation":[
                    "did:web:demo.talao.co#key-1"
                ]
            }

```

## Claims attribute and Presentation Exchange of the siopv2 verifier (authentication)


```json

{
        "id_token" : {
        },
        "vp_token": {
            "presentation_definition": {
                "id": "pass_for_gaiax",
                "input_descriptors": [
                    {
                        "id": "ParticipantCredential issued by Talao",
                        "purpose" : "Test for Gaia-X hackathon",
                        "format" : {
                            "ldp_vc": {
                                "proof_type": [
                                                "JsonWebSignature2020"
                                ]
                            }
                        },
                        "constraints": {
                            "limit_disclosure": "required",
                            "fields": [
                                {
                                    "path": [
                                        "$.credentialSubject.type"
                                    ],
                                    "purpose" : "One can only accept ParticipantCredential",
                                    "filter": {
                                        "type": "string",
                                        "pattern": "ParticipantCredential"
                                    }
                                },
                                {
                                    "path": [
                                        "$.issuer"
                                    ],
                                    "purpose" : "One can accept only ParticipantCredential signed by Talao",
                                    "filter": {
                                        "type": "string",
                                        "pattern": "did:web:talao.co"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }

``` 
