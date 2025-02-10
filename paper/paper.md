---
title: 'Tag-Pag: A Dedicated Tool for Systematic Web Page Annotations'
tags:
  - Paper
authors:
  - name: Anton Pogrebnjak
    equal-contrib: true
    orcid: 0009-0004-1219-337X
    affiliation: 1
  - name: Julian Schelb
    equal-contrib: true
    orcid: 0000-0000-0000-0000 # TODO: Add this
    affiliation: 1
  - name: Andreas Spitz
    equal-contrib: true
    orcid: 0000-0002-5282-6133
    affiliation: 1
  - name: Celina Kacperski
    equal-contrib: true
    orcid: 0000-0002-8844-5164
    affiliation: 2
  - name: Roberto Ulloa
    orcid: 0000-0002-9870-5505
    equal-contrib: true
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

<!-- possible names Tagweb|WebAnnotator|Tagpag|Tag-Pag  -->

Tag-Pag is an application designed to simplify the categorization of web pages, a task increasingly common for researchers who scrape webpages to analyze individuals' browsing patterns or train machine learning classifiers. Unlike existing tools that focus on annotating sections of text, Tag-Pag systematizes broad-level annotations, allowing users to determine whether an entire document relates to a particular topic. It offers an intuitive interface that integrates the experiences of several research projects into a ready-to-use tool with broad applications.

Tag-Pag allows for configuring web pages and labels, integrating libraries to extract clean and raw content from the HTML and URL indicators that aid the annotation process. It provides direct access to both scraped and live version of the webpage. Our tool is designed to enhance the annotation process through features like quick navigation, label assignment, and export functionality, making it a versatile and efficient tool for various research applications.


# Statement of need


The annotation of web data is increasingly common across multiple disciplines, serving purposes such as analyzing online behavioral patterns [@stier_populist_2020; @guess_almost_2021; @ulloa_search_2023, @flaxman_filter_2016], auditing the performance of online platforms [@makhortykh_how_2020], or training and evaluating machine learning classifiers [@schelb_assessing_2024]. As researchers collect vast amounts of web data, the need for systematic and efficient tools to annotate and categorize this content becomes critical.

Existing tools often focus on annotating specific sections within a text [@rampin_taguette_2021; @meister_tact_2023; huang_rqda_2016], where the user selects a portion of text and assigns a label or establishes connections between parts of speech [@strippel_brat_2022].These tools fall short when the goal is to annotate entire pages to determine, for example, if the content corresponds to very specific topics [@schelb_assessing_2024], misinformation [@urman_where_2022], or, more broadly, political content [@stier_populist_2020; @guess_almost_2021], news articles [flaxman_filter_2016; @ulloa_search_2023] or pages that restrict access such as logins [@dahlke_quantifying_2023]. Tag-Pag addresses this gap by allowing broad-level annotations of entire web pages, offering a dedicated solution for a straightforward need that integrates previous research experiences.

Researchers typically obtain web content by scraping it from dedicated servers. Despite its limitations related to the use of external environments that do not reflect individuals' computers [@ulloa_insitu_2024] and changes due to time delays in the scraping [@ulloa_insitu_2024; @dahlke_quantifying_2023], we argue that systematically scraping the content is the best alternative as it can be done closest to the time in which the individual visited the content and the delays can be uniformly distributed across visits by ensuring consistency. Recently, new tracking tools that collect content directly from an individual's browser have emerged [e.g., @adam_improving_2024], strengthening the argument of prioritizing systematically collected data for annotation purposes instead of encouraging the annotators to gather the content by their means (i.e., visiting the URLs using their browsers).

Despite this, no existing tools facilitate the annotation of such content, leaving researchers to rely on disparate and often inefficient methods. For example, researchers may depend on URL information, manually visit (and revisit) the webpage at different times, or rarely access the HTML content that was systematically collected, as manually locating the content imposes a barrier unless a dedicated tool like Tag-Pag is available.

Tag-Pag integrates the authors' previous experiences with webpage annotations into a single tool. It uses libraries to extract clean [@barbaresi_trafilatura_2021] and raw [@artem_golubin_selectolax_2023] content from HTML, enhancing the annotation process's efficiency. The tool parses URLs, which often contain relevant information about the page's content, adding another layer of contextual data for annotations. Users can easily open the scraped HTML, the live webpage, or the latest version stored in the Wayback Machine, facilitating a comprehensive examination of the content. For researchers creating training datasets, Tag-Pag allows easy text editing to retain only the relevant parts for classifiers, i.e., manually removing boilerplate that filters through the cleaned text, a valuable feature for refining datasets to improve machine learning models.

Additionally, Tag-Pag includes functionality designed to speed up the annotation process: it is flexible and easy to configure, bind key to interfaces actions for rapid label assignment, supports automatic transitions for single-label annotations, and includes features to locate unannotated pages efficiently. The tool also supports multiple annotators, with the functionality to hide other's annotations and randomize the tasks' order to avoid priming effects [@flaxman_filter_2016; @shen; @mathur]. Comments and annotations can be easily exported to CSV, ensuring compatibility with further steps of the analysis pipeline.

By integrating these features, Tag-Pag offers a systematic, efficient, and user-friendly approach to web page annotation, addressing the needs of researchers across various disciplines.


# Citations

Citations to entries in paper.bib should be in [rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html) format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements

This research was funded by the Deutsche Forschungsgemeinschaft (DFG – German Research Foundation) under Germany‘s Excellence Strategy – EXC- 2035/1 – 390681379. The funders had no role in study design, data collection and analysis, decision to publish, or preparation of the manuscript.

# References

