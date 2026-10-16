
import cv2
import numpy as np
import config


class Visao:
    def __init__(self):
        self.qr = cv2.QRCodeDetector()

    def ler_qr(self, frame):
        texto, _, _ = self.qr.detectAndDecode(frame)
        return texto.strip() or None

    def detectar_cor(self, frame):
        """Cor predominante na região central da imagem (onde a caixa deve estar)."""
        h, w = frame.shape[:2]
        roi = frame[h // 4: 3 * h // 4, w // 4: 3 * w // 4]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        melhor, maximo = "desconhecida", 0
        for nome, faixas in config.CORES.items():
            mascara = None
            for baixo, alto in faixas:
                m = cv2.inRange(hsv, np.array(baixo), np.array(alto))
                mascara = m if mascara is None else cv2.bitwise_or(mascara, m)
            n = cv2.countNonZero(mascara)
            if n > maximo:
                melhor, maximo = nome, n
        return melhor if maximo >= config.MIN_PIXELS_COR else "desconhecida"

    @staticmethod
    def decidir(qr, cor):
        """Retorna (produto, saida): o QR Code manda; sem QR válido, decide pela cor."""
        if qr in config.PRODUTOS:
            p = config.PRODUTOS[qr]
            return p["produto"], p["saida"]
        return "Sem QR (" + cor + ")", config.REGRA_COR.get(cor, config.SAIDA_PADRAO)
