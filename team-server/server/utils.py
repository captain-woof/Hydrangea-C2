import base64
import random
import string

def base64Encode(s: str, outputString = True):
    encodedBytes = base64.b64encode(s.encode("utf-8") if isinstance(s, str) else s)
    if outputString:
        return encodedBytes.decode("utf-8")
    else:
        return encodedBytes

def base64Decode(s: str, outputString = True):
    encodedBytes = base64.b64decode(s.encode("utf-8") if isinstance(s, str) else s)
    if outputString:
        return encodedBytes.decode("utf-8")
    else:
        return encodedBytes
    
def generateRandomStr(strLen: int):
    return "".join([random.choice(string.ascii_letters) for _ in range(0, strLen)])