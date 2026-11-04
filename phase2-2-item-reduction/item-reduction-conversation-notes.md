# GitInstrument: notes on the item reduction (phase 2)

> Content pasted by Eliane on 2026-10-26 (excerpts of the work sessions on the item reduction). Kept as written; only the headings and tables were formatted in Markdown.

---

## 1. Request: trace the *Results Summary* table

I started adding phase 2's analyses to the repository. Unfortunately, I did a lot of things manually and barely remembers what I did. I need help to track the notebooks and results.

I've included a new folder Item Reduction with the item reduction part of phase 2. In the root folder, there is a excel file called Summary of Index in Item Reduction.xlsx. The first tab (Results Summary) is the table we will reference in the paper. It uses data from the other Reliability Version X and Complete_Fit_Model_Results tabs. The R notebooks used are in the Notebooks folder. Can you track from where the results in the first tab came from?

> I'll map out the Item Reduction folder, read the Excel summary, and trace each result in the first tab back to its source tab and the R notebook that produced it.

I traced all 149 numbers in the Results Summary tab back to the R output files that produced them. 139 match their source exactly, and 10 have problems you should fix before the paper. I didn't change the Excel file.

### Where the numbers come from

**Reliability rows (3–20):** these are Cronbach's alpha values. They were produced by `phase2-2-itemreduction/02-reliability/Reproduce2-reliability.Rmd`, which saved them as CSV files in the run folders under `Item Reduction/ModelFit-CFA/`. You then put them in the `Reliability/260429V?_Reliability.xlsx` workbooks and pasted them into the "Reliability Version X" tabs.

**Model fit rows (21–56):**

- **Notebooks:** they come from `Reproduce3-MG-CFA-Model_1.Rmd` (full model and Model_1), `Model_2.Rmd` and `Model_3.Rmd`.
- **Output files:** these saved `fit_indices-*.csv` files, which you renamed with a `V?_` prefix and moved into one dated folder per version.
- **Workbook:** they went through `ModelFit-CFA/260429CompleteModelFit.xlsx` and were pasted into the `Complete_Fit_Model_Results` tab. The `260428CompleteFitModel.xlsx` file is an older draft with broken references; it isn't the source.

### Problems in the table

- **I48** (SRMR, Version E, Model_1) is wrong. It shows the RMSEA value (0.0859). The formula in `CompleteModelFit!G34` points to the RMSEA row. The correct SRMR is 0.0771.
- **I6, I7, I11, I12, I16 and I17** are not Version E results. When you ran Version E, the reliability notebook still had Model_2 set to Version B and Model_3 set to Version D. These values are exactly those versions' results. No Version E Model 2 or 3 was ever fitted, so these cells should probably be blank.
- **G15 and H15** (Visualization, Model_1, Versions C and D) used P022A instead of P089. The item-level output files confirm it, but your item tab and the fit notebook both say P089. Decide which set you meant, then rerun the reliability (and check the matching fit runs).
- The **column I header** says "Version 3" but should say "Version E".
- **C47** is a typed number, not a formula. The value is correct.
- The **"complete list" values in column C** come from the 3-factor structure. Version E's own full-data values differ (Task_cognition 0.935 vs 0.946; Visualization 0.899 vs 0.916). The full-model fit in column C is also the 3-factor, 65-item model, while column I's is the 4-factor, 61-item one.

Two things will matter if you try to reproduce this. Each notebook is still set to the last version you ran, because you switched versions by commenting item lists in and out. Also, the Version B folder has no Model_2 reliability files. Those numbers are still right, because B and B2 use the same items for Model_2 and the B2 folder has the files.

