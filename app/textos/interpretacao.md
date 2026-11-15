## Inferência e interpretação

**Hipótese.** Entre pessoas ocupadas com 25 anos ou mais, as mulheres têm mais ensino superior completo que os homens e, mesmo assim, ganham menos pelo trabalho, na média geral e entre quem tem superior.

**Como testamos.** A hipótese vira quatro perguntas (QP). Os valores dos homens são conhecidos, porque temos o arquivo inteiro. A amostra de 1.537 pessoas estima só o lado das mulheres, e cada pergunta compara essa estimativa com o valor dos homens. A hipótese nula (H0) diz que mulheres e homens são iguais naquele ponto, e a alternativa (H1) diz que são diferentes. Usamos α = 0,05, testes bilaterais e intervalos de confiança (IC) de 95%.

1. **QP1.** A proporção de mulheres ocupadas com superior completo é maior que a dos homens (15,0%)?
2. **QP2.** Entre quem tem superior, a parcela de mulheres que ganham mais que R$ 4.000,00 (a mediana dos homens com superior) é menor que a dos homens (49,8% deles ficam acima desse valor)?
3. **QP3.** O rendimento médio das mulheres ocupadas é menor que o dos homens (R$ 2.895,41)?
4. **QP4.** O rendimento médio das mulheres com superior é menor que o dos homens com superior (R$ 6.661,44)?

**Resultado.** Nas quatro perguntas, a amostra apoia a hipótese e a população confirma: hipótese sustentada. Em todas, o valor-p fica abaixo de 0,05 e o intervalo contém o valor da população.

**Ressalvas.**

- **A população é o arquivo.** As conclusões valem para o arquivo de microdados, não para o Brasil, e o peso do IBGE não entra.
- **A diferença de rendimento é bruta.** Não controla profissão, horas trabalhadas nem idade, e não prova discriminação.
- **Outra amostra daria outros números.** Em 1.000 amostras simuladas, o intervalo t do rendimento ficou inteiro abaixo do valor da população em 6,1% das amostras na QP3 e 7,1% na QP4, quando o esperado era 2,5%. O rendimento é muito assimétrico, e isso faz o intervalo t errar mais que o nominal. Por isso o erro de concluir "sustentada" pode chegar a cerca de 7,1%, e não a 5%. O excesso favorece a hipótese.

<!-- saiba-mais -->

### Como ler os resultados

- **Intervalo de confiança de 95%:** vem de um método que, em amostras repetidas, cobre o parâmetro em 95% delas. Não quer dizer que este intervalo específico tem 95% de probabilidade de conter o parâmetro.
- **Valor-p:** é a probabilidade, supondo H0 verdadeira, de obter uma estatística de teste pelo menos tão extrema quanto a observada. Rejeita-se H0 quando é menor que 0,05.
- **Intervalo e teste são o mesmo evento.** Em cada questão o intervalo é a inversão do próprio teste. Então "valor de comparação fora do intervalo" e "valor-p menor que 0,05" são a mesma coisa. Se o valor caísse dentro do intervalo, a conclusão seria não rejeitar H0, o que não é o mesmo que aceitar H0.
- **Resultado na amostra:** *apoia* quando o intervalo fica inteiro do lado esperado do valor dos homens, *inconclusivo* quando o contém e *contradiz* quando fica inteiro do outro lado.
- **Resultado na população (arquivo):** *vale* ou *não vale*, calculado no arquivo inteiro, sem inferência.
- **Hipótese:** *sustentada* se as quatro questões apoiam (ou valem), *negada* se alguma contradiz (ou não vale) e *inconclusiva* nos demais casos.

Notação: `p_M` e `p_H` são as proporções de mulheres e homens com superior completo. `mu_M` e `mu_H` são os rendimentos médios de mulheres e homens ocupados. `mu_MS` e `mu_HS` são os mesmos, só entre quem tem superior. `m_H` é a mediana do rendimento dos homens com superior, e `p0` é a proporção desses homens acima de `m_H`.

### QP1. Proporção de mulheres ocupadas com superior completo

