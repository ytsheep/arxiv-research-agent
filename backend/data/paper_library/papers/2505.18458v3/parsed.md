# A Survey of LLM × DATA

## Method

Data
Data4LLM
Object
Storage
Vector
Storage
Graph
Storage
Data
Sampling
Index
Dataverse
Insufficient data
Noisy, Redundant,
or Sensitive Data
Inadequate Data
Composition
Data 
Mixing
Data
Synthesis
pipelines
pipeline
orchestration
training data
inference data
vLLM
Haystack
Langchain
Llamalndex
3FS
LanceDB
relation
data
unstructured
data
origin
data
training
data
model
data
RAG
data
inference
data
K-V
Trafilatura
Sanitization
Ethical, De-identified
& Harm-Free data
Sufficient &
Balanced
Volume of
data
abundance
Logically 
Clear,
InstructionGuided data
articulation
"IaaS" 
Concept of 
LLM Data
Rich, Diverse, MultiDimension Coverage
Inclusiveness
Snowflake
Data Processing
NL2SQL
/ Code
Semantic
Analysis
Prompt
Compression
Data
Provenance
Knowledge
Rerank
Knowledge
Filtering
Fig. 1: Overview of LLM × DATA (with “IaaS” Concept).


# 1
INTRODUCTION
L




## INTRODUCTION

L
arge language models (LLMs1) have made remarkable
progress in both general domain applications (e.g., opendomain question answering [332], cross-modal video summarization [175], general-purpose code generation [191]) and
•
¶ Co-first authors with equal contributions.
1. We use LLMs to refer to billion-scale language models capable of
supporting general NLP tasks [472] or multimodal tasks [444], [322].
specific domain applications (e.g., biomedical literature analysis [394], legal document review [221], SQL generation for
business intelligence [250]). As shown in Figure 1, apart
from technical advances in LLMs [289], [64], [460], [301],
[241], [227], data management has emerged as a critical factor in unlocking LLMs’ full potential in these applications
(DATA4LLM). It includes efficient and scalable solutions
for data processing, storage, and serving across the LLM
lifecycle, as evidenced in recent academic studies [157], [285],
[254] and industry reports [327], [433], [69], [39]. Conversely,

LLM-powered techniques are increasingly being adopted to
enhance data management tasks, such as data manipulation,
analysis, and system optimization (LLM4DATA).
DATA4LLM. Effective data management is fundamental to
the scalable development and deployment of LLMs. To illustrate this, we highlight representative scenarios where LLMs
depend on specialized techniques for data processing, storage,
and serving across various stages of the LLM lifecycle.
Example- 1
⃝Data Processing for LLMs. Processing a
large-scale training dataset (e.g., ∼4 TB multi-modal tokens
utilized in Qwen2.5-VL pretraining [70]) poses several challenges. First, acquiring diverse raw data (e.g., over 10,000
object categories for visual grounding) demands substantial
efforts in data collection (Section 2.3.1) and, in many cases,
data synthesis (Section 2.3.6). Second, preparing high-quality
training samples requires robust pre-processing, including rigorous data filtering (Section 2.3.3), along with dedicated evaluation approaches. Third, the overall performance of LLMs
depends heavily on an end-to-end pipeline that effectively
schedules and coordinates these processing tasks, especially
for the pretraining stage (Section 2.3.7).
Example- 2
⃝Data Storage for LLMs. Managing storage
for LLMs, spanning both training datasets (see Example- 1⃝)
and massive model parameters (e.g., DeepSeek-R1 with 671B
parameters [162]), poses significant challenges. First, largescale datasets must be partitioned and distributed across multiple storage nodes, introducing challenges in data placement
and consistency management (Section 2.4.2). Second, to support efficient LLM training and inference, these storage nodes
must deliver high I/O throughput for timely data transfer
to compute nodes (Section 2.4.4). Third, the massive size of
model parameters increases the risk of training interruptions,
necessitating robust fault tolerance mechanisms to recover
and resume training from intermediate states (Section 2.4.5).
Example– 3
⃝Data Serving for LLMs. Data serving plays
a critical role in selecting and preparing input data (e.g., the
task-specific prompts), directly affecting the quality of LLM’s
responses. Taking retrieval-augmented generation (RAG) as
an example, EyeLevel.ai [37] observed that when relying
solely on vector similarity, RAG accuracy declines notably
with 10,000-page documents, and the performance degradation can reach up to 12% with 100,000 pages (still fewer
than enterprise-scale datasets). Several challenges arise in this
context. First, the retrieved knowledge is typically noisy and
must be filtered and re-ranked to ensure relevance and factual
accuracy (Section 2.5.1). Second, the retrieved content is often
lengthy and exceeds the input capacity or comprehension
of LLMs, necessitating effective compression techniques to
preserve utility while improving performance (Section 2.5.2).
LLM4DATA. Conversely, various LLM-based techniques
can be leveraged to enhance core data management tasks,
including data manipulation, data analysis, and system-level
optimization. The following examples illustrate how LLMs
can be applied to improve these tasks in practice.
Example- 1
⃝LLM-based Data Manipulation. Data manipulation, including cleaning, integration, and discovery, is
critical for ensuring high-quality datasets. Traditional methods depend on rigid rules and domain-specific configurations,
requiring extensive manual efforts and struggling with complex data samples [243], [78], [74]. For instance, standardizing
date formats (e.g., “Fri Jan 1st 10:36:28 2021” vs. “1996.07.10
AD at 15:08:56”) or resolving textual inconsistencies (e.g.,
“Monticello VA, Jasper” vs. “Monticello VAA”) typically
requires intricate programming scripts or handcrafted constraints [319], [432]. These approaches also struggle with
cross-row error detection, such as mismatched city-state-zip
entries. In contrast, LLMs can infer semantic similarities and
autonomously generate cleaning workflows


# 20 hours to identify promising configurations for a single

TPC-H workload [177]. Moreover, root cause analysis over
anomalies can be error-prone, particularly in multi-cause
scenarios where metrics are highly interdependent [490]. In
contrast, LLMs offer a new paradigm by integrating domain
knowledge (e.g., tuning manuals) and applying advanced
reasoning to instruct optimization. By leveraging retrievalaugmented prompts, LLMs can efficiently identify root causes
or recommend precise configurations, enabling faster and
more accurate optimization in complex environments [489],
[248], [223] (Section 3.3).
1.1
Techniques of DATA4LLM
Characteristics of LLM Datasets (§ 2.2). As shown in
Figure 1, datasets (following the “IaaS” concept) play a critical role in enabling the desired capabilities at each LLM stage,
including (1) pre-training, (2) continual pre-training, (3) finetuning, (4) reinforcement learning, (5) retrieval-augmented
generation (RAG), (6) LLM agents, and (7) evaluation. For
each stage, we separately analyze the characters of required
data (e.g., preferred formats and emphasized aspects within
IaaS) and the corresponding data techniques (see Table 1).
Data Processing for LLMs (§ 2.3). We introduce techniques to prepare high-quality datasets for LLMs based on a
2

series of processing steps.
• Data Acquisition. Data acquisition aims to (1) extract relevant data (e.g., text and images) from noisy data sources with
certain structures (e.g., dynamically rendered web pages) [73],
[144], [76], [73], [6], [19], [30], [31], and (2) extract data from
complicated data sources (e.g., scanned or handwritten documents) with techniques such as complex layout analysis [202],
[18], [392], [180], [391], [407], [257], [326], [406].
• Data Deduplication. Data deduplication aims to identify duplicates in large-scale textual or multi-modal data, including
exact string matching
[122], [299], hash identification [88],
[81], [122], [299], [347], [358], [207], [298], sample reweighing
[167] and embedding-based clustering [46], [385], [360].
• Data Filtering. We review data filtering methods at two
primary levels: (1) Sample-level filtering selects high-quality
and diverse samples using strategies like perplexity measuring [383], [61], [288], influence assessment [254], [168],
clustering methods [45], [436], prompt-based scoring [411],
[264], [345], or mixes of these strategies [285], [84], [126]; (2)
Content-level filtering aims to remove undesirable or harmful
content from large-scale datasets, such as toxic language, personal identifiable information (PII), biased statements [268],
[275], and improper images and videos [437], [216], [390].
• Data Selection. Data selection aims to select sub-datasets
and evaluate their ability to accurately represent the target
distribution, especially when handling diverse datasets or
domains. There are methods like similarity-based data selection [423], [421], [321], [80], optimization-based data selection [130], [417], [269], and model-based data selection [465].
• Data Mixing. Data mixing aims to effectively integrate
datasets from diverse domains without degrading quality or
destabilizing LLM performance. Key techniques include: (1)
Heuristic optimization, which empirically tunes data ratios
to enhance downstream performance. Examples include twostage mixing [139], source rebalancing [347], and entropybased weighting [152]; (2) Bilevel optimization, which formulates data weighting as a nested optimization problem
to jointly balance training and validation objectives [302],
[135]; (3) Distributionally robust optimization, which enhances
resilience to worst-case domain shifts by emphasizing underperforming or rare data domains [420], [278]; (4) Modelbased optimization, which builds predictive models to map
data mixing ratios to loss and task performance. Approaches
include linear predictive modeling (e.g., REGMIX [263]),
nonlinear function fitting [152], [439], [160], scaling law-based
estimation [323], and latent source attribution [251].
• Data Synthesis. We introduce data synthesis techniques designed to address the following key challenges: (1) Mitigating
harmful characteristics such as toxicity or bias, which can be
inherited or amplified in synthetic data (e.g., program-aided
verification [496], semantic scoring [173], and multi-agent consistency filtering [346]); (2) Balancing data utility and privacy,
through privacy-preserving synthetic rewriting and key-entity
obfuscation methods during the RAG stage [450]; (3) Generating diverse and logically consistent reasoning data using
approaches like formal proof-based validation [178], Chainof-Thought (CoT) branching and error correction [173], and
high-quality problem synthesis guided by structure and complexity constraints [260], [442]; (4) Automating human-like
evaluation and feedback generation with LLM-based preference modeling [71], judge models for response ranking [476],
and clustering-based diversity quantification [92].
• Data Pipelines. We first introduce frameworks that integrate



## 1.3
Comparison with Existing Surveys

Different from existing LLM and data management surveys [405], [55], [86], [398], [272], [274], [374], [488], our survey
offers a comprehensive and detailed overview of the key intersections between LLMs and data management, highlighting
how they can mutually benefit from each other. We uniquely
position our work at the intersection of data for LLMs (e.g.,
how to acquire, process, store, and serve LLM data) and
LLMs for data (e.g., how LLMs can be leveraged to enhance
data management tasks).
• We propose the IaaS concept as a principled lens to assess LLM dataset quality. The IaaS concept identifies four
essential dimensions, including inclusiveness, abundance, articulation, and sanitization. This concept is promising to
offers an evaluative criteria for guiding data management
and understanding its impact across the LLM development
lifecycle (see Section 2.1).
• We investigate the unique characteristics of data across
different LLM development stages (Figure 2), and provide a
systematic overview of the associated challenges and techniques in data processing, storage, and serving (Table 1). In
contrast, prior surveys [405], [55], [86] primarily center on the
pre-training stage without covering the full LLM lifecycle like
supervised fine-tuning (SFT), retrieval-augmented generation
(RAG), and agent-based applications.
• We provide a lifecycle-based taxonomy of DATA4LLM,
introducing key tasks in data processing, storage, and serving.
For each task, we summarize representative methodologies,
discuss their design principles, and analyze their strengths
and limitations. In comparison, [405] focuses on deduplication
and filtering, [55] emphasizes data selection, and [373] reviews
data annotation strategies, none of which offer a systematic
perspective across the data management pipeline.
• We introduce recent advances in LLM4DATA, outlining key
components of LLM-driven data optimization. While earlier
work [488] has investigated the application of classical machine learning in data management, it largely neglects the
distinctive strengths and limitations of LLMs, particularly
in manipulating data for non-LLM tasks, processing semistructured and unstructured data, and enabling system-level
optimizations.
• We highlight open challenges and future directions from
both ends: (1) improving data management techniques to
meet practical LLM training and deployment needs (e.g.,
efficient data evaluation, scalable multi-modal storage), and
(2) enhancing LLMs’ ability (e.g., private knowledge understanding, informative representation for non-sequential and
non-textual data) to perform complex data management tasks
across diverse real-world scenarios.
5

2
Data Management for LLM (DATA4LLM)
2.1
“IaaS” Concept of LLM Data
Based on our investigation of over 400 papers 2, we introduce
the IaaS concept for evaluating the quality of LLM datasets.
(1) Inclusiveness: LLMs require data with broad and diverse
coverage across multiple dimensions, including domains (e.g.,
general knowledge, specialized fields like finance, medicine,
math [98], and physics [233]), task types (e.g., question answering, summarization, code completion [401], [290], [353],
[45], [436]), data sources (e.g., GitHub, Wikipedia [149], [11],
[330], [347]), languages [93], [347], expression styles (e.g.,
academic, casual, formal [282], [470]), and data modalities
(e.g., text [149], [11], images [145], [185], videos [437], [216],
[390], tables [330]).
(2) abundance: LLMs require data with appropriate volume
and balanced composition to prevent overfitting on homogeneous data. Specifically, abundance of data involves: (i)
constructing well-balanced datasets during pre-training [139],
[302], [420], [263], (ii) adjusting data ratios to align with target applications during fine-tuning [278], [135], and (iii) continually enhancing domain-specific capabilities while maintaining acceptable general performance degradation in continual pre-training [323], [160]. Notably, the strength of LLMs lies
not only in large-scale data [282], [481], [11], [330], [149], [347],
but also in constructing purposefully balanced datasets, which
can further accelerate training and reduce computational cost.
(3) articulation: LLMs require data that exhibit strong articulation, including three key aspects: (i) the data should be wellformatted (e.g., proper punctuation and capitalization [90]),
clean (free from duplicates, typos, and irrelevant content such
as spam or gibberish [90]), and self-contained, featuring clear,
fluent, and unambiguous language [282], [470], (ii) the data
should be instructive [178], [179], [98], i.e., offering sufficient
context, guidance, and intermediate explanations that help
the model connect questions to relevant background knowledge and understand the reasoning process. (iii) the data
should involve step-by-step reasoning[230], [442], [346], [173],
[496], such that enhancing the LLMs’ reasoning capabilities
by decomposing complex tasks into smaller, interpretabl


## 2.2
Data Characters across LLM Stages

Next we specifically discuss the data characteristics across
different LLM stages, together with the distinct techniques
for data processing, storage, and serving (Table 1).
Data for Pretraining. In the pre-training stage, LLMs
rely on TB-scale, diverse datasets to acquire broad language
and even cross-modality understanding capabilities, while
reducing the risk of overfitting. These datasets are typically
sourced from a wide range of domains and formats, including
web crawls (e.g., HTML pages and WARC files [11]), opensource code repositories (e.g., raw source code files with metadata [14]), books (e.g., plain text or EPUB formats [497]), academic papers (e.g., LaTeX source or PDF-converted text [2]),
and interleaved image-text corpora (e.g., aligned captioned
images in JSON or WebDataset format [224]).
Data for Continual Pre-training. Continual pre-training
(or continued pre-training) typically involves datasets containing millions to billions of tokens, which are often over 100
times smaller than those used in the initial pre-training stage.
The primary objective is to fill knowledge gaps and adapt
the model to specific domains. Representative domain-specific
datasets are like: (1) Finance: BBT-FinCorpus [273], a largescale and diverse financial datasets comprising approximately
300 GB of text; and (2) Healthcare: Medical-pt [429], a
Chinese-English medical dataset containing 360,000 entries
curated from medical encyclopedias.
Data for Supervised Fine-Tuning (SFT). Unlike pretraining, SFT relies on data presented in the form of
instruction-response pairs, where the response includes not
only the correct answer but also guidelines on tone, style, and
reasoning steps to ensure user-friendly output.
The SFT stage typically involves much smaller datasets
compared to pre-training. These datasets often consist of
thousands to millions of labeled examples, with each example
carefully crafted to guide the model in learning a specific,
narrower set of tasks. For instance, in Figure 2, (1) the summarization task constructs prompts using problem descriptions
and summarization objects; (2) closed QA using questions and
corresponding knowledge texts; (3) open QA tasks using only
questions without knowledge text; and (4) captioning tasks
using task descriptions and images. These prompts are paired
with unique responses for model finetuning.
The composition of SFT datasets varies based on the
application scenarios:
(1) General Instruction Following: For LLMs as generalpurpose chatbots, SFT data include instructions for various
daily tasks. Databricks-dolly-15K [110] is a corpus containing
over 15,000 records. It encompasses seven types of tasks,
including creative writing, closed QA, open QA, summarization, information extraction, classification, brainstorming.
This dataset is designed to enhance LLM to better adapt to
specialized outputs that align with human-style requirements
across diverse tasks. For example, in text summarization, it
provides concise summary statements; whereas in text organization tasks, it structures outputs in table-of-contents format.
(2) Specific Domain Usage: For models specialized in
fields such as law, finance, or medicine, the SFT data focuses
6

TABLE 1: Technique Comparison - Data Processing, Storage, and Serving Techniques for Different LLM Stages. “N/A”
indicates that no relevant work has been reported yet, although the corresponding techniques could potentially be applied.
Stage
Pre-training /
Incremental Pre-training
Supervised
Fine-Tuning
Reinforcement
Learning
Inference
RAG


## Evaluation

Acquisition
✓
✓
✓
N/A
✓
✓
De-duplication
✓
✓
N/A
N/A
N/A
N/A
Filtering
✓
✓
N/A
N/A
×
N/A
Selection
✓
✓
N/A
N/A
N/A
N/A
Mixing
✓
✓
×
N/A
×
×
Data
Processing
Synthesis
✓
✓
✓
N/A
✓
✓
Distribution
Distributed File System
Model Offload (GPUs, CPUs)
Model Offload
(GPUs, CPUs)
Model Offload
(GPUs, CPUs)
Model Offload
(GPUs, CPUs)
Model Offload
(GPUs, CPUs)
Model Offload
(GPUs, CPUs)
Transmission
Caching Data Placement
Parallelized Pipeline
Data/Operator Offloading (CPUs)
Parallelized Pipeline
Data/Operator Offloading (CPUs)
Parallelized Pipeline
Data/Operator Offloading (CPUs)
×
N/A
N/A
Fault Tolerance
✓
✓
✓
×
×
×
Data
Storage
KV Cache
N/A
N/A
N/A
Cache Space Management
KV Indexing
KV Placement
KV Shrinking
KV Placement
KV Shrinking
N/A
Selection
Sample-Scoring-Based
Model-State-Based
Model-State-Based
Experience-Based
N/A
×
SLM-Based Filtering
LLM-Based Filtering
Metric-Based Re-ranking
LLM-Based Re-ranking
×
Compression
N/A
N/A
N/A
✓
✓
N/A
Packing
✓
✓
✓
×
×
×
Data
Serving
Provenance
×
×
×
✓
N/A
×
Chinese Culture


## Evaluation

Summarization
Translation
Code Classifcation
Code Compilation
Code Synthesis
Automatic Code 
Repair
Code Translation
Closed QA
Open QA
Summarization
Information Extraction
Classification
Creative Writing
Legal Question 
Answering
Public Opinion Summarization
Document Reading 
Comprehension
Similar Cases Matching
Legal Element 
Extraction
Judicial 
Examination
Legal Event 
Detection
Judgement 
Prediction
Legal Case 
Classification
Documents 
Summarization
Alpaca - GPT4 
Corpus
Judgement Prediction
Firefly Model Corpus
Legal Question 
Answering
Law
403K Samples
 Model Size 13B
SFT
Classification
Code
Commonsense
Creative Natural Language 
Generation (NLG)
Grammar
Linguistic
M otion Detection
Named Entity 
Recognition
Natural Language 
Inference
Question Answering 
(QA)
Reasoning
Sentiment
Structured Data
Style Transfer
Toxicity
General
Eval
45K Samples
Law
11.7K Samples
Eval
General
SFT
15K Samples
 Model Size 12B
Brainstorming
Bug Fixes
Testing &  QA
Code 
Development
Misc
Refactoring/ Code Cleanup
Code
59K Samples
SFT
 Model Size 16B
(5k Samples)
Legal Article 
Recommendation
Element Recognition
Named Entity Recognition
Judicial Summarization
Case Recognition
Controversy 
Focus Mining
Similar Case 
Matching
Charge Prediction
Prison Term 
Prediction
Civil Trial Prediction
Legal Question 
Answering
Judicial Reasoning 
Generation
Case Understanding
Legal Consultation
Code
Eval
7.5K Samples
(a)
(b)
(c)
(d)
(e)
(e)
(f)
Fig. 3: Example LLM Data Distributions - (a) General Domain (SFT)[110], (b) General Domain (Eval) [244], (c) Law
(SFT)[447], (d) Law (Eval)[115], (e) Code (SFT) [294], (f) Code (Eval)[208].
on tasks pertinent to these fields. For example, DISC-LawSFT [447] is a legal SFT dataset containing 295k data entries from various legal scenarios, such as legal information
extraction (32k), legal judgment prediction (16k), legal event
detection (27k), and legal question-answering (93k). Similarly,
Medical-SFT [429] is a medical SFT dataset (totaling 2,060k
pieces), composed of medical inquikry data (790k), online
medical encyclopedia QA data (360k), English medical inquiry data (110k), medical knowledge graph QA data (79k).
For tasks such as legal question-answering and legal judgment
prediction, the data is structured as triplets, comprising the
prompt, response, and supporting reference information (e.g.,
legal provisions, case-based evidence, or regulatory documents). For the remaining tasks, they all take the form of
instruction pairs composed of prompt and response.
Data for Reinforcement Learning (RL). RL is generally
divided into two types: one is RLHF (Reinforcement Learning
with Human Feedback), and the other is Reasoning-oriented
Reinforcement Learning (RoRL).
(1) RLHF: RLHF data is typically smaller than SFT data
(e.g., thousands to dozens of millions of data samples), which
involve more complex data annotations. Specifically, annotators compare multiple candidate responses to the same
instruction and rank them according to human preference
(e.g., levels from most helpful to least helpful). Collecting
these preference pairs or rankings is more time-consuming
than constructing instruction-response pairs in SFT.
In the general domain, UltraFeedback [113] consists of
64,000 samples. For each sample, different models are used
to generate 4 responses for each prompt (totaling 256,000
responses). GPT-4 is then employed to generate feedback
for these four responses, which is used to help LLMs to
generate outputs that are in line with human standards and
appropriateness.
In
specific
domains
such
as
healthcare,
MedicalRLHF [429] has 4,000 random questions from a Chinese
medical dialogue dataset. Each question is paired with a wellorganized answer (i.e., the human doctor’s reply) and a weaker
answer from Llama-based model fine-tuned over synthesized
QA samples. These labeled data are used to train a reward
model. During the training of the LLM, the reward model
provides feedback based on the LLM’s answers, guiding the
7

training process towards generating high-quality responses.
(2) RoRL: Compared to the complex annotated data in
RLHF, RoRL allows the model to discover the best reasoning
approach on its own through the correctness of the reward
model. Specifically, it focuses on tasks requiring long-term
reasoning, such as mathematical, coding, and logical designing
experiments [162]. Under the premise of providing feedback
on whether the answer is correct or not, algorithm such as the
Group Relative Policy Optimization (GRPO) [162] and longCoT RL [377] are adopted to train the model to independently
discover the optimal problem-solving steps and converge.
Data for Retrieval-Augmented Generation (RAG).
The RAG stage differs from above training stages, which
involves large-scale dataset (reference corpus) for LLMs to
retrieve from during inference. In this stage, data must be
strictly reviewed to ensure authenticity and validity, while
dynamic data requires real-time updates. The domain of
RAG datasets vari


## Method

Objective
Solution
Tools
Website
Crawling
HTML Textual
Content Extraction
Rule-based
Trafilatura [73]
Rule-based
BET [144]
ML-based
Dragnet [313]
Automate Browser
Interactions
HTML parsing
Beautiful Soup [6]
Control web driver
Selenium [19]
Wrap high-level API
Playwright [30]
DevTools protocol
Puppeteer [31]
Layout-based
Content Extraction
from Handwritten
or Non-text Data
Model pipeline
PaddleOCR
Model pipeline
MinerU [392]
Multimodal LLM
GOT2.0 [407]
Multimodal LLM
Fox [257]
Entity
recognition
& linking
New Sample Derivation
Bi-Transformer
ReFinED [68]
Translation Consistency
Seq2seq Framework
using References
AACTRANS [215]
Text-Image Integration
Multimodal LLM
UMIE [367]
traInteract [446] takes the instruction as the root node, and
uses both the correct actions and their corresponding incorrect actions as nodes to construct a preference trajectory
tree, enabling the agent to learn the human preference of
different actions. Second, other studies focus on enhancing
the agent’s tool usage capabilities using tool usage data. For
instance, AutoTools [351] fine-tunes models on tool data that
is labeled with special tags, such as <python>code</python>,
thereby grounding language in concrete tool invocations.
Third, to enhance the agent’s multi-turn dialogue capability,
UltraChat [117] employs an additional LLM to simulate user
instructions and conversational content, thereby collecting
multi-turn dialogue data.


## 2.3
Data Processing for LLM




## 2.3.1
Data Acquisition

Unlike classic machine learning, which primarily relies on
collecting labeled data within a specific domain for supervised
training (e.g., data for sentiment analysis and sentence similarity estimation), data acquisition for LLMs typically (1)
relies on large-scale web scraping to collect extensive data
across diverse domains for unsupervised pretraining and (2)
employs techniques such as layout analysis and entity linking
to extract additional data from the collected content.
Principles
Unlike classic ML data acquisition, LLMs rely heavily
on large-scale web scraping to ensure broad coverage
and robust generalization. The main challenge is extracting high-quality textual content, often aided by
layout-based and entity-linking methods. Managing
time and resource efficiency at scale remains vital.
Data Sources. The data is gathered from two primary
sources:
(1) Public Data, often freely available under open licenses,
include resources such as webpages [11], books [497], and
publicly accessible code repositories [214].
• Webpage sources provide extensive pre-processed website
content, such as 1.56T english text from crawled websites in
C4 [331], 6.6B multilingual pages in mC4 [431], 6.3 trillion
tokens of multilingual pages in CulturaX [297].
• Digitized books supply structured, high-quality text, such
as over 75,000 eBooks in Project Gutenberg [38], over two


# 8

Data 
Processing
Trafilatura
Dragnet
PaddleOCR

GOT2.0
Fox 
UMIE 
ReFinED 
Web Crawling
Layout Analysis
Entity Linking
1. Data Acquisition
Fast 
Fast
Retrieval
Accurate
Retrieval
Training Stage Requirement
Multiversity
Large Scale
Effectiveness
Low Repetition Rate
Standard Format
Content Safety
Content Privacy
RAG Stage Requirement
Data Serving
Optimizing Sequence
Combination
Data
Selection
Data 
Packing
1. Data Serving For Training
Semantic-Based
Packing
Short Sequence Insertion
Model-StateBased
Experience-Based
Strategies
Sample Scoring
Data Storage
 1. Training Data Storage
