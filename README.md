# NLP-Driven Sustainable Design

This repository contains the code, datasets, and documentation for a research project conducted as part of the **Berkeley Engineering Design Scholars Program** and continued under the [**Co-Design Lab**](https://codesign.berkeley.edu/team/derrick-ng/) at UC Berkeley. The research leverages **Natural Language Processing (NLP)** techniques to analyze customer reviews and sustainability certifications, extracting insights to inform sustainable product design strategies.

## Overview

The project began in **Summer 2024** as part of the [Berkeley Engineering Design Scholars Program](https://jacobsinstitute.berkeley.edu/news/meet-the-2024-berkeley-engineering-design-scholars/), where foundational tools and methodologies were developed. The research continued in **Fall 2024** under the [Co-Design Lab](https://codesign.berkeley.edu/team/derrick-ng/), refining NLP techniques and expanding datasets to provide actionable insights. This work focuses on bridging the gap between customer perceptions and sustainable product design through data-driven analysis.

## Methodology

1. **Data Collection**:
   - Automated web scraping of product and review data from Amazon using **DrissionPage** and **BeautifulSoup**.
   - Focused on sustainability-certified products to ensure relevance for sustainable design strategies.

2. **Data Preprocessing**:
   - Cleaned, tokenized, and mapped customer reviews to sustainability certifications and product features for structured analysis.

3. **NLP Analysis**:
   - Applied **Aspect-Based Sentiment Analysis (ABSA)** using models like **BERT**, **VADER**, and **OpenAI’s API** for fine-grained sentiment extraction.
   - Conducted **topic modeling** using **Latent Dirichlet Allocation (LDA)** and **Non-Negative Matrix Factorization (NMF)** to identify recurring themes and insights.
   - Incorporated affordance-related keywords to enhance the analysis of product functionality.

4. **Evaluation and Synthesis**:
   - Constructed correlation matrices linking customer sentiments, product affordances, and sustainability certifications.
   - Synthesized actionable insights for sustainable design, forming the basis for a future journal publication.

## Key Milestones

### Summer 2024:
1. Developed foundational web scraping tools to collect Amazon product and review data related to sustainability certifications.
2. Applied initial NLP techniques, including **ABSA** (BERT and VADER) and **topic modeling (LDA)**, to analyze customer sentiments and sustainability themes.
3. Presented findings at the **2024 Berkeley Engineering Design Scholars Final Poster Session**. [View Poster](https://github.com/NGZheWee/NLP-DrivenSustainableDesign/blob/main/Summer%202024%20(Engineering%20Design%20Scholar%20Program)/NLP%20Driven%20Sustainable%20Design_Derrick.pdf)

### Fall 2024:
1. Expanded datasets to include product categories, features, and affordances for deeper analysis.
2. Enhanced NLP models by refining **ABSA** techniques (OpenAI API) and by incorporating **topic modeling (NMF)**.
3. Synthesized findings for journal article preparation.

## Acknowledgments

This research was conducted under the mentorship of **Dr. Kosa Goucher-Lambert** and supported by the **Berkeley Engineering Design Scholars Program** and the **Co-Design Lab**, Jacobs Institute for Design Innovation, UC Berkeley.
