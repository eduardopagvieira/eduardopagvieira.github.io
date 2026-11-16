"""
Gera os dados resumidos do painel do site (dados/painel.js) a partir das bases tratadas dos projetos.

Lê, nas pastas vizinhas do portfólio,
    ../rouanet/dados/tratados/projetos.csv
    ../rouanet/dados/auxiliares/populacao_uf.csv
    ../consumidor/dados/tratados/reclamacoes_2025.csv.gz
    ../bndes/dados/tratados/operacoes.parquet
    ../bndes/resultados/macro_anual.csv
    ../rouanet/resultados/texto_temas.csv e texto_palavras.csv (gerados por rouanet/textos.py)

e grava um único arquivo pequeno com cubos já agregados. O painel filtra esses cubos no navegador,
então o site continua estático e abre rápido.

Uso
    python gerar_dados.py
"""

import json
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
SAIDA = AQUI / "dados" / "painel.js"

SEGMENTOS_CURTOS = {
    "Bancos, Financeiras e Administradoras de Cartão": "Bancos e cartões",
    "Operadoras de Telecomunicações (Telefonia, Internet, TV por assinatura)": "Telecomunicações",
    "Bancos de Dados e Cadastros de Consumidores": "Cadastros de consumidores",
    "Provedores de Conteúdo e Outros Serviços na Internet": "Serviços na internet",
    "Operadoras de Planos de Saúde e Administradoras de Benefícios": "Planos de saúde",
    "Empresas de Intermediação de Serviços / Negócios": "Intermediação de serviços",
    "Seguros, Capitalização e Previdência": "Seguros e previdência",
    "Empresas de Pagamento Eletrônico": "Pagamento eletrônico",
    "Empresas de Recuperação de Crédito": "Recuperação de crédito",
    "Transporte Aéreo": "Transporte aéreo",
    "Comércio Eletrônico": "Comércio eletrônico",
    "Energia Elétrica": "Energia elétrica",
}
SEGMENTOS_NO_FILTRO = 10      # os demais viram "Outros"
EMPRESAS_NO_RANKING = 40


def rouanet():
    pasta = RAIZ / "rouanet"
    t = pd.read_csv(pasta / "dados/tratados/projetos.csv", encoding="utf-8-sig", low_memory=False,
                    usecols=["ano", "regiao", "uf", "area", "aprovado", "captou", "valor_aprovado", "valor_captado"])
    a = t[t["aprovado"] & t["ano"].between(2019, 2025)]
    cubo = (a.groupby(["ano", "regiao", "area"])
              .agg(projetos=("ano", "size"), aprovado=("valor_aprovado", "sum"), captado=("valor_captado", "sum"),
                   captaram=("captou", "sum"))
              .reset_index())
    pop = pd.read_csv(pasta / "dados/auxiliares/populacao_uf.csv").set_index("uf")["populacao"]
    uf = a.groupby(["ano", "uf", "regiao", "area"])["valor_captado"].sum().reset_index()
    temas = pd.read_csv(pasta / "resultados/texto_temas.csv", encoding="utf-8-sig")
    pal = pd.read_csv(pasta / "resultados/texto_palavras.csv", encoding="utf-8-sig")
    pal = pal[~pal["palavra"].str.contains(" ")]
    return {
        "campos": ["ano", "regiao", "area", "projetos", "aprovado", "captado", "captaram"],
        "cubo": [[int(r.ano), r.regiao, r.area, int(r.projetos), round(r.aprovado), round(r.captado), int(r.captaram)]
                 for r in cubo.itertuples()],
        "uf": [[int(r.ano), r.uf, r.regiao, r.area, round(r.valor_captado)] for r in uf.itertuples() if r.valor_captado > 0],
        "populacao": {k: int(v) for k, v in pop.items()},
        "temas": [[r.nome, int(r.projetos), round(r.bruta, 4), round(r.ajustada, 4), bool(r.generico)]
                  for r in temas.itertuples()],
        "palavras_sim": pal.head(12)["palavra"].replace({"line": "on-line"}).tolist(),
        "palavras_nao": pal.tail(12)["palavra"].iloc[::-1].tolist(),
    }


