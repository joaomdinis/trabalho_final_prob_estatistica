import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pyarrow.parquet as pq
import streamlit as st

ROOT = Path(__file__).resolve().parent
ARQUIVOS = {
  "pop": ROOT / "data" / "processed" / "populacao.parquet",
  "amo": ROOT / "outputs" / "amostra" / "amostra.parquet",
}
JSONS = {
  "inf": ROOT / "outputs" / "results" / "inferencia.json",
  "ilu": ROOT / "outputs" / "results" / "ilustracao.json",
}
TEXTOS = ROOT / "app" / "textos"
COLUNAS = ["mulher", "nivel_sup", "superior_completo", "situacao_rendimento", "pos_indeterminado", "rendimento"]
NIVEIS = ["sem superior completo", "graduação", "especialização", "mestrado", "doutorado"]
SITUACOES = ["valido", "zero", "outra_forma", "nao_remunerado", "sem_informacao"]
ROTULO_SIT = {
  "valido": "válido",
  "zero": "zero",
  "outra_forma": "outra forma (sem dinheiro, produtos ou mercadorias)",
  "nao_remunerado": "não remunerado (ajuda a morador ou parente)",
  "sem_informacao": "sem informação",
}
SEXOS = ["mulher", "homem"]
GRUPOS = ["total", "mulher", "homem"]
ROTULO_GRUPO = {"total": "Total", "mulher": "Mulheres", "homem": "Homens"}
COR = {"mulher": "#2a6fbb", "homem": "#e08a00", "pop": "#7a7a7a", "amo": "#2a6fbb"}
COR_ILU = {"cobre": "#8a9bb0", "inteiro_abaixo": "#d1495b", "inteiro_acima": "#e08a00"}
QPS = ["qp1", "qp2", "qp3", "qp4"]
QP_NOME = {
  "qp1": "QP1: proporção com superior completo, mulheres ocupadas",
  "qp2": "QP2: proporção acima da mediana dos homens, mulheres com superior",
  "qp3": "QP3: rendimento médio, mulheres ocupadas",
  "qp4": "QP4: rendimento médio, mulheres com superior",
}
VEREDITO = {"vale": "vale", "nao_vale": "não vale"}
NUM_FAIXAS_HIST = 40
BINS_ILUSTRACAO = 30


def fnum(x, d):
  if x is None or (isinstance(x, float) and np.isnan(x)):
    return "—"
  s = f"{x:,.{d}f}"
  return s.replace(",", "X").replace(".", ",").replace("X", ".")


def fauto(x):
  if isinstance(x, str):
    return x
  return fnum(x, 0 if float(x).is_integer() else 2)


def pct(x, d=1):
  return "—" if x is None or np.isnan(x) else fnum(x * 100, d) + "%"


def pp(x, d=2):
  return "—" if x is None or np.isnan(x) else ("+" if x > 0 else "") + fnum(x * 100, d) + " p.p."


def rs(x):
  return "—" if x is None or np.isnan(x) else "R$ " + fnum(x, 2)


def rs_dif(x):
  return "—" if np.isnan(x) else ("+" if x > 0 else "-" if x < 0 else "") + rs(abs(x))


def fp(p):
  return "< 0,0001" if p < 0.0001 else fnum(p, 4)


def div(a, b):
  return a / b if b else float("nan")


def ler_texto(nome):
  caminho = TEXTOS / nome
  if not caminho.exists():
    st.info(f"Texto ainda não disponível: app/textos/{nome}")
    return
  principal, _, detalhe = caminho.read_text(encoding="utf-8").partition("<!-- saiba-mais -->")
  st.markdown(principal)
  if detalhe.strip():
    with st.expander("Saiba mais"):
      st.markdown(detalhe)


@st.cache_resource(show_spinner=False)
def ler_json(chave):
  return json.loads(JSONS[chave].read_text(encoding="utf-8"))


@st.cache_resource(show_spinner="Carregando dados")
def carregar(nome):
  t = pq.read_table(ARQUIVOS[nome], columns=COLUNAS).to_pandas()
  sit = pd.Categorical(t["situacao_rendimento"], categories=SITUACOES).codes
  assert (sit >= 0).all()
  d = {
    "mulher": t["mulher"].to_numpy(dtype=bool),
    "nivel": t["nivel_sup"].to_numpy(dtype=np.int8),
    "s": t["superior_completo"].to_numpy(dtype=bool),
    "sit": sit.astype(np.int8),
    "pos": t["pos_indeterminado"].to_numpy(dtype=bool),
    "y": t["rendimento"].to_numpy(dtype=np.float64),
  }
  d["ok"] = ~np.isnan(d["y"])
  d["cell"] = (d["mulher"] * 5 + d["nivel"]).astype(np.uint8)
  return d


def mascara(d, sexos, niveis):
  lut = np.zeros(10, dtype=bool)
  for s, n in itertools.product(sexos, niveis):
    lut[s * 5 + n] = True
  return lut[d["cell"]]


