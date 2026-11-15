## Base de dados e população

**Fonte.** IBGE, Censo Demográfico 2022, microdados de acesso público (questionário da amostra, registro de pessoas, todas as UFs). O acesso não exige login.

- **Página com as bases:** [Microdados de acesso público](https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Microdados_e_Areas_de_Ponderacao/Microdados_de_acesso_Publico/), com as pastas `csv/` e `txt/`.
- **Arquivo usado:** [Todas_as_UFs.zip](https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Microdados_e_Areas_de_Ponderacao/Microdados_de_acesso_Publico/csv/Todas_as_UFs.zip), na pasta `csv/`.
- **Dicionário de variáveis e notas metodológicas:** [Documentação](https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Microdados_e_Areas_de_Ponderacao/Documentacao/).

**Contexto e objetivo.** O Censo 2022 usou dois questionários: o básico, aplicado a todos os domicílios, e o da amostra, aplicado a cerca de 11% deles, que é o único que perguntou o rendimento do trabalho de todas as pessoas. Os microdados usados aqui são os do questionário da amostra, com um registro por pessoa: 21.538.508 pessoas, cerca de 10,6% dos 203.080.756 residentes. Cada registro tem um peso (P0110), que diz quantas pessoas do país ele representa. Como só cerca de 11% dos domicílios responderam, cada registro representa, em média, cerca de 9 pessoas, e o valor varia entre os registros. A soma dos pesos é 203.080.756, o total de residentes. Aqui a base serve para testar uma hipótese: entre pessoas ocupadas com 25 anos ou mais, as mulheres têm mais ensino superior completo que os homens e, mesmo assim, ganham menos pelo trabalho.

**Tamanho.** O arquivo tem 21.538.508 registros e 169 variáveis. Depois dos filtros, a população do trabalho tem 7.642.045 pessoas e 13 colunas.

**População e unidade amostral.** A população são as pessoas ocupadas na semana de referência, com 25 anos ou mais e sexo informado: 3.223.225 mulheres (42,2%) e 4.418.820 homens (57,8%). A unidade amostral é a pessoa, um registro do arquivo. A população é o próprio arquivo, não o Brasil. O peso do IBGE não é usado: tratamos o arquivo como a população para poder calcular os valores verdadeiros e compará-los com a amostra sorteada. Por isso as conclusões valem para o arquivo.

**Variáveis usadas.**

- **Sexo:** qualitativa nominal (mulher ou homem).
- **Superior completo:** qualitativa binária, base das questões 1 e 2.
- **Nível de escolaridade superior:** qualitativa ordinal (sem superior completo, graduação, especialização, mestrado, doutorado).
- **Situação do rendimento:** qualitativa nominal (válido, outra forma, não remunerado, zero, sem informação).
- **Rendimento mensal:** quantitativa contínua, em R$, bruto e habitual de todos os trabalhos. É a variável das questões 2, 3 e 4.

Resultado principal na população: 28,4% das mulheres ocupadas têm superior completo, contra 15,0% dos homens. A média do rendimento é R$ 2.339,75 para as mulheres e R$ 2.895,41 para os homens.

<!-- saiba-mais -->

### Como a população foi montada

Cada registro tem um peso (P0110), e a soma dos pesos no arquivo é 203.080.756, igual ao total oficial de residentes do Censo 2022.

| Etapa | Registros |
|---|---|
| Pessoas no arquivo | 21.538.508 |
| Sexo informado (1 ou 2) | 21.519.292 |
| Idade de 25 anos ou mais | 13.940.709 |
| Ocupadas na semana de referência | 7.642.045 |

O arquivo tem 19.216 registros com sexo ignorado. Eles ficam fora da população, e nenhum deles tem 25 anos ou mais. A população é também o quadro do sorteio, e cada pessoa recebe um número `id_pop` de 1 a N na ordem do arquivo.

O arquivo já é uma amostra do Censo, com pesos diferentes entre as pessoas. Com e sem peso os números mudam:

| Sexo | Superior completo, sem peso | Superior completo, com peso | Rendimento médio, sem peso | Rendimento médio, com peso |
|---|---|---|---|---|
| Mulheres | 28,4% | 31,8% | R\$ 2.339,75 | R\$ 2.683,61 |
| Homens | 15,0% | 19,4% | R\$ 2.895,41 | R\$ 3.374,84 |

### Descrição completa das variáveis