- **Em palavras:** a amostra indica que a proporção de mulheres ocupadas com superior completo é maior que a dos homens, e a população confirma.
- **Variável e evento:** `superior_completo`, evento "tem superior completo", entre as mulheres ocupadas da amostra (n = 621, 182 com superior).
- **Hipóteses:** H0: `p_M = p_H`. H1: `p_M ≠ p_H`. Sentido esperado: `p_M > p_H`. A comparação `p_H` = 15,0% é a proporção dos homens ocupados com superior na população.
- **Teste:** z para uma proporção, com erro padrão calculado sob H0. z = 10,00, valor-p < 0,0001. Rejeita-se H0.
- **IC de Wilson 95%:** 25,86% a 33,01%, meia-largura de 3,57 p.p., em torno da estimativa de 29,3%. O intervalo fica inteiro acima de 15,0%, então o resultado na amostra é *apoia*.
- **População contra amostra:** na população `p_M` = 28,4%. A estimativa ficou 0,88 p.p. acima, e o intervalo contém o valor da população. Resultado na população: *vale*.
- **Condições:** n · `p_H` = 93,05 e n · (1 - `p_H`) = 527,95, ambos acima de 10. Não há nulos no domínio. Todas ok.
- **Teste complementar, fora do veredito:** comparando mulheres e homens, ambos da amostra, as proporções são 29,3% (621 mulheres) e 17,0% (916 homens). A diferença é 12,28 p.p., com IC de Newcombe de 7,98 p.p. a 16,63 p.p., z = 5,70 e valor-p < 0,0001. Sucessos e fracassos ficam acima de 10 nos dois grupos (182, 439, 156 e 760). É o teste que um estudo real faria, porque fora deste trabalho a proporção dos homens também seria desconhecida.

### QP2. Mulheres com superior acima da mediana dos homens com superior

- **Em palavras:** entre quem tem superior completo, uma parcela menor de mulheres que de homens passa da mediana masculina, e a população confirma.
- **Variável e evento:** `rendimento`, evento "rendimento maior que `m_H`", entre as mulheres com superior e rendimento válido da amostra (n = 178, 44 acima de `m_H`).
- **Valores dos homens:** `m_H` = R\$ 4.000,00 é a mediana do rendimento dos homens com superior na população. `p0` = 49,8% é a proporção desses homens com rendimento estritamente acima de `m_H`. `p0` não é 50% porque o rendimento é declarado em valores redondos e 38.605 desses homens declaram exatamente R\$ 4.000,00. Usar 50% embutiria um viés no teste.
- **Hipóteses:** H0: `pi_M = p0`. H1: `pi_M ≠ p0`. Sentido esperado: `pi_M < p0`. Se as mulheres com superior ganhassem como os homens com superior, a parcela delas acima de `m_H` seria igual a `p0`.
- **Teste:** z para uma proporção, com erro padrão sob H0. z = -6,69, valor-p < 0,0001. Rejeita-se H0.
- **IC de Wilson 95%:** 18,96% a 31,55%, meia-largura de 6,29 p.p., em torno da estimativa de 24,7%. O intervalo fica inteiro abaixo de 49,8%: *apoia*.
- **População contra amostra:** na população `pi_M` = 29,8%. A estimativa ficou 5,10 p.p. abaixo, e o intervalo contém o valor da população. Resultado na população: *vale*.
- **Condições:** n · `p0` = 88,63 e n · (1 - `p0`) = 89,37, ambos acima de 10. Sem nulos. Todas ok.

### QP3. Rendimento médio das mulheres ocupadas

- **Em palavras:** a amostra indica que as mulheres ocupadas ganham, em média, menos que os homens ocupados, e a população confirma. Na população as médias são R\$ 2.339,75 para as mulheres e R\$ 2.895,41 para os homens.
- **Variável:** `rendimento` (R\$ por mês), entre as mulheres ocupadas com rendimento válido da amostra (n = 613).
- **Hipóteses:** H0: `mu_M = mu_H`. H1: `mu_M ≠ mu_H`. Sentido esperado: `mu_M < mu_H`. A comparação `mu_H` = R\$ 2.895,41 é a média dos homens ocupados com rendimento válido na população.
- **Teste:** t para uma média com 612 graus de liberdade. A média amostral é R\$ 2.329,81, o desvio-padrão amostral R\$ 4.184,57 e o erro padrão R\$ 169,01. t = -3,35, valor-p = 0,0009. Rejeita-se H0.
- **IC t 95%:** R\$ 1.997,89 a R\$ 2.661,72, meia-largura de R\$ 331,92. O intervalo fica inteiro abaixo de R\$ 2.895,41: *apoia*.
- **Bootstrap BCa ao lado** (B = 10.000, semente 2026111203): R\$ 2.109,96 a R\$ 2.881,46, categoria *apoia*. O BCa é mostrado ao lado do intervalo t e não decide o resultado. O limite superior do BCa, R\$ 2.881,46, fica muito perto de `mu_H`, R\$ 2.895,41. Com outra semente do bootstrap a categoria do BCa poderia mudar. Por isso a concordância entre t e BCa na QP3 não é evidência forte a favor do resultado do t.
- **População contra amostra:** na população `mu_M` = R\$ 2.339,75. A estimativa ficou R\$ 9,94 abaixo, e o intervalo contém o valor da população. Resultado na população: *vale*.
- **Condições:** sem nulos (ok). Regra de Cochran, n > 25 · G1²: a assimetria amostral é G1 = 15,59, o mínimo pedido é 6.078,78 e n = 613, então o status é **aviso**. A concordância entre t e BCa aparece como ok, com a ressalva acima.

