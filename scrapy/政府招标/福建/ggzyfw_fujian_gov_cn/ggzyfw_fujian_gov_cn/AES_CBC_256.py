# -*- coding: utf-8 -*-
# @Date    : 2022-09-27 11:22
# @Author  : chenxuepeng
import base64
from Crypto.Cipher import AES
from Crypto.Cipher.AES import MODE_CBC, MODE_ECB

PKCS7PADDING = 0
PKCS5PADDING = 1

BASE64 = 0
HEX = 1


class AesCrypto:
    def __init__(self, key, mode=MODE_CBC, padding=PKCS7PADDING, iv=None, encode_type=BASE64):
        """
        :param key: 密钥， 32byte=>256, 16byte=>128, 24byte=>192
        :param mode: 加密模式
        :param iv: 16byte 长度字符串
        :param padding: 填充方式
        :param encode_type: 输出格式
        """

        self.key = key.encode()
        self.mode = mode
        self.encode_type = encode_type
        self.iv = iv
        if self.iv:
            self.iv = self.iv.encode()

        if padding == PKCS7PADDING:
            self.padding_func = self.pkcs7padding
            self.unpadding_func = self.unpadding
        else:
            raise Exception('padding is invalid')

    def pkcs7padding(self, text: str, bs=16):
        """明文使用PKCS7填充 """
        remainder = bs - len(text.encode()) % bs
        padding_text = chr(remainder) * remainder
        return text + padding_text

    def unpadding(self, text):
        """ 去掉填充字符 """
        remainder = text[-1]
        padding_text = ord(remainder) * remainder
        return text.rstrip(padding_text)

    def encrypt(self, text):
        try:
            """ 加密 """
            text = self.padding_func(text)
            # 注意：加密中的和解密中的AES.new()不能使用同一个对象，所以在两处都使用了AES.new()
            kwargs = {
                'key': self.key,
                'mode': self.mode
            }
            if self.mode == MODE_CBC:
                kwargs['iv'] = self.iv
            text = AES.new(**kwargs).encrypt(text.encode())
            if self.encode_type == BASE64:
                return base64.b64encode(text).decode()
        except:
            return 'false'

    def decrypt(self, text):
        """ 解密 """
        try:
            if self.encode_type == BASE64:
                text = base64.b64decode(text.encode())
            kwargs = {
                'key': self.key,
                'mode': self.mode
            }
            if self.mode == MODE_CBC:
                kwargs['iv'] = self.iv
            text = AES.new(**kwargs).decrypt(text)
            text = self.unpadding_func(text.decode())
            return text
        except:
            return 'false'

