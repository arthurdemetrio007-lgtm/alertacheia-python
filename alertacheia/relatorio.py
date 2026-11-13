"""Exibição no terminal e gravação dos resultados."""

import pandas as pd

ROTULOS = {"NORMAL": "Normal", "ATENCAO": "Atenção", "ALERTA": "Alerta", "EVACUAR": "Evacuar"}


def formatar_horas(horas):
    if horas is None or pd.isna(horas):
        return "não prevê"
    if horas == 0:
        return "já alagou"
    if horas < 1:
        return f"{round(horas * 60)} min"
    return f"{horas:.1f} h"


def imprimir_situacao(tabela):
    print(f"{'Bairro':<18}{'Estado':<10}{'Falta':>9}{'Alaga em':>12}{'Relatos':>9}")
    print("-" * 58)
    for linha in tabela.itertuples():
        print(
            f"{linha.bairro:<18}{ROTULOS[linha.estado]:<10}{linha.falta_cm:>6.0f} cm"
            f"{formatar_horas(linha.horas_ate_alagar):>12}{linha.relatos_ativos:>9}"
        )
    avisar = tabela[tabela["estado"] != "NORMAL"]
    if avisar.empty:
        print("\nNenhum bairro precisa de aviso agora.")
        return
    print("\nAvisos a enviar:")
    for linha in avisar.itertuples():
        print(f"- {linha.bairro} ({ROTULOS[linha.estado]}, por {linha.motivo}): {linha.acao}")


def imprimir_bairro(linha):
    print(f"\n{linha['bairro']}")
    print(f"  Estado: {ROTULOS[linha['estado']]} (por {linha['motivo']})")
    print(f"  Alaga quando o nível chega a {linha['cota_alagamento_cm']:.0f} cm; faltam {linha['falta_cm']:.0f} cm")
    print(f"  Previsão para alagar: {formatar_horas(linha['horas_ate_alagar'])}")
    print(f"  Relatos ativos dos moradores: {linha['relatos_ativos']}")
    print(f"  O que fazer: {linha['acao']}")


def _data(valor, vazio="-"):
    return valor.strftime("%d/%m %H:%M") if pd.notna(valor) else vazio


def _horas(valor):
    return f"{valor:.0f} h" if pd.notna(valor) else "-"


def imprimir_antecedencia(tabela):
    print(f"{'Bairro':<18}{'Alaga em':>9}{'1º aviso':>14}{'Alerta':>14}{'Água chegou':>14}{'Antecedência':>14}")
    print(f"{'':<18}{'':>9}{'(atenção)':>14}{'':>14}{'':>14}{'aviso/alerta':>14}")
    print("-" * 83)
    for linha in tabela.itertuples():
        antecedencia = f"{_horas(linha.antecedencia_aviso_h)}/{_horas(linha.antecedencia_alerta_h)}"
        print(
            f"{linha.bairro:<18}{linha.cota_alagamento_m:>7.2f} m{_data(linha.primeiro_aviso):>14}"
            f"{_data(linha.primeiro_alerta):>14}{_data(linha.agua_chegou, 'não alagou'):>14}{antecedencia:>14}"
        )
    avisos = tabela["antecedencia_aviso_h"].dropna()
    if not avisos.empty:
        menor = tabela.loc[avisos.idxmin(), "bairro"]
        print(
            f"\nPrimeiro aviso, em média, {avisos.mean():.0f} h antes da água chegar."
            f" Menor antecedência: {avisos.min():.0f} h ({menor})."
        )