def resumo(y, ddof):
  if y.size == 0:
    return {k: float("nan") for k in ["media", "mediana", "desvio_padrao", "q1", "q3", "p10", "p90", "minimo", "maximo", "cv"]} | {"n": 0}
  p10, q1, med, q3, p90 = np.percentile(y, [10, 25, 50, 75, 90])
  media = float(y.mean())
  dp = float(y.std(ddof=ddof)) if y.size > ddof else float("nan")
  return {
    "n": int(y.size), "media": media, "mediana": float(med), "desvio_padrao": dp, "q1": float(q1), "q3": float(q3),
    "p10": float(p10), "p90": float(p90), "minimo": float(y.min()), "maximo": float(y.max()), "cv": dp / media,
  }


@st.cache_data(show_spinner="Calculando", max_entries=64)
def calcular(nome, sexos, niveis):
  d = carregar(nome)
  ddof = 0 if nome == "pop" else 1
  m = mascara(d, sexos, niveis)
  base = {"total": m, "mulher": m & d["mulher"], "homem": m & ~d["mulher"]}
  res = {}
  for g, mg in base.items():
    rend = mg & d["ok"]
    res[g] = {
      "registros": int(mg.sum()),
      "s": int((mg & d["s"]).sum()),
      "nivel": np.bincount(d["nivel"][mg], minlength=5).tolist(),
      "sit": np.bincount(d["sit"][mg], minlength=5).tolist(),
      "pos": int((mg & d["pos"]).sum()),
      "rend": resumo(d["y"][rend], ddof),
      "rend_s": resumo(d["y"][rend & d["s"]], ddof),
      "rend_sem": resumo(d["y"][rend & ~d["s"]], ddof),
    }
  yv = d["y"][m & d["ok"]]
  lim = (float(np.percentile(yv, 99)), float(yv.min()), float(yv.max())) if yv.size else None
  return {"grupos": res, "lim": lim}


@st.cache_data(show_spinner="Calculando", max_entries=64)
def histograma(nome, sexos, niveis, log, arestas):
  d = carregar(nome)
  m = mascara(d, sexos, niveis) & d["ok"]
  out = {}
  for g, mg in {"mulher": m & d["mulher"], "homem": m & ~d["mulher"]}.items():
    y = d["y"][mg]
    out[g] = np.histogram(np.log10(y) if log else y, bins=np.array(arestas))[0].tolist()
  out["total_valido"] = int(m.sum())
  return out


def arestas_de(lim, log):
  if log:
    lo, hi = np.log10(lim[1]), np.log10(lim[2])
    if hi <= lo:
      lo, hi = lo - 0.5, hi + 0.5
    return tuple(np.linspace(lo, hi, NUM_FAIXAS_HIST + 1))
  return tuple(np.linspace(0, lim[0], NUM_FAIXAS_HIST + 1))


def eixos(fig, x, y, log_ticks=None):
  fig.update_xaxes(title_text=x, showticklabels=True, showline=True, ticks="outside")
  fig.update_yaxes(title_text=y, showticklabels=True, showline=True, ticks="outside", rangemode="tozero")
  if log_ticks is not None:
    ks = list(range(int(np.floor(log_ticks[0])), int(np.ceil(log_ticks[1])) + 1))
    fig.update_xaxes(tickvals=ks, ticktext=[fnum(10.0 ** k, 0) for k in ks])
  fig.update_layout(separators=",.", margin={"t": 30, "r": 10}, legend={"orientation": "h", "y": -0.25})
  return fig


def grafico(fig, chave):
  st.plotly_chart(fig, width="stretch", key=chave)


def barras_hist(series, arestas, log, x, y, chave, medianas=()):
  ar = np.array(arestas)
  centros = (ar[:-1] + ar[1:]) / 2
  fig = go.Figure()
  for nome, valores, cor in series:
    fig.add_bar(x=centros, y=valores, width=np.diff(ar), name=nome, marker_color=cor, opacity=0.6)
  topo = max(max(valores) for _, valores, _ in series) * 1.05
  for nome, valor, cor in medianas:
    if not np.isnan(valor):
      fig.add_trace(go.Scatter(
        x=[np.log10(valor) if log else valor] * 2, y=[0, topo], mode="lines",
        name=f"Mediana, {nome.lower()}: {rs(valor)}", line={"color": cor, "dash": "dash", "width": 2},
      ))
  fig.update_layout(barmode="overlay", bargap=0)
  eixos(fig, x, y, (ar[0], ar[-1]) if log else None)
  if not log:
    fig.update_xaxes(tickformat=",.0f")
  grafico(fig, chave)


def tabela(df):
  st.dataframe(df, hide_index=True, width="stretch")


def linha_grupos(rotulo, f):
  return [rotulo] + [f(g) for g in GRUPOS]