Storage
Formats
Distributed
Storage
LLM-native
Formats
Multimodal
Formats
Chain Replication with 
Apportioned Queries
Metadata
Association
Data Chunking
Vector Storage
Indexing
Columnar Storage
Vector 
compression
Graph Storage 
Linear Dimen.
Reduction
PropertyBased
TripleBased
Hierarchical
Aggregation
3. RAG Data Storage
Multi-Model
Support
Table Schema
Semantic
Awareness
Non-Linear Dimen.
Reduction
Asynchronous
Checkpoint
Redundant
Calculation
Fault 
Tolerance
Model Offload (GPUs,CPUs,NVMe Memories)
2. Model Data Storage
Offload
 Chunking-Based 
Space Management
Create Prefix
Index
Shrinking within (between) KV Layers
4. Data Storage For Inference
KV 
Cache
3. Data Serving For RAG
Content
Organization 
Knowledge
 Filtering
Knowledge
Compression
Chunking
Language Model


## Evaluation

Tree Structure
Semantic or
Logical Units
Query-Based dynamic chunking
Knowledge
Re-ranking
LLM-based 
Metric-Based
SLM-based 
LLM-based 
Metric-Based
SLM-Based
Prompt Compression
Covert Markers Embeding
Word Frequency Statistics
Data Provenance
2. Data Serving For Inference
LLM-Based
3. Data Filtering
Model
Scoring
Statistical


## Evaluation

Hybrid


## Evaluation

Content-Level
Sample-Level
  Regular Expression
Prompt-based
Filtering
Perplexity
Prompt-based Scoring
Gradient/Shapley Value
K-means
Metric
Permutation
Metric
Combination
2. Data Deduplication
MD5
SimHash
MinHash
DotHash
Suffix Array
MinHashLSH
SoftDeDup
Bloom Filter
SemDedup 
with Text/Image Encoder
FairDeDup
Insutrction-Response Pair Synthesis
6. Data Synthesis
Pipeline
Distributionally 
Robust Optimization
Empirical
Strategies
Model-based
Mixing
Quality-based 
Two Stage Training
Tweaking 
Data Diversity
5. Data Mixing
Linear
Regression
Ranking 
By Entropy


## Framework

4. Data Selection
Bayesian Similarity
Prompt-based Scoring
Cosine Similarity
Linear Search
Gradient-based Search
Orchestration
7. End-to-End Pipelines
CCNet
DCLM-BASELINE
Data-Juicer
Data-Juicer Sandbox
Dataverse
CC_Cleaner
MDR
LP
Model-specific Pipelines
Inference Stage Requirement
Content
Safety
Content
Privacy
Exact Substring
Matching
Hash
Identification
Embeddingbased Clustering
Frequency 
Analysis
Similarity-Based 
Selection
Optimization-Based
Selection
Lexicon Set Overlap
Bayes-based Selection
Kernel Density Regularization
Model-Based
Selection
 Non-Linear   
  Regression
Knowledge
Distillation
Prompt 
Distillation
Program-Aided
Distillation
Multi-Stage Collaboration KD
Pre-Training
Data Synthesis
Mathematical Data Synthesis
Rephrasing
Synthesis
Cross-Language 
Data Synthesis
Code
Synthesis
Knowledge & QA Pair Synthesis
SFT 
Data Synthesis
Alignment 
Data Synthesis
Reasoning 
Data Synthesis
Fast 
 Data 
Movement
Data Caching
Data/Operator Offloading (CPUs)
Overlapping 
Storage and Computing
Graph-Based
Vectory-Based
Embedding
Fine-Tuned Model Based
Fig. 4: Overview of DATA4LLM Techniques.
million free ebooks in Open Library [28], and film-aigned book
descriptions in BookCorpus [497]).
• Code repositories (e.g., GitHub [14], GitLab [20], Bitbucket [7]) offer abundant programming data that can facilitate code search and analysis tasks, such as CodeSearchNet [181] with 2M (comment, code) pairs.
(2) Private Data involve proprietary or confidential information not publicly available, such as internal company
documents, customer support logs, application event logs,
subscriber-only content (e.g., premium news articles, licensed
scientific databases). Collecting this data requires careful
attention to ethical and legal constraints (e.g., GDPR,
CCPA) and mandates removing sensitive details (e.g., employing anonymization or pseudonymization) and using secure
pipelines (e.g., CI/CD systems) with encryption and rolebased access controls. For instance, proprietary codebases and
user-generated content (chat logs, Q&A sessions) must be
gathered under secure processes to maintain confidentiality.
Data Acquisition Methods. As shown in Table 2, there are
three main techniques for data acquisition, including website
crawling, layout analysis, and entity recognition and linking.
(1) Website Crawling. Most data are obtained through
website crawling, which aims to extract textual content from
crawled HTML files or multimodal image-text pairs using
various extraction tools and browser automation assistants.
Generally, we first parse the raw HTML to separate
meaningful textual content from boilerplate elements. Second,
since typical extraneous components (e.g., headers, footers,
advertisements, sidebars) often contribute little to the data
value (e.g., for LLM training), we execute scripts (using CSS
selectors or XPath queries) to identify and extract critical
elements like article text, headlines, dates, and author bylines.
Third, once the relevant text has been scraped, we store it in
structured format such as JSON, CSV, database (see data
storage in Section 2.4) for further processing. Specifically, for
image elements encountered in HTML files, the image source
URL is recorded, and the content of the alt attribute within
the <img> tag is extracted and utilized as the corresponding
image’s textual caption.
• Rule-based Crawling. Most existing tools use heuristic rulebased matching algorithm. Trafilatura [73] is a heuristic
algorithm based on hand-crafted rules (e.g., match HTML
DOM nodes with the class equal to “navbar” to filter the
navigation bar). BET [144] employs the cumulative HTML
tag distribution to find the largest region of fewest tags per
text and extracts the corresponding text as the main content.
• ML-based Crawling. Since many website regions cannot be
easily classified by rules, some works [76], [73] design a HTML
tag classifier to judge whether a DOM node contains textual
content, where they adopt L2 regularized logistic regression
that inputs text density features and word frequencies in ”id“
and ”class“ attributes and outputs the probability that a given
9

node contains textual useful content.
• Auxiliary Tools. Moreover, some auxiliary tools integrate
user-friendly APIs for operating and interacting with HTML
DOM trees. Beautiful Soup [6] is widely used to parse the
raw HTML in Python. Selenium [19] automates browser
actions and handles dynamic pages by controlling a web
driver that communicates with the browser. Playwright [30]
provides a high-level API to automate browser tasks while
Puppeteer [31] communicates directly with the browser using
the DevTools Protocol, allowing for headless browser interactions (e.g., in JavaScript-heavy websites).
(2) Layout Analysis. Layout analysis focuses on extracting
textual content from handwritten or non-textual data (e.g.,
from the crawled ones), which can contain valuable information and require advanced layout analysis techniques for
effective extraction. Exi


## Method

Objective
Modality
Work
Exact
substring
matching
Deduplicate
samples with
identical substrings
Text
MD5 [122]
Suffix Array [299]
Hashing
identification
Deduplicate
samples with
similar substrings
Text
SimHash [88]
MinHash [81], [122], [299]
MinHashLSH [347], [358]
MinHash +
Bloom Filter [207]
DotHash [298]
Frequency
analysis
Down-weighing
samples with
higher commonness
Text
SoftDeDup [167]
Embeddingbased
clustering
Deduplicate
samples with
identical topics but
different formats
Text +
Image
SemDeDup [46]
SemDeDup +
SSL Prototypes[385]
FairDeDup [360]
(DS) to extract 4.8M triples, where each triple consists of a
subject, a relationship, and an object.
Furthermore, to ensure the consistency of derived and
origin samples (e.g., translation across English and other
languages), Alignment-Augmented Consistent Translation
(AACTRANS) model [215] uses a Seq2Seq framework that
incorporates reference text in the target language to guide
translations, ensuring consistency across related pieces of
text. During training, aligned text pairs are augmented with
reference-based word alignments to bias the model toward
consistent translations. At inference, a common reference
translation of the original sentence is used to align and translate related extractions using the AACTRANS model.
However, AACTRANS fails to leverage shared knowledge
across tasks, limiting the alignment performance. Instead,
UMIE [367] integrates text and visual inputs and produces
structured outputs to learn linking knowledge from multiple
tasks. The UMIE model is composed of four modules: (1)
a text encoder for task instruction comprehension, (2) a
visual encoder for image understanding, (3) a gated attention
mechanism for cross-modal integration, and (4) a text decoder
for structured output generation. Following different task
instructors, UMIE is capable of performing various MIE tasks
and generating corresponding structured outputs, thereby
facilitating knowledge sharing.
Notably, recent LLMs could automatically learn the relationships among samples from randomly provided data, rendering the explicit entity linking an optional procedure in the
data acquisition process [119].


## 2.3.2
Data Deduplication

The collected raw data often contains significant redundancy,
which can negatively impact LLM performance either by
reducing its generalization ability to new or rarely-seen tasks
[299] or by memorizing and overfitting to the repeated subsets [169], [422]. Various deduplication methods have been
proposed to detect and mitigate duplication, either by (1)
completely removing duplicate samples [122], [299], [347],
[358], [207], [46], [385], [360] or by (2) down-weighing duplicate
samples for data resampling [167]. We classify these methods
into four main categories.
Exact Substring Matching. Exact substring matching
methods identify and remove exactly identical samples across
datasets, which can happen if (1) a sample references another
sample (e.g., a report related to another), or (2) two individual
datasets accidentally include the same sample (e.g., a webpage
10

of a popular website). It is commonly used as a preliminary
step to remove duplications. Relevant methods leverage techniques like hashing [122] and suffix array [299] at the sample
or sentence level.
Principles
Compared to structured classic ML data, LLM data
is unstructured and requires careful identification and
removal of duplicate or near-duplicate content from
training datasets to improve efficiency, prevent overfitting, and mitigate bias using statistical metrics like
perplexity or model evaluation. Challenges include (1)
how to encode semantic texts into representations that
could be precisely and efficiently compared and (2) the
scalability of the deduplication methods.
• Sample-Level. [122] conducts sample-level deduplication
by calculating the MD5 hashing value of each sample and
deduplicate samples with identical MD5 values.
• Sentence-Level. [299] performs sentence-level deduplication
by using Suffix Array, which combines all the samples into
one sentence, computes the sentence Suffix Array, and deduplicates samples with common prefixes in the Suffix Array.
Suffix Array [283] is a data structure that stores the starting
indices of string suffixes in lexicographical order. For instance,
given the string “patata”, its suffixes in lexicographical order
are [“a” (index 5), “ata” (index 3), “atata” (index 1), “patata”
(index 0), “ta” (index 4), “tata” (index 2)], so its suffix array
is (5, 3, 1, 0, 4, 2). As identically duplicate samples have the
same prefix, they will become adjacent in the suffix array,
making it easier to find the duplicates across the samples. In
practice, they construct a suffix array on the sequence with
a threshold of 50 tokens (empirically determined for significantly reducing the false positives), and find the duplicate
samples with common prefixes in linear time.
Approximate Hashing-based Deduplication. Hashingbased methods hash each sample into a fixed-length vector
and deduplicate samples with significant vector overlap. Compared with the exact matching-based approach, it can identify
near-duplicate samples with only a few words of difference
(e.g., advertisements generated using the same template).
Unlike normal hashing algorithms like MD5, hashes generated
in this approach do not change significantly with even a bit of
modification, making it possible to detect near-duplicate samples. There are various hashing algorithms, including SimHash
[88], MinHash [81], DotHash [298], and their variants [347],
[358].
• MinHash [81] hashes samples into vectors using a series of
hashing functions, where only the minimum value is retained
for each function, and estimates similarity for each pair of
vectors through Jaccard Index Jaccard(X, Y ) = X∩Y
X∪Y , where
X and Y represent sets of elements (For example, if X = a,
b, c, d and Y = b, c, d, e, f, the Jaccard Index over X and
Y would be 1
2). [356] demonstrates that MinHash generally
outperforms SimHash. In practice, [122] employed MinHash
to the code data on both the sample and the repository levels
for diversity and integrity, and [299] employed MinHash on
the sample level.
Moreover, MinHash has various variants for acceleration.
MinHashLSH [347], [358] improves MinHash by involving
locality-sensitive hashing (LSH), which divides a vector into
multiple bands and only compares the samples with partially
identical vector bands instead of the whole vector, mitigating the computational overhead in sample comparison. LSHBloom [207] further improves MinHashLSH by using Bloom
Filter, which hashes each band into a single integer value and
inserting it into each corresponding Bloom Filter, and the
sample will be flagged as a duplicate if any band’s hashed
value collides with an entry in the Bloom filter, accelerating
duplicate samples searching while reducing memory usage
with negligible false positive rate (e.g., 1e-5 in experiments).
However, MinHash-based methods require building massive vector sets. When the number of samples and their
lengths grow large, constructing vector sets becomes exceedingly expensive in terms of both time and space. Moreover,
as the feature vector c


# 11

of each sample by multiplying the frequencies of all the n-

grams that appear in the document. Samples with higher
commonness are more likely to be duplicates and thus be
down-weighted.
Embedding-Based Clustering. Except for samples with
the same or similar substrings, some samples with similar
semantics but different formats (i.e, expressed differently)
may also negatively affect LLM training performance. For
instance, for the following two sentences: (i) “Unleash your
potential with our lightweight, high-performance sports shoes –
designed for comfort, speed, and style”; (ii) “Step into greatness with durable, breathable sports shoes perfect for running,
training, and everyday adventures”. Both of the sentences are
sports shoe advertisements but expressed differently, and such
duplicates could degenerate model performance by making
data imbalanced and introducing bias to the model. To address this issue, another approach leverages language models’
embeddings (representing similar items as vectors close to
each other in the vector space) for deduplication.
SemDeDup [46] identifies semantic duplicates by clustering embeddings and deduplicating those with high cosine
similarities. It first encodes each sample into an embedding
by leveraging the OPT [462] text encoder and the CLIP [325],
[182] image encoder, and clusters the embeddings with Kmeans, so one can save time by finding duplicates within the
cluster rather than the whole vector space. Then, within each
cluster, it searches for semantic duplicates with cosine similarity above the pre-defined threshold. Finally, within each group
of duplicates, it retains only the sample closest to the cluster
centroid. As a multi-modal method, it can be applied to both
text and image data, making it possible to deduplicate image
data. In practice, [45] leverages SemDeDup to deduplicate the
image-text pair dataset LAION-400M [341].
Like MinHash, SemDeDup also has many variants for
performance improvement. [385] combines SemDeDup with
the Self-Supervised Learning (SSL) Prototypes metric, which
clusters the samples and retains the samples in each cluster based on their distance to their corresponding cluster
centroid, where the samples closer to the centroid are more
likely to be removed. FairDeDup [360] modifies the logic of
SemDeDup to improve the representation of underrepresented
sensitive groups by prioritizing the retention of samples that
align with sensitive concepts defined through user-provided
prototypes, such as demographic subgroups. Within each
cluster, instead of selecting the farthest sample from the
centroid, it selects the sample that maximizes similarity to
the least-represented group in the cluster to prevent samples
with sensitive concepts from being pruned.
Non-Text Data Deduplication. As LLMs are increasingly
applied to multimodal tasks (e.g., image-text retrieval, visual
question answering), non-text data types such as images
are becoming integral to LLM training datasets, necessitating dedicated deduplication techniques. Similar to texts,
images can also be encoded into embeddings through neural
networks designed for image-like data such as CNN, after
which embedding-based deduplication methods can be applied. SemDedup [46] adopts a semantic-based method by
computing cosine similarity between image embeddings; two
images are considered duplicates if their similarity exceeds
a predefined threshold, which is tuned to balance detection
TABLE 4: Data Filtering Methods for LLMs.
Category
Objective
Methods
Samplelevel
Filtering
Remove
low-quality
samples
Perplexity Measuring [383], [61], [288], [239], [238]
Influence Assessment [254], [168]
Clustering [45], [436]
Model Scoring [411], [264], [345]
Mixed Methods [285], [84], [126]
Contentlevel
Filtering
Remove
partial-noising
samples
Privacy Anonymization [275], [268]
Image & Video Filtering [437], [216], [390]
IFD >
Threshold?
Yes
Enhance
Score
Scorer
Enhance the samples
A
Estimate
IFD Score
Perplexity-based Data Filtering
Perplexity
B
Clustering-based Data Filtering
Encode to
Embedding
Clusters
C
Prompting-based Data Filtering
Prune by
Cluster
Complexity
Complexity
IFD =
0.8
IFD =
0.4
IFD =


## 0.7
No
Previous tokens
Next token
IFD Score
Average Inter-
cluster Distance

Average Intracluster Distance
Original
Dataset
Filtered
Dataset
Score the (enhanced) samples
Train
High
Low
Original Dataset
Filtered Dataset
Removed Dataset
Original Dataset
Removed Dataset
Filtered Dataset
Original Sample
Enhanced Samples
Scores
Score
Fig. 5: Example Data Filtering Workflows [238], [45], [264].
precision and recall. In contrast, MINT-1T employs a hashbased approach, using SHA256 checksums to identify and
remove exact duplicates efficiently. Meanwhile, the DataComp
pipeline [146] leverages the CNN-based near-duplicate detector [445] to eliminate subtle duplicates and prevent evaluation
set leakage. Models trained on these deduplicated image
sets exhibit improved performance over baselines such as
CLIP [325] for higher precision and recall.


## 2.3.3
Data Filtering
Data filtering removes low-quality or sensitive samples from

the dataset to reduce computational overhead and protect
privacy, while the model trained on the subset exhibits similar or even better performance than the one trained on
the original dataset. To achieve this, one has to (i) remove
samples with low quality (Sample-level filtering) or partial
noisy information (Content-level filtering), and (ii) keep the
selected samples diverse enough to cover various domains.
Sample-level Filtering refers to evaluating samples using
metrics or models and removing the samples that fail to meet
the threshold (e.g., quality and diversity). There are multiple
metrics in this category:


# 12

Principles

Compared to classic ML data filtering, LLM data
filtering emphasizes turning unstructured text into
measurable metrics, with the main challenge being the
effectiveness of evaluation methods, the standards of
low-quality samples, and the computational complexity of these methods across massive datasets.
(1) Statistical Evaluation uses various statistical methods
to evaluate samples by directly applying statistical metrics to
the samples (e.g., clustering results) or indirectly capturing
characteristics from the models trained on the dataset (e.g.,
loss or perplexity from a surrogate model). Applicable statistical metrics include perplexity (and its variants), influence on
model parameters, and clustering.
• Perplexity Measuring. Perplexity measures the difficulty of
a model generating the responses, represented as aggregated
probabilities of the j-th response token given the question
tokens and previous j −1 response tokens PPL(y|x) =
exp

−1
N
PN
j=1 log p(yj|x, y1, ..., yj−1)

. The higher the perplexity value is, the harder the model generates the response.
It is commonly used in selecting high-quality subsets in pretraining and fine-tuning phases. Based on the original perplexity, there have been several studies for improving the metric,
including computing perplexities using a smaller-sized model
for training a larger-sized model to reduce computational
overhead, or employing advanced techniques such as Learning
Percentage (LP) and Instruction-Following Difficulty (IFD)
to identify and select challenging samples.
Specifically, [383] uses an existing model to compute
perplexity scores for multiple domains and selects pretraining samples from the domains with high correlation
between the downstream benchmark error and the perplexity
scores on the domain samples. The correlation is measured
through a rank-based correlation coefficient γj = P sign(yk −
yl)(rankj(xk,j) −rankj(xl,j)), where the rank difference reflects the model performance difference on the same sample,
helpful in estimating θ∗. They then rank the domains based on
γj and select samples from the top-ranked domains. To scale
the process, a fastText classifier [199] is trained to distinguish
selected documents, enabling page-level data selection.
To enhance efficiency, [61] leverages a smaller-sized surrogate model to select high-quality pre-training subsets via perplexity score for training larger-sized models, greatly reducing
the computational overhead in model training while still
achieving the same performance as with the full dataset. They
first train a surrogate model, a smaller-sized MosaicML [378]
model with 125 million parameters, on a random subset of the
pre-training dataset to compute the perplexity scores for the
remaining samples. Based on the perplexity scores, they find
the optimal subset through a combination of selection criteria:
(i) the part of samples to keep (e.g., samples with low/medium/high perplexity scores), and (ii) the fraction of samples
to keep (e.g., 25%, 50%, 75%). The subset is evaluated by
training a larger-sized MosaicML model on it and analyzing
the model’s performance on downstream benchmarks. While
the result shows that the smaller-sized model can effectively
and efficiently filter data for the larger-sized model, they also
find that the effectiveness highly depends on the dataset.
For example, keeping the high perplexity samples exhibits
better performance on the Pile dataset [149], while keeping
the medium perplexity samples exhibits better performance
on the Dolma dataset [361].
Furthermore, there are some variants of perplexity-based
evaluation. First, [288] proposes a perplexity-based metric, Learning Percentage (LP), to select samples that are
more challenging for models to learn. Learning Percentage
LP(i) =
Pi−1−Pi
P0−Pn
measures the perplexity drop ratio of a
sample between the specific epoch i and the whole training
procedure. The key idea is that models tend to learn easier
samples first and harder samples later, so one can find harder
samples that are not thoroughly learned during early epochs.
The authors use LP(1) (the learning percentage after the first
epoch) to rank the training samples from the hardest to the
easiest and split them into three equal-sized parts. It shows
that the smaller-sized variant of the model can effectively
select samples for the larger-sized variant, and models of all
sizes trained on the harder part outperform the ones trained
on all the samples.
Also based on perplexity, [239] proposes the InstructionFollowing Difficulty (IFD) metric to select samples that are
more difficult for models to follow. IFD (IFDθ(Q, A) =
P P L(A|Q)
P P L(A) ) measures the influence of the questions (instructions and inputs combined) on generating corresponding responses by comparing the perplexity of the response with
or without the question strings PPL(A|Q) and PPL(A). A
higher IFD score suggests higher model following difficulty.
The authors first build a pre-experienced subset by cl


# 1
n
P
i

1
n∇θL(si, ˆθ)TH−1
ˆθ ∇θL(s, ˆθ); (ii) Effort Score for as-


# 13

sessing the difficulty for the surrogate model to learn a

specific sample for generalization to new samples, defined
as δs = ∥∇ϕLLLM(s)∥2, where Φ is the model parameter. A higher effort score suggests greater difficulty. The
final score combines the above two scores, written as Is =
Influence Score + λ · Effort Score.
Besides, SHED [168] utilizes the Shapley value [339], which
estimates the contribution of a member to the group, to
calculate the influence of a sample on the model performance
and select representative samples with high influence. The
method first clusters the samples and selects the ones closest to each cluster centroid as the representative samples
to reduce computational overhead. It then calculates the
Shapley value for each representative sample i by iteratively
removing n samples from the dataset until all the samples
have been removed and calculating the contribution of the
removed n samples in each iteration a to the model performance compared with the previous iteration, written as:
c(an+1..(a+1)n)∈Dp = v(Dp \ {1..an}) −v(Dp \ {1..(a + 1)n}).
The process will be repeated for k times for higher accuracy,
after which the Shapley value for each representative sample
i is defined as Si ≈


# 1
k
P
k

ci(k)
n . Finally, the subsets can
be selected either by selecting from the top-rank samples
or weighted sampling the samples through Pr(i) =
efSi
P
i efSi ,
where f controls the trade-off between quality and diversity.
• Clustering. A common approach to select high-quality and
diverse subsets is to encode the samples into embeddings
in the latest space and cluster them using cosine similarity,
where similar samples are usually clustered into the same
group. Selecting within the clusters reduces redundancy, while
selecting across the clusters increases diversity.
Density-Based Pruning (DBP) [45] selects high-quality
and diverse subsets by clustering samples into clusters and
resampling the samples based on the cluster complexity. They
encode the samples into embeddings using a pre-trained vision model DINOV2-L/14 [300] and cluster them using Kmeans. For each cluster, they calculate the average intracluster cosine-distance to the internal centroid dintra and
inter-cluster cosine distance to the other centroids dinter,
and the cluster complexity as a product of the two distances
C = dintra × dinter. The cluster complexity is later converted
to probability using softmax to resample the samples across
clusters, where clusters with higher complexity have higher
weights.
Rather than the sample embedding itself, SmallToLarge [436] selects a diverse subset by clustering the samples
based on their loss trajectories. It first trains a smaller-sized
surrogate LLM model on the whole dataset to obtain the loss
trajectories of each training sample, defined as Li(ϕ(t)) =
−log pϕ(t)(yi|xi), where ϕ(t) is the model parameters at time
t. These samples are then clustered based on loss trajectories
and randomly resampled to form a diverse subset.
(2) Model Scoring uses LLMs for evaluating sample quality. The quality criteria can either be specified (i) explicitly
via LLM prompt engineering or (ii) implicitly learned from
human-labeled data.
QuRating [411] selects high-quality pre-training samples
by prompting LLM to compare pairs of samples along the
four quality criteria (writing style, fact & trivia amount,
educational value, and the expertise required to understand),
training a rater on the scalar quality ratings, and filtering
samples using the rater. Initially, GPT-3.5-turbo is prompted
on each pair of samples to judge which one is better on each
quality criterion, where the binary confidence pB≻A ∈[0, 1]
that the sample B is preferred over the sample A is recorded.
The pairwise binary confidence is then translated into sample
quality ratings pB≻A = σ(sB −sA) through the BradleyTerry model. A QuRater model is later trained on these
quality ratings to predict quality ratings for new samples
on each criterion. The new samples are resampled with the
probability p(di) ∝exp   si
τ

, where τ adjusts the trade-off
between quality and diversity.
Rather than prompting the models to compare samples,
Data-Efficient Instruction Tuning for Alignment (DEITA)
[264] prompts LLM models to evolve and score the samples
for building sample scorers. The authors first prompt ChatGPT to evolve the samples along instruction complexity and
response quality, and again prompt ChatGPT to score these
evolved samples. They then train scorers on the evolved samples with their corresponding scores to enable their scoring
abilities. Finally, they use these scorers to score new samples
and multiply the scores to form the final score, where the new
samples are resampled based on the final scores for diversity.
Model scoring methods also help mitigate bias and toxicity. LLM often exhibit harmful biases due to the massive
and unchecked datasets they are trained on, which can have
various biases, ranging from gender and racial stereotypes to
cultural and socioeconomic prejudices [296]. Safety-enhanced
Aligned LLM Fine-tuning (SEAL) [345] selects high-quality
and safe fine-tuning samples through a safety-aligned selector. The selector is trained based on a safety-aligned model,
Merlinite-7b [366], using bi-level optimization, which minimizes the safety loss on the safe dataset while minimizing
the fine-tuning loss on the filtered dataset during training to
ensure the selector always prioritizes safe and high-quality
samples during selection. After the selection, the top-p%
samples will be selected.
(3) Hybrid Methods. Instead of relying on a single method,
some methods mix various kinds of data filtering methods and
evaluate each permutation of these methods or parameters
to find the best combination of methods or parameters that
further boosts model performance.
[285] selects high-quality pre-training data based on three
metrics: (i) Perplexity, (ii) EL2N χ(xi, yi) = E∥f(xi) −yi∥2
for measuring the prediction probability discrepancy between
the reference model and the ground truth, and (iii) Memorization factor score(M, N) =


