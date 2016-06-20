from ctypes import *
from ctypes.util import find_library
from datetime import datetime

import sys
mdmi_path = '/opt/mdmi/modules'
if not mdmi_path in sys.path:
    sys.path.append(mdmi_path)
from pkeypool.keypoolclient import KeyPoolClient
from pkeypool.keypoolclient import pkeypool_is_enabled

crypto = CDLL(find_library("crypto"))
ssl = CDLL(find_library("ssl"))
ssl.OPENSSL_config(None)
crypto.OpenSSL_add_all_ciphers()
crypto.OpenSSL_add_all_digests()
#ssl.OpenSSL_add_all_algorithms()

ssl.ERR_load_ERR_strings()
ssl.ERR_load_crypto_strings()
ssl.ERR_load_EVP_strings()

crypto.BIO_s_file.restype = c_void_p
crypto.BIO_s_mem.restype = c_void_p
crypto.BIO_new.argtypes = [c_void_p]
crypto.BIO_new.restype = c_void_p
crypto.BIO_free_all.argtypes = [c_void_p]
crypto.BIO_ctrl.argtypes = [c_void_p, c_int, c_long, c_void_p]
crypto.PEM_read_bio_X509.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p]
crypto.PEM_read_bio_X509.restype = c_void_p
crypto.PEM_read_bio_PrivateKey.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p]
crypto.PEM_read_bio_PrivateKey.restype = c_void_p
crypto.i2d_X509_bio.argtypes = [c_void_p, c_void_p]
crypto.i2d_X509_bio.restype = c_void_p
crypto.i2d_PKCS12_bio.argtypes = [c_void_p]
crypto.PKCS12_create.argtypes = [c_char_p, c_char_p, c_void_p, c_void_p, c_void_p, c_int, c_int, c_int, c_int, c_int]
crypto.PKCS12_create.restype = c_void_p

crypto.EVP_PKEY_new.restype = c_void_p
crypto.RSA_generate_key.argtypes = [c_int, c_ulong, c_void_p, c_void_p]
crypto.RSA_generate_key.restype = c_void_p
crypto.EVP_PKEY_assign.argtypes = [c_void_p, c_int, c_void_p]
crypto.EVP_PKEY_free.argtypes = [c_void_p]
crypto.RSA_free.argtypes = [c_void_p]
crypto.X509_NAME_new.restype = c_void_p
crypto.OBJ_txt2nid.argtypes = [c_char_p]
crypto.X509_NAME_add_entry_by_NID.argtypes = [c_void_p, c_int, c_int, c_char_p, c_int, c_int, c_int]
crypto.X509_REQ_new.restype = c_void_p
crypto.X509_REQ_free.argtypes = [c_void_p]
crypto.X509_REQ_set_pubkey.argtypes = [c_void_p, c_void_p]
crypto.X509_NAME_free.argtypes = [c_void_p]
crypto.X509_REQ_set_subject_name.argtypes = [c_void_p, c_void_p]
crypto.X509_REQ_sign.argtypes = [c_void_p, c_void_p, c_void_p]
crypto.X509_REQ_get_pubkey.argtypes = [c_void_p]
crypto.X509_REQ_get_pubkey.restype = c_void_p
crypto.X509_REQ_verify.argtypes = [c_void_p, c_void_p]
crypto.X509_new.restype = c_void_p
crypto.X509_set_version.argtypes = [c_void_p, c_long]
crypto.ASN1_INTEGER_new.restype = c_void_p
crypto.ASN1_INTEGER_free.argtypes = [c_void_p]

crypto.BN_pseudo_rand.argtypes = [c_void_p, c_int, c_int, c_int]
crypto.BN_to_ASN1_INTEGER.argtypes = [c_void_p, c_void_p]
crypto.BN_free.argtypes = [c_void_p]
crypto.X509_set_serialNumber.argtypes = [c_void_p, c_void_p]
crypto.X509_set_issuer_name.argtypes = [c_void_p, c_void_p]
crypto.X509_get_subject_name.argtypes = [c_void_p]
crypto.X509_get_subject_name.restype = c_void_p
crypto.X509_set_subject_name.argtypes = [c_void_p, c_void_p]
crypto.X509_gmtime_adj.argtypes = [c_void_p, c_long]
crypto.X509_set_pubkey.argtypes = [c_void_p, c_void_p]
crypto.X509_add_ext.argtypes = [c_void_p, c_void_p, c_int]
crypto.X509_sign.argtypes = [c_void_p, c_void_p, c_void_p]
crypto.EVP_sha1.restype = c_void_p