def painel(nome, chave, sexos, niveis):
  res = calcular(nome, sexos, niveis)
  g = res["grupos"]
  if g["total"]["registros"] == 0:
    st.warning("Nenhum registro atende à combinação de filtros.")
    return None
  st.subheader("Indicadores")
  tabela(pd.DataFrame(
    [
      linha_grupos("Pessoas (N)", lambda k: fnum(g[k]["registros"], 0)),
      linha_grupos("Participação no total", lambda k: pct(div(g[k]["registros"], g["total"]["registros"]))),
      linha_grupos("Proporção com superior completo", lambda k: pct(div(g[k]["s"], g[k]["registros"]))),
      linha_grupos("Pessoas com rendimento válido", lambda k: fnum(g[k]["rend"]["n"], 0)),
      linha_grupos("Rendimento médio (R$)", lambda k: rs(g[k]["rend"]["media"])),
      linha_grupos("Rendimento mediano (R$)", lambda k: rs(g[k]["rend"]["mediana"])),
      linha_grupos("Desvio-padrão do rendimento (R$)", lambda k: rs(g[k]["rend"]["desvio_padrao"])),
    ],
    columns=["Indicador"] + [ROTULO_GRUPO[k] for k in GRUPOS],
  ))
  with st.expander("Tabelas de frequência"):
    c1, c2 = st.columns(2)
    with c1:
      st.markdown("**Sexo**")
      tabela(pd.DataFrame(
        [[ROTULO_GRUPO[k], fnum(g[k]["registros"], 0), pct(div(g[k]["registros"], g["total"]["registros"]))] for k in SEXOS],
        columns=["Sexo", "Pessoas", "Proporção"],
      ))
    with c2:
      st.markdown("**Superior completo por sexo** (proporção dentro do sexo)")
      linhas = []
      for k in SEXOS:
        linhas.append([ROTULO_GRUPO[k], "com superior completo", fnum(g[k]["s"], 0), pct(div(g[k]["s"], g[k]["registros"]))])
        linhas.append([ROTULO_GRUPO[k], "sem superior completo", fnum(g[k]["registros"] - g[k]["s"], 0), pct(div(g[k]["registros"] - g[k]["s"], g[k]["registros"]))])
      tabela(pd.DataFrame(linhas, columns=["Sexo", "Categoria", "Pessoas", "Proporção"]))

    def por_sexo(rotulos, campo, titulo, casas=lambda i: 1):
      linhas = []
      for i, r in enumerate(rotulos):
        linha = [r]
        for k in SEXOS:
          linha += [fnum(g[k][campo][i], 0), pct(div(g[k][campo][i], g[k]["registros"]), casas(i))]
        linhas.append(linha)
      return pd.DataFrame(linhas, columns=[titulo, "Mulheres: pessoas", "Mulheres: proporção", "Homens: pessoas", "Homens: proporção"])

    st.markdown("**Nível de escolaridade superior por sexo** (proporção dentro do sexo)")
    tabela(por_sexo(NIVEIS, "nivel", "Nível"))
    st.caption(
      f"Superior completo com nível indeterminado, contado como graduação: mulheres {fnum(g['mulher']['pos'], 0)} "
      f"({pct(div(g['mulher']['pos'], g['mulher']['registros']))} das ocupadas), homens {fnum(g['homem']['pos'], 0)} "
      f"({pct(div(g['homem']['pos'], g['homem']['registros']))} dos ocupados)."
    )
    st.markdown("**Situação do rendimento por sexo** (proporção das pessoas ocupadas do sexo)")
    sit = por_sexo([ROTULO_SIT[s] for s in SITUACOES], "sit", "Situação", casas=lambda i: 1 if i == 0 else 3)
    excl = ["Total excluído do rendimento (soma das categorias não válidas)"]
    for k in SEXOS:
      n = sum(g[k]["sit"][1:])
      excl += [fnum(n, 0), pct(div(n, g[k]["registros"]), 3)]
    sit.loc[len(sit)] = excl
    tabela(sit)

  st.subheader("Gráficos")
  linhas_nivel = [(ROTULO_GRUPO[k], [100 * div(v, g[k]["registros"]) for v in g[k]["nivel"]], COR[k]) for k in SEXOS]
  fig = go.Figure([go.Bar(x=NIVEIS, y=y, name=n, marker_color=c) for n, y, c in linhas_nivel])
  fig.update_layout(barmode="group")
  eixos(fig, "Nível de escolaridade superior", "Proporção (%)")
  grafico(fig, f"{chave}_nivel")
  fig = go.Figure(go.Bar(x=[ROTULO_GRUPO[k] for k in SEXOS], y=[100 * div(g[k]["s"], g[k]["registros"]) for k in SEXOS], marker_color=[COR[k] for k in SEXOS]))
  eixos(fig, "Sexo", "Proporção com superior completo (%)")
  grafico(fig, f"{chave}_s")

  ref = calcular("pop", sexos, niveis)
  if ref["lim"] is None or g["total"]["rend"]["n"] == 0:
    st.info("Nenhum rendimento válido sob estes filtros: histograma e box plot não são exibidos.")
  else:
    log = st.toggle("Escala log10 no eixo do rendimento (visão descritiva)", value=True, key=f"{chave}_log")
    ar = arestas_de(ref["lim"], log)
    h = histograma(nome, sexos, niveis, log, ar)
    barras_hist(
      [(ROTULO_GRUPO[k], [100 * div(v, g[k]["rend"]["n"]) for v in h[k]], COR[k]) for k in SEXOS], ar, log,
      "Rendimento mensal (R$, escala log)" if log else "Rendimento mensal (R$)", "Proporção das pessoas do sexo (%)", f"{chave}_hist",
      [(ROTULO_GRUPO[k], g[k]["rend"]["mediana"], COR[k]) for k in SEXOS],
    )
    if not log:
      acima = g["total"]["rend"]["n"] - sum(h["mulher"]) - sum(h["homem"])
      st.caption(f"Eixo limitado ao percentil 99 do rendimento válido da população sob o filtro. {fnum(acima, 0)} pessoas com rendimento acima do limite não aparecem.")
    grupos_box = [
      ("Mulheres sem superior", g["mulher"]["rend_sem"], COR["mulher"]),
      ("Mulheres com superior", g["mulher"]["rend_s"], COR["mulher"]),
      ("Homens sem superior", g["homem"]["rend_sem"], COR["homem"]),
      ("Homens com superior", g["homem"]["rend_s"], COR["homem"]),
    ]
    fig = go.Figure()
    for rotulo, r, cor in grupos_box:
      if r["n"]:
        fig.add_trace(go.Box(
          x=[rotulo], q1=[r["q1"]], median=[r["mediana"]], q3=[r["q3"]], lowerfence=[r["p10"]], upperfence=[r["p90"]],
          mean=[r["media"]], name=rotulo, marker_color=cor, showlegend=False,
        ))
    eixos(fig, "Grupo", "Rendimento mensal (R$)")
    fig.update_yaxes(tickformat=",.0f")
    grafico(fig, f"{chave}_box")
    st.caption("Box plot: caixa de Q1 a Q3 com a mediana, hastes no percentil 10 e no percentil 90, linha tracejada na média.")

  with st.expander("Resumo do rendimento válido por sexo e por superior completo"):
    nomes_r = {"rend": "", "rend_s": " com superior completo", "rend_sem": " sem superior completo"}
    linhas = []
    for campo, suf in nomes_r.items():
      for k in GRUPOS:
        r = g[k][campo]
        linhas.append([
          ROTULO_GRUPO[k] + suf, fnum(r["n"], 0), rs(r["media"]), rs(r["mediana"]), rs(r["desvio_padrao"]), rs(r["q1"]), rs(r["q3"]),
          rs(r["p10"]), rs(r["p90"]), rs(r["minimo"]), rs(r["maximo"]), fnum(r["cv"], 2),
        ])
    tabela(pd.DataFrame(linhas, columns=["Grupo", "n", "Média", "Mediana", "Desvio-padrão", "Q1", "Q3", "P10", "P90", "Mínimo", "Máximo", "Coef. de variação"]))
  return res


