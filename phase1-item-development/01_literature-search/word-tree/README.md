# Word tree of "experience" (historical record)

Exploratory aid used in May 2024 to refine the search string of the literature search (step 01). It shows the most frequent words before and after "experience" in IEEE VIS papers, which separated the expressions about user experience (e.g. *experience with the tool*, *experience of using*, *experience working with*) from irrelevant uses (e.g. *years of experience*, *prior experience*, *based on our experience*). The UX expressions became the first group of the final search string (see [`../README.md`](../README.md)).

| File | Content |
|---|---|
| `experience.gv.png` | The word tree (27 May 2024) |
| `experience.gv` | Its Graphviz source |
| `word_tree.py` | The script that drew it (`wordtree` package + Graphviz) |

**Corpus.** The full texts of the IEEE VIS 2021 papers, as XML files extracted with GROBID, on the team NAS (`Z:\Proceedings\VisWeek\Vis-all_full_paper_pdfs-text-extraction-results\Vis-2021`). The script reads the raw XML, so some branches contain XML tags (e.g. `<ref type="bibr"`).

**Not meant to be re-run.** No result of the paper depends on the tree. Re-running the script today would probably give a different tree: the NAS extractions may have changed, the versions of `wordtree` and Graphviz were not recorded, and the input folder was edited by hand. The figure and its source are kept as they were produced.