### QP4. Rendimento médio das mulheres com superior completo

- **Em palavras:** entre quem tem superior completo, as mulheres ganham em média menos que os homens, e a população confirma. Na população as médias são R\$ 4.129,40 para as mulheres e R\$ 6.661,44 para os homens.
- **Variável:** `rendimento` (R\$ por mês), entre as mulheres com superior e rendimento válido da amostra (n = 178).
- **Hipóteses:** H0: `mu_MS = mu_HS`. H1: `mu_MS ≠ mu_HS`. Sentido esperado: `mu_MS < mu_HS`. A comparação `mu_HS` = R\$ 6.661,44 é a média dos homens com superior e rendimento válido na população.
- **Teste:** t para uma média com 177 graus de liberdade. A média amostral é R\$ 4.213,61, o desvio-padrão amostral R\$ 7.119,52 e o erro padrão R\$ 533,63. t = -4,59, valor-p < 0,0001. Rejeita-se H0.
- **IC t 95%:** R\$ 3.160,51 a R\$ 5.266,71, meia-largura de R\$ 1.053,10. O intervalo fica inteiro abaixo de R\$ 6.661,44: *apoia*.
- **Bootstrap BCa ao lado** (B = 10.000, semente 2026111204): R\$ 3.553,35 a R\$ 6.302,88, categoria *apoia*. Também aqui o BCa não decide o resultado.
- **População contra amostra:** na população `mu_MS` = R\$ 4.129,40. A estimativa ficou R\$ 84,21 acima, e o intervalo contém o valor da população. Resultado na população: *vale*.
- **Condições:** sem nulos (ok). Regra de Cochran: G1 = 10,12, mínimo 2.560,64, n = 178, status **aviso**. Concordância entre t e BCa: ok.

### O que significam os avisos de Cochran

Nas QP3 e QP4 o status da regra de Cochran é aviso. Isso é evidência contra a aproximação normal da média, na qual o intervalo t se apoia. Um status ok não seria evidência a favor. A evidência direta sobre o intervalo t está na ilustração abaixo, na cobertura observada em 1.000 amostras. Pela regra fixada antes do sorteio, o método previsto (t) decide mesmo com aviso, e o aviso é divulgado.

### População contra amostra

- Os quatro intervalos contêm o valor da população. As estimativas ficaram a +0,88 p.p. (QP1), -5,10 p.p. (QP2), -R\$ 9,94 (QP3) e +R\$ 84,21 (QP4) do valor da população.
- A estimativa pontual quase nunca coincide com o parâmetro. O intervalo mostra a faixa de valores compatíveis com a amostra, e sua largura reflete o tamanho do domínio. As QP2 e QP4 usam só 178 mulheres, por isso seus intervalos são mais largos (meia-largura de 6,29 p.p. e de R\$ 1.053,10) que os da QP1 e da QP3 (3,57 p.p. e R\$ 331,92).
- Em todas as questões os dois resultados coincidem: a amostra apoia e a população confirma. Eles poderiam discordar por variabilidade amostral, e a discordância seria relatada sem correção.

### Efeito da variabilidade amostral (ilustração)

Foram sorteadas da população (arquivo) 1.000 outras amostras aleatórias simples de 1.537 pessoas, com o mesmo desenho e semente 2026111209. Nenhum resultado oficial usa esses números. A inferência oficial é a da amostra única.

