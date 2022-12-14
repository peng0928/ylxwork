from dateutil.relativedelta import relativedelta
import urllib, datetime
from urllib import parse
import base64, re, hashlib, time
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


def bs64(word=None):
    code = base64.b64encode(word.encode('utf-8'))
    code = str(code, 'utf-8')
    return code


def d_bs64(word=None):
    try:
        code = str(base64.b64decode(word), 'utf-8')
        return code
    except:
        return None


def md5(word=None):
    m = hashlib.md5()
    m.update(str(word).encode("utf-8"))
    return m.hexdigest()


def sha1(word=None):
    m = hashlib.sha1()
    m.update(str(word).encode("utf-8"))
    return m.hexdigest()


def sha224(word):
    the_sha512 = hashlib.sha224()
    the_sha512.update(word.encode('utf-8'))
    the_string_sha1 = the_sha512.hexdigest()
    return the_string_sha1


def sha256(word=None):
    sha256 = hashlib.sha256()
    sha256.update(word.encode())
    res = sha256.hexdigest()
    return res


def sha512(word=None):
    the_sha512 = hashlib.sha512()
    the_sha512.update(word.encode('utf-8'))
    the_string_sha1 = the_sha512.hexdigest()
    return the_string_sha1


def sha3_512(word=None):
    the_sha512 = hashlib.sha3_512()
    the_sha512.update(word.encode('utf-8'))
    the_string_sha1 = the_sha512.hexdigest()
    return the_string_sha1


def unicode_escape(word=None):
    if isinstance(word, bytes):
        word = str(word, 'unicode_escape')
        word = bytes(word, 'unicode_escape')
        return word.decode('unicode_escape')
    if isinstance(word, str):
        word = re.sub(r'(\\u[a-zA-Z0-9]{4})', lambda x: x.group(1).encode("utf-8").decode("unicode-escape"), word)
        word = bytes(word, 'unicode_escape')
        return word.decode('unicode_escape')


def unicode(word=None):
    word = word.encode('unicode_escape')
    return word


def timestamp():
    return int(time.time() * 1000)


def d_timestamp(word=None):
    try:
        word = str(word)
        length = len(word)
        if length > 10:
            length = int(length) - 10
            for i in range(length):
                word = int(word) / 10
        else:
            word = int(word)
        now = time.localtime(word)
        now = time.strftime('%Y-%m-%d %H:%M:%S', now)
        return now
    except:
        return None




def aes_cbc(word=None, key=None, offset=None):
    # key  ??????
    # offset  ?????????
    try:
        # ??????  utf-8?  ?????? 16??????
        offset = bytes(offset, encoding='utf-8')
        key = bytes(key, encoding='utf-8')
        # ????????????AES?????? ??????  ?????? ?????????
        cipher = AES.new(key, AES.MODE_CBC, offset)
        # ??????
        decrypt_content = cipher.decrypt(bytes.fromhex(word))
        result = str(decrypt_content, encoding='utf-8')
        # OKCS7 ??????
        length = len(result)  # ???????????????
        unpadding = ord(result[length - 1])  # ??????????????????????????????ASCII
        result = result[0:length - unpadding]
        return result.rstrip('\0')
    except:
        return None


def aes_cbc_encrypt(text=None, key=None, iv=None):
    try:
        key = key.encode('utf-8')
        iv = iv.encode('utf-8')
        text = text.encode('utf-8')
        cryptor = AES.new(key, AES.MODE_CBC, iv)
        # ????????????key ???????????????16???AES-128???,
        # 24???AES-192???,??????32 ???AES-256???Bytes ??????
        # ??????AES-128 ??????????????????
        length = 16
        count = len(text)
        if count < length:
            add = (length - count)
            # \0 backspace
            text = text + ('\0' * add).encode('utf-8')
        elif count > length:
            add = (length - (count % length))
            text = text + ('\0' * add).encode('utf-8')
        ciphertext = cryptor.encrypt(text)
        # ??????AES??????????????????????????????????????????ascii??????????????????????????????????????????????????????????????????
        # ???????????????????????????????????????????????????16???????????????
        ciphertext = b2a_hex(ciphertext)
        return str(ciphertext, 'utf-8')
    except:
        return None


def url_unquote(word=None):
    # URL??????
    new_txt = urllib.parse.unquote(word, 'utf-8')
    return new_txt


def url_enquote(word=None):
    # URL??????
    new_txt = urllib.parse.quote(word, 'utf-8')
    return new_txt
