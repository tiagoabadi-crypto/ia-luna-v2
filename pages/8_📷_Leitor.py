import cv2
import numpy as np
from pyzbar.pyzbar import decode

def ler_codigo(img_bytes):
    try:
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        codigos = decode(img)
        for obj in codigos: return obj.data.decode('utf-8')
    except: return None