def comparar(sexos, niveis):
  pop = calcular("pop", sexos, niveis)
  amo = calcular("amo", sexos, niveis)
  gp, ga = pop["grupos"], amo["grupos"]
  if ga["total"]["registros"] == 0:
    return
  itens = [("Proporção de mulheres", lambda g: div(g["mulher"]["registros"], g["total"]["registros"]), "p")]
  for k in GRUPOS:
    itens.append((f"Proporção com superior completo ({ROTULO_GRUPO[k].lower()})", lambda g, k=k: div(g[k]["s"], g[k]["registros"]), "p"))
  for k in GRUPOS:
    itens.append((f"Rendimento médio ({ROTULO_GRUPO[k].lower()})", lambda g, k=k: g[k]["rend"]["media"], "r"))
  for k in GRUPOS:
    itens.append((f"Rendimento mediano ({ROTULO_GRUPO[k].lower()})", lambda g, k=k: g[k]["rend"]["mediana"], "r"))
  linhas = []
  for rotulo, f, tipo in itens:
    vp, va = f(gp), f(ga)
    if tipo == "p":
      linhas.append([rotulo, pct(vp), pct(va), pp(va - vp)])
    else:
      linhas.append([rotulo, rs(vp), rs(va), rs_dif(va - vp)])
  st.subheader("Comparação entre população e amostra sob o filtro")
  tabela(pd.DataFrame(linhas, columns=["Indicador", "População", "Amostra", "Diferença (amostra menos população)"]))
  st.caption("Sob filtros estreitos as contagens da amostra são pequenas e as diferenças são ruidosas. Nenhum teste é feito em subconjuntos filtrados.")

  st.subheader("População e amostra sobrepostas")
  for campo, rotulos, x, ch in [("nivel", NIVEIS, "Nível de escolaridade superior", "nivel")]:
    fig = go.Figure()
    for nome, g, cor in [("População", gp, COR["pop"]), ("Amostra", ga, COR["amo"])]:
      tot = g["total"]["registros"]
      fig.add_bar(x=rotulos, y=[100 * div(v, tot) for v in g["total"][campo]], name=nome, marker_color=cor)
    fig.update_layout(barmode="group")
    eixos(fig, x, "Proporção (%)")
    grafico(fig, f"cmp_{ch}")
  if pop["lim"] is None or ga["total"]["rend"]["n"] == 0:
    st.info("Sem rendimento válido na amostra sob estes filtros: histograma sobreposto não exibido.")
    return
  log = st.toggle("Escala log10 no eixo do rendimento (visão descritiva)", value=True, key="cmp_log")
  ar = arestas_de(pop["lim"], log)
  hp, ha = histograma("pop", sexos, niveis, log, ar), histograma("amo", sexos, niveis, log, ar)
  barras_hist(
    [
      ("População", [100 * div(sum(x), hp["total_valido"]) for x in zip(hp["mulher"], hp["homem"])], COR["pop"]),
      ("Amostra", [100 * div(sum(x), ha["total_valido"]) for x in zip(ha["mulher"], ha["homem"])], COR["amo"]),
    ],
    ar, log, "Rendimento mensal (R$, escala log)" if log else "Rendimento mensal (R$)", "Proporção de pessoas (%)", "cmp_hist",
  )
  if not log:
    st.caption("Eixo limitado ao percentil 99 do rendimento válido da população sob o filtro. As proporções usam todas as pessoas com rendimento válido de cada conjunto.")


