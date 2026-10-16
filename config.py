
import os

PASTA = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PASTA, "esteira.db")

# ---------------- GPIO (BCM) ----------------
MOTOR_ESTEIRA = [17, 18, 27, 22]    # IN1..IN4 do ULN2003 nº 1 (pinos físicos 11, 12, 13, 15)
MOTOR_SEPARADOR = [5, 6, 13, 19]    # IN1..IN4 do ULN2003 nº 2 (pinos físicos 29, 31, 33, 35)
LASER = {1: 12, 2: 16}              # base do 2N2222A: pinos físicos 32 e 36
LDR_DO = {1: 20, 2: 21}             # saída DO do LM393: pinos físicos 38 e 40
# GPIO23 e GPIO24 estão livres.

# ---------------- Motores 28BYJ-48 ----------------
ATRASO_PASSO_ESTEIRA = 0.002        # s entre passos (menor = mais rápido; abaixo de ~0,0015 o motor perde passos)
ATRASO_PASSO_SEPARADOR = 0.002
SENTIDO_ESTEIRA = 1                 # use -1 para inverter o sentido da esteira
PASSOS_DESVIO = 512                 # meio-passo: 4096 = 1 volta, 512 ≈ 45° (ajustar ao braço)
TEMPO_DESVIADO = 1.5                # s que o braço fica desviado antes de voltar
ATRASO_CAMERA_SEPARADOR = 2.0       # s entre ler a caixa e acionar o braço (calibrar com a velocidade da esteira)

# ---------------- LDR + LM393 ----------------
# Nível lógico de DO quando o feixe está INTERROMPIDO (1 = HIGH, 0 = LOW).
# Varia conforme o módulo: teste no seu e ajuste aqui (e no potenciômetro).
LDR_NIVEL_INTERROMPIDO = 1
LDR_BOUNCE_MS = 300                 # ignora novas interrupções por este tempo

# ---------------- Câmera / visão ----------------
CAMERA_INDEX = 0
LARGURA, ALTURA = 320, 240
COOLDOWN_LEITURA_S = 3.0            # evita registrar a mesma caixa várias vezes
MIN_PIXELS_COR = 1500               # mínimo de pixels da cor na região central

# Faixas HSV do OpenCV (H 0-179). Calibrar com a iluminação real.
CORES = {
    "vermelho": [((0, 120, 70), (10, 255, 255)), ((170, 120, 70), (179, 255, 255))],
    "amarelo":  [((20, 100, 100), (35, 255, 255))],
    "verde":    [((40, 80, 50), (85, 255, 255))],
    "azul":     [((95, 100, 50), (130, 255, 255))],
}

# ---------------- Regras de destino ----------------
# Texto do QR Code -> produto e saída (1 = reta, 2 = lateral, com o separador acionado)
PRODUTOS = {
    "CAIXA_A": {"produto": "Produto A", "saida": 1},
    "CAIXA_B": {"produto": "Produto B", "saida": 2},
    "CAIXA_C": {"produto": "Produto C", "saida": 2},
}
# Se não houver QR válido, decide pela cor.
REGRA_COR = {"vermelho": 2, "azul": 2}
SAIDA_PADRAO = 1
