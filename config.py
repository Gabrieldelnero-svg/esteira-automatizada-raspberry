
import os

PASTA = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PASTA, "esteira.db")

# GPIO (BCM) 
MOTOR_ESTEIRA = [17, 18, 27, 22]    #  (pinos físicos 11, 12, 13, 15)
MOTOR_SEPARADOR = [5, 6, 13, 19]    #  (pinos físicos 29, 31, 33, 35)
LASER = {1: 12, 2: 16}              # base do 2N2222A: pinos físicos 32 e 36
LDR_DO = {1: 20, 2: 21}             # saída DO do LM393: pinos físicos 38 e 40


# Motores 28BYJ-48 
ATRASO_PASSO_ESTEIRA = 0.002        
ATRASO_PASSO_SEPARADOR = 0.002
SENTIDO_ESTEIRA = 1                 # -1 para inverter o sentido da esteira
PASSOS_DESVIO = 512                 # meio-passo: 4096 = 1 volta, 512 ≈ 45° (ajustar ao braço)
TEMPO_DESVIADO = 1.5                
ATRASO_CAMERA_SEPARADOR = 2.0      

#  LDR + LM393 

LDR_NIVEL_INTERROMPIDO = 1
LDR_BOUNCE_MS = 300               

# Câmera 
CAMERA_INDEX = 0
LARGURA, ALTURA = 320, 240
COOLDOWN_LEITURA_S = 3.0            
MIN_PIXELS_COR = 1500               

# Faixas HSV do OpenCV
CORES = {
    "vermelho": [((0, 120, 70), (10, 255, 255)), ((170, 120, 70), (179, 255, 255))],
    "amarelo":  [((20, 100, 100), (35, 255, 255))],
    "verde":    [((40, 80, 50), (85, 255, 255))],
    "azul":     [((95, 100, 50), (130, 255, 255))],
}



PRODUTOS = {
    "CAIXA_A": {"produto": "Produto A", "saida": 1},
    "CAIXA_B": {"produto": "Produto B", "saida": 2},
    "CAIXA_C": {"produto": "Produto C", "saida": 2},
}

REGRA_COR = {"vermelho": 2, "azul": 2}
SAIDA_PADRAO = 1
