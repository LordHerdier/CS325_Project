# Stage 5 Report: Job Matching with Embeddings

## 1. Introduction

This report walks through the final stage of our project: using embeddings to match a candidate’s resume against a set of scraped job postings. We’ll cover how we grabbed the data, preprocessed it, picked and applied our embedding model, calculated similarity, and—finally—what we learned when we looked at the top 10 matches. Sprinkle in a dash of snark, hold the fluff.

---

## 2. Data Acquisition Method & Challenges Faced

* **What I wanted to do:** Tap a first-party API from LinkedIn or Indeed like a civilized developer.
* **Reality check:** Those APIs are either locked down tighter than Fort Knox or require you to be an Approved Vendor™. RapidAPI third-party aggregators? Same story.
* **Workaround:** I used [Jobspy](https://github.com/cullenwatson/jobspy), a Python library that scrapes multiple job boards, has proxy support, and still gets updates now and then.
* **Scope limit:** Focused only on Indeed, since their IP-ban filters are less trigger-happy than LinkedIn or Glassdoor.
* **Key hiccup:** I almost over-engineered a fancy UI and extra features that nobody asked for—had to scrap that branch and reorient back to the spec.

---

## 3. Preprocessing Steps

1. **Column pruning:** Dropped irrelevant fields (company URLs, logos, employee counts, etc.).
2. **Normalization:** Converted all text to lowercase, stripped escape sequences and special characters.
3. **Deduplication:** Checked for and removed duplicate postings.
4. **Cost control:** Kept the text lean to avoid burning through LLM API credits on fluff.

---

## 4. Embedding Model Selection

* **Model:** OpenAI’s `text-embedding-3-small`.
* **Reasoning:**

  * Familiarity with the OpenAI Python SDK.
  * Wanted to keep API costs from climbing faster than my caffeine bill.
  * Compared to the “large” variant, the small model was “good enough” for proof-of-concept.

---

## 5. Similarity Calculation

* **Technique:** Cosine similarity between the resume vector and each job posting vector.
* **Workflow:**

  1. Pass the resume through an LLM extraction prompt to pull out key skills and years of experience.
  2. Embed those extracted elements.
  3. Compute cosine similarity via standard vector math.

---

## 6. Top 10 Job Postings & Similarity Scores

| Rank | Job Title                              | Company           | Location         | Similarity |
| :--: | :------------------------------------- | :---------------- | :--------------- | :--------: |
|   1  | Salesforce Developer                   | Kobie Marketing   | St Louis, MO, US |   0.4443   |
|   2  | HRIS Analyst II                        | Core Main         | St Louis, MO, US |   0.4422   |
|   3  | Account Manager                        | Freespace         | St Louis, MO, US |   0.4319   |
|   4  | Scrum Master                           | Stifel            | St Louis, MO, US |   0.4288   |
|   5  | Care Coordinator – Pathways to Success | Centerstone       | Alton, IL, US    |   0.4281   |
|   6  | Director, Internal Communications      | Maritz            | Fenton, MO, US   |   0.4276   |
|   7  | Analyst II, Corporate Development      | Spire Energy      | St Louis, MO, US |   0.4266   |
|   8  | VP of National Operations Service      | ArchKey Solutions | Fenton, MO, US   |   0.4266   |
|   9  | Registered Nurse (RN)                  | Exceed LLC        | St Louis, MO, US |   0.4261   |
|  10  | Summer 2026 Talent Acquisition Intern  | Keeley Companies  | St Louis, MO, US |   0.4250   |

*Based on a database of 699 scraped Indeed postings.*

---

## 7. Analysis of Results

* **So… do these make sense?**

  * A few hits feel on point (Salesforce Developer, Scrum Master).
  * But most fall below 0.45, which is barely “meh” on the –1 to 1 scale.
  * And let’s be honest: RN? Director of Comms? That’s a stretch.
* **Strengths:**

  * Pipeline is functional end-to-end.
  * Cosine similarity is quick and well-understood.
* **Weaknesses:**

  * **Database size:** 699 jobs is peanuts compared to thousands available.
  * **Extraction loss:** The multi-stage LLM extraction may be throwing away context.
  * **Model limitations:** Single, “small” embedding model might gloss over nuance.

---

## 8. Possible Improvements & Future Work

* **Title-focused scraping:** Let the LLM suggest likely job titles, then scrape only those—no more shotgun approach.
* **Dual-model comparison:** Run both small and large embedding models (or a competitor like Cohere) to see which yields tighter matches.
* **API shift:** Migrate to an officially supported jobs API if/when one becomes available.
* **UI upgrade:** Build a lean web interface to let users filter and browse matches without diving into code.
* **Code refactoring & comments:** Clean up technical debt, add inline comments, and enforce linting.