def fmt_tipo(q):
  if q["tipo"] == "proporcao":
    return {"est": lambda x: pct(x, 1), "lim": lambda x: pct(x, 2), "dif": pp, "ep": lambda x: fnum(x * 100, 2) + " p.p."}
  return {"est": rs, "lim": rs, "dif": rs_dif, "ep": rs}


def tabela_itens(itens):
  tabela(pd.DataFrame(itens, columns=["Item", "Valor"]))


def tabela_condicoes(cond):
  tabela(pd.DataFrame([[c["nome"], fauto(c["valor"]), fauto(c["limite"]), c["status"]] for c in cond], columns=["Condição", "Valor", "Limite", "Status"]))


def bloco_qp(q, alfa, nivel):
  f = fmt_tipo(q)
  ic = q["ic"]
  est = q["estatistica"]
  itens = [
    ["Variável", q["variavel"]],
    ["Domínio na amostra", q["dominio"]],
  ]
  if "evento" in q:
    itens.append(["Evento", q["evento"]])
  itens += [
    ["H0", q["h0"].replace("!=", "≠")],
    ["H1", q["h1"].replace("!=", "≠")],
    ["Nível de significância (α)", fnum(alfa, 2)],
    ["Tamanho do domínio na amostra (n)", fnum(q["n_dominio"], 0)],
    ["Estimativa pontual", f["est"](q["estimativa"])],
    [f"IC {pct(nivel, 0)} ({ic['metodo']})", f"{f['lim'](ic['inferior'])} a {f['lim'](ic['superior'])}"],
    ["Valor dos homens (comparação)", f["est"](q["referencia"])],
    ["Estatística de teste", f"{est['nome']} = {fnum(est['valor'], 2)}" + (f" (gl = {fnum(est['gl'], 0)})" if "gl" in est else "")],
    ["Valor-p", fp(q["valor_p"])],
    ["Decisão", "rejeita H0" if q["rejeita_h0"] else "não rejeita H0"],
    ["Resultado na amostra", q["veredito_amostral"]],
    ["Valor populacional do domínio", f["est"](q["valor_populacional"])],
    ["Resultado na população (arquivo)", VEREDITO[q["veredito_exato"]]],
  ]
  tabela_itens(itens)
  with st.expander("Detalhes técnicos"):
    detalhes = [["Sentido esperado", f"parâmetro {q['lado_esperado']} que a referência"]]
    if "sucessos" in q:
      detalhes.append(["Sucessos no domínio", fnum(q["sucessos"], 0)])
    if "m_H" in q:
      detalhes.append(["Mediana dos homens com superior e rendimento válido (m_H)", rs(q["m_H"])])
    detalhes += [
      ["Meia-largura do IC", f["lim"](ic["meia_largura"]) if q["tipo"] == "media" else fnum(ic["meia_largura"] * 100, 2) + " p.p."],
      ["Erro padrão" + (" sob H0" if q["tipo"] == "proporcao" else ""), f["ep"](est["erro_padrao"])],
      [f"Constante de referência ({q['referencia_nome']})", f["est"](q["referencia"])],
      ["Estimativa menos valor populacional", f["dif"](q["diferenca_estimativa_menos_populacional"])],
      ["IC contém o valor populacional", "sim" if q["ic_contem_valor_populacional"] else "não"],
    ]
    if q["tipo"] == "media":
      b = q["ic_bootstrap"]
      detalhes += [
        ["Desvio-padrão amostral", rs(q["desvio_padrao_amostral"])],
        [f"IC {pct(nivel, 0)} ({b['metodo']}, B = {fnum(b['B'], 0)}, semente {b['semente']})", f"{rs(b['inferior'])} a {rs(b['superior'])}"],
        ["Resultado pelo BCa (apenas informativo)", b["veredito"]],
        ["Assimetria amostral G1", fnum(q["assimetria_G1"], 2)],
        ["25 G1² (n mínimo de Cochran)", fnum(q["cochran_n_minimo"], 2)],
      ]
    tabela_itens(detalhes)
    if "exato" in q:
      st.markdown("**Teste binomial exato e Clopper-Pearson (condição não atendida)**")
      tabela_itens([[kk, fauto(v) if not isinstance(v, (dict, list)) else json.dumps(v, ensure_ascii=False)] for kk, v in q["exato"].items()])
    st.markdown("**Condições**")
    tabela_condicoes(q["condicoes"])
    if q["tipo"] == "media":
      st.caption(
        "Status ok na regra de Cochran não é evidência de que a aproximação t vale. Status aviso é evidência contra a aproximação. "
        "A evidência direta está na cobertura do intervalo t na ilustração abaixo."
      )
    if "duas_proporcoes" in q:
      d = q["duas_proporcoes"]
      st.markdown("**Complementar, fora de qualquer veredito: duas proporções (mulheres contra homens, ambas da amostra)**")
      tabela_itens([
        ["Mulheres ocupadas na amostra", fnum(d["n_mulheres"], 0)],
        ["Homens ocupados na amostra", fnum(d["n_homens"], 0)],
        ["Proporção com superior, mulheres", pct(d["p_mulheres"])],
        ["Proporção com superior, homens", pct(d["p_homens"])],
        ["Diferença (mulheres menos homens)", pp(d["diferenca"])],
        [f"IC {pct(nivel, 0)} ({d['ic']['metodo']})", f"{pp(d['ic']['inferior'])} a {pp(d['ic']['superior'])}"],
        ["Estatística z", fnum(d["z"], 2)],
        ["Valor-p", fp(d["valor_p"])],
      ])
      tabela_condicoes(d["condicoes"])


