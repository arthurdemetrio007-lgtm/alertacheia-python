"""Configurações: caminhos, endereços das APIs e limites de nível.

Os limites do sensor são os mesmos do firmware (alertacheia-edge/include/config.h).
Os limites do Guaíba são as cotas oficiais de alerta (2,55 m) e de inundação (3,00 m)
da régua do Cais Mauá em 2024, segundo o Governo do Estado do RS.
"""

from pathlib import Path

PASTA_PROJETO = Path(__file__).resolve().parent.parent
PASTA_ENTRADA = PASTA_PROJETO / "dados" / "entrada"
PASTA_SAIDA = PASTA_PROJETO / "dados" / "saida"

ARQUIVO_BAIRROS = PASTA_ENTRADA / "bairros.csv"
ARQUIVO_SENSOR = PASTA_ENTRADA / "leituras_sensor.csv"
ARQUIVO_OCORRENCIAS = PASTA_ENTRADA / "ocorrencias.json"
ARQUIVO_GUAIBA_ANA = PASTA_ENTRADA / "ana_87450020_2024.xls"
ARQUIVO_GUAIBA_SUBIDA = PASTA_ENTRADA / "guaiba_subida_2024.csv"

# APIs usadas pelo sensor (Edge) e pelo app web (Front-end e Web Development)
THINGSPEAK_CANAL = "3567645"
THINGSPEAK_CHAVE_LEITURA = "E8I3MJ2EBERKUQXO"  # chave só de leitura
URL_SENSOR = f"https://api.thingspeak.com/channels/{THINGSPEAK_CANAL}/feeds.json"
URL_OCORRENCIAS = "https://6af3cb2255a1de7dcf034822.mockapi.io/api/v1/ocorrencias"
TEMPO_LIMITE_S = 15

# Réguas de nível. Cada bairro começa a alagar em "inundacao + margem do bairro".
REGUAS = {
    "sensor": {"nome": "sensor do arroio", "alerta_cm": 150, "inundacao_cm": 200},
    "guaiba": {"nome": "Guaíba no Cais Mauá", "alerta_cm": 255, "inundacao_cm": 300},
}

# Regras de decisão
HORAS_PARA_ALERTA = 6       # água deve chegar ao bairro em até 6 h: alerta
HORAS_PARA_ATENCAO = 24     # água deve chegar ao bairro em até 24 h: atenção
HORAS_RELATOS_RECENTES = 12  # relatos dos moradores valem por 12 h
SENSOR_PARADO_MIN = 10      # sem leitura nova há mais de 10 min: sensor parado