| | QP1 | QP2 | QP3 | QP4 |
|---|---|---|---|---|
| Valor na população | 28,4% | 29,8% | R\$ 2.339,75 | R\$ 4.129,40 |
| Tamanho do domínio: média (mínimo a máximo) | 648,0 (589 a 709) | 183,2 (143 a 221) | 638,6 (579 a 696) | 183,2 (143 a 221) |
| Média das estimativas | 28,4% | 29,9% | R\$ 2.338,52 | R\$ 4.122,78 |
| Desvio-padrão das estimativas | 1,81 p.p. | 3,39 p.p. | R\$ 133,23 | R\$ 387,62 |
| 95% centrais das estimativas | 24,9% a 31,9% | 23,5% a 36,9% | R\$ 2.109,26 a R\$ 2.611,95 | R\$ 3.547,25 a R\$ 4.894,29 |
| IC cobre o valor da população | 94,8% (0,70 p.p.) | 95,2% (0,68 p.p.) | 93,1% (0,80 p.p.) | 92,2% (0,85 p.p.) |
| IC inteiro abaixo | 2,9% (0,53 p.p.) | 1,8% (0,42 p.p.) | 6,1% (0,76 p.p.) | 7,1% (0,81 p.p.) |
| IC inteiro acima | 2,3% (0,47 p.p.) | 3,0% (0,54 p.p.) | 0,8% (0,28 p.p.) | 0,7% (0,26 p.p.) |
| IC inteiro do lado esperado | 2,3% (acima) | 1,8% (abaixo) | 6,1% (abaixo) | 7,1% (abaixo) |

Entre parênteses está o erro padrão de Monte Carlo. Os valores nominais são 95% de cobertura e 2,5% para cada lado.

- **A estimativa muda de amostra para amostra.** Na QP3, 95% das médias amostrais ficaram entre R\$ 2.109,26 e R\$ 2.611,95. A estimativa oficial, R\$ 2.329,81, é uma dessas possibilidades. Outra semente daria outros números.
- **O intervalo de Wilson ficou perto do nominal.** A cobertura foi de 94,8% na QP1 e 95,2% na QP2. Com quatro intervalos, a chance de pelo menos um errar não é pequena.
- **O intervalo t erra mais que o nominal, e quase sempre para baixo.** A cobertura foi de 93,1% na QP3 e 92,2% na QP4, e os erros ficaram concentrados no lado de baixo. É o efeito da assimetria à direita: uma amostra que não pega rendimentos altos tem média baixa e também desvio-padrão baixo, então o intervalo fica estreito justamente quando a média está baixa e, nesses casos, fica inteiro abaixo do valor da população.
- São estimativas de Monte Carlo com 1.000 amostras, não valores exatos. O erro padrão de cada uma está na tabela.

### Controle de erro da conclusão "sustentada"

**Por questão.** A decisão "apoia" de cada questão tem erro nominal de 2,5% para cada lado, metade dos 5% de um teste bilateral. Na ilustração, o intervalo ficou inteiro do lado esperado em 2,3% das amostras na QP1 (erro padrão de 0,47 p.p.), 1,8% na QP2 (0,42 p.p.), 6,1% na QP3 (0,76 p.p.) e 7,1% na QP4 (0,81 p.p.). Nas QP3 e QP4 essa parcela passa de 2,5%. Nas QP1 e QP2 não passa. Do lado oposto, nas QP3 e QP4 o intervalo ficou inteiro acima em 0,8% (0,28 p.p.) e 0,7% (0,26 p.p.) das amostras, abaixo de 2,5%. Então, nessas duas questões, "contradiz" ocorre por acaso menos que o nominal.

**Global.** A conclusão "sustentada" exige que as quatro questões apoiem. Pela lógica de interseção e união, o erro dessa conclusão é no máximo, aproximadamente, a maior parcela por questão do lado esperado: 7,1%, com erro padrão de 0,81 p.p., na QP4. O esperado era um nível global de no máximo 5%. Esse valor não vale aqui: o erro de "sustentada" não está controlado em 5%. O limite para o erro desta conclusão é de cerca de 7,1%, não 5%. O excesso favorece a hipótese, porque nas QP3 e QP4 o intervalo t erra mais para baixo, que é justamente o lado esperado. A decisão de manter o intervalo t e divulgar esse excesso foi tomada antes do sorteio.

**Ressalvas.** Nas QP3 e QP4, ler a parcela do lado esperado como o erro da decisão supõe que, no limite de H0, a distribuição do rendimento das mulheres teria a mesma forma, só deslocada até o valor dos homens. Com outra forma o erro seria outro. Nas QP1 e QP2 a parcela foi medida no valor verdadeiro da população, e por isso só aproxima o erro no limite de H0. A conclusão "negada", que não ocorreu, também não teria erro controlado em 5%: seu limite aproximado é a soma dos quatro erros unilaterais nominais.

### Limitações