def grafico_ic(qs, dados, titulo_x, chave, mult):
  fig = go.Figure()
  pos = {k: i + 1 for i, k in enumerate(qs)}
  est = [dados[k]["estimativa"] * mult for k in qs]
  fig.add_trace(go.Scatter(
    x=est, y=[pos[k] for k in qs], mode="markers", name="Estimativa e IC",
    marker={"color": "#2a6fbb", "size": 9},
    error_x={
      "type": "data", "symmetric": False,
      "array": [(dados[k]["ic"]["superior"] - dados[k]["estimativa"]) * mult for k in qs],
      "arrayminus": [(dados[k]["estimativa"] - dados[k]["ic"]["inferior"]) * mult for k in qs],
    },
  ))
  for i, k in enumerate(qs):
    fig.add_trace(go.Scatter(
      x=[dados[k]["referencia"] * mult] * 2, y=[pos[k] - 0.3, pos[k] + 0.3], mode="lines", name="Constante de referência",
      line={"color": "#d1495b", "dash": "dash"}, legendgroup="ref", showlegend=i == 0,
    ))
  fig.add_trace(go.Scatter(
    x=[dados[k]["valor_populacional"] * mult for k in qs], y=[pos[k] for k in qs], mode="markers", name="Valor populacional",
    marker={"symbol": "diamond", "color": "#222222", "size": 11},
  ))
  eixos(fig, titulo_x, "Questão")
  fig.update_yaxes(tickvals=list(pos.values()), ticktext=[k.upper() for k in qs], range=[0.4, len(qs) + 0.6], rangemode="normal")
  grafico(fig, chave)


def histograma_dominio(amo, qk, log, bins, chave):
  m = amo["ok"] & amo["mulher"]
  if qk == "qp4":
    m &= amo["s"]
  y = amo["y"][m]
  h, ar = np.histogram(np.log10(y) if log else y, bins=bins)
  barras_hist(
    [("Amostra", h.tolist(), COR["amo"])], tuple(ar), log,
    "Rendimento mensal (R$, escala log)" if log else "Rendimento mensal (R$)", "Número de pessoas", chave,
  )


