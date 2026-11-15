# Spec: statistical design

Step 2. Written 2026-11-12, before any draw. Revised the same day in correction cycle 1 after auditoria/passo_2_spec.md (defects S1 to S7), and again in the closing cycle after the cycle 2 audit (defects S8 to S12) and João's decisions at the step 2 gate (12.1), and finally in closing edits for S13, S14 and the step 1 re-audit points D4, D5, D6 and the blank-earnings-type aviso (12.1), still before any draw. Last edited in the pre-draw edits of João's step 3 gate decisions (final n = 1,537, C1 to C5, S16, 12.1). From then on the spec is frozen for the draw and its sha256 goes into the manifest (sha256_spec, section 6). Sources: docs/enunciado.txt (verbatim assignment, source of truth), docs/requirements.md (decisions taken), outputs/validacao/relatorio_dados.md and .json (step 1 data report), auditoria/passo_1_dados.md (step 1 audit).

Counts quoted here come from the step 1 data report or the step 1 audit. No population parameter (proportion, mean, median, standard deviation) is typed in this spec. They are computed by code at step 3 and live in outputs/results/populacao.json. Nothing in this spec is a source for numbers in texts, app or video, except the fixed design constants (seeds, n, alpha, confidence level, B, R). Figures from auditoria/ quoted here are design rationale only and are never cited by texts.

Notation. U = frame. M = women, H = men. S = complete higher education. V = valid earnings. Domain names concatenate: MSV = women with S and valid earnings. N_d = size of domain d in the frame, n_d = realized size of domain d in the sample. y = monthly earnings in R$. Phi = standard normal cdf. z = Phi^-1(0.975) = 1.959963984540054 (full double precision everywhere, never 1.96).

## 1. Hypothesis and research questions

Hypothesis (statement). Among employed people aged 25 or older in the Census 2022 public sample microdata file for Brazil, women have a higher proportion with complete higher education than men and, even so, earn less from work, both on average and among those with complete higher education.

The hypothesis is the conjunction of four directional claims. Each research question (QP) tests one claim. One parameter of a women's domain is compared with a constant computed on the full frame for the corresponding men's domain (justification: the assignment asks to compare sample inference with directly computed population values, and a one-sample test against a known frame constant is exactly that comparison).

| QP | Claim | Parameter (women's domain) | Reference constant (men's domain, full frame) | Confirms the claim | Denies the claim |
|---|---|---|---|---|---|
| 1 | Women have a higher proportion with S | p_M, proportion with S among employed women | p_H, proportion with S among employed men | p_M > p_H | p_M <= p_H |
| 2 | Women with S earn less (position in the distribution) | pi_M, proportion of women in MSV with earnings strictly above m_H | p0, proportion of men in HSV with earnings strictly above m_H, where m_H is the median earnings in HSV | pi_M < p0 | pi_M >= p0 |
| 3 | Women earn less on average | mu_M, mean earnings in MV | mu_H, mean earnings in HV | mu_M < mu_H | mu_M >= mu_H |
| 4 | Women with S earn less on average | mu_MS, mean earnings in MSV | mu_HS, mean earnings in HSV | mu_MS < mu_HS | mu_MS >= mu_HS |

How each QP confirms or denies the hypothesis: the hypothesis is sustained only if all four claims hold (exact layer) or all four are supported by the sample (inferential layer). Any single denied claim negates it. Section 7 gives the rules.

QP1 and QP2 are the two hypotheses on a proportion and QP3 and QP4 the two on a mean (assignment section 4, items a and b, "pelo menos duas hipóteses" each). QP2 is the proportion version of the earnings claim among people with S: if women with S earned like men with S, the share of them above the men's median would equal p0. Justification for p0 instead of 0.5: earnings are heaped at round values, so the share of men strictly above their own median is below 0.5 when there are ties at m_H. Using 0.5 would build a bias into the test.

## 2. Population, frame, sampling unit, variables and derivations

### 2.1 Population and frame
- Source file: IBGE, Censo Demográfico 2022, public microdata of the sample questionnaire, persons register, 27 UF csv files inside Todas_as_UFs.zip (relatorio_dados.json: fonte.url_esperada, fonte.sha256_zip). The file has 21,538,508 records and 169 columns (fonte.registros_no_arquivo, fonte.colunas_no_cabecalho).
- Population of interest: persons in that file with sex informed (P0150 in {1, 2}), aged 25 or older (P0180 in 06 to 17) and employed in the reference week (P0950 = 1). Justification: the hypothesis is about the employed adult population, and 25 is the usual age by which higher education can have been completed.
- The population is the file, not the Brazilian population. The file is itself a probability sample of the Census with unequal weights (P0110). The weight is not used in any inference (justification: the assignment frames the base as the population and asks for an SRS from it, and requirements.md fixes this).
- Frame: the population as listed in data/processed/populacao.parquet, one row per person. N = 7,642,045 (relatorio_dados.json: funil[3].registros). Order: id_pop ascending, which is file order (UF 11 to 53, then row order inside each csv) after the filters.
- Sampling unit: the person (one record). Elementary unit and sampling unit coincide.
- Funnel (relatorio_dados.json funil): 21,538,508 in the file, 21,519,292 with sex informed, 13,940,709 aged 25 or older, 7,642,045 employed. The 19,216 records with sex 9 also have age 99 and none is aged 25 or older (audit 6.1), so the sex filter removes nobody from the age window.

### 2.2 Variables of the frame (data/processed/populacao.parquet)
Thirteen columns, in this order. Types are logical types.

| Column | Type | Source | Exact derivation |
|---|---|---|---|
| id_pop | UInt32 | none | 1 to N in file order after the filters, unique. UInt32 is the type the pipeline writes since step 1 and holds 1 to N exactly (decision D6 (b), 12.1) |
| sexo | int8 | P0150 | value of P0150 (1 or 2) |
| sexo_rotulo | string | P0150 | "homem" if 1, "mulher" if 2 |
| mulher | bool | P0150 | P0150 = 2 |
| faixa_idade | string, ordered | P0180 | code k in 06 to 16 maps to the 5-year group from 5(k-1) to 5(k-1)+4 years (06 = 25 a 29, 16 = 75 a 79), 17 maps to 80+. Labels as stored in the parquet, ordered by code |
| superior_completo | bool | P0760 | P0760 = 7. No nulls |
| nivel_sup | int8 | P0760, P0700, P0740 | rule in 2.3 |
| nivel_sup_rotulo | string | nivel_sup | 0 "sem superior completo", 1 "graduação", 2 "especialização", 3 "mestrado", 4 "doutorado" |
| pos_indeterminado | bool | P0760, P0700 | P0760 = 7 and P0700 blank or 99 |
| instrucao_indeterminada | bool | P0760 | P0760 in {8, 9, 901 to 914}. Treated as not S. Zero records in the public file (P0760 takes only 1 to 7, audit 3.4) |
| situacao_rendimento | string | P1070, P1080, P0990 | rule in 2.4 |
| rendimento | float64, R$ | P1080 | P1080 when situacao_rendimento = "valido", else null |
| peso | float64 | P0110 | P0110 as published. Descriptive use only, never in inference |

Quantitative variable for the mean parameters: rendimento (usual gross monthly earnings from all jobs, R$ nominal, Census reference period July 2022, as published, no deflation, no trimming, no top-coding by us). Justification for no trimming: trimming changes the parameter being estimated, and the frame mean is the defined target.
Qualitative variables: sexo (nominal), superior_completo (binary), nivel_sup (ordinal, described by frequencies only, never averaged), faixa_idade (ordinal), situacao_rendimento (nominal).
Age exists only in 5-year groups. There is no age in years, so there is no mean age.

### 2.3 Education level rule (decision D2, João, 2026-11-12, option (a))
nivel_sup is assigned in this order:
1. 0 if superior_completo is false.
2. 4 if P0700 = 15 and P0740 = 1.
3. 3 if P0700 = 14 and P0740 = 1.
4. 2 if P0700 = 13 and P0740 = 1.
5. 1 otherwise. This includes P0700 = 12, P0700 in {13, 14, 15} with P0740 different from 1 (2 = not concluded, 9 = ignored, or blank), and P0700 blank or 99 (pos_indeterminado).

Meaning: the highest postgraduate level concluded, with graduação as the floor for everyone with S. This diverges from the wording of docs/requirements.md (levels from P0700 alone) by João's decision at the step 1 gate. Effect (audit 4.3): 20,396 records with P0700 in 13 to 15 and P0740 = 2 are level 1. Justification: a label "mestrado" should mean a concluded master's degree. The four QPs use superior_completo only and are unaffected. Current counts per sex and level: relatorio_dados.json resumo.sexo_x_nivel, which already follows this rule.

### 2.4 Earnings situation rule (defect D3 target, to be fixed by the coder after step 2)
Form of the D3 fix: new label "nao_remunerado" (decision O12 (a), João, 2026-11-12).
situacao_rendimento, evaluated per frame record in this order:
1. "valido": P1070 = 1 and P1080 > 0.
2. "zero": P1070 = 1 and P1080 = 0 or blank. Zero records (audit 3.5).
3. "outra_forma": P1070 = 2 (earnings only in a form other than money, products or goods).
4. "nao_remunerado": P1070 blank and P0990 = 9 (unpaid worker helping a household member or relative). Display label in the app and texts: "não remunerado (ajuda a morador ou parente)". These people have no earnings by definition. It is not missing information.
5. "sem_informacao": any other case (P1070 blank and P0990 different from 9). Expected count 0.

Target counts: nao_remunerado = 63,297 (19,943 men, 43,354 women), sem_informacao = 0, and valido, outra_forma, zero unchanged from relatorio_dados.json resumo.sexo_x_situacao_rendimento (audit 6.3: all 63,297 blank-type employed records have P0990 = 9, and all P0990 = 9 records have blank type). The pipeline reads P0990 for this derivation only and does not store it. The frame keeps its 13 columns. The data report adds two checks: count of P1070 blank with P0990 different from 9 (expected 0, level ok if 0, aviso otherwise) and count of P0990 = 9 with P1070 not blank (expected 0). Valid earnings, and so QP2, QP3 and QP4, are unchanged.
The older data-report aviso "ocupados da janela com tipo de rendimento em branco" stays an aviso (decision of 2026-11-12, option (a), 12.1). Its count is expected: it is exactly the nao_remunerado records (P1070 blank and P0990 = 9), and the check "P1070 blank and P0990 different from 9" already covers the case that would be a problem. It is not a data problem, and the step 7 texts must not present it as one (criterion 61).

### 2.5 Check P0950 against P0960 (defect D1 target)
The check compares the event "employed" (P0950 = 1 against P0960 = 1) inside the age window, not the raw values with blanks. Expected divergences: 0 (audit 4.4). Blank P0950 with P0960 = 0 is not a divergence.

### 2.6 Sequence before step 3
The coder fixes D1 and D3 together, reruns `uv run tests/testar_preparar_dados.py` (with synthetic cases for nao_remunerado and the event comparison) and `uv run src/preparar_dados.py` once, and the auditor re-audits. The rerun must leave id_pop and every column except situacao_rendimento identical to the parquet audited at step 1. data/processed/populacao.parquet is frozen from then on: its sha256 is recorded in populacao.json (step 3) and in the manifest (step 4), and it must not change afterwards.

## 3. Parameters

All computed by code at step 3 on the full frame, unweighted, and written to outputs/results/populacao.json (keys in section 9). Domains (all subsets of U):
- M: mulher true. H: mulher false.
- MS, HS: the above with superior_completo true.
- MV, HV: the above with situacao_rendimento = "valido" (equivalently rendimento not null).
- MSV, HSV: S and valid.

Definitions. Means are arithmetic means. The median is the Hyndman-Fan type 7 quantile at 0.5 (for an even count, the average of the two middle order statistics). All quantiles use type 7. Population standard deviation uses divisor N_d (ddof 0), because the frame is the whole population.

| Symbol | Formula | Domain | Role |
|---|---|---|---|
| p_M | (1/N_M) sum over M of 1(S_i) | M | QP1 parameter |
| p_H | (1/N_H) sum over H of 1(S_i) | H | QP1 reference constant |
| m_H | type 7 median of y over HSV | HSV | defines the QP2 event |
| p0 | (1/N_HSV) sum over HSV of 1(y_i > m_H) | HSV | QP2 reference constant |
| pi_M | (1/N_MSV) sum over MSV of 1(y_i > m_H) | MSV | QP2 parameter |
| mu_M | (1/N_MV) sum over MV of y_i | MV | QP3 parameter |
| mu_H | (1/N_HV) sum over HV of y_i | HV | QP3 reference constant |
| mu_MS | (1/N_MSV) sum over MSV of y_i | MSV | QP4 parameter |
| mu_HS | (1/N_HSV) sum over HSV of y_i | HSV | QP4 reference constant |
| sigma_d | sqrt((1/N_d) sum over d of (y_i - mu_d)^2) | MV, HV, MSV, HSV | power at step 3, descriptive |

Also recorded: empates_em_m_H = number of HSV records with y = m_H, and whether the two middle order statistics of HSV differ. The strict inequality in the QP2 event is fixed (justification: requirements.md, and it makes p0 well defined under ties).