1. **População é o arquivo.** As conclusões valem para o arquivo de microdados, não para a população brasileira. O arquivo não é autoponderado e o peso não foi usado. Com peso, a proporção com superior seria 31,8% nas mulheres e 19,4% nos homens, contra 28,4% e 15,0% sem peso (Painel 1).
2. **Quem fica fora das questões de rendimento.** As questões 2, 3 e 4 e todas as medidas de rendimento usam só o rendimento válido. Ficam fora os não remunerados (ajudam morador ou parente, sem pagamento, o que não é dado faltante) e quem recebe só em outra forma. A questão 1 usa todos os ocupados. A exclusão é maior entre as mulheres: 46.993 (1,458% das ocupadas) contra 22.977 (0,520% dos ocupados).
3. **O rendimento é declarado.** É o rendimento bruto mensal habitual de todos os trabalhos, informado pela própria pessoa, em reais nominais de julho de 2022, e se concentra em valores redondos.
4. **A diferença de rendimento é bruta.** O arquivo público não tem horas trabalhadas nem ocupação (profissão), e a idade não é controlada. As diferenças entre mulheres e homens não estão ajustadas por profissão, jornada, idade ou outro fator. Elas são descritivas, não dizem nada sobre causas e não são evidência de discriminação.
5. **Idade.** A idade só define a população (25 anos ou mais). O arquivo público traz idade só em faixas, então ela não é analisada nem controlada.
6. **Níveis de escolaridade.** 133.507 pessoas com superior completo e nível de pós desconhecido contam como graduação. Elas são 1,7% dos ocupados. Quem cursou pós-graduação sem concluir também conta como graduação. As quatro questões usam só o superior completo e não são afetadas.
7. **Domínios menores que a amostra.** O tamanho de cada domínio é aleatório e menor que 1.537. A margem de 2,5% vale para uma proporção na amostra inteira. Nos domínios os intervalos são mais largos.
8. **Valores dos homens tratados como conhecidos.** Eles vêm da população, o que só é possível porque o arquivo inteiro está disponível. Um estudo real compararia duas estimativas, como no teste complementar da QP1.
9. **Rendimento muito assimétrico.** Na população, a média das mulheres é R\$ 2.339,75, a mediana R\$ 1.500,00, o P90 R\$ 4.800,00 e o máximo R\$ 2.700.000,00. Entre os homens, a média é R\$ 2.895,41, a mediana R\$ 1.800,00, o P90 R\$ 5.000,00 e o máximo R\$ 5.000.000,00. O intervalo t depende do teorema central do limite, que nesses tamanhos de domínio não deixa a média amostral perto da normal. O BCa e a regra de Cochran aparecem ao lado, e nenhum dos dois resolve o problema.
10. **Uma única amostra.** Outra semente daria outras estimativas. A ilustração mostra o quanto elas variam.
11. **Controle de erro.** O erro de "sustentada" não está controlado em 5%. O limite é de cerca de 7,1% (QP4), e o excesso favorece a hipótese.
12. **Significância não é relevância prática.** As diferenças aparecem também em pontos percentuais e em reais para que o tamanho delas possa ser julgado.
13. **Sexo binário, como registrado.** 19.216 registros com sexo ignorado ficam fora da população, e nenhum deles tem 25 anos ou mais.
14. **Sem correção para população finita.** A fração amostral é muito pequena, então a escolha é desprezível e deixa os intervalos um pouco conservadores.
15. **Regra de Cochran.** Um ok da regra não mostraria que a aproximação t vale, e um aviso é evidência contra ela. A evidência direta é a cobertura do intervalo t na ilustração.
16. **A ilustração é Monte Carlo.** As parcelas vêm de 1.000 amostras e têm erro padrão próprio. A leitura como erro da decisão depende das suposições descritas na seção de controle de erro.
17. **BCa da QP3.** O limite superior do BCa (R\$ 2.881,46) fica muito perto de `mu_H` (R\$ 2.895,41), então a concordância entre t e BCa na QP3 não deve ser lida como confirmação forte.

### O que os quatro resultados dizem sobre a hipótese

No arquivo tomado como população, as quatro afirmações valem: as mulheres ocupadas têm proporção maior de superior completo que os homens e, mesmo assim, ganham menos em média, entre todos os ocupados e entre quem tem superior. Entre as mulheres com superior completo e rendimento válido, a parcela acima da mediana do rendimento dos homens com superior é menor que a parcela desses homens acima dela. Então a hipótese é *sustentada* na população.

A amostra única de 1.537 pessoas chega à mesma conclusão: as quatro questões apoiam, e a hipótese é *sustentada* também na amostra. Esse acerto é o que se espera de uma AAS, mas não é garantido. O erro da conclusão "sustentada" na amostra tem limite de cerca de 7,1%, não 5%, e o excesso joga a favor da hipótese.

A conclusão vale para pessoas ocupadas com 25 anos ou mais do arquivo, sem peso, com rendimento válido nas questões de rendimento. As diferenças de rendimento são brutas e não provam discriminação.