def tabela_global(inf):
  linhas = []
  for k in QPS:
    q = inf["questoes"][k]
    f = fmt_tipo(q)
    linhas.append([
      QP_NOME[k], f["est"](q["estimativa"]), f"{f['lim'](q['ic']['inferior'])} a {f['lim'](q['ic']['superior'])}",
      f["est"](q["referencia"]), fp(q["valor_p"]), q["veredito_amostral"], VEREDITO[q["veredito_exato"]],
    ])
  h = inf["hipotese"]
  linhas.append(["Hipótese (as quatro afirmações)", "", "", "", "", h["veredito_amostral"], h["veredito_exato"]])
  tabela(pd.DataFrame(linhas, columns=["Questão", "Estimativa", "IC 95%", "Valor dos homens", "Valor-p", "Resultado na amostra", "Resultado na população (arquivo)"]))


def nota_controle(ilu):
  mx = ilu["maior_proporcao_lado_esperado"]
  st.info(
    f"Nas {fnum(ilu['R'], 0)} amostras simuladas, o maior erro de decisão unilateral foi {pct(mx['valor'])} "
    f"({mx['questao'].upper()}), acima do nominal de {pct((1 - ilu['nivel_confianca']) / 2)}."
  )


def ilustracao(ilu, inf, qs):
  st.write(
    f"As {fnum(ilu['R'], 0)} amostras de tamanho {fnum(ilu['n'], 0)} abaixo foram sorteadas da população (arquivo) só para ilustrar. "
    "Nenhum veredito usa estes números. A inferência oficial é a da amostra única."
  )
  nominal_ic, nominal_lado = ilu["nivel_confianca"], (1 - ilu["nivel_confianca"]) / 2
  for k in qs:
    q = ilu["questoes"][k]
    prop = q["metodo_ic"] == "Wilson"
    mult = 100 if prop else 1
    f = pct if prop else (lambda x, d=1: rs(x))
    x_tit = "Estimativa da proporção (%)" if prop else "Rendimento médio estimado (R$)"
    xx_tit = "Proporção (%)" if prop else "Rendimento médio (R$)"
    st.subheader(QP_NOME[k])
    reps = [r for r in q["replicacoes"] if r["estimativa"] is not None]
    est = np.array([r["estimativa"] for r in reps]) * mult
    h, ar = np.histogram(est, bins=BINS_ILUSTRACAO)
    centros = (ar[:-1] + ar[1:]) / 2
    ymax = float(h.max())
    fig = go.Figure(go.Bar(x=centros, y=h, width=np.diff(ar), name="Estimativas das amostras ilustrativas", marker_color=COR["pop"], opacity=0.7))
    fig.add_trace(go.Scatter(x=[q["valor_populacional"] * mult] * 2, y=[0, ymax], mode="lines", name="Valor populacional", line={"color": "#d1495b", "dash": "dash"}))
    fig.add_trace(go.Scatter(
      x=[inf["questoes"][k]["estimativa"] * mult], y=[0], mode="markers", name="Estimativa da AAS oficial",
      marker={"symbol": "diamond", "size": 12, "color": "#222222"}, cliponaxis=False,
    ))
    fig.update_layout(bargap=0)
    eixos(fig, x_tit, "Número de amostras")
    grafico(fig, f"ilu_hist_{k}")
    primeiras = [r for r in q["replicacoes"][:100] if r["estimativa"] is not None]
    fig = go.Figure()
    for ind, rotulo in [("cobre", "IC cobre o valor populacional"), ("inteiro_abaixo", "IC inteiro abaixo do valor populacional"), ("inteiro_acima", "IC inteiro acima do valor populacional")]:
      sel = [r for r in primeiras if r[ind]]
      fig.add_trace(go.Scatter(
        x=[r["estimativa"] * mult for r in sel], y=[r["r"] for r in sel], mode="markers", name=rotulo,
        marker={"color": COR_ILU[ind], "size": 5},
        error_x={
          "type": "data", "symmetric": False,
          "array": [(r["superior"] - r["estimativa"]) * mult for r in sel],
          "arrayminus": [(r["estimativa"] - r["inferior"]) * mult for r in sel],
          "color": COR_ILU[ind], "thickness": 1.2,
        },
      ))
    fig.add_trace(go.Scatter(x=[q["valor_populacional"] * mult] * 2, y=[0, 101], mode="lines", name="Valor populacional", line={"color": "#222222", "dash": "dash"}))
    eixos(fig, xx_tit, "Amostra ilustrativa (número)")
    fig.update_yaxes(range=[101, 0], rangemode="normal")
    grafico(fig, f"ilu_ic_{k}")
    se = q["erro_padrao_mc"]
    est_r = q["estimativas_resumo"]
    nd = q["n_dominio"]
    linhas = [
      ["Amostras válidas", fnum(q["R_validas"], 0), "", ""],
      ["Tamanho do domínio: média, mínimo e máximo", f"{fnum(nd['media'], 1)}, {fnum(nd['minimo'], 0)} e {fnum(nd['maximo'], 0)}", "", ""],
      ["Média das estimativas", f(est_r["media"], 1) if prop else rs(est_r["media"]), "", ""],
      ["Desvio-padrão das estimativas", fnum(est_r["desvio_padrao"] * 100, 2) + " p.p." if prop else rs(est_r["desvio_padrao"]), "", ""],
    ]
    for rot, kk, se_k, nom in [
      ("Cobertura do IC (proporção que cobre o valor populacional)", "proporcao_cobre", "cobre", nominal_ic),
      ("IC inteiro abaixo do valor populacional", "proporcao_inteiro_abaixo", "inteiro_abaixo", nominal_lado),
      ("IC inteiro acima do valor populacional", "proporcao_inteiro_acima", "inteiro_acima", nominal_lado),
      (f"IC inteiro do lado esperado ({'abaixo' if q['lado_esperado'] == 'menor' else 'acima'})", "proporcao_lado_esperado", "lado_esperado", nominal_lado),
    ]:
      linhas.append([rot, pct(q[kk]), fnum(se[se_k] * 100, 2) + " p.p.", pct(nom)])
    tabela(pd.DataFrame(linhas, columns=["Medida", "Valor observado", "Erro padrão de Monte Carlo", "Valor nominal"]))