crypto.BIO_write.argtypes = [c_void_p, c_void_p, c_int]
crypto.PKCS7_sign.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p, c_int]
crypto.PKCS7_sign.restype = c_void_p
crypto.i2d_PKCS7_bio_stream.argtypes = [c_void_p, c_void_p, c_void_p, c_int]
crypto.PKCS7_free.argtypes = [c_void_p]

crypto.PEM_X509_INFO_read_bio.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p]
crypto.PEM_X509_INFO_read_bio.restype = c_void_p
#crypto.sk_X509_new_null.restype = c_void_p
#crypto.sk_X509_CRL_new_null.restype = c_void_p
crypto.sk_new_null.restype = c_void_p
#crypto.sk_X509_INFO_pop_free.argtypes = [c_void_p, c_void_p]
#crypto.sk_X509_pop_free.argtypes = [c_void_p, c_void_p]
crypto.sk_pop_free.argtypes = [c_void_p, c_void_p]
#crypto.sk_X509_INFO_num.argtypes = [c_void_p]
crypto.sk_num.argtypes = [c_void_p]
#crypto.sk_X509_INFO_value.argtypes = [c_void_p, c_int]
#crypto.sk_X509_INFO_value.restype = c_void_p
crypto.sk_value.argtypes = [c_void_p, c_int]
crypto.sk_value.restype = c_void_p
#crypto.sk_X509_push.argtypes = [c_void_p, c_void_p]
#crypto.sk_X509_CRL_push.argtypes = [c_void_p, c_void_p]
crypto.sk_push.argtypes = [c_void_p, c_void_p]

class ASN1_TIME(Structure):
    _fields_ = [('length', c_int),
                ('type', c_int),
                ('data', c_char_p),
                ('flags', c_long)]

class X509_VAL(Structure):
    _fields_ = [('notBefore', c_void_p),
                ('notAfter', POINTER(ASN1_TIME))]

class X509_CINF(Structure):
    _fields_ = [('version', c_void_p),
                ('serialNumber', c_void_p),
                ('signature', c_void_p),
                ('issuer', c_void_p),
                ('validity', POINTER(X509_VAL))]

class X509_INFO(Structure):
    _fields_ = [("x509", c_void_p),
                ("crl", c_void_p)]

class X509(Structure):
    _fields_ = [('cert_info', POINTER(X509_CINF))]

class X509V3_CTX(Structure):
    _fields_ = [('flags', c_int),
                ("issuer_cert", c_void_p),
                ("subject_cert", c_void_p),
                ("subject_req", c_void_p),
                ("crl", c_void_p),
                ("db_meth", c_void_p),
                ("db ", c_void_p)]

def issuer_certificate(issuer_ca, issuer_key, user_info, passout, pkey):
    ui = user_info.split(';')
    for i in ui:
        kv = i.split(':')
        if len(kv) == 2:
            if kv[0] == 'Username':
                username = kv[1]
            elif kv[0] == 'DeviceID':
                device_id = kv[1]

    cn = 'MOBILE VPN USER : %s' % device_id
    subj = '/C=US/ST=California/L=Los Gatos/O=Websense, Inc./CN=%s/emailAddress=%s' % (cn, username)

    name = generate_name(subj)

    #pkey = generate_key()
    if not pkey:
        return None, None

    req = generate_request(pkey, name)
    if not req:
        crypto.EVP_PKEY_free(pkey)
        return None, None

    (x509, notAfter) = generate_certificate(pkey, req, issuer_ca, issuer_key, name, user_info)
    if not x509:
        crypto.EVP_PKEY_free(pkey)
        crypto.X509_REQ_free(req)
        return None, None

    p12 = generate_p12(x509, pkey, passout)
    if not p12:
        crypto.EVP_PKEY_free(pkey)
        crypto.X509_REQ_free(req)
        crypto.X509_free(x509)
        return None, None

    crypto.EVP_PKEY_free(pkey)
    crypto.X509_REQ_free(req)
    crypto.X509_free(x509)

    return p12, cn, notAfter