I saved two files in `Gdrive_files\Item Reduction\` on your computer:

- `Results_Summary_PROVENANCE.md`: the explanation, the list of problems and a short note on making the notebooks reproducible.
- `Results_Summary_cell_lineage.csv`: one row per cell, with its source tab, workbook, CSV file, notebook and check status.

A natural next step would be to finish the loop in `Reproduce2-comp-reliability.Rmd` so it runs every version in one go. That would let you regenerate the whole table from code and fix problems 1–3 at the same time.

---

## 2. Regenerating the reliability files

**Eu preciso gerar tudo isto novamente. Como você pode me ajudar a regerar os arquivos de reliability (primeiro)?**

> Planejando um script para regenerar arquivos de confiabilidade.

Vou montar um único notebook R que regera todos os arquivos de reliability, para todas as versões e modelos, a partir de uma lista central de itens. Antes de entregar, vou testá-lo aqui e conferir se reproduz os valores antigos. Começo lendo o notebook atual e localizando os dados de entrada.

**Perguntas e respostas:**

| Pergunta | Resposta |
|---|---|
| Qual base de dados deve ser a oficial para os alfas do artigo? | "vou te responder tudo, mas vamos por parte. Não entendi a primeira questão, você disse que os dados não colapsados reproduzem exatamente os valores da tabela. Onde vc os encontrou? Por que precisa do arquivo original? Dentre os 66 items está algum item de atenção? P901 e P902?" |
| Nas Versões C e D (Model_1, visualização), qual item entra? | P022A (como foi rodado) |
| A Versão E deve ter Model_2 e Model_3? | [No preference] |

Os arquivos não colapsados que reproduzem a tabela estão em `phase2-2-itemreduction\Data\Reproduce7_Data\`, os três `ratings-stimulus_{system,task_cognition,visualization}.csv` usados no IRT. Com eles, todos os alfas dos Models 1, 2 e 3 batem com a tabela até a décima casa decimal.

**Como identifiquei o colapso.** Os valores antigos não batiam com o `ratings-stimulus.csv` atual (pastas Reproduce2, 3 e 4). Esse arquivo é idêntico ao `Reproduce1_Data\ratings-6.csv`, e os dois estão colapsados. Ao aplicar o seu script `04_Colapsing_Low-Frequency Categories-toRight.R` (limite de 2,5%) aos arquivos do Reproduce7, o resultado fica célula por célula igual ao `ratings-stimulus.csv` atual. Os arquivos do Reproduce7 ainda têm 91 categorias com frequência ≤ 2,5%; o atual não tem nenhuma.

**Por que preciso do arquivo original.** Os arquivos do Reproduce7 têm só 49 itens (14 + 19 + 16, a lista do Model_1 da Versão A). Os outros 16 itens, como P031, P102, P103 e P213, só existem na versão colapsada. Sem eles não consigo reproduzir a linha "complete list" de nenhum fator nem o fator reliability da Versão E.

**Itens de atenção.** Eu errei ao dizer 66 itens: são 65 itens, e a 66ª coluna é o seed. P901 e P902 não aparecem em nenhum dos arquivos de dados, então já foram removidos antes.

**Tamanho da diferença.** Com os dados colapsados, a maioria dos alfas muda menos de 0,01. A maior mudança é de cerca de +0,013 (visualization, Model_3). Há um ponto de atenção: os notebooks de CFA leem o arquivo colapsado. A tabela atual pode estar misturando alfas de dados não colapsados com CFA de dados colapsados. Não consegui confirmar isso porque o R não pode ser instalado aqui.

**O que já ficou pronto.** O notebook novo `phase2-2-itemreduction\02-reliability\Reproduce2-reliability-all-versions.Rmd` está na sua pasta. Ele roda todas as versões e modelos de uma vez, a partir de uma única lista de itens no topo, sem precisar comentar e descomentar blocos.

- **Suas decisões:** as Versões C e D usam P022A, como você escolheu. A Versão E ficou só com Model_1, porque você não indicou preferência.
- **Saída:** vai para uma pasta nova com data em `Data_Analysis\` e não sobrescreve nada. Ela inclui uma tabela consolidada no formato da Results Summary, que substitui o passo manual no Google Sheets.
- **Ainda não testado:** o notebook ainda não foi rodado em R, então rode-o no RStudio antes de confiar nos resultados.
- **Arquivo de dados:** o padrão é o `ratings-stimulus.csv` colapsado, e trocar exige mudar uma linha.

Falta você decidir qual base é a oficial:

- **Não colapsada:** reproduz a tabela atual, mas você precisa me dizer onde está o arquivo original com os 65 itens antes do colapso. Pode estar no histórico do git ou na pasta de onde os dados vieram.
- **Colapsada:** fica coerente com a CFA, e os alfas mudam um pouco.

> **Nota de 2026-10-26 (contexto atual):** essas decisões foram revistas depois. Em 2026-10-15 ficou decidido que os passos 01 e 02 usam os dados **colapsados**, e que o Model_1 das Versões C e D usa **P089** (o P022A do run de abril foi um engano). Ver `item-reduction-context.md`, §4.2.

---

## 3. Scripts used in the multi-criteria ranking

> Tracing how the April ranking criteria were originally calculated.

Não existe um script que tenha feito a triangulação em si. Em abril, o ranking foi montado nas planilhas da equipe, e a prioridade final foi um julgamento da equipe olhando os três critérios juntos. Os scripts que existem calcularam os critérios que alimentaram o ranking, ou hoje documentam o ranking.

**Scripts que geraram os critérios (abril de 2026)**

| Critério | Origem | Equivalente no repositório |
|---|---|---|
| Confiabilidade (α se o item for retirado) | cálculo em R sobre os dados não agrupados, dentro dos fatores da EFA de 65 itens | `01_reliability/01_reliability.Rmd` (`item_drop_table`), hoje com os 49 itens e dados agrupados |
| Carga fatorial (λ) | EFA de 3 fatores (run `260318Data_Analysis-PolyCorr-2_5_Collapsed`) | `00-efa-screening/input/efa-pa-3-factors-agg.csv` |
| IRT (gráficos pontuados) | `Reproduce7-IRT-graded.Rmd`, gráficos de 12/04 (`260412-IRT-ThirdRun-Colored`) | `03_irt/03_irt.Rmd`, que reproduz os mesmos gráficos com os dados não agrupados |

**Etapas feitas à mão nas planilhas**

- notas da rubrica do IRT e rank do IRT (planilha de 23/04);
- prioridade inicial (*Ranking revisited considering reliability, loadings and IRT*);
- prioridade final, revisada pela Petra e pela Anne-Flore (*Ranking revisited 2*).

**Scripts de documentação em `04_ranking/`** (criados agora; não fazem o ranking):

- `extract_ranking_criteria.py`: extrai das planilhas os valores, ranks, notas e prioridades para o `ranking_criteria.csv`;
- `build_ranking_table.py`: confere se cada rank segue o seu valor, se os modelos reduzidos são os cinco primeiros de cada critério e se o pool da busca combinatória são os primeiros da prioridade final. Gera a tabela `tab:triangulation-ranking` e o `ranking_table_full.csv`;
- `build-irt-ranking-table.py`: gera a tabela `tab:IRT-ranking`.

No artigo, o mais fiel é descrever a triangulação como uma decisão da equipe, apoiada nos três critérios, e não como um procedimento automático. Os scripts entram como material suplementar, para reproduzir os critérios e conferir a coerência das tabelas.

---

## 4. Source of the EFA loadings and order of P088, P026 and P086

**De onde vem a tabela com os efa loadings? Qual é a ordem original entre os items P088, P026 e P086 - logo apos a execução do efa?**

### De onde vem a tabela de cargas

O arquivo usado no repositório é `phase2-2-item-reduction/00-efa-screening/input/efa-pa-3-factors-agg.csv`. Ele é uma cópia de:

```
UXVis/Replication - UXVis development figures/Data_Analysis_by_date_focus/
  260318Data_Analysis-PolyCorr-2_5_Collapsed/generatedData-EFA/Agg/PA1 Stimuli 3 factors - Agg.csv
