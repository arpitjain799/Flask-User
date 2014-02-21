import base64
from Crypto.Cipher import AES
from itsdangerous import BadSignature, SignatureExpired, TimestampSigner

class TokenManager():
    def __init__(self, app_secret):
        """
        Create a cypher to encrypt IDs and a signer to sign tokens.
        """
        # Create cypher to encrypt IDs
        key = app_secret + '0123456789abcdef'  # ensure >=16 characters
        sixteen_byte_key = key[0:16]  # get first 16 characters
        self.cipher = AES.new(sixteen_byte_key)

        # Create signer to sign tokens
        self.signer = TimestampSigner(app_secret)

    def encrypt_id(self, id):
        """
        Encrypts integer ID to url-safe base64 string
        """
        str1 = '%016d' % id                             # --> 16 byte integer string
        str2 = self.cipher.encrypt(str1)                # --> encrypted data
        str3 = base64.urlsafe_b64encode(str2)           # --> URL safe base64 string with '=='
        return str3[0:-2]                               # --> base64 string without '=='

    def decrypt_id(self, encrypted_id):
        """
        Decrypts url-safe base64 string to integer ID
        """
        try:
            str3 = encrypted_id.encode('ascii') + '=='  # --> base64 string with '=='
            str2 = base64.urlsafe_b64decode(str3)       # --> encrypted data
            str1 = self.cipher.decrypt(str2)            # --> 16 byte integer string
            return int(str1)                            # --> integer id
        except:
            return 0

    def generate_token(self, user_id):
        """
        Return token with user_id, timestamp and signature
        """
        return self.signer.sign(self.encrypt_id(user_id))

    def verify_token(self, token, max_age):
        """
        Verify token and return (is_valid, has_expired, user_id).

        Returns (True, False, user_id) on success.
        Returns (False, True, None) on expired tokens.
        Returns (False, False, None) on invalid tokens.
        """
        try:
            data = self.signer.unsign(token, max_age=1000)
            is_valid = True
            has_expired = False
            user_id = self.decrypt_id(data)
        except SignatureExpired:
            is_valid = False
            has_expired = True
            user_id = None
        except BadSignature:
            is_valid = False
            has_expired = False
            user_id = None
        return (is_valid, has_expired, user_id)