def generate_p12(x509, pkey, passout):
    if not x509 or not pkey or not passout:
        return None

    p12 = crypto.PKCS12_create(passout, 'Websense Mobile Security', pkey, x509, None, 0, 0, 0, 0, 0)

    return p12

def generate_certificate(pkey, req, issuer_ca, issuer_key, name, nsComments):
    pubkey = crypto.X509_REQ_get_pubkey(req)
    if not pubkey:
        return None
    ssl.ERR_clear_error()

    # Varify REQ
    rc = crypto.X509_REQ_verify(req, pubkey)
    if rc <= 0:
        crypto.EVP_PKEY_free(pubkey)
        return None

    x509 = crypto.X509_new()
    if not x509:
        crypto.EVP_PKEY_free(pubkey)
        return None

    # X509 V3
    rc = crypto.X509_set_version(x509, 2)
    if not rc:
        crypto.EVP_PKEY_free(pubkey)
        crypto.X509_free(x509)
        return None

    # set serial
    sno = crypto.ASN1_INTEGER_new()
    btmp = crypto.BN_new()
    if not sno or not btmp:
        crypto.EVP_PKEY_free(pubkey)
        crypto.X509_free(x509)
        if sno:
            crypto.ASN1_INTEGER_free(sno)
        if btmp:
            crypto.BN_free(btmp)
        return None

    rc = crypto.BN_pseudo_rand(btmp, 64, 0, 0)
    if not rc:
        crypto.EVP_PKEY_free(pubkey)
        crypto.X509_free(x509)
        crypto.ASN1_INTEGER_free(sno)
        crypto.BN_free(btmp)

        return None

    rc = crypto.BN_to_ASN1_INTEGER(btmp, sno)
    if not rc:
        crypto.EVP_PKEY_free(pubkey)
        crypto.X509_free(x509)
        crypto.ASN1_INTEGER_free(sno)
        crypto.BN_free(btmp)

        return None

    rc = crypto.X509_set_serialNumber(x509, sno)
    if not rc:
        crypto.EVP_PKEY_free(pubkey)
        crypto.X509_free(x509)
        crypto.ASN1_INTEGER_free(sno)
        crypto.BN_free(btmp)

        return None

    crypto.ASN1_INTEGER_free(sno)
    crypto.BN_free(btmp)

    sno = None
    btmp = None

    # Set Issuer and subject
    rc = crypto.X509_set_issuer_name(x509, crypto.X509_get_subject_name(issuer_ca))
    if not rc:
        crypto.EVP_PKEY_free(pubkey)
        crypto.X509_free(x509)

        return None
    rc = crypto.X509_set_subject_name(x509, name)
    if not rc:
        crypto.EVP_PKEY_free(pubkey)
        crypto.X509_free(x509)

        return None

    crypto.X509_NAME_free(name)
    # Set Start time and End time
    #crypto.X509_gmtime_adj(crypto.X509_get_notBefore(x509), -60*60*24)
    #crypto.X509_gmtime_adj(crypto.X509_get_notAfter(x509), 60*60*24*3652)
    validity = cast(x509, POINTER(X509)).contents.cert_info.contents.validity.contents
    crypto.X509_gmtime_adj(validity.notBefore, -60 * 60 * 24)
    crypto.X509_gmtime_adj(validity.notAfter, 60 * 60 * 24 * 3652)

    # Set public key
    rc = crypto.X509_set_pubkey(x509, pubkey)
    if not rc:
        crypto.EVP_PKEY_free(pubkey)
        crypto.X509_free(x509)

        return None

    crypto.EVP_PKEY_free(pubkey)

    # Add extentions
    add_extension(x509, issuer_ca, 87, "CA:FALSE") # NID_basic_constraints 87
    add_extension(x509, issuer_ca, 82, "hash") # NID_subject_key_identifier 82
    add_extension(x509, issuer_ca, 90, "keyid:always,issuer:always") # NID_authority_key_identifier 90

    if nsComments:
        add_extension(x509, issuer_ca, 78, nsComments) # NID_netscape_comment 78

    # Sign with SHA1
    rc = crypto.X509_sign(x509, issuer_key, crypto.EVP_sha1())
    if not rc:
        crypto.EVP_PKEY_free(pubkey)
        crypto.X509_free(x509)

        return None

    notAfter = cast(x509, POINTER(X509)).contents.cert_info.contents.validity.contents.notAfter.contents.data
    dt = datetime.strptime(cast(notAfter, c_char_p).value, "%y%m%d%H%M%SZ")
    notAfter = dt.strftime("%Y/%m/%d")
    return x509, notAfter

