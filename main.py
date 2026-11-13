"""AlertaCheia: decide quais bairros avisar sobre alagamento e com quanta antecedência.

Uso:
    python main.py        abre o menu
    python main.py 2      roda direto uma opção do menu (1, 2 ou 3)
"""

import sys
import unicodedata

import pandas as pd

from alertacheia import config
from alertacheia.cheia2024 import salvar_grafico, simular
from alertacheia.coleta import baixar_leituras_sensor, baixar_ocorrencias
from alertacheia.decisao import avaliar_bairros, relatos_ativos
from alertacheia.guaiba import montar_serie_guaiba
from alertacheia.relatorio import imprimir_antecedencia, imprimir_bairro, imprimir_situacao
from alertacheia.tratamento import (
    carregar_bairros,
    carregar_leituras_sensor,
    carregar_ocorrencias,
    preparar_serie,
)

MENU = """
=== AlertaCheia: alerta de alagamento por bairro ===
1 - Atualizar dados (sensor e ocorrências)
2 - Ver a situação agora em cada bairro
3 - Simular a cheia de maio de 2024
4 - Consultar um bairro
0 - Sair
"""


def sem_acento(texto):
    normalizado = unicodedata.normalize("NFD", texto)
    return "".join(letra for letra in normalizado if unicodedata.category(letra) != "Mn").casefold().strip()


def atualizar_dados():
    print(baixar_leituras_sensor())
    print(baixar_ocorrencias())


def calcular_situacao():
    """Situação de cada bairro com a última leitura do sensor e os relatos ativos."""
    leituras = carregar_leituras_sensor()
    if leituras.empty:
        print("Ainda não há leituras do sensor. Use a opção 1 para baixar.")
        return None

    serie = preparar_serie(leituras, frequencia="1min", janela_taxa=5)
    ultima = serie.iloc[-1]
    momento = serie.index[-1]
    agora = pd.Timestamp.now(tz="America/Sao_Paulo")

    regua = config.REGUAS["sensor"]
    print(f"\nNível no {regua['nome']}: {ultima['nivel_suave_cm']:.1f} cm", end="")
    if pd.notna(ultima["taxa_cm_h"]):
        print(f", variando {ultima['taxa_cm_h']:+.1f} cm/h", end="")
    print(f" (leitura de {momento:%d/%m %H:%M}).")
    if agora - momento > pd.Timedelta(minutes=config.SENSOR_PARADO_MIN):
        print("Atenção: o sensor está sem enviar leituras. A análise usa o último valor recebido.")

    relatos = relatos_ativos(carregar_ocorrencias(), agora)
    situacao = avaliar_bairros(ultima["nivel_suave_cm"], ultima["taxa_cm_h"], carregar_bairros(), regua, relatos)

    config.PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    situacao.insert(0, "calculado_em", f"{agora:%Y-%m-%d %H:%M}")
    situacao.to_csv(config.PASTA_SAIDA / "situacao_bairros.csv", index=False)
    return situacao


def ver_situacao():
    situacao = calcular_situacao()
    if situacao is not None:
        print()
        imprimir_situacao(situacao)
        print("\nTabela salva em dados/saida/situacao_bairros.csv")


def consultar_bairro():
    situacao = calcular_situacao()
    if situacao is None:
        return
    nome = input("\nNome do bairro: ")
    encontrados = situacao[situacao["bairro"].map(sem_acento) == sem_acento(nome)]
    if encontrados.empty:
        print("Bairro não monitorado. Bairros disponíveis: " + ", ".join(sorted(situacao["bairro"])))
        return
    imprimir_bairro(encontrados.iloc[0])


def simular_cheia_2024():
    serie_guaiba = montar_serie_guaiba()
    antecedencia, serie = simular(serie_guaiba, carregar_bairros())
    pico = serie_guaiba.loc[serie_guaiba["nivel_cm"].idxmax()]
    print(f"\nPico da cheia: {pico['nivel_cm'] / 100:.2f} m em {pico['data']:%d/%m %H:%M}.")
    print("Se o AlertaCheia existisse em 2024, cada bairro teria sido avisado assim:\n")
    imprimir_antecedencia(antecedencia)

    config.PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    serie_guaiba.to_csv(config.PASTA_SAIDA / "guaiba_2024_cais_maua.csv", index=False)
    antecedencia.to_csv(config.PASTA_SAIDA / "cheia_2024_antecedencia.csv", index=False)
    inicio_medicao = serie_guaiba.loc[serie_guaiba["origem"].str.startswith("ANA"), "data"].min()
    salvar_grafico(serie, antecedencia, config.PASTA_SAIDA / "cheia_2024.png", inicio_medicao)
    print("\nResultados salvos em dados/saida: guaiba_2024_cais_maua.csv, cheia_2024_antecedencia.csv e cheia_2024.png")


def executar(opcao):
    match opcao:
        case "1":
            atualizar_dados()
        case "2":
            ver_situacao()
        case "3":
            simular_cheia_2024()
        case "4":
            consultar_bairro()
        case "0":
            return False
        case _:
            print("Opção inválida. Digite um número do menu.")
    return True


def main():
    if len(sys.argv) > 1:
        executar(sys.argv[1])
        return
    continuar = True
    while continuar:
        print(MENU)
        continuar = executar(input("Escolha uma opção: ").strip())
    print("Até logo.")


if __name__ == "__main__":
    main()