```

É a saída da EFA de 18/03/2026: eixos principais, 3 fatores, correlações policóricas, todas as ferramentas juntas e respostas agrupadas a 2,5%. O MD5 está no README do passo 00. A mesma tabela foi colada na aba *PA1 Stimuli 3 factors – Agg* da planilha da EFA, colunas *Collapse 2.5*. Ao lado dela, essa aba tem também as cargas da EFA com respostas não agrupadas.

### Ordem dos itens no System, logo após a EFA (o arquivo vem ordenado pela carga)

| Ordem | Item | λ (agrupados, usado) | λ (não agrupados) |
|---|---|---|---|
| 1 | P088 | 0,892 | 0,772 |
| 2 | P026 | 0,884 | 0,889 |
| 3 | P214 | 0,870 | 0,938 |
| 4 | P4026A | 0,793 | — |
| 5 | P074 | 0,727 | — |
| 6 | P086 | 0,726 | 0,609 |

Na EFA usada (respostas agrupadas), a ordem é **P088 > P026 > P086**: P088 em 1º, P026 em 2º e P086 em 6º no System. É a mesma ordem do rank de carga no `ranking_criteria.csv` e na tabela da triangulação.

Na EFA com respostas não agrupadas a ordem muda: P214 (0,94) > P026 (0,89) > P088 (0,77) > P086 (0,61). Não preenchi P4026A e P074 nessa coluna. Se o texto do artigo citar outra ordem, como no exemplo "#2 P088, #5 P086, #6 P026" da seção de triangulação, vale conferir de qual coluna ou ranking ela veio.