def add_extension(x509, issuer_ca, nid, value):
    ctx = X509V3_CTX()
    ctx.db = None
    crypto.X509V3_set_ctx(byref(ctx), issuer_ca, x509, None, None, 0)
    ext = crypto.X509V3_EXT_conf_nid(None, byref(ctx), nid, value)
    if ext:
        crypto.X509_add_ext(x509, ext, -1)
        crypto.X509_EXTENSION_free(ext)

def generate_key(cnt=1):
    g_keylist = []

    if pkeypool_is_enabled():
        g_keylist = generate_key_from_pool(cnt)
        #key pool doesn't work, generate key in real time
        if len(g_keylist) != cnt:
            g_keylist = generate_key_in_time(cnt)
    else:
        g_keylist = generate_key_in_time(cnt)

    if len(g_keylist) == 0:
        return None

    return g_keylist

def generate_key_in_time(cnt):
    keylist = []
    for i in range(cnt):
        pkey = crypto.EVP_PKEY_new()
        if not pkey:
            break

        rsa = crypto.RSA_generate_key(1024, 0x10001L, None, None)
        if not rsa:
            crypto.EVP_PKEY_free(pkey)
            break

        #rc = crypto.EVP_PKEY_assign_RSA(pkey, rsa)
        #define EVP_PKEY_assign_RSA(pkey,rsa) EVP_PKEY_assign((pkey),EVP_PKEY_RSA, (char *)(rsa))
        rc = crypto.EVP_PKEY_assign(pkey, 6, rsa) # EVP_PKEY_RSA NID_rsaEncryption 6
        if rc != 1:
            crypto.EVP_PKEY_free(pkey)
            crypto.RSA_free(rsa)
            break

        keylist.append(pkey)

    return keylist

def generate_key_from_pool(cnt):
    keylist = []

    client = KeyPoolClient()
    keylist_tmp = client.require(cnt)
    for i in range(len(keylist_tmp)):
        key = keylist_tmp.pop()
        pkey = load_key_from_string(key, len(key))
        keylist.append(pkey)

    return keylist

def generate_name(subj):
    name = crypto.X509_NAME_new()
    items = subj.split('/')
    for item in items:
        if item:
            kv = item.split('=')
            if len(kv) == 2 and kv[1]:
                nid = crypto.OBJ_txt2nid(kv[0])
                if nid:
                    rc = crypto.X509_NAME_add_entry_by_NID(name, nid, 0x1000, kv[1], -1, -1, 0)

    return name

def generate_request(pkey, name):
    #if not subj:
        #subj = "/O=Websesne,Inc./CN=Mobile CA Utiles"
    
    #name = generate_name(subj)
    if not name:
        return None

    req = crypto.X509_REQ_new()
    if not req:
        crypto.X509_NAME_free(name)

    rc = crypto.X509_REQ_set_pubkey(req, pkey)
    if not rc:
        crypto.X509_NAME_free(name)
        crypto.X509_REQ_free(req)

        return None

    rc = crypto.X509_REQ_set_subject_name(req, name)
    if not rc:
        crypto.X509_NAME_free(name)
        crypto.X509_REQ_free(req)

        return None

    rc = crypto.X509_REQ_sign(req, pkey, crypto.EVP_sha1())
    if not rc:
        crypto.X509_NAME_free(name)
        crypto.X509_REQ_free(req)

        return None

    #crypto.X509_NAME_free(name)
    return req