# 1
N
PN

i 1(zM+i = ˆzM+i) for
measuring the fraction of N tokens correctly generated after
prompting the model with the first M tokens [77]. For each
metric, they retain samples based on two criteria: (i) the
fraction of samples to keep (10%, 30%, 50%, and 70%) and (ii)
the part of samples to keep, e.g., the bottom (for Perplexity
and L2-Norm Error) and top (for Memorization). They train
LLM for each case and select the best-performing one, and the
result shows that Perplexity effectively removes the “easiest”
samples, improving model performance and outperforming
other metrics.
Instead of comparing metrics and choosing the best of
them, InstructionMining [84] combines various metrics (e.g.,
including input/output length, reward score, perplexity, etc.)
into one linear function with each metric as indicator, written
14

as logLloss ∝L0 + β0 + β1I1 + β2I2 + · · · + βnIn + ϵ. The β
parameters are estimated using least squares. In practice, it
evaluates fine-tuning samples on a fine-tuned model LLaMA2-7B [386] and selects samples by finding the optimal set of
samples to keep using the hyperparameter optimizer BlendSearch [395].
MoDS [126] considers diversity into selection and iteratively selects high-quality, diverse, and necessary subsets
and adds the samples the LLM model performs poorly on
during fine-tuning using a reward model and the K-Center
greedy algorithm [342]. The method is conducted mainly in
three steps: (i) Use a reward model to score the quality of
each (instruction, input, output) triplet in the dataset, where
the low-quality ones are filtered out, forming a high-quality
dataset. (ii) Use the K-Center greedy algorithm [342] to select
the samples in the high-quality dataset that are farthest apart
from each other in the BERT [206] embedding space, forming
a diverse seed dataset. (iii) Fine-tune a pre-trained LLM
model on the seed dataset to enable its instruction-following
ability and generate responses for the high-quality dataset.
The generated responses are evaluated using the same reward
model, and those with low quality scores, which means the
model is weak at generating such responses, will be collected.
The collected samples with their original responses will be
selected again using the K-Center greedy algorithm and then
added to the seed dataset, forming the final dataset.
Content-level Filtering. To avoid removing too many critical samples from the dataset and weakening the model performance, some works only filter out noise or sensitive content
within the samples. For noise removal, common methodologies
include removing or replacing specific characters (e.g., remove
invisible or invalid characters, unescape HTML characters and
detect punctuation misuse), removing unnecessary texts (e.g.,
the texts that appear as decorating elements on the web pages
such as “print”, “likes” and “loading” ), and cleaning harmful
information (e.g., spam, gambling, pornographic content and
site links) [433].
For privacy anonymization, LLMs can memorize private and sensitive information (e.g, user identity details
or clinical health data) from datasets during pre-training
and fine-tuning, which can be leaked through specially
crafted prompts, thereby posing significant privacy risks. [275]
demonstrates that it is possible to extract, reconstruct, and infer personally identifiable information (PII) from LLM models by identifying the most frequent PII appearing in model
responses or by prompting models with partial information
about a specific individual. From a data management perspective, these privacy threats can be mitigated by identifying and
filtering out potential sensitive information in the datasets.
DeID-GPT [268] utilizes existing LLMs to identify and
remove PII from unstructured medical text without changing
its meaning. In their case, the LLMs are prompted to deidentify information from clinical notes in accordance with
HIPAA privacy regulations. An example prompt is: “Please
de-identify the following clinical notes by replacing any terms
that could be a name, an address, a date, or an ID with the
term ‘[redacted]’.”
Instead of using general LLMs, [275] uses Named Entity
Recognition (NER) models such as spaCy [33] and Flair [52]
to tag PII in the samples and removes or replaces them with
TABLE 5: Comparison of Different Data Selection Methods.


## Method

Stage
Evaluation Metric
Similarity
Pre-training,
Fine-tuning
Cosine Similarity [423]
Bag-of-Words Similarity [421]
Lexicon Set Overlap [321]
Bayes-based Selection [80]
Optimization
Fine-tuning
Linear Search [130]
Gradient-Influence Search [417]
Kernel-Density Regularization [269]
Model
Pre-training
Logits-based LM-Score [465]
hashed tags, entity tags like “[NAME]” or “[LOCATION]”,
or a simple tag like “[MASK]”. The last tag was adopted to
maximize privacy, as the other ones are still vulnerable to
membership inference by linking the samples.
The rise of multi-modal LLMs, particularly large video
generation models, drives the need for robust video data filtering. CogVideoX [437] employs a pipeline focusing on coherent
motion, removing videos with poor dynamics. It defines negative labels for artificial edits, low motion connectivity, visual
flaws, and excessive text. A manually annotated subset trains
six Video-LLaMA[455]-based filters, while optical flow and
aesthetic scores ensure motion coherence and visual appeal,
refining the dataset to approximately 35M high-quality 6second clips.
HunyuanVideo [216] uses a multi-step pipeline: splitting
videos into clips, encoding embeddings, deduplication, and
resampling. Filters include motion (OpenCV-based optical
flow), OCR (text removal), clarity (visual blur detection), aesthetic (Dover[414]-based scoring), and source (YOLOX[153]-
like watermark/border removal). This process generates five
progressive training sets with increasing thresholds.
Wan [390] applies pre- and post-processing pipelines. Preprocessing filters unsuitable data using OCR, aesthetic evaluation (LAION-5B [341]), NSFW scoring, watermark detection, and resolution thresholds, removing approximately
50% of low-quality data. Samples are clustered for diversity,
manually scored, and an expert model selects high-quality,
naturally distributed data. Videos are classified into six tiers,
prioritizing smooth motion. Post-processing refines images by
selecting top 20% via an expert model and manually curating
gaps. For videos, top candidates are filtered by visual quality
and motion complexity, ensuring balance and diversity across
12 themes.


## 2.3.4
Data Selection

Different from previous reviews [55], [398], we define data
selection as the process of choosing subsets of already wellcleaned data samples in order to adapt LLMs to specific
domains (e.g., medical or legal LLMs).
Principles
Unlike traditional ML data selection, LLM data selection focuses on aligning the topics of the text samples,
requiring encoding semantic topics into measurable
distributions. However, managing computational efficiency and ensuring robust generalization across diverse tasks remain critical unresolved issues.
15

Similarity-based Data Selection. One class of methods
aims to select subsets similar to the specified target data.
• Cosine Similarity: Domain-Adaptive Continual Pre-training
(DACP) [423] adapts a general-purpose LLM to a target task
by selecting domain-specific unlabeled data based on similarity (cosine similarity), novelty (perplexity), and diversity
(entropy). For the similarity part, it identifies data most
similar to the task-specific labeled data by encoding both into
embeddings (using [33]) and choosing domain samples that
align with the task’s embedding distribution.
• Bag-of-Words Similarity: DSIR [421] selects a subset of
unlabeled pre-training data matching the target distribution
by computing feature distributions (ˆpfeat, ˆqfeat) for raw and
target data represented as bag-of-words, estimating importance weights wi =
ˆpfeat(zi)
ˆqfeat(zi), and resampling raw data with
probability
wi
PN
i=1 wi .
• Lexicon Set Overlap: [321] selects the subset with the most
shared lexicons using the Domain Specific Score (DSS), which
quantifies the relevance of a dialogue set T to specific domains
by measuring the overlap between T and domain lexicons L =
{l1, l2, . . . , lm}, calculated as DSS(T, L) =


# 1
m
Pm