| Variável no painel | Origem no arquivo | Tipo | Descrição |
|---|---|---|---|
| `sexo` | P0150 | qualitativa nominal | 1 homem, 2 mulher. O código 9 (ignorado) fica fora da população |
| condição de ocupação | P0950 (P0960 como conferência) | qualitativa | define a população: ocupado na semana de referência |
| `superior_completo` | P0760 | qualitativa binária | verdadeiro quando P0760 = 7. É a variável das questões 1 e 2 |
| `nivel_sup` | P0760, P0700, P0740 | qualitativa ordinal | 0 sem superior completo, 1 graduação, 2 especialização, 3 mestrado, 4 doutorado. A pós-graduação só conta quando foi concluída (P0740 = 1). Quem cursou pós-graduação sem concluir fica em graduação. Descrita por frequências, nunca por média |
| `pos_indeterminado` | P0760, P0700 | qualitativa binária | superior completo com curso mais alto em branco ou ignorado (P0700 em branco ou 99). Conta como graduação |
| `situacao_rendimento` | P1070, P1080, P0990 | qualitativa nominal | válido (rendimento em dinheiro, produtos ou mercadorias, valor maior que 0), outra forma (P1070 = 2), não remunerado (ajuda a morador ou parente, P0990 = 9), zero e sem informação |
| `rendimento` | P1080 | quantitativa contínua, R\$ por mês | rendimento bruto mensal habitual de todos os trabalhos, em reais nominais do período de referência do Censo (julho de 2022), como publicado. Preenchido só quando a situação é válida. É a variável das questões 2, 3 e 4 |
| `peso` | P0110 | quantitativa | peso amostral do IBGE. Uso apenas descritivo, nunca na inferência |

A idade (P0180) só define a população, com o corte de 25 anos ou mais. O arquivo público não tem idade em anos, horas trabalhadas nem ocupação (profissão). P0770 (instrução compatível com 2010) serve só de conferência.

### Escolaridade superior na população

28,4% das mulheres ocupadas têm superior completo (916.126 pessoas), contra 15,0% dos homens ocupados (662.118). No total são 20,7%.

| Nível | Mulheres | Homens |
|---|---|---|
| sem superior completo | 2.307.099 (71,6%) | 3.756.702 (85,0%) |
| graduação | 713.784 (22,1%) | 527.416 (11,9%) |
| especialização | 164.219 (5,1%) | 100.157 (2,3%) |
| mestrado | 27.188 (0,8%) | 23.026 (0,5%) |
| doutorado | 10.935 (0,3%) | 11.519 (0,3%) |

133.507 pessoas têm superior completo com o curso mais alto em branco ou ignorado (`pos_indeterminado`). Elas são 1,7% de todos os ocupados, 2,5% das mulheres ocupadas (81.221) e 1,2% dos homens ocupados (52.286). Contam como graduação, o que torna as parcelas de pós-graduação um limite inferior. As quatro questões usam só o superior completo e não são afetadas.

### Rendimento na população

O rendimento é muito assimétrico à direita: a média fica bem acima da mediana, e o máximo fica muito acima do percentil 90.

| Grupo | Pessoas | Média | Mediana | Desvio-padrão | P90 | Máximo |
|---|---|---|---|---|---|---|
| Mulheres | 3.176.232 | R\$ 2.339,75 | R\$ 1.500,00 | R\$ 4.529,37 | R\$ 4.800,00 | R\$ 2.700.000,00 |
| Homens | 4.395.843 | R\$ 2.895,41 | R\$ 1.800,00 | R\$ 7.584,63 | R\$ 5.000,00 | R\$ 5.000.000,00 |
| Mulheres com superior | 911.024 | R\$ 4.129,40 | R\$ 3.000,00 | R\$ 7.307,24 | R\$ 8.000,00 | R\$ 2.700.000,00 |
| Homens com superior | 660.218 | R\$ 6.661,44 | R\$ 4.000,00 | R\$ 17.363,37 | R\$ 15.000,00 | R\$ 5.000.000,00 |

O desvio-padrão da população usa divisor N. A escala logarítmica do histograma é só uma visão descritiva.

### Quem fica fora das medidas de rendimento

As medidas de rendimento e as questões 2, 3 e 4 usam só o rendimento válido. Ficam de fora os ocupados não remunerados (P0990 = 9), que ajudam um morador ou parente sem receber, e os que recebem só em outra forma (P1070 = 2). Rendimento zero e sem informação têm contagem 0. Não remunerado é trabalho sem pagamento, não é dado faltante. A questão 1 usa todos os ocupados e não é afetada.

| Sexo | Ocupados | Outra forma | Não remunerado | Total excluído |
|---|---|---|---|---|
| Mulheres | 3.223.225 | 3.639 (0,113%) | 43.354 (1,345%) | 46.993 (1,458%) |
| Homens | 4.418.820 | 3.034 (0,069%) | 19.943 (0,451%) | 22.977 (0,520%) |

As parcelas são calculadas sobre os ocupados de cada sexo. A exclusão é maior entre as mulheres.