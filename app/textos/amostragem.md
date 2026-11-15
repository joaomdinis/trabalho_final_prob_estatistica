## Tamanho da amostra e sorteio

**Tamanho.** Para estimar uma proporção com margem de erro `e`, usa-se a fórmula abaixo, com o resultado arredondado para cima. Os parâmetros são 95% de confiança (z = 1,959963984540054), p = 50% e e = 2,5%. O p = 50% é a escolha conservadora, porque maximiza p · (1 - p) e serve para qualquer proporção.

$$
n = \frac{z^{2}\, p\,(1-p)}{e^{2}} = \frac{1{,}959964^{2} \times 0{,}5 \times 0{,}5}{0{,}025^{2}} = \frac{0{,}960365}{0{,}000625} = 1.536{,}58 \quad\Rightarrow\quad n = 1.537
$$

A calculadora sugerida (USP/Bauru) estava indisponível, então o tamanho foi calculado direto pela fórmula acima, a fórmula padrão para o tamanho de amostra de uma proporção. Com a correção para população finita (N = 7.642.045) o resultado seria 1.536,27, que também arredonda para 1.537.

**Sorteio.** Uma amostra aleatória simples, sem reposição, de 1.537 pessoas entre as 7.642.045 da população. Foi feita uma única vez, com semente fixa (20261112). Todas as pessoas têm a mesma probabilidade de entrar, 1.537 / 7.642.045.

**A amostra contra a população.** A amostra tem 40,4% de mulheres, contra 42,2% na população. A proporção com superior completo é 22,0% na amostra e 20,7% na população. A média do rendimento é R$ 2.706,63 na amostra e R$ 2.662,33 na população. As diferenças são pequenas e vêm da variabilidade amostral, não de erro no sorteio. A tabela de comparação, mais abaixo neste painel, mostra cada indicador.

<!-- saiba-mais -->


### Procedimento da amostra aleatória simples

- **Quadro:** a população ordenada por `id_pop`, de 1 a N.
- **Gerador e semente:** `numpy.random.PCG64` com semente 20261112, fixada antes do sorteio e sem olhar os dados. A semente é a data em que o desenho foi escrito.
- **Algoritmo:** cada pessoa do quadro recebe uma chave uniforme entre 0 e 1. As pessoas são ordenadas pela chave, e entram na amostra as 1.537 de menor chave.
- **Mesma probabilidade:** as chaves são independentes e têm a mesma distribuição, então a ordenação é uma permutação aleatória uniforme. Qualquer subconjunto de 1.537 pessoas tem a mesma chance de ser o escolhido.
- **Sorteio único:** o comando `uv run src/amostragem.py sortear --margem 0.025` rodou uma vez. Ele se recusa a rodar de novo quando o manifesto já existe.
- **Manifesto** (`outputs/amostra/manifest.json`): guarda semente, n, N, probabilidade de inclusão, algoritmo, comando e as versões Python 3.11.5, numpy 2.4.6, polars 2.1.0 e scipy 1.17.1. Guarda também os hashes sha256 do quadro, da amostra e da lista de ids. O hash da lista de ids é `d1293efeb342259a5c2b78ef2cd06b8e68dfd35ea89eef45d962e27eea0c345d`. Com a mesma semente e a mesma versão do numpy, o sorteio se reproduz exatamente.
- **Conferências do sorteio:** 13 PASS, 0 WARN e 0 FAIL. Elas verificam tamanho, ids únicos, todos os ids no quadro, linhas idênticas às do quadro e a reprodução com a mesma semente.

### Comparação completa

A amostra tem 621 mulheres (40,4%) e 916 homens (59,6%). Sem filtro, os indicadores ficam assim:

| Indicador | Grupo | População | Amostra | Diferença (amostra menos população) |
|---|---|---|---|---|
| Proporção de mulheres | total | 42,2% | 40,4% | -1,77 p.p. |
| Proporção com superior completo | total | 20,7% | 22,0% | +1,34 p.p. |
| Proporção com superior completo | mulheres | 28,4% | 29,3% | +0,88 p.p. |
| Proporção com superior completo | homens | 15,0% | 17,0% | +2,05 p.p. |
| Média do rendimento válido | total | R\$ 2.662,33 | R\$ 2.706,63 | +R\$ 44,30 |
| Média do rendimento válido | mulheres | R\$ 2.339,75 | R\$ 2.329,81 | -R\$ 9,94 |
| Média do rendimento válido | homens | R\$ 2.895,41 | R\$ 2.959,63 | +R\$ 64,21 |
| Mediana do rendimento válido | total | R\$ 1.600,00 | R\$ 1.600,00 | R\$ 0,00 |
| Mediana do rendimento válido | mulheres | R\$ 1.500,00 | R\$ 1.500,00 | R\$ 0,00 |
| Mediana do rendimento válido | homens | R\$ 1.800,00 | R\$ 1.900,00 | +R\$ 100,00 |
| Média do rendimento com superior | mulheres | R\$ 4.129,40 | R\$ 4.213,61 | +R\$ 84,21 |
| Média do rendimento com superior | homens | R\$ 6.661,44 | R\$ 6.115,93 | -R\$ 545,51 |

Uma AAS não reproduz a população exatamente, e outra semente daria outros valores. As medianas ficam muito perto das da população, e as médias variam mais. A maior diferença em reais está na média dos homens com superior. A cauda do rendimento é muito longa, e uma amostra de 1.537 pessoas quase nunca contém os valores extremos. O maior rendimento da amostra é R\$ 90.000,00, e o da população é R\$ 5.000.000,00. Entre os homens com superior, o maior valor da amostra é R\$ 40.000,00, e o da população é R\$ 5.000.000,00.

Na amostra, 11 pessoas são não remuneradas (8 mulheres e 3 homens), e nenhuma recebe só em outra forma. Os níveis de pós-graduação têm contagens pequenas (13 com mestrado e 9 com doutorado), então as proporções desses níveis na amostra são imprecisas.

O desvio-padrão na amostra usa divisor n - 1. Com filtros estreitos, as contagens da amostra ficam pequenas e as diferenças ficam ruidosas. Nenhum teste é feito sobre subconjuntos filtrados.