def aba_inferencia():
  inf, ilu = ler_json("inf"), ler_json("ilu")
  ler_texto("interpretacao.md")
  st.header("Resultados da amostra única")
  st.caption(f"Amostra de {fnum(inf['n'], 0)} pessoas sorteadas de {fnum(inf['N'], 0)}, α = {fnum(inf['alfa'], 2)}, confiança {pct(inf['nivel_confianca'], 0)}. Os filtros da barra lateral não atuam neste painel.")
  tabela_global(inf)
  nota_controle(ilu)
  sel = st.radio("Questão", ["QP1", "QP2", "QP3", "QP4", "Todas"], index=0, horizontal=True, key="sel_qp")
  qs = QPS if sel == "Todas" else [sel.lower()]
  for k in qs:
    st.subheader(QP_NOME[k])
    bloco_qp(inf["questoes"][k], inf["alfa"], inf["nivel_confianca"])
  props = [k for k in qs if k in ("qp1", "qp2")]
  meds = [k for k in qs if k in ("qp3", "qp4")]
  st.header("Estimativa, intervalo de confiança, referência e valor populacional")
  if props:
    grafico_ic(props, inf["questoes"], "Proporção (%)", "ic_prop", 100)
  if meds:
    grafico_ic(meds, inf["questoes"], "Rendimento médio (R$)", "ic_med", 1)
  if meds:
    st.header("Condição de normalidade aproximada: histograma do rendimento no domínio da amostra")
    log = st.toggle("Escala log10 no eixo do rendimento (visão descritiva)", key="t3_log")
    bins = st.slider("Número de faixas do histograma", 10, 100, 30, key="t3_bins")
    amo = carregar("amo")
    for k in meds:
      st.markdown(f"**{QP_NOME[k]}**")
      histograma_dominio(amo, k, log, bins, f"t3_hist_{k}")
  with st.expander("Ilustração da variabilidade amostral (não é a inferência oficial)", expanded=False):
    ilustracao(ilu, inf, qs)


def main():
  st.set_page_config(page_title="Censo 2022: mulheres, escolaridade e rendimento", layout="wide")
  st.title("Escolaridade superior e rendimento de mulheres e homens ocupados")
  st.subheader(
    "Hipótese: entre pessoas ocupadas com 25 anos ou mais, as mulheres têm mais ensino superior completo que os homens "
    "e, mesmo assim, ganham menos pelo trabalho, na média geral e entre quem tem superior."
  )
  st.caption("Fonte: Censo 2022, IBGE, microdados de pessoas. As conclusões valem para o arquivo, não para o Brasil.")
  st.sidebar.header("Filtros dos painéis 1 e 2")
  sex_sel = st.sidebar.multiselect("Sexo", SEXOS, default=SEXOS, key="f_sexo")
  niv_sel = st.sidebar.multiselect("Nível de escolaridade superior", NIVEIS, default=NIVEIS, key="f_nivel")
  st.sidebar.caption("Os filtros valem para os painéis 1 e 2. O painel 3 mostra resultados fixos de outputs/results e não pode ser recalculado para um subconjunto.")
  sexos = tuple(sorted(int(s == "mulher") for s in sex_sel))
  niveis = tuple(sorted(NIVEIS.index(n) for n in niv_sel))
  vazio = not (sexos and niveis)
  t1, t2, t3 = st.tabs(["Painel 1: população", "Painel 2: amostra", "Painel 3: inferência e comparação"])
  with t1:
    ler_texto("base.md")
    if vazio:
      st.warning("Selecione ao menos um valor em cada filtro.")
    else:
      painel("pop", "t1", sexos, niveis)
  with t2:
    ler_texto("amostragem.md")
    if vazio:
      st.warning("Selecione ao menos um valor em cada filtro.")
    elif painel("amo", "t2", sexos, niveis) is not None:
      comparar(sexos, niveis)
  with t3:
    aba_inferencia()


main()
