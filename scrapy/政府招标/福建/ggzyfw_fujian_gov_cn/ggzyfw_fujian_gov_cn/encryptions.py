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
    # key  秘钥
    # offset  偏移值
    try:
        # 转码  utf-8?  字节 16进制
        offset = bytes(offset, encoding='utf-8')
        key = bytes(key, encoding='utf-8')
        # 创建一个AES算法 秘钥  模式 偏移值
        cipher = AES.new(key, AES.MODE_CBC, offset)
        # 解密
        decrypt_content = cipher.decrypt(bytes.fromhex(word))
        result = str(decrypt_content, encoding='utf-8')
        # OKCS7 填充
        length = len(result)  # 字符串长度
        unpadding = ord(result[length - 1])  # 得到最后一个字符串的ASCII
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
        # 这里密钥key 长度必须为16（AES-128）,
        # 24（AES-192）,或者32 （AES-256）Bytes 长度
        # 目前AES-128 足够目前使用
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
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        ciphertext = b2a_hex(ciphertext)
        return str(ciphertext, 'utf-8')
    except:
        return None


def url_unquote(word=None):
    # URL解码
    new_txt = urllib.parse.unquote(word, 'utf-8')
    return new_txt


def url_enquote(word=None):
    # URL解码
    new_txt = urllib.parse.quote(word, 'utf-8')
    return new_txt
