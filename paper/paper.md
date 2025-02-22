---
title: 'Tag-Pag: A Dedicated Tool for Systematic Web Page Annotations'
tags:
  - Paper
authors:
  - name: Anton Pogrebnjak
    equal-contrib: false
    orcid: 0009-0004-1219-337X
    affiliation: 1
  - name: Julian Schelb
    equal-contrib: false
    orcid: 0009-0002-8034-7364
    affiliation: 1
  - name: Andreas Spitz
    equal-contrib: false
    orcid: 0000-0002-5282-6133
    affiliation: 1
  - name: Celina Kacperski
    equal-contrib: false
    orcid: 0000-0002-8844-5164
    affiliation: 2
  - name: Roberto Ulloa
    orcid: 0000-0002-9870-5505
    equal-contrib: false
    affiliation: 2
affiliations:
 - name: Department of Computer Science, University of Konstanz, Germany
   index: 1
 - name: Cluster of Excellence "The Politics of Inequalities", University of Konstanz, Germany
   index: 2
date: 26.08.2024
bibliography: paper.bib
---

# Summary

Tag-Pag is an application designed to simplify the categorization of web pages, a task increasingly common for researchers who scrape web pages to analyze individuals' browsing patterns or train machine learning classifiers. Unlike existing tools that focus on annotating sections of text, Tag-Pag systematizes page-level annotations, allowing users to determine whether an entire document relates to one or multiple predefined topics. 

Tag-Pag offers an intuitive interface to configure the input web pages and annotation labels. It integrates libraries to extract content from the HTML and URL indicators to aid the annotation process. It provides direct access to both scraped and live versions of the web page. Our tool is designed to expedite the annotation process with features like quick navigation, label assignment, and export functionality, making it a versatile and efficient tool for various research applications. Tag-Pag is available at https://github.com/Pantonius/TagPag.

# Statement of need


The annotation of web data is increasingly common across multiple disciplines, serving purposes such as analyzing online behavioral patterns [@stier_populist_2020; @guess_almost_2021; @wojcieszak_non-news_2024; @ulloa_search_2023], auditing the performance of online platforms [@makhortykh_how_2020; @kacperski_examining_2024], or training and evaluating machine learning classifiers [@schelb_assessing_2024]. As the need for processing web data grows, researchers have turned to systematic and efficient methodologies that span the entire process—from data collection to categorization—to ensure robust results.

Online behavioral researchers have recently investigated limitations of web scraping, such as reliance on external environments that differ from individuals' computers [@ulloa_beyond_2024] and changes due to time delays in scraping [@ulloa_beyond_2024; @dahlke_quantifying_2023]. To improve reliability and validity, researchers attempt to scrape data from web pages as close to the visit time of participants as possible and uniformly distribute the delay between the visit and the web page collection. Such limitations have, more recently, been addressed by developing new web tools that collect content directly from an individual's browser [e.g., @adam_improving_2024; @gesis_panel_team_gesis_2025]. Other researchers have gone to the effort of standardizing web data collections for algorithm auditings to avoid for, example, noise stemming from search engine personalization [@ulloa_scaling_2024]. 

These academic efforts illustrate the importance placed on collecting high-quality data for annotation purposes; so far, however, there has been a lack of tools to facilitate the manual annotation process. This has led researchers to instead use inefficient methods such as relying on the URL, rarely accessing the systematically scraped content, or manually visiting (and revisiting) the related web page at different times. As a result, promising lines of inquiry — especially those requiring large-scale and consistent annotations — might be left unexplored. 

Existing tools often focus on annotating specific sections within a text [@rampin_taguette_2021; @meister_tact_2023; @huang_rqda_2016], where the user selects a portion of text and assigns a label or establishes connections between parts of speech [@strippel_brat_2022]. These tools fall short when the goal is to annotate entire pages to determine, for example, if the content corresponds to very specific topics [@schelb_assessing_2024], misinformation [@urman_where_2022], or, more broadly, political content [@stier_populist_2020; @guess_almost_2021], news articles [@ulloa_search_2023] or pages that restrict access such as logins [@dahlke_quantifying_2023]. Tag-Pag [^1] addresses this gap by allowing broad-level annotations of entire web pages.

[^1]: Tag-Pag. https://github.com/Pantonius/TagPag

![Annotation interface for web pages classification tasks. The interface of Tag-Pag is divided into a left sidebar and a main panel. The sidebar provides task navigation, annotation selection labels, and additional tools such as key shortcut references and annotation downloads. The main panel displays web page content in multiple views, including a cleaned text version, raw text, and URL decomposition. Annotators can label data using predefined categories and add comments. Tag-Pag automatically highlight relevant sections of the URL (at the top). \label{fig:interface}](fig1.png)

Tag-Pag uses libraries to extract two versions of the content from the HTML (see Figure \ref{fig:interface}): (1) cleaned text [@barbaresi_trafilatura_2021], with removed boilerplate such as menus and advertisements, and (2) raw text [@artem_golubin_selectolax_2023], with only removed HTML elements. The tool also parses the URLs themselves, which often contain relevant information about the page's content, adding another layer of contextual data for annotations. For a comprehensive overview, users can open the scraped HTML, the live web page, or the latest version stored in the Wayback Machine. For researchers creating or refining training datasets to improve machine learning models, Tag-Pag allows easy text editing to retain only the relevant parts for classifiers, e.g., manually removing boilerplate to further filter the cleaned text.

Additionally, Tag-Pag includes functionality designed to speed up the annotation process: key bindings associated to interface actions for rapid label assignment, automatic transition between pages for single-label annotations are supported, and a feature to locate unannotated pages is included. Comments and annotations can be exported to CSV, ensuring compatibility with further steps of the analysis pipeline. 

The tool also supports multiple annotators, with the functionality to hide one another's annotations and randomize the tasks' order to avoid priming effects [@shen_unintentional_2019; @mathur_sequence_2017].
 
By integrating these features, Tag-Pag offers a systematic, efficient, and user-friendly approach to web page annotation, addressing the needs of researchers across various disciplines.

# Acknowledgements

This research was funded by the Deutsche Forschungsgemeinschaft (DFG – German Research Foundation) under Germany‘s Excellence Strategy – EXC- 2035/1 – 390681379. The funders had no role in study design, data collection and analysis, decision to publish, or preparation of the manuscript.

# References

