# Patristic Sources 
Working files to pool a dataset of patristic sources (Greek and Latin Church Fathers) in XML TEI Format. The dataset was created in the objective of patristic text reuse detection in reformation-age letters.

## Sources
- [Corpus Corporum](https://mlat.uzh.ch/browser?path=/)
- [Open Greek & Latin](https://www.opengreekandlatin.org)
- [Patristic Text Archive](https://pta.bbaw.de/en/)

## Pooling
Using a list of church fathers ([church-fathers.csv](church-fathers.csv)) the Corpus Corporums website and the GitHub Repos of Open Greek & Latin and the Patristic Text Archive were scraped. The scripts download files and organise them by Church Father ID (CF_ID) in folders.

A full list of all authors, their works and the web-sources to these works can be found here [sources-catalogue.csv](sources-catalogue.csv).

### Downloading Scripts
Three separate scripts download texts from three different sources:
- [cc-tei-download.ipynb](scripts/cc-tei-download.ipynb): Downloads from Corpus Corporum (University of Zurich)
- [ogl-tei-download.ipynb](scripts/ogl-tei-download.ipynb): Downloads from Perseus Digital Library (Open Greek and Latin)
- [pta-tei-download.ipynb](scripts/pta-tei-download.ipynb): Downloads from Patristic Text Archive (Berlin-Brandenburg Academy)

## Duplicates 
Generally, Latin translations were kept, as scholars accessed patristic texts through Latin translations, not necessarily Greek originals. Where multiple versions of the same text in Latin are available, scholarly editions (such as CSEL) are preferred over Migne's Patrologia Latina. Expections are Hieronymus Epistolae and all works used to create ground truth data annotations.

Generally (depending of availability), one version of each work was kept in their original language and the latin translations of greek works.

With the scripts, all sources can be scraped again to delete duplicate according to preferences.

## Dataset Stats
Total files      : 700
Church fathers   : 52

| Church Father               | Number of Works  |
|-----------------------------|------------------|
| Augustinus von Hippo        | 155              |
| Hieronymus                  | 104              |
| Ambrosius von Mailand       |  49              |
| Tertullian                  |  37              |
| Boethius                    |  32              |
| Isidor von Sevilla          |  26              |
| Papst Gregor I. (der Große) |  26              |
| Hilarius von Poitiers       |  25              |
| Cyprian                     |  24              |
| Prosper von Aquitanien      |  24              |

## Worth noting
This collection represents a best-effort collection and makes no claim to completeness. Variant editions, fragmentary texts and sources not yet digitised, or simply not found by me, remain left.

Furthermore, original texts from Syriac Church Fathers were not sourced as reformers' engagement (which was the starting point for this pooling) with Syriac traditions was largely mediated through Latin intermediaries.
