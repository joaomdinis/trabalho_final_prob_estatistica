# Requirements

Source: docs/enunciado.txt (verbatim). This file holds the decisions already taken. If the two differ, stop and ask João.

## Goal
Test one hypothesis with the Census 2022 public microdata, using one simple random sample (SRS, "AAS"), three interactive dashboards and a video of at most 5 minutes. The dashboards are the three tabs of one Streamlit app, app/app.py. The population is the file itself after the filter below. Population parameters come from the full frame. Inference uses only the sample.
Everything runs locally: no git, no hosting, no cloud (João, 2026-11-12). The delivery of links, video and base is handled by João and is out of scope here.

## Hypothesis (a statement)
Among employed people aged 25 or older in the Brazil file, women have a higher proportion with complete higher education than men and, even so, earn less from work, both on average and among those with complete higher education.

## Data
- Source: IBGE, Census 2022, public microdata of the sample questionnaire, persons register, all of Brazil, no login. Zip of all UFs (about 1 GB): https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Microdados_e_Areas_de_Ponderacao/Microdados_de_acesso_Publico/csv/Todas_as_UFs.zip. The same folder has one zip per UF. João chose all of Brazil on 2026-11-12. The script accepts one persons csv or one per UF inside the zip, and the structure of Todas_as_UFs.zip was not inspected before step 1. Documentation in the same FTP tree under Documentacao/: dictionary ("Layout e dicionário/Dicionário de Variáveis - Microdados CD2022.pdf"), public layout and methodological notes.
- Reconciliation reference: IBGE, Censo 2022, population by age and sex (second tally, 27/10/2023). Brazil totals: 203,080,756 residents, 104,548,325 women, 98,532,431 men. Sum of weights is expected to match the total, and by sex to differ slightly because of records with ignored sex.
- Population: employed persons aged 25 or older, no upper bound. Sampling unit: the person (one record). Frame: the file filtered to that population. The draw is made from the frame.
- The file is not self-weighting. The IBGE weight (P0110) is not used in the inference. Texts and video say that the conclusions refer to the file as the population, not to the Brazilian population. Weighted and unweighted proportions differ, and the data report shows by how much.
- Variables: P0150 sex (1 male, 2 female, 9 ignored). P0180 age in 5-year groups (no age in years, 25 or older is groups 6 to 17, `80+` on top). P0110 weight. P0760 education level (7 = complete higher). P0770 2010-compatible version (cross-check). P0700 highest course attended (12 graduação, 13 especialização, 14 mestrado, 15 doutorado, 99 ignored, blank for current students and for people who never attended). P0740 course concluded. P0950 employed (defines the frame). P0960 employed, 10 or older (cross-check). P1070 earnings type (1 money, products or goods, 2 other form). P1080 usual gross monthly earnings from all jobs, filled only when the type is 1. The public file has no weekly hours and no occupation.
- Education level for description: 0 sem superior completo, 1 graduação, 2 especialização, 3 mestrado, 4 doutorado. It is qualitative ordinal: describe it by frequency and by sex, never average it. Grouping happens only at display time. There is no post-doctorate in the Census.
- Earnings in R$ as published. The log scale is only a descriptive view. Valid earnings: type 1 and value above 0.

## Pipeline
`uv run src/preparar_dados.py` downloads the zip (or uses `--zip`, or the zip already in data/raw), checks it, extracts the persons csv, maps the columns, validates, derives the variables and writes data/processed/populacao.parquet, outputs/validacao/relatorio_dados.md and .json. Any erro stops it with exit code 1 and no parquet. `uv run tests/testar_preparar_dados.py` runs it on synthetic data with known truth (56 checks).
Defaults: complete higher education with P0700 blank or 99 counts as graduação and is flagged `pos_indeterminado`. Instruction codes 8, 9 and 901 to 914 count as no complete higher education and are flagged `instrucao_indeterminada`. Frame columns: id_pop, sexo, sexo_rotulo, mulher, faixa_idade, superior_completo, nivel_sup, nivel_sup_rotulo, pos_indeterminado, instrucao_indeterminada, situacao_rendimento, rendimento, peso.
There is no reference run for Brazil. The previous run, on the RS file only, is discarded. Step 1 produces the reference numbers, and the auditor recomputes them from the raw csv.

## Research questions (one parameter against a constant computed on the full frame)
M = women, H = men, S = complete higher education. Tests are two-sided at 5%. CIs have 95%.

| QP | Domain in the sample | Parameter | H0 | H1 (expected direction) | Reference from the full frame |
|---|---|---|---|---|---|
| 1 | employed women | proportion with S | p_M = p_H | p_M ≠ p_H (expected p_M > p_H) | p_H: proportion with S among employed men |
| 2 | women with S and valid earnings | proportion with earnings strictly above m_H | p = p0 | p ≠ p0 (expected p < p0) | m_H: median earnings of men with S. p0: proportion of men with S strictly above m_H (0.5 only if there are no ties) |
| 3 | employed women with valid earnings | mean earnings (R$) | mu_M = mu_H | mu_M ≠ mu_H (expected mu_M < mu_H) | mu_H: mean among employed men with valid earnings |
| 4 | women with S and valid earnings | mean earnings (R$) | mu_MS = mu_HS | mu_MS ≠ mu_HS (expected mu_MS < mu_HS) | mu_HS: mean among men with S and valid earnings |