Reference constants are treated as known in the tests, which is legitimate only because the frame is known. This is disclosed (section 13).

## 4. Tests

Common to all questions:
- alpha = 0.05, two-sided. Confidence level 95%. Justification: requirements.md.
- Sampling model: the sample is an SRS without replacement of size n from U. Conditional on the realized n_d, the sample units in domain d are an SRS without replacement of size n_d from domain d (property of SRS). All inference is conditional on n_d, which is reported.
- Finite population correction: not applied. Sampling fraction f = n/N is below 0.0004 for every candidate n (n at most 2,401, N = 7,642,045), so the factor sqrt(1 - f) differs from 1 by less than 0.0002. Omitting it makes intervals very slightly conservative. f is reported in inferencia.json.
- Decision rule: reject H0 if and only if p-value < 0.05. Intervals are closed. For every test below the CI is the inversion of the same test with the same critical value, so "reference outside the CI", "|statistic| > critical value" and "p-value < 0.05" are the same event. The code asserts this equivalence for each QP.
- Data for inference: outputs/amostra/amostra.parquet only, plus the reference constants from outputs/results/populacao.json. The column peso is never read by the inference code.

### 4.1 QP1, proportion with S among employed women
- Variable and event: superior_completo, event superior_completo = true, in domain M of the sample.
- H0: p_M = p_H (p_H is the frame constant). H1: p_M ≠ p_H. Expected direction p_M > p_H.
- Estimate: p_hat = x/n_M, x = number of sampled women with S.
- Statistic: one-sample score z with the standard error under H0: z = (p_hat - p_H) / sqrt(p_H (1 - p_H) / n_M). Null distribution: approximately N(0, 1). p-value = 2 (1 - Phi(|z|)).
- CI: Wilson score at 95%: center = (p_hat + z^2/(2 n_M)) / (1 + z^2/n_M), half-width = (z / (1 + z^2/n_M)) sqrt(p_hat (1 - p_hat)/n_M + z^2/(4 n_M^2)). It is the set of p0 with |p_hat - p0| <= z sqrt(p0 (1 - p0)/n_M), so it never disagrees with the z test.
- Conditions and how: (i) SRS by design, verified at step 4. (ii) n_M p_H >= 10 and n_M (1 - p_H) >= 10 with the realized n_M, computed and reported. (iii) superior_completo has no nulls in the domain, checked.
- Supplementary, not in any verdict: two-proportion z test, women against men, both from the sample (requirements.md). Conditional on n_M and n_H, the two subsamples are independent SRSs of their domains. Statistic z2 = (p_hat_M - p_hat_H) / sqrt(p_bar (1 - p_bar)(1/n_M + 1/n_H)), p_bar = (x_M + x_H)/(n_M + n_H), N(0, 1) under H0: p_M = p_H. CI for p_M - p_H: Newcombe hybrid score (method 10), from the two Wilson intervals (l_M, u_M) and (l_H, u_H): lower = d - sqrt((p_hat_M - l_M)^2 + (u_H - p_hat_H)^2), upper = d + sqrt((u_M - p_hat_M)^2 + (p_hat_H - l_H)^2), d = p_hat_M - p_hat_H. This method was fixed by decision O6 (a) (João, 2026-11-12). Condition: successes and failures at least 10 in each group.
- Reported: n_M, x, p_hat, Wilson CI, half-width, p_H, z, standard error under H0, p-value, decision, sample verdict, frame value p_M, p_hat - p_M, whether the CI contains p_M, the condition values, and the supplementary block.

### 4.2 QP2, proportion above the men's median among women with S
- Variable and event: rendimento in domain MSV of the sample, event rendimento > m_H (m_H from populacao.json).
- H0: pi_M = p0. H1: pi_M ≠ p0. Expected direction pi_M < p0.
- Estimate, statistic, null distribution, CI, p-value: as in 4.1 with n_MSV, x = number above m_H, and p0 in place of p_H.
- Conditions: n_MSV p0 >= 10 and n_MSV (1 - p0) >= 10, realized n_MSV, reported. rendimento non-null in the domain, checked.
- Reported: as in 4.1 plus m_H, p0 and empates_em_m_H.

