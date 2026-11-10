# Genome-scale metabolic models

Stored gzip-compressed SBML (COBRApy reads `.xml.gz` directly). Used by
`modules/flux.py` and the **Flux Analysis** page.

| File | Model | Reference | Obtained from |
|---|---|---|---|
| `iML1515.xml.gz` | *E. coli* K-12 MG1655, 2,712 reactions, 1,877 metabolites | Monk JM et al. (2017) *Nat Biotechnol* 35:904–908. doi:10.1038/nbt.3956 | [SysBioChalmers/ecModels](https://github.com/SysBioChalmers/ecModels) `eciML1515/model/iML1515.xml` (original from BiGG Models) |
| `yeast-GEM.xml.gz` | *S. cerevisiae* S288C, yeast-GEM v9.1.1, 4,105 reactions, 2,748 metabolites | Lu H et al. (2019) *Nat Commun* 10:3586. doi:10.1038/s41467-019-11581-3 | [SysBioChalmers/yeast-GEM](https://github.com/SysBioChalmers/yeast-GEM) `model/yeast-GEM.xml` |

Check the source repositories for license terms before redistributing.
Models are used unmodified; medium and exchange constraints are applied at
runtime from the measured rates.