i=1
|T ∩li|
n
,
where n is the number of tokens in T.
• Bayes-based Selection: CoLoR-filter [80] formulates pretraining subset selection as a Bayesian optimization problem,
which selects a subset S by maximizing downstream likelihood
Pr(Ddown|S). It uses two auxiliary models: A “prior” model
(θprior) trained on a large general dataset Ddown and a “conditional” model (θprior) fine-tuned on the union of the large general dataset and a small downstream dataset Dprior+down. The
selection criterion for a data point xi is the conditional loss
reduction (CoLoR): CoLoR(xi) = −log Pr(xi|θprior+down) −
(−log Pr(xi|θprior)). The key idea is to score samples based on
the likelihood difference between these two models and select
the ones that exhibit higher likelihood under the conditional
model and larger conditional loss reduction.
Optimization-based Data Selection. Optimization-based
data selection methods select subsets towards reducing model
loss and improving model performance on the target tasks.
• Linear Search. Model-Aware Dataset Selection with Datamodels (DsDm) [130] selects the optimal subset of training
data that minimizes the model’s loss on target tasks by
employing linear datamodel [184], a parameterized function
that maps a subset of training data to the model outputs
for the specified target, to estimate how the inclusion of
each training sample would affect the model’s loss on the
target, reducing computational overhead. In practice, a linear
datamodel τθx(1S) = θ⊤
x 1S with parameters θx and a characteristic vector 1S (a binary vector indicating which samples
are in S) is adopted to map the subset S to the model loss on
a sample x through Lx(S) = E[ℓ(x; A(S))]. For each target,
the characteristic vector 1S is adjusted to reflect the subset,
and the parameters θx are estimated using a regression loss
function like mean squared error over the training subset.
After training, the datamodel selects the subset S of the size
k that minimizes the loss ˆLDtarg(S) = 1
n
Pn
i=1 τθxi (1S) for the
target task.
• Gradient-Influence Search. Low-rank Gradient Similarity
Search (LESS) [417] identifies the most impactful subset
of data for fine-tuning LLMs by analyzing gradient similarities. It first fine-tunes the model on a random subset
(e.g., 5% of data) for a few epochs using LoRA to reduce
trainable parameters and accelerate gradient computation,
and saves the checkpoints after each epoch. Next, LESS
computes Adam LoRA gradients for each training sample,
projects them into lower-dimensional gradient features via
random projection, and stores them in a gradient datastore.
For downstream tasks, it calculates gradient features of fewshot validation samples and estimates the influence of each
training sample z on a validation sample z′ using cosine
similarity: InfAdam(z, z′) ≜PN
i=1 ¯ηi cos(∇ℓ(z′; θi), Γ(z, θi)),
where Γ(z, θ) is the Adam update. The training samples with
the highest influence scores are selected for fine-tuning.
• Kernel-Density Regularization. Task-Specific Data Selection (TSDS) [269] identifies high-quality pre-training or finetuning data for particular tasks by balancing two objectives: (i) distribution alignment with the target task data
and (ii) diversity to avoid near-duplicates, accomplished
via kernel density estimation (KDE) regularization. Concretely, one begins with a small set of target task samples Q
=
{qi}M
i=1
and a large candidate pool D
=
{xj}N
j=1, both of which are embedded into a shared metric space (e.g., using gradient-based or semantic embeddings). The optimization for distribution alignment is conducted by solving for probability mass γij (transported
from qi
to xj): minγ∈RM×N
≥0
α
C
PM
i=1
PN
j=1 γijdij + (1 −
α)GKDE(γ)
s.t.
PN
j=1 γij
=
1
M , ∀i
∈
[M], where dij
is the distance between qi and xj in the metric space,
and GKDE(γ) is the regularization term that adds diversity and penalizes over-density using KDE: GKDE(γ)
=
M maxi,j ρj
γij −
1/ρj
M P
j′ 1/ρj′
, where ρj
=
P
x′∈D(1 −
f(xj, x′)2/h2 is the density estimate for candidate xj (higher
for near-duplicates). Afterwards, it samples xj with probability pj = P
i γ∗
ij.
Model-based Data Selection. These methods aim to determine subsets guided by prompting the LLM itself.
Autonomous Data Selection (AutoDS) [465] prompts
the LLM to assess and select mathematical and educational samples from a larger dataset. For each sample,
the LLM is asked two questions: (i) Is it mathematically relevant, and (ii) It it educationally valuable. The
LLM responds to each question with “Yes” or “No”, and
the logit of each response is extracted to compute the
LM-Score: LM-Score(·) =
exp(logit(‘YES’))
exp(logit(‘YES’))+exp(logit(‘NO’)), and
the composite score: LM-Score(Q1, Q2) = LM-Score(Q1) ·
LM-Score(Q2). The composite score ranks and selects highquality math samples.


## 2.3.5
Data Mixing

Since LLMs rely on massive and diverse datasets, the composition of these datasets significantly impacts model performance [295]. For instance, as shown in Figure 3, we can
see LLMs require different ratios of domain data to achieve
capabilities such as medical diagnosis, coding, and solving
math problems. To this end, data mixing refers to the strategy
of (1) combining datasets from different domains, sources or
structures in specific proportions to train LLMs or (2) making
LLMs give different proportions of attention on different
domains (e.g., by changing the sampling probabilities) in the
training session. Effective data mixing ensures that the model
16

TABLE 6: Comparison of Data Mixing Methods for LLMs.
Taxonomy
Stage
Methods
Traits
Before Training
(Human Experience)
Pre-training
Multi-Source Data Adjusting
Intuitive and easy to implement, suitable for rapid experimentation.
[139], [347]
Entropy-Based Mixing [152]
Low computation cost with quality quantification by entropy.
Before Training
(Model-Based Optimization)
Pre-training
Linear Regression Model [263]
Only 10% of DoReMi’s [420] computational resources are required.
Simultaneously train hundreds of small models to accelerate optimization.
Pre-training
Bivariate Data Mixing Law [152]
Avoid iterative training of proxy models (low computational costs).
Show relation between loss and training steps.
Continual Pre-training
Chinchilla Scaling Law [323]
Support knowledge transferring to new domains (↓over 95% training costs).
Pre-training
Exponential Functions [439]
Support datasets without explicit domain division.
Continual Pre-training
Power-law Function [160]
Compared to single-objective optimization like [323]
[160] ensures that domain performance improvement
does not compromise general capabilities.
Pre-training
Classification Model [251]
Reverse engineering for finding the suitable data recipe of LLMs.
During Training
(Bilevel Optimization)
Pre-training
Calculate domain contribution by
Requires a proxy model, performances well in OOD datasets.
gradient inner products[135]
Fine-tuning
Dynamically adjust weights by
Multiple applications like multilingual training,
gradient alignment values [302]
instruction following, large-scale data reweighting
During Training
(Distributionally Robust Optimization)
Pre-training
Group DRO [420]
For pre-training, smooth adjusting to prevent abrupt weight changes
Fine-tuning
Task-level DRO [278]
For fine tuning, quick response to task difficulty changes
captures broad generalization capabilities while balancing
performance across tasks and domains [140]. Existing data
mixing methods can be classified into two main categories:
Principles
Unlike traditional ML models like BERT (trained
on smaller, domain-specific data with homogeneous
distributions), LLMs require massive multilingual or
multi-domain corpora, raising the critical challenge
of optimizing dataset mixing ratios for performance.
Current methods use heuristic experimentation or formulate ratio-performance relationships (e.g., validation loss), but cost-effective determination of optimal
ratios, beyond heuristics, remains unresolved due to
high cost demands for functional approximations.
Before-Training Mixing (Human Experience). This
method provides empirical data mixing strategies such as
setting different ratios of datasets based on various factors
(e.g., complexity and diversity of the datasets) that likely
improve LLMs’ abilities.
First, to study the effect of data mixture, there are works
that experiment heuristically on different data ratios for pretraining of LLMs. [139] suspects training sequence from
simple to complex data would improve LLMs’ performance,
thus introduces a two-stage data mixing strategy for LLM
pre-training: (1) It first blends web-crawled data with minimal
high-quality content (1.9% math, 15% code), testing ratios
(<35% high-quality) and selecting optimal mixtures via evaluations on CommonsenseQA [371] and HumanEval [95]. (2)
It then filters low-quality data, boosting math (24%→29%),
code (20%→29%), and instructional alignment data. Ratios
are similarly optimized through empirical validation. The
method iteratively refines proportions using down-sampled
Megatron-8B [355] for efficiency, then scales findings to a
25B model, balancing diversity-quality tradeoffs with reduced
experimental overhead. Similarly, Slimpajama [347] explores
the impact of data source diversity and weight distribution
on model performance by adjusting the proportions of data
from multiple sources, such as Commoncrawl [11], C4 [330],
Github [14] .
Second, we can utilize metrics to judge different datasets
and mix them. To calculate the best result rather than
just try different combinations, Bimix
[152] adopts entropy metrics (e.g., Shannon entropy [343], conditional entropy [343]) as the quality scores which are then normalized to compute the proportions of each domain (e.g.,
conditional entropy, written as as Hi

X(t+1)
i
| X(t)
i

=
−P
x∈X(t)
i
P
x′∈X(


## 2.3.6
Data Distillation and Synthesis

Synthetic data, which mimics real-world scenarios, is particularly valuable for resolving problems such as (i) data
scarcity (e.g., augmenting data for a small dataset) [426], (ii)
privacy concerns (e.g., replacing sensitive data with synthesis
data) [419], (iii) the need for diverse and high-quality datasets
(e.g., generating examples for underrepresented cases) [260],
(iv) lack of reasoning data (e.g., for code, chain of thought),
(v) human alignment (e.g., label better LLM’s response by
human beings or LLMs).
Principles
Traditional ML methods use rule-based templates,
basic
augmentation
(lexical
substitution,
backtranslation), or statistical models to create limited
synthetic data, addressing data scarcity/class imbalance. While LLM-driven synthesis employs LLMs
to produce diverse, high-quality data, tackling data
scarcity, privacy concerns, and diverse training needs.
Key paradigms include: (i) sample-driven generation,
(ii) domain-aligned synthesis, and (iii) reasoningcentric formatting. Challenges involve ensuring rigorous reasoning chain synthesis and optimizing costquality balance in data production.
Despite the advantages, synthetic data can negatively
impact LLM training, such as when characteristics like toxicity are inherited from the source model or even amplified [352]. Thus, it is vital to design data synthesis methods for
LLMs [495]. As shown in Figure 4, we discuss methods dealing
these problem through the diverse LLM stages, including preTraining, SFT, Reinforcement Learning and RAG.
Knowledge Distillation. Due to LLMs’ massive parameter
scale and high resource demands which make practical deployment challenging, so we utilize knowledge distillation (such
as designing paradigms to prompt LLM to generate highquality data) to training a student LLM with less parameters
to mimic the target model’s generation ability.
• Task-Specific Prompt Distillation. To significantly reduce
inference costs and latency while maintaining performance,
[353] employs task-specific prompts: (1) Chain-of-Density
(CoD): Iteratively adds entities to summarize for enhanced
density. (2) Chain-of-Thought (CoT): Guides reasoning tasks
(e.g., math) through stepwise logic. Using GSM8K [106] data
and Llama-3.1-405B-Instruct, synthetic data is generated
for fine-tuning smaller models (Llama-3.1-8B/70B-Instruct)
paired with simplified prompts, balancing efficiency and task
specialization.
• Code Verification and Error Correction Distillation. Existing knowledge distillation methods (e.g., Chain-of-Thought
Fine-tuning) rely on synthetic data generated by LLMs, but
such data often contains incorrect intermediate reasoning
steps which can mislead small models during learning, hindering the improvement of their reasoning capabilities.
Pad [496] proposes Program-aided Distillation (PaD) to
address error-prone synthetic data in knowledge distillation
with (i) Programmatic Reasoning: LLMs generate executable
code (e.g., math problems as Python calculations) instead of
natural language CoT, with Python compilers auto-filtering
logic errors. (ii) Error-Injection Training: Models learn error
correction by fixing synthetically injected AST-based errors
(e.g., NameError). (iii) Semantic Validation: Decoding selects
steps via semantic alignment scoring (e.g., cosine similarity)
to prevent error propagation. PaD replaces flawed CoT steps
with verifiable program logic, enhancing small models’ reasoning robustness through code-based distillation and selfcorrection mechanisms.
• Multi-stage Collaboration Distillation Between Student models. In domains with high annotation costs (e.g., biomedical parsing) or complex task structures (e.g., syntactic/semantic parsing), labeled data is extremely scarce, making
traditional supervised fine-tuning ineffective. MCKD [467]
introduces Multi-stage Collaborative KD (MCKD) for lowresource generation as 3 steps. (i) Initialization: GPT-3.5
generates pseudo-labels for unlabeled data. (ii) Collaborative
Distillation: Splits data into two subsets for cross-labeling via
paired T5-Base models, reducing noise overfitting. Iteratively
refines labels over 3 iterations. (iii) Final Training: Trains a
single model on refined labels. Achieves near-supervised performance with 50 labeled examples (vs. 500 required traditionally) through multi-stage noise reduction and collaborative
pseudo-label optimization.
Pre-training Data Augmentation. The pre-training stage
of LLM requires a vast amount of data and it can be costly
to synthesize such data with powerful models like GPT19

4. Therefore, there are techniques like distillation [481], or
simply mixing synthetic data into the whole corpus.
• Distilled LLM for Mathematical Data Synthesis. JiuZhang3.0 [481] proposes an LLM-based synthesis method for
high-quality math problems: (i) Model Distillation, fine-tunes
DeepSeekMath-7B on GPT-4-generated QA pairs (with curated prompts and math texts) to mimic GPT-4’s generation.
(ii) Uses gradient similarity to prioritize task-r


# 20

models to produce variations of real images that retain seman-

tic consistency while augmenting the dataset. Concerning image captioning, several studies focus on improving the quality
of image-text pairs. LaCLIP [133] uses ChatGPT to rewrite
existing captions, thereby introducing greater diversity in
linguistic expression while maintain the core semantic content.
A limitation of this method is the potential for visual semantic
loss due to the language model’s lack of direct access to the image. To mitigate this, VeCLIP [222] incorporates a multimodal
LLM (LLaVA) to provide a detailed visual description of the
image contents (e.g., color and shape attributes, objects, and
relations among objects). This description is then fused with
the original caption by a LLM to yield a more comprehensive
final caption. To simultaneously synthesize both image and
text samples, CtrlSynth [83] proposes a system comprising
three modules: the Florence-large [418] vision tagging model
to extract basic visual elements of an image (e.g., color and
shape attributes, objects, and relations among objects), the
Qwen2-7B-Instruct [434] language model to generate synthetic text which meets the requirements in the instruction,
and the stable-diffusion-x1-base-1.0 [314] text-to-image model
to generate novel and diverse image samples based on text
prompts.
SFT Data Augmentation. The SFT stage of LLM training
mainly focus on improvement of specific domains (math,
medicine, etc.), aligning LLM’s knowledge to instructions, enhancing reasoning ability, etc. Current methods take LLMs as
the main method to generate data with some designed frameworks. Many works [179], [260], [290] take existed datasets as
seeds to synthesize mimic datasets.
• LLM-based Knowledge and Q&A Pairs Synthesis. To enrich
or enhance the diversity of data for better model performance,
there are various prompt frameworks such as building topic
taxonomy [233] and iterative synthesis [179].
For example, to cover various domains of human knowledge, GLAN [233] introduces a knowledge-classification
framework for synthetic text generation by GPT-4. (i) Organize knowledge domains (natural sciences/humanities) into
disciplines (math/programming) by; (ii) Develop course outlines with units (e.g., ”Intro to Calculus”) and core concepts
(e.g., ”Limits”); (iii) Use GPT-4 to create diverse questions by
combining concepts, then generate answers with faster GPT3.5. This structured approach ensures systematic coverage
of knowledge areas while balancing generation quality and
efficiency.
Though this could enhance understanding of LLM about
many domains, but to get better enhancement still needs
to focus on one aspect, like math, KPDDS [179] identifies
mathematical problem themes (e.g., algebra, geometry) and
core skills (e.g., factoring) using GPT-4, then constructs a
matrix mapping theme co-occurrence probabilities to guide
logical problem generation. GPT-4 synthesizes new questions
based on these themes and solutions, which are evaluated for
quality (clarity, coherence) and refined via GPT-4 voting. The
method further diversifies questions through variations and
applies iterative voting to optimize output. This structured
approach ensures contextually coherent, avoiding random
combinations.
Instead of combining elements like KPDDS (e.g., combining
algebra
and
geometry
to
synthesize
problems),
TABLE 7: Data Synthesis for LLM.
Stage
Category
Methods
Distillation
Reasoning Augmentation
Cot [353]
Prompt with Tools [496]
Data Augmentation
Prompt with Multi-Agent [467]
Pre-Training
Data Augmentation
Distillation + Fine Tuning + Prompt [481]
Prompt [99], [98], [282], [93],[344], [92]
SFT
Data Augmentation
Prompt [233], [179], [260], [290]
Reasoning Augmentation
Prompt [178], [173], [346]
Human Label [253]
Automated Label [399]
High Quality Reasoning Data [442], [230]
RL
Prompts Optimization
Prompt [401]
Human Feedback
RLHF [71]
RLHF By LLM [476]
RAG
Privacy Protection
Prompt [450]
MMIQC [260] enhances mathematical reasoning by iteratively
generating complex, diverse problems from existing ones for
fine-tuning. Using a seed dataset, GPT-4 creates problems via
added constraints, variables, or extended reasoning. A filtering mechanism ensures logical consistency, problem-solution
alignment, and correctness, with validated data expanding the
dataset iteratively.
• LLM-based Alignment Data Augmentation. Domain knowledge is one thing, and lead LLM’s knowledge align with
instruction is another thing that could be done to get better
performance through techniques like few-shot prompting.
AgentInstruct [290] uses LLMs to create scalable, diverse Q&A data. GPT-4 converts raw input (text/code) into
structured formats (argument passages, API lists) to enable
diverse instruction creation. Multiple GPT-4 agents generate
varied task instructions and answers following a detailed
taxonomy (e.g., reading comprehension, coding tasks). GPT4 and Claude-3 then refine tasks by adding complexity (e.g.,
integrating dense context or escalating difficulty), ensuring
high-quality,


# 4 generates corresponding problems through two types of

solutions: (1) One is a natural language explanation of the
reasoning process, and (2) the other is a formal language
solution that can be verified (e.g., code compatible with
mathematical proof tools). Next, formal solutions are verified
using mathematical proof tools to ensure the correctness of
21

the reasoning and answers. For content that fails verification,
the model adjusts based on feedback and re-verifies until a
correct result is generated.
• CoT Data Synthesis By LLM Exploring. Works mentioned
above highly rely GPT-4 for its advanced ability for math
to generate problems and solutions to fine-tune for higher
reasoning ability. While more recent research try to enhance
LLMs’ reasoning ability by technique like Chain-of-Thought
(CoT, which let LLMs use tokens to output their reasoning
steps) and synthesis or label finer reasoning data for training.
By generating CoT data that covers a wide range of reasoning paths through a trial-and-error self-verification loop,
[173] breaks the traditional limitation of relying solely on
correct reasoning paths. Specifically, multiple LLMs (e.g.,
Qwen-7B, Llama-3-8B) are utilized to generate diverse solutions for the same mathematical problem (20-50 responses
per problem) to encourage models to explore incorrect paths
(e.g., wrong formulas, logical leaps) while retaining complete
error analysis. Then a verifier LLM (e.g., GPT-4) performs
critical analysis on each response: (a) For incorrect paths,
annotate the error steps and generate correction suggestions
(e.g., “Step 3 misapplies the cosine theorem, which should
be replaced with the Pythagorean theorem”). (b) For correct
paths, extract key reasoning steps to form a concise CoT.
Merge corrected incorrect attempts with correct paths to
construct multi-branch CoT.
Similarly,
Satori
[346]
introduces
Chain-of-ActionThought (COAT), a reasoning framework with meta-action
tokens (Continue / Reflect / Explore) enabling dynamic
pauses, logic verification, and strategy shifts with a two-stage
pipeline: (i) Multiple LLM agents generate COAT-formatted
reasoning chains to fine-tune a base model for COATformatted syntax mastery. (ii) Partial rollbacks (≤5 steps)
from historical reasoning (correct/incorrect paths) append
<reflect> to trigger revised reasoning with reinforcement
learning (RL) combined with rewards for answer correctness,
error correction, and penalties for failures. The RL-enhanced
model is distilled into base models (e.g., Llama8B) for
iterative refinement.
These works propose framework by letting LLM reason by
themselves, and we also have works that label reasoning data
for fine tuning to get reasoning ability.
• Reasoning Data Labeling. [253] compares the effects of
outcome supervision (provides feedback based solely on the
correctness of the final answer) and process supervision (provides feedback for each step in the reasoning process) on
mathematical reasoning tasks by comparing manually labeling the reasoning steps generated by GPT-4 with outcome
supervision. The results showed that process supervision
model achieved significantly higher problem-solving accuracy
(78.2%) compared to outcome supervision model (72.4%)
But this would cost too much manual effort, so MATHSHEPHERD [399] proposes a method to automatically generate process-annotated data for training Process Reward
Models (PRM, which evaluate the quality of each reasoning
step). First, complete the remaining reasoning and answers
multiple times for the initially generated reasoning steps with
LLM, then each step is scored based on two metrics: (1) Hard
Estimation (whether the correct answer is generated, with
values of 0 or 1). (2) Soft Estimation (the proportion of correct
answers generated through this step). These scores assess the
step’s ability to derive the correct answer.
• High Quality and Well Format Data Are The Keys To Better
Reasoning. Moreover, LIMO [442] and [230] state that high
quality and well-formatted reasoning data are keys to high
performance. [442] emphasizes stimulating complex reasoning
capabilities in LLMs through a small number of high-quality
training examples with questions and reasoning chains. Powerful models (such as R1, DeepSeek-R1-Distill-Qwen32B) are
used for evaluation and synthesis, retaining problems that
remain challenging. Each problem is accompanied by detailed
solutions and reasoning chains (from official solutions, expert
solutions, and LLMs-generated Cot, etc.) and filtered by
rules-based and LLM-assisted methods.
[230] finds that the overall structure of the reasoning steps
is more important than the specific content. With problems
from Numina-Math [235] etc. and long CoT generated by
DeepSeek-R1 [162] and QwQ-32B-Preview [379] as data to
fine-tune. With modification of the fine-tune data, reveals that
training the model with incorrect answer samples results in an
accuracy drop of only 3.2% compared to training with correct
samples. However, shuffling 67% of the reasoning steps in the
training samples


## 2.3.7
End-to-End Data Processing Pipelines

With above data processing methods, we separately introduce
existing frameworks that support common processing operations; practices of integrating some of these methods within
pipelines in real-world LLM data preparation; together with
some preliminary pipeline orchestration methods.
Principles
When designing data processing pipelines, several
critical factors must be considered: (1) the trade-off
between data quality and quantity; (2) dependencies
across the processing operations (e.g., text extraction
necessarily preceding operations like deduplication
and filtering); (3) efficiency optimization (e.g., conducting computationally intensive steps like modelbased filtering after lightweight processing steps like
URL filtering).


## 2.2.7.1 Typical data processing frameworks

Data processing frameworks provide built-in libraries, operators, and intuitive interfaces that can benefit the design
of data processing pipelines for different LLMs. Here we
showcase three typical data processing frameworks.
(1) Data-juicer [90] is an open-source framework designed
for customizable, high-quality, and efficient data processing.
It offers a diverse range of pre-built data processing operators such as data formatting, mapping, filtering, and deduplication. Additionally, the framework features visualization
and automatic evaluation, enabling users to receive immediate feedback on their data pipeline. To manage large-scale
datasets effectively, Data-juicer is optimized for distributed
computing, ensuring robust performance and scalability.
(2) Dataverse [305] is an open-source framework designed
to simplify custom ETL (Extract-Transform-Load) pipeline
development through an easy-to-use block-based interface
that enables users to easily customize by adding, removing,
or rearranging blocks. The platform offers a diverse range of
pre-built data processing operators, including deduplication,
decontamination, bias mitigation, and toxicity reduction,
while also supporting the integration of data from multiple
sources. Similar to Data-juicer, Dataverse integrates with
Apache Spark for distributed processing and supports AWS
integration for cloud scalability.
(3) [368] introduces a data processing framework that
allows users to customize data processing pipelines using a
comprehensive suite of operators categorized in two main
modules: (1) The processing module consisting of data reformatting (read and import strctured data), cleaning (removed
undesired data such as HTML tags and translate text), filtering, and deduplication (using MinHashLSH in Section 2.3.2)
operators; (2) The analyzing module featuring refined data
probing and automatic evaluation.


## 2.2.7.2 Typical data pipelines

Data processing pipelines aim to orchestrate a subset of data
processing operations (in a specific order) that transform raw
data into high-quality LLM training data (mostly for the
pre-training stage). Here we showcase three representative
pipelines.
• The MacroData Refinement (MDR) pipeline is designed to
construct the RefinedWeb Dataset, which has been used for
pre-training Falcon LLMs [311]. MDR refines web-scale data
from Common Crawl [11] through three main operations.
(i) Data acquisition: MDR first applies a lightweight URL
filter to exclude irrelevant links before any computationally
intensive steps. It then extracts text from WARC files using
warcio and Trafilatura [73], followed by language identification (i.e., removing content with limited natural language)
using fastText [199] as implemented in CCNet [410].
(ii) Data filtering: To eliminate low-quality content, MDR
employs both (1) document-level filtering [328] and (2) linelevel filtering, which removes noisy content such as social
media counters or navigation links.
(iii) Data deduplication: Despite prior filtering, substantial
content duplication remains, which can degrade model performance. MDR performs both fuzzy deduplication using MinHash and exact deduplication with suffix arrays to minimize
redundancy. To address computational limits, the Common
Crawl corpus is partitioned into 100 segments, with deduplication performed per segment. Additionally, to avoid cross-part
redundancy, URL-level deduplication is applied by excluding
URLs already retained in earlier segments.
Overall, MDR follows three core design principles: (i) scale
first, by maximizing data volume from Common Crawl to
support large model training; (ii) strict deduplication, as rigorous redundancy elimination is critical for training efficiency
and generalization; and (iii) heuristic filtering, favoring rulebased filters over ML-based ones to reduce bias and maintain
transparency.
• The DCLM-Baseline pipeline also processes data from the
Common Crawl dataset. Different from MDR, in addition
to text extraction and language identification, it applies efficient heuristic filtering [311] to exclude irregular content
(e.g., toxic words or webpages from illegal sources). Next,
DCLM-Baseline adopts a Bloom filter for data deduplication,
ensuring its scalability with large datasets. Finally, over the
processed data with much smaller size, it conducts modelbased quality filtering (most computationally intensive) to
remove low-quality content. Specifically, a fastText classifier trained on instruction-formatted data, including OH-2.5
(OpenHermes 2.5) and ELI5 (ExplainLikeImFive), is used to
retain the top 10% of documents.
• The FineWeb pipeline (for preparing a 15T-token pretraining dataset) starts with text extraction from WARC files
using Trafilatura [73], which is more custom than directly
using WET format data and language filtering with fastText.
Different from the above pipelines, it conducts MassiveText
filtering, i.e., heuristic quality filters and repetition filters


# 23

URL filtering
Text extraction
Language
filtering
Fuzzy
deduplication

C4 quality
filtering
Custom
filtering
MassiveText
filtering
PII
reformatting
Model-based
filtering
Language
filtering
Pre-training
data
CommonCrawl
(WARC)
URL filtering
Text extraction
Heuristic
filtering
Pre-training
data(1.4%)
Bloom filter
deduplication
URL filtering
Text extraction
Language
filtering
Repetition
removal
Fuzzy&Exact
deduplication
Document-level
filtering
Line-level
filtering
Pre-training
data(11.67%)
RefinedWeb
DCLM-Baseline
FineWeb
CommonCrawl
(WARC)
CommonCrawl
(WARC)
-0.8%
-50.8%
-28.5%
-6.2%
-12.3%
-3.69%
-48.80%
-11.54%
-5.82%
-6.81%
-11.67%
Fig. 6: Typical data processing pipelines for LLMs.
on paragraph, line, and gram level [328]. Besides, it conducts fuzzy deduplication using individual MinHash deduplication for each CommonCrawl snapshot, as this approach
matches RefinedWeb’s performance, whereas global deduplication yields little improvement over non-deduplicated data.
After deduplication, given the observation that the C4 dataset
yields superior performance on some benchmarks despite its
smaller size, a selection of C4 [330]’s heuristic filters is applied
to drop low-quality content such as unpunctuated lines and
policy statements. Finally, to further enhance data quality,
additional custom heuristic filters are developed through a
systematic process. Moreover, personal identifiable information (PII) such as email addresses is anonymized using regex
patterns in the public release of the dataset.
Compared to MDR and DCLM-Baseline, the FineWeb
pipeline is considerably more complex due to its integration
of multiple layers of filtering, each inspired by empirical
evaluations and comparisons with other datasets such as C4
and RefinedWeb. Its design reflects a trade-off that prioritizes
performance over simplicity.


## 2.2.7.3 Orchestration of data pipelines

The above data pipelines are mostly designed by experience. Instead, Data-Juicer Sandbox [91] proposes a “ProbeAnalyze-Refine” workflow, which involves systematically exploring the impact of various data processing operations
and their orders on model performance, combining effective
operations into data recipes, and optimizing data utilization
through duplication analysis and diversity analysis. The orchestrated pipelines are validated through applications on
state-of-the-art models like Mini-Gemini (for image-to-text
generation) and EasyAnimate (for text-to-video generation).


## 2.4
Data Storage for LLM

In this section, we introduce storage techniques for LLMs,
which we categorize accroding to the tasks they address,
including (1) data formats, (2) data distribution, (3) data
organization, (4) data movement, (5) data fault tolerance, and
(6) KV cache.


## 2.4.1
Data Formats

Data formats are file formats for training data and models.
For LLMs, appropriate file formats for data and models can
enhance storage efficiency, accommodate multimodal data,
be suitable for model training, ensure security, and influence
compatibility across different frameworks.
Principles
Compared to traditional machine learning, LLMs
place greater demands on data being multi-modal and
in a unified format. The main challenge is how to
achieve high data reading efficiency in multi-modal
scenarios. Current methods address this using techniques like sequential storage.
Training
Data
Format.
For
training
data,
file
formats are required to have good storage efficiency (e.g.,
TFRecord [44]), be adaptable to large amounts of data (e.g.,
MindRecord [40]), and sometimes be suitable for model training (e.g., tf.data.Dataset [43]).
(1) Pure-Text Formats.
Common
formats
such
as
CSV,
JSON, TSV, and TXT are often used to store pure-text
LLM data (though they are not limited to such content).
However, for large-scale training datasets (at the PB scale),
these formats incur significant storage overhead due to the
lack of compression (e.g., not supporting binary encoding),
leading to storage waste and slow data loading during LLM
training.
To address these issues, TFRecord [44] is based on Protobuf (a highly efficient binary serialization protocol) and stores
data in a row-based format. As a binary format, its size is
significantly smaller than JSON or CSV. Besides, data can be
written and read in a streaming manner, making it especially
suitable for scenarios like training where data is consumed
sample by sample.
(2) Multimodal Formats. Pure-text formats are not wellsuited for multimodal datasets containing images, videos, and
text. To address this, file formats such as TFRecord [44] in
TensorFlow and MindRecord [40] in MindSpore have been developed to natively support efficient multimodal data storage.
• Unlike traditional formats (e.g., COCO JSON [10], which
store image metadata in separate JSON files), TFRecord [44]
allows users to encapsulate images, labels, and metadata
within a single tf.train.Example, eliminating the need for
24

separate label files. Moreover, as multimodal datasets substantially increase data volume, TFRecord supports data
sharding, enabling the creation of distributed files that can be
assigned across multiple servers to facilitate parallel training.
• MindRecord organizes data into two types of files: (i) the
data file, which contains a file header, scalar data pages
(e.g., image labels and filenames), and block data pages (e.g.,
image and text) to store training data; and (ii) the index file,
which maintains indexing information based on scalar data to
support efficient retrieval and dataset analysis.
(4) Tensor Data Formats.
Compared
to
the
storage
formats mentioned above, tensor formats represent data as
multi-dimensional arrays. On GPUs or TPUs, such multidimensional structures can be partitioned and processed in
parallel, making them highly suitable for large-scale computation. For example, tf.data.Dataset [43] can organize various
raw data types (e.g., images, text) into a unified tensor format,
ready for direct use by models. However, tensor formats, due
to their dense multi-dimensional storage, incur large storage
overhead and offer poor readability, and are typically adopted
only in model training.
Model Data Format. Model storage formats need to pay
attention to security (e.g., Safetensors [85]) and are usually
closely tied to their respective model training frameworks [32],
[42], [22].
• Pickle (.pkl [13]) is a Python-specific format supported
by almost all Python frameworks and can store any Python
object, not limited to model parameters, making it convenient
for saving model states and other custom information.
• Safetensors [85] was introduced by Huggingface to address
the security concerns inherent in Python’s Pickle-based serialization. While Pickle serializes both the data and behavior
of Python objects—enabling arbitrary code execution during deserialization—safetensors avoids this risk by focusing
exclusively on tensors and their associated metadata. This
design ensures safe deserialization without the possibility of
executing malicious code. Additionally, safetensors supports
memory mapping (mmap), which significantly enhances the
efficiency of model loading.
• PyTorch-specific formats (e.g., .pt, .pth [32]) are optimized
for model storage. Typically, .pth files are used to save
training checkpoints, including model parameters, optimizer
states, and epoch information, while .pt files are used to store
only the model parameters.
• TensorFlow offers two common saving formats [42]: (1)
SavedModel format for saving the entire model, including
computation graph, weights, optimizer; (2) .ckpt for storing
model weights, optimizer states, and training metadata, and
is used to save and restore progress during training.
• ONNX [27] is a cross-framework deep learning model format tha


# 1
Data Loading
Start
Response
Asynchronous
File Reading
Method




## Method

2


# 3
Other Processing
LLM Training
Data Loading
LLM Large-scale Data Storage

Fig. 7: The storage architecture of 3FS [15].


## 2.4.2
Data Distribution

With the development of LLMs, the scale of LLM training
datasets and the number of parameters of LLMs themselves
are growing rapidly (e.g., 9.5 PB data form Common Crawl
[183], DeepSeek-R1 [162] has 617B parameters). A single node
cannot store such large-scale data, and the data needs to
be distributed across multiple nodes. The key technologies
involved mainly include (1) distributed storage systems and
(2) heterogeneous storage systems.
Principles
Compared to traditional machine learning, the data
(e.g., training data and model data) used in LLMs
including both is growing exponentially. The main
challenge lies in how to efficiently store and manage
such large-scale data. Current approaches address this
through distributed and heterogeneous storage systems.
Distributed Storage Systems. Distributed storage systems refer to storing a large-scale datasets across multiple
nodes (e.g., JuiceFS [16], 3FS [15]). Traditional distributed
file systems (such as HDFS [79]) often come with high costs.
Moreover, most distributed file systems still use the POSIX
protocol when loading the training data for LLMs, which
bring about significant software overhead.
JuiceFS [16], a typical distributed file system based on
object storage, uses object storage (e.g., S3 [4]) as the backend
to store data. Compared to traditional distributed file systems (file or block storage), distributed file systems based on
object storage enables simpler horizontal scaling. It does not
need complex directory hierarchy (File Storage) and does not
involve complex management logic (Block Storage), thereby
significantly reducing storage costs (approximately 20% of the
cost of traditional file systems).
As shown in Figure 7, 3FS [15] employs a large number
of SSDs for distributed data storage and uses the CRAQ
algorithm to ensure data consistency. Specifically, a piece of
data is saved as multiple same chunks, which together form
25

a Chain. For read requests, they can be sent to any chunk
in the Chain, and the chunk will return the data. For write
requests, the writing operation is carried out sequentially on
each chunk. When a certain chunk malfunctions, instead of
using the incremental data generated during the abnormal
period to overwrite the data as in traditional methods, it
first moves the chunk to the end of the chain. Only when
the chunk returns to normal will the entire content of other
samples be copied to the abnormal chunk. These operations,
while ensuring data consistency, will cause a certain delay in
write operations. However, they have almost no impact on
read operations, which are more important for LLM training.
Meanwhile, 3FS [15] discovers that in the context of LLM
training, the File Cache significantly consumes system memory, thereby degrading overall I/O performance. To address
this, 3FS adopts an asynchronous data loading approach, disables file caching and exclusively utilizes Direct I/O for data
access, significantly reducing memory pressure. Moreover, it
performs system-level alignment of buffer pointers, offsets,
and lengths to satisfy Direct I/O requirements, thereby avoiding additional memory copies caused by user-side alignment
operations.
Heterogeneous Storage Systems. Heterogeneous storage systems refers to deploying the model state across diverse storage media (e.g., GPUs, CPUs, NVMes Memory).
When deploying the model, The Zero Redundancy Optimizer
(ZeRO) [333] deploys model states across multiple GPUs.
However, simply distributing the model across multiple GPUs
often significantly increases computational costs.
Some methods [334], [337], [336], [435] alleviate GPU
memory pressure by storing data in host memory or NVMe
SSD. vDNN [337] utilizes a per-layer memory management
approach based on a sliding window that dynamically allocates memory at runtime based on the computational demands of the current layer. Its memory transfer mechanism
includes both static and dynamic policies: the static policy
offloads feature maps of all layers or only convolutional layers,
while the dynamic policy determines which layers and convolutional algorithms to offload at runtime, balancing trainability and performance based on network characteristics.
vDNN fully utilizes CPU memory by offloading intermediate
feature maps that are not immediately needed and prefetching
them prior to backpropagation. ZeRO-Infinity [334] offloads
model states to CPU (e.g. activations) and NVMe memory,
effectively alleviating the GPU memory bottleneck. To further reduce memory pressure, it introduces a memory-centric
tiling technique that lowers the working memory requirements
for LLM training, enabling the execution of large operators
without relying on model parallelism.
However, both vDNN and ZeRO-Infinity only utilize
CPU’s memory without leveraging its computational capabilities. In contrast, ZeRO-Offload [336] retains the parameters and forward/backward computations on the GPU while
offloading the remaining computations (such as optimizer
calculati


## 2.4.3
Data Organization

Data organization refers to data operations (e.g., content
organization in vector-based organization) during the storage
stage that are designed to optimize retrieval accuracy and
efficiency in RAG systems. When LLM answers questions,
issues like hallucination [187] and lack of timeliness often
arise. To address these limitations, RAG [228] (e.g., vectorbased retrieval and graph-based retrieval) have been introduced. They provide models with real-time, reliable context
during inference. And both retrieval methods are based on
the relevant data organization operations (e.g., vector-based
organization and graph-based organization).
Principles
Compared to traditional machine learning, LLMs require RAG knowledge to access real-time information.
The main challenge is how to ensure both the efficiency
and accuracy of retrieval. Current methods address
this through vector-based and graph-based data organization techniques. However, existing RAG systems
still fall short of meeting the high-quality retrieval
demands at the enterprise level, where the document
scale can reach millions of pages.
Vector-Based
Organization Vector-based organization
refers to converting data into vector form for efficient retrieval.
It processes the original data through multiple stages (e.g.,
Content Organization, Chunking, Embedding, Compression
and Storage).
(1) Content Organization. For the source data, organizing the
content can enhance its logical structure, thereby facilitating
improved efficiency and accuracy in retrieval. Works like
Dense x retrieval [97], APS [172] refine text into independent
semantic units, which could be described as the minimal
sentence that include all the necessary context information
from the original text to express its meanings, and Thread [57]
reorganizes documents into logical units, with each unit containing prerequisites, headers, body content, linkers (describing possible paths for next step), and metadata, enabling
a logical and structured representation of the document’s
content, which significantly enhances the system’s logical coherence and processing efficiency especially in complex tasks
(e.g., troubleshooting and dynamic operational workflows).
Similarly, [89] organizes the content of scientific papers
into a hierarchical tree structure, where the root node of
the tree is the paper’s title and child nodes are different
sections, such as the introduction and methods. The relationship between parent and child nodes represents the globallocal content relationships, such as the connection between
the abstract and introduction. Then it traverses the paths
from the root node to the leaf nodes to extract important
contextual information.
26

(2) Chunking. In vector-based retrieval, embedding long texts
may reduce retrieval efficiency. Thus, an effective chunking
strategy is required to divide the text into appropriately
sized segments for encoding. The optimal chunk length needs
to balance retaining fine-grained semantics and maintaining
sufficient context, since a too long text might suffer from
significant semantic compression during embedding, while too
short a text would increase processing costs.
Allowing overlap between consecutive chunks ensures that
important information at the boundaries is not lost and the
continuity of context is maintained. Different from traditional
chunking, MoG [480] adopts a dynamic chunking strategy,
which chunks data when building the knowledge base, where
MoG dynamically determines the optimal granularity (e.g.,
sentence-level, paragraph-level, or section-level) of the knowledge source based on the input query through a trained router.
The router, implemented as an MLP, assigns weights to
different granularities to guide snippet selection. MoGG [480]
extends MPG by converting reference documents into graphs
and redefining granularity as hopping ranges, enabling effective retrieval of dispersed information for complex queries.
(3) Embedding. In vector-based retrieval, the original input
(text, images, audio, or other domains) is transformed into
dense vector representations using models specifically adjusted for each data type. These representations encapsulate
the underlying semantic meaning of the original content, and
are then stored in a vector database for storage and retrieval.
Various embedding models are used to correctly encode semantic information:
• BGE uses a bilingual joint training framework that combines language-specific subword tokenization and specialized
adaptation layers. This design aligns semantic representations across languages, improving cross-lingual retrieval accuracy [94].
• STELLA features a cross-instance attention aggregation
mechanism that explicitly captures inter-sentence dependencies during pretraining. Besides the general embedding model,
STELLA offers an extra dialogue model in incomplete query
situations where the user input has problems such as semantic
omission and reference digestion. This reduces the embedding
dimensions 


## 2.4.4
Data Movement
Data movement refers to the process of moving data from

storage nodes to computing nodes. This process can achieve
high data movement performance by caching data. Meanwhile, offloading data and operators to multiple nodes for
computation can improve the speed of data preprocessing.
Additionally, the highest overall performance can be achieved
by overlapping data storage and computation operations to
jointly schedule storage and computing resources.
Principles
Compared to traditional machine learning, LLMs involve massive data transfers from storage nodes to
compute nodes. The main challenge is how to accelerate the data moving rate. Current methods address
this through data caching, compute-storage overlap,
and data/operator offloading.
Caching Data in advance can increase the data moving rate.
However, if a fixed cache policy is used, in order to meet the
IO requirements of training, the configured storage capacity
often far exceeds that required for storing the dataset [469].
Therefore, a dynamically adjustable cache policy is needed.
Some methods [219], [161], [469] dynamically adjust the cache
mechanism by analyzing the characteristics and requirements
of LLM jobs in real time.
Quiver [219] optimizes cache sharing strategies based on
the following IO characters during model training: (1) data
shareability (due to significant overlap in data access within
and across jobs), (2) substitutability (the I/O order does
not affect job correctness, enabling small caches to improve
performance by substituting data and reducing thrashing),
and (3) predictability (using mini-batch processing times to
estimate job sensitivity to I/O performance for informed cache
allocation).
Fluid [161] dynamically adjusts cache capacity according
to I/O conditions, optimizing the online training speed for
28

each individual LLM job. Specifically, Fluid uses a coordinator to monitor the processes of LLM jobs. It calculates the
number of samples within a specific time window based on
the batch sizes fed back by the jobs, and thus obtains the realtime training speed. Subsequently, based on the concept of
the TCP congestion control algorithm [315], it adopts a trialand-error approach to dynamically adjust the cache capacity.
When the training speed increases, the cache capacity is
increased according to the preset scaling-up factor and scaling
step. Conversely, when the training speed decreases, the cache
capacity is decreased according to the preset scaling-down
factor and scaling step.
Meta proposes Tectonic-Shift [469], a hybrid storage architecture that integrates flash memory with the traditional
HDD-based distributed file system Tectonic. Tectonic-Shift
organizes data segments into buckets for storage in flash
memory and determines segment admission and reinsertion by
comparing bucket priorities (computed from both historical
and predicted future access patterns) against dynamically
adjusted thresholds. It also optimizes the segment size (e.g.,
256 KB) of CacheLib [9] to improve flash memory utilization.
Data/Operator Offloading refers to offloading data preprocessing operations such as shuffling, sampling, and augmentation, to multiple devices in order to improve processing
speed. Currently, data preprocessing pipelines (e.g., tf.data)
are typically performed on the CPU, whose efficiency is often
lower than the training speed achieved by Machine Learning (ML) accelerators like GPUs and TPUs. So enhancing
the efficiency of data preprocessing to match the high-speed
processing capabilities of ML accelerators has become a challenge [159].
Some research [158], [67] offload data preprocessing tasks
to remote CPU servers. Cachew [158] divides the input dataset
of each job into independent subsets for processing by remote CPU nodes. Additionally, users can specify locations for
caching and reusing data in the input pipeline. The scheduler
makes decisions during runtime based on specific metrics and
algorithms through automatic scaling and caching strategies.
The automatic scaling strategy adjusts the number of worker
nodes according to client-reported metrics. The automatic
caching strategy compares the processing times of different
cache locations and selects the optimal caching scheme. The
tf.data service [67] addresses input data bottlenecks by horizontally scaling CPU nodes and leveraging a coordinated read
mechanism to mitigate straggler issues caused by input size
variability in distributed training. Specifically, it is comprised
of four key components: a dispatcher, a pool of workers,
clients, and an orchestrator. The dispatcher manages dataset
assignment to workers using various sharding strategies, for
example, the OFF strategy performs no sharding, the DYNAMIC strategy applies disjoint first-come-first-served sharding, and several static sharding strategies are also supported.
Workers are responsible for actual data processing. Clients
issue data processing requests to the workers. Orchestrator
deploys the aforementioned three components as containers
within the same Borg [384] 


## 2.4.5
Data Fault Tolerance
Data fault tolerance refers to the ability to quickly resume

from the point of interruption during model training by
storing checkpoints or performing redundant computations in
the event of training interruptions.


# 29

Principles

Compared to traditional machine learning, LLMs
place greater emphasis on fault tolerance during training due to their large model sizes and the high cost
of retraining. The main challenge is how to quickly
resume normal training in the event of an interruption.
Current methods address this by saving checkpoints or
using redundant computation.
Checkpoints. Some methods store the model state as checkpoints to handle training interruptions. However, restoring
model states across multiple platforms or frameworks may
encounter compatibility issues. At the same time, frequently
saving model checkpoints can consume a large amount of
storage space, especially during large-scale model training.
For compatibility issues, PaddleNLP [29] has developed
a unified model storage technology. It stores model weights,
optimizer weights, and other data in a unified safetensors format, eliminating the need to differentiate distributed strategies during checkpoint storage. Specifically, when the distributed training strategy changes (e.g., switching between
data parallelism and model parallelism) or the number of
machines is adjusted, Unified Checkpoint enables training
to resume using only a single complete checkpoint, without
requiring separate checkpoints for each configuration.
(1) Asynchronous Storage. Apart from standardized checkpoint
storage,
for
frequently
saving
model,
some
researches [291], [194] aim to accelerate checkpoint saving
through asynchronous storage without affecting the model’s
training speed.
CheckFreq [291] employs a two-stage checkpointing technique designed to capture model state copies in memory
for asynchronous storage while ensuring model parameter
consistency through pipelining with subsequent iteration computations. Specifically, when idle GPU memory is available, it
prioritizes snapshotting on the GPU to reduce costs; otherwise, it stores checkpoints in CPU memory and adjusts the
checkpoint frequency accordingly.
In the training of LLMs on the MegaScale system [194],
HDFS is used to store the model state. When storing model
states, there are problems of balancing the checkpoint frequency and dealing with the HDFS bandwidth bottleneck during model recovery in the training process. To address this,
MegaScale adopts a two-phase storage approach: (1) GPU
worker nodes quickly write the on-chip state to the host
memory and continue training; (2) a background process asynchronously transfers the state to HDFS to reduce interference
with training. When resuming training, a worker node in the
specified data parallel group reads the shared state partition
and broadcasts it to other nodes, reducing the HDFS load and
alleviating bandwidth pressure.
(2) Hierarchical Management refers to storing model checkpoints across a multi-level storage system, storing the checkpoints that may be needed in the closer storage nodes, aiming
to improve recovery speed. Gemini [403] stores checkpoints
in a hierarchical storage system composed of local CPU
memory, remote CPU memory, and remote persistent storage.
It introduces a near-optimal checkpoint placement strategy
for CPU memory. By analyzing the relationship between
the number of machines and checkpoint replicas, it flexibly
adopts group placement or ring placement to maximize the
likelihood of recovery from CPU memory in the event of
failures. ByteCheckpoint [389] manages checkpoint files using
an architecture combining SSD and HDD storage servers.
New checkpoint files are stored as ”hot” data on SSDs for
quick access due to evaluation task downloads after creation.
Once the evaluation is completed and there are no training
anomalies, their access frequency drops, and they become
”cold” data, being migrated to HDDs to free up SSD space
and ensure the hot storage can efficiently store currently
frequently accessed checkpoint files.
Redundant Computations Unlike checkpoint, some methods [382], [186], [147] are based on parallel computing and
redundantly compute the state data of the model, enabling
quick recovery of the training state from non-failed nodes in
case of failures.
Inspired by the RAID disk redundancy technology [307],
Bamboo [382] enables each computing node to perform computations not only on the neural network layers it is responsible for, but also on some layers of its neighboring nodes
as redundant computations. When a node is preempted, its
predecessor node has all the information required for training,
allowing the training to continue without wasting previous
computational results.
Unlike Bamboo’s node-based redundant computation,
Oobleck [186] uses pipeline templates to define training
pipeline execution, specifying node allocation, stage numbers, and model layer-GPU mappings. During training, at
least f + 1 logically-equivalent yet physically-heterogeneous
pipelines are instantiated from these templates, considering
the fault tolerance threshold f and batch size. When a pipeline
node fails, Oobleck leverages other pipelines’ model state
redundancy a


## 2.4.6
KV Cache

LLMs use auto-regressive generation, where each token depends on prior ones. KV Cache avoids redundant computation
by reusing stored key-value pairs, improving efficiency. However, its memory grows with sequence length, making efficient
cache management crucial.
Principles
Compared to traditional machine learning, LLMs require KV cache to accelerate inference. The main
challenge lies in efficiently managing the cache as the
KV size grows rapidly. Current methods address this
by indexing KV, shrinking KV, and managing KV
placement or cache space.
Cache Space Management refers to separating the logical
structure of the KV cache from its physical storage imple30

mentation, which facilitates memory allocation and improves
memory utilization. vLLM [220] and vTensor [428] divide
the KV cache into fixed-size blocks and store them in a
non-contiguous manner. vLLM manages these blocks through
a mapping mechanism, while vTensor stores the fixed-size
KV cache blocks non-contiguously in physical memory. This
decouples the logical and physical KV blocks, utilizing a block
table to manage dynamic memory allocation by tracking the
mapping relationships and fill states.
KV Placement refers to using a perception strategy to store
frequently used KV in faster storage media (such as GPU
memory), while storing less frequently used KV in slower
storage media (such as SSD), or releasing them directly.
RAGCache [197] provides a prefix-aware PGDSF replacement
policy that prioritizes cache nodes based on access frequency,
size, and recomputation cost. And stores frequently accessed
data in fast GPU memory and less frequent data in slower host
memory, maximizing cache efficiency. CachedAttention [148]
leverages the inference job scheduler to observe the jobs
waiting for execution. To improve cache efficiency, the KV
cache of a pending job is prefetched into the host memory
from disk before execution. Meanwhile, KV caches that are
no longer required are evicted, based on the jobs waiting to be
executed.
KV Shrinking KV Cache Shrinking refers to trimming or
reducing the KV Cache in order to lower memory usage
and improve inference efficiency. CacheGen [265] uses a customized tensor encoder to encode the KV cache into a more
efficient bitstream, thereby reducing bandwidth usage. It also
compresses the KV cache using techniques such as block-based
encoding, hierarchical quantization, and arithmetic encoding,
while dynamically adjusting the compression level and transmission method based on network conditions to ensure low
latency and high generation quality.
Unlike CacheGen, which only considers intra-layer redundancy, MiniCache [255] is based on the similarity of KV cache
states in adjacent layers. It decomposes the state vectors into
magnitude and direction components, calculates the direction
vectors using SLERP [354], and merges the KV caches of adjacent layers to form a merged cache that contains information
such as direction vectors, magnitudes, and angles.
Compared with the traditional method of storing the complete KV data, HCache [150] only stores the hidden states (the
size of the hidden states is only half that of the KV cache, and
recomputing the KV cache from the hidden states can reduce
the computational load). When restoring the state, a bubblefree restoration scheduler is used to concurrently execute the
transmission of hidden states and the recomputation from
hidden states, maximizing the overall resource utilization.
KV Indexing refers to the process of constructing an indexing architecture for the KV Cache to accelerate the query
process of the KV Cache. ChunkAttention [440] organizes the
KV cache into a prefix tree using a prefix-aware KV cache
(PAKV), sharing key-value tensors of common prefixes to accelerate the corresponding KV query process. [478] proposes
Prefix Sharing Maximization (PSM): By dynamically reordering data columns and rows, it maximizes prefix sharing among
requests to improve cache hit rates. Column Reordering sorts
columns based on value frequency and size, prioritizing those
with more shared prefixes. Row Sorting groups requests with
identical prefixes together, further enhancing cache reuse.


## 2.5
Data Serving for LLM
Data service encompasses data preprocessing operations car-

ried out after data is transferred from storage to computing
nodes and before its actual utilization by the LLM, aiming
to facilitate more effective data consumption by the LLM.
These data preprocessing operations include: data shuffling,
data compression, data packing, and data provenance.


## 2.5.1
Data Shuffling
Data shuffling in data serving means that different data needs

to be selected and provided to LLMs at various stages (e.g., in
different epochs for pretraining). For example, corresponding
training data needs to be supplied according to the training
requirements during the training stage; during the RAG stage,
corresponding knowledge needs to be supplied based on the
degree of relevance to the questions.
Principles
Compared to traditional machine learning, LLM applications are divided into multiple stages, each requiring different types of data to be fed into the model.
The main challenge is how to select data that meets
the specific requirements of LLMs. In the training
stage, current methods provide training data by scoring based on data samples or model states, or by using
empirical training strategies. In the RAG stage, data
is selected through metrics, rules, or models to supply
relevant knowledge to the LLM.
Data Shuffling for Training. As LLMs continuously
trained over new tasks, it may begin to lose its ability to retain
early task knowledge, a phenomenon known as catastrophic
forgetting [287], [286]. To address this, some data supply
methods are employed to manage datasets during the training process and provide high-quality data. Meanwhile, some
methods, instead of altering the dataset, propose reasonable
learning strategies.
(1) Data Pruning. Data pruning refers that during the training process, partial shuffling is carried out on the training
dataset, and high-quality data is retained, so that the model
is trained on the data that has not been fully learned and is of
high quality.
Sample Scoring. Some methods [137], [66] prune datasets by
scoring samples, selecting high-scoring samples for subsequent
training. [137] applies the EL2N metric to identify important
examples in a dataset, written as χ(xi, yi) = E∥f(xi) −yi∥2,
where f(xi) is the model’s prediction and yi is the true
sample. Based on the computed EL2N values, it periodically prunes irrelevant data during training. [66] extends
the EL2N metric to evaluate sample importance, written as
ˆχema(x, y) ←α · ˆχnlu(x, y) + (1 −α) · ˆχema(x, y), where α is
a smoothing parameter. Based on extended EL2N values, it
periodically selects data subsets for training.
Model State Scoring. Unlike the aforementioned approach
of scoring samples and prune the dataset, some methods [372],
[56], [416], [276] prune the distribution of dataset by scoring
the model’s state (such as training loss and learning status).
31

Moving-one-Sample-out (MoSo) [372] identifies and selects
the most informative LLM pre-training samples by assessing
the influence of a specific sample on the training loss. The
MoSo score measures how the training loss over the dataset
S excluding z (i.e., S \ z) would change when the sample
z is removed. This approximation measures the agreement
between z and S \z, where the sample is considered important
and receives a higher score if the gradient of z is consistently
aligned with the average gradient.
Similarly, Velocitune [276] is a dynamic domain weight
adjustment method based on learning velocity, which is defined as Vt[i] =
ℓt[i]−ℓtarget[i]
ℓinit[i]−ℓtarget[i] , where Vt[i] denotes the learning
velocity for domain i at step t, ℓt[i] is the current loss for
domain i, ℓtarget[i] is the target loss for domain i, predicted
by the scaling law [201], ℓinit[i] is the initial loss for domain
i, calculated before training starts. The method calculates
the learning velocity of each domain and dynamically adjusts
the sampling weights, giving more attention to domains with
slower learning progress, thereby achieving a balanced learning effect.
Some methods [56], [416] combine reinforcement learning
based on scoring the model to adjust the dataset. ODM [56]
is based on the multi-armed bandit algorithm. It regards
each data domain as an arm and uses classical reinforcement
learning methods. By taking the training loss as the reward
function, it optimizes the data mixing ratio online to adapt to
training dynamics. That is, it dynamically adjusts the sampling weights of each data domain and preferentially selects
data with high information gain and large losses.
MOS [416] proposes a scoring network that dynamically
adjusts the sampling probabilities of different datasets based
on the model’s current learning state, combined with reinforcement learning, to alter the distribution of training
data. This adjustment is guided by three reward functions:
(i) Transferability for measuring the similarity (e.g, cosine
distance) between datasets as the reward. (ii) Learning difficulty for measuring the perplexity changes. (iii) Learning
trajectory for smoothing the reward values using Exponential
Moving Average (EMA) to more stably optimize the sampling
distribution.
(2) Training Strategy. In addition to directly prune the
dataset during training, appropriate learning strategies can
also alleviate catastrophic forgetting.
[123] found that different abilities vary with data volume, with mixed data
improving abilities at low res


## 2.5.2
Data Compression
Data compression refers to compressing the input data for the

model. Previous studies have shown that prompts are crucial
for triggering LLM domain-specific knowledge, and prompts
are typically designed based on specific tasks (including chainof-thought, context learning, and historical dialogues). As
the complexity of chain-of-thought, context learning, and
RAG increase, longer prompts are required [189]. However,
overly long prompts may lead to higher response latency,
increased costs, and even exceeding the maximum token limit.
Existing methods mainly compress the model inputs in two
aspects. Some methods [427], [101], [348], [200], [335] compress
the retrieved results in the RAG stage and then put them
into the prompt, while other methods compress the entire
prompt [189], [190], [303], [293], [102].
Principles
Compared to traditional machine learning, LLMs often require longer inputs, and in some cases, the input
must be compressed to fit into the model. The main
challenge is how to compress the input without losing important information. Current methods mainly
achieve this through compression based on information entropy, rule-based templates, or model-driven
approaches.


# 32

RAG Knowledge Compression The retrieved RAG knowl-

edge can be compressed by a model to make small texts
carry more information. Techniques like RECOMP [427],
CompAct [348], and FAVICOMP [200] adopt rule-based RAG
context compression schemes, where predefined rules or templates explicitly guide the model to extract key information
and remove redundant content. Alternatively, methods like
xRAG [101] and COCOM [335] use soft prompt-based RAG
context compression schemes, where learnable parameters
(such as the modality projector W in xRAG or the overall
model training in COCOM) enable implicit vector learning.
These implicit vectors dynamically adjust attention weights
when the model processes input, allowing the model to adaptively optimize context representations under context compression.
Prompt Compression. Prompt compression means that
after the retrieved knowledge is put into the Prompt, the
entire Prompt will be compressed.
(1) Metric-Based Compression. Some studies [189], [190],
based on the hypothesis that a vast amount of knowledge is
stored in the model parameters, have proposed methods to
compress prompts while minimizing information loss. LLMLingua [189] uses a perplexity criterion to remove redundant
tokens from the original prompt. By quantifying the negative
logarithmic probability (perplexity) of each token through
a small model, LLMLingua identifies and removes tokens
that can be predicted from the model’s inherent knowledge,
thereby shortening the prompt while retaining essential context.
LLMLingua’s extended version, LongLLMLingua [190],
uses a dual-granularity compression strategy: (i) Coarsegrained compression initially filters key information at the
document level to provide more focused content for finegrained compression; (ii) Fine-grained compression further
optimizes at the token level to precisely retain key information. These two strategies work together to improve the quality of the prompt and model performance. LongLLMLingua
also assigns different “compression budgets” to documents
based on their importance, aiming to achieve the best global
compression effect.
(2) Finetuned-Model-Based Compression. Unlike the aforementioned methods that use a small model’s perplexity for
compression, some methods [303], [293], [102] directly perform
the compression task end-to-end by fine-tuning a model.
LLMLingua-2 [303] defines prompt compression as a problem
of classifying tokens and trains a dedicated model for compression. It uses a Transformer encoder to capture bidirectional
contextual information, ensuring that the compressed prompt
is faithful to the original. [293] proposes a technique called
’gisting’, where a language model is trained to condense the
prompt into a compact ’gist token’. These tokens encapsulate
the core semantic content of the prompt and can be cached for
later use. This method achieves a compression rate of up to 26
times. [102] suggests a method to transform pre-trained language models into AutoCompressors. The AutoCompressor
compresses long contexts into summary vectors, and training
is performed on the model parameters using these summary
vectors.


## 2.5.3
Data Packing
Data Packing aims to address the requirement for uniform

sequence lengths in LLMs’ training inputs, which combines
short texts in an appropriate way to enhance text coherence
and reduce the number of padding tokens. In this way, we
can avoid the excessive truncation caused by the drawbacks of
simple concatenation and splitting methods [116].
Short Sequence Insertion. Some methods [116], [259] involve inserting short sequences into long sequences to minimize padding. The Best-fit Packing [116] first splits long
documents according to the model’s context length, then sorts
all document blocks in descending order of length. For each
document block, it selects the training sequence set with the
smallest remaining capacity that can accommodate it. [259]
prioritizes long documents and uses a greedy algorithm to fill
remaining space with short document segments (sequences),
reducing padding and minimizing document concatenation to
lower contextual noise.
Principles
Compared to traditional machine learning, LLMs
place higher demands on the semantic quality of training data. Additionally, due to the requirement for uniform input lengths, a key challenge is maintaining semantic integrity without excessive truncation. Existing techniques tackle this through short-sequence insertion, sequence concatenation, and semantic-aware
composition. However, it remains crucial to account
for the impact of these data packaging operations on
overall training efficiency.
Sequence
Combination
Optimization.
Some
methods [218], [316] optimize sequence combinations for efficient
packing. [218] proposes two efficient sequence packing algorithms: (1) The Shortest Pack First Histogram Packing
(SPFHP) uses a sequence length histogram, sorts sequences
from long to short, and applies a worst-fit algorithm to
prioritize placing the histogram intervals into the remaining
largest “packs”, while limiting packing depth to avoid creating
excessive small packs, thus improving space utilization. (2)
The Non-Negative Least Squares Histogram Packing (NNLSHP) converts the packing problem into a non-negative least
squares problem, using dynamic programming to enumerate
reasonable sequence combination strategies, constructing a
packing matrix to determine the strategy’s repetition count.
It also assigns small weights to short sequences’ residuals to
reduce long sequence leftovers, achieving efficient packing.
[316] splits documents into multiple fixed-length “buckets”
based on their length, ensuring that each sequence comes from
the same document to avoid cross-document attention issues.
Additionally, by combining Variable Sequence Length Curriculum (VSL), different lengths of sequences are dynamically
sampled during training to maintain a consistent total token
count.
Semantic-Based Packing. Some methods [364], [349] improve data coherence through semantic-based data packing.
[349] reorders pretraining data by combining semantically
related documents into coherent input contexts, allowing the
33

LLM to read and reason across document boundaries. Similarly, SPLICE [364] randomly selects a document as the root
document, and in a breadth-first manner, uses retrieval methods like BM25 and Contriever (trained from a mix of Wiki and
CCNet data) to retrieve k similar documents, adding them
to the training sample until the maximum length is reached.
Finally, the tree structure is flattened using a specific tree
traversal strategy to generate the training example.


## 2.5.4
Data Provenance

Data Provenance is the process of tracking the sources,
transformations, and lineage of data, which is increasingly
recognized critical in ensuring the reliability, transparency,
and accountability of LLM data [54].
Principles
Compared with traditional machine-learning models,
LLMs demand heightened safeguards for output security owing to their powerful generative capabilities.
The central challenge is to preserve output integrity
without degrading quality. Current solutions embed
watermarks or deploy statistical-detection techniques
to reveal any tampering.
Embedding Markers. Current data provenance methods [482], [105], [256], [212] generally modify the generation
logic to embed covert markers into the text. This is done in a
way that does not disrupt the text itself, thereby providing a
medium for tracing the origin of the data.
Bileve [482] enhances the traceability and integrity of text
by embedding two distinct levels of signals: (1) Statistical
signal embedded globally to detect whether the text originates from a specific model. (2) Content-related signature
embedded within each generation unit to verify if the text
has been tampered with. During detection, the validity of the
signature is first verified; if the signature is invalid, a statistical
test is then used to determine whether the text comes from the
target model.
Unlike Bileve that emphasizes strict traceability after text
tampering, [105] focuses on embedding watermarks in a way
that preserves the quality of the generated output. It embeds
hidden markers that can only be detected by individuals
possessing a specific key, while remaining imperceptible to
others that the text has been altered. Specifically, the method
employs a pseudo-random function (PRF, used to generate
seemingly random numbers) to determine the shuffling of each
output word, ensuring that the generated text is statistically
indistinguishable from the original model’s output. During
detection, the presence of hidden markers is ascertained by
calculating a score for each word in the text (based on the
numbers generated by the pseudo-random function).
Unlike previous approaches, UPV [256] introduces a watermarking method that enables detection without requiring
access to the key used during generation, thereby eliminating
the risk of key leakage. It employs two independent neural networks for watermarking. During text generation, the watermark generation network utilizes an embedding module and a
fully connected classifier to predict watermark signals based
on token information within a sliding window, and accordingly adjusts the language model’s output distribution. For
detection, an LSTM-based network takes the text sequence as
input and identifies the watermark, leveraging shared token
embedding parameters with the generation network.
Compared to methods that require specific keys for detection, [131] embeds a special type of watermark into text generated by language models, which can be detected by anyone
without the need for any secret information. It selects specific
lexical combinations (rejection sampling, ensuring that the
embedding of the marker does not affect the naturalness of
the text) during text generation, in conjunction with an error
correction mechanism (error-correcting codes, allowing the
marker to be recovered even after partial modification of the
text), to embed an encrypted signature (public key signature,
ensuring the non-forgeability of the marker) into the text.
During detection, one only needs to extract these specific
lexical combinations from the text and verify the validity of the
signature to determine whether the text contains the marker.
Statistical Provenance. Unlike the aforementioned methods that rely on detecting special markers for tracing the
origin, [212] achieve data provenance through the statistical
information of the vocabulary. Specifically, before generating
each word, the model randomly divides the vocabulary into
two parts (green-listed and red-listed tokens) and tends to
favor the shuffling of green-listed tokens during the generation
process (green-listed tokens are a randomly selected subset of
the vocabulary). By employing statistical tests (a mathematical method used to determine whether text adheres to specific
rules), it is possible to detect whether the proportion of greenlisted tokens in the text is abnormal, thereby ascertaining if
the text is machine-generated.


# 3
LLM for Data Management

After preparing the LLMs with carefully processed / stored /
served data, we next introduce the LLM techniques that can
be utilized to enhance data management tasks, including data
manipulation, data analysis, and data system optimization.


## 3.1
LLM for Data Manipulation
LLM can be employed to explore and prepare appropri-

ate data for non-LLM-oriented tasks, such as data cleaning
for classification tasks, data integration for extracting wellstructured tables from unstructured sources, and data discovery for identifying relevant datasets. Unlike data preparation
pipelines designed specifically for LLM applications, these
methods focus on enhancing the quality and utility of data
for downstream analytical or machine learning tasks.


## 3.1.1
LLM for Data Cleaning
Data cleaning focuses on transforming corrupted or low-

quality data into a reliable form suitable for downstream
applications (e.g., statistical analysis or training machine
learning models). It encompasses a range of tasks such as handling missing values, correcting typos, resolving formatting
inconsistencies, and addressing dependency violations. These
tasks are typically categorized into data standardization, error
detection and correction, and data imputation.
34

2. Data Integration
3. Data Discovery
1. Data Cleaning
Data Manipulation
LLM-GDO
Data Standardization
Prompt-based
Evaporate
Agent-based
Pipeline Generation
CleanAgent
AutoDCWorkflow
Data Error Processing
Prompt-based
Data Imputation
RetClean
RetClean
Multi-News+
RAG Assisted
LLMErrorBench
Prompt-based
LLMClean
Cocoon
Multi-News+
LLM-based
Context Enrichment
LLMError
Bench
Fine-tuning-based
GIDCL
Agent-OM
Schema Matching
Prompt-based
Context-Enriched
RAG
Agent-based
Orchestration
LLMSchemaBench
Magneto 
KG-RAG4SM
Harmonia
BATCHER
MatchGPT
Jellyfish
Entity Matching
Prompt-based
Multi-Model
Collaboration
Localized Multi-Task
Fine-tuning
LEDD
Pneuma
AutoDDG
Data Profiling
Prompt-based
RAG-Assisted
Goby
RACOON
CHORUS
Data Annotation
Prompt-based
RAG-Assisted
Birdie
1. Configuration Tuning
λ-Tune
LATuner
DB-GPT
2. Query Optimization
GenRewrite
LITHE
LLMSteer
GPTuner
Andromeda
R-Bot
Prompt-based
RAG-based
Enrichment
Traning-Enhanced
Alignment
DB-GPT
E2ETune
Prompt-based
RAG-based Enrichment
LLM-QO
Training-Enhanced
Improvement
3. Anomaly Diagnosis
DB-GPT
ByteHTAP
Prompt-based
RAG-based Enrichment
Multi-Agent Collaboration
Localized Specialized
Fine-tuning
D-Bot
Panda
D-Bot
D-Bot
Data System Optimization
1. Structured Data Analysis
PACHINCO
DataCoder
Multi-Step
QA
NL2SQL
End-to-end 
QA
2. Semi-structured Data Analysis
TAPERA
Extractor 
ReAcTable
CABINET
TableGPT
TabPedia
SPREADSHEET
BENCH
MiMoTable
 Semi-structured
Tables
Relational Data Analysis
Data Analysis
NAT - NL2GQL
 -NL2GQL
LLM-based
Semantic
NL2GQL
FlexKBQA 
UniKGQA 
GraphGPT 
Graph Data Analysis
3. Unstructured Data Analysis
Documents
UDOP
DocPedia
Pix2Struct
Programming
Language
RepoFusion
CoCoMIC
COMEM
Fig. 8: Overview of LLM4DATA Techniques.
Traditional data cleaning methods depend on rigid rules
and constraints (e.g., zip code validation), demanding substantial manual effort and domain expertise (e.g., schema
knowledge in financial data) [237], [432]. Additionally, they
often require domain-specific training, which restricts their
generalizability [63]. Recent studies show that large language
models (LLMs) can address these limitations by offering natural language interfaces that reduce manual and programming
effort, eliminate the need for complex runtime environments,
and support seamless integration of domain knowledge. These
methods primarily target the following tasks.
Data Standardization. Data standardization involves converting diverse, inconsistent, or non-conforming values into
a consistent format to ensure reliable analysis and effective
downstream processing. Existing methods use either structured LLM prompting for specific cleaning operations or
LLM agents for automated pipeline generation.
(1) Prompt Based End-to-End Standardization. The
first approach constructs well-structured prompts with explicit standardization instructions and employs advanced
prompting techniques (e.g., Chain-of-Thought) to improve
the effectiveness of LLM-based standardization methods.
For example, LLM-GDO [279] utilizes user-defined prompts
(UDPs), including in-context learning examples, to implement
LLM-based operators that replace traditional user-defined
functions (UDFs) across various standardization tasks (e.g.,
normalizing numerical values). This method simplifies logic
implementation and facilitates the seamless integration of domain knowledge. Evaporate [63] employs LLMs to transform
semi-structured documents into structured views through
two main strategies: (i) Evaporate-Direct, which prompts the
LLM to extract values directly, and (ii) Evaporate-Code,
which guides the LLM to synthesize extraction code and ensembles multiple candidate functions using weak supervision
to improve output quality while maintaining low cost.
(2) Agent Based Operation and Pipeline Generation. To address the inefficiencies of LLM-based solutions, such as the reliance on multi-turn prompts and
expert-level prompt engineering, the second method employs
LLM agents to automatically generate cleaning operations
and orchestrate end-to-end pipelines. For instance, CleanAgent [319] integrates domain-specific APIs with autonomous
agents to execute a standardization pipeline that includes
API call generation (e.g., clean
date(df, ‘‘Admission
Date’’, ‘‘MM/DD/YYYY’’)) and iterative code execution.
Similarly, AutoDCWorkflow [237] adopts LLM agents to construct pipelines for resolving duplicates and inconsistent formats. The agent performs step-by-step reasoning to identify
relevant columns, evaluate data quality, and generate appropriate operations (e.g., upper() and trim()), wh


# 35

repairs through iterative feedback from integrated correction

tools such as Baran. LLMErrorBench [74] employs LLM
agents equipped with Python (via IPython) and prompted
with task-specific instructions and contextual hints (e.g., error
locations) to explore, modify, and repair datasets iteratively.
Corrections (e.g., value replacement, missing data handling)
are guided by performance feedback from pre-defined code
execution and evaluation pipelines.
(3) Fine-tuning Based End-to-End Error Processing.
To improve error correction accuracy while preserving computational efficiency and model adaptability, the third approach
fine-tunes LLMs to capture dataset-specific patterns and
dependencies that are typically difficult to model through
prompting alone. For example, GIDCL [432] fine-tunes a local
LLM (e.g., Mistral-7B) using Low-Rank Adaptation (LoRA)
to optimize error correction, constructing training data from
labeled tuples and pseudo-labeled tuples generated via LLMbased augmentation, with each training instance formatted as
a context-enriched prompt comprising: (i) an instruction (e.g.,
“Correct the ProviderID to a valid numeric format”), (ii) a
serialized erroneous cell with row and column context (e.g.,
“<COL>ProviderID<VAL>1x1303...”), (iii) in-context learning demonstrations (e.g., “bxrmxngham →birmingham”),
and (iv) retrieval-augmented examples from the same cluster
(e.g., clean tuples via k-means).
Data Imputation. Given a data entry with missing attribute
values (e.g., NULL), data imputation aims to infer the missing values using available contextual information accurately.
Existing methods either (i) use structured prompts to convey
contextual hints to LLM, or (ii) apply retrieval-augmented
generation (RAG) to integrate relevant external data.
(1) Prompt Based End-to-End Imputation. To incorporate contextual information for imputing missing values, the
first approach constructs structured prompts. For example,
RetClean [129] enhances LLM effectiveness by serializing each
tuple into a formatted representation (e.g., “[Name: John;
Age: 25; Gender: NULL]”) and pairing it with a targeted
question such as “What is the correct value for Gender?”.
This prompt design enables the LLM to generate accurate,
context-aware missing values.
(2) RAG Assisted Localized Imputation. To enable online LLMs in handling unseen, domain-specific, or private
datasets, the second approach adopts the retrieval-augmented
generation (RAG) paradigm. For example, RetClean [129]
introduces a retrieval-based data cleaning framework that
indexes a data lake using both syntactic (Elasticsearch) and
semantic (Faiss/Qdrant) methods. It retrieves the top-k relevant tuples, reranks them (e.g., using ColBERT), and then
leverages an LLM to infer missing values, while maintaining
lineage tracking for transparency and traceability.


## 3.1.2
LLM for Data Integration

Data integration aims to align elements across heterogeneous
datasets to enable unified access, analysis, and knowledge extraction. For instance, it includes identifying tables or records
that correspond to the same real-world entity. Moreover, it
facilitates downstream tasks such as data augmentation by
establishing semantic relationships across sources.
Traditional integration methods often struggle with semantic ambiguities and conflicts, particularly in complex integration scenarios without domain-specific knowledge [277].
Furthermore, classical models (e.g., pretrained models) generally require large amounts of task-specific training data and
tend to degrade in performance when encountering out-ofdistribution entities [308]. In contrast, recent studies have
shown that LLMs possess strong semantic understanding,
enabling them to uncover correlations across datasets and incorporate domain-specific knowledge, thereby offering robust
generalization across diverse integration tasks.
Entity Matching. The goal of entity matching is to determine whether two entries refer to the same real-world entity.
Existing methods leverage LLMs through well-structured
prompts and advanced reasoning mechanisms, incorporate
multiple models for collaborative matching, and apply multitask fine-tuning to further enhance performance.
(1) Prompt Based End-to-End Matching. To improve
LLM’s effectiveness on matching tasks, the first approach
crafts well-structured prompts and integrates auxiliary mechanisms to strengthen the robustness of the reasoning process.
• Manually-Crafted Prompt. This method incorporates detailed instructions and illustrative examples into the prompts
to guide LLM in performing entity matching more effectively.
For example, MatchGPT [308] evaluates the performance of
both open-source and closed-source LLMs (e.g., Llama 3.1
and GPT-4o mini) with (i) different prompt designs, (ii)
the selection of in-context demonstrations, (iii) automatic
generation of matching rules, and (iv) fine-tuning LLMs using
a shared pool of training data. To reduce inference costs,
BATCHER [134] introduces a batch prompting method that
allows multiple entity pairs to be processed simultaneously.
It optimizes in-context learning by (i) grouping entity pairs
into a single prompt and (ii) applying a greedy cover-based
strategy to select demonstrations such that each query in the
batch is semantically close to at least one example.
• Pseudo-Code Guided Reasoning. To mitigate hallucinations
arising from over-reliance on an LLM’s internal knowledge,
this method integrates external formalized representations
to enhance the robustness and reliability of the reasoning
process. For example, KcMF [430] guides LLMs using expertdesigned pseudo-code instructions structured as a sequence of
if-then-else logical conditions, combined with external domain
knowledge (e.g., datasets and examples). It further adopts an
ensemble strategy by generating outputs from different knowledge sources (e.g., Wikidata and domain-specific datasets)
and applies a voting mechanism to aggregate results, improving consistency and accuracy.
(2) End-to-End Matching with Multi-Model Collaboration. To leverage the strengths of different models
across tasks, the second approach employs collaborative entity matching using models of varying sizes. For example,
COMEM [400] introduces a compound entity matching framework that combines multiple strategies with LLM collaboration to address global consistency, which is often ignored
in binary matching. It employs (i) a local strategy using a
medium-sized LLM (3B-11B) as a matcher or comparator
to rank top-k candidates via bubble sort, reducing position
bias and context length dependency; and (ii) a global selection
strategy using a stronger LLM (e.g., GPT-4o) to refine top-k
candidates by modeling inter-record interactions.
(3) Localized LLM Fine-tuning of Multi-Task Learning. To enhance the generalization capability of local LLMs,
the last approach integrates multiple task-specific datasets
36

within a unified multi-task instruction tuning framework. For
example, Jellyfish [454] applies parameter-efficient instruction
tuning to locally deployed LLMs (7B-13B) across diverse
data processing tasks. It employs techniques such as chainof-thought prompting over task-specific serialized data and
reasoning data distillation, using explanation traces generated
by a larger mixture-of-experts model (Mixtral-8x7B-Instruct)
to guide the learning process.
Schema Matching. The objective of schema matching is
to identify correspondences between elements of different
database schemas (e.g., matching attribute names “employee
ID” and “staff number”). Existing approaches directly apply
prompting techniques to enable LLMs to perform end-to-end
matching, utilize retrieval-augmented generation (RAG) to
enhance contextual understanding, and employ LLM agents
to orchestrate the overall matching workflow.
(1) Prompt Based End-to-End Matching. To facilita


## 3.1.3
LLM for Data Discovery
Data discovery focuses on identifying relationships within

datasets through tasks like data annotation (e.g., column type
classification) and profiling (e.g., metadata generation). Unlike data analysis, which emphasizes statistical computations
or factual answer generation, data discovery enables deeper
semantic understanding critical for downstream applications
such as integration, search, and recommendation.
Existing data discovery methods face two limitations.
First, they typically consider limited interaction between
queries and tables [163]. Second, many of these approaches
rely heavily on large training datasets, struggle with distribution shifts, and fail to generalize to rare or domain-specific
data [143], [217]. Recent studies have shown that LLMs can
effectively address these challenges by generating high-quality
metadata, enriching dataset context, and supporting natural
language interfaces for data discovery tasks.
Data Profiling. Data profiling typically involves characterizing a given dataset by generating additional information
(e.g., dataset descriptions). Recent methods often employ
prompting techniques to guide LLM in generating such metadata by leveraging their pretrained knowledge and contextual
understanding.
(1) Manually Crafted Profiling Prompt Engineering.
To profile different aspects of a dataset without extensive
manual effort or code implementation, the first approach relies
on a set of manually crafted profiling prompts. For example,
AutoDDG [456] utilizes LLM with carefully designed prompts
to generate two types of descriptions (i.e., User-Focused Descriptions (UFDs) for readability and Search-Focused Descriptions (SFDs) for search optimization) tailored to the
dataset’s content and intended usage. LEDD [58] employs
carefully crafted prompts to support core data discovery tasks
in data lakes. For hierarchical cataloging, prompts instruct
LLM to summarize data clusters into semantically meaningful
categories. For semantic search, prompts refine natural language queries before embedding and retrieval. For real-time
relation analysis, prompts guide LLM in comparing expanded
graph nodes and describing inter-table relationships.
(2) RAG Assisted Context Enrichment. To enhance
retrieval effectiveness across diverse query types, the second
method adopts a hybrid approach that integrates diverse
retrieval techniques. For example, Pneuma [72] adopts a RAG
framework to retrieve relevant tables from databases, data
lakes, or repositories based on natural language queries. It
combines LLMs with traditional retrieval techniques, such
as full-text and vector search, using LLMs for both schema
narration (i.e., generating meaningful column descriptions)
and as judges to refine and rerank retrieved results.
Data Annotation. Data annotation involves assigning semantic or structural labels to data elements, such as identifying column types (e.g., Manufacturer or birthDate from
the DBPedia ontology). Recent methods leveraging LLM
typically design prompts with task-specific annotation instructions. Additionally, some approaches employ retrievalaugmented generation (RAG) techniques and the contextual
reasoning capabilities of LLMs to further enrich the annotation context and improve performance.
37

(1) Task-Specific Annotation Prompt Engineering.
To flexibly support diverse annotation tasks, the first approach encodes task-specific instructions and requirements
within carefully crafted prompt templates. For example,
CHORUS [203] integrates LLMs into the annotation pipeline
using task-specific prompts that incorporate instructions,
demonstrations, data samples, metadata, domain knowledge,
and output formatting guidance. Goby [204] explores the
use of LLMs for semantic column type annotation in a
domain-specific enterprise setting by crafting a set of tailored
prompts. It proposes several techniques to improve performance, including tree serialization (providing the full ontology
as prompt context), grammar-constrained decoding (enforcing hierarchical structure during generation), and step-bystep prompting (Chain-of-Thought strategy to guide ontology
navigation). LLMCTA [217] evaluates diverse LLMs for generating and refining label definitions by employing methods
like knowledge generation prompting (e.g., producing initial
demonstrations), self-refinement (error-based definition improvement), and self-correction (two-step pipeline featuring
a reviewer model).
(2) RAG Assisted Annotation Context Enrichment.
To supply LLM with relevant annotation context, the second
approach utilizes diverse retrieval strategies within retrievalaugmented generation (RAG) frameworks to enrich the input.
• Classical Retrieval Technique. To mitigate the shortcomings of vanilla LLM-based annotation, such as outdated
knowledge, this method augments the context with retrieved
external knowledge. For example, RACOON [408] performs
semantic type annotation by leveraging a Knowledge Graph
(KG) to retrieve entity-related information (e.g., labels and
triples) associated with column cell


## 3.2
LLM for Data Analysis

Apart from data manipulation, LLMs hold the potential
to revolutionize traditional data analysis paradigms by supporting natural language interfaces and enabling advanced,
semantic-aware analysis tasks that typically require human
involvement. In this section, we discuss the challenges and
techniques of LLM-based data analysis, including structured
data analysis, semi-structured data analysis, and unstructured data analysis.


## 3.2.1
LLM for Structured Data Analysis

Structured data refers to data with well-defined schemas like
relational (tabular) data [107] and graph data [60].
Data Analysis
Structured
Relational Data
LLM as
NL-Interface
NL2SQL [452],
[247], [370], [234],
[229], [317], [234]
NL2Code [443],
[104], [176], [171]
SemanticAware
Multi-Step QA [494],
[226], [475], [464], [404]
End-to-End QA [240],
[365], [306],
[82], [477], [471]
Graph Data
LLM as
NL-Interface
NL2GQL [252], [493]
SemanticAware
Retrieval-ThenReasoning [458], [193]
Execution-ThenReasoning [424], [246]
Fine-Tuning
Based [441], [397], [375]
Agent Based [192], [100]
Semi-Structured
Markup Language
Semi-Structured
Tables [165], [281], [245]
Unstructured
Document
OCRDependent [376],
[62]
OCR-Free
Text Masked
Learning [225], [49]
Visual Embedded
Learning [174], [138]
Program Language
Vulnerability
Detection
Program Analysis
Based [271], [457]
Case-driven Prompt
Engineering [270], [492]
SemanticAware
Code Summarization
[154], [51], [284]
Code Completion
[357], [118], [413]
Fig. 9: Overview of LLM for Data Analysis.


## 3.2.1.1 Relational Data Analysis

LLM for Natural Language Interfaces. Basic analysis
jobs for relational data are typically characterized by welldefined operations. These include basic calculations (e.g.,
summation, averaging, counting, ranking), statistical analysis
(e.g., regression, K-means clustering), and data quality assurance processes (e.g., constraint validation, outlier detection).
Such tasks can generally be supported by tools like SQL or
Python libraries (e.g., Pandas).
(1) NL2SQL. With the help of LLM, users can directly perform operations using natural language. NL2SQL focuses on
translating natural language queries into SQL commands by
leveraging techniques such as (i) schema linking, which aligns
user intents with database schema to resolve ambiguities [452],
[247], (ii) content retrieval, which dynamically extracts relevant information from the database to refine query generation [370], [234], and (iii) SQL generation strategies such as
multi-step generation, intermediate SQL representation, and
different decoding strategies [229], [317], [234], [483], [484].
(2) NL2Code. Different from NL2SQL, NL2Code approaches


# 38

Question
Table
Intermediate
Table
Processor
Output
Input
Iterative
SQL
Python
LLM

Tools
LLM /
MLLM
(1) Pre-Train 
(For MLLM)
(2) Fine-Tuning
(For LLM / MLLM)
Question
Table
Answer
Image Caption
Table Recognition
Table QA
Fact Verification
...
(a)
(b)
End-to-End
LLM
Answer
Fig. 10: General Workflows - (a) Multi-Step Relational
Data QA. (b) End-to-End Relational Data QA.
emphasize enhancing relational data analysis through generating Python code (e.g., Pandas, NumPy), which includes a
vast number of library APIs characterized by high variability
and complexity, and often requiring the handling of complex
chain operations. Recent advancements address these issues
to some extent.
• Model Finetuning: PACHINCO [443] fine-tunes a 62B parameter PALM [104] model in two stages (i.e., separately
using a Python source code corpus with 64B tokens and a
Jupyter notebook corpus with 9.6B tokens) so as to improve
model performance on analysis-related tasks (e.g., calculate
the amount of games added in each year for each month).
DataCoder [176] utilizes different types of contexts (e.g., code,
text, and data) by employing dual encoders (e.g., data encoder
and code + text encoder) and one general decoder to generate
code in notebooks.
• LLM Based Analysis Agent: Data Interpreter [171], on
the other hand, leverages LLMs through APIs to generate
task and action graphs. Specifically, they utilize LLM’s semantic reasoning ability to accurately decompose complex
user queries into subproblems (e.g., correlation analysis, data
exploration, and anomaly detection), and refine and verify
each subproblem to improve code generation results for data
science tasks.
LLM for Semantic Analysis. Moreover, some jobs require
LLM-based analysis, such as those that involve semantic
understanding or demand outputs in natural language format (e.g., table summarization). These challenges call for
methodologies like (1) multi-step question answering (QA)
with diverse decomposition strategies and (2) end-to-end QA
leveraging specifically optimized LLMs.
• Multi-Step QA. Multi-step question answering (QA) refers
to decomposing complex queries into a sequence of subquestions to facilitate step-by-step reasoning. According to
the question decomposition mechanisms, existing methods
can be categorized into two types: (1) static decomposition,
which follows predefined and fixed processing steps (e.g.,
retrieve-select-reason), and (2) LLM-driven iterative decomposition, in which the LLM dynamically determines the next
operation based on the contextual history of the reasoning
process.
(1) Static Decomposition. The static decomposition includes
Retriever-Selector-Reasoner frameworks and the variants,
which partition tasks into modular components for better multi-step inference and enhanced interpretability. The
Extractor-Reasoner-Executor paradigm [494] extracts the relevant segments from the context, generates the logic rules or
equations, and performs the rules or executes the equations to
get the final answer through LLM prompting. S3HQA [226]
trains a retriever which aims to perform initial filtering of
heterogeneous resources, utilizes a selector to select the most
relevant factual knowledge, and a generation-based reasoner
to obtain final answers.
(2) Iterative Decomposition. However, static decomposition
paradigm performs poorly on multi-hop queries, while LLMdriven iterative decomposition, which dynamically refines
subtasks through recursive reasoning, could effectively address the issue.
TAPERA [475] introduces the query decomposition step
into the question answering process by adopting the LLMdriven approach. The Planner decomposes the query into subqueries, forming an initial plan. The Reasoner then generates
executable programs for each sub-query, while the Answer
Generator derives answers based on the program outputs to
fulfill the plan. Finally, the Planner updates or finalizes the
plan as needed.
Similarly, ReAcTable [464] and CHAIN-OF-TABLE [404]
iteratively generate operations and update the table to
present a reasoning chain as a proxy for intermediate thoughts
through prompting LLMs and in-context learning.
• End-to-End QA. End-to-End Question Answering (QA)
refers to approaches in which the answer-generating LLM directly produces the final response without intermediate steps
or iterative refinement. Based on the data representation and
processing mechanisms, the relevant methods can be classified
into table-specific LLM fine-tuning, table content retrieval,
and table-as-image analysis.
(1) Table-Specific LLM Fine-Tuning. Fine-tuning LLMs on
task-specific
table
datasets
enables
them
to
internalize analytical knowledge directly within their parameters.
TableGPT [240] fine-tunes LLMs like GPT-3.5 using a diverse
set of table tasks synthesized from real-world tables. Building
on Qwen2.5 [324], TableGPT2 [365] introduces a table encoder
to generate a hybrid table representation, an adapter to generate query representations, and a LLM decoder generates an
agent workflow (i.e., the tool execution pipeline) to derive the
final 


## 3.2.1.2 Graph Data Analysis

Different from relational data, graph data represents entities (vertices) and their inter-dependencies (relationships) to
explicit model of complex network semantics (e.g., social
networks and knowledge graphs) beyond rigid tabular schema,
which presents unique challenges due to the vast search
space and complex path reasoning in multi-hop queries [59].
Compared with relational data analysis, graph data analysis
involves more complex jobs like summarization based on the
multi-hop relations across the graph vertices and reasoning
over text-attributed graphs whose nodes and edges are associated with text [252], [493]. Graph data can not only be
stored in relational databases, but also be stored and queried
in knowledge graphs and accessed through SPARQL in RDF
databases (e.g., Blazegraph [8] and GraphDB [21]) or Cypher
in Neo4j [17].
Traditional graph analysis (e.g., statistical methods, graph
neural network (GNN) based methods) encompasses a spectrum of tasks, including node classification (e.g., categorizing
academic papers into research domains), graph classification
(e.g., predicting node properties over molecular graphs), link
prediction (i.e., inferring latent relationships between graph
nodes), community detection (i.e., identifying densely connected subgraphs), anomaly detection (i.e., identifying deviations from expected patterns), graph clustering, and etc.
However, these methods have their own limitations. Statisticsbased methods fail to handle complex semantic information
(e.g., query can be extremely complex and requires human expertise), while graph neural networks (GNNs) exhibit limited
generalization capabilities, necessitating task-specific retraining on different tasks.
In contrast, the advent of LLMs offers transformative potential by leveraging their advanced reasoning capacities and
cross-domain generalization abilities, which can (1) simplify
the query writing costs (e.g., NL interfaces) and (2) achieve
semantic-aware analysis unsupported in traditional ones.
Natural Language To Graph Analysis Query. Different
from NL2SQL, the syntax of graph query language generation
is more complex (i.e., MATCH, LOOKUP, GET and other
operations unique to graph data manipulation) and there exist
two operation objects (i.e., vertex and edge) [493]. By integrating natural language interfaces with graph data, LLMs
facilitate flexible and efficient query generation without the
need for specialized model architectures.
To enhance LLMs’ comprehension of the complex syntax of Graph Query Language (GQL), R3-NL2GQL [493]
proposes a hybrid approach leveraging relatively small LLM
(e.g., LLaMA3-7B) as a selector and GQL rewriter, while employing a larger LLM (e.g., GPT-4) as a reasoner. The selector
identifies the necessary CRUD functions, clauses, and schema,
while the rewriter refines the query by aligning it with the
relevant graph data retrieved by minimum edit distance and
semantic similarity calculation. The LLM then synthesizes the
aligned question, selected operations, and schema to generate
the final GQL query.
To address the limitations of LLMs in planning and collaborating with other LLMs, NAT-NL2GQL [252] introduces
a three-agent framework. The Preprocessor agent constructs
context information, including query rewriting, path linking,
and the extraction of query-relevant schemas. The Generator
agent, an LLM fine-tuned with NL-GQL data, generates
GQL statements based on the rewritten queries and extracted
schemas. The Refiner agent iteratively enhances the GQL
or contextual information by leveraging error feedback from
GQL execution results.
Note
that,
within
the
context
of
AI
for
Science
(AI4Science), the integration of LLMs with graph data analysis has also shown significant potential and wide-ranging
applications (e.g., treat polymers as graphs and predict their
properties [242], [309]), which is not the primary focus of this
survey.
LLM-based Semantic Analysis. Furthermore, certain jobs
necessitate semantic-aware analysis, such as summarizing textual paragraphs embedded within graph nodes. Based on
the adopted LLM strategies, we classify the relevant methods into retrieval-then-reasoning methods, execution-thenreasoning methods, graph task based fine-tuning methods,
and agent based methods.
•
Retrieval-Then-Reasoning.
Retrieval-then-reasoning
first extracts a question-specific subgraph from the graph
to identify the most relevant entities and then generates
answers using LLMs. To address the challenge of a vast search
space, [458] introduces a two-stage approach. First, a trainable
and decoupled subgraph retriever selects a relevant subgraph
based on the query. Then, reasoning is performed over the
retrieved subgraph to derive the final answer. UniKGQA [193]
integrates retrieval and reasoning within a unified model architecture. It comprises a semantic matching module, leveraging a pre-trained RoBERTa [266] for the semantic alignment
between questions and relations in graphs, and a matching
informat


## 3.2.2
LLM for Semi-Structured Data Analysis

Semi-structured data refers to data that are neither with
strictly predefined schema like relational models nor raw data
(e.g., plain text or images) [48]. Meanwhile, they still maintain
part of organizational properties (e.g., tags, headers) and have
hierarchical or nested representation (e.g., County - Province
- City in a nested JSON).


## 3.2.2.1 Markup Language

Markup languages (e.g., XML, JSON, and HTML) are widely
used for structuring and exchanging data across systems.
Traditional approaches for processing these formats typically
involve transforming them into structured tables or representing them as hierarchical tree structures. Leveraging the
reasoning capabilities of LLMs, it becomes possible to directly
extract and interpret hierarchical relationships, attributes,
and nested structures from data without the need for intermediate transformations.


## 3.2.2.2 Semi-Structured Tables

Compared to structured relational data, semi-structured tables exhibit a more complex structural organization characterized by merged cells. This inherent complexity presents a
significant challenge in aligning queries with the table content
and structure in query answering tasks. The lack of efficient
tools (usually using the openpyxl library) and representation
methods (usually stored in Excel or HTML files) for handling
semi-structured tables makes it more difficult to process such
data.
Although research on semi-structured table analysis is
limited, several studies have compiled various semi-structured
table reasoning datasets, providing valuable data support.
TEMPTABQA [165] consists of 11,454 question-answer
pairs focused on temporal queries, while SPREADSHEETBENCH [281] presents a challenging benchmark for spreadsheet manipulation, with 912 questions derived from realworld scenarios. MiMoTable [245] incorporates reasoning
across multiple sheets and files, containing 1,719 queries
within 428 spreadsheets. Evaluation results on these benchmarks highlight a significant performance gap (ranging from
20% to 50%) between state-of-the-art models and human
performance, calling for further exploration in this area.


## 3.2.3
LLM for Unstructured Data Analysis

Unstructured data refers to data that lacks explicit structure,
as it does not adhere to a predefined schema. Additionally,
it exhibits high variability in format, length, and modality,
which further complicates its processing and analysis.


## 3.2.3.1 Documents
Documents exhibit complex layouts and styles with diverse

elements, including a hybrid of images, tables, charts, plain
text, and formulas.
• OCR-Dependent Methods. OCR-based methods refer to
approaches that involve performing Optical Character Recognition on document images, followed by the integration of
textual, layout, and visual features for reasoning. UDOP [376]
integrates text and layout modalities within a unified encoder,
dynamically fusing image patch tokens and text tokens based
on their spatial information. Specifically, when the center of
a text token’s bounding box falls within an image patch, the
corresponding image patch embedding is added to the text
token embedding, enabling a more cohesive representation
of document structure. DocFormerV2 [62] preserves the integrity of layout information by employing a visual encoder.
Image patches and text bounding box positions are embedded
through a linear layer and added to the corresponding token
embeddings as input to the T5 [331] encoder. To achieve local
feature semantic alignment, the model undergoes pretraining
on token-to-line (i.e., predict whether a key-value pair is
on the same line or adjacent lines) and token-to-grid (i.e.,
predict each token located in which image grid) tasks. The
T5 decoder is then incorporated to fine-tune the whole model
on downstream tasks.
• OCR Free Methods. However, the OCR step often introduces semantic errors, resulting in suboptimal performance.
To fill this gap, OCR-free methods have emerged, directly
generating the target token sequences with end-to-end multimodal LLMs [257], [407]. Based on different approaches to
enhancing model understanding of textual semantics, related
works can be categorized into text masked learning and visual
embedded learning.
(1) Text Masked Learning. Text Masked Learning involves
masking textual content within a document and training
41

the model to predict the missing text. Pix2Struct [225] is a
typical vision-encoder-text-decoder pre-trained image-to-text
model designed for visual language understanding based on
ViT [124]. It is pretrained to parse masked web pages into
simplified HTML. The model introduces a variable-resolution
input representation, rescaling input images to maximize the
number of patches that can fit within the given sequence
length, to prevent aspect ratio distortion. DUBLIN [49] designed multiple fine-tuning tasks (i.e., bounding box prediction based on given text, text prediction based on given
bounding box, masked text generation, and query answering)
to improve the generalization ability.
(2) Visual Embedded Learning. In Visual Embedded Learning, there are no specially designed training objectives. Instead, the model is directly fine-tuned on downstream tasks to
enhance its understanding of textual content within images.
mPLUG-DocOwl1.5 [174] introduces a spatial-aware visionto-text module designed for representing high-resolution,
text-rich images. This module preserves structural information while reducing the length of visual features. It consists
of a convolution layer to shorten the sequence length and a
fully connected layer that projects visual features into the
language embedding space. Unlike most methods that crop
or resize the initial image before feeding it into a vision
encoder, DocPedia [138] directly processes visual input in the
frequency domain. It utilizes JPEG DCT [388] extraction to
obtain DCT coefficients, which are then processed using a
frequency adapter before being input into the vision encoder.
This approach allows the model to capture more visual and
textual information while using a limited number of tokens.
The performance improvement observed in the experiment
suggests that this method offers a novel approach for processing high-resolution images.


## 3.2.3.2 Program Language Analysis

Programming language analysis involves multiple levels of
abstraction, including lexical analysis, parsing, and semantic
analysis, each requiring distinct techniques to process source
code effectively. Additionally, it must handle both local and
global information, such as variable scopes, function call
chains, and complex dependencies, which pose significant
challenges for accurate program understanding.
LLM as Program Vulnerability Detection Tools. Recent advancements in LLMs have opened new avenues for
improving vulnerability detection tools. Training LLMs based
on program analysis techniques enhances their ability to understand programs at both the lexical and syntactic levels.
Leveraging in-context learning through case-driven prompt
engineering enhances the model’s accuracy by providing relevant examples.
• Program Analysis based Training. Static and dynamic program analysis are commonly used methods for
detecting vulnerabilities in programs. By assisting these processes, LLMs improve the accuracy of vulnerability detection.
PDBER [271] is a model fine-tuned on CodeBERT [141]
through three tasks (i.e., Predicting Masked Tokens, Predicting Statement-Level Control Dependencies, and Predicting
Token-Level Data Dependencies). This enables more finegrained vulnerability analysis at the statement level. To reduce the impact of irrelevant information, [457] decomposes
the control flow graph (CFG) into multiple execution paths
from the entry node to the exit node. CodeBERT and a CNN
are employed to capture intra-path and inter-path representations, respectively. The extracted feature vectors are then
combined as a unified program representation, which serves
as input to a MLP classifier for vulnerability detection.
• Case-driven Prompt Engineering. Leveraging the incontext learning and few-shot learning capabilities of LLMs
can significantly improve their accuracy in vulnerability detection. VUL-GPT [270] uses GPT-3.5 to generate analysis content (i.e., the program interpretation) for the input code and
retrieves similar code snippets and corresponding vulnerability information through BM25 [338] or TF-IDF. The retrieved
information, along with the original code and analysis, is then
input into GPT to detect vulnerabilities. [492] designs various
prompts, such as random code samples and retrieve-based
code samples, and demonstrates that GPT-4 outperforms
state-of-the-art models in vulnerability detection.
LLM-based
Semantic-aware
Analysis.
Traditional
semantic-aware tasks convert programs into ASTs [362] or
graph structures [151] and train Seq2Seq models to learn
program syntax, dependencies, and semantics. However,
these approaches lack general knowledge, leading to limited
generalization ability. By leveraging the world knowledge and
few-shot learning capabilities of LLMs, the performance of
tasks such as code summarization and code completion has
been significantly improved.
• LLM as Code Summarizer. Recent advancements in
LLM-powered code summarization focus on retrieving similar
code snippets and leverage LLMs’ few-shot learning capability
to enhance performance. [154] retrieves similar code examples
by measuring token overlap and the cosine distance between
embedding vectors of code snippets. In contrast, [51] employs
the BM25 algorithm and incorporates repository information,
data flow information, and variable information to construct
three-shot prompts. SCLA [284] further enhances code semantics in LLM prompts by preprocessing the code sample pool to
extract semantic information. By simultaneously leveraging
few-shot learning, it achieves state-of-the-art performance
based on Gemini-1.5-Pro.
• LLM as Repository-Level Code Completer. Repository
context (e.g., imports, related classes, etc.) plays a crucial role
in code completion. Given the strong semantic understanding
and generative capabilities of LLMs, how to integrate contextual information into code completion has become a key research focus. RepoFusion [357] appends the surrounding text
of the target code to the repository context retrieved based
on BM25, encoding and concatenating them as input to the
decoder for code generation. This approach enables the model
to produce context-aware code completions by leveraging
both local and repository-level information. CoCoMIC [118]
proposes a more robust retrieval method based on program
dependency graphs. Given an incomplete program, it retrieves
the most relevant context by analyzing file imports within
the constructed graph. By defining the relevant context as
files within a two-hop neighborhood, this approach mitigates
the risk of excluding vital dependencies while avoiding the
inclusion of irrelevant information. However, some researchers
have found that simple retrieval methods fail to improve
performance in up to 80% of cases and may even degrade performance due to the inclusion of irrelevant information [413].
42

As a result, Repoformer introduces a self-supervised learning
approach to enable


## 3.3
LLM for Data System Optimization

This section presents the application of LLM to optimize
the performance of different data systems across three key
tasks: (1) Configuration Tuning: selecting effective system
configurations, such as database knobs and indexes; (2) Query
Optimization: accelerating input SQL queries through logical
rewrites and physical plan selection; (3) Anomaly Diagnosis:
addressing system anomalies, such as spikes in the usage of
specific system resources.


## 3.3.1
LLM for Configuration Tuning

Configuration tuning aims to identify effective configurations,
such as database knobs [231], [474] and indexes [485], [487],
[486], to optimize the system performance. Traditional tuning
approaches, including rule-based methods and learning-based
techniques with classical machine learning models, often require extensive explorations without a promising starting
point [231]. Furthermore, they might result in sub-optimal
configurations, despite using advanced techniques such as
transfer learning [463], [402].
A key limitation of these methods is the failure to incorporate extensive domain knowledge (e.g., information from
system manuals and public forum discussions) into the tuning
process, relying solely on runtime feedback from benchmark
evaluations to guide optimization. To address this issue, recent
approaches utilize LLM with large-scale domain knowledge to
enhance the tuning process via the following methods.
Tuning Task-Aware Prompt Engineering. The first
method manually designs prompts with informative details
(e.g., system status) to assist LLM in configuration tuning
(e.g., database knobs and indexes). Some approaches further
enhance this by introducing automatic prompt generation
techniques or by formulating it as an optimization problem.
(1) Manually-Crafted Tuning Prompt. Existing methods
design prompts that incorporate essential details (e.g., system
status) tailored to the characteristics of specific tasks. In
particular, the constructed prompts typically consist of the
following components.
• Configuration Task Instruction. To convey the overall
tuning objective, existing methods specify task instructions
in the prompts using chain-of-thought (CoT) and role-playbased guidance. For instance, LLMBench [243] explicitly
defines the goals of three key subtasks in knob tuning: (i)
knob pruning to retain the most influential knobs, (ii) model
initialization to select promising knobs for warm-starting
bayesian optimization, and (iii) knob recommendation to
return optimal configurations for specific workloads. Similarly,
LATuner [132] instructs LLM to identify critical knobs for
warm-starting the tuning process and select promising knobs
as training samples for boosting the sampling procedure.
• Input Tuning Context. To enable LLM to effectively
support the tuning process for specific workloads, existing
methods enrich the tuning context with detailed information. Specifically, prompts are carefully structured to include:
(i) Configuration Specifications: list of tunable knobs (e.g.,
names and allowable value ranges) and usage descriptions,
including fixed-task demonstrations (e.g., LLMBench [243],
LATuner [132]); (ii) Environment Information: covering workload and database characteristics (e.g., compressed SQL snippets with join conditions in λ-Tune [156]), as well as hardware
settings (e.g., memory size and CPU core count).
• Output Tuning Requirement. To ensure accurate parsing and interpretation of configurations generated by LLM,
output formats are explicitly specified in the prompt. For
instance, LLMBench [243] requires that recommended knob
values be returned in JSON format, while LATuner [132]
enforces constraints such as excluding the use of the “None”
value in the configuration output.
(2) Automatic Tuning Prompt Generation. To improve
the efficiency of prompt generation for different workloads, existing methods propose the following techniques to automate
the process of identifying effective prompts.
• Input Specific Prompt Generation. To identify the most
suitable prompts for varying tasks, existing methods automatically tailor prompt generation based on specific inputs. For
example, DB-GPT [491] introduces an automatic prompt generation framework that leverages LLM to produce multiple
instruction candidates, selecting the optimal ones using scoring functions associated with the performance improvement.
Additionally, DB-GPT [491] and LLMIdxAdvis [473] select
demonstration examples in the prompts based on semantic
similarity between candidate examples and input queries, as
computed by a model-based encoder.
• Optimization Problem Formulation. To reduce token
usage and convey the most relevant context to the LLM,
some methods formulate prompt generation as a cost-based
optimization problem. For instance, λ-Tune [156] compresses
workload representations by modeling the selection of join
conditions as an integer linear programming problem, introducing binary decision variables to capture the positional
relationships of different columns.
RAG Based Tuning Experience Enrichment. The second method builds an offline knowledge base from diverse
external sources and performs online retrieval to provide LLM
with context-specific knowledge (e.g., similar historical tuning cases). This approach addresses the limitations of direct
prompting, which often yields overly generic responses lacking
concrete commands and effective configurations [96].
(1) LLM Based Tuning Experience Preparation. Given
that exi


# 43

utilizes a Sentence-BERT encoder trained with contrastive

learning to generate embeddings, which are then used to
perform similarity searches across various sources, including
historical queries and troubleshooting manuals.
Training Enhanced Tuning Goal Alignment. The third
method introduces additional training to further refine LLMs,
improving their alignment with tuning objectives. For example, DB-GPT [491] proposes techniques to facilitate effective
fine-tuning, including: (i) heuristic statistical data embedding,
(ii) LLM-assisted annotation of high-quality samples, (iii)
contrastive learning of supplementary training data generation, and (iv) delta tuning to minimize trainable parameters while maintaining performance. Similarly, E2ETune [177]
fine-tunes LLMs (e.g., Mistral-7B) using training data comprising “(workload) →(configuration)” pairs, where diverse
workloads are generated via GPT-4 prompting and optimal
configurations are identified using the HEBO algorithm [112].


## 3.3.2
LLM for Query Optimization

Query optimization aims to accelerate SQL execution through
logical (e.g., query rewriting) and physical (e.g., join order
and plan selection) enhancements. Traditional logical optimization relies on predefined rewrite rules or learning-based
approaches to determine rule application order, while physical optimization employs heuristic algorithms using statistical data or learning-based techniques leveraging query plan
features. However, these approaches often overlook external
SQL optimization knowledge, limiting their effectiveness and
generalizability across diverse SQL patterns.
To address these limitations, recent studies investigate
the use of LLM to directly rewrite input SQL queries or
determine optimal rule application sequences for logical optimization. They also explore leveraging LLM to select optimal
query execution plans for physical optimization, drawing on
the extensive SQL optimization knowledge encoded within the
model. These methods can be broadly categorized as follows.
Optimization-Aware Prompt Engineering. The first
method directly employs LLMs to perform query optimization using well-structured prompts composed of two key components: (i) manually crafted templates enriched with taskspecific details (e.g., explicit task instructions), and (ii) relevant optimization examples automatically selected to more
effectively guide the optimization process.
(1) Manually-Crafted Optimization Prompt. Existing
methods construct prompts with the following components to
facilitate the query optimization task.
• Optimization Task Instruction. To clarify the optimization objective and guide LLMs to produce specific optimization actions, detailed task instructions are included
in the prompts. For logical query optimization, some methods instruct LLMs to directly generate equivalent rewritten
queries with improved performance (e.g., DB-GPT [491], GenRewrite [261], and LITHE [363]), while others ask them to
determine the optimal sequence of rewrite rule applications
for a given query (e.g., LLM-R2[248] and R-Bot[369]). For
physical query optimization, some approaches prompt LLMs
to generate complete query plans with specified operators and
join orders (e.g., LLM-QO [196]), while others instruct LLMs
to generate optimization hints or select the most effective plan
from a set of candidates (e.g., LLMOpt [438]).
• Input Optimization Context. To enable effective query
optimization for specific workloads, existing methods augment prompts with additional contextual information to
better inform LLMs. This includes: (i) Database Statistics:
column selectivity [363], histograms, distinct value counts,
and estimated cardinalities [196]; (ii) Rule Specifications: a list
of applicable rewrite rules accompanied by usage descriptions
(e.g., GenRewrite [261] presents natural language hints as the
rules) and illustrative examples [248].
• Output Optimization Requirement. To ensure that
the optimizations produced by LLMs are valid and easily
processed for downstream use, some methods explicitly define output formatting requirements within the prompts. For
example, LLM-R2 enforces that selected rewrite rules be
returned in the format “rules selected: [rule names]” [248],
while LLM-QO specifies that the generated query plan should
follow the “join operator(table1, table2)” format [196].
(2) In-Context Learning with Optimization Example.
Rather than relying on fixed examples to illustrate how LLM
should perform optimization, some methods automatically
retrieve examples that are semantically similar to the input query to provide more effective guidance. For instance,
LLM-R2 [248] introduces a contrastive representation model
to encode query plans based on features such as operators,
cardinalities, and costs, and retrieves a set of high-quality
demonstrations, i.e., successfully optimized rewritten queries.
RAG Based Optimization Experience Enrichment.
The second method adopts the retrieval-augmented generation (RAG) paradigm to equip LLM with relevant contextual
information for targeted optimization of specific queries. It
constructs and retrieves optimization knowledge from multiple sources that are semantically related to the input query.
(1) LLM Based Optimization Experience Preparation.
To consolidate optimization experience from multiple sources,
existing methods introduce an offline preparation pipeline
that leverages LLM to process and integrate data into a unified format. For example, R-Bot [369] employs LLM to generate rewrite rule specifications by (i) summarizing rule code
within a hierarchical structure and (ii) extracting information
from structured documentation blocks. It further uses LLM
to standardize the resulting specifications, explicitly outlining
application conditions and detailed rewrite transformations.
(2) Hybrid Optimization Experience Retrieval. To more
accurately identify relevant optimization experiences, both
structural and semantic characteristics of the input queries are
considered during simil


## 3.3.3
LLM for Anomaly Diagnosis

Anomaly diagnosis focuses on analyzing root causes and identifying recovery solutions for anomalies (e.g., spikes in system
resource usage) during the system runtime, such as databases.
Traditional rule-based methods often fail to accurately identify root causes across diverse scenarios, while classical machine learning models (e.g., random forests) cannot generate
comprehensive reports with detailed recovery solutions.
Recent studies demonstrate that LLMs, with their advanced textual understanding and reasoning capabilities, can
effectively pinpoint root causes and generate detailed diagnosis reports with recovery solutions in various formats. These
LLM-based approaches can be categorized as follows.
Manually Crafted Prompts for Anomaly Diagnosis.
The first method emulates the reasoning process of a human
DBA, which involves referencing essential statistical information and conducting an in-depth analysis during diagnosis.
The information is incorporated into well-structured prompts
to enhance diagnosis accuracy. For example, DBG-PT [155]
utilizes LLM to detect query execution slowdowns caused
by changes in query plans, using prompts that include: (i)
a summary of plan differences, (ii) a request for feasible
configuration recommendations, and (iii) a specification of the
reasoning process with output formatted in JSON format.
RAG Based Diagnosis Experience Enrichment. The
second method adopts retrieval-augmented generation (RAG)
paradigm to provide LLM with relevant diagnosis knowledge,
leveraging two key components: a knowledge base and a
retriever. For instance, D-Bot [490], [489] enhances database
anomaly diagnosis by preparing a corpus of documents and
tools considering the hierarchical document structure, then
using a fine-tuned Sentence-BERT encoder to retrieve relevant materials and guide LLM via prompts enriched with
the retrieved content. ByteHTAP [425] supports LLM-based
diagnosis of query performance regressions in HTAP systems
by first constructing a knowledge base of historical queries and
their associated performance explanations. It then employs an
enhanced tree-CNN classifier to encode and retrieve relevant
plan pairs. The retrieved information is incorporated into
prompts that include: (i) background information (e.g., key
differences among HTAP system engines), (ii) a task description (e.g., retrieved diagnosis knowledge with explicit inputoutput specifications), and (iii) additional user-provided context (e.g., recent index changes).
Multi-Agent Mechanism for Collaborative Diagnosis.
The third method adopts an agent-based diagnosis framework, where specialized agents with distinct responsibilities
collaborate to improve diagnosis accuracy and efficiency. For
example, D-Bot [490], [489] orchestrates multiple domainspecific LLM agents, each aligned with a cluster of preprocessed diagnosis knowledge, to support precise anomaly
diagnosis in databases. These agents, coordinated by a chief
agent, conduct multi-step root cause analysis via a treesearch algorithm. Similarly, Panda [359] emulates experienced
database engineers by leveraging LLM agents across five
functional components: (i) question verification to eliminate
irrelevant queries, (ii) grounding to provide necessary input
query context, (iii) verification to ensure diagnosis accuracy
and source attribution, (iv) feedback integration to incorporate user input, and (v) affordance assessment to estimate the
performance impact of generated solutions.
Localized LLM Enhancement via Specialized FineTuning. The last method employs specialized fine-tuning
strategies for localized LLMs of modest scale (e.g., 6B-14B),
leveraging distilled knowledge to approximate the outputs
of larger models while achieving comparable performance.
For instance, D-Bot [490] applies multi-task fine-tuning to
improve the diagnosis capabilities of localized LLMs. Specifically, three models (i.e., Llama2-13B, CodeLlama-13B, and
Baichuan2-13B) are fine-tuned to replicate the diagnosis results generated by the GPT-4-powered D-Bot. The fine-tuning
dataset consists of samples covering D-Bot diagnosis workflows across five sub-tasks (e.g., tool invocation), along with
associated prompts and historical dialogue messages.
Practices of LLMs for Data Management
Alibaba Cloud [5] has integrated Text-to-SQL features into its BI platform, facilitating NL queries
over structured datasets. Amazon Nova [3] employs
automated document processing to extract structured
information from diverse unstructured sources. In
terms of data systems, PawSQL [41], an advanced
query optimization platform, offers both SQL rewriting and index recommendation capabilities, adopted
by over 10,000 professionals. Database diagnosis also
thrives on a robust ecosystem. For instance, DBDoctor [35], compatible with mainstream databases,
delivers kernel-level performance diagnostics for comprehensive system analysis and optimization.


# 4
Challenges and Future Directions




## 4.1
Data Management for LLM




## 4.1.1 Task-Specific Data Selection for Efficient Pretraining

In LLM pre-training, vast amounts of general data are typically used, but much of this data may not be relevant to
the target task. The inclusion of irrelevant data not only
increases training time but also impedes the model’s adaptability to specific tasks. For instance, when training a model
for the medical domain, unrelated data sources such as news
articles and social media posts may hinder the learning of
domain-specific knowledge. Consequently, the challenge lies
in automatically selecting task-relevant data while discarding
irrelevant information during pretraining. Currently, most
approaches rely on hand-crafted filtering rules or fixed labeled
datasets for data selection, lacking dynamic strategies that
45

adapt to the model’s evolving task-specific needs. Exploring
methods to automatically select relevant data and discard
irrelevant data during pre-training represents a promising
avenue for improving task adaptability and training efficiency.


## 4.1.2 Optimizing Data Processing Pipelines

Currently, the construction of data processing pipelines for
LLMs relies heavily on experience and experimentation. For
instance, in building the FineWeb dataset, decisions such
as whether to use the WET or WARC format for text extraction from CommonCrawl, or whether to apply a global
MinHash approach for deduplication or perform it separately
for each snapshot, are made only after training models and
benchmarking their performance. However, this experimental
methodology is resource-intensive. In the case of FineWeb,
over 70 models with 1 billion parameters were trained, consuming a total of 80,000 H100 GPU hours. To improve the
efficiency of these pipelines, future research should focus on
developing data-driven methods that can predict optimal preprocessing configurations. in advance, reducing the reliance on
costly trial-and-error approaches. This would not only minimize computational costs but also accelerate the development
of high-quality datasets for LLMs.


## 4.1.3 LLM Knowledge Update and Version Control

In fast-evolving domains (e.g., healthcare, finance, law),
knowledge is constantly updated. To ensure the reliability
of LLMs, the data used for training and fine-tuning must
be up-to-date. Delays in incorporating the latest knowledge
can result in outdated or harmful outputs, particularly in
fields like medicine where guidelines frequently change. While
there have been various approaches to data synthesis and
augmentation, little attention has been given to efficiently
managing rapid knowledge updates or resolving contradictions when new information conflicts with older data. Existing
systems often rely on static datasets, which are problematic
in dynamic sectors. Although platforms like ChatGPT and
Deepseek allow LLMs to search the web, this approach may
not always guarantee accuracy or relevance, leading to suboptimal results. A more effective solution would involve a platform that facilitates the creation, sharing, and version control
of datasets with real-time knowledge updates. By leveraging
community-driven contributions, this platform could enable
users to synthesize and share datasets using customizable
methods, such as LLM-generated prompts from documents
or websites, offering continuous, high-quality updates and
improving the overall accuracy and reliability of LLMs.


## 4.1.4 Comprehensive Dataset Evaluation

The performance enhancement of models is closely tied to the
use of ’high-quality’ datasets. However, determining what constitutes a high-quality dataset remains a challenge. Typically,
the quality of a dataset can only be inferred after training
and evaluating a model, which makes the process indirect
and resource-intensive. When a dataset’s quality is subpar,
it can lead to significant computational overhead and inefficiencies. While existing research [393] has proposed a modelagnostic method for evaluating datasets across three aspects:
reliability, difficulty, and validity. These dimensions alone do
not fully capture a dataset’s quality. The current framework
falls short of providing a comprehensive evaluation that aligns
with the model’s capabilities and performance improvements.
Therefore, a promising direction for future research is the development of a robust dataset evaluation system that does not
rely on model training. This system should provide consistent
quality scores that directly correlate with model performance
enhancements, enabling more efficient dataset selection and
use without the need for exhaustive training cycles.


## 4.1.5 Hybrid RAG Indexing and Retrieval

Currently, there lacks a single database that integrates fulltext, vector, knowledge graph, and structured search interfaces into a cohesive indexing and retrieval engine for
Retrieval-Augmented Generation (RAG) training. While systems like Elasticsearch [36] excel in full-text and vector search,
and LightRAG [164] has introduced advanced vector and
graph processing, these solutions remain siloed. They lack a
unified platform designed specifically for hybrid RAG, where
multiple indexing and search mechanisms coexist to support
efficient downstream applications. Although emerging platforms like AutoRAG [209] provide frameworks for constructing RAG pipelines, they focus on workflow management,
model integration, and automation rather than offering a
fully integrated database with indexing and retrieval engines.
A promising direction for future RAG data serving is the
development of an integrated platform that provides seamless
indexing and retrieval for diverse data types, while also integrating data serving features such as knowledge filtering and
re-ranking [47], thereby improving the efficiency and flexibility
of RAG applications.


## 4.2
LLM for Data Management




## 4.2.1 Unified Data Analysis System

One of the major challenges in LLM for Data Analysis is
the absence of a unified system capable of handling diverse
data types. Currently, analyzing different data formats often
requires designing task-specific models separately. The most
straightforward approach to enabling a system to process
all types of data is to integrate these models into a single
framework. However, this leads to prohibitively high deployment and maintenance costs due to the need to manage
multiple models simultaneously. A more promising direction
is to develop a model that can flexibly accommodate various
data inputs and user requirements while supporting the analysis of structured, semi-structured, and unstructured data.
Such a system would establish a paradigm for LLM for Data
Analysis at the system level and offer a generalized capability
for analyzing data across different structural types, thereby
facilitating data automation.


## 4.2.2 Data Analysis with Private Domain Knowledge

Another challenge in leveraging LLMs for data analysis is
the effective utilization of private domain knowledge. Current
approaches primarily rely on RAG to retrieve relevant knowledge or fine-tune models on domain-specific datasets. However, these methods struggle when dealing with novel or highly
complex domain knowledge. For example, in Text-to-SQL
tasks involving large-scale databases with 10,000 columns and
46

1,000,000 rows, where each column is associated with specific
domain knowledge, existing techniques often fail to generalize
effectively. The lack of datasets that explicitly incorporate
domain knowledge further exacerbates this issue, making it
difficult to meet the demands of real-world industrial applications. Consequently, developing more advanced mechanisms
for integrating domain knowledge into LLMs remains a critical
open research problem.


## 4.2.3 Representing Non-Sequential and Non-Textual Data

Current LLM-based approaches typically transform nonsequential and non-textual data into serialized textual formats
to align with the input requirements of LLMs [129], [196],
[438]. While this enables basic compatibility, it overlooks
the original structural semantics of the data and can lead
to significant information loss in downstream tasks. For instance, in data manipulation and analysis, relational tables
(originally structured as two-dimensional matrices) are typically flattened into multiple serialized sequences, obscuring
inherent row-column relationships [78], [74], [319]. Similarly,
in system optimization tasks, crucial statistical signals such
as column selectivities and histograms are either omitted or
naively encoded as plain texts, limiting their utility in guiding
optimization decisions [156], [132]. Consequently, a promising
future direction is to develop more expressive and task-aware
representations that preserve the structural and statistical
integrity of such data. This includes leveraging multi-modal
LLMs or designing tailored encoding strategies that maintain
the uniqueness of these data types, thereby enabling more
effective and semantically informed LLM applications.


## 4.2.4 Efficient LLM Utilization Under Budget Constraints

While LLMs have shown strong potential across data manipulation, analysis, and system optimization tasks, their high
computational cost and latency pose challenges for real-time
or large-scale applications [196], [53]. For example, relying
solely on LLMs is impractical for processing tens of millions
of rows in relational table analysis due to prohibitive resource
demands [432], [304]. Similarly, current LLM-based query
optimizers often require minutes per query, far exceeding
the millisecond-level efficiency of traditional statistical methods [369], [248]. Therefore, a promising direction is to develop
hybrid strategies that integrate LLMs with traditional techniques or to devise scheduling mechanisms that allocate tasks
across multiple LLMs based on cost-performance trade-offs.
Such approaches can enhance the practicality and scalability
of LLM-based systems under real-world budget constraints.


# 5
Conclusion




## Conclusion

In this paper, we summarize the recent techniques on
DATA4LLM and LLM4DATA. The former focuses on utilizing data processing, storage, serving techniques to address
the data problems in different LLM stages. The latter focuses on using LLM capabilities to reduce the complexity
of conducting data management, e.g., data manipulation,
data analysis, and data system optimization. We also provide
some research challenges and open problems in DATA4LLM,
LLM4DATA, and hybrid data and LLM optimization.
References
[1]
https://arangodb.com/.
[2]
https://arxiv.org/.
[3]
https://aws.amazon.com/cn/ai/generativeai/nova/understanding/.
[4]
https://aws.amazon.com/s3.
[5]
https://bailian.console.aliyun.com/xiyan.
[6]
https://beautiful-soup-4.readthedocs.io/en/latest/.
[7]
https://bitbucket.org/product/.
[8]
https://blazegraph.com/.
[9]
https://cachelib.org/.
[10]
https://cocodataset.org/.
[11]
https://commoncrawl.org/.
[12]
https://docs.cohere.com.
[13]
https://docs.python.org/3/library/pickle.html.
[14]
https://github.com/.
[15]
https://github.com/deepseek-ai/3fs.
[16]
https://github.com/juicedata/juicefs.
[17]
https://github.com/neo4j/neo4j.
[18]
https://github.com/paddlepaddle/paddleocr.
[19]
https://github.com/seleniumhq/selenium.
[20]
https://gitlab.com/.
[21]
https://graphdb.ontotext.com/.
[22]
https://huggingface.co/.
[23]
https://huggingface.co/ckiplab/bert-tiny-chinese.
[24]
https://huggingface.co/infgrad/stella-large-zh-v2.
[25]
https://lancedb.com.
[26]
https://milvus.io.
[27]
https://onnx.ai.
[28]
https://openlibrary.org/.
[29]
https://paddlenlp.readthedocs.io.
[30]
https://playwright.dev/.
[31]
https://pptr.dev/.
[32]
https://pytorch.org/.
[33]
https://spacy.io/.
[34]
https://weaviate.io.
[35]
https://www.dbdoctor.cn/.
[36]
https://www.elastic.co/elasticsearch.
[37]
https://www.eyelevel.ai/post/do-vector-databases-loseaccuracy-at-scale.
[38]
https://www.gutenberg.org/.
[39]
https://www.llamaindex.ai/.
[40]
https://www.mindspore.cn/.
[41]
https://www.pawsql.com/.
[42]
https://www.tensorflow.org.
[43]
https://www.tensorflow.org/guide/data.
[44]
https://www.tensorflow.org/tutorials/load
data/tfrecord.
[45]
A. Abbas, E. Rusak, K. Tirumala, W. Brendel, K. Chaudhuri,
and A. S. Morcos.
Effective pruning of web-scale datasets
based on complexity of concept clusters.
arXiv preprint
arXiv:2401.04578, 2024.
[46]
A. Abbas, K. Tirumala, D. Simig, S. Ganguli, and A. S. Morcos.
Semdedup: Data-efficient learning at web-scale through semantic deduplication. arXiv preprint arXiv:2303.09540, 2023.
[47]
A. Abdallah, J. Mozafari, B. Piryani, and A. Jatowt. Asrank:
Zero-shot re-ranking with answer scent for document retrieval.
arXiv preprint arXiv:2501.15245, 2025.
[48]
S. Abiteboul. Querying semi-structured data. In Database Theory—ICDT’97: 6th International Conference Delphi, Greece,
January 8–10, 1997 Proceedings 6, pages 1–18. Springer, 1997.
[49]
K. Aggarwal, A. Khandelwal, K. Tanmay, O. M. Khan, Q. Liu,
M. Choudhury, H. H. Chauhan, S. Som, V. Chaudhary,
and S. Tiwary.
Dublin: Visual document understanding by
language-image network, 2023.
[50]
C. Aguerrebere, I. Bhati, M. Hildebrand, M. Tepper, and
T. Willke. Similarity search in the blink of an eye with compressed indices, 2023.
[51]
T. Ahmed, K. S. Pai, P. Devanbu, and E. Barr.
Automatic
semantic augmentation of language model prompts (for code
summarization). In Proceedings of the IEEE/ACM 46th International Conference on Software Engineering, ICSE ’24, New
York, NY, USA, 2024. Association for Computing Machinery.
[52]
A. Akbik, T. Bergmann, D. Blythe, K. Rasul, S. Schweter,
and R. Vollgraf.
Flair: An easy-to-use framework for stateof-the-art nlp.
In Proceedings of the 2019 conference of the
North American chapter of the association for computational
linguistics (demonstrations), pages 54–59, 2019.
47

[53]
P. Akioyamen, Z. Yi, and R. Marcus. The unreasonable effectiveness of llms for query optimization. CoRR, abs/2411.02862,
2024.
[54]
M. M. Alam and W. Wang. A comprehensive survey on data
provenance: State-of-the-art approaches and their deployments
for iot security enforcement. J. Comput. Secur., 29(4):423–446,
2021.
[55]
A. Albalak, Y. Elazar, S. M. Xie, S. Longpre, N. Lambert,
X. Wang, N. Muennighoff, B. Hou, L. Pan, H. Jeong, et al.
A survey on data selection for language models. arXiv preprint
arXiv:2402.16827, 2024.
[56]
A. Albalak, L. Pan, C. Raffel, and W. Y. Wang.
Efficient
online data mixing for language model pre-training.
In R0FoMo: Robustness of Few-shot and Zero-shot Learning in Large
Foundation Models, 2023.
[57]
K. An, F. Yang, L. Li, J. Lu, S. Cheng, S. Si, L. Wang, P. Zhao,
L. Cao, Q. Lin, et al. Thread: A logic-based data organization
paradigm for how-to question answering with retrieval augmented generation. arXiv preprint arXiv:2406.13372, 2024.
[58]
Q. An, C. Ying, Y. Zhu, Y. Xu, M. Zhang, and J. Wang. LEDD:
large language model-empowered data discovery in data lakes.
CoRR, abs/2502.15182, 2025.
[59]
R. Angles. A comparison of current graph database mod


# 1988 ACM SIGMOD international conference on Management

of data, pages 109–116, 1988.
[308] R. Peeters, A. Steiner, and C. Bizer.
Entity matching using
large language models.
In EDBT, pages 529–541. OpenProceedings.org, 2025.
[309] Q. Pei, L. Wu, K. Gao, J. Zhu, Y. Wang, Z. Wang, T. Qin, and
R. Yan. Leveraging biomolecule and natural language through
multi-modal learning: A survey, 2024.
[310] G. Penedo, H. Kydl´ıˇcek, A. Lozhkov, M. Mitchell, C. Raffel,
L. Von Werra, T. Wolf, et al. The fineweb datasets: Decanting
the web for the finest text data at scale.
arXiv preprint
arXiv:2406.17557, 2024.
[311] G. Penedo, Q. Malartic, D. Hesslow, R. Cojocaru, A. Cappelli, H. Alobeidli, B. Pannier, E. Almazrouei, and J. Launay.
The refinedweb dataset for falcon llm: Outperforming curated
corpora with web data, and web data only.
arXiv preprint
arXiv:2306.01116, 2023.
[312] B. Peng, C. Li, P. He, M. Galley, and J. Gao. Instruction tuning
with gpt-4. arXiv preprint arXiv:2304.03277, 2023.
[313] M. E. Peters and D. Lecocq.
Content extraction using diverse feature sets.
In Proceedings of the 22nd International
Conference on World Wide Web, WWW ’13 Companion, page
89–90, New York, NY, USA, 2013. Association for Computing
Machinery.
[314] D. Podell, Z. English, K. Lacey, A. Blattmann, T. Dockhorn,
J. M¨uller, J. Penna, and R. Rombach. Sdxl: Improving latent
diffusion models for high-resolution image synthesis, 2023.
[315] J. Postel.
Transmission control protocol.
Technical report,
1981.
[316] H. Pouransari, C.-L. Li, J.-H. R. Chang, P. K. A. Vasu, C. Koc,
V. Shankar, and O. Tuzel.
Dataset decomposition: Faster
llm training with variable sequence length curriculum. arXiv
preprint arXiv:2405.13226, 2024.
[317] M. Pourreza and D. Rafiei.
Din-sql: Decomposed in-context
learning of text-to-sql with self-correction, 2023.
[318] R. Pradeep, S. Sharifymoghaddam, and J. Lin. Rankvicuna:
Zero-shot listwise document reranking with open-source large
language models. arXiv preprint arXiv:2309.15088, 2023.
[319] D. Qi and J. Wang. Cleanagent: Automating data standardization with llm-based agents. CoRR, abs/2403.08291, 2024.
[320] Z. Qiang, W. Wang, and K. Taylor.
Agent-om: Leveraging llm agents for ontology matching.
arXiv preprint
arXiv:2312.00326, 2023.
[321] R. Qin, J. Xia, Z. Jia, M. Jiang, A. Abbasi, P. Zhou, J. Hu,
and Y. Shi.
Enabling on-device large language model personalization with self-supervised data selection and synthesis.
In Proceedings of the 61st ACM/IEEE Design Automation
Conference, pages 1–6, 2024.
[322] Z. Qin, D. Chen, W. Zhang, L. Yao, Y. Huang, B. Ding, Y. Li,
and S. Deng. The synergy between data and multi-modal large
language models: A survey from co-development perspective.
arXiv preprint arXiv:2407.08583, 2024.
[323] H. Que, J. Liu, G. Zhang, C. Zhang, X. Qu, Y. Ma, F. Duan,
Z. Bai, J. Wang, Y. Zhang, et al. D-cpt law: Domain-specific
continual pre-training scaling law for large language models.
arXiv preprint arXiv:2406.01375, 2024.
[324] Qwen, :, A. Yang, B. Yang, B. Zhang, B. Hui, B. Zheng, B. Yu,
C. Li, D. Liu, F. Huang, H. Wei, H. Lin, J. Yang, J. Tu,
J. Zhang, J. Yang, J. Yang, J. Zhou, J. Lin, K. Dang, K. Lu,
K. Bao, K. Yang, L. Yu, M. Li, M. Xue, P. Zhang, Q. Zhu,
R. Men, R. Lin, T. Li, T. Tang, T. Xia, X. Ren, X. Ren, Y. Fan,
Y. Su, Y. Zhang, Y. Wan, Y. Liu, Z. Cui, Z. Zhang, and Z. Qiu.
Qwen2.5 technical report, 2025.
[325] A. Radford, J. W. Kim, C. Hallacy, A. Ramesh, G. Goh,
S. Agarwal, G. Sastry, A. Askell, P. Mishkin, J. Clark, et al.
Learning transferable visual models from natural language supervision.
In International conference on machine learning,
pages 8748–8763. PMLR, 2021.
[326] A. Radford, J. W. Kim, C. Hallacy, A. Ramesh, G. Goh,
S. Agarwal, G. Sastry, A. Askell, P. Mishkin, J. Clark,
G. Krueger, and I. Sutskever.
Learning transferable visual
models from natural language supervision, 2021.
[327] A. Radford, J. Wu, R. Child, D. Luan, D. Amodei, I. Sutskever,
et al. Language models are unsupervised multitask learners.
OpenAI blog, 1(8):9, 2019.
[328] J. W. Rae, S. Borgeaud, T. Cai, K. Millican, J. Hoffmann,
F. Song, J. Aslanides, S. Henderson, R. Ring, S. Young, et al.
Scaling language models: Methods, analysis & insights from
training gopher. arXiv preprint arXiv:2112.11446, 2021.
[329] R. Rafailov, A. Sharma, E. Mitchell, S. Ermon, C. D. Manning,
and C. Finn.
Direct preference optimization: Your language
model is secretly a reward model, 2024.
[330] C. Raffel, N. Shazeer, A. Roberts, K. Lee, S. Narang,
M. Matena, Y. Zhou, W. Li, and P. J. Liu. Exploring the limits
of transfer learning with a unified text-to-text transformer.
Journal of machine learning research, 21(140):1–67, 2020.
[331] C. Raffel, N. Shazeer, A. Roberts, K. Lee, S. Narang,
M. Matena, Y. Zhou, W. Li, and P. J. Liu. Exploring the limits
of transfer learning with a unified text-to-text transformer,
2023.
[332] R. Rahnamoun and M. Shamsfard.
Multi-layered evaluation
using a fusion of metrics and llms as judges in open-domain
question answering.
In Proceedings of the 31st Inter


# 2024 Conference on Empirical Methods in Natural Language

Processing (EMNLP), 2024. arXiv preprint arXiv:2402.13446.
[374] Z. Tan, D. Li, S. Wang, et al. Large language models for data
annotation and synthesis: A survey. In EMNLP, pages 930–957.
Association for Computational Linguistics, 2024.
[375] J. Tang, Y. Yang, W. Wei, L. Shi, L. Su, S. Cheng, D. Yin,
and C. Huang. Graphgpt: Graph instruction tuning for large
language models, 2024.
[376] Z. Tang, Z. Yang, G. Wang, Y. Fang, Y. Liu, C. Zhu, M. Zeng,
C. Zhang, and M. Bansal. Unifying vision, text, and layout for
universal document processing, 2023.
[377] K. Team, A. Du, B. Gao, B. Xing, et al. Kimi k1.5: Scaling
reinforcement learning with llms, 2025.
[378] M. N. Team et al.
Introducing mpt-7b: A new standard
for open-source, commercially usable llms. DataBricks (May,
2023) www. mosaicml. com/blog/mpt-7b, 2023.
[379] Q. Team. Qwq: Reflect deeply on the boundaries of the unknown. Hugging Face, 2024.
[380] M. Tepper, I. S. Bhati, C. Aguerrebere, M. Hildebrand, and
T. Willke. Leanvec: Searching vectors faster by making them
fit, 2024.
[381] M. Tepper, I. S. Bhati, C. Aguerrebere, and T. Willke. Gleanvec: Accelerating vector search with minimalist nonlinear dimensionality reduction, 2024.
[382] J. Thorpe, P. Zhao, J. Eyolfson, Y. Qiao, Z. Jia, M. Zhang,
R. Netravali, and G. H. Xu.
Bamboo: Making preemptible
instances resilient for affordable training of large {DNNs}. In
20th USENIX Symposium on Networked Systems Design and
Implementation (NSDI 23), pages 497–513, 2023.
[383] T. Thrush, C. Potts, and T. Hashimoto.
Improving pretraining data using perplexity correlations.
arXiv preprint
arXiv:2409.05816, 2024.
[384] M. Tirmazi, A. Barker, N. Deng, M. E. Haque, Z. G. Qin,
S. Hand, M. Harchol-Balter, and J. Wilkes.
Borg: the next
generation. In Proceedings of the fifteenth European conference
on computer systems, pages 1–14, 2020.
[385] K. Tirumala, D. Simig, A. Aghajanyan, and A. Morcos. D4:
Improving llm pretraining via document de-duplication and
diversification.
Advances in Neural Information Processing
Systems, 36:53983–53995, 2023.
[386] H. Touvron, L. Martin, K. Stone, P. Albert, A. Almahairi,
Y. Babaei, N. Bashlykov, S. Batra, P. Bhargava, S. Bhosale,
et al. Llama 2: Open foundation and fine-tuned chat models.
arXiv preprint arXiv:2307.09288, 2023.
[387] B. Trabucco, K. Doherty, M. Gurinas, and R. Salakhutdinov.
Effective data augmentation with diffusion models, 2023.
[388] G. Wallace.
The jpeg still picture compression standard.
IEEE Transactions on Consumer Electronics, 38(1):xviii–
xxxiv, 1992.
[389] B. Wan, M. Han, Y. Sheng, Y. Peng, H. Lin, M. Zhang, Z. Lai,
M. Yu, J. Zhang, Z. Song, X. Liu, and C. Wu. Bytecheckpoint:
A unified checkpointing system for large foundation model
development, 2024.
[390] A. Wang, B. Ai, B. Wen, C. Mao, C.-W. Xie, D. Chen,
F. Yu, H. Zhao, J. Yang, J. Zeng, et al.
Wan: Open and
advanced large-scale video generative models. arXiv preprint
arXiv:2503.20314, 2025.
[391] A. Wang, H. Chen, L. Liu, K. Chen, Z. Lin, J. Han, and G. Ding.
Yolov10: Real-time end-to-end object detection, 2024.
55

[392] B. Wang, C. Xu, X. Zhao, L. Ouyang, F. Wu, Z. Zhao, R. Xu,
K. Liu, Y. Qu, F. Shang, B. Zhang, L. Wei, Z. Sui, W. Li, B. Shi,
Y. Qiao, D. Lin, and C. He. Mineru: An open-source solution
for precise document content extraction, 2024.
[393] C. Wang, Q. Dong, X. Wang, H. Wang, and Z. Sui. Statistical
dataset evaluation: Reliability, difficulty, and validity, 2022.
[394] C. Wang, M. Li, J. He, Z. Wang, E. Darzi, Z. Chen, J. Ye,
T. Li, Y. Su, J. Ke, et al. A survey for large language models in
biomedicine. arXiv preprint arXiv:2409.00133, 2024.
[395] C. Wang, Q. Wu, S. Huang, and A. Saied.
Economic hyperparameter optimization with blended search strategy.
In
International Conference on Learning Representations, 2021.
[396] H. Wang, J. Wang, C. T. Leong, and W. Li. Steca: Step-level
trajectory calibration for llm agent learning, 2025.
[397] J. Wang, J. Wu, Y. Hou, Y. Liu, M. Gao, and J. McAuley. Instructgraph: Boosting large language models via graph-centric
instruction tuning and preference alignment, 2024.
[398] J. Wang, B. Zhang, Q. Du, J. Zhang, and D. Chu. A survey
on data selection for llm instruction tuning.
arXiv preprint
arXiv:2402.05123, 2024.
[399] P. Wang, L. Li, Z. Shao, R. Xu, D. Dai, Y. Li, D. Chen,
Y. Wu, and Z. Sui.
Math-shepherd: Verify and reinforce
llms step-by-step without human annotations. arXiv preprint
arXiv:2312.08935, 2023.
[400] T. Wang, X. Chen, H. Lin, X. Chen, X. Han, L. Sun, H. Wang,
and Z. Zeng.
Match, compare, or select? an investigation of
large language models for entity matching. In COLING, pages
96–109. Association for Computational Linguistics, 2025.
[401] Y.
Wang,
Y.
Kordi,
S.
Mishra,
A.
Liu,
N.
A.
Smith,
D. Khashabi, and H. Hajishirzi.
Self-instruct: Aligning language models with self-generated instructions. arXiv preprint
arXiv:2212.10560, 2022.
[402] Z. Wang, X. He, K. Chen, C. Lin, and J. Su. Code-aware crossprogram transfer hyperparameter optimization.
I


## References

(e.g., levels from most helpful to least helpful). Collecting
these preference pairs or rankings is more time-consuming
than constructing instruction-response pairs in SFT.
In the general domain, UltraFeedback [113] consists of
64,000 samples. For each sample, different models are used
to generate 4 responses for each prompt (totaling 256,000
responses). GPT-4 is then employed to generate feedback
for these four responses, which is used to help LLMs to
generate outputs that are in line with human standards and
appropriateness.
In
specific
domains
such
as
healthcare,
Medical-
RLHF [429] has 4,000 random questions from a Chinese
medical dialogue dataset. Each question is paired with a well-
organized answer (i.e., the human doctor’s reply) and a weaker
answer from Llama-based model fine-tuned over synthesized
QA samples. These labeled data are used to train a reward
model. During the training of the LLM, the reward model
provides feedback based on the LLM’s answers, guiding the
7

training process towards generating high-quality responses.
(2) RoRL: Compared to the complex annotated data in
RLHF, RoRL allows the model to discover the best reasoning
approach on its own through the correctness of the reward
model. Specifically, it focuses on tasks requiring long-term
reasoning, such as mathematical, coding, and logical designing
experiments [162]. Under the premise of providing feedback
on whether the answer is correct or not, algorithm such as the
Group Relative Policy Optimization (GRPO) [162] and long-
CoT RL [377] are adopted to train the model to independently
discover the optimal problem-solving steps and converge.
Data for Retrieval-Augmented Generation (RAG).
The RAG stage differs from above training stages, which
involves large-scale dataset (reference corpus) for LLMs to
retrieve from during inference. In this stage, data must be
strictly reviewed to ensure authenticity and validity, while
dynamic data requires real-time updates. The domain of
RAG datasets varies depending on the specific application
scenarios. For instance, (1) in the medicine-specific LLM
application (Medical-Graph-RAG), MIMIC-IV is used as the
RAG dataset [415]. This dataset contains data from over
65,000 ICU patients and more than 200,000 patients treated
in emergency departments; (2) in the legal field, the RAG
knowledge base used by DISC-LawLLM [447] contains more
than 800 national and local laws, regulations, and rules, as
well as 24,000 legal-related exam questions. Besides, RAG
data can include users’ historical conversation records or
personal information, in order to build a user-personalized
LLM [350], [451], [453].
Data for LLM Evaluation. Suitable evaluation datasets are
essential for evaluating the performance of LLMs. They pro-
vide representative data samples that reflect different aspects
of an LLM’s capabilities.
In the general domain, the MMMU benchmark is used
to assess the performance of LLMs across major multi-modal
tasks in six key disciplines, covering 30 subjects and 183 sub-
fields. It is built from 11,500 carefully curated questions and
effectively tests models’ perception, knowledge, and reasoning
abilities [448].
In specific domains, typical evaluation datasets include
those in coding, healthcare and law domains: (1) OpenAI’s
HumanEval dataset includes 164 programming problems,
complete with function signatures, docstrings, bodies, and
multiple unit tests. These problems are handcrafted to ensure
they are not part of the training sets used for code generation
models [95]; (2) MedQA [198] contains a large number of
medical exam questions from various regions, totaling 61,097
questions; (3) LexEval [232] constructs 23 evaluation tasks
based on a legal cognitive classification framework, covering
different aspects of legal knowledge, with at least 100 evalua-
tion samples for each task.
Data for LLM Agents. Beyond vanilla LLMs, agents strive
for more advanced capabilities such as planning, tool or-
chestration and multi-turn dialogue capability [262]. These
capabilities impose higher requirements on the training data
for LLMs. First, many studies [396] aim to enhance planning
abilities through interaction trajectory data, which refers to
a sequence of records generated during the interaction be-
tween the agent and the environment, typically represented as
(instruction i, action a1, observation o1, . . . , action an). Ul-
TABLE 2: Data Acquisition for LLMs.
Method
Objective
Solution
Tools
Website
Crawling
HTML Textual
Content Extraction
Rule-based
Trafilatura [73]
Rule-based
BET [144]
ML-based
Dragnet [313]
Automate Browser
Interactions
HTML parsing
Beautiful Soup [6]
Control web driver
Selenium [19]
Wrap high-level API
Playwright [30]
DevTools protocol
Puppeteer [31]
Layout-based
Content Extraction
from Handwritten
or Non-text Data
Model pipeline
PaddleOCR
Model pipeline
MinerU [392]
Multimodal LLM
GOT2.0 [407]
Multimodal LLM
Fox [257]
Entity
recognition
& linking
New Sample Derivation
Bi-Transformer
ReFinED [68]
Translation Consistency
Seq2seq Framework
using References
AACTRANS [215]
Text-Image Integration
Multimodal LLM
UMIE [367]
traInteract [446] takes the instruction as the root node, and
uses both the correct actions and their corresponding incor-
rect actions as nodes to construct a preference trajectory
tree, enabling the agent to learn the human preference of
different actions. Second, other studies focus on enhancing
the agent’s tool usage capabilities using tool usage data. For
instance, AutoTools [351] fine-tunes models on tool data that
is labeled with special tags, such as <python>code</python>,
thereby grounding language in concrete tool invocations.
Third, to enhance the agent’s multi-turn dialogue capability,
UltraChat [117] employs an additional LLM to simulate user
instructions and conversational content, thereby collecting
multi-turn dialogue data.
2.3
Data Processing for LLM
2.3.1
Data Acquisition
Unlike classic machine learning, which primarily relies on
collecting labeled data within a specific domain for supervised
training (e.g., data for sentiment analysis and sentence sim-
ilarity estimation), data acquisition for LLMs typically (1)
relies on large-scale web scraping to collect extensive data
across diverse domains for unsupervised pretraining and (2)
employs techniques such as layout analysis and entity linking
to extract additional data from the collected content.
Principles
Unlike classic ML data acquisition, LLMs rely heavily
on large-scale web scraping to ensure broad coverage
and robust generalization. The main challenge is ex-
tracting high-quality textual content, often aided by
layout-based and entity-linking methods. Managing
time and resource efficiency at scale remains vital.
Data Sources. The data is gathered from two primary
sources:
(1) Public Data, often freely available under open licenses,
include resources such as webpages [11], books [497], and
publicly accessible code repositories [214].
• Webpage sources provide extensive pre-processed website
content, such as 1.56T english text from crawled websites in
C4 [331], 6.6B multilingual pages in mC4 [431], 6.3 trillion
tokens of multilingual pages in CulturaX [297].
• Digitized books supply structured, high-quality text, such
as over 75,000 eBooks in Project Gutenberg [38], over two
8

Data 
Processing
Trafilatura
Dragnet
PaddleOCR 
GOT2.0
Fox 
UMIE 
ReFinED 
Web Crawling
Layout Analysis
Entity Linking
1. Data Acquisition
Fast 
Fast
Retrieval
Accurate
Retrieval
Training Stage Requirement
Multiversity
Large Scale
Effectiveness
Low Repetition Rate
Standard Format
Content Safety
Content Privacy
RAG Stage Requirement
Data Serving
Optimizing Sequence
Combination
Data
Selection
Data 
Packing
1. Data Serving For Training
Semantic-Based
Packing
Short Sequence Insertion
Model-State-
Based
Experience-Based
Strategies
Sample Scoring
Data Storage
 1. Training Data Storage
Storage
Formats
Distributed
Storage
LLM-native
Formats
Multimodal
Formats
Chain Replication with