def dumps_ca_to_string(cert):
    out = crypto.BIO_new(crypto.BIO_s_mem())
    if not out:
        return None

    rc = crypto.i2d_X509_bio(out, cert)
    if rc != 1:
        crypto.BIO_free_all(out)
        return None

    #data = POINTER(c_char_p)()
    data = c_char_p()
    #define BIO_get_mem_data(b,pp)  BIO_ctrl(b,BIO_CTRL_INFO,0,(char *)pp)
    #define BIO_CTRL_INFO       3  /* opt - extra tit-bits */
    length = crypto.BIO_ctrl(out, 3, 0, byref(data))

    #r = plistlib.Data(cast(data, POINTER(c_char * length)).contents.raw)
    r = cast(data, POINTER(c_char * length)).contents.raw
    crypto.BIO_free_all(out)

    return r

def dumps_p12_to_string(p12):
    out = crypto.BIO_new(crypto.BIO_s_mem())
    if not out:
        return None

    rc = crypto.i2d_PKCS12_bio(out, p12)
    if rc != 1:
        crypto.BIO_free_all(out)
        return None

    #data = POINTER(c_char_p)()
    data = c_char_p()
    #define BIO_get_mem_data(b,pp)  BIO_ctrl(b,BIO_CTRL_INFO,0,(char *)pp)
    #define BIO_CTRL_INFO       3  /* opt - extra tit-bits */
    length = crypto.BIO_ctrl(out, 3, 0, byref(data))

    #r = plistlib.Data(cast(data, POINTER(c_char * length)).contents.raw)
    r = cast(data, POINTER(c_char * length)).contents.raw
    crypto.BIO_free_all(out)

    return r

def load_ca_from_file(file_name):
    out = crypto.BIO_new(crypto.BIO_s_file())
    if not out:
        return None
    #rc = crypto.BIO_read_filename(out, file_name)
    #define BIO_read_filename(b,name) BIO_ctrl(b,BIO_C_SET_FILENAME, BIO_CLOSE|BIO_FP_READ,(char *)name)
    rc = crypto.BIO_ctrl(out, 108, 0x01 | 0x02, file_name) # BIO_C_SET_FILENAME 108
                                                          # BIO_CLOSE 0x01
                                                          # BIO_FP_READ 0x02
    if rc <= 0:
        # logging
        crypto.BIO_free_all(out)
        return None

    x509 = crypto.PEM_read_bio_X509(out, None, 0, None)
    #x509 = crypto.PEM_read_bio_X509_AUX(out, None, 0, None)
    if not x509:
        # logging
        crypto.BIO_free_all(out)
        return None

    crypto.BIO_free_all(out)

    return x509

def load_cas_from_file(file_name, passcode=None):
    out = crypto.BIO_new(crypto.BIO_s_file())
    if not out:
        return None, None
    #rc = crypto.BIO_read_filename(out, file_name)
    #define BIO_read_filename(b,name) BIO_ctrl(b,BIO_C_SET_FILENAME, BIO_CLOSE|BIO_FP_READ,(char *)name)
    rc = crypto.BIO_ctrl(out, 108, 0x01 | 0x02, file_name) # BIO_C_SET_FILENAME 108
                                                          # BIO_CLOSE 0x01
                                                          # BIO_FP_READ 0x02
    if rc <= 0:
        # logging
        crypto.BIO_free_all(out)
        return None, None

    # x509 = crypto.PEM_read_bio_X509(out, None, 0, None)
    # STACK_OF(X509_INFO) * PEM_X509_INFO_read_bio(BIO *bp, STACK_OF(X509_INFO) *sk, pem_password_cb *cb, void *u)
    stack_of_x509 = crypto.PEM_X509_INFO_read_bio(out, None, None, None)
    if not stack_of_x509:
        crypto.BIO_free_all(out)
        return None, None

    #x509s = crypto.sk_X509_new_null()
    x509s = crypto.sk_new_null()
    if not x509s:
        crypto.sk_pop_free(stack_of_x509, crypto.X509_INFO_free)
        crypto.BIO_free_all(out)
        return None, None

    #crls = crypto.sk_X509_CRL_new_null()
    crls = crypto.sk_new_null()
    if not crls:
        crypto.sk_pop_free(stack_of_x509, X509_INFO_free)
        crypto.sk_X509_pop_free(x509s, crypto.X509_free)
        crypto.BIO_free_all(out)

        return None, None

    error = 0
    total = crypto.sk_num(stack_of_x509)
    for i in xrange(total):
        x509_info = crypto.sk_value(stack_of_x509, i)
        x509_info = cast(x509_info, POINTER(X509_INFO)).contents
        if x509_info.x509:
            if not crypto.sk_push(x509s, x509_info.x509):
                error = 1
                break;
            x509_info.x509 = None
        if x509_info.crl:
            if not crypto.sk_push(crls, x509_info.crl):
                error = 1
                break;
            x509_info.crl = None

    if error or not (crypto.sk_num(x509s) or crypto.sk_num(crls)):
        crypto.sk_pop_free(stack_of_x509, crypto.X509_INFO_free)
        crypto.sk_pop_free(x509s, crypto.X509_free)
        crypto.sk_pop_free(crls, crypto.X509_CRL_free)
        crypto.BIO_free_all(out)
        return None, None

    crypto.sk_pop_free(stack_of_x509, crypto.X509_INFO_free)

    crypto.BIO_free_all(out)
    #crypto.sk_X509_pop_free(x509s, crypto.X509_free)
    #crypto.sk_X509_CRL_pop_free(crls, crypto.X509_CRL_free)

    return x509s, crls