### 4.3 QP3, mean earnings of employed women
- Variable: rendimento (R$) in domain MV of the sample.
- H0: mu_M = mu_H (frame constant). H1: mu_M ≠ mu_H. Expected direction mu_M < mu_H.
- Estimate: ybar. s = sample standard deviation with divisor n_MV - 1. SE = s / sqrt(n_MV).
- Statistic: t = (ybar - mu_H) / SE. Null distribution: Student t with n_MV - 1 degrees of freedom (approximate, relies on the central limit theorem because earnings are not normal). p-value = 2 (1 - F_t(|t|; n_MV - 1)).
- CI: ybar ± t_crit SE, t_crit = F_t^-1(0.975; n_MV - 1).
- Bootstrap alongside, BCa at 95%, B = 10,000, generator numpy.random.Generator(numpy.random.PCG64(2026111203)). Algorithm: x = the domain values ordered by id_pop ascending. idx = rng.integers(0, n_d, size=(B, n_d)). theta_b = mean of x[idx[b]]. z0 = Phi^-1((#{theta_b < ybar} + 0.5 #{theta_b = ybar}) / B). Jackknife means theta_(i) = mean of x without unit i, theta_dot = their average, a = sum (theta_dot - theta_(i))^3 / (6 (sum (theta_dot - theta_(i))^2)^1.5). For q in {0.025, 0.975}: alpha_q = Phi(z0 + (z0 + Phi^-1(q)) / (1 - a (z0 + Phi^-1(q)))). Interval = type 7 quantiles of theta_b at alpha_0.025 and alpha_0.975. Justification for BCa over percentile: earnings are right-skewed and BCa corrects bias and skewness to second order. The bootstrap verdict category (same rule as section 7 applied to the BCa interval) is reported.
- Conditions and how: (i) SRS by design. (ii) finite variance, assumed (earnings are bounded in practice). (iii) approximate normality of ybar: histogram of the domain in tab 3 (app computes it from the sample), adjusted sample skewness G1 = (sqrt(n(n-1))/(n-2)) m3 / m2^1.5 with central moments m_k = (1/n) sum (y - ybar)^k, and Cochran's rule n_MV > 25 G1^2 evaluated with the sample G1 (status ok or aviso). Meaning of the status: "ok" says only that the sample-based rule is met. It does not show that the premise holds. With a heavy right tail the sample G1 grossly underestimates the domain skewness, because a sample of a few hundred rarely contains the extreme values that drive it. The step 2 audit measured this on the frame (design rationale only, auditoria/passo_2_spec.md check 4.12 and auditoria/passo_2_spec_cobertura.json): at the expected n_d for n = 1,068 the rule came out "ok" in about 29.8% (MV) and 14.8% (MSV) of simulated samples, although with the frame skewness it fails by about three orders of magnitude. An "aviso" is evidence against the premise, an "ok" is not evidence for it. interpretacao.md shows the status with this caveat stated in words, without a frame skewness figure (no output carries one), and points to the empirical evidence of section 4.6, whose t-interval miss rates in outputs/results/ilustracao.json show directly how far the t approximation is from nominal (limitation 13.15). The app shows the status of the rule as fixed in 9.4 (changed after the draw, section 11, Deviation 2). (iv) agreement between the t and BCa verdict categories (ok or aviso). An aviso is shown as such, never as a pass. What governs when a condition fails: section 4.5 (decision O7 (a)). Size of the directional t decision under this skewness: section 7.2 (decision O10 (a), t governs and the excess is disclosed).
- Reported: n_MV, ybar, s, SE, mu_H, t, df, p-value, t CI, half-width, BCa CI with B and seed, bootstrap verdict, decision, sample verdict, frame value mu_M, ybar - mu_M, whether the t CI contains mu_M, G1, 25 G1^2, condition statuses.

### 4.4 QP4, mean earnings of women with S
As 4.3 in domain MSV, reference mu_HS, bootstrap seed 2026111204. Expected direction mu_MS < mu_HS.

### 4.5 Rule when a condition fails (decision O7 (a), João, 2026-11-12, consistent with O10 (a))
The verdict uses the prefixed method (Wilson for QP1 and QP2, t for QP3 and QP4), whatever the conditions show. A failed condition is reported as aviso next to the result and disclosed in interpretacao.md. For QP3 and QP4 the BCa interval and its verdict category stay reported alongside and never change the verdict. For a proportion with n_d p0 < 10 or n_d (1 - p0) < 10, the exact two-sided binomial test (p-value = sum of binomial probabilities not larger than that of the observed count) and the Clopper-Pearson interval are reported alongside. Justification: the rules are fixed before the draw and are not changed after seeing the data.

### 4.6 Sampling-variability illustration (decision O2 (b), João, 2026-11-12, never in any verdict)
Purpose: show with evidence from outputs how estimates and 95% CIs vary across SRSs of the same design, and how often each CI method covers the frame value. It is labeled as an illustration wherever it appears. The official inference is the single SRS of section 6. Justification: requirements.md (tab 3 illustration, "the official inference stays the single SRS") and the enunciado item "efeito da variabilidade amostral".
- Script and time: src/inferencia.py, at step 5, in the same run that writes inferencia.json, with its own generator object. Output: outputs/results/ilustracao.json (keys in 9.6). It must be code writing to outputs/ because the app computes no CI. It runs after the draw but reads only the frame and populacao.json, and it cannot change any rule: the verdict rules are fixed in section 7 and the inference reads nothing from it.
- Source of the draws: data/processed/populacao.parquet as frozen in 2.6, sorted by id_pop ascending, position i = 0 to N - 1 corresponding to id_pop = i + 1. Never amostra.parquet.
- Design of each illustrative sample: SRS without replacement of size n (the n approved at step 3, 1,537, 12.1) from the whole frame, the same design as the official sample, so domain sizes n_d vary across samples as they do in the real draw.
- R = 1,000 illustrative samples. Justification: the size offered in O2. The Monte Carlo standard error of a share p is sqrt(p (1 - p) / 1,000), about 0.0069 at p = 0.95 and about 0.0049 at p = 0.025, enough to show a gap of a few percentage points from nominal but not to resolve small differences, which is disclosed.
- Generator and seed: rng = numpy.random.Generator(numpy.random.PCG64(2026111209)), used only for the illustration. Justification: fixed now, before any draw and without looking at data, and distinct from the draw seed 20261112, from the bootstrap seeds 2026111203 and 2026111204, and from the seeds 2026111205 to 2026111208 of the removed section 5.5, so no stream is shared or confused.
- Algorithm: for r = 1 to R, in this order, pos_r = rng.choice(N, size=n, replace=False, shuffle=False), with no other call to rng. The positions of sample r are pos_r sorted ascending, and the sample is the frame rows at those positions. Justification for Generator.choice instead of the random keys of section 6: random keys would need 1,000 vectors of 7,642,045 uniforms and 1,000 full sorts, while choice without replacement is an exact SRS at a small cost. Exact reproduction needs the same NumPy version, recorded in the file, and sha256_posicoes lets the auditor confirm it.
- Per sample r and QP k: the domain subsample as defined in section 3 (M for QP1, MSV for QP2, MV for QP3, MSV for QP4), its realized n_d, the estimate and the 95% CI with exactly the governing method of section 4 for that QP (Wilson for QP1 and QP2 with full-precision z and the event of 4.1 or 4.2, t with t_crit = F_t^-1(0.975; n_d - 1) for QP3 and QP4), and three indicators against the frame value theta_k (populacao.json questoes.qpk.valor_populacional): cobre (inferior <= theta_k <= superior), inteiro_abaixo (superior < theta_k), inteiro_acima (inferior > theta_k). No BCa, no test statistic and no verdict category per sample (justification: not part of what O2 offered). If n_d = 0 for a proportion or n_d < 2 for a mean, the CI is null, the sample is excluded from that QP's shares and the count is reported (expected 0).
- Summaries per QP over the R_validas valid samples: mean, standard deviation (ddof 1) and type 7 quantiles 0.025, 0.5 and 0.975 of the estimates; mean, minimum and maximum of n_d; shares proporcao_cobre, proporcao_inteiro_abaixo and proporcao_inteiro_acima (they add up to 1), each with Monte Carlo standard error sqrt(p (1 - p) / R_validas); proporcao_lado_esperado, the share of CIs entirely on the expected side of the frame value (inteiro_acima for QP1, inteiro_abaixo for QP2, QP3 and QP4), with its standard error. Global: maior_proporcao_lado_esperado and the QP where it occurs. Justification for the split of non-coverage by side and for the global key: the O10 (a) disclosure needs the direction and the bound from outputs, and the writer reads json only and must not compute.
- Reading of the shares, fixed now. proporcao_cobre is the empirical coverage of the method at this design and n (nominal 0.95). proporcao_lado_esperado is the empirical rate at which the CI lies entirely on the expected side of the true value (nominal 0.025). For QP3 and QP4, under the location-shift assumption of 7.2, it equals the size of the directional "supports" decision, because the t interval is location equivariant. For QP1 and QP2 there is no location shift of a proportion and the coverage of the Wilson interval changes with p, so the rate measured at the true p_M or pi_M only approximates the size at the boundary p = p_H or p = p0. maior_proporcao_lado_esperado then approximates the bound on the size of "sustained" (7.2). These are the figures the texts use to disclose the O10 (a) excess error (7.2, 13.11, criterion 53). They are Monte Carlo estimates with the stated standard error and depend on that assumption, and the texts say so.
- The illustration never feeds any verdict, condition status or decision. The verdict code does not read ilustracao.json.

## 5. Sample size and power

### 5.1 Formula
n = ceil(z^2 p (1 - p) / e^2) with z = Phi^-1(0.975) in full precision, p = 0.5 and e the margin of error. Justification for p = 0.5: it maximizes p(1 - p), so it is conservative for any proportion. Justification for full-precision z: with z = 1.96 the 2% margin gives exactly 2401.0 in real arithmetic and floating-point error can push the ceiling to 2402.

| e | n |
|---|---|
| 5% | 385 |
| 4% | 601 |
| 3% | 1,068 |
| 2.5% | 1,537 |
| 2% | 2,401 |

Default: n = 1,068 (95%, 3%, p = 0.5, requirements.md). Approved at step 3 by the rule of 5.4: n = 1,537 (95%, 2.5%, p = 0.5, 12.1). No finite population correction (section 4). With the correction n0 / (1 + (n0 - 1)/N) the 3% row would give 1,067, and the other rows are unchanged. The margin e refers to a proportion estimated on the whole sample. Domain estimates use n_d < n and have wider margins, reported as realized half-widths.

### 5.2 Calculator confirmation (João, step 3)
João enters in the USP/Bauru calculator named in docs/enunciado.txt: confidence 95%, margin 3% (or the margin he approves), proportion 50%. If the calculator asks for a population size, he enters N from populacao.json. He keeps a screenshot. Expected result 1,068, or 1,067 if the calculator applies the finite population correction or rounds instead of taking the ceiling. Either confirms the computation, the difference being explained in amostragem.md. For the approved margin 2.5% the expected result is 1,537 (real value 1,536.58), or 1,536 if the calculator applies the finite population correction (about 1,536.27) and rounds to the nearest integer. João confirmed n = 1,537 in the calculator at step 3 and kept the screenshot (12.1). n stays as approved at step 3. The writer leaves `[PREENCHER: captura da calculadora USP/Bauru]` in app/textos/amostragem.md.

### 5.3 Power (step 3, `planejar`, draws nothing)
For each n in the table and each QP, with the real frame parameters from populacao.json:
- Expected domain size n_d = n N_d / N (N_d from populacao.json dominios). Assumption: n_d concentrates around its mean (binomial coefficient of variation sqrt((1 - N_d/N)/(n N_d/N))), so plugging the expectation is a first-order approximation, disclosed in planejamento.md.
- Proportions (QP1 with p = p_M and reference p_H, QP2 with p = pi_M and reference p0), one-sample score test with SE under H0: s0 = sqrt(p0 (1 - p0)/n_d), s1 = sqrt(p (1 - p)/n_d), power = Phi((p0 - z s0 - p)/s1) + 1 - Phi((p0 + z s0 - p)/s1).
- Means (QP3 with d = |mu_H - mu_M| / sigma_MV, QP4 with d = |mu_HS - mu_MS| / sigma_MSV), normal approximation as in requirements.md: power = Phi(d sqrt(n_d) - z) + Phi(-d sqrt(n_d) - z). It ignores the t correction and the non-normality of earnings and is slightly optimistic for small n_d, disclosed.
- Joint floor F(n) = 1 - sum over the four QPs of (1 - power_k) (Bonferroni bound on the probability that all four tests reject). It is a lower bound because the four tests share one sample.
- Power is two-sided and measures the ability to detect the true frame difference whatever its direction. It does not depend on whether the hypothesis holds.

planejamento.md contains one table with columns: margem, n, then for each QP n_d esperado, efeito (p - p0 or d) and poder, then piso_conjunto. It also states the rule outcome and the recommended n. If it reports empates_em_m_H and meio_difere (section 3), they are information, not checks: meio_difere = false is the normal case when there are ties at m_H and is never marked WARN (decision C3 (a), 12.1).

### 5.4 Rule for choosing n
1. If F(1,068) >= 0.80, recommend n = 1,068.
2. Otherwise recommend n = 1,537 (margin 2.5%) if F(1,537) >= 0.80.
3. If F(1,537) < 0.80, report F for all five n and stop for João (open decision O9). No automatic increase.
João approves the final n at the step 3 gate. Outcome at step 3: F(1,068) < 0.80 and F(1,537) >= 0.80, so rule 2 applied, O9 was not triggered, and João approved n = 1,537 (values in outputs/validacao/planejamento.md, 12.1). Choosing n from real parameters is legitimate planning: the tests and verdict rules are fixed here before the draw, and a larger n only adds precision.

### 5.5 Removed by João's decision 2026-11-12
The proposed error-rate simulation inside `planejar` (frame skewness, simulated t and BCa rates, seeds 2026111205 to 2026111208, populacao.json keys assimetria_dominio, cochran_n_minimo_quadro and tamanho_simulado) was rejected in full. `planejar` computes only 5.1 to 5.4, draws nothing and calls no random generator. The number is kept so that references stay stable.

## 6. SRS procedure

- Design: simple random sampling without replacement, equal inclusion probability n/N for every frame record, every subset of size n equally likely.
- Frame: data/processed/populacao.parquet as frozen in 2.6, sorted by id_pop ascending. The code asserts id_pop is exactly 1 to N, unique.
- Generator: numpy.random.Generator(numpy.random.PCG64(seed)).
- Seed: 20261112. Justification: it is the date this spec was written, it was fixed before any draw and without looking at any data, and a date makes it evident that it was not searched among candidates. Any fixed integer gives a valid SRS.
- n: 1,537 (95%, margin 2.5%, p = 0.5), approved by João at step 3 (12.1). sortear computes n from the margin with the formula of 5.1.
- Command for the single draw: `uv run src/amostragem.py sortear --margem 0.025`.
- `--margem` is mandatory in sortear and has no default (decision C1 (a), 12.1). Justification: a default margin could silently produce a sample of a size João did not approve, and a draw cannot be redone.

Algorithm (random keys), `uv run src/amostragem.py sortear --margem 0.025`:
1. If outputs/amostra/manifest.json exists, exit with a non-zero code without writing anything. If `--margem` is absent, exit with a non-zero code without writing anything.
2. Read the frame and sort by id_pop ascending. Let position i = 0 to N - 1 correspond to id_pop = i + 1.
3. rng = numpy.random.Generator(numpy.random.PCG64(20261112)). u = rng.random(N), float64 in [0, 1), u[i] is the key of position i. No other call to rng precedes it.
4. order = numpy.argsort(u, kind="stable"). The selected positions are order[0:n] (the n smallest keys, ties broken by smaller id_pop).
5. Selected ids = positions + 1, sorted ascending.
6. amostra.parquet = the frame rows with those ids, all 13 columns unchanged, ordered by id_pop.
Why equal probability: the keys are i.i.d. continuous uniform, so their ranking is a uniformly random permutation and the first n positions form a uniformly random n-subset. Ties have probability of order N^2 / 2^54 and only matter at the cut, where the id_pop tie-break is fixed in advance. Why this algorithm rather than Generator.choice: it is fully specified here, so anyone can reproduce it with any language that implements PCG64, and it does not depend on the internal algorithm of choice. NumPy does not guarantee bit-stream stability across versions, so the manifest records the NumPy version and the hash of the id list.

Manifest outputs/amostra/manifest.json, keys:
- semente (20261112), n, N, fracao_amostral (n/N), probabilidade_inclusao (n/N)
- desenho ("AAS sem reposição"), algoritmo (text of steps 3 to 5), gerador ("numpy.random.PCG64")
- nivel_confianca (0.95), margem_erro (the value passed in `--margem`, 0.025), p_planejamento (0.5)
- versoes: python and every third-party library that src/amostragem.py actually imports and uses, each with its installed version (numpy always, since the draw depends on it). A library the script does not import is not listed (decision C2 (a), 12.1)
- sha256_populacao_parquet, sha256_amostra_parquet, sha256_ids (sha256 of the ascending ids written as decimal strings joined by "\n", UTF-8, no trailing newline), sha256_spec (docs/spec.md at the time of the draw)
- comando (the actual command line used, as received by the process, including `--margem` and its value, never a fixed text, decision C1 (a), 12.1), gerado_em (ISO 8601 UTC)
outputs/validacao/sorteio.md: n, N, seed, uniqueness, membership, row equality with the frame, the manifest hashes, and the sample composition by sex next to the frame (descriptive only).

One draw only. Never redraw. A rerun after the manifest exists is refused.

## 7. Verdict rules

### 7.1 Exact layer (frame, no inference)
Each QP holds if and only if the strict inequality of its claim holds in the frame: p_M > p_H, pi_M < p0, mu_M < mu_H, mu_MS < mu_HS. The hypothesis is sustained ("sustentada") if all four hold and negated ("negada") if any fails. Written in populacao.json at step 3.

### 7.2 Inferential layer (sample)
Per QP, with the 95% CI of section 4 (Wilson for QP1 and QP2, t for QP3 and QP4) and the reference constant r:
- supports ("apoia"): the CI lies entirely on the expected side of r (upper < r when the expected direction is "<", lower > r when it is ">"). Equivalent to rejecting H0 with the estimate on the expected side.
- inconclusive ("inconclusivo"): r is inside the closed CI. Equivalent to not rejecting H0.
- contradicts ("contradiz"): the CI lies entirely on the other side of r.
Hypothesis: sustained ("sustentada") if the four support, negated ("negada") if any contradicts, inconclusive ("inconclusiva") otherwise.

Intersection-union logic. The hypothesis is the intersection of four directional claims, so its negation (the global null) is the union of the four directional nulls H0k: theta_k on the non-expected side of r_k or equal to it. "Sustained" requires rejecting every H0k ("supports" in all four). Let alpha_k be the actual size of the directional rejection k, that is the supremum over H0k of the probability that QP k is "supports". By the intersection-union theorem the size of the "sustained" rule is at most max_k alpha_k, with no multiplicity correction and no independence assumption. The supremum is approached when one claim sits at its boundary (theta_k = r_k, where the claim is false by the strict inequality of 7.1) and the other three are far on their expected side, so that they support with probability near 1.

What alpha_k is. The nominal value is 0.025 (one side of a two-sided 5% test). The actual value is not guaranteed to be 0.025:
- QP1 and QP2 (score z test, Wilson CI): alpha_k is approximately 0.025 by the normal approximation for the binomial, at the realized n_d. The illustration of 4.6 gives the empirical rate (proporcao_lado_esperado) at step 5.
- QP3 and QP4 (t test, t CI): alpha_k is NOT close to 0.025 in this frame. The step 2 audit simulated 20,000 SRSs of the expected n_d for n = 1,068 from each women's domain of the frame (n_d = 444 for MV and 127 for MSV) and counted how often the t CI lay entirely below the true domain mean (auditoria/passo_2_spec_cobertura.json, keys ic_t_inteiro_abaixo_de_mu and ic_t_inteiro_acima_de_mu, reported in auditoria/passo_2_spec.md check 4.10). Result: about 7.2% (MV) and 8.4% (MSV) entirely below, against 2.5% nominal, and about 0.59% and 0.37% entirely above. Monte Carlo standard error sqrt(p(1 - p)/20,000), about 0.002 for both. Cause: earnings are extremely right-skewed in the frame (audit check 4.12), and with right skew the t interval misses low far more often than high. The low side is exactly the expected side of QP3 and QP4, so the distortion favors the hypothesis.
- Assumption behind reading these rates as alpha_k: under a boundary null the domain distribution has the frame shape shifted to the reference (location-shift model). Under other shapes alpha_k differs. The figures hold for the expected n_d at n = 1,068 and change with n. The approved n is 1,537 (12.1), so they are not the figures at the approved n: those come from the illustration of 4.6, run at the approved n. A later run with 100,000 replications in the cycle 2 audit gave about 6.9% and 8.3%, consistent with these.

Consequence and decision. With the t interval governing QP3 and QP4, the size of "sustained" is bounded by about max(0.072, 0.084) = 0.084 at n = 1,068 (approximate, Monte Carlo, location-shift assumption), not by 0.05 as docs/requirements.md states ("global level at most 5%"). João decided on 2026-11-12, at the step 2 gate and before any draw or exact verdict existed, to keep the t interval governing QP3 and QP4 and to disclose the excess error and its direction (O10 (a), 12.1). The verdict rule of this section is therefore unchanged. Disclosure: interpretacao.md and the video script state that the error of "sustained" is not controlled at 5%, that its excess favors the hypothesis, and give the figures from outputs/results/ilustracao.json (4.6) against two distinct references that are never mixed. (i) Per question: the expected-side share (questoes.qpk.proporcao_lado_esperado, which for QP3 and QP4 is proporcao_inteiro_abaixo) and, for QP3 and QP4, the opposite-side share proporcao_inteiro_acima, each with its Monte Carlo standard error (erro_padrao_mc), are compared with the nominal one-sided 2.5% per direction of a two-sided 95% CI, because each is the empirical size of the directional decision of one QP, not of the hypothesis. A per-question share is never compared with 5%. (ii) Globally: the size of "sustained" is at most about the largest per-question expected-side share, maior_proporcao_lado_esperado (valor, erro_padrao_mc, questao), and this bound is set against the nominal global 5% that docs/requirements.md claims. Note on the nominal value: with nominal one-sided 2.5% decisions the intersection-union bound would itself be 2.5%, and the 5% of requirements.md is the two-sided alpha. The texts correct the 5% claim of requirements.md and are not required to discuss this note. The location-shift caveat applies to both readings. The audit figures above are design rationale and are never cited by texts, because auditoria/ is not a source of numbers. No text may claim that "sustained" is controlled at 5%. The disclosure is made whatever the verdict. If the sample verdict is "sustentada", the text says explicitly that the bound on its error is about maior_proporcao_lado_esperado and not 5%. Tab 3 carries this disclosure through interpretacao.md, which it renders (9.4, criterion 36), and in addition shows the one-sentence error-control note fixed in 9.4 (changed after the draw, section 11, Deviation 2). The rules of this paragraph for interpretacao.md and the video script are not changed by Deviation 2.

The "negated" conclusion is a union of four directional rejections and is not covered by the intersection-union theorem. "Negated" is an error only when the hypothesis is true, that is when all four claims hold with strict inequality. Its error probability is then P(at least one QP is "contradicts") <= sum_k P(QP k is "contradicts") (Bonferroni). Each term approaches its one-sided nominal value 0.025 as theta_k approaches r_k from the expected side and never reaches it, because at theta_k = r_k claim k is false and "negated" is correct. So the supremum of the error of "negated" is approximately 4 x 0.025 = 0.10, approached in the limit where all four parameters tend to their boundaries together, and not attained. All these values are approximate (normal approximation for QP1 and QP2, t approximation for QP3 and QP4). For QP3 and QP4 the measured "contradicts" side rates (about 0.59% and 0.37%) are below nominal in this frame, so the 0.10 bound is conservative for those two terms. João decided to keep this rule and disclose the bound (O8 (a), 2026-11-12), and section 13 lists it.

### 7.3 Comparison reported per QP
Frame value of the domain parameter, point estimate, CI, half-width, reference constant, statistic, p-value, decision, both verdicts, estimate minus frame value, and whether the CI contains the frame value. The two layers can disagree, and the disagreement is reported as an effect of sampling variability, never corrected.

## 8. Assignment map

Criteria: C1 base (10%), C2 sample size and SRS (10%), C3 panel 1 (10%), C4 panel 2 (10%), C5 CIs and tests (20%), C6 interpretation and comparison (20%), C7 video (20%).

| Enunciado item | Delivered by | Produced by | Checked by | Criterion |
|---|---|---|---|---|
| 1 Objective: sampling, CIs, tests, population against sample, dashboards, video | the app as a whole and the video | coder, writer, João | auditor, João | all |
| 2 Large base from a reliable source | base.md in tab 1 (IBGE Census 2022, 21,538,508 records) | writer | auditor | C1 |
| 2 Quantitative and qualitative variables for mean and proportion | base.md variable table, section 2.2 | writer | auditor | C1 |
| 2 Source and access link | base.md, from relatorio_dados.json fonte.url_esperada | writer | auditor | C1 |
| 2 Context and objective of the base | base.md | writer | auditor | C1 |
| 2 Number of observations and variables | base.md: file (registros_no_arquivo, colunas_no_cabecalho) and frame (N, 13 columns) | writer | auditor | C1 |
| 2 Population of interest and sampling unit | base.md, section 2.1 | writer | auditor | C1 |
| 2 Description of the selected variables | base.md, section 2.2 | writer | auditor | C1 |
| 3 Compute the sample size | planejamento.md, amostragem.md, calculator screenshot | coder (step 3), writer, João | auditor | C2 |
| 3 Report and justify confidence, margin, proportion | amostragem.md, section 5 | writer | auditor | C2 |
| 3 Select the SRS, document it, equal probability | sortear, manifest.json, sorteio.md, amostragem.md, section 6 | coder (step 4), writer | auditor (reproduces the draw) | C2 |
| 4 Three interactive panels | app/app.py, 3 tabs: sidebar filters for tabs 1 and 2, tab 3 elements of O11 (a) + (d) (9.1, 9.4) | coder | auditor, João | C3, C4, C6 |
| 4 P1 descriptive indicators | tab 1 indicator table | coder | auditor | C3 |
| 4 P1 distributions of the selected variables | tab 1 charts | coder | auditor | C3 |
| 4 P1 charts suited to variable types | tab 1 (bars for qualitative, histogram and box plot for earnings) | coder | auditor | C3 |
| 4 P1 frequencies and proportions of qualitative variables | tab 1 frequency tables | coder | auditor | C3 |
| 4 P1 mean, median, standard deviation and others | tab 1 earnings summary | coder | auditor | C3 |
| 4 P2 reproduce the analysis with the sample only | tab 2, same layout, reads amostra.parquet | coder | auditor | C4 |
| 4 P2 identify differences between sample and population | tab 2 comparison table and overlaid distributions, amostragem.md | coder, writer | auditor | C4, C6 |
| 4 P3a qualitative variable and event | tab 3, QP1 and QP2 blocks | coder | auditor | C5 |
| 4 P3a H0 and H1 | tab 3, from inferencia.json | coder | auditor | C5 |
| 4 P3a proportion CI from the sample | Wilson CI, inferencia.json | coder | auditor (second method) | C5 |
| 4 P3a test for the proportion | z test, inferencia.json | coder | auditor | C5 |
| 4 P3a alpha, statistic, p-value, conclusion | tab 3 table | coder | auditor | C5 |
| 4 P3a population proportion against the estimate, interpreted | tab 3 comparison, interpretacao.md | coder, writer | auditor | C6 |
| 4 P3b quantitative variable | tab 3, QP3 and QP4 blocks | coder | auditor | C5 |
| 4 P3b H0 and H1 | tab 3 | coder | auditor | C5 |
| 4 P3b mean CI from the sample | t CI with BCa alongside | coder | auditor (second method) | C5 |
| 4 P3b test for the mean | t test | coder | auditor | C5 |
| 4 P3b alpha, statistic, p-value, conclusion | tab 3 table | coder | auditor | C5 |
| 4 P3b population mean against the estimate, interpreted | tab 3 comparison, interpretacao.md | coder, writer | auditor | C6 |
| 4 Hypotheses relevant to the base, justify the parameters | section 1, interpretacao.md | architect, writer | auditor | C5, C6 |
| 4 Verify the conditions of the procedures | tab 3 conditions table and histograms, inferencia.json condicoes | coder, writer | auditor | C5 |
| 4 Differences between parameters and estimates | tab 3 comparison table | coder | auditor | C6 |
| 4 Point estimates against CIs | tab 3 CI chart (estimate, CI, reference, frame value) | coder | auditor | C6 |
| 4 Conclusions of the tests | tab 3, both verdict layers | coder, writer | auditor, João | C5, C6 |
| 4 Limitations and effect of sampling variability | interpretacao.md, section 13, and the tab 3 sampling-variability illustration (4.6, ilustracao.json, 9.4) | writer, coder (src/inferencia.py, app) | auditor | C6 |
| 4 Parameters computed directly, inference from the sample | populacao.json (frame) and inferencia.json (sample only), sections 3 and 4 | coder | auditor | C5, C6 |
| 5 Video of at most 5 minutes | docs/roteiro_video.md, recording | writer, João | auditor (script), João | C7 |
| 5 Topic: base, origin, population | script topic 1 | writer | auditor | C7 |
| 5 Topic: sample size and SRS | script topic 2 | writer | auditor | C7 |
| 5 Topic: descriptive panels | script topic 3 | writer | auditor | C7 |
| 5 Topic: hypotheses, CIs, tests | script topic 4 | writer | auditor | C7 |
| 5 Topic: interpretation, population against sample | script topic 5 | writer | auditor | C7 |
| 5 Objective, interpretation first | script style (A46) | writer | auditor, João | C7 |
| 6 Link to the panels | out of scope by João's decision | none | none | none |
| 6 YouTube link to the video | out of scope by João's decision | none | none | none |
| 6 Link to the original base with source | out of scope by João's decision (the link also appears in base.md as content of item 2) | none | none | none |
| 6 Links open without authorization, available during grading | out of scope by João's decision | none | none | none |
| 7 Criteria C1 to C7 | rows above, acceptance criteria in section 10 | all | auditor | C1 to C7 |

## 9. App

One file app/app.py, one Streamlit app, `st.tabs` with three tabs: "Painel 1: população", "Painel 2: amostra", "Painel 3: inferência e comparação". Run: `uv run --with-requirements requirements.txt streamlit run app/app.py`.

### 9.1 Filters
Sidebar, shared by tabs 1 and 2: sexo (multiselect: mulher, homem), nivel_sup_rotulo (multiselect, 5 levels in order), faixa_idade (multiselect, groups in order). Default: all selected. With an empty selection the tabs show a notice instead of charts. Justification for shared filters: tab 2 must compare sample and population under the same subset. The sidebar filters do not act on tab 3: its numbers come from inferencia.json and cannot be recomputed in the app for a subset. The sidebar says so. Enunciado line 44 asks for three interactive panels, so tab 3 has its own interactive elements, fixed by decision O11 (a) + (d) (João, 2026-11-12): a selector of the question shown (radio "Questão" with QP1 to QP4 and "Todas", default "QP1", changed after the draw, section 11, Deviation 2) and, on the condition histograms of QP3 and QP4, a log10 x-scale toggle and a bin-count slider (10 to 100, default 30), both computed in the app from amostra.parquet as descriptive views. The question selector also selects which QP the illustration charts of 9.4 show.

### 9.2 Tab 1 (population, data/processed/populacao.parquet)
- Indicators: N filtered, share of women, proportion with S overall and by sex, count of valid earnings, mean, median, standard deviation (ddof 0) of earnings overall and by sex.
- Frequency and proportion tables: sexo, superior_completo by sex, nivel_sup by sex, faixa_idade, situacao_rendimento by sex. pos_indeterminado count shown as a note under the level table (decision O5 (a), João, 2026-11-12: counted as graduação and disclosed).
- Charts: bar chart of nivel_sup by sex (x "Nível de escolaridade superior", y "Proporção (%)"), bar chart of faixa_idade by sex (x "Faixa de idade", y "Número de pessoas"), bar chart of proportion with S by sex (x "Sexo", y "Proporção com superior completo (%)"), histogram of valid earnings by sex (x "Rendimento mensal (R$)", y "Número de pessoas"), with an optional log10 x scale toggle labeled as a descriptive view (x "Rendimento mensal (R$, escala log)"), box plot of valid earnings by sex and by S (x "Grupo", y "Rendimento mensal (R$)").
- Earnings summary table by sex and by S: n, mean, median, standard deviation, Q1, Q3, P10, P90, minimum, maximum, coefficient of variation. Quantiles type 7.
- Text: app/textos/base.md.

### 9.3 Tab 2 (sample, outputs/amostra/amostra.parquet)
- The same indicators, tables and charts as tab 1 computed on the sample (standard deviation with ddof 1, justification: sample estimator).
- Comparison table under the current filter: indicator, population, sample, difference (sample minus population), for share of women, proportion with S overall and by sex, mean and median earnings overall and by sex.
- Overlaid relative-frequency charts population against sample for nivel_sup and faixa_idade (y "Proporção (%)"), and overlaid earnings densities or relative histograms (y "Proporção de pessoas (%)").
- Note on screen: under narrow filters the sample counts are small and differences are noisy, and no test is run on filtered subsets.
- Text: app/textos/amostragem.md.

### 9.4 Tab 3 (inference, outputs/results/inferencia.json and populacao.json)
- For each QP a block: variable and event or variable, domain, H0, H1, expected direction, alpha, n_d, estimate, CI (method, bounds, half-width), statistic (name, value, df for t), p-value, decision, sample verdict, frame value, reference constant, estimate minus frame value, CI contains frame value, exact verdict, conditions with status ok or aviso (for QP3 and QP4 the caption of the Cochran row states the status of the rule, ok or aviso, and does not contain the phrase "subestima muito a assimetria do domínio", changed after the draw, section 11, Deviation 2. The full caveat of 4.3 iii reaches tab 3 through interpretacao.md). QP1 also shows the two-proportion block. QP3 and QP4 also show the BCa interval and its verdict category.
- CI chart per QP (proportions and means on separate charts): point estimate with the CI as an error bar, a vertical line at the reference constant and a marker at the frame value. x "Proporção (%)" or "Rendimento médio (R$)", y "Questão".
- Histogram of the sample domain earnings for QP3 and QP4 (condition check, computed in the app from amostra.parquet), x "Rendimento mensal (R$)", y "Número de pessoas".
- Interactive elements: O11 (a) + (d) as in 9.1. None of them changes a number from inferencia.json or ilustracao.json, they only select what is shown or how a descriptive histogram is drawn. The global table is always visible whatever the selector.
- Global table: four QPs with both verdicts, and the hypothesis verdict in both layers.
- Error-control note next to the global table (O10 (a), wording changed after the draw, section 11, Deviation 2): exactly one sentence, "Nas {R} amostras simuladas, o maior erro de decisão unilateral foi {valor} ({questão}), acima do nominal de 2,5%.", with {R} = ilustracao.json R, {valor} = ilustracao.json maior_proporcao_lado_esperado.valor as a percentage under 9.5, {questão} = maior_proporcao_lado_esperado.questao shown as "QP1" to "QP4", and "2,5%" = (1 - nivel_confianca) / 2 formatted under 9.5. The note does not mention docs/requirements.md or a global 5%, and compares the per-question share only with the nominal one-sided 2.5% (7.2 (i)). The sentence is true only if valor > (1 - nivel_confianca) / 2, which the auditor checks (criterion 59).
- Sampling-variability illustration (4.6), read from outputs/results/ilustracao.json, below the official results inside a st.expander collapsed by default (expanded=False) whose label is "Ilustração da variabilidade amostral (não é a inferência oficial)" (placement and wording changed after the draw, section 11, Deviation 2), with the sentence "As {R} amostras de tamanho {n} abaixo foram sorteadas da população (arquivo) só para ilustrar. Nenhum veredito usa estes números. A inferência oficial é a da amostra única." ({R} and {n} filled from ilustracao.json, never typed). It follows the question selector (all four QPs stacked when "Todas"). Per QP:
  - Histogram of the R_validas estimates. x "Estimativa da proporção (%)" for QP1 and QP2 or "Rendimento médio estimado (R$)" for QP3 and QP4, y "Número de amostras". A vertical line at the frame value (valor_populacional) and a marker at the official SRS estimate (inferencia.json questoes.qpk.estimativa), both in the legend. Binning is a display choice made in the app (30 bins).
  - CI chart of the illustrative samples 1 to 100 in replication order (fixed in advance, no selection by result): one horizontal segment per sample from inferior to superior with a point at the estimate, colored by cobre, inteiro_abaixo or inteiro_acima, and a vertical line at the frame value. x "Proporção (%)" or "Rendimento médio (R$)", y "Amostra ilustrativa (número)". Justification for 100: 1,000 segments are unreadable, and the shares in the table use all valid samples.
  - Table: R_validas, n_d mean, minimum and maximum, mean and standard deviation of the estimates, proporcao_cobre, proporcao_inteiro_abaixo, proporcao_inteiro_acima and proporcao_lado_esperado, each with its Monte Carlo standard error, next to the nominal values 95%, 2.5% and 2.5%.
  - The app computes nothing inferential for the illustration: every bound, indicator and share comes from ilustracao.json.
- Text: app/textos/interpretacao.md (comparison, limitations, sampling variability).
- The app computes no CI, test statistic or p-value, imports no scipy or statsmodels and makes no network call.

### 9.5 Display conventions (app and texts)
Brazilian number format (decimal comma, dot for thousands). Proportions as percentages with 1 decimal place (CI bounds and differences of proportions with 2 decimal places of percentage points). R$ with 2 decimal places. Statistics z and t with 2 decimal places. p-values with 4 decimal places, and "< 0,0001" when smaller. Counts as integers. The texts use exactly the rounding the app shows.
Exception (decision S16 (b), 12.1): the excluded share (situacao_rendimento_excluida.proporcao) and the share of each non-valid category of situacao_rendimento (outra_forma and nao_remunerado, and zero and sem_informacao if shown) are displayed in percent with 3 decimal places, in texts and app, so that the displayed parts add up to the displayed total. Justification: with 1 decimal the parts shown do not add up to the total shown (step 2 audit, cycle 5 check 5.2.9), and with 3 decimals they do for the frame values of each sex. The share of "valido" keeps the general rule. Under narrow app filters 3 decimals make a rounding mismatch unlikely but do not exclude it.

### 9.6 Files the app reads
| File | Content | Units |
|---|---|---|
| data/processed/populacao.parquet | the 13 columns of 2.2 | rendimento in R$/month, peso unitless |
| outputs/amostra/amostra.parquet | same 13 columns, n rows | same |
| outputs/results/populacao.json | keys below | proportions in [0, 1], R$ |
| outputs/results/inferencia.json | keys below | proportions in [0, 1], R$ |
| outputs/results/ilustracao.json | keys below | proportions and shares in [0, 1], R$ |
| app/textos/base.md, amostragem.md, interpretacao.md | Markdown in Brazilian Portuguese | none |

outputs/results/populacao.json (step 3):
- gerado_em, sha256_populacao_parquet, N
- dominios: M, H, MS, HS, MV, HV, MSV, HSV (counts)
- questoes.qp1 to qp4, each with: parametro, valor_populacional, N_dominio, referencia_nome, referencia, N_referencia, lado_esperado ("maior" or "menor"), veredito_exato ("vale" or "nao_vale"). qp2 adds m_H, empates_em_m_H, meio_difere (bool). qp3 and qp4 add sigma_dominio and sigma_referencia (ddof 0).
- hipotese_veredito_exato ("sustentada" or "negada")
- descritivas: the block D below on the frame, with ddof 0

Block D (descriptives): ddof, metodo_quantis ("tipo 7"), grupos with keys total, mulher, homem, each holding: registros, proporcao_do_total, superior_completo {n, proporcao}, nivel_sup [list of {nivel_sup, rotulo, n, proporcao}], faixa_idade [list of {faixa_idade, n, proporcao}], situacao_rendimento [list of {situacao, n, proporcao}, one entry for each of the five labels of 2.4 in the order valido, zero, outra_forma, nao_remunerado, sem_informacao, with n = 0 when absent, proporcao = n / registros of the same group, that is the share of the employed of that group], situacao_rendimento_excluida {n, proporcao, categorias} (n = sum of the situacao_rendimento counts of the group whose situacao is not "valido", proporcao = n / registros of the same group, categorias = list of the non-valid labels with n > 0 that the sum contains), pos_indeterminado {n, proporcao} (n = records of the group with pos_indeterminado true, proporcao = n / registros of the same group, that is the share of the employed of that group, not of those with S, decision C4 (a), 12.1), rendimento_valido {n, media, mediana, desvio_padrao, q1, q3, p10, p90, minimo, maximo, cv}, rendimento_valido_superior {same keys, domain S and valid}.

outputs/results/inferencia.json (step 5):
- gerado_em, alfa (0.05), nivel_confianca (0.95), z_critico, n, N, fracao_amostral, semente, sha256_amostra_parquet, sha256_populacao_json
- questoes.qp1 to qp4, each with: tipo ("proporcao" or "media"), variavel, evento (proportions), unidade, dominio (label), n_dominio, h0, h1, lado_esperado, estimativa, ic {metodo, inferior, superior, meia_largura}, estatistica {nome, valor, erro_padrao, gl (t only)}, valor_p, rejeita_h0, veredito_amostral, referencia_nome, referencia, valor_populacional, N_dominio, diferenca_estimativa_menos_populacional, ic_contem_valor_populacional, veredito_exato, condicoes (list of {nome, valor, limite, status}).
  - proportions add sucessos. qp2 adds m_H and p0. If a condition fails, exato {valor_p, ic_clopper_pearson}.
  - means add desvio_padrao_amostral, ic_bootstrap {metodo "BCa", B, semente, inferior, superior, veredito}, assimetria_G1, cochran_n_minimo.
  - qp1 adds duas_proporcoes {n_mulheres, n_homens, p_mulheres, p_homens, diferenca, z, valor_p, ic {metodo "Newcombe", inferior, superior}, condicoes}.
- hipotese: veredito_exato, veredito_amostral, regra (text of section 7)
- descritivas_amostra: block D on the sample, with ddof 1
- diferencas_amostra_populacao: list of {indicador, grupo, populacao, amostra, diferenca} for share of women, proportion with S (total, mulher, homem), mean and median valid earnings (total, mulher, homem), mean valid earnings with S (mulher, homem)

outputs/results/ilustracao.json (step 5, section 4.6, illustration only):
- rotulo ("ilustração da variabilidade amostral, não entra em nenhum veredito"), gerado_em, semente (2026111209), gerador ("numpy.random.PCG64"), metodo_sorteio ("Generator.choice sem reposição, shuffle=False, posições do quadro ordenado por id_pop"), R (1000), n, N, nivel_confianca (0.95), versoes {python, numpy}, sha256_populacao_parquet, sha256_populacao_json, sha256_posicoes (sha256 of the R lines, line r = the ascending positions of sample r as decimal strings joined by ",", lines joined by "\n", UTF-8, no trailing newline)
- questoes.qp1 to qp4, each with: parametro, dominio, metodo_ic ("Wilson" or "t"), valor_populacional, lado_esperado ("maior" or "menor"), R_validas, amostras_excluidas, n_dominio {media, minimo, maximo}, estimativas_resumo {media, desvio_padrao, q025, q50, q975}, proporcao_cobre, proporcao_inteiro_abaixo, proporcao_inteiro_acima, proporcao_lado_esperado, erro_padrao_mc {cobre, inteiro_abaixo, inteiro_acima, lado_esperado}, replicacoes (list of R entries in replication order, each {r, n_dominio, estimativa, inferior, superior, cobre, inteiro_abaixo, inteiro_acima}, null bounds for excluded samples)
- maior_proporcao_lado_esperado {valor, erro_padrao_mc, questao}
- Units: estimates, bounds and valor_populacional in [0, 1] for QP1 and QP2 and in R$ per month for QP3 and QP4. Shares and standard errors in [0, 1].

### 9.7 Sources for each text (the writer reads only json and markdown)
| Text | Files and keys for its numbers |
|---|---|
| app/textos/base.md | relatorio_dados.json: fonte.url_esperada, fonte.registros_no_arquivo, fonte.colunas_no_cabecalho, funil[*].registros, mapa_colunas, resumo.pos_indeterminado, resumo.sexo_x_situacao_rendimento (after the D3 rerun), resumo.conferencia_por_sexo (weighted against unweighted). populacao.json: N, dominios.*, descritivas.grupos.*, including descritivas.grupos.mulher and .homem situacao_rendimento (n, proporcao per category) and situacao_rendimento_excluida (n, proporcao, categorias) for the earnings exclusions (13.2, criterion 61). Context and definitions from docs/spec.md sections 1 and 2 |
| app/textos/amostragem.md | outputs/validacao/planejamento.md (n per margin, power, joint floor, recommendation). manifest.json: semente, n, N, fracao_amostral, probabilidade_inclusao, algoritmo, gerador, versoes, sha256_*. outputs/validacao/sorteio.md (checks). inferencia.json: diferencas_amostra_populacao, descritivas_amostra. populacao.json: descritivas. Marker `[PREENCHER: captura da calculadora USP/Bauru]` |
| app/textos/interpretacao.md | inferencia.json: questoes.* (all keys), hipotese.*, n, alfa, nivel_confianca. populacao.json: questoes.*, hipotese_veredito_exato, descritivas.grupos.*.rendimento_valido and rendimento_valido_superior (media, mediana, p90, maximo, to support the right-skew statement of 13.9). ilustracao.json: R, n, semente, questoes.*.proporcao_cobre, proporcao_inteiro_abaixo, proporcao_inteiro_acima, proporcao_lado_esperado, erro_padrao_mc.*, estimativas_resumo.*, n_dominio.*, valor_populacional, and maior_proporcao_lado_esperado.* (sampling variability, limitations 13.10, 13.11, 13.15 and 13.16, the O10 (a) disclosure). relatorio_dados.json: resumo.conferencia_por_sexo, resumo.pos_indeterminado, resumo.sexo_x_situacao_rendimento (limitations). populacao.json descritivas.grupos.mulher and .homem situacao_rendimento (n, proporcao per category) and situacao_rendimento_excluida (n, proporcao, categorias) (earnings exclusions, 13.2, criterion 61). Section 13 of this spec for the list of limitations |
| docs/roteiro_video.md | the union of the three rows above. Five topics in the order of enunciado section 5. The O10 (a) disclosure in topic 4 or 5 uses ilustracao.json maior_proporcao_lado_esperado and questoes.qp3 and qp4 proporcao_inteiro_abaixo |

## 10. Acceptance criteria

Each line is testable by someone who did not write the code. Numerical tolerance, unless stated: counts exact, real numbers relative 1e-9 against an independent reimplementation and 1e-6 against a second library. Criteria 48 to 53 were added in correction cycle 1 of step 2, criteria 54 to 60 in the closing cycle criterion 61 in the closing edits of 2026-11-12, and criteria 62 to 64 in the pre-draw edits of the step 3 gate (2026-11-12). They sit under their step but keep new numbers, so that earlier numbers stay stable. Removed criteria keep their number with the mark "removed".

Before step 3 (D1 and D3 fix)
1. [DATA] The rerun parquet has 7,642,045 rows and the 13 columns of 2.2 in order, and id_pop and every column except situacao_rendimento are identical to the parquet audited at step 1. C1
2. [DATA] situacao_rendimento counts are nao_remunerado 63,297 (19,943 men, 43,354 women), sem_informacao 0, and valido, outra_forma, zero as in the step 1 report (O12 (a)). C1
3. [CODE] The P0950 against P0960 check compares the event value 1 and reports 0 divergences, and the two new P0990 checks report 0. C1
4. [CODE] `uv run tests/testar_preparar_dados.py` passes with synthetic cases covering nao_remunerado and the event comparison. C1

Step 3 (tamanho)
5. [DATA] populacao.json has every key of 9.6, and N and dominios match counts recomputed by the auditor from the parquet. C5
6. [DATA] Every parameter of section 3 matches the auditor's own computation, with m_H as the type 7 median and the strict inequality in p0 and pi_M. C5
7. [DATA] veredito_exato per QP and hipotese_veredito_exato follow 7.1. C6
8. [CODE] `planejar` creates nothing under outputs/amostra, never uses seed 20261112 and calls no random number generator. C2
9. [DATA] planejamento.md lists n = 385, 601, 1,068, 1,537, 2,401 for e = 5%, 4%, 3%, 2.5%, 2%, computed with full-precision z and the ceiling. C2
10. [DATA] Expected n_d, effects, power per QP and margin, and the joint floor match the auditor's computation with the formulas of 5.3, and the recommendation follows 5.4. C2
48. Removed by João's decision 2026-11-12 (section 5.5 rejected).

Step 4 (sorteio)
11. [CODE] `sortear` exits with a non-zero code and changes no file when outputs/amostra/manifest.json exists. C2
12. [DATA] amostra.parquet has n rows, the 13 frame columns, unique id_pop, and every row is identical to the frame row with the same id_pop. C2
13. [DATA] The auditor's own implementation of the section 6 algorithm, with seed 20261112 and the NumPy version in the manifest, reproduces the id list exactly (same sha256_ids). C2
14. [DATA] manifest.json has every key of section 6, with n = 1,537, margem_erro = 0.025, comando equal to the command line actually used (containing `--margem 0.025`), and versoes listing python and exactly the third-party libraries that src/amostragem.py imports, each with its installed version, and its sha256 values match the files, including sha256_spec against docs/spec.md at the time of the draw. C2
15. [CODE] Applied to a toy frame of N = 1,000 and n = 100 with 20,000 different seeds, the selection function gives inclusion counts that a chi-square goodness-of-fit test against the uniform does not reject at 1%. C2
62. [CODE] An automated test in tests/ checks criterion 11: in a temporary directory that holds a manifest.json, sortear exits with a non-zero code and no file in that directory is created, changed or removed. The test runs before the draw, uses only the temporary directory and never reads, creates or writes anything under outputs/amostra/ (decision C5 (a)). C2
63. [CODE] An automated test in tests/ checks that sortear called without `--margem` exits with a non-zero code and writes nothing, run against a temporary directory before the draw and never touching outputs/amostra/ (decision C1 (a)). C2

Step 5 (inferencia)
16. [DATA] inferencia.json has every key of 9.6 for each QP, and n_dominio matches the auditor's counts from the sample. C5
17. [DATA] For QP1 and QP2, estimate, Wilson CI, z, standard error and p-value match the auditor's reimplementation and a second library (for example statsmodels proportion_confint with method "wilson" and a score z with the H0 variance). C5
18. [DATA] For QP3 and QP4, mean, s, t, df, p-value and t CI match the auditor and scipy.stats.ttest_1samp. C5
19. [DATA] The BCa interval is reproduced exactly with the seed and ordering of 4.3, and an independent BCa (for example scipy.stats.bootstrap) differs from it by less than 5% of the t interval width at each bound. C5
20. [DATA] For each QP, rejeita_h0, "reference outside the CI" and "p-value < 0.05" agree, and veredito_amostral follows 7.2. C5
21. [DATA] hipotese.veredito_amostral follows 7.2 and hipotese.veredito_exato equals populacao.json. C6
22. [DATA] Every condition of section 4 is computed with the stated threshold and an unmet one has status aviso, never ok. C5
23. [DATA] valor_populacional and referencia equal populacao.json, and diferenca_estimativa_menos_populacional and ic_contem_valor_populacional are correct. C6
24. [DATA] The QP1 two-proportion block matches the auditor and a second library. C5
25. [DATA] descritivas_amostra and diferencas_amostra_populacao match the auditor's computation on the sample and the frame. C4
26. [CODE] The inference code reads only amostra.parquet and populacao.json and never references the column peso. C5
27. [DATA] sha256 of populacao.parquet equals the value in manifest.json. C2
54. [CODE] The illustration in src/inferencia.py uses its own numpy.random.Generator(numpy.random.PCG64(2026111209)) and the algorithm of 4.6 with R = 1,000 and the approved n (1,537), draws only from data/processed/populacao.parquet, never reads amostra.parquet for it, and never uses the seeds 20261112, 2026111203 or 2026111204. C6
55. [DATA] The auditor's own implementation of 4.6, with the seed and the NumPy version recorded in ilustracao.json, reproduces sha256_posicoes exactly, and for every replication and QP its n_dominio, estimativa, inferior, superior and the three indicators match ilustracao.json (counts exact, reals relative 1e-9). C6
56. [DATA] In ilustracao.json every share equals the count of its indicator over R_validas, the three shares of each QP add up to 1, every erro_padrao_mc equals sqrt(p (1 - p) / R_validas), proporcao_lado_esperado takes the side of 4.6 for each QP, maior_proporcao_lado_esperado is the largest of the four with its QP, and valor_populacional equals populacao.json. C6
57. [CODE] No verdict, decision or condition status in inferencia.json depends on the illustration: the code that writes inferencia.json never reads ilustracao.json or the illustration generator (static check), and the auditor's own recomputation of inferencia.json for criteria 16 to 24, made without any illustration, reproduces it. C5

Step 6 (app)
28. [CODE] app/app.py is a single file with one st.tabs call and exactly three tabs titled as in section 9. C3
29. [CODE] An AppTest of the auditor runs without exception in the default state, for every single-value combination of sexo, nivel_sup_rotulo and faixa_idade, and for an empty selection. C3
30. [CODE] Every chart has a non-empty title on both axes and a visible numeric or categorical scale on both axes. C3
31. [CODE] With no filter, the tab 1 numbers equal populacao.json descritivas and the tab 2 numbers equal inferencia.json descritivas_amostra, with the rounding of 9.5. C3
32. [CODE] For at least 20 filter combinations chosen by the auditor, the tab 1 and tab 2 numbers match the auditor's own computation. C4
33. [CODE] Tab 3 shows every item of 9.4 for each QP, with values equal to inferencia.json under the rounding of 9.5. C5
34. [CODE] Static check: the app imports none of scipy, statsmodels, requests, urllib, httpx, socket, calls no .ppf, .cdf or .sf, and contains no literal 1.96 or 1.959. C5
35. [CODE] The app reads only the files listed in 9.6. C6
36. [CODE] Each text of app/textos is rendered in its tab (base.md in tab 1, amostragem.md in tab 2, interpretacao.md in tab 3). C6
49. [CODE] Tab 1 contains, in the default state, every chart of 9.2 with the planned type: bar charts for nivel_sup by sex, faixa_idade by sex and proportion with S by sex, a histogram of valid earnings by sex with the log10 toggle, and a box plot of valid earnings by sex and by S, each with the axis titles of 9.2. The auditor checks the chart type from the chart specification (mark or trace type), not from the title. C3
50. [CODE] Tab 1 contains every table of 9.2: the indicator table, the frequency and proportion tables for sexo, superior_completo by sex, nivel_sup by sex, faixa_idade and situacao_rendimento by sex (each with a count column and a proportion column), the pos_indeterminado note, and the earnings summary table with the eleven statistics of 9.2. C3
51. [CODE] Tab 2 contains every chart and table of criterion 49 and 50 computed on the sample, plus the comparison table of 9.3 with columns indicador, população, amostra, diferença, the overlaid relative-frequency bar charts for nivel_sup and faixa_idade, the overlaid relative earnings histograms or densities with y "Proporção de pessoas (%)", and the small-sample note. C4
52. [CODE] Tab 3 has the interactive elements fixed by O11, with the radio "Questão" defaulting to "QP1" (9.1), an AppTest that changes each of them runs without exception, and no change alters any number taken from inferencia.json or hides the global table. Edited after the draw (section 11, Deviation 2). C3, C5
58. [CODE] Tab 3 shows the illustration section of 9.4 inside a st.expander collapsed by default whose label is the heading of 9.4, with the sentence of 9.4 (using "população (arquivo)", not "quadro") and the statement that it is not the official inference, for each QP the histogram of estimates and the CI chart of samples 1 to 100 with the axis titles of 9.4, the frame value line and the official estimate marker, and the shares table, with every value equal to ilustracao.json under the rounding of 9.5, and the app computes no bound, indicator or share for it. Edited after the draw (section 11, Deviation 2). C6
59. [CODE] Tab 3 shows next to the global table the error-control note of 9.4 as exactly one sentence equal to "Nas {R} amostras simuladas, o maior erro de decisão unilateral foi {valor} ({questão}), acima do nominal de 2,5%.", with R, maior_proporcao_lado_esperado.valor (rounding of 9.5) and maior_proporcao_lado_esperado.questao equal to ilustracao.json and 2,5% equal to (1 - nivel_confianca) / 2, and the note mentions neither docs/requirements.md nor a global 5%. The auditor also checks in ilustracao.json that valor > (1 - nivel_confianca) / 2, so that "acima" is true, and reports a blocking [SPEC] defect otherwise. Edited after the draw (section 11, Deviation 2). The disclosure rules for the texts (7.2, 13.11, criterion 53) are unchanged. C5, C6

Step 7 (textos)
37. [TEXT] base.md states the source, the access link, the context and objective of the base, the numbers of observations and variables of the file and of the frame, the population, the sampling unit and the description of the selected variables. C1
38. [TEXT] amostragem.md states and justifies confidence, margin and proportion, gives the n formula and result, the power result, the seed, the algorithm, the equal probability argument, the sample-population differences, and contains the calculator marker or João's fill. C2
39. [TEXT] Every number in base.md, amostragem.md and interpretacao.md is found in the sources listed for that text in 9.7, with the rounding of 9.5. C6
40. [TEXT] Every statement about a result or verdict matches inferencia.json and populacao.json. C6
41. [TEXT] interpretacao.md compares, per QP, the frame value with the estimate and the CI, states the test conclusion and both verdicts, and explains the effect of sampling variability. C6
42. [TEXT] The texts say that the conclusions refer to the file as the population and not to the Brazilian population, that the weight is not used in inference, and disclose every limitation of section 13. C6
43. [TEXT] Style: Brazilian Portuguese, no em dash, no semicolon in prose, no praise. C6
44. [TEXT] docs/roteiro_video.md covers the five topics of enunciado section 5 in order, each with a planned duration. C7
45. [TEXT] The spoken text has at most 650 words (about 4 min 40 s at 140 words per minute) and the planned durations add up to at most 5 min. C7
46. [TEXT] For each QP the script states the hypothesis, the CI, the test decision, the comparison with the frame value and one sentence of interpretation, and it states the global verdict in both layers. C7
47. [TEXT] Every number in the script is found in the sources of 9.7, and the script follows the style rules of 43. C7
53. [TEXT] interpretacao.md and the script disclose, as decided in O10 (a), that "sustained" is not controlled at 5%, compare each per-question share from ilustracao.json (qp3 and qp4 proporcao_inteiro_abaixo and proporcao_inteiro_acima, and any proporcao_lado_esperado cited, with Monte Carlo standard errors) with the nominal 2.5% per direction and never with 5%, state that the global size of "sustained" is at most about maior_proporcao_lado_esperado (valor, erro_padrao_mc, questao) against the nominal global 5% claimed by docs/requirements.md (7.2, 13.11), state its direction (toward the hypothesis for QP3 and QP4 under the t interval) and the location-shift caveat, make the disclosure whatever the verdict, and never claim that "sustained" is controlled at 5%. C6
60. [TEXT] interpretacao.md presents the sampling-variability illustration as an illustration drawn from the frame, says that the official inference is the single SRS and that no verdict uses the illustration, and uses its figures (coverage per QP, spread of estimates) to explain the effect of sampling variability. C6
61. [TEXT] base.md and interpretacao.md state that the earnings domains of QP2, QP3 and QP4 and the earnings descriptives exclude the unpaid workers (nao_remunerado, P0990 = 9) and the other non-valid earnings records (outra_forma, and zero and sem_informacao if present), give for women and for men the excluded share of the employed of that sex (populacao.json descritivas.grupos.mulher and .homem situacao_rendimento_excluida) and say explicitly that it is the sum of nao_remunerado and outra_forma (plus any other non-valid category with count above 0), give each of those categories separately by sex both as a count and as a share of the employed of that sex (populacao.json descritivas.grupos.mulher and .homem situacao_rendimento, n and proporcao, counts also citable from relatorio_dados.json resumo.sexo_x_situacao_rendimento), with every figure equal to its key under the rounding of 9.5 (the excluded share and each non-valid category share in percent with 3 decimal places, per the 9.5 exception, so that for each sex the displayed category shares add up to the displayed excluded share) and none typed or computed by the writer, say that QP1 uses all employed, and do not present nao_remunerado or the data-report aviso on blank earnings type as missing data or a data problem (2.4, 13.2). C1, C6
64. [TEXT] Wherever base.md, interpretacao.md or the script cite a pos_indeterminado share, it equals populacao.json descritivas.grupos.*.pos_indeterminado.proporcao under the rounding of 9.5, the text says explicitly that it is a share of the employed of that group, and no text presents it as a share of those with complete higher education (13.6, decision C4 (a)). C1, C6
65. [TEXT] interpretacao.md and docs/roteiro_video.md state that the BCa interval is reported alongside and does not decide the verdict (4.5, O7 (a), O10 (a)), that for QP3 its upper bound lies very close to the reference mu_H, and that the agreement between the t and BCa categories on QP3 is therefore not strong evidence. The only numbers they cite for this caveat are inferencia.json questoes.qp3.ic_bootstrap.superior and mu_H from inferencia.json questoes.qp3.referencia (equal to populacao.json questoes.qp3.referencia), under the rounding of 9.5, shown side by side. They cite no difference between the two, no other number for it and nothing from auditoria/ (13.17). Added after the draw (section 11). C5, C6, C7

## 11. Deviations

The only place where a change after the draw is recorded. Each entry needs João's written approval, the date, what changed, why and its effect on results.

Deviation 1. 2026-11-13.
- When: after the single draw (step 4) and after the step 5 results (outputs/results/inferencia.json, outputs/results/ilustracao.json) and the step 5 audit (auditoria/passo_5_inferencia.md) were known.
- Approval: João, in writing, at the step 5 gate, 2026-11-13.
- What changed: (1) new limitation 13.17 and new criterion 65, the QP3 BCa caveat that the step 7 texts must disclose (interpretacao.md and docs/roteiro_video.md), citing only inferencia.json questoes.qp3.ic_bootstrap.superior and questoes.qp3.referencia (mu_H). (2) Wording of 7.2 (disclosure paragraph), 9.4 (error-control note), 13.11 and criterion 53, to fix the reference of comparison: each per-question share of ilustracao.json is compared with the nominal one-sided 2.5% per direction, and the global size of "sustained" is stated as at most about maior_proporcao_lado_esperado (with its Monte Carlo standard error) against the nominal global 5% claimed by docs/requirements.md. The previous wording left open a comparison of a per-question share with 5%. (3) This entry.
- Why: auditoria/passo_5_inferencia.md observation 2 (the QP3 BCa upper bound is close to mu_H and its category is within bootstrap Monte Carlo error) and observation 1 (the error figure of "sustained" and its reference).
- Effect: none on results. No seed, n, sampling algorithm, test, CI method, condition, threshold or verdict rule changed, and no number in data/ or outputs/ changes. The verdicts in inferencia.json and populacao.json stand. Only what the step 6 app note and the step 7 texts must say changes, and the changes were made with the results known, which is why they are confined to disclosure.
- Hash: sha256_spec in outputs/amostra/manifest.json is the hash of the pre-draw version of this file, the version frozen for the draw (confirmed unchanged at step 5, auditoria/passo_5_inferencia.md check 4). The current file differs from it only because of the edits listed here and this entry. The pre-draw text of each changed passage follows, so that the frozen version can be reconstructed (criterion 65 and limitation 13.17 did not exist, and this section read "(empty)").
  - 7.2, pre-draw: "Disclosure: interpretacao.md, tab 3 and the video script state that the error of "sustained" is not controlled at 5%, that its excess favors the hypothesis, and give its empirical size from outputs/results/ilustracao.json (questoes.qp3 and qp4 proporcao_inteiro_abaixo and proporcao_inteiro_acima, maior_proporcao_lado_esperado, each with its Monte Carlo standard error, 4.6), with the location-shift caveat."
  - 9.4, pre-draw: "- Error-control note next to the global table (O10 (a)): one sentence stating that "sustentada" is not controlled at 5%, that the excess favors the hypothesis, and the value of ilustracao.json maior_proporcao_lado_esperado with its Monte Carlo standard error and the QP where it occurs."
  - 13.11, pre-draw (the two changed sentences): "So "sustained" can be reached by error more often than 5%, the excess favors the hypothesis, and "contradicts" is rarer than nominal for QP3 and QP4. The texts state the empirical size from ilustracao.json (maior_proporcao_lado_esperado and qp3 and qp4 proporcao_inteiro_abaixo and proporcao_inteiro_acima, with Monte Carlo standard errors) and its direction, whatever the verdict, and never say that "sustained" is controlled at 5%."
  - Criterion 53, pre-draw (the changed clause): "give its empirical size from ilustracao.json (maior_proporcao_lado_esperado, and qp3 and qp4 proporcao_inteiro_abaixo and proporcao_inteiro_acima, with Monte Carlo standard errors), state its direction"

Deviation 2. 2026-11-13.
- When: after the single draw (step 4), after the step 5 results and after the step 6 app and its audit (auditoria/passo_6_app.md) were known.
- Approval: João, in writing, at the step 6 gate, 2026-11-13 (as relayed to the architect by the orchestrator).
- What changed, all confined to the app (tab 3) and its criteria: (1) 9.4 error-control note: now exactly one sentence, "Nas {R} amostras simuladas, o maior erro de decisão unilateral foi {valor} ({questão}), acima do nominal de 2,5%.", from ilustracao.json R and maior_proporcao_lado_esperado (valor, questao), with no mention of docs/requirements.md, of a global 5% or of the Monte Carlo standard error, compared only with the nominal one-sided 2.5%. (2) "quadro" replaced by "população (arquivo)" in app labels, which in this spec affects only the illustration sentence of 9.4. JSON values and key names that contain "quadro" (ilustracao.json metodo_sorteio, the removed key cochran_n_minimo_quadro) are outputs or history and are unchanged. (3) The caption of the Cochran row in tab 3 drops the phrase "subestima muito a assimetria do domínio" and keeps the status of the rule (9.4, and the app clause of 4.3 iii). (4) Tab 3 radio "Questão" defaults to "QP1" instead of "Todas" (9.1, criterion 52), and the illustration section sits inside a st.expander collapsed by default, labeled with its heading (9.4, criterion 58). (5) Criterion 59 rewritten for the new note, with an added check that valor > (1 - nivel_confianca) / 2, the premise of the word "acima". (6) The 7.2 disclosure paragraph no longer lists tab 3 among the places that carry the full disclosure, and says that tab 3 carries it through interpretacao.md plus the one-sentence note. The rules for interpretacao.md and the video script in 7.2 (i) and (ii), 13.11, 13.15 and criterion 53 are unchanged. (7) The minor presentation fixes D1 to D6 of auditoria/passo_6_app.md (box plot caption, p.p. units, sign format of R$ differences, unused code, vertical alignment, numpy pin in requirements.txt) need no spec change: the spec does not fix those details. (8) This entry. The 12.1 rows (O10 (a), S14) are a record of decisions as taken and are not edited.
- Why: João's presentation choices at the step 6 gate: a shorter tab 3 note that keeps the per-question comparison with its correct nominal reference (2.5%) and leaves the global discussion to interpretacao.md, plain language in labels ("população (arquivo)" instead of the technical "quadro"), a shorter Cochran caption, and a tab 3 that opens on one question with the illustration collapsed.
- Effect: none on results. No seed, n, sampling algorithm, test, CI method, condition, threshold or verdict rule changed, and no number in data/ or outputs/ changes. The verdicts in inferencia.json and populacao.json stand. Made with the results known, which is why it is confined to presentation. What the app no longer says in the note (not controlled at 5%, direction of the excess, Monte Carlo standard error, location-shift caveat) is still disclosed in interpretacao.md, rendered in tab 3, and in the video script, under rules that are unchanged.
- Hash: sha256_spec in outputs/amostra/manifest.json remains the hash of the pre-draw version (Deviation 1). The current file differs from it by the edits of Deviation 1, of this entry and the entries themselves. The pre-change text of each passage edited here follows. Unless marked, it is also the pre-draw text. For the 9.4 note the pre-draw text is quoted in Deviation 1.
  - 4.3 (iii), pre-draw: "The app and interpretacao.md show the status with this caveat stated in words, without a frame skewness figure (no output carries one), and point to the empirical evidence of section 4.6, whose t-interval miss rates in outputs/results/ilustracao.json show directly how far the t approximation is from nominal (limitation 13.15)."
  - 7.2, pre-change (text of Deviation 1, whose first words are also pre-draw): "Disclosure: interpretacao.md, tab 3 and the video script state that the error of "sustained" is not controlled at 5%, that its excess favors the hypothesis, and give the figures". The paragraph ended at "...the bound on its error is about maior_proporcao_lado_esperado and not 5%." The two sentences after it did not exist.
  - 9.1, pre-draw: "(radio "Questão" with QP1 to QP4 and "Todas", default "Todas")"
  - 9.4 Cochran clause, pre-draw: "(for QP3 and QP4 the Cochran row carries the caveat of 4.3 iii in words: an "ok" is not evidence that the t approximation holds, see the illustration below)"
  - 9.4 note, pre-change (text of Deviation 1): "- Error-control note next to the global table (O10 (a)): one sentence stating that "sustentada" is not controlled at 5%, that the excess favors the hypothesis, and the value of ilustracao.json maior_proporcao_lado_esperado with its Monte Carlo standard error and the QP where it occurs, presented as an approximate upper bound on the global size of "sustentada" set against the global 5% claimed by docs/requirements.md, while the per-question share it comes from is set against the nominal one-sided 2.5% (7.2)."
  - 9.4 illustration, pre-draw: "- Sampling-variability illustration (4.6), read from outputs/results/ilustracao.json, in its own section below the official results, headed "Ilustração da variabilidade amostral (não é a inferência oficial)", with the sentence "As {R} amostras de tamanho {n} abaixo foram sorteadas do quadro só para ilustrar."
  - Criterion 52, pre-draw: "52. [CODE] Tab 3 has the interactive elements fixed by O11, an AppTest that changes each of them runs without exception, and no change alters any number taken from inferencia.json or hides the global table. C3, C5"
  - Criterion 58, pre-draw (the changed clause, and it ended at "for it. C6"): "58. [CODE] Tab 3 shows the illustration section of 9.4 with its heading and the statement that it is not the official inference, for each QP"
  - Criterion 59, pre-draw: "59. [CODE] Tab 3 shows the error-control note of 9.4 next to the global table, with maior_proporcao_lado_esperado, its standard error and its QP equal to ilustracao.json. C5, C6"

## 12. Decisions for João

### 12.1 Decisions already taken (not reopened)
| Date | Decision | Source |
|---|---|---|
| 2026-11-12 | All of Brazil (Todas_as_UFs.zip) | requirements.md |
| 2026-11-12 | Everything local, no git, no hosting, no cloud. Delivery of links, video and base out of scope | requirements.md |
| before step 1 (undated in requirements.md) | Hypothesis, the four QPs, alpha 5% two-sided, 95% CIs, Wilson for proportions, t with bootstrap alongside for means, z and t tests, the two verdict layers and the intersection-union rule (its "global level at most 5%" claim does not hold for QP3 and QP4 under t in this frame, see 7.2 and the O10 (a) row below), n = 1,068 with the five margins, the power rule and the 0.80 floor, frame, variables, defaults for pos_indeterminado and instrucao_indeterminada, one app with three tabs, weight outside the inference | requirements.md |
| 2026-11-12 (step 1 gate) | D2: education level rule (a), postgraduate levels only when concluded (P0740 = 1), else graduação (section 2.3) | João |
| 2026-11-12 (step 1 gate) | D1 and D3 fixed together by the coder right after step 2, with one pipeline rerun and re-audit (sections 2.4 to 2.6). The form of the D3 fix was decided at the step 2 gate (O12 below) | João |
| 2026-11-12 (step 2 gate) | O10 (a): the t interval stays the governing method for QP3 and QP4, and the verdict rule of 7.2 is unchanged. The "global level at most 5%" of requirements.md does not hold for "sustained" (about 8.4% at n = 1,068 per the step 2 audit, with the excess toward the hypothesis). The excess error and its direction are disclosed in interpretacao.md, tab 3 and the video script, with figures from outputs/results/ilustracao.json (4.6, 7.2, 9.4, 13.11, criteria 53 and 59). Options not chosen: (b) BCa governs, (c) larger n, (d) stricter level for "supports", (e) Johnson t, (f) t and BCa co-govern. Taken before any draw and before any exact verdict existed | João |
| 2026-11-12 (step 2 gate) | Section 5.5 (error-rate simulation in `planejar`) rejected in full: its seeds 2026111205 to 2026111208, the populacao.json keys assimetria_dominio, cochran_n_minimo_quadro and tamanho_simulado, the tab 3 frame-skewness field, criterion 48 and the permission for `planejar` to call a random generator are removed (5.5, criterion 8) | João |
| 2026-11-12 (step 2 gate) | O2 (b): sampling-variability illustration in tab 3, labeled as an illustration, with the official inference only on the single SRS. Specified in 4.6, 9.4 and 9.6 and criteria 54 to 60. One fixed seed 2026111209 replaces the "seeds 1 to 1,000" of the original offer. The instruction to use one fixed seed for the illustration came from the orchestrator (Claude), not from João. The seed design stays (see the S14 row below) | João (O2 (b)), orchestrator (fixed seed) |
| 2026-11-12 (step 2 gate) | O4 (a): no age view in tab 1 | João |
| 2026-11-12 (step 2 gate) | Kept at their defaults: O1 (a) no Wald interval, O3 (a) no weighted indicators in the app (the weighted against unweighted difference stays in base.md from relatorio_dados.json), O5 (a) pos_indeterminado counted as graduação and disclosed, O6 (a) Newcombe interval for the supplementary difference, O7 (a) the prefixed method governs and a failed condition is disclosed (4.5), O8 (a) the "negated" rule is kept and its familywise error up to about 10% is disclosed, O11 (a) + (d) question selector and histogram log10 toggle and bin slider in tab 3, O12 (a) new label nao_remunerado | João |
| 2026-11-12 | S14 (step 2 audit, cycle 3): (1) the fixed-seed instruction for the illustration is attributed to the orchestrator, not to João (O2 row corrected), and the seed design 2026111209 stays. (2) The error-control note in tab 3 next to the global table (9.4, criterion 59) is kept, now as João's decision. (3) The official-estimate marker on the illustration histogram (9.4, criterion 58) is kept, now as João's decision | João |
| 2026-11-12 | S13 (step 2 audit, cycle 3): 4.6 wording fixed. proporcao_lado_esperado equals the size of the directional "supports" decision for QP3 and QP4 under location shift and only approximates it for QP1 and QP2. No number changes | João |
| 2026-11-12 | Data-report aviso "ocupados da janela com tipo de rendimento em branco" (63,297 records, exactly the nao_remunerado records): option (a), kept as an aviso. It is expected and is not a data problem (2.4, criterion 61). Options not chosen: (b) level ok or new wording, (c) remove the aviso | João |
| 2026-11-12 | D6 (step 1 re-audit): option (b), the spec states id_pop as UInt32 (2.2), the type written since step 1. The code and the parquet stay as they are. Option not chosen: (a) change the code to int64, which would change the parquet sha256 before the freeze of 2.6 | João |
| 2026-11-12 | D4 and D5 (step 1 re-audit): option (b), left as they are and accepted as minor defects. D4: the code classifies "zero" as P1070 = 1 and P1080 = 0 only, not P1080 blank as in 2.4. It affects 0 real records (no P1070 = 1 record has P1080 0 or blank), so no output changes. D5: gaps in the synthetic test cases (labels of the planted P0990 cases, the reverse D1 direction, P0990 blank, P1080 blank). It concerns test coverage only, criterion 4 is met in substance and no output changes | João |
| 2026-11-12 | S15 (step 2 audit, cycle 4): option (a), 13.16 wording fixed. Reading the expected-side share as the size of "supports" holds for QP3 and QP4 under location shift and only approximately for QP1 and QP2, consistent with 4.6. No number or rule changes | João |
| 2026-11-12 | Exclusion disclosure (13.2, criterion 61): base.md and interpretacao.md say explicitly that the excluded share of the employed of each sex is the sum of nao_remunerado and outra_forma, and also report each category separately by sex as a count and as a share of the employed of that sex. All figures are read from outputs. To supply them, block D of 9.6 fixes situacao_rendimento proporcao as n over the group's registros with all five labels listed, and adds situacao_rendimento_excluida {n, proporcao, categorias} per group in populacao.json. The 9.7 rows for base.md and interpretacao.md cite these keys | João |
| 2026-11-12 (step 3 gate) | Final n = 1,537 (95% confidence, margin 2.5%, p = 0.5), by rule 2 of 5.4: joint floor 0.706 at 1,068 and 0.870 at 1,537 (outputs/validacao/planejamento.md). João confirmed n in the USP/Bauru calculator and kept the screenshot. O9 not triggered and closed. Draw command: `uv run src/amostragem.py sortear --margem 0.025` (5.1, 5.2, 5.4, 6). Pre-draw fix R1 (auditoria/passo_3_tamanho.md, Reauditoria pré-sorteio): 13.7 now refers to the approved 2.5% margin (n = 1,537) instead of 3% | João |
| 2026-11-12 (step 3 gate) | C1 (a): `--margem` is mandatory in sortear, with no default, and the manifest field comando records the actual command line used (6, criteria 14 and 63) | João |
| 2026-11-12 (step 3 gate) | C2 (a): manifest versoes lists python and the libraries src/amostragem.py actually uses, with their versions (6, criterion 14) | João |
| 2026-11-12 (step 3 gate) | C3 (a): meio_difere = false is the normal case with ties and is reported in planejamento.md as information, not WARN (5.3) | João |
| 2026-11-12 (step 3 gate) | C4 (a): block D pos_indeterminado is {n, proporcao} with proporcao = n / registros of the group (share of the employed). Texts say so and never present it as a share of those with S (9.6, 13.6, criterion 64) | João |
| 2026-11-12 (step 3 gate) | C5 (a): automated test of criterion 11 (sortear refuses if the manifest exists), run against a temporary directory and never touching outputs/amostra/ (criterion 62) | João |
| 2026-11-12 (step 3 gate) | S16 (b): exception in 9.5, the excluded share and each non-valid category share are shown in percent with 3 decimals in texts and app, so the parts add up to the total (9.5, criterion 61). Options not chosen: (a) a note that the parts may not add up, (c) both | João |

### 12.2 Open decisions
No decision remains open. O9 was contingent and was not triggered at step 3 (F(1,537) >= 0.80, 12.1), so it is closed. O1 to O12 are not reopened.

O9 (closed, not triggered). If the joint floor stays below 0.80 at n = 1,537 (contingent, decided at step 3 only if it happens).
- (a) Keep 1,068 and disclose the low power of the weakest QP.
- (b) n = 2,401 (margin 2%).
- (c) n = 1,537 anyway.
- No default. Recommendation deferred to step 3, with the power table in hand.

## 13. Limitations the texts must disclose

1. The population is the public sample microdata file, not the Brazilian population. The file is not self-weighting and the weight is not used, so unweighted and weighted values differ (relatorio_dados.json resumo.conferencia_por_sexo).
2. Earnings parameters condition on positive cash earnings (valido). The earnings domains of QP2, QP3 and QP4 (MV, HV, MSV, HSV) and every earnings descriptive (tabs 1 and 2, populacao.json and inferencia.json rendimento_valido and rendimento_valido_superior) exclude all employed records whose situacao_rendimento is not "valido": the unpaid workers (nao_remunerado, P1070 blank and P0990 = 9, who help a household member or relative and have no earnings by definition, 63,297 records in the frame per the design target of 2.4), the earnings only in another form (outra_forma, P1070 = 2), and zero and sem_informacao if present. QP1 is unaffected (it uses all employed). The excluded share is larger among women. The texts give, for women and for men separately: (i) the excluded share of the employed of that sex, from populacao.json descritivas.grupos.mulher and .homem situacao_rendimento_excluida.proporcao (with its count n), saying explicitly that this share is the sum of the non-valid categories, which in this frame are nao_remunerado and outra_forma (zero and sem_informacao have count 0 per the step 1 report and the 2.4 targets, and the texts name a category only if its count is above 0), and (ii) each of those categories separately, as a count and as a share of the employed of that sex, from populacao.json descritivas.grupos.mulher and .homem situacao_rendimento (n and proporcao of the entries nao_remunerado and outra_forma). Counts may also be cited from relatorio_dados.json resumo.sexo_x_situacao_rendimento. Every figure is read from these keys, never typed or computed by the writer. The texts present nao_remunerado as unpaid work, not as missing data or a data problem (2.4).
3. Earnings are usual gross monthly earnings from all jobs, self-reported, nominal R$ of July 2022, heaped at round values (the reason p0 is not 0.5).
4. The public file has no hours worked and no occupation, so the earnings gaps are raw, not adjusted, and say nothing about causes or discrimination.
5. Age exists only in 5-year groups, so there is no mean age and age is not controlled in the tests.
6. Education levels: 133,507 people with S and unknown level are counted as graduação (current students, lower bound), and 20,396 who attended but did not conclude a postgraduate course are graduação by rule D2. The four QPs use S and are unaffected. Any pos_indeterminado share cited is populacao.json descritivas.grupos.*.pos_indeterminado.proporcao, which is n over the employed of the group (registros). The texts say explicitly that it is a share of the employed and never present it as a share of those with complete higher education, and the writer does not compute any other ratio (criterion 64).
7. Domain sizes are random and smaller than n. The approved 2.5% margin (n = 1,537, 12.1) refers to a proportion on the whole sample with p = 0.5. Domain intervals, especially for women with S, are wider (realized half-widths in inferencia.json).
8. The reference constants are treated as known, which is possible only because the frame is known. A real study would compare two estimates, which is what the supplementary two-proportion test of QP1 shows.
9. Earnings are extremely right-skewed in the frame: the mean is well above the median and the maximum is far above P90 (populacao.json descritivas.grupos.*.rendimento_valido and rendimento_valido_superior, media, mediana, p90, maximo). The t interval relies on the central limit theorem, which at these domain sizes does not make ybar close to normal. The BCa interval and the skewness check are shown next to it, and neither removes the problem (13.11, 13.15).
10. Single sample: another seed would give other estimates. For QP1 and QP2 each 95% Wilson interval misses its frame value in about 1 of 20 samples (approximately, the illustration gives the observed share in ilustracao.json proporcao_cobre). For QP3 and QP4 the 95% t interval misses more often than 1 in 20 and mostly on the low side (13.11, ilustracao.json proporcao_cobre and proporcao_inteiro_abaixo). With four intervals the chance that at least one misses is not small.
11. Error control and its direction (decision O10 (a)). By the intersection-union rule the size of "sustained" is at most the largest actual one-sided size among the four directional decisions, not 5% by construction. For QP3 and QP4 the t interval governs, and in this frame it lies entirely below the true mean (the expected side) far more often than the nominal 2.5% and entirely above it less often. So for QP3 and QP4 the size of the directional "supports" decision exceeds its nominal one-sided 2.5%, the size of "sustained" is at most about the largest per-question size and is not controlled at the 5% that docs/requirements.md claims, the excess favors the hypothesis, and "contradicts" is rarer than nominal for QP3 and QP4. The texts compare each per-question share from ilustracao.json (qpk proporcao_lado_esperado, which for QP3 and QP4 is proporcao_inteiro_abaixo, and qp3 and qp4 proporcao_inteiro_acima, with Monte Carlo standard errors) with the nominal 2.5% per direction and never with 5%, and state that the global size of "sustained" is at most about maior_proporcao_lado_esperado (valor, with erro_padrao_mc, at questao), against the nominal global 5% claimed by docs/requirements.md (7.2). They do so whatever the verdict, state the direction, and never say that "sustained" is controlled at 5%. "Negated" has familywise error up to about 10% (approximate, section 7.2, decision O8 (a)).
12. Statistical significance is not practical relevance. Differences are also reported in R$ and percentage points.
13. Sex is binary as recorded. 19,216 records with sex ignored are outside the frame, and none of them is aged 25 or older.
14. The finite population correction is not applied, a negligible and conservative choice.
15. The skewness condition (Cochran's rule with the sample G1) can say "ok" while the premise fails: with a heavy right tail the sample G1 grossly underestimates the skewness of the domain, because a sample rarely contains the extreme values that drive it. An "ok" is not evidence that the t approximation holds, and an "aviso" is evidence against it. The direct evidence on the t approximation is the coverage of the t interval in the illustration (ilustracao.json qp3 and qp4 proporcao_cobre and proporcao_inteiro_abaixo). This is stated in words, without a frame skewness figure.
16. The figures of 13.10, 13.11 and 13.15 come from the illustration of 4.6: 1,000 SRSs of the approved n drawn from the frame after the official draw, labeled as an illustration and used in no verdict. They are Monte Carlo estimates with a stated standard error (sqrt(p (1 - p) / 1,000), about 0.5 to 0.9 percentage points for shares between 2.5% and 10% or near 95%), not exact values. Reading the share on the expected side as the size of "supports" holds for QP3 and QP4 under the assumption that under a boundary null the domain has the frame shape shifted to the reference (location-shift assumption, 7.2), and only approximately for QP1 and QP2, where there is no location shift of a proportion and the coverage of the Wilson interval changes with p, so the share measured at the frame value only approximates the size at the boundary p = p_H or p = p0 (4.6).
17. The BCa interval of QP3 is fragile evidence (added after the draw, section 11). The BCa interval is reported alongside the t interval and never decides the verdict (4.5, decisions O7 (a) and O10 (a)). For QP3 its upper bound lies very close to the reference mu_H, so its category depends on the Monte Carlo error of the bootstrap (B = 10,000, seed fixed before the draw) and could have been "inconclusivo" with another bootstrap seed (design rationale only: auditoria/passo_5_inferencia.md observation 2, never cited by texts). The agreement between the t and BCa categories on QP3 (the condition of 4.3 iv) must therefore not be presented as strong evidence or as corroboration of the t verdict. interpretacao.md and the video script disclose this. The only numbers they cite for it are the QP3 BCa upper bound, inferencia.json questoes.qp3.ic_bootstrap.superior, and mu_H, inferencia.json questoes.qp3.referencia (equal to populacao.json questoes.qp3.referencia), shown side by side under the rounding of 9.5. No output key holds their difference, so the texts do not state it, compute nothing and cite nothing from auditoria/ (criterion 65).
