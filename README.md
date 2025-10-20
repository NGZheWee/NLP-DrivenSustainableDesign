# NLP-Driven Sustainable Design

This repository hosts the code, datasets, and documentation for a research project conducted under the **Berkeley Engineering Design Scholars Program** and the **Co-Design Lab** at UC Berkeley.  
The study explores how **Natural Language Processing (NLP)** and data-driven analytics can bridge customer perceptions and sustainable product design by extracting design-relevant insights from large-scale review and certification data.

---

## Overview

The project began in **Summer 2024** through the [Berkeley Engineering Design Scholars Program](https://jacobsinstitute.berkeley.edu/news/meet-the-2024-berkeley-engineering-design-scholars/) and continued through **Fall 2024 – Spring 2025** at the [Co-Design Lab](https://codesign.berkeley.edu/team/derrick-ng/).  
Our goal was to understand how consumers interpret sustainability information and how these insights can guide sustainable product development and certification strategies.  
This work culminated in a **peer-reviewed publication** at *ASME IDETC-CIE 2025 (Anaheim, CA)* —  
*“Data-Driven Sustainable Design Opportunities from Automated User Insights” (IDETC2025-169019).*

---

## Methodology

1. **Data Collection**  
   - Compiled over **23 000 Amazon reviews** across **290 sustainability-certified products** using automated web-scraping pipelines built with `DrissionPage`, `BeautifulSoup`, and structured CSV workflows.  
   - Focused on certifications such as **Energy Star**, **Fair Trade**, and **FSC** to ensure environmental and social relevance.

2. **Data Pre-Processing**  
   - Cleaned, tokenized, and mapped reviews to product features and certification tags.  
   - Filtered noise, standardized sentiment scales, and aligned text segments with affordance-related descriptors (e.g., durability, packaging, energy use).

3. **NLP Analysis**  
   - Applied **Aspect-Based Sentiment Analysis (ABSA)** using **BERT**, **VADER**, and the **OpenAI API** for fine-grained sentiment extraction.  
   - Conducted **topic modeling** via **LDA** and **NMF** to uncover latent sustainability themes and user concerns.  
   - Performed **correlation and clustering analyses** to link sentiment polarity and thematic relevance to certification attributes, revealing perception gaps between consumer priorities and certification focus.

4. **Validation & Synthesis**  
   - Constructed correlation matrices and co-occurrence networks connecting consumer sentiment, product affordances, and certification data.  
   - Compared **LLM-generated design opportunities** against manually derived insights, demonstrating that the NLP pipeline can scale sustainable-design ideation beyond human-coded analyses.

---

## Key Findings

- Certifications emphasizing **visible, experiential product features** (e.g., packaging, durability, ergonomics) correlate with positive sentiment, while **upstream sustainability claims** (e.g., supply-chain ethics) receive less engagement.  
- The integrated **ABSA + Topic-Modeling + LLM** pipeline effectively automates the extraction of design-relevant sustainability signals from unstructured user data.  
- Results demonstrate a scalable, repeatable framework to inform **eco-conscious product redesign**, **certification alignment**, and **consumer communication strategies**.

---

## Key Milestones

### **Summer 2024**
1. Developed foundational scraping tools to collect Amazon product and review data tied to sustainability certifications.  
2. Implemented initial NLP analyses including **ABSA (BERT & VADER)** and **topic modeling (LDA)**.  
3. Presented preliminary results at the **Berkeley Engineering Design Scholars Final Poster Session**.  
   [View Poster](https://github.com/NGZheWee/NLP-DrivenSustainableDesign/blob/main/Summer%202024%20(Engineering%20Design%20Scholar%20Program)/NLP%20Driven%20Sustainable%20Design_Derrick.pdf)

### **Fall 2024**
1. Expanded the dataset to include product categories, features, and affordances for deeper cross-analysis.  
2. Enhanced **ABSA** with **OpenAI API** integration and introduced **NMF** for complementary topic modeling.  
3. Conducted correlation analyses linking sentiment, affordances, and certification metadata to uncover perception gaps.

### **Spring 2025**
1. Finalized multimodal analysis and validated NLP pipeline outputs against manual coding for reliability.  
2. Synthesized insights into an interpretable framework for sustainable product redesign.  
3. Co-authored and published the paper *“Data-Driven Sustainable Design Opportunities from Automated User Insights”* in *ASME IDETC-CIE 2025* (Anaheim, CA).

---

## Publication

**Goridkov, N., Ng, Z. W., Chen, F., & Goucher-Lambert, K. (2025).**  
*Data-Driven Sustainable Design Opportunities from Automated User Insights.*  
*Proceedings of the ASME IDETC-CIE 2025*, Anaheim, CA — Paper IDETC2025-169019.  
[Read the Paper](https://codesign.berkeley.edu/papers/goridkov-reviews-idetc/)

---

## Acknowledgments

This research was supervised by **Dr. Kosa Goucher-Lambert** and supported by the **Jacobs Institute for Design Innovation** through the **Berkeley Engineering Design Scholars Program** and the **Co-Design Lab**.
