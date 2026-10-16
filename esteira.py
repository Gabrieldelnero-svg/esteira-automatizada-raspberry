
import threading
import time

import cv2
import RPi.GPIO as GPIO

import config
import db
from visao import Visao

# Sequência de meio-passo  (4096 passos por volta do eixo)
SEQ = [(1, 0, 0, 0), (1, 1, 0, 0), (0, 1, 0, 0), (0, 1, 1, 0),
       (0, 0, 1, 0), (0, 0, 1, 1), (0, 0, 0, 1), (1, 0, 0, 1)]


class Motor:
    def __init__(self, pinos):
        self.pinos, self.idx = pinos, 0
        for p in pinos:
            GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)

    def passo(self, sentido=1):
        self.idx = (self.idx + sentido) % 8
        for p, v in zip(self.pinos, SEQ[self.idx]):
            GPIO.output(p, v)

    def liberar(self):  
        for p in self.pinos:
            GPIO.output(p, 0)

    def mover(self, passos, atraso):
        sentido = 1 if passos >= 0 else -1
        for _ in range(abs(passos)):
            self.passo(sentido)
            time.sleep(atraso)
        self.liberar()


class Esteira(threading.Thread):
    """Gira o motor da esteira continuamente enquanto estiver ligada."""

    def __init__(self, motor):
        super().__init__(daemon=True)
        self.motor, self.ligada, self.encerrar = motor, threading.Event(), threading.Event()

    def run(self):
        while not self.encerrar.is_set():
            if self.ligada.is_set():
                self.motor.passo(config.SENTIDO_ESTEIRA)
                time.sleep(config.ATRASO_PASSO_ESTEIRA)
            else:
                self.motor.liberar()
                time.sleep(0.05)


class Separador:
    def __init__(self, motor):
        self.motor, self.trava = motor, threading.Lock()

    def desviar_e_voltar(self):
        with self.trava:  
            self.motor.mover(config.PASSOS_DESVIO, config.ATRASO_PASSO_SEPARADOR)
            time.sleep(config.TEMPO_DESVIADO)
            self.motor.mover(-config.PASSOS_DESVIO, config.ATRASO_PASSO_SEPARADOR)


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    db.iniciar()

    
    for pino in config.LASER.values():
        GPIO.setup(pino, GPIO.OUT, initial=GPIO.HIGH)

    esteira = Esteira(Motor(config.MOTOR_ESTEIRA))
    separador = Separador(Motor(config.MOTOR_SEPARADOR))
    esteira.start()

  
    borda = GPIO.RISING if config.LDR_NIVEL_INTERROMPIDO else GPIO.FALLING
    for saida, pino in config.LDR_DO.items():
        GPIO.setup(pino, GPIO.IN)
        GPIO.add_event_detect(pino, borda, bouncetime=config.LDR_BOUNCE_MS,
                              callback=lambda canal, s=saida: (db.registrar_contagem(s),
                                                               print(f"[contagem] saída {s}")))

    cam = cv2.VideoCapture(config.CAMERA_INDEX)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, config.LARGURA)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, config.ALTURA)
    if not cam.isOpened():
        raise SystemExit("Câmera não encontrada. Verifique o cabo CSI e o driver (/dev/video0).")

    visao = Visao()
    esteira.ligada.set()
    ultimo_qr, ultimo_t = None, 0.0
    print("Esteira em operação. Ctrl+C para encerrar.")
    try:
        while True:
            ok, frame = cam.read()
            if not ok:
                time.sleep(0.1)
                continue
            qr = visao.ler_qr(frame)
            if not qr:
                continue
            agora = time.time()
            if qr == ultimo_qr and agora - ultimo_t < config.COOLDOWN_LEITURA_S:
                continue  
            ultimo_qr, ultimo_t = qr, agora

            cor = visao.detectar_cor(frame)
            produto, saida = visao.decidir(qr, cor)
            db.registrar_leitura(qr, cor, produto, saida)
            print(f"[leitura] QR={qr} cor={cor} produto={produto} -> saída {saida}")
            if saida == 2:
                threading.Timer(config.ATRASO_CAMERA_SEPARADOR, separador.desviar_e_voltar).start()
    except KeyboardInterrupt:
        pass
    finally:
        esteira.ligada.clear()
        esteira.encerrar.set()
        cam.release()
        for pino in config.LASER.values():
            GPIO.output(pino, GPIO.LOW)
        GPIO.cleanup()
        print("Encerrado.")


if __name__ == "__main__":
    main()