QP1 and QP2 are the two hypotheses on a proportion and QP3 and QP4 the two on a mean that the assignment asks for. QP1 is also run as a two-proportion test (women against men, both from the sample).

## Procedure
- CI: Wilson for proportions, which is the inversion of the z test that uses the standard error under H0, so CI and test never disagree. For means, the t interval with a bootstrap interval alongside.
- Tests: one-sample z test for proportions (standard error under H0) and one-sample t test for means.
- Conditions: n·p0 ≥ 10 and n·(1 − p0) ≥ 10 with the realized domain size, which is random in an SRS. For means, a histogram and the bootstrap next to the t interval. Report the realized domain sizes.
- Exact verdict (frame): each question holds or not in the full frame. The hypothesis is sustained if the four hold and negated if any fails.
- Sample verdict: per question, supports (CI entirely on the expected side of the reference), inconclusive (CI contains the reference) or contradicts (CI entirely on the other side). The hypothesis is sustained if the four support, negated if any contradicts, inconclusive otherwise. Sustained requires the four rejections (intersection-union test: global level at most 5%, no correction).
- Comparison per question: population value of the domain, point estimate, CI, reference, test statistic, p-value and both verdicts.
- Negated and inconclusive outcomes are valid. Never tune the analysis toward the hypothesis.

## Sample
- SRS without replacement from the frame, equal probabilities, n = 1,068 (95% confidence, 3% margin of error, p = 0.5, conservative because it maximizes the variance). With n = z²p(1 − p)/e², the margins 5%, 4%, 3%, 2.5% and 2% give 385, 601, 1,068, 1,537 and 2,401. N is in the millions, so the finite population correction is negligible.
- Power at step 3: for those five n, with the real parameters, two-sided 5%, normal approximation and expected domain sizes. Proportions use the one-sample formulas with the real p_M, p_H and p0. Means use d = |mu_H − mu_M| / sigma_M, with sigma_M the standard deviation of the domain in the frame. The joint floor is 1 − the sum of (1 − power) over the four questions (Bonferroni bound). If it is below 0.80 at n = 1,068, propose margin 2.5% (n = 1,537). João approves the final n before the draw.
- João confirms n in the USP/Bauru sample size calculator named in the assignment (docs/enunciado.txt names it without a link) and keeps a screenshot. The writer leaves a `[PREENCHER: ...]` marker for it in app/textos/amostragem.md.
- One draw only. The seed is fixed in the spec. The manifest records the seed, n, N, library versions and hashes. Rerunning reproduces the same sample.

## App (one app.py with 3 tabs)
- Streamlit, versions pinned in requirements.txt. Run: `uv run --with-requirements requirements.txt streamlit run app/app.py`.
- Tab 1 describes the population. Tab 2 describes the sample with the differences from the population. Tab 3 has the four questions with every item the assignment asks (variable or event, H0 and H1, CI, test, alpha, statistic, p-value, conclusion, population against sample), the comparison, the limitations and the effect of sampling variability.
- Interactive: filters by sex, education level and age group. Every chart has both axes with scale and title.
- The app reads data/processed/populacao.parquet (tab 1), outputs/amostra/amostra.parquet (tab 2), outputs/results/*.json and app/textos/*.md directly. Descriptive statistics under a filter are computed in the app. It computes no CI, test statistic or p-value, imports no scipy and makes no network call.
- Texts shown: app/textos/base.md (tab 1), amostragem.md (tab 2) and interpretacao.md (tab 3). They are the documentation the assignment asks for. No docx or pdf is planned.

## Texts and video
Brazilian Portuguese. The writer produces the three texts and docs/roteiro_video.md. Video of at most 5 minutes with five topics: base and population, sample size and SRS, descriptive tabs, hypotheses with CIs and tests, interpretation and comparison. It prioritizes statistical interpretation. João records it.

## Grading criteria (from the assignment text)
| Criterion | Weight |
|---|---|
| Base choice, description and context | 10% |
| Sample size and SRS | 10% |
| Panel 1 | 10% |
| Panel 2 | 10% |
| Confidence intervals and tests | 20% |
| Interpretation and comparison | 20% |
| Video | 20% |

## Decisions for the architect to list for João at step 2
Each with options and trade-offs. None is decided.
1. Wald interval next to Wilson, in case the course taught only Wald.
2. A sampling-variability illustration in tab 3 with many other samples, labeled as an illustration. The official inference stays the single SRS.
3. Weighted indicators in tab 1, yes or no. Weighted and unweighted proportions differ among men and women.
4. Age view in tab 1: proportion with S and mean earnings by sex and 5-year age group. It shows whether the education gap changes sign among the oldest and whether the earnings gap depends on age. Cost: one more chart and more to explain in the video.
5. Complete higher education with unknown level: records with complete higher education and P0700 blank or 99, probably current students (unconfirmed). Step 1 gives the count. By default they count as graduação and carry `pos_indeterminado`. Options: (a) keep and disclose the count, (b) show them as a fifth category, (c) leave them out of the level views only and keep them in the S indicator. The four questions use S and are unaffected.

## Out of scope
Other bases or UFs, a second sample for inference, model fitting, tests beyond those above, the weight in the inference, hosting and delivery of links.