def load_key_from_string(content, length):
    data = c_char_p(content)
    #EVP_PKEY* d2i_AutoPrivateKey(EVP_PKEY **a, const unsigned char **pp, long length)
    pkey = crypto.d2i_AutoPrivateKey(None, byref(data), length)
    return pkey

def load_key_from_file(file_name, passcode=None):
    out = crypto.BIO_new(crypto.BIO_s_file())
    if not out:
        return None
    #rc = ssl.BIO_read_filename(out, file_name)
    rc = crypto.BIO_ctrl(out, 108, 0x01 | 0x02, file_name) # BIO_C_SET_FILENAME 108
                                                          # BIO_CLOSE 0x01
                                                          # BIO_FP_READ 0x02
    if rc <= 0:
        # logging
        crypto.BIO_free_all(out)
        return None

    pkey = crypto.PEM_read_bio_PrivateKey(out, None, None, passcode)
    if not pkey:
        # logging
        crypto.BIO_free_all(out)
        return None

    crypto.BIO_free_all(out)

    return pkey

def sign_with_domain_ca(domain_ca_path, domain_key_path, intermediate_ca_path, content):
    if not domain_ca_path or not domain_key_path or not intermediate_ca_path or not content:
        return None

    intermediate_ca = load_cas_from_file(intermediate_ca_path)
    intermediate_ca = intermediate_ca[0]
    if not intermediate_ca:
        return None
    domain_ca = load_ca_from_file(domain_ca_path)
    if not domain_ca:
        return None
    domain_key = load_key_from_file(domain_key_path)
    if not domain_key:
        return None

    in_data = crypto.BIO_new(crypto.BIO_s_mem())
    if not in_data:
        return None

    # int    BIO_write(BIO *b, const void *buf, int len)
    crypto.BIO_write(in_data, content, len(content))
    # PKCS7 *PKCS7_sign(X509 *signcert, EVP_PKEY *pkey, STACK_OF(X509) *certs, BIO *data, int flags)
    p7 = crypto.PKCS7_sign(domain_ca, domain_key, intermediate_ca, in_data, 0)

    out_data = crypto.BIO_new(crypto.BIO_s_mem())
    if not out_data:
        return None

    # int i2d_PKCS7_bio_stream(BIO *out, PKCS7 *p7, BIO *data, int flags)
    if crypto.i2d_PKCS7_bio_stream(out_data, p7, in_data, 0) != 1:
        return None

    data = c_char_p()
    length = crypto.BIO_ctrl(out_data, 3, 0, byref(data))

    #r = plistlib.Data(cast(data, POINTER(c_char * length)).contents.raw)
    r = cast(data, POINTER(c_char * length)).contents.raw

    crypto.sk_pop_free(intermediate_ca, crypto.X509_free)
    crypto.X509_free(domain_ca)
    crypto.EVP_PKEY_free(domain_key)
    crypto.PKCS7_free(p7)
    crypto.BIO_free_all(in_data)
    crypto.BIO_free_all(out_data)

    return r
