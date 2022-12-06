# WMT22 Term-Based Evaluation Metric for Legal Texts
[//]: <> (repository name: wmt22-term-based-metric)
This repository contains the code for the automatic term-based evaluation metric, which is beneficial for the use in translation of the legal texts.
## Presentation of the Concept
* [paper](https://www.statmt.org/wmt22/pdf/2022.wmt-1.41.pdf) - short paper submitted to [WMT'22](https://www.statmt.org/wmt22/)
* [poster.pdf](poster.pdf) - poster with the main ideas, presented at the [WMT'22](https://www.statmt.org/wmt22/)

### Data
The data used for testing the suggested metric is the [ELITR agreement corpus](https://github.com/ELITR/agreement-corpus). 
The scores of the widespread automated metrics that we checked against ours are taken from the results from [WMT2021 News Track](https://github.com/wmt-conference/wmt21-news-systems/tree/main/scores).

***

# Release 0

#### What is accessible:
* main pipeline for processing the files and computing the metrics
* tentative howto and documentation (see below) 
#### TODO for future:
* new modes for tokenization and alignment steps
* **!!!IMPORTANT!!!** Currently, no specific module for controlling *unambiguity* (see [paper](https://www.statmt.org/wmt22/pdf/2022.wmt-1.41.pdf), page 1) is provided. I am working on it
* better documentation of the classes and functions
* **I consider the current code to be a proposal, not a final realization; so any theoretical and implementational advice is welcome**

## Code Sample
* [example.ipynb](example.ipynb): the main run of the metric
 [comparative_analysis.ipynb](comparative_analysis.ipynb): analysis of my metric variants and its comparison to the mainstream MT metrics
 
## Code description:
* [tokenization.py](tokenization.py):
  * main class: `Tokenizer`
  * input: txt files, sentences separated by newlines, naming conventions: no underscore!!!
  * output: tokenized files with suffix `_tokenized`
  * main methods: 
    * `tokenize_file` for a specific file
    * `tokenize_folder` for the whole folder

* [alignment.py](alignment.py):
  *  main class: `Aligner`
  * input: source texts (src), target (translated) texts (tgt)
  * output: alignment files (alignment)
  * main methods:
    * create_bitext - for a pair of source and target files

* [metric_preparation.py](metric_preparation.py):
  * class `TermBasedMetricPreparator` (creates df with necessary info for final metric)
  * input: src, tgt, alignment
  * output: csv file (hereinafter TORT) with source sentences, target sentences, source terms per sentence, translated "candidate" terms per sentence, "pseudo-reference" terms per sentence 
  * main methods:
    * pipeline (applied for a triplet (src, tgt, alignment) for each text separately)

* [statistics.py](statistics.py) 
  * class `TermBasedMetric` (makes final statistics):
  * input: TORT csv file
  * output: tuple of two floats: "own" metric and "F1" metric for a pair of documents (see page 3 in the paper for the description of metrics)
  * main methods:
    * make_metrics

* [data.zip](data.zip) - zip file with all input and generated data for the code above. You should unpack the 5 folders **straight into your working directory** (not into the `data` folder!)