def consumidor():
    cols = ["mes", "regiao", "empresa", "segmento", "respondida", "avaliada", "resolvida", "nota"]
    t = pd.read_csv(RAIZ / "consumidor/dados/tratados/reclamacoes_2025.csv.gz", encoding="utf-8-sig", usecols=cols,
                    dtype={"mes": "category", "regiao": "category", "empresa": "category", "segmento": "category"},
                    low_memory=False)
    t["resolvida"] = t["resolvida"].astype("boolean").fillna(False).astype(int)
    t["respondida"] = t["respondida"].astype(bool).astype(int)
    t["avaliada"] = t["avaliada"].astype(bool).astype(int)
    t["nota"] = t["nota"].fillna(0)
    maiores = t["segmento"].value_counts().head(SEGMENTOS_NO_FILTRO).index
    t["seg"] = t["segmento"].astype(str).where(t["segmento"].isin(maiores), "Outros")
    t["seg"] = t["seg"].map(lambda s: SEGMENTOS_CURTOS.get(s, s))
    t["regiao"] = t["regiao"].astype(str).replace({"nan": "Não informada"})
    cubo = (t.groupby(["mes", "seg", "regiao"], observed=True)
              .agg(n=("mes", "size"), respondidas=("respondida", "sum"), avaliadas=("avaliada", "sum"),
                   resolvidas=("resolvida", "sum"), soma_notas=("nota", "sum"))
              .reset_index())
    emp = (t.groupby(["empresa", "seg"], observed=True)
             .agg(n=("mes", "size"), respondidas=("respondida", "sum"), avaliadas=("avaliada", "sum"),
                  resolvidas=("resolvida", "sum"), soma_notas=("nota", "sum"))
             .reset_index().sort_values("n", ascending=False))
    emp = emp.drop_duplicates("empresa").head(EMPRESAS_NO_RANKING)
    return {
        "campos": ["mes", "segmento", "regiao", "n", "respondidas", "avaliadas", "resolvidas", "soma_notas"],
        "cubo": [[r.mes, r.seg, r.regiao, int(r.n), int(r.respondidas), int(r.avaliadas), int(r.resolvidas),
                  int(r.soma_notas)] for r in cubo.itertuples()],
        "empresas": [[str(r.empresa).strip(), r.seg, int(r.n), int(r.respondidas), int(r.avaliadas), int(r.resolvidas),
                      int(r.soma_notas)] for r in emp.itertuples()],
    }


def bndes():
    pasta = RAIZ / "bndes"
    d = pd.read_parquet(pasta / "dados/tratados/operacoes.parquet",
                        columns=["ano", "setor", "porte", "regiao", "valor_contratado_real"])
    d["regiao"] = d["regiao"].astype(str).replace({"nan": "Não informada"})
    cubo = (d.groupby(["ano", "setor", "porte", "regiao"], observed=True)
              .agg(operacoes=("ano", "size"), valor=("valor_contratado_real", "sum")).reset_index())
    macro = pd.read_csv(pasta / "resultados/macro_anual.csv")
    return {
        "campos": ["ano", "setor", "porte", "regiao", "operacoes", "valor"],
        "cubo": [[int(r.ano), r.setor, r.porte, r.regiao, int(r.operacoes), round(r.valor / 1e6, 1)]
                 for r in cubo.itertuples() if r.operacoes > 0],
        "pib": [[int(r.ano), round(r.contratado_pib, 4)] for r in macro.itertuples()],
    }


def main():
    dados = {"rouanet": rouanet(), "consumidor": consumidor(), "bndes": bndes()}
    SAIDA.parent.mkdir(exist_ok=True)
    texto = json.dumps(dados, ensure_ascii=False, separators=(",", ":"))
    SAIDA.write_text("// Gerado por gerar_dados.py. Não editar à mão.\nwindow.PAINEL = " + texto + ";\n", encoding="utf-8")
    print(f"{SAIDA.name}: {SAIDA.stat().st_size / 1024:.0f} KB")
    for k, v in dados.items():
        print(f"  {k}: {len(v['cubo'])} linhas no cubo")


if __name__ == "__main__":
    main()
