# A Survey of LLM × DATA

## Document Header

1

           A Survey of LLM × DATA

          Xuanhe Zhou∗¶, Junxuan He∗¶, Wei Zhou∗¶, Haodong Chen∗¶, Zirui Tang∗¶, Haoyu Zhao∗¶, Xin Tong∗,
               Guoliang Li†, Youmin Chen∗, Jun Zhou∗, Zhaojun Sun∗, Binyuan Hui‡, Shuo Wang†, Conghui He§,
                                         Zhiyuan Liu†, Jingren Zhou‡, Fan Wu∗
                ∗Shanghai Jiao Tong University †Tsinghua University ‡Alibaba Group §Shanghai AI Laboratory
                                     https://github.com/weAIDB/awesome-data-llm

             Abstract—The integration of large language model (LLM) and data management (DATA) is rapidly redefining both domains. In this
                 survey, we comprehensively review the bidirectional relationships. On the one hand, DATA4LLM, spanning large-scale data processing,
                 storage, and serving, feeds LLMs with diversity, redundant, high quality, and sanitized data (following the “IaaS” concept) required for
                stages like pre-training, post-training, retrieval-augmented generation, and agentic workflows: (i) Data processing for LLMs includes
                 scalable acquisition, deduplication, filtering, selection, domain mixing, and synthetic augmentation; (ii) Data Storage for LLMs focuses
             on efficient data and model formats, distributed and heterogeneous storage hierarchies, KV-cache management, and fault-tolerant
                checkpointing; (iii) Data serving for LLMs tackles challenges in RAG (e.g., knowledge post-processing), LLM inference (e.g., prompt
               compression, data provenance), and training strategies (e.g., data packing and shuffling). On the other hand, in LLM4DATA, LLMs are2025        emerging as general-purpose engines for data management. We review recent advances in (i) data manipulation, including automatic
               data cleaning, integration, discovery; (ii) data analysis, covering reasoning over structured, semi-structured, and unstructured data, and
                   (iii) system optimization (e.g., configuration tuning, query rewriting, anomaly diagnosis), powered by LLM techniques like retrieval-Jun       augmented prompting, task-specialized fine-tuning, and multi-agent collaboration.
1
               Index Terms—Large Language Model, Data Management, DATA4LLM, LLM4DATA

                                 ✦

                                        Data Processing                  Data Storage    Data Serving       Example Datasets
                                                                                                                                                                         across LLM stages              Data4LLM                                                                                                                                                   Pre-Training[cs.DB]                                                                                                                        3FS   LanceDB         vLLM       Haystack
                                                  High-Flyer    Databricks    Snowflake     Data Juicer      Dataverse      Trafilatura
                                                                                                                                 inference data                    Product                                                                                          KV Cache
                                               Data                            Insufficient data                                                                            Langchain   Llamalndex                                                                                                    Inclusiveness                                                                                                            Noisy,                                                                                                      Redundant,                                                                                                                                                                               Continual                                                           RAG data                                                   Synthesis                                                                                                        or                                                                                                                    Sensitive                                                                                                         Data                                                                                                                       Rich,                                                                                                                         Diverse,                                                                                                                             Multi-                                                                       RAG                                                                                                                         data                                                                                                                                                                                   Pre-Training                                                                                                                                                    Vector                                                                                                                                             Graph                                                                                                           Coverage                                                                                                  Inadequate                                                                                                         Data                 Dimension                                                             pipelines                                                                                                                                                Storage                                                                                                                                                           Storage                                                                                                                                                    Chunk                                                                                                                                                                                                             Knowledge                                                                                                                                                                                                                        Knowledge                                               Data                                                                                               Composition
                                                Mixing                          abundance              articulation                                   Index     Rerank      Filtering
                                                                    Data                  Sufficient &   "IaaS"        Logically       model data
                                                                                                                                                                   Clear,                                                                                                         Balanced                                                                                                                                                  Checkpointing                                                                                                        Concept                                                                                                                                  of                                                                            Selection                                                                                                                            inference                                                                                                                          data                                                                                                                                                         Instruction-                                                                                            Volume                                                                                                                        of                                                                                          LLM Data                                                                                                                                                                 SFT                 Method                                               Data                                                                                                                                                          Offloading                                                                                                                             Guided                                                                                                                                              data                                                                                                             data                                                                                                                                                                                  Data                                                                                                                                                         Prompt                                                           Filtering                                                                                                                                                                                Provenance                                                                    Data                                                                                                              training                                                                                                       data       Compression                                                                                                       Sanitization                                                                     Deduplication
                                                                                                                                 Ethical, De-identified                 Distributed    Object
                                               Data                                                                                                                                    training data                                                                                                                                                            Storage                                                                                       pipeline              & Harm-Free data                  Storage                                                                                                                                                                                                     Reinforcement Learning                                                   Acquisition                                                                                                                                                                                 Data                                                                                                                                                                    Data                                                                                  orchestration                                                                                                                                           Data Processing
                                                                                                                                                          Offloading              Packing      Sampling

                                                                                                               inference                                                      RAG                                                                 model                                                                    training                  Data          origin                                data                                                                                         data                                                                           data                                                            data                                                                                                        data   K-V                      RAG

                                     Data Manipulation                           Data Analysis                         System Optimization

                                                                                                                            Document                                                                                  NL2SQL                LLM4Data                                                                                                                                                                            Configuration                                                                                                                                                                        Query                                                  Data                                                                 Data                                                                                                 NL2GQL                                                                                                     un-                                                                                                                                                                  Analysis                                                                                                                                                            Agent                                                                                                                                                                 Tuning                                                                                                                                                                                         Optimization                                                                         Integration                                                                                                                          / Code       graph                                                                                 relation                       RAG           Cleaning                                                                                                                            structuredarXiv:2505.18458v3
                                                                       data     Semantic                                                                                            data  Semantic                                                                                                                                    Program                                                                                                                data                                                                                                                                                      Anomaly Diagnosis                                                     Data Discovery                      prompt                                                                                                            Analysis                                                                                                                                      Analysis                                                                                                                                                                  Analysis                              agent
                             train

                                           Fig. 1: Overview of LLM × DATA (with “IaaS” Concept).

      1  INTRODUCTION                                           specific domain applications (e.g., biomedical literature analysis [394], legal document review [221], SQL generation for
          arge language models (LLMs1) have made remarkable                                                                       business intelligence  [250]). As shown in Figure  1, apart
             progress in both general domain applications (e.g., open-  L                                                   from technical advances in LLMs [289], [64], [460], [301],       domain question answering [332], cross-modal video summa-                                                                                 [241], [227], data management has emerged as a critical facrization [175], general-purpose code generation [191]) and                                                                          tor in unlocking LLMs’ full potential in these applications
                                                  (DATA4LLM). It includes efficient and scalable solutions
         •  ¶ Co-first authors with equal contributions.                        for data processing, storage, and serving across the LLM
              1. We use LLMs to refer to billion-scale language models capable of   lifecycle, as evidenced in recent academic studies [157], [285],
         supporting general NLP tasks [472] or multimodal tasks [444], [322].    [254] and industry reports [327], [433], [69], [39]. Conversely,
LLM-powered techniques are increasingly being adopted to   plex data samples [243], [78], [74]. For instance, standardizing
enhance data management tasks, such as data manipulation,   date formats (e.g., “Fri Jan 1st 10:36:28 2021” vs. “1996.07.10
analysis, and system optimization (LLM4DATA).        AD at 15:08:56”) or resolving textual inconsistencies (e.g.,
                                                             “Monticello VA, Jasper” vs. “Monticello VAA”) typicallyDATA4LLM. Effective data management is fundamental to
                                                                 requires intricate programming scripts or handcrafted con-the scalable development and deployment of LLMs. To illusstraints  [319],  [432]. These approaches also struggle withtrate this, we highlight representative scenarios where LLMs
                                                              cross-row error detection, such as mismatched city-state-zipdepend on specialized techniques for data processing, storage,
                                                                       entries. In contrast, LLMs can infer semantic similarities andand serving across various stages of the LLM lifecycle.
                                                       autonomously generate cleaning workflows to resolve such in-Example- ⃝Data1       Processing for LLMs. Processing a                                                                  consistencies without requiring explicit rule definitions [237],large-scale training dataset (e.g., ∼4 TB multi-modal tokens                                                                       [432], [454]. This semantic understanding enables LLMs toutilized in Qwen2.5-VL pretraining [70]) poses several chal-                                                        adapt flexibly to diverse data issues and support more scalablelenges. First, acquiring diverse raw data (e.g., over 10,000                                                    and context-aware data manipulation (Section 3.1).object categories for visual grounding) demands substantial                                               Example- ⃝LLM-based2           Data Analysis. Data analysisefforts in data collection (Section 2.3.1) and, in many cases,                                                             over heterogeneous sources, such as medical records anddata synthesis (Section 2.3.6). Second, preparing high-quality                                                                transactional data, is essential in many real-world applica-training samples requires robust pre-processing, including rig-                                                                      tions. Traditional deep learning models, while effective at per-orous data filtering (Section 2.3.3), along with dedicated eval-                                                          forming specific semantic-level analysis, struggle to generalizeuation approaches. Third, the overall performance of LLMs                                                                across diverse data formats and task types. For instance, tasksdepends heavily on an end-to-end pipeline that effectively                                                          such as table extraction and table-based question answer-schedules and coordinates these processing tasks, especially                                                              ing across heterogeneous sources (e.g., relational tables andfor the pretraining stage (Section 2.3.7).                                                        knowledge graphs) often require the development of separate,Example- ⃝Data2       Storage for LLMs. Managing storage                                                                  specialized models. This process  is both resource-intensive
for LLMs, spanning both training datasets (see Example-1⃝)                                                    and difficult to scale. In contrast, LLMs offer a unified reason-and massive model parameters (e.g., DeepSeek-R1 with 671B                                                              ing framework that leverages broad semantic understanding,parameters [162]), poses significant challenges. First, large-                                                             enabling them to support a wide range of analytical tasksscale datasets must be partitioned and distributed across mul-                                                                across various data modalities with greater flexibility andtiple storage nodes, introducing challenges in data placement                                                         reduced efforts for task-specific engineering (Section 3.2).and consistency management (Section 2.4.2). Second, to sup-                                               Example- ⃝LLM-based3           System Optimization. System
port efficient LLM training and inference, these storage nodes                                                             optimization entails configuring parameters  (e.g., memorymust deliver high I/O throughput for timely data transfer                                                                   settings) and monitoring runtime status (e.g., resource uti-to compute nodes (Section 2.4.4). Third, the massive size of                                                                     lization) to ensure optimal system performance. Traditionalmodel parameters increases the risk of training interruptions,                                                            approaches, such as manual tuning or deep learning-basednecessitating robust fault tolerance mechanisms to recover                                                        methods, are time-consuming and inefficient [474]. For in-and resume training from intermediate states (Section 2.4.5).                                                                 stance, methods of Bayesian Optimization (BO) or ReinforceExample–⃝Data3      Serving for LLMs. Data serving plays                                                   ment Learning (RL) require numerous workload replays over
a critical role in selecting and preparing input data (e.g., the                                                        20 hours to identify promising configurations for a single
task-specific prompts), directly affecting the quality of LLM’s  TPC-H workload [177]. Moreover, root cause analysis over
responses. Taking retrieval-augmented generation (RAG) as                                                          anomalies can be error-prone, particularly in multi-cause
an example, EyeLevel.ai  [37] observed that when relying                                                                scenarios where metrics are highly interdependent [490]. In
solely on vector similarity, RAG accuracy declines notably                                                                  contrast, LLMs offer a new paradigm by integrating domain
with 10,000-page documents, and the performance degrada-                                                        knowledge  (e.g., tuning manuals) and applying advanced
tion can reach up to 12% with 100,000 pages  (still fewer                                                             reasoning to instruct optimization. By leveraging retrievalthan enterprise-scale datasets). Several challenges arise in this                                                     augmented prompts, LLMs can efficiently identify root causes
context. First, the retrieved knowledge is typically noisy and                                                              or recommend precise configurations, enabling faster and
must be filtered and re-ranked to ensure relevance and factual                                                   more accurate optimization in complex environments [489],
accuracy (Section 2.5.1). Second, the retrieved content is often                                                                       [248], [223] (Section 3.3).
lengthy and exceeds the input capacity or comprehension
of LLMs, necessitating effective compression techniques to
preserve utility while improving performance (Section 2.5.2).   1.1  Techniques of DATA4LLM
                                                       Characteristics of LLM Datasets (§ 2.2). As shown in
LLM4DATA. Conversely, various LLM-based techniques                                                           Figure 1, datasets (following the “IaaS” concept) play a critican be leveraged to enhance core data management tasks,                                                                    cal role in enabling the desired capabilities at each LLM stage,
including data manipulation, data analysis, and system-level                                                              including (1) pre-training, (2) continual pre-training, (3) fineoptimization. The following examples illustrate how LLMs                                                              tuning, (4) reinforcement learning, (5) retrieval-augmented
can be applied to improve these tasks in practice.                                                             generation (RAG), (6) LLM agents, and (7) evaluation. For
Example- ⃝LLM-based1           Data Manipulation. Data ma-   each stage, we separately analyze the characters of required
nipulation, including cleaning, integration, and discovery, is   data (e.g., preferred formats and emphasized aspects within
critical for ensuring high-quality datasets. Traditional meth-  IaaS) and the corresponding data techniques (see Table 1).
ods depend on rigid rules and domain-specific configurations,  Data Processing for LLMs (§ 2.3). We introduce techrequiring extensive manual efforts and struggling with com-   niques to prepare high-quality datasets for LLMs based on a
                                                      2
series of processing steps.                               and clustering-based diversity quantification [92].
• Data Acquisition. Data acquisition aims to (1) extract rele-   • Data Pipelines. We first introduce frameworks that integrate
vant data (e.g., text and images) from noisy data sources with   basic data processing operators and interfaces, serving as the
certain structures (e.g., dynamically rendered web pages) [73],   general foundation for building data pipelines [90], [305], [368].
[144], [76], [73], [6], [19], [30], [31], and (2) extract data from  Then we showcase typical pipelines with heuristic mechanisms
complicated data sources (e.g., scanned or handwritten docu-   that properly arrange these operators (mainly for LLM prements) with techniques such as complex layout analysis [202],   training) [311], [236], [310]. Finally, we discuss strategies that
[18], [392], [180], [391], [407], [257], [326], [406].               go beyond heuristic designs to further optimize these data
• Data Deduplication. Data deduplication aims to identify du-   processing pipelines [91].
plicates in large-scale textual or multi-modal data, including                                             Data Storage for LLMs (§ 2.4). We review data storage
exact string matching  [122], [299], hash identification [88],                                                             techniques for LLMs from the following main aspects.[81], [122], [299], [347], [358], [207], [298], sample reweighing                                                        • Data Formats. We review commonly-used dataset and[167] and embedding-based clustering [46], [385], [360].                                                     model data formats  for LLMs. Dataset formats include• Data Filtering. We review data filtering methods at two                                                    TFRecord  [44], MindRecord [40] for multimodal data, andprimary levels: (1) Sample-level filtering selects high-quality                                                                 tf.data.Dataset that can be directly fed into LLMs [43]. Forand diverse samples using strategies  like perplexity mea-                                                     model data storage, there are formats like Pickle [13] andsuring  [383],  [61],  [288], influence assessment  [254],  [168],                                     ONNX [27].clustering methods [45], [436], prompt-based scoring [411],
                                                        • LLM Data Distribution. LLM data distribution aims to[264], [345], or mixes of these strategies [285], [84], [126]; (2)
                                                                  store data across multiple storage nodes in a cluster, whichContent-level filtering aims to remove undesirable or harmful
                                                        mainly serves  for storing large-scale LLM training data.content from large-scale datasets, such as toxic language, perKey approaches include (1) distributed storage systems likesonal identifiable information (PII), biased statements [268],
                                                        JuiceFS [16] and 3FS [15]; and (2) heterogeneous storage[275], and improper images and videos [437], [216], [390].
                                                          systems for model data (e.g., across GPUs and CPUs) [333],• Data Selection. Data selection aims to select sub-datasets
                                                                       [334], [337], [336], [435].and evaluate their ability to accurately represent the target
                                                        • LLM Data Organization. LLM data organization aims todistribution, especially when handling diverse datasets or
                                                           transform data into a format suitable for storage and retrievaldomains. There are methods like similarity-based data se-
                                                          (mainly for the RAG stage) in heterogeneous forms. First,lection [423], [421], [321], [80], optimization-based data selecfor vector RAG, relevant techniques include content format-tion [130], [417], [269], and model-based data selection [465].
                                                                 ting [97], [172], [57], [89], chunking [480], embedding [94],• Data Mixing. Data mixing aims to effectively integrate
                                                                            [24], [249], compression [50], [380], [381], [381]. Second, fordatasets from diverse domains without degrading quality or
                                                       graph RAG, we discuss indexing techniques such as generatingdestabilizing LLM performance. Key techniques include: (1)
                                                               textual summary for quick retrieval [127], [164], [136]. WeHeuristic optimization, which empirically tunes data ratios
                                                                  also introduce the systems that integrate these techniques,to enhance downstream performance. Examples include twoincluding vector search engines [125], [26], [34], [25] and graphstage mixing [139], source rebalancing [347], and entropystorage platforms [292], [65], [1].based weighting [152]; (2) Bilevel optimization, which formulates data weighting as a nested optimization problem   • LLM Data Movement. LLM data movement aims to improve
to jointly balance training and validation objectives [302],   the speed of data movement across storage and compute
[135]; (3) Distributionally robust optimization, which enhances   nodes. Relevant techniques include (1) caching data [219],
resilience to worst-case domain shifts by emphasizing un-   [161], [469]; (2) offloading data/operator to multiple devices
derperforming or rare data domains [420], [278]; (4) Model-   (e.g., across CPUs)  [158], [67], [159], [468]; and (3) overlapbased optimization, which builds predictive models to map   ping of storage and computing in training stage [466], [479].
data mixing ratios to loss and task performance. Approaches   • LLM Model Data Fault Tolerance. LLM model data fault
include linear predictive modeling  (e.g., REGMIX  [263]),   tolerance aims to enhance the ability to recover from system
nonlinear function fitting [152], [439], [160], scaling law-based   failures during model training. Relevant techniques include
estimation [323], and latent source attribution [251].            (1) checkpointing [291], [194], [403], [389], which stores check-
• Data Synthesis. We introduce data synthesis techniques de-   points across a hierarchical storage system; and (2) redundant
signed to address the following key challenges: (1) Mitigating   computation, which leverages redundant states of LLM in
harmful characteristics such as toxicity or bias, which can be   parallel training (e.g., pipeline parallelism [382], hybrid paralinherited or amplified in synthetic data (e.g., program-aided   lelism [186], [147]) to support rapid fault recovery.
verification [496], semantic scoring [173], and multi-agent con-   • KV Cache in LLMs. KV caching in LLMs is essential for
sistency filtering [346]); (2) Balancing data utility and privacy,   enabling fast and efficient inference by managing key-value
through privacy-preserving synthetic rewriting and key-entity  memory usage. Existing techniques include: (1) Memory layobfuscation methods during the RAG stage [450]; (3) Gen-   out and allocation, which optimize the physical organization
erating diverse and logically consistent reasoning data using   of KV memory for high performance and scalability [220],
approaches like formal proof-based validation [178], Chain-   [428]; (2) Storage offloading, which places KV data on suitable
of-Thought (CoT) branching and error correction [173], and   storage media to balance speed and capacity [197], [148]; (3)
high-quality problem synthesis guided by structure and com-  KV compression, which reduces memory footprint through
plexity constraints [260], [442]; (4) Automating human-like   techniques like encoding compression [265], [255], [150]; (4)
evaluation and feedback generation with LLM-based prefer-   Efficient indexing, which accelerates KV access via specialized
ence modeling [71], judge models for response ranking [476],   retrieval structures [440], [478].
                                                      3
Data Serving for LLMs (§ 2.5). We provide an overview of   with context via RAG techniques  [72]; (2) Data Annotadata serving techniques tailored for LLMs from four aspects.    tion, which assigns semantic labels or types through various
• LLM Data Shuffling. LLM data shuffling aims to deter-  prompting strategies [203], [204], [217], supported by classical
mine the appropriate order of data application during stages   retrieval-based [408] and LLM-generated context [163].
like LLM training and RAG. In the training  stage, we  LLM for Data Analysis (§  3.2). LLMs  significantly
discuss data pruning techniques (e.g., sample-scoring-based                                                        improve the analytical capabilities across structured, semiapproaches [137], [66], model-state-based approaches [372],                                                                structured, and unstructured data.
[56], [416], [276]) and data-centric training strategies [123].                                                        • Structured Data Analysis. For relational data analysis, natIn the RAG stage, we discuss RAG knowledge filtering [280],                                                                ural language interfaces allow users to write high-level ques-
[114], [87] and re-ranking [128], [12], [318], [47].                                                                  tions instead  of SQL/Python code  [452]. Multi-step QA
• LLM Data Compression. LLM data compression aims to                                                        frameworks  (e.g., TAPERA  [475] and ReAcTable  [464])
compress the model’s input data to stay within the context                                                     decompose complex  queries, while some end-to-end  soluwindow limit or to facilitate model understanding. Relevant                                                                  tions fine-tune LLMs  specifically  for tabular tasks  (e.g.,
techniques include: (1) RAG knowledge compression (e.g.,                                                TableGPT  [240]),  apply  content  retrieval  (e.g., CABIrule-based [427], [348], [200] and model-based method [101],                                       NET [306]) or convert tables into images for analysis (e.g.,
[335]); and (2) prompt compression (e.g., metric-based [189],                                                    Table-LLaVA [477]). For graph data, LLMs facilitate seman-
[190] and model-based method [303], [293], [102]).                                                                           tic queries with GQL generation (e.g., R3-NL2GQL [493]) and
• LLM Training Data Packing. LLM training data packing   knowledge-aware QA by retrieving or reasoning over relevant
aims to ensure uniform sequence lengths  in training  in-                                                         subgraphs [424].
puts. Relevant techniques include: (1) short sequence inser-                                                        • Semi-Structured Data Analysis. Meanwhile, handling semition [116], [259]; (2) optimizing sequence combination [218],                                                              structured data (e.g., JSON and spreadsheets) remains chal-
[316]; and (3) semantic-cased packing [364], [349]).                                                                  lenging. Recent benchmarks (e.g., TEMPTABQA [165] and
• LLM Inference Data Provenance. LLM  inference  data                                        SPREADSHEETBENCH  [281])  reveal  substantial  perforprovenance aims to ensure the factual consistency of LLM-                                                  mance gaps.
generated content. Relevant techniques include: (1) embed-                                                        •  Unstructured Data Analysis.  Finally,  unstructured  datading markers [482], [105], [256]; and (2) statistical prove-                                                                 analysis leverages LLMs to address document and programnance [212]).                                                                 analysis tasks. For document analysis, OCR-dependent approaches involve performing OCR on document images fol1.2  Techniques of LLM4DATA                           lowed by the integration of textual, layout, and visual features
                                                                      for reasoning  (e.g., UDOP [376] and DocFormerV2  [62]).LLM for Data Manipulation (§ 3.1). LLMs have been                                                      OCR-free  methods  directly  generate  the  answer  withincreasingly applied to data manipulation tasks, with the goal
                                                            end-to-end multimodal LLMs  (e.g., Pix2Struct [225] andof preparing high-quality datasets for non-LLM applications                                          DUBLIN [49]). For program analysis, LLMs could serve asand enhancing data quality for downstream usage. Key areas
                                                                 vulnerability detection tools using program analysis basedinclude data cleaning, data integration, and data discovery.
                                                                training (e.g., PDBER [271]) or case-driven prompt engineer-• Data Cleaning. This task involves standardizing and refining                                                              ing  (e.g., VUL-GPT [270]). For program related analysis,datasets through a series of operations. We highlight three maLLMs could summarize repositories (e.g., SCLA [284]) orjor subtasks: (1) Data Standardization, which reformats data                                                                serve as a repository-level code completer  (e.g., RepoFu-samples using handcrafted standardization prompts [279], [63]                                                                sion [357]) using their powerful semantic reasoning abilities.or agents that generate cleaning operations or pipelines [319],
[237]; (2) Data Error Processing, which identifies and corrects  LLM for Data System Optimization (§ 3.3). LLMs
noisy data via direct LLM prompting [103], [461], [432],   equipped with advanced reasoning and code generation cacontext-enrichment techniques [78], [74], or task-specific fine-   pabilities have been increasingly adopted in core system
tuning for error handling [432]; (3) Data Imputation, which   optimization tasks. These include: (1) configuration tuning
fills in missing values using explicit imputation instructions   (identifying optimal system settings); (2) query optimization
and retrieval-augmented generation (RAG) methods [129].      (rewriting or refining input queries for performance gains);
• Data Integration. This task focuses on identifying and rec-  and (3) anomaly diagnosis (analyzing system issues to ensure
onciling semantically related datasets across heterogeneous   performance reliability).
sources. We review two core subtasks: (1) Entity Matching,   • Configuration Tuning. This task leverages LLMs to dewhich aligns data entries referring to the same real-world   termine effective configuration parameters for improved sysentity using structured prompts [308], [134], sometimes aug-  tem performance through: (1) Prompt engineering tailored
mented with predefined code-based reasoning strategies [430];   to tuning tasks, using both manually crafted [243], [132],
(2) Schema Matching, which establishes correspondences be-   [156] and automatically generated prompts [491], [473]; (2)
tween schema elements using direct prompting [304], RAG   Retrieval-augmented generation (RAG), which incorporates
techniques incorporating multiple models [267], knowledge   prior tuning experiences during offline knowledge base prepagraph-based methods [277], and agent-based workflow gen-   ration [223] and online knowledge retrieval [96]; (3) Objectiveeration [320], [340].                                            aligned tuning, which is enhanced through targeted training
• Data Discovery. This task aims to extract informative in-   techniques [491], [177].
sights from a dataset. We cover two key subtasks: (1) Data   • Query Optimization. This task utilizes LLMs to rewrite
Profiling, which generates descriptive metadata and sum-   queries  or  improve  execution  plans  by:  (1)  Designing
maries using task-specific prompts [456], [58], and enhanced   optimization-oriented prompts that include  explicit guid4
                                                                            (b) Continual                    (c) Supervised
                     (a) Pre-Training Data                                                   (Morethan1T            Pre-Training Data            Fine-Tuning Data
                                                        Unlabeledsamples)
                                                                                      (10M~100BUnlabeledsamples)                 (100k~10Mlabeledsamples)
                                 This                                                                                                                                                                                                          Closed                                                                                                                                                     QA                                                 is a list of characters     RedPajama   package           kg.jl.common;                                                     OBELICS                      A                                                                                                     Medical Imaging Data                                                                                                                                                                Prompt                                                                                                                                                                                          Response   import          android.content;                                          Data              (141M                                                                                                      text and                                      Aglaint...                                                                                                                                                                          What                                                                                                                                                                                                                                                                                          is                                                                                                                                                                                                                          lung          Lung                                                                                                                                                                                                                                  cancer                                                                                                                                                                                                                                                                                                                                  is a   import          android.                                   ...                                                                    353M                                                                                    images)                                 Agravaine...                                                    General                                                                                                                                                                                                  cancer?                                                                                                                                                                                                                            (Malignant                                                                                                                                                                                                                                          type                                                                                                                                                                                                                                                                               of                                                                                                                                                                                                                                             malignant
                                                                                                                                                                                                 tumor                                                                                                                                                                                                                              includes ...)    ... tumor that ....                                              Domains                                    2.3%   Q:        Is         there            anyway                                     I                    can       14.8%                                                                                                                                                    QA                                                  (1.2T                                                    token)                                                                                                   Open    get         this            to keep                   the                     setup?
   A: Um, standard "stock"               C4                                                                                                                                                      Task    What is lung cancer?     Lungof malignant...cancer is a type
    fixes: ...                5.0%                                                                                                                                                                      Captioning
                                                      Lung                                                                 cancer                                                                                                   is a                                                                                                                                         This                                                                                                                           image                                                                                                                                       appears                                                                                                                                                                                 to be                                                                                                                                         a                                                                                                                                            computed                                                                                                                                                                                                                                                        ...                        1.7%                          Data                                                                                                                                                                                                                                          This                                                                                                                                                                                                                                                                                                                        is                                                                                                                                                                                                             a                                                                                                                                                                                                                                         medical                                                                type                                                                             of                                                                     malignant                                                                                                                           tomography                                                                                                                                             (CT)                                                                                                                                          scan                                                                                                                                                                                    of                                                                                                                                                                     the                                                                                                                                                                                                  lungs...    \section{Introduction}\section{Introduction}                         LetLet                                                                              The match                                                                                            between                                                                                                                                                                      CT                                                                                                                                                                                                                     scan                                                                                                                                                                                                                   image                                                                                                                                                                                                                                                                                           of                        2.0%                         Sources                                                           tumor                                                                               that   $G$$G$       bebe aa simplesimple                                                                                                                                                                                                                                               the                                                                                                                                                                                                                                                             lungs,                                                                                                                                                                                                                                                                   with                                                                                                                                                                                                                   a                                                                                   Manchester                                                                                                                  City                                                                                            and                                                                               AFC                                                                                                                                                                                 ...                                                                     originates                                                                                         in the   undirectedundirected             graphgraph                    withwith                         thethe                                                                                                                                                                                                                                                     section                                                                                                                                                                                                                                                                                  of                                                                                                                                                                                                                                                         the                                                                                                                                                                                                                                                        lung                                                                               Bournemouth                                                                                         ended                                                                                                                      with                                                                                                                                                                                                     ...                                                                                                                                                                                                                                    Please                                                                                                                                                                                                                                                         write                                                                                                                                                                                                                           a one-                                                                                                                                                                                                                                                        ...                                                                             lungs....                                       74.2%                                                                                                                                                                                                                             area                                                                                                                                                                                                                                                                                  circled                                                                                                                                                                                                                                                                                                           in                                                                                                                                                                                                                                                                                red,    \textit{vertex\textit{vertex                      set}....set}....                                                                                                                                                                                                                       sentence                                                                                                                                                                                                                                                     description                                                                                            A                                                                                                                                                                       Little                                                                                                                                 General                                                                                                                   Domain                                                                                                                                        Data
                                                                                                                                                                                                                                                                                                                                                                                                               ...                                                                                                                                                                                                                                             of the                                                                                                                                                                                                                                                                                  figure.

   Datasets                                                                                            Datasets                                  Datasets

       (f) LLM Agent Data                    (e) LLM RAG Data                      (d) Reinforcement Learning Data

    Interaction Trajectory Data                                  Medical Diagnosis Report                            (1k~1Mlabeledsamples)
                                                                                                                                             outcome                             What's                                       the                                      weather?           Instruction(i)                                                                                                                                                                                                                         (1)                                                                                                                                                                   Lung                                                                                                                                                                                          cancer                                                                                                                                                                                                                                                                           is                                                                                                                                                                               a                                                                                                                                                                                                                   disease.                                                                     Instruction                     RLHF
                                                                                                                                                                                                                         (2)                                                                                                                                                                   Smoking                                                                                                                                                                                                                                                                       is a                                                                                                                                                                                                 major                                                                                                                                                                                                           cause.            supervision                            Tool                              Usage                                     Data                                        Name: Lung cancer                                                                                                                                                                                                                         (3)                                                                                                                                                                                                                                                                                                                                       It can                                                                                                                                                                                       spread                                                                                                                                                                                                                                        to                                                                                                                                                                                                                                                        tissues...                                                                                                                    What is lung                             <python>
                                                                                                                                       cancer?                                                      Malignant                                                           tumor          Action(a1)            getLocation                                      GPS              Type:                                                                                                                                                                                                                         (1)                                                                                                                                                                    Lung                                                                                                                                                                                           cancer                                                                                                                                                                                                                                                                             is a                                                                                                                                                                                                                    disease.
                              </python>                                                 Context:                                                    Lung cancer                                                                                                                                                                                                                         (2)                                                                                                                                                                                  Only old                                                                                                                                                                                              people                                                                                                                                                                                                                     get                                                                                                                                                                                                                                                                                                                                                                                                   it.                                                                                                     is one of the most                  process                                                                                                                           supervision
       Observation(o1)          Location=London             common and serious types of cancer                                                                         (3)      It always causes fever...
                            Tool Usage Data                          globally...
                             <python>                     Image:
                                                                                                                                                           <think>                                                                                                                                        GPRO                                                                                                                  Cough          Action(a2)         getWeatherBy                                                                                                                                                         Consider                                                                                                                        common                                                                                                                                                                                                respiratory                                                                                                                                                                             <answer>                                Location        Location                                                                              accompanied                                                                                                                                      by
                              </python>                                                                                                                                                       system                                                                                                                                                                                          diseases;                                                                                                                                                                                                                                                                                                                                                                                              ...                          It                                                                                                                                                                                                                                                                        is                                                                                                                                                                                                                                            fracture.                                                                                                                     a small                                                                                                                           amount
         Answer             Current weather is...                                                                                                          of hemoptysis;                           It is fracture.                  </answer>
                                                                                                                                                               </think>
                           ...                                                                                 ...                                                                                                     ...

   Datasets                                         Datasets                                                  Datasets

       Fig. 2: Example Data Characteristics across LLM Stages - (a) Pretraining data [109], [224], (b) Continual
     pre-training [111], (c) SFT [447], (d) Reinforcement learning [429], [162], [253], (e) RAG [415], (f) Agent [396], [351].

ance [363], [491], [438] and in-context examples [248]; (2)   systematic overview of the associated challenges and techEnriching optimization knowledge using RAG techniques, in-   niques in data processing, storage, and serving (Table 1). In
cluding LLM-generated and hybrid retrieval strategies [369];   contrast, prior surveys [405], [55], [86] primarily center on the
(3)  Enhancing  optimization  performance  through  task-   pre-training stage without covering the full LLM lifecycle like
specific training [53], [196], [438].                              supervised fine-tuning (SFT), retrieval-augmented generation
• Anomaly Diagnosis. This task involves identifying the root  (RAG), and agent-based applications.
causes of anomalies and suggesting effective solutions via:                                                        • We provide a lifecycle-based taxonomy of DATA4LLM,
(1) Direct LLM prompting based on detailed diagnosis con-   introducing key tasks in data processing, storage, and serving.
text [155]; (2) RAG-based enrichment using relevant historical                                                         For each task, we summarize representative methodologies,
diagnosis experience [490], [425]; (3) Multi-agent collabora-                                                                discuss their design principles, and analyze their strengths
tion mechanisms for comprehensive diagnosis [490], [359].                                                    and limitations. In comparison, [405] focuses on deduplication
                                                    and filtering, [55] emphasizes data selection, and [373] reviews
1.3  Comparison with Existing Surveys                    data annotation strategies, none of which offer a systematic
Different from existing LLM and data management sur-   perspective across the data management pipeline.
veys [405], [55], [86], [398], [272], [274], [374], [488], our survey
                                                        • We introduce recent advances in LLM4DATA, outlining keyoffers a comprehensive and detailed overview of the key intercomponents of LLM-driven data optimization. While earliersections between LLMs and data management, highlighting                                                     work [488] has investigated the application of classical ma-how they can mutually benefit from each other. We uniquely
                                                              chine learning in data management, it largely neglects theposition our work at the intersection of data for LLMs (e.g.,
                                                                    distinctive strengths and limitations of LLMs, particularlyhow to acquire, process, store, and serve LLM data) and                                                                   in manipulating data for non-LLM tasks, processing semi-LLMs for data (e.g., how LLMs can be leveraged to enhance
                                                              structured and unstructured data, and enabling system-leveldata management tasks).
                                                               optimizations.• We propose the IaaS concept as a principled lens to assess LLM dataset quality. The IaaS concept identifies four   • We highlight open challenges and future directions from
essential dimensions, including inclusiveness, abundance, ar-  both ends: (1) improving data management techniques to
ticulation, and sanitization. This concept  is promising to  meet practical LLM training and deployment needs  (e.g.,
offers an evaluative criteria for guiding data management   efficient data evaluation, scalable multi-modal storage), and
and understanding its impact across the LLM development   (2) enhancing LLMs’ ability (e.g., private knowledge underlifecycle (see Section 2.1).                                      standing, informative representation for non-sequential and
• We investigate the unique characteristics of data across   non-textual data) to perform complex data management tasks
different LLM development stages (Figure 2), and provide a   across diverse real-world scenarios.
                                                      5
2  Data Management for LLM (DATA4LLM)       contextual framework, serving as a critical foundation for
                                                              building safe LLMs [345], [360].
2.1  “IaaS” Concept of LLM Data
Based on our investigation of over 400 papers 2, we introduce   2.2  Data Characters across LLM Stages
the IaaS concept for evaluating the quality of LLM datasets.                                                     Next we specifically discuss the data characteristics across(1) Inclusiveness: LLMs require data with broad and diverse                                                                     different LLM stages, together with the distinct techniquescoverage across multiple dimensions, including domains (e.g.,                                                                      for data processing, storage, and serving (Table 1).general knowledge, specialized fields like finance, medicine,
                                             Data for Pretraining. In the pre-training stage, LLMsmath [98], and physics [233]), task types (e.g., question anrely on TB-scale, diverse datasets to acquire broad languageswering, summarization, code completion [401], [290], [353],
                                                    and even cross-modality understanding capabilities, while[45], [436]), data sources (e.g., GitHub, Wikipedia [149], [11],
                                                            reducing the risk of overfitting. These datasets are typically[330], [347]), languages  [93], [347], expression styles  (e.g.,
                                                           sourced from a wide range of domains and formats, includingacademic, casual, formal [282], [470]), and data modalities
                                                 web crawls (e.g., HTML pages and WARC files [11]), open-(e.g., text [149], [11], images [145], [185], videos [437], [216],
                                                             source code repositories (e.g., raw source code files with meta-[390], tables [330]).
                                                         data [14]), books (e.g., plain text or EPUB formats [497]), aca-(2) abundance: LLMs require data with appropriate volume
                                                      demic papers (e.g., LaTeX source or PDF-converted text [2]),and balanced composition to prevent overfitting on homoand interleaved image-text corpora (e.g., aligned captionedgeneous data. Specifically, abundance of data involves: (i)
                                                         images in JSON or WebDataset format [224]).constructing well-balanced datasets during pre-training [139],
[302], [420], [263], (ii) adjusting data ratios to align with tar-  Data for Continual Pre-training. Continual pre-training
get applications during fine-tuning [278], [135], and (iii) con-   (or continued pre-training) typically involves datasets continually enhancing domain-specific capabilities while main-   taining millions to billions of tokens, which are often over 100
taining acceptable general performance degradation in contin-   times smaller than those used in the initial pre-training stage.
ual pre-training [323], [160]. Notably, the strength of LLMs lies  The primary objective is to  fill knowledge gaps and adapt
not only in large-scale data [282], [481], [11], [330], [149], [347],   the model to specific domains. Representative domain-specific
but also in constructing purposefully balanced datasets, which   datasets are like: (1) Finance: BBT-FinCorpus [273], a largecan further accelerate training and reduce computational cost.   scale and diverse financial datasets comprising approximately
(3) articulation: LLMs require data that exhibit strong articu-   300 GB of text; and (2) Healthcare: Medical-pt  [429], a
lation, including three key aspects: (i) the data should be well-   Chinese-English medical dataset containing 360,000 entries
formatted (e.g., proper punctuation and capitalization [90]),   curated from medical encyclopedias.
clean (free from duplicates, typos, and irrelevant content such  Data for Supervised Fine-Tuning (SFT). Unlike preas spam or gibberish [90]), and self-contained, featuring clear,   training, SFT  relies on data  presented  in  the form  of
fluent, and unambiguous language [282], [470], (ii) the data   instruction-response pairs, where the response includes not
should be instructive [178], [179], [98], i.e., offering sufficient   only the correct answer but also guidelines on tone, style, and
context, guidance, and intermediate explanations that help   reasoning steps to ensure user-friendly output.
the model connect questions to relevant background knowl-     The SFT stage typically involves much smaller datasets
edge and understand the reasoning process. (iii) the data  compared to pre-training. These datasets often consist of
should involve step-by-step reasoning[230], [442], [346], [173],   thousands to millions of labeled examples, with each example
[496], such that enhancing the LLMs’ reasoning capabilities   carefully crafted to guide the model in learning a specific,
by decomposing complex tasks into smaller, interpretable   narrower set of tasks. For instance, in Figure 2, (1) the summasteps.                                                             rization task constructs prompts using problem descriptions
(4) Sanitization: LLMs require data to be sanitized, meaning  and summarization objects; (2) closed QA using questions and
it is rigorously controlled and filtered to remove harmful ele-   corresponding knowledge texts; (3) open QA tasks using only
ments while maintaining inclusiveness and neutrality. This in-   questions without knowledge text; and (4) captioning tasks
volves four critical dimensions: (i) Privacy compliance, which   using task descriptions and images. These prompts are paired
requires the exclusion of personally identifiable information   with unique responses for model finetuning.
(e.g., ID numbers, phone numbers), inferred social relation-     The composition of SFT datasets varies based on the
ships, and geolocation-related metadata [450], [268], [275]; (ii)   application scenarios:
Toxicity-free content, ensuring the complete removal of hate  (1) General Instruction Following: For LLMs as generalspeech, incitement to violence, and psychologically harmful   purpose chatbots, SFT data include instructions for various
language, as well as eliminating any discriminatory or aggres-   daily tasks. Databricks-dolly-15K [110] is a corpus containing
sive semantic constructs [296]; (iii) Ethical consistency, which   over 15,000 records. It encompasses seven types of tasks,
prohibits the presence of extremist ideologies, instructions for   including creative writing, closed QA, open QA, summaillegal activities, and stereotype-reinforcing narratives that   rization, information extraction, classification, brainstorming.
may cause  social harm  [345],  [360],  [296]; and (iv) Risk   This dataset is designed to enhance LLM to better adapt to
mitigation, filtering out unverified medical claims, politically   specialized outputs that align with human-style requirements
misleading information, and culturally insensitive expressions   across diverse tasks. For example, in text summarization, it
to prevent misinformation and value misalignment. Sanitized   provides concise summary statements; whereas in text organidata must maintain a neutral tone and adopt an inclusive   zation tasks, it structures outputs in table-of-contents format.
                                                      (2) Specific Domain Usage: For models specialized in
   2. https://github.com/weAIDB/awesome-data-llm                    fields such as law, finance, or medicine, the SFT data focuses
                                                      6
 TABLE 1: Technique Comparison - Data Processing, Storage, and Serving Techniques for Different LLM Stages. “N/A”
  indicates that no relevant work has been reported yet, although the corresponding techniques could potentially be applied.

            Stage                IncrementalPre-trainingPre-training/                  Fine-TuningSupervised                  ReinforcementLearning                   Inference          RAG           Evaluation
                 Acquisition            ✓                    ✓                    ✓                    N/A              ✓            ✓
               De-duplication           ✓                    ✓                       N/A                   N/A                N/A            N/A
    Data         Filtering             ✓                    ✓                       N/A                   N/A              ×             N/A
 Processing      Selection             ✓                    ✓                       N/A                   N/A                N/A            N/A
                Mixing              ✓                    ✓                    ×                    N/A              ×            ×
                 Synthesis             ✓                    ✓                    ✓                    N/A              ✓            ✓
                Distribution          Distributed File System               Model Offload                   Model Offload               Model Offload            Model Offload       Model Offload                                 Model Offload (GPUs, CPUs)            (GPUs, CPUs)                  (GPUs, CPUs)               (GPUs, CPUs)           (GPUs, CPUs)       (GPUs, CPUs)
                                     Caching                                          Data                                                  Placement                                                                                      Parallelized                                                                                              Pipeline                                                                                                                             Parallelized                                                                                                                                   Pipeline               Transmission                                               Parallelized                                                         Pipeline                                                                                                                             N/A                                                                                                                                            N/A                                                                                         Offloading                                                                                 (CPUs)   Data/Operator                                                                                                                              Offloading                                                                                                               (CPUs)         ×                                 Data/Operator                                                     Offloading                                                   (CPUs)   Data/Operator
    Data      Fault                   Tolerance                                                                                            ×                                                                                                            ×                                                                                                                         ×                              ✓                                                   ✓                                                                        ✓   Storage                                                                                                                             Cache Space Management
          KV Cache              N/A                      N/A                      N/A              KVKVPlacementIndexing         KVKV PlacementShrinking         N/A
                                                                                          KV Shrinking
                                                                                                                                               SLM-Based Filtering
                                                                           Model-State-Based                  Selection            Sample-Scoring-Based                                         Model-State-Based                                                                            Experience-Based                 N/A                 ×              Metric-BasedLLM-Based Re-rankingFiltering       ×    Data                                                                                                                                            LLM-Based                                                                                                                                                                               Re-ranking
                                                                                                                                            N/A   Serving     Compression             N/A                      N/A                      N/A                 ✓                                                                                                           ✓
                 Packing             ✓                    ✓                    ✓                  ×               ×            ×
               Provenance            ×                    ×                    ×                  ✓                 N/A           ×

                              Information Extraction                                                            Alpaca - GPT4    Judgement Prediction                                               Refactoring/ Code Cleanup
                                                                           Classification                        Documents  Corpus
                                                                                               Summarization                                   Firefly Model Corpus
                  Summarization                                                                    Legal Case
                                                                                                                   Classification
                                      SFT                          Brainstorming           JudgementPrediction                SFT                    Legal Question        Misc             SFT                Bug Fixes                                                                                                                                              Answering          Code                                                                                                 Legal                                                                                                     Event                   General                                                                                                                             403KLawSamples                                                                                                                                                                                               59K Samples                                                                                                Detection                                                15K Samples                Creative Writing                                                                                                                                                                                                Model                                                                                                                                                                                                                                                               Size 16B                                                                                                                            Model                                                                                                                                                                        Size 13B
                                                Model                                                                    Size 12B
                                                                                                                      Judicial                         (c)                                                                               (5k Samples)                                                                                              Examination                                                        (a)                                                                                                                                                                                                               (e)
                                                                                                                Legal                                                                                                             Element                     Open QA                                                                                                                                                    Legal                                                                                                                                               Question
                                                                                                                         Extraction                                                                                                                                         Answering                                                                   Closed QA                    Similar                                                                                                Cases                                                                                                     Matching                                                                                                                                               Code                        (e)      Testing & QA
                                                                                           Document Reading  Public Opinion Summarization            Development
                                                                                                  Comprehension
                                         Reasoning   Sentiment                                                                                                                 Legal                                                                                                               Question           Judicial                                                                                                                                     Reasoning                      Question                              Answering                                                                                                        Answering                                                                        Style Transfer                                                                                                                                     Generation                             (QA)                                                                                                                                           Code Synthesis                    AutomaticRepairCode
                                                                                                                                  Civil Trial Prediction
                    Natural Language                                    Structured Data              Prison Term                                Case Understanding
                        Inference                                                                                                          Prediction                                                                   Summarization                                                                                                                                                                                           Code Translation
            Named                           Entity                   Eval                                                                                       Toxicity           Charge                                                                                                           Prediction                 Eval                 Legal Consultation                            Eval
                 Recognition                                                                                Translation                   General                                                                                                          Similar                                                                                            Case                                                Law                                                                                        Matching                                                                      Code          M otion                       Detection                                                45K Samples              Chinese                                                                                    Culture                                                                                                                                              11.7K                                                                                                                                         Samples                                                                                               Controversy                                                                                                                                                                                                               Samples                                                                                                                                                          Legal Article                                   7.5K
                        Linguistic                   (b)                   Classification             Focus Mining                   (d)              Recommendation                                       (f)             Code Classifcation
                     Grammar                                                              Case Recognition
                                Evaluation                      Code                                                                   Element Recognition
                                  Creative                                         Natural                                          Language  Commonsense                                       Judicial Summarization  Named Entity Recognition                 Code Compilation                                   Generation                                            (NLG)

  Fig. 3: Example LLM Data Distributions - (a) General Domain (SFT)[110], (b) General Domain (Eval) [244], (c) Law
                       (SFT)[447], (d) Law (Eval)[115], (e) Code (SFT) [294], (f) Code (Eval)[208].

on tasks pertinent to these fields. For example, DISC-Law-   involve more complex data annotations. Specifically, annoSFT [447] is a legal SFT dataset containing 295k data en-   tators compare multiple candidate responses to the same
tries from various legal scenarios, such as legal information   instruction and rank them according to human preference
extraction (32k), legal judgment prediction (16k), legal event   (e.g., levels from most helpful to least helpful). Collecting
detection (27k), and legal question-answering (93k). Similarly,   these preference pairs or rankings is more time-consuming
Medical-SFT [429] is a medical SFT dataset (totaling 2,060k   than constructing instruction-response pairs in SFT.
pieces), composed of medical inquikry data (790k), online                                                                In the general domain, UltraFeedback [113] consists of
medical encyclopedia QA data (360k), English medical in-                                                            64,000 samples. For each sample, different models are used
quiry data (110k), medical knowledge graph QA data (79k).                                                               to generate 4 responses for each prompt (totaling 256,000
For tasks such as legal question-answering and legal judgment                                                                responses). GPT-4  is then employed to generate feedback
prediction, the data is structured as triplets, comprising the                                                                      for these four responses, which  is used to help LLMs toprompt, response, and supporting reference information (e.g.,                                                             generate outputs that are in line with human standards and
legal provisions, case-based evidence, or regulatory docu-                                                              appropriateness.
ments). For the remaining tasks, they all take the form of
instruction pairs composed of prompt and response.               In   specific  domains  such  as  healthcare,  MedicalRLHF [429] has 4,000 random questions from a Chinese
Data for Reinforcement Learning (RL). RL is generally                                                          medical dialogue dataset. Each question is paired with a welldivided into two types: one is RLHF (Reinforcement Learning                                                            organized answer (i.e., the human doctor’s reply) and a weaker
with Human Feedback), and the other is Reasoning-oriented                                                        answer from Llama-based model fine-tuned over synthesized
Reinforcement Learning (RoRL).                                    QA samples. These labeled data are used to train a reward
(1) RLHF: RLHF data is typically smaller than SFT data   model. During the training of the LLM, the reward model
(e.g., thousands to dozens of millions of data samples), which   provides feedback based on the LLM’s answers, guiding the
                                                      7
                                                TABLE 2: Data Acquisition for LLMs.training process towards generating high-quality responses.
(2) RoRL: Compared to the complex annotated data in       Method            Objective                Solution               Tools
RLHF, RoRL allows the model to discover the best reasoning                HTML Textual           Rule-basedRule-based          TrafilaturaBET [144][73]
approach on its own through the correctness of the reward                      Content Extraction         ML-based         Dragnet [313]
model. Specifically, it focuses on tasks requiring long-term        CrawlingWebsite                     HTML parsing      Beautiful Soup [6]
reasoning, such as mathematical, coding, and logical designing                     AutomateInteractionsBrowser    WrapControlhigh-levelweb driverAPI    PlaywrightSelenium [19][30]
experiments [162]. Under the premise of providing feedback                                            DevTools protocol     Puppeteer [31]
                                                                                                                   Model pipeline       PaddleOCR
                                                                                                                   Model pipeline       MinerU [392]on whether the answer is correct or not, algorithm such as the      Layout-based     Contentfrom HandwrittenExtraction
Group Relative Policy Optimization (GRPO) [162] and long-                          or Non-text Data       MultimodalMultimodal LLMLLM     GOT2.0Fox [257][407]
CoT RL [377] are adopted to train the model to independently         Entity     New Sample Derivation      Bi-Transformer      ReFinED [68]                                                                                                                               Seq2seq Framework
                                                                                                                                        using Referencesdiscover the optimal problem-solving steps and converge.              recognition& linking     Translation Consistency                AACTRANS [215]                                                                                                    Text-Image Integration    Multimodal LLM     UMIE [367]
Data for Retrieval-Augmented Generation (RAG).
The RAG stage differs from above training stages, which
involves large-scale dataset (reference corpus) for LLMs to   traInteract [446] takes the instruction as the root node, and
retrieve from during inference. In this stage, data must be   uses both the correct actions and their corresponding incorstrictly reviewed to ensure authenticity and validity, while   rect actions as nodes to construct a preference trajectory
dynamic data requires real-time updates. The domain of   tree, enabling the agent to learn the human preference of
RAG datasets varies depending on the specific application   different actions. Second, other studies focus on enhancing
scenarios. For instance, (1) in the medicine-specific LLM   the agent’s tool usage capabilities using tool usage data. For
application (Medical-Graph-RAG), MIMIC-IV is used as the   instance, AutoTools [351] fine-tunes models on tool data that
RAG dataset [415]. This dataset contains data from over    is labeled with special tags, such as <python>code</python>,
65,000 ICU patients and more than 200,000 patients treated   thereby grounding language in concrete tool invocations.
in emergency departments; (2) in the legal field, the RAG   Third, to enhance the agent’s multi-turn dialogue capability,
knowledge base used by DISC-LawLLM [447] contains more   UltraChat [117] employs an additional LLM to simulate user
than 800 national and local laws, regulations, and rules, as   instructions and conversational content, thereby collecting
well as 24,000 legal-related exam questions. Besides, RAG   multi-turn dialogue data.
data can include users’ historical conversation records or
personal information, in order to build a user-personalized
LLM [350], [451], [453].                                      2.3  Data Processing for LLM
Data for LLM Evaluation. Suitable evaluation datasets are   2.3.1  Data Acquisition
essential for evaluating the performance of LLMs. They pro-   Unlike classic machine learning, which primarily relies on
vide representative data samples that reflect different aspects   collecting labeled data within a specific domain for supervised
of an LLM’s capabilities.                                        training (e.g., data for sentiment analysis and sentence simIn the general domain, the MMMU benchmark is used   ilarity estimation), data acquisition for LLMs typically (1)
to assess the performance of LLMs across major multi-modal   relies on large-scale web scraping to collect extensive data
tasks in six key disciplines, covering 30 subjects and 183 sub-   across diverse domains for unsupervised pretraining and (2)
fields. It is built from 11,500 carefully curated questions and   employs techniques such as layout analysis and entity linking
effectively tests models’ perception, knowledge, and reasoning   to extract additional data from the collected content.
abilities [448].
   In specific domains, typical evaluation datasets include                                                           Principles
those in coding, healthcare and law domains: (1) OpenAI’s
HumanEval dataset includes 164 programming problems,
                                                               Unlike classic ML data acquisition, LLMs rely heavilycomplete with function signatures, docstrings, bodies, and
                                                        on large-scale web scraping to ensure broad coveragemultiple unit tests. These problems are handcrafted to ensure
                                                       and robust generalization. The main challenge is ex-they are not part of the training sets used for code generation
                                                                    tracting high-quality textual content, often aided bymodels [95]; (2) MedQA [198] contains a large number of
                                                                layout-based and entity-linking methods. Managingmedical exam questions from various regions, totaling 61,097
                                                             time and resource efficiency at scale remains vital.questions; (3) LexEval [232] constructs 23 evaluation tasks
based on a legal cognitive classification framework, covering
different aspects of legal knowledge, with at least 100 evalua-  Data Sources. The data  is gathered from two primary
tion samples for each task.                                      sources:
Data for LLM Agents. Beyond vanilla LLMs, agents strive  (1) Public Data, often freely available under open licenses,
for more advanced capabilities such as planning, tool or-   include resources such as webpages [11], books [497], and
chestration and multi-turn dialogue capability [262]. These   publicly accessible code repositories [214].
capabilities impose higher requirements on the training data   • Webpage sources provide extensive pre-processed website
for LLMs. First, many studies [396] aim to enhance planning   content, such as 1.56T english text from crawled websites in
abilities through interaction trajectory data, which refers to  C4 [331], 6.6B multilingual pages in mC4 [431], 6.3 trillion
a sequence of records generated during the interaction be-   tokens of multilingual pages in CulturaX [297].
tween the agent and the environment, typically represented as   • Digitized books supply structured, high-quality text, such
(instruction i, action a1, observation o1, . . . , action an). Ul-   as over 75,000 eBooks in Project Gutenberg [38], over two
                                                      8
                                  Training Stage Requirement                                                     Inference Stage Requirement                  RAG Stage Requirement
      Multiversity          Effectiveness        Large Scale      Content Safety                Content           Content                            Fast             Accurate                                                                                                                                          Fast
    Low Repetition Rate        Standard Format       Content Privacy       Fast                Safety             Privacy                           Retrieval            Retrieval

                                             2. Data Deduplication                3. Data Filtering                                                                     3. RAG Data Storage
                                                                                                                                                                                       Vectory-Based                                            Exact                                                                                            Sample-Level                                       Data Storage                                                 Substring   MD5      Suffix Array                                                                                                                                                                                                                                Semantic                                                                                                                                                          Content                                          Matching                                                                                                                                                                                                                                                           or      Tree Structure                                                                                                                           Gradient/Shapley Value                                                                                                                                                                                                                                                               Logical                                                                                                                                                                                                                                                                 Units                                                                                                Statistical                                                                                                                                                                 Organization
                                                                                                                               1. Training                                                                                                           Data Storage                                                                          MinHash        Evaluation                                                                                                                                      Perplexity                                                                                                                      K-means                                         Hash        SimHash                                                                                                                                                   Chunking      Query-Based dynamic chunking    Data                    Identification                                                                DotHash   MinHashLSH                                                                   Model                                                                                                                                                                       Multimodal                                                                                                                                                                                               LLM-native                                                                                                                Prompt-based                                                                                                                                          Scoring            Storage
                                                                                Scoring                                                                                                              Formats        Formats          Formats        Embedding         Fine-Tuned Model Based                                                               SemDedup
                                                                            Hybrid        Metric         Metric  Processing        Embedding-    with Text/Image                                                                                    Encoder
                                       based Clustering                                                                                                                                                                                                                              Dimen.   Non-Linear                                                                                                                                                                                                                                                 Dimen.                                                                                                                                                                  Vector       Linear                                                                                                                    Permutation  Combination                                                                          FairDeDup           Evaluation                                                                                                                                                                                                                                    Reduction                                                                                                                                                                                                                                                     Reduction                                                                                                                            Distributed  Data Chunking        AssociationMetadata         compression                                                                                               Content-Level
                                          Frequency
                                                 Analysis      SoftDeDup  Bloom Filter         Regular Expression        Prompt-basedFiltering              Storage          ChainApportionedReplicationQuerieswith          Vector Storage  Table Schema   Columnar Storage

                                                                                                                                                                               Graph-Based
                                                                                                                                                                            Data Caching
                      1. Data Acquisition                                  6. Data Synthesis                        Data       Data/Operator Offloading (CPUs)         Indexing        AggregationHierarchical       AwarenessSemantic
                                                                                              Movement
                                                                                                                                                                                   Overlapping
                                                                                                                                                                  and Computing        Graph Storage  Property-Based      Triple-Based    Multi-ModelSupport     Web Crawling          Trafilatura         Dragnet                               Prompt         Program-Aided                                      Storage
                                                           Knowledge        Distillation             Distillation
       Layout Analysis      PaddleOCR         GOT2.0                 Distillation
                                                                                                   Multi-Stage Collaboration KD
         Entity Linking     UMIE        Fox      ReFinED                                                                             2. Model Data Storage               4. Data Storage For Inference

                                                                                                                                  Fault       Asynchronous        Redundant                          Chunking-Based        Create Prefix
                       4. Data Selection                                             Insutrction-Response Pair Synthesis             Tolerance      Checkpoint           Calculation         KV       Space Management          Index
                                                                                                                                                     Cache
                                                                      Pre-Training                                                                                             Mathematical Data Synthesis                Offload  Model Offload (GPUs,CPUs,NVMe Memories)                      Shrinking within (between) KV Layers
                                                                          Synthesis       Similarity-Based    Cosine Similarity      Bayesian Similarity        Data
           Selection        Lexicon Set Overlap    Bayes-based Selection                           Rephrasing   Cross-Language     Code
                                                                                                           Synthesis    Data Synthesis    Synthesis                                                                   3. Data Serving For RAG
       Optimization-Based     Linear Search    Gradient-based Search                      Data Serving
                                                                                                                                                Knowledge                                                                                                                                                                                                        Language                                                                                                                                                                                                      Model            Selection                Kernel Density Regularization
                                                                                                                                                                                                                                                Evaluation                                                                                                                                                                                                    Filtering                                                                                     Knowledge & QA Pair Synthesis                      1. Data Serving For Training                                                                 SFT
                                                             Data Synthesis                                                                                           Alignment                                                                                                             Reasoning          Model-Based                                                                                                                                                                                     Short                                                                                                                                                                      Sequence Insertion                                                                                                                Data                                                                                        Data                                                                                                        Synthesis      Data                                                                                                                             Synthesis                                                                                                                                                Knowledge            Selection               Prompt-based Scoring
                                                                                                                                                                                             Optimizing                                                                                                                                                                                      Sequence                                                                                                                                                                                                            Semantic-Based                                                                                                                    Packing                                                                                                                                                                  Re-ranking    LLM-based    Metric-Based
                                                                                                                                                                                     Combination                                                                                                                                                                                                                      Packing

                                                                                                                                                    Sample Scoring
                                                                                                                Data                                                                                                                                                Knowledge    SLM-based    LLM-based                                                                                                                                                                            Model-State-                                                                                                                                                                                                                  Experience-Based         Compression                       5. Data Mixing                                     7. End-to-End Pipelines                     Selection
                                                                                                                                                                    Based              Strategies
         Empirical      Quality-based       Tweaking       Ranking         Framework      Data-Juicer          Dataverse
         Strategies  Two Stage Training   Data Diversity    By Entropy
                                                                             CCNet    CC_Cleaner   MDR      LP                                         2. Data Serving For Inference                                                                     Pipeline
       Model-based     Distributionally         Linear     Non-Linear                         DCLM-BASELINE    Model-specific Pipelines           Prompt Compression        Metric-Based            SLM-Based         LLM-Based
         Mixing     Robust Optimization   Regression    Regression
                                                               Orchestration         Data-Juicer Sandbox                    Data Provenance      Covert Markers Embeding         Word Frequency Statistics

                                        Fig. 4: Overview of DATA4LLM Techniques.

million free ebooks in Open Library [28], and film-aigned book   meaningful textual content from boilerplate elements. Second,
descriptions in BookCorpus [497]).                              since typical extraneous components (e.g., headers, footers,
• Code repositories  (e.g., GitHub  [14], GitLab  [20],  Bit-   advertisements, sidebars) often contribute little to the data
bucket [7]) offer abundant programming data that can fa-   value (e.g., for LLM training), we execute scripts (using CSS
cilitate code search and analysis tasks, such as CodeSearch-   selectors or XPath queries) to identify and extract critical
Net [181] with 2M (comment, code) pairs.                     elements like article text, headlines, dates, and author bylines.
(2) Private Data involve proprietary or confidential in-   Third, once the relevant text has been scraped, we store it in
formation not publicly available, such as internal company   structured format such as JSON, CSV, database (see data
documents, customer support logs, application event logs,   storage in Section 2.4) for further processing. Specifically, for
subscriber-only content (e.g., premium news articles, licensed  image elements encountered in HTML files, the image source
scientific databases). Collecting this data requires careful  URL is recorded, and the content of the alt attribute within
attention  to  ethical and  legal  constraints  (e.g., GDPR,   the <img> tag is extracted and utilized as the corresponding
CCPA) and mandates removing sensitive details (e.g., em-   image’s textual caption.
ploying anonymization or pseudonymization) and using secure   • Rule-based Crawling. Most existing tools use heuristic rulepipelines (e.g., CI/CD systems) with encryption and role-   based matching algorithm. Trafilatura  [73]  is a  heuristic
based access controls. For instance, proprietary codebases and   algorithm based on hand-crafted rules (e.g., match HTML
user-generated content (chat logs, Q&A sessions) must be  DOM nodes with the class equal to “navbar” to filter the
gathered under secure processes to maintain confidentiality.    navigation bar). BET [144] employs the cumulative HTML
Data Acquisition Methods. As shown in Table 2, there are   tag distribution to find the largest region of fewest tags per
three main techniques for data acquisition, including website   text and extracts the corresponding text as the main content.
crawling, layout analysis, and entity recognition and linking.   • ML-based Crawling. Since many website regions cannot be
(1) Website Crawling. Most data are obtained through   easily classified by rules, some works [76], [73] design a HTML
website crawling, which aims to extract textual content from   tag classifier to judge whether a DOM node contains textual
crawled HTML  files or multimodal image-text pairs using   content, where they adopt L2 regularized logistic regression
various extraction tools and browser automation assistants.     that inputs text density features and word frequencies in ”id“
   Generally, we  first parse the raw HTML to separate  and ”class“ attributes and outputs the probability that a given
                                                      9
                                               TABLE 3: Data Deduplication for LLMs.node contains textual useful content.
• Auxiliary Tools. Moreover, some auxiliary tools integrate     Method        Objective      Modality        Work
user-friendly APIs for operating and interacting with HTML        Exact          Deduplicate                 MD5 [122]
                                                                                                                                                       Suffix Array [299]DOM trees. Beautiful Soup [6] is widely used to parse the      matchingsubstring      identicalsamplessubstringswith        Text
raw HTML in Python. Selenium  [19] automates browser                                                   SimHash [88]
                                                                                                  Deduplicateactions and handles dynamic pages by controlling a web       Hashing                                MinHash [81], [122], [299]                                                                                                       MinHashLSH [347], [358]
                                                                                                                 MinHash +driver that communicates with the browser. Playwright [30]      identification    similarsamplessubstringswith        Text
provides a high-level API to automate browser tasks while                                               BloomDotHashFilter[298][207]
Puppeteer [31] communicates directly with the browser using      Frequency      Down-weighing
the DevTools Protocol, allowing for headless browser interac-        analysis      highersamplescommonnesswith        Text         SoftDeDup [167]
tions (e.g., in JavaScript-heavy websites).                          Embedding-       Deduplicate                  SemDeDup [46]                                                                                               samples with       Text +        SemDeDup +
(2) Layout Analysis. Layout analysis focuses on extracting        based        identical topics but     Image      SSL Prototypes[385]
textual content from handwritten or non-textual data (e.g.,       clustering       different formats                   FairDeDup [360]
from the crawled ones), which can contain valuable information and require advanced layout analysis techniques for
                                                     (DS) to extract 4.8M triples, where each triple consists of aeffective extraction. Existing methods include pipeline-based
                                                                 subject, a relationship, and an object.and end-to-end approaches.
                                                             Furthermore, to ensure the consistency of derived and• Layout Analysis Pipelines. Intuitively, many works adopt
                                                                   origin samples  (e.g., translation across English and otherOCR technology (e.g., Tesseract [202]) to convert raw data
                                                              languages), Alignment-Augmented  Consistent  Translation(e.g., scanned books) into machine-readable formats [18], [392]
                                           (AACTRANS) model [215] uses a Seq2Seq framework thatin a pipeline manner, which consist of multiple small models.
                                                              incorporates reference text in the target language to guidePaddleOCR [18] passes an image through a Layout Analysis
                                                                   translations, ensuring consistency across related pieces ofmodel, which divides the image into different regions such as
                                                                     text. During training, aligned text pairs are augmented withtext, tables, and formulas for separate processing. The table
                                                               reference-based word alignments to bias the model towardarea is sent to the Form Recognition module for structured
                                                                consistent translations. At inference, a common referencerecognition, and the text areas and formulas are input to
                                                                 translation of the original sentence is used to align and trans-the OCR engine for text recognition. Finally, the Layout
                                                                     late related extractions using the AACTRANS model.Restoration module reconstructs all the regions in textual
                                                           However, AACTRANS fails to leverage shared knowledgeformat using heuristic rules based on the relative location
                                                                across tasks, limiting the alignment performance. Instead,information of different extracted regions.
                                         UMIE [367] integrates text and visual inputs and produces    Similarly, MinerU  [392] works  in a  pipeline manner.
                                                              structured outputs to learn linking knowledge from multipleIt fine-tunes LayoutLMv3  [180]  for layout detection and
                                                                   tasks. The UMIE model is composed of four modules: (1)YOLOv8 [391] for formula detection to improve the system’s
                                                        a text encoder for task instruction comprehension, (2) ageneralization (handling a wider range of document types).
                                                                  visual encoder for image understanding, (3) a gated attentionThe detected data are kept in markdown or JSON format.
                                                    mechanism for cross-modal integration, and (4) a text decoder• End-to-End Models. End-to-End layout analysis refers to
                                                                      for structured output generation. Following different taskadopt multi-modal LLMs to conduct end-to-end text acinstructors, UMIE is capable of performing various MIE tasksquisition. For instance, GOT2.0 [407] is a acquisition model
                                                    and generating corresponding structured outputs, therebycomposed of (i) a high-compression encoder that transforms
                                                                       facilitating knowledge sharing.the image to tokens, (ii) a long-context decoder that outputs
the corresponding OCR results, and (iii) a linear layer acting      Notably, recent LLMs could automatically learn the relaas the connector to map the channel dimension between the   tionships among samples from randomly provided data, renvision encoder and the language decoder. Another exam-   dering the explicit entity linking an optional procedure in the
ple is Fox [257], which employs the natural content-aware   data acquisition process [119].
CLIP-ViT [326] and the artificial content-aware Vary [406]
as two vision encoders, enabling the model to perform fine-   2.3.2  Data Deduplication
grained interactions and multi-page document understand-  The collected raw data often contains significant redundancy,
ing. The end-to-end architecture reduces maintenance costs  which can negatively impact LLM performance either by
and enhances versatility, enabling the recognition of more   reducing its generalization ability to new or rarely-seen tasks
complex elements (e.g., charts, sheet music) and supporting   [299] or by memorizing and overfitting to the repeated subimproved readability formats for formulas and tables (e.g.,   sets [169], [422]. Various deduplication methods have been
LATEX, Markdown). However, due to the use of LLMs with   proposed to detect and mitigate duplication, either by (1)
larger parameter size (e.g, <20M for PaddleOCR vs. 580M   completely removing duplicate samples [122], [299], [347],
for GOT2.0 and 1.8B for Fox), the inference efficiency of these   [358], [207], [46], [385], [360] or by (2) down-weighing duplicate
methods still needs improvement.                           samples for data resampling [167]. We classify these methods
(3) Entity Recognition & Linking. Additionally, we can   into four main categories.
derive more valuable LLM samples by identifying and link-  Exact Substring Matching. Exact substring matching
ing entities from the above extracted data. WEBIE [412]  methods identify and remove exactly identical samples across
introduces a large-scale, entity-linked information extraction   datasets, which can happen if (1) a sample references another
dataset with 1.6M sentences from Common Crawl. It links   sample (e.g., a report related to another), or (2) two individual
entities using ReFinED [68], and applies distant supervision   datasets accidentally include the same sample (e.g., a webpage
                                                     10
of a popular website). It is commonly used as a preliminary      Moreover, MinHash has various variants for acceleration.
step to remove duplications. Relevant methods leverage tech-  MinHashLSH [347], [358] improves MinHash by involving
niques like hashing [122] and suffix array [299] at the sample   locality-sensitive hashing (LSH), which divides a vector into
or sentence level.                                              multiple bands and only compares the samples with partially
                                                                    identical vector bands instead of the whole vector, mitigating the computational overhead in sample comparison. LSH-   Principles                                                 Bloom [207] further improves MinHashLSH by using Bloom
                                                                        Filter, which hashes each band into a single integer value and
   Compared to structured classic ML data, LLM data       inserting it into each corresponding Bloom Filter, and the
     is unstructured and requires careful identification and      sample will be flagged as a duplicate  if any band’s hashed
   removal of duplicate or near-duplicate content from      value collides with an entry in the Bloom filter, accelerating
    training datasets to improve efficiency, prevent over-       duplicate samples searching while reducing memory usage
    fitting, and mitigate bias using statistical metrics like      with negligible false positive rate (e.g., 1e-5 in experiments).
    perplexity or model evaluation. Challenges include (1)         However, MinHash-based methods require building mashow to encode semantic texts into representations that       sive vector  sets. When the number of samples and their
    could be precisely and efficiently compared and (2) the       lengths grow large, constructing vector sets becomes exceedscalability of the deduplication methods.                    ingly expensive in terms of both time and space. Moreover,
                                                              as the feature vector computation for each sample depends on
                                                                     this shared vocabulary, it is difficult to fully parallelize the• Sample-Level. [122] conducts sample-level deduplication
                                                                 process.by calculating the MD5 hashing value of each sample and
                                                        • SimHash [88]. To address MinHash’s issues, SimHash [88]deduplicate samples with identical MD5 values.
                                                              generates a sample’s feature vector solely from the words• Sentence-Level. [299] performs sentence-level deduplication                                                                                       it contains, converts each sample into a fixed-dimensionalby using Suffix Array, which combines all the samples into                                                           binary vector for similarity comparison. Specifically, it firstone sentence, computes the sentence Suffix Array, and dedu-                                                           hashes each token in the sample (e.g., by BPE tokenizer [75])plicates samples with common prefixes in the Suffix Array.                                                                  into a fixed-dimension vector of {0, 1}d (e.g., [1, 0, 0, 1] andSuffix Array [283] is a data structure that stores the starting                                                                               [1, 1, 0, 0] ) weighted by the pre-defined weight w (e.g., w1indices of string suffixes in lexicographical order. For instance,                                                    and w2), where the weight  is positive for 1 and negativegiven the string “patata”, its suffixes in lexicographical order                                                                      for 0 (e.g., [w1, −w1, −w1, w1], [w2, w2, −w2, −w2]). Then itare [“a” (index 5), “ata” (index 3), “atata” (index 1), “patata”                                                     added up these weighted vectors to a new vector of the same(index 0), “ta” (index 4), “tata” (index 2)], so its suffix array                                                         dimension d (e.g., [w1 + w2, −w1 + w2, −w1 −w2, w1 −w2]).is (5, 3, 1, 0, 4, 2). As identically duplicate samples have the                                                                    Finally, the values of the new vector are mapped to anothersame prefix, they will become adjacent in the suffix array,                                                              vector of {0, 1}d, where the positive values are mapped to 1making it easier to find the duplicates across the samples. In                                                    and 0 otherwise. The final vector is the fingerprint of eachpractice, they construct a suffix array on the sequence with                                                           sample, and the similarity of the two samples is estimated bya threshold of 50 tokens (empirically determined for signif-                                                                 calculating the Hamming distance between their vectors.icantly reducing the false positives), and find the duplicate                                                    Compared with MinHash, SimHash stores and compares
samples with common prefixes in linear time.                                                            only one hash signature for each sample, greatly reducing the
Approximate Hashing-based Deduplication. Hashing-   storage and computing overhead. However, keeping only one
based methods hash each sample into a fixed-length vector   signature makes it harder to distinguish between two samples,
and deduplicate samples with significant vector overlap. Com-   especially those with low Hamming distances, requiring carepared with the exact matching-based approach, it can identify   ful curation of data features.
near-duplicate samples with only a few words of difference   • DotHash [298]. Moreover, to further improve the deduplica-
(e.g., advertisements generated using the same template).   tion accuracy and efficiency, DotHash [298] assumes that uniUnlike normal hashing algorithms like MD5, hashes generated   formly sampled vectors in high-dimensional space are quasiin this approach do not change significantly with even a bit of   orthogonal. It encodes each sample into a combination of sammodification, making it possible to detect near-duplicate sam-   ple elements represented as fixed-length basis vectors, and the
ples. There are various hashing algorithms, including SimHash   dot product of these vectors is an unbiased estimate of their
[88], MinHash [81], DotHash [298], and their variants [347],   intersection. For example, given two samples with their ele-
[358].                                              ment basis vectors a = Pa∈A ψ(a)  and   b = Pb∈B ψ(b),
• MinHash [81] hashes samples into vectors using a series of   the intersection is calculated by E[a · b] = |A ∩B|.
hashing functions, where only the minimum value is retained      However, [121] found that DotHash performs badly if the
for each function, and estimates similarity for each pair of   length of the basis vector is lower than the number of basis
vectors through Jaccard Index Jaccard(X, Y ) = X∩YX∪Y , where   vectors, where quasi-orthogonal no longer holds.
X and Y represent sets of elements (For example, if X = a,  Approximate Frequency-based Down-Weighting. To
b, c, d and Y = b, c, d, e, f, the Jaccard Index over X and   prevent the loss of potentially valuable information by retainY would be 12). [356] demonstrates that MinHash generally   ing only one sample and removing the rest, SoftDeDup [167]
outperforms SimHash. In practice, [122] employed MinHash   deduplicates by reweighting samples, where samples with
to the code data on both the sample and the repository levels   higher commonness are assigned lower sampling weights.
for diversity and integrity, and [299] employed MinHash on   Specifically, SoftDeDup computes the frequency of each nthe sample level.                                     gram across all the samples and calculates the commonness
                                                     11
                                              TABLE 4: Data Filtering Methods for LLMs.of each sample by multiplying the frequencies of all the ngrams that appear in the document. Samples with higher    Category    Objective                 Methods
commonness are more likely to be duplicates and thus be                                    Perplexity Measuring [383], [61], [288], [239], [238]
down-weighted.                                                               Sample-level        low-qualityRemove               InfluenceClusteringAssessment[45], [254],[436] [168]
                                                                                                  Filtering       samples            Model Scoring [411], [264], [345]
Embedding-Based Clustering. Except for samples with                                     Mixed Methods [285], [84], [126]
                                                                                                                          Privacy Anonymization [275], [268]the same or similar substrings, some samples with similar      Content-level       partial-noisingRemove
                                                                                                  Filtering       samplessemantics but different formats  (i.e, expressed differently)                                  Image & Video Filtering [437], [216], [390]
may also negatively affect LLM training performance. For
instance, for the following two sentences: (i) “Unleash your
potential with our lightweight, high-performance sports shoes –     A  Perplexity-based Data Filtering
designed for comfort, speed, and style”; (ii) “Step into great-          Perplexity    Next token    Previous tokens                                 Removed Dataset
ness with durable, breathable sports shoes perfect for running,                                                                      IFD =
                                                                                                                                                                                                      0.8training, and everyday adventures”. Both of the sentences are          IFD Score
                                                                                                                                                                                     IFD =
                                                                                                                                          Nosports shoe advertisements but expressed differently, and such          Original Dataset                                                       0.4                                         Filtered Dataset

                                                                                                                                                                                     IFD                                                                                                                                                                          =duplicates could degenerate model performance by making                                      Estimate
                                                                                                                                                                                                                                 Threshold?                                                                                                                                              IFD Score                                                                                                                                                                                                      0.7data imbalanced and introducing bias to the model. To ad-                                                                                                          IFD >       Yes
dress this issue, another approach leverages language models’      B  Clustering-based Data Filtering
embeddings (representing similar items as vectors close to
                                                                                                                    Complexity                                                      Removed Dataseteach other in the vector space) for deduplication.
                                                                                                                                          Average Intra-            Average Intercluster Distance            cluster Distance  SemDeDup [46] identifies semantic duplicates by clusterOriginal Dataset                                                                                                                  Filtered Dataseting embeddings and deduplicating those with high cosine
similarities. It first encodes each sample into an embedding                           EncodeEmbeddingto                          PruneClusterby
by leveraging the OPT [462] text encoder and the CLIP [325],                               Clusters                             Complexity
[182] image encoder, and clusters the embeddings with Kmeans, so one can save time by finding duplicates within the      C Prompting-based Data Filtering
                                                                                                                                         Enhance the samplescluster rather than the whole vector space. Then, within each          Original Sample                       Enhanced Samples                       Low

                                                                                                                               Enhance                                                      Datasetcluster, it searches for semantic duplicates with cosine similar-                                                                                                    Original
ity above the pre-defined threshold. Finally, within each group                                                                                                                                                                                                          Score
                                                                                                                                                   Score the (enhanced) samples
of duplicates, it retains only the sample closest to the cluster                                              Scores                                                           Filtered
centroid. As a multi-modal method, it can be applied to both                             Score                                                   High    Train               Dataset
text and image data, making it possible to deduplicate image                                                                                               Scorer
data. In practice, [45] leverages SemDeDup to deduplicate the                                                                  Fig. 5: Example Data Filtering Workflows [238], [45], [264].image-text pair dataset LAION-400M [341].
   Like MinHash, SemDeDup also has many variants for
performance improvement. [385] combines SemDeDup with
the Self-Supervised Learning (SSL) Prototypes metric, which   precision and recall. In contrast, MINT-1T employs a hashclusters the samples and retains the samples in each clus-   based approach, using SHA256 checksums to identify and
ter based on their distance to their corresponding cluster  remove exact duplicates efficiently. Meanwhile, the DataComp
centroid, where the samples closer to the centroid are more   pipeline [146] leverages the CNN-based near-duplicate deteclikely to be removed. FairDeDup [360] modifies the logic of   tor [445] to eliminate subtle duplicates and prevent evaluation
SemDeDup to improve the representation of underrepresented   set leakage. Models trained on these deduplicated image
sensitive groups by prioritizing the retention of samples that   sets exhibit improved performance over baselines such as
align with sensitive concepts defined through user-provided  CLIP [325] for higher precision and recall.
prototypes, such as demographic subgroups. Within each
cluster, instead of selecting the farthest sample from the
centroid, it selects the sample that maximizes similarity to
the least-represented group in the cluster to prevent samples   2.3.3  Data Filtering
with sensitive concepts from being pruned.
                                                    Data filtering removes low-quality or sensitive samples fromNon-Text Data Deduplication. As LLMs are increasingly                                                            the dataset to reduce computational overhead and protectapplied to multimodal tasks (e.g., image-text retrieval, visual                                                                  privacy, while the model trained on the subset exhibits sim-question answering), non-text data types such as images                                                                             ilar or even better performance than the one trained onare becoming integral to LLM training datasets, necessi-                                                            the original dataset. To achieve this, one has to (i) removetating dedicated deduplication techniques. Similar to texts,                                                         samples with low quality (Sample-level filtering) or partialimages can also be encoded into embeddings through neural                                                              noisy information (Content-level filtering), and (ii) keep thenetworks designed for image-like data such as CNN, after                                                                  selected samples diverse enough to cover various domains.which embedding-based deduplication methods can be applied. SemDedup [46] adopts a semantic-based method by  Sample-level Filtering refers to evaluating samples using
computing cosine similarity between image embeddings; two   metrics or models and removing the samples that fail to meet
images are considered duplicates  if their similarity exceeds   the threshold (e.g., quality and diversity). There are multiple
a predefined threshold, which is tuned to balance detection   metrics in this category:
                                                     12
                                                                   find that the effectiveness highly depends on the dataset.   Principles                                                         For example, keeping the high perplexity samples exhibits
                                                               better performance on the Pile dataset [149], while keeping
   Compared to classic ML data filtering, LLM data                                                            the medium perplexity samples exhibits better performance
    filtering emphasizes turning unstructured text into                                                     on the Dolma dataset [361].
   measurable metrics, with the main challenge being the                                                             Furthermore, there are some variants of perplexity-based    effectiveness of evaluation methods, the standards of                                                                evaluation.  First,  [288] proposes a perplexity-based met-    low-quality samples, and the computational complex-                                                                                ric, Learning Percentage (LP), to select samples that are    ity of these methods across massive datasets.                                                   more challenging for models to learn. Learning Percentage
                                                      LP(i) =  Pi−1−PiP0−Pn  measures the perplexity drop ratio of a
(1) Statistical Evaluation uses various statistical methods   sample between the specific epoch i and the whole training
to evaluate samples by directly applying statistical metrics to   procedure. The key idea is that models tend to learn easier
the samples (e.g., clustering results) or indirectly capturing   samples first and harder samples later, so one can find harder
characteristics from the models trained on the dataset (e.g.,   samples that are not thoroughly learned during early epochs.
loss or perplexity from a surrogate model). Applicable statis-  The authors use LP(1) (the learning percentage after the first
tical metrics include perplexity (and its variants), influence on   epoch) to rank the training samples from the hardest to the
model parameters, and clustering.                                easiest and split them into three equal-sized parts. It shows
• Perplexity Measuring. Perplexity measures the difficulty of   that the smaller-sized variant of the model can effectively
a model generating the responses, represented as aggregated   select samples for the larger-sized variant, and models of all
probabilities of the j-th response token given the question   sizes trained on the harder part outperform the ones trained
tokens and previous j −1 response tokens PPL(y|x) =  on all the samples.
                                                             Also based on perplexity, [239] proposes the Instruction-exp −1N PNj=1 log p(yj|x, y1, ..., yj−1)  . The higher the per-                                                            Following Difficulty (IFD) metric to select samples that areplexity value is, the harder the model generates the response.
                                                   more  difficult  for models to  follow. IFD (IFDθ(Q, A) =It is commonly used in selecting high-quality subsets in pre-   P P L(A|Q)                                                                                  ) measures the influence of the questions (instruc-training and fine-tuning phases. Based on the original perplex-    P P L(A)
                                                                  tions and inputs combined) on generating corresponding re-ity, there have been several studies for improving the metric,
                                                            sponses by comparing the perplexity of the response withincluding computing perplexities using a smaller-sized model
                                                              or without the question strings PPL(A|Q) and PPL(A). Afor training a larger-sized model to reduce computational
                                                             higher IFD score suggests higher model following difficulty.overhead, or employing advanced techniques such as Learning
                                                The authors first build a pre-experienced subset by clusteringPercentage (LP) and Instruction-Following Difficulty (IFD)
                                                    and resampling the samples from the WizardLM [426] andto identify and select challenging samples.
                                                   Alpaca-GPT4 [312] datasets, on which they train the model    Specifically,  [383] uses an  existing model to compute                                                                      for one epoch to obtain initial knowledge. The model is thenperplexity  scores  for  multiple domains and  selects  pre-                                                         used to calculate the IFD score on all the samples, and thetraining samples from the domains with high correlation                                                           ones with high IFD scores are prioritized.between the downstream benchmark error and the perplexity
                                                                     Superfiltering [238] further enhances [239] by employingscores on the domain samples. The correlation is measured
                                                            the surrogate model from [61]. Instead of training a smaller-through a rank-based correlation coefficient γj = P sign(yk −
                                                                  sized model, the authors directly use GPT-2 [327] as theyl)(rankj(xk,j) −rankj(xl,j)), where the rank difference resurrogate model to calculate IFD scores on the same datasets.flects the model performance difference on the same sample,
                                                 Compared to their previous work [239], the adoption of sur-helpful in estimating θ∗. They then rank the domains based on
                                                             rogate model simplifies the procedure and accelerates theγj and select samples from the top-ranked domains. To scale
                                                                          filtering process.the process, a fastText classifier [199] is trained to distinguish
selected documents, enabling page-level data selection.        • Influence Assessment. Another data filtering approach is to
                                                                  assess the influence of a sample on LLM model performance   To enhance efficiency, [61] leverages a smaller-sized surroor learning process by measuring how the metrics changegate model to select high-quality pre-training subsets via perwhen the sample is upweighted or removed. The samples withplexity score for training larger-sized models, greatly reducing
                                                                substantial impact on the model parameters are regarded asthe computational overhead in model training while  still
                                                                      influential and thus are selected.achieving the same performance as with the full dataset. They
first train a surrogate model, a smaller-sized MosaicML [378]    DEALRec [254] identifies influential and challenging fineInfluence Score formodel with 125 million parameters, on a random subset of the   tuning samples through two metrics: (i)
pre-training dataset to compute the perplexity scores for the   assessing the influence of a specific sample on the model
remaining samples. Based on the perplexity scores, they find   performance. It starts by measuring the influence on pathe optimal subset through a combination of selection criteria:   rameter change, where a surrogate model is trained on the
(i) the part of samples to keep (e.g., samples with low/medi-    full dataset to estimate how the model parameters would
um/high perplexity scores), and (ii) the fraction of samples   change when certain sample is removed or upweighted, exto keep (e.g., 25%, 50%, 75%). The subset is evaluated by   pressed by  ˆθ−s −ˆθ                                                ≈ nH−11    ˆθ ∇θL(s, ˆθ), where Hˆθ  is the
training a larger-sized MosaicML model on it and analyzing   Hessian matrix and ∇θL(s, ˆθ) is the loss gradient of sample
the model’s performance on downstream benchmarks. While   s. The formula  is then evolved to measure the influence
the result shows that the smaller-sized model can effectively  on empirical risk change, expressed by Iremove, loss(s, D) =
                                                                                                          Effort Score  for as-and efficiently filter data for the larger-sized model, they also   n1 Pi n∇θL(si,1        ˆθ)TH−1ˆθ ∇θL(s, ˆθ);  (ii)
                                                     13
sessing the  difficulty  for the surrogate model to learn a   training a rater on the scalar quality ratings, and filtering
specific sample for generalization to new samples, defined   samples using the rater. Initially, GPT-3.5-turbo is prompted
as δs = ∥∇ϕLLLM(s)∥2, where Φ  is the model parame-  on each pair of samples to judge which one is better on each
ter. A higher  effort score suggests greater  difficulty. The   quality criterion, where the binary confidence pB≻A ∈[0, 1]
final score combines the above two scores, written as Is =   that the sample B is preferred over the sample A is recorded.
Influence Score + λ · Effort Score.                       The pairwise binary confidence is then translated into sample
   Besides, SHED [168] utilizes the Shapley value [339], which   quality ratings pB≻A = σ(sB −sA) through the Bradleyestimates the contribution of a member to the group, to   Terry model. A QuRater model  is later trained on these
calculate the influence of a sample on the model performance   quality ratings to predict quality ratings for new samples
and select representative samples with high influence. The  on each criterion. The new samples are resampled with the
method first clusters the samples and selects the ones clos-   probability p(di) ∝exp  siτ   , where τ adjusts the trade-off
est to each cluster centroid as the representative samples   between quality and diversity.
to reduce computational overhead.  It then calculates the     Rather than prompting the models to compare samples,
Shapley value for each representative sample i by iteratively   Data-Efficient Instruction Tuning for Alignment (DEITA)
removing n samples from the dataset until all the samples   [264] prompts LLM models to evolve and score the samples
have been removed and calculating the contribution of the   for building sample scorers. The authors first prompt Chatremoved n samples in each iteration a to the model per-  GPT to evolve the samples along instruction complexity and
formance compared with the previous iteration, written as:   response quality, and again prompt ChatGPT to score these
c(an+1..(a+1)n)∈Dp = v(Dp \ {1..an}) −v(Dp \ {1..(a + 1)n}).   evolved samples. They then train scorers on the evolved samThe process will be repeated for k times for higher accuracy,   ples with their corresponding scores to enable their scoring
after which the Shapley value for each representative sample   abilities. Finally, they use these scorers to score new samples
i  is defined as Si ≈  k1 Pk ci(k)n   . Finally, the subsets can  and multiply the scores to form the final score, where the new
be selected either by selecting from the top-rank samples   samples are resampled based on the final scores for diversity.
or weighted sampling the samples through Pr(i) =    efSi    ,     Model scoring methods also help mitigate bias and toxPi efSi     icity. LLM often exhibit harmful biases due to the massivewhere f controls the trade-off between quality and diversity.                                                    and unchecked datasets they are trained on, which can have• Clustering. A common approach to select high-quality and                                                               various biases, ranging from gender and racial stereotypes todiverse subsets  is to encode the samples into embeddings                                                                  cultural and socioeconomic prejudices [296]. Safety-enhancedin the latest space and cluster them using cosine similarity,                                                          Aligned LLM Fine-tuning (SEAL) [345] selects high-qualitywhere similar samples are usually clustered into the same                                                    and safe fine-tuning samples through a safety-aligned selec-group. Selecting within the clusters reduces redundancy, while                                                                       tor. The selector is trained based on a safety-aligned model,selecting across the clusters increases diversity.                                                              Merlinite-7b [366], using bi-level optimization, which miniDensity-Based Pruning (DBP) [45] selects high-quality                                                          mizes the safety loss on the safe dataset while minimizing
and diverse subsets by clustering samples into clusters and                                                            the fine-tuning loss on the filtered dataset during training to
resampling the samples based on the cluster complexity. They                                                            ensure the selector always prioritizes safe and high-quality
encode the samples into embeddings using a pre-trained vi-                                                         samples during selection. After the selection, the top-p%
sion model DINOV2-L/14 [300] and cluster them using K-                                                         samples will be selected.
means. For each cluster, they calculate the average intra-  (3) Hybrid Methods. Instead of relying on a single method,
cluster cosine-distance to the internal centroid dintra and                                                   some methods mix various kinds of data filtering methods and
inter-cluster cosine distance to the other centroids dinter,                                                              evaluate each permutation of these methods or parameters
and the cluster complexity as a product of the two distances                                                               to find the best combination of methods or parameters that
C = dintra × dinter. The cluster complexity is later converted                                                                further boosts model performance.
to probability using softmax to resample the samples across                                                                       [285] selects high-quality pre-training data based on three
clusters, where clusters with higher complexity have higher                                                                metrics: (i) Perplexity, (ii) EL2N χ(xi, yi) = E∥f(xi) −yi∥2weights.                                                                      for measuring the prediction probability discrepancy between
   Rather  than  the  sample embedding  itself,  SmallTo-   the reference model and the ground truth, and (iii) Mem1 PNi 1(zM+i = ˆzM+i) forLarge [436] selects a diverse subset by clustering the samples   orization factor score(M, N) = N
based on their loss trajectories. It first trains a smaller-sized   measuring the fraction of N tokens correctly generated after
surrogate LLM model on the whole dataset to obtain the loss  prompting the model with the first M tokens [77]. For each
trajectories of each training sample, defined as Li(ϕ(t)) =   metric, they retain samples based on two criteria: (i) the
−log pϕ(t)(yi|xi), where ϕ(t) is the model parameters at time   fraction of samples to keep (10%, 30%, 50%, and 70%) and (ii)
t. These samples are then clustered based on loss trajectories   the part of samples to keep, e.g., the bottom (for Perplexity
and randomly resampled to form a diverse subset.            and L2-Norm Error) and top (for Memorization). They train
(2) Model Scoring uses LLMs for evaluating sample qual-  LLM for each case and select the best-performing one, and the
ity. The quality criteria can either be specified (i) explicitly   result shows that Perplexity effectively removes the “easiest”
via LLM prompt engineering or (ii) implicitly learned from   samples, improving model performance and outperforming
human-labeled data.                                         other metrics.
   QuRating [411] selects high-quality pre-training samples      Instead of comparing metrics and choosing the best of
by prompting LLM to compare pairs of samples along the   them, InstructionMining [84] combines various metrics (e.g.,
four quality criteria (writing style, fact & trivia amount,   including input/output length, reward score, perplexity, etc.)
educational value, and the expertise required to understand),   into one linear function with each metric as indicator, written
                                                     14
                                         TABLE 5: Comparison of Different Data Selection Methods.as logLloss ∝L0 + β0 + β1I1 + β2I2 + · · · + βnIn + ϵ. The β
parameters are estimated using least squares. In practice, it     Method       Stage           Evaluation Metric
evaluates fine-tuning samples on a fine-tuned model LLaMA-                                        Cosine Similarity [423]
2-7B [386] and selects samples by finding the optimal set of       Similarity     Pre-training,      Bag-of-Words Similarity [421]
samples to keep using the hyperparameter optimizer Blend-                     Fine-tuning        Lexicon Set Overlap [321]                                                                                                       Bayes-based Selection [80]
Search [395].                                                                                                Linear Search [130]
  MoDS [126] considers diversity into selection and iter-     Optimization    Fine-tuning      Gradient-Influence Search [417]                                                                                                     Kernel-Density Regularization [269]
atively selects high-quality, diverse, and necessary subsets       Model       Pre-training       Logits-based LM-Score [465]
and adds the samples the LLM model performs poorly on
during fine-tuning using a reward model and the K-Center
greedy algorithm [342]. The method is conducted mainly in   hashed tags, entity tags like “[NAME]” or “[LOCATION]”,
three steps: (i) Use a reward model to score the quality of   or a simple tag like “[MASK]”. The last tag was adopted to
each (instruction, input, output) triplet in the dataset, where  maximize privacy, as the other ones are still vulnerable to
the low-quality ones are filtered out, forming a high-quality  membership inference by linking the samples.
dataset. (ii) Use the K-Center greedy algorithm [342] to select                                                   The rise of multi-modal LLMs, particularly large video
the samples in the high-quality dataset that are farthest apart                                                             generation models, drives the need for robust video data filterfrom each other in the BERT [206] embedding space, forming                                                                     ing. CogVideoX [437] employs a pipeline focusing on coherent
a diverse seed dataset. (iii) Fine-tune a pre-trained LLM                                                          motion, removing videos with poor dynamics. It defines negmodel on the seed dataset to enable its instruction-following                                                                  ative labels for artificial edits, low motion connectivity, visual
ability and generate responses for the high-quality dataset.                                                                     flaws, and excessive text. A manually annotated subset trains
The generated responses are evaluated using the same reward                                                                     six Video-LLaMA[455]-based filters, while optical flow and
model, and those with low quality scores, which means the                                                                 aesthetic scores ensure motion coherence and visual appeal,
model is weak at generating such responses, will be collected.                                                                    refining the dataset to approximately 35M high-quality 6The collected samples with their original responses will be                                                          second clips.
selected again using the K-Center greedy algorithm and then                                                       HunyuanVideo [216] uses a multi-step pipeline: splittingadded to the seed dataset, forming the final dataset.                                                              videos into clips, encoding embeddings, deduplication, and
Content-level Filtering. To avoid removing too many crit-   resampling. Filters include motion (OpenCV-based optical
ical samples from the dataset and weakening the model per-   flow), OCR (text removal), clarity (visual blur detection), aesformance, some works only filter out noise or sensitive content   thetic (Dover[414]-based scoring), and source (YOLOX[153]-
within the samples. For noise removal, common methodologies   like watermark/border removal). This process generates five
include removing or replacing specific characters (e.g., remove   progressive training sets with increasing thresholds.
invisible or invalid characters, unescape HTML characters and    Wan [390] applies pre- and post-processing pipelines. Predetect punctuation misuse), removing unnecessary texts (e.g.,   processing filters unsuitable data using OCR, aesthetic evalthe texts that appear as decorating elements on the web pages   uation (LAION-5B [341]), NSFW scoring, watermark desuch as “print”, “likes” and “loading” ), and cleaning harmful   tection, and resolution thresholds, removing approximately
information (e.g., spam, gambling, pornographic content and  50% of low-quality data. Samples are clustered for diversity,
site links) [433].                                          manually scored, and an expert model selects high-quality,
   For privacy anonymization, LLMs can memorize  pri-   naturally distributed data. Videos are classified into six tiers,
vate and  sensitive information  (e.g, user  identity  details   prioritizing smooth motion. Post-processing refines images by
or clinical health data) from datasets during pre-training   selecting top 20% via an expert model and manually curating
and  fine-tuning, which can be  leaked through  specially   gaps. For videos, top candidates are filtered by visual quality
crafted prompts, thereby posing significant privacy risks. [275]  and motion complexity, ensuring balance and diversity across
demonstrates that it is possible to extract, reconstruct, and in-   12 themes.
fer personally identifiable information (PII) from LLM models by identifying the most frequent PII appearing in model                                                                    2.3.4  Data Selection
responses or by prompting models with partial information
about a specific individual. From a data management perspec-   Different from previous reviews [55], [398], we define data
tive, these privacy threats can be mitigated by identifying and   selection as the process of choosing subsets of already wellfiltering out potential sensitive information in the datasets.     cleaned data samples in order to adapt LLMs to specific
                                                      domains (e.g., medical or legal LLMs).  DeID-GPT [268] utilizes existing LLMs to identify and
remove PII from unstructured medical text without changing
its meaning. In their case, the LLMs are prompted to de-      Principles
identify information from clinical notes in accordance with
HIPAA privacy regulations. An example prompt is: “Please                                                               Unlike traditional ML data selection, LLM data selecde-identify the following clinical notes by replacing any terms       tion focuses on aligning the topics of the text samples,
that could be a name, an address, a date, or an ID with the       requiring encoding semantic topics into measurable
term ‘[redacted]’.”                                                     distributions. However, managing computational effiInstead of using general LLMs, [275] uses Named Entity      ciency and ensuring robust generalization across diRecognition (NER) models such as spaCy [33] and Flair [52]       verse tasks remain critical unresolved issues.
to tag PII in the samples and removes or replaces them with
                                                     15
Similarity-based Data Selection. One class of methods   (e.g., 5% of data) for a few epochs using LoRA to reduce
aims to select subsets similar to the specified target data.       trainable parameters and accelerate gradient computation,
• Cosine Similarity: Domain-Adaptive Continual Pre-training  and saves the checkpoints after each epoch. Next, LESS
(DACP) [423] adapts a general-purpose LLM to a target task  computes Adam LoRA gradients for each training sample,
by selecting domain-specific unlabeled data based on simi-   projects them into lower-dimensional gradient features via
larity (cosine similarity), novelty (perplexity), and diversity  random projection, and stores them in a gradient datastore.
(entropy). For the similarity part,  it identifies data most   For downstream tasks, it calculates gradient features of fewsimilar to the task-specific labeled data by encoding both into   shot validation samples and estimates the influence of each
embeddings (using [33]) and choosing domain samples that   training sample z on a validation sample z′ using cosine
align with the task’s embedding distribution.                     similarity: InfAdam(z, z′) ≜PNi=1 ¯ηi cos(∇ℓ(z′; θi), Γ(z, θi)),
• Bag-of-Words Similarity: DSIR [421] selects a subset of  where Γ(z, θ) is the Adam update. The training samples with
unlabeled pre-training data matching the target distribution   the highest influence scores are selected for fine-tuning.
by computing feature distributions (ˆpfeat, ˆqfeat) for raw and   • Kernel-Density Regularization. Task-Specific Data Selectarget data represented as bag-of-words, estimating impor-   tion (TSDS) [269] identifies high-quality pre-training or finetance weights wi =  ˆpfeat(zi)ˆqfeat(zi), and resampling raw data with   tuning data for particular tasks by balancing two objecprobability    wi     .                                                  tives: (i) distribution alignment with the target task data
      PNi=1 wi                                    and  (ii)  diversity to avoid near-duplicates, accomplished• Lexicon Set Overlap: [321] selects the subset with the most                                                                via kernel density estimation (KDE) regularization. Con-shared lexicons using the Domain Specific Score (DSS), which                                                                       cretely, one begins with a small set of target task sam-quantifies the relevance of a dialogue set T to specific domains                                                                  ples Q =  {qi}Mi=1  and  a  large  candidate  pool D =by measuring the overlap between T and domain lexicons L =                                                   1         |T ∩li|   {xj}Nj=1, both of which are embedded into a shared met-
{l1, l2, . . . , lm}, calculated as DSS(T, L) = m Pmi=1  n   ,   ric space  (e.g., using gradient-based or semantic embed-where n is the number of tokens in T.                                                                  dings). The optimization for distribution alignment is con-
• Bayes-based Selection: CoLoR-filter  [80] formulates pre-                                                         ducted by  solving  for  probability mass  γij  (transported
training subset selection as a Bayesian optimization problem,                             α                                                                                                                          γijdij + (1 −                                                       from  qi  to  xj): minγ∈RM×N≥0  C PMi=1 PNj=1which selects a subset S by maximizing downstream likelihood
Pr(Ddown|S). It uses two auxiliary models: A “prior” model  α)GKDE(γ)   s.t. PNj=1 γij = M1 , ∀i ∈  [M], where  dij
(θprior) trained on a large general dataset Ddown and a “condi-    is the distance between  qi and xj  in the metric space,
tional” model (θprior) fine-tuned on the union of the large gen-  and GKDE(γ)  is the regularization term that adds divereral dataset and a small downstream dataset Dprior+down. The   sity and penalizes over-density using KDE: GKDE(γ) =
                                                                                                   1/ρjselection criterion                    for                    a data point                                       the conditional loss                                     xi is                             M maxi,j ρj  γij −                                                                                                                                                    , where  ρj = Px′∈D(1 −                                               M P                                                                                                                                            j′ 1/ρj′                                 −reduction         (CoLoR):                  = −log                 CoLoR(xi)                                          Pr(xi|θprior+down)
(−log Pr(xi|θprior)). The key idea is to score samples based on   f(xj, x′)2/h2 is the density estimate for candidate xj (higher
the likelihood difference between these two models and select   for near-duplicates). Afterwards, it samples xj with probabilthe ones that exhibit higher likelihood under the conditional   ity pj = Pi γ∗ij.
model and larger conditional loss reduction.               Model-based Data Selection. These methods aim to deOptimization-based Data Selection. Optimization-based   termine subsets guided by prompting the LLM itself.
data selection methods select subsets towards reducing model     Autonomous Data  Selection (AutoDS)  [465] prompts
loss and improving model performance on the target tasks.     the LLM to assess and  select mathematical and educa-
• Linear Search. Model-Aware Dataset Selection with Data-   tional samples from a  larger  dataset. For each sample,
models (DsDm) [130] selects the optimal subset of training   the LLM  is asked two  questions:  (i)  Is  it mathematidata that minimizes the model’s loss on target tasks by   cally relevant, and  (ii)  It  it educationally valuable. The
employing linear datamodel [184], a parameterized function  LLM responds to each question with “Yes” or “No”, and
that maps a subset of training data to the model outputs   the  logit  of each response  is extractedexp(logit(‘YES’))to compute the
for the specified target, to estimate how the inclusion of   LM-Score: LM-Score(·) = exp(logit(‘YES’))+exp(logit(‘NO’)), and
                                                                                                                                                                                                  ·each training sample would affect the model’s loss on the   the composite score: LM-Score(Q1, Q2) = LM-Score(Q1)
target, reducing computational overhead. In practice, a linear   LM-Score(Q2). The composite score ranks and selects highdatamodel τθx(1S) = θ⊤x 1S with parameters θx and a charac-   quality math samples.
teristic vector 1S (a binary vector indicating which samples
are in S) is adopted to map the subset S to the model loss on   2.3.5  Data Mixing
a sample x through Lx(S) = E[ℓ(x; A(S))]. For each target,   Since LLMs rely on massive and diverse datasets, the comthe characteristic vector 1S is adjusted to reflect the subset,   position of these datasets significantly impacts model perand the parameters θx are estimated using a regression loss   formance [295]. For instance, as shown in Figure 3, we can
function like mean squared error over the training subset.   see LLMs require different ratios of domain data to achieve
After training, the datamodel selects the subset S of the size   capabilities such as medical diagnosis, coding, and solving
k that minimizes the loss ˆLDtarg(S) = n                                          1 Pni=1 τθxi (1S) for the  math problems. To this end, data mixing refers to the strategy
target task.                                                         of (1) combining datasets from different domains, sources or
• Gradient-Influence Search. Low-rank Gradient Similarity   structures in specific proportions to train LLMs or (2) making
Search (LESS) [417]  identifies the most impactful subset  LLMs give different proportions of attention on different
of data for fine-tuning LLMs by analyzing gradient simi-  domains (e.g., by changing the sampling probabilities) in the
larities. It  first fine-tunes the model on a random subset   training session. Effective data mixing ensures that the model
                                                     16
                     TABLE 6: Comparison of Data Mixing Methods for LLMs.

          Taxonomy                    Stage                Methods                                           Traits
                                                                   Multi-Source Data Adjusting             Before Training                                                                                      Intuitive and easy to implement, suitable for rapid experimentation.                                                 Pre-training                       [139], [347]        (Human Experience)                                                                Entropy-Based Mixing [152]          Low computation cost with quality quantification by entropy.
                                                                                           Only 10% of DoReMi’s [420] computational resources are required.                                                 Pre-training          Linear Regression Model [263]                                                                                                   Simultaneously train hundreds of small models to accelerate optimization.

                                                                                                  Avoid iterative training of proxy models (low computational costs).                                                 Pre-training         Bivariate Data Mixing Law [152]                                                                                            Show relation between loss and training steps.

                                        Continual Pre-training      Chinchilla Scaling Law [323]     Support knowledge transferring to new domains (↓over 95% training costs).             Before Training
      (Model-Based Optimization)                                                 Pre-training          Exponential Functions [439]                Support datasets without explicit domain division.

                                                                                            Compared to single-objective optimization like [323]
                                        Continual Pre-training       Power-law Function [160]                    [160] ensures that domain performance improvement
                                                                                                                does not compromise general capabilities.

                                                 Pre-training             Classification Model [251]            Reverse engineering for finding the suitable data recipe of LLMs.
                                                                   Calculate domain contribution by                                                 Pre-training                                                 Requires a proxy model, performances well in OOD datasets.                                                                       gradient inner products[135]           During Training
           (Bilevel Optimization)                                                              Dynamically adjust weights by                  Multiple applications like multilingual training,                                               Fine-tuning                                                                     gradient alignment values [302]                  instruction following, large-scale data reweighting
                                                 Pre-training             Group DRO [420]             For pre-training, smooth adjusting to prevent abrupt weight changes           During Training
  (Distributionally Robust Optimization)                                               Fine-tuning               Task-level DRO [278]                 For fine tuning, quick response to task difficulty changes

captures broad generalization capabilities while balancing  from multiple sources, such as Commoncrawl [11], C4 [330],
performance across tasks and domains [140]. Existing data  Github [14] .
mixing methods can be classified into two main categories:        Second, we can utilize metrics to judge different datasets
                                                    and mix them. To calculate the best result rather than
                                                                    just try  different combinations, Bimix   [152] adopts en-   Principles                                                           tropy metrics (e.g., Shannon entropy [343], conditional entropy  [343])  as  the  quality  scores which  are then  norUnlike traditional ML models  like BERT (trained                                                          malized to compute the proportions of each domain (e.g.,
   on smaller, domain-specific data with homogeneous                                                               conditional  entropy, written  as  as Hi  X(t+1)i       | X(t)i   =    distributions), LLMs require massive multilingual or
                                                                                                                                                                    |  x), where X(t+1)i   multi-domain corpora, raising the critical challenge   −Px∈X(t)i Px′∈X(t+1)i   P(x, x′) log P(x′
    of optimizing dataset mixing ratios for performance.                                                             X(t)i   are sets of tokens at positions t + 1 and t separately,   Current methods use heuristic experimentation or for-                                                 x and x′ are tokens belonging to them, P(x, x′) is the joint
   mulate ratio-performance relationships (e.g., valida-                                                                   probability, P(x′ | x) is the conditional probability.
    tion loss), but cost-effective determination of optimal
                                                     Before-Training Mixing (Model-Based Optimization).    ratios, beyond heuristics, remains unresolved due to
                                                         This category of methods design linear or non-linear models   high cost demands for functional approximations.
                                                             that depict (i) the relation between the distribution of each
                                                        domain, (ii) validation loss, and (iii) some other variables like
Before-Training Mixing (Human Experience). This   training steps, based on which they find the optimal settings
method provides empirical data mixing strategies such as   through various model-based techniques.
setting different ratios of datasets based on various factors  (1) Linear Regression Model: Some methods utilize pairs
(e.g., complexity and diversity of the datasets) that likely   like data mixtures and corresponding model performance to
improve LLMs’ abilities.                                                      fit a linear regressing model, such that finding the best data
    First, to study the effect of data mixture, there are works   mixture ratios.
that experiment heuristically on different data ratios for pre-      Typically, REGMIX [263] defines the domains by source
training of LLMs. [139] suspects training sequence from   (like ArXiv, FreeLaw, etc.), which uses Dirichlet distribution
simple to complex data would improve LLMs’ performance,   (which controls the distribution of probabilities across multithus introduces a two-stage data mixing strategy for LLM   ple categories with a parameter) to generate all kinds of data
pre-training: (1) It first blends web-crawled data with minimal   distribution of several domains to train a small-scale proxy
high-quality content (1.9% math, 15% code), testing ratios  model to collect performance data, which is then used to fit
(<35% high-quality) and selecting optimal mixtures via eval-   a linear regression model (LightGBM [205]) to predict the
uations on CommonsenseQA [371] and HumanEval [95]. (2)   optimal data mixing distribution. Then REGMIX uses both
It then filters low-quality data, boosting math (24%→29%),   the best distribution and the average of top-100 distributions
code (20%→29%), and instructional alignment data. Ratios   to verify on variations of TinyLlama [459] with additional
are similarly optimized through empirical validation. The   layers with versions of 1B and 7B.
method iteratively refines proportions using down-sampled  (2) Non-linear Regression Model: There are also many
Megatron-8B [355] for efficiency, then scales findings to a  methods that design non-linear regression models for data
25B model, balancing diversity-quality tradeoffs with reduced   mixing by considering more complex training characters.
experimental overhead. Similarly, Slimpajama [347] explores   • Bivariate Data Mixing Law. Based on observations  of
the impact of data source diversity and weight distribution   validation loss changes due to variables  like domain proon model performance by adjusting the proportions of data   portion (where the data come from different sources  like
                                                     17
Pile-CC) and training steps, BiMix [152] proposes Bivariate   ratios of data, the relationships between loss and mixture
Data Mixing Law that depicts the relation among domain’s   ratio, and training volume fit in power-law forms, which are
proportion, training steps and validation loss, which can be   described as L(R) = α · Rs + β and L(T) = α1 · T s1 + β1,
                              Bi + Ci  , where Ai,Bi,Ci are  where α, β, s, α1, β1 and s1 are fitting parameters. Based the                               αi   sβiwritten as Li (ri, s) =  rAii
domain-dependent scaling coefficients, αi and βi are power-   relationships, they propose a metric Critical Mixture Ratio,
law exponents that control the influence of domain proportion  which is the maximum data mixing ratio that balances beand training steps respectively, s represents the training step   tween (1) significantly reducing domain loss while (2) keeping
count. It utilizes the law to fit the actual data curves by fixing   the increase in general loss within a pre-defined tolerance
the domain’s proportion or training steps and varies the other   range. Based on the two aspects, the ratio  is defined as
one to get validation loss by training a small model (decoder-  R∗= max{R | R ∈F}, where R is the ratio of generic dataset
only transformers based on the DoReMi [420] architecture  and domain-specific dataset, F is feasible mixture ratios which
with 280M parameters). After depicting the  relation, we   comprises all mixing proportions that satisfy the constraints
model the task as an optimization problem (resolvable by La-   of the general loss function.
grange multipliers) and then verify on larger LLM (decoder-  During-Training Mixing (Bilevel Optimization). This
only transformers based on the DoReMi [420] architecture  method adopts a closed-loop optimization technique that
with 1B parameters).                                         ensures model parameters are well optimized [108]. Gener-
• Chinchilla Scaling Law. D-CPT [323] establishes a math-    ally, Bilevel optimization involves two nested optimization
ematical relationship which could be used to find the best   problems: (1) the inner-level problem ensures model parammixture of general and domain-specific data between valida-   eters are optimized under given weights  (e.g., minimizing
tion loss, model size, data size, and domain data mixing ratios   weighted training  loss), while (2) the outer-level updates
based on Chinchilla Scaling Law [170] to optimize domain-   weights through backpropagation of validation loss, forming
specific continual pre-training as L(N, D, r) = E + NAα +   a closed-loop optimization.
B·rη Dβ + (r+ϵ)γC   (N  is model parameter count, D is training      Typically, ScaleBiO [302] reconstructs the data sampling
data volume (number of tokens), r is domain corpus ratio,   weight optimization problem into a bilevel optimization probE, A, B, C, α, β, γ, η, ϵ are fitting parameters), with a variation   lem, where outer-level problem  is adjusting data weights
which introduces K which describes the difficulty to learn the   to minimize validation loss; and the inner-level problem is
domain’s knowledge as L(N, D, r) = E+ NαA + B·rηDβ + (r+ϵ)γC  +   adjusting model parameters to minimize weighted training
 F  (F  is a fitting parameter). It  fits formula parameters   loss and it could be applied to tasks like multilingual trainingKµ
through small-scale experiments to predict performance under   (mixture of languages) and instruction following (mixture of
different training configurations and find the suitable ratio   quality). ScaleBio first experiments on small models. Then it
to minimize the domain validation loss while ensuring the   extends to larger models like LLaMA-3. ScaleBiO initialize
generalization loss does not exceed the specified threshold.     the weights equably for all data sources. In each iteration,
• Exponential Functions. Data Mixing Law [439] establishes    it randomly selects a subset of data sources to update their
an exponential relationship between validation loss and data   weights: for the selected data sources, it adjusts the weights
mixing ratios of several domains (e.g., public datasets like  by optimizing the gradient of the validation loss, prioritizing
Pile-CC, Books3), L(r) = c + k exp Pi tiri  , where L(r) is   the increase of weights for data that contribute significantly to
the validation loss, r represents the mixing ratios of different  model performance, while decreasing the weights for data that
domains, and c, k, and  ti are learnable parameters. That   have less impact on performance. After updating the weights,
is,  it experiments on a small model with the exponential   retrain the model parameters and repeat the process until
relationships to predict the best data domain mixing ratios on   convergence.
LLM performance with scaling laws, which combines training     To enhance the  efficiency  of BiO-based data mixing,
step scaling laws (L(S) = c + kSα, where S is the number of  DoGE [135] defines (i) inner-level problem as that under
training steps, and α is a fitting parameter.), which is used to   the condition of fixed data mixing ratios, optimize the proxy
infer the validation loss at target training steps from results at  model parameters to minimize the weighted sum of domain
smaller steps, and model size scaling laws (L(N) = c + kN β,   losses; and  (ii) outer-level problem as adjusting the data
where N is the number of model parameters, and β is a fitting   mixing ratios such that the model parameters obtained through
parameter), which is used to infer the validation loss for large   inner-level problem optimization achieve optimal performance
model sizes from smaller model sizes.                      on the target loss. The method is executed on a small-scale
• Classification Model. [251] aims to find the data proportion   proxy by following steps: Initially, it sets the domain weights
of closed-source model by data proportion detection, which   as a uniform distribution. In each iteration, it dynamically
first generating large-scale data from the LLM, then using a   adjusts the weight of each domain based on the gradient alignclassification model to categorize the generated data and com-  ment value (calculated as the inner product of the gradient
pute perplexity, deriving the proportions of pre-training data   of current data domain and the sum of gradients from all
based on the Data Mixing Law [439] (which is a mathematical   data domains), which measures the contribution of the data
formula describing the relationship between the proportion of  from the current domain to the gradient direction of all other
pre-training data and the model’s loss in different domains.).   domains’ data. Using the updated weights, it resamples the
                                                         data and updates the model parameters. Repeat the process• Power-law Function. CMR [160] aims to optimize the confor multiple iterations until the weights stabilize, then applytinual pre-training by finding the best ratio of generic dataset
                                                               to actual LLM pre-training.and domain-specific dataset. Based on the research before and
the data observed on different sizes of models with different  During-Training Mixing (Distributionally Robust Op18
timization). To search for a robust data mixing strategy      Despite the advantages, synthetic data can negatively
(which can be sub-optimal but with low uncertainty), some   impact LLM training, such as when characteristics like toxmethods adopt Distributionally Robust Optimization (DRO)   icity are inherited from the source model or even amplifor data mixing. DRO achieves robustness against distribu-   fied [352]. Thus, it is vital to design data synthesis methods for
tional uncertainty by optimizing for the worst-case scenario  LLMs [495]. As shown in Figure 4, we discuss methods dealing
within a set of distributions (referred to as the uncertainty set   these problem through the diverse LLM stages, including preor ambiguity set).                                             Training, SFT, Reinforcement Learning and RAG.
• For LLM pre-training, DoReMi [420] defines the worst case  Knowledge Distillation. Due to LLMs’ massive parameter
as domains where the proxy model underperforms compared                                                                   scale and high resource demands which make practical deployto the reference model, which initially sets the domain weights                                                   ment challenging, so we utilize knowledge distillation (such
as a uniform distribution and each domains contains several                                                              as designing paradigms to prompt LLM to generate highsample sets, and uses it to train Transformer decoder-only LM                                                                quality data) to training a student LLM with less parameters
with 280M parameters and computes loss in each example set,                                                               to mimic the target model’s generation ability.
which provides a reference point to measure the improvement                                                        • Task-Specific Prompt Distillation. To significantly reduce
potential (the loss difference) of the proxy model in each                                                                 inference costs and latency while maintaining performance,
domain. Next, DoReMi trains a small-scale proxy model                                                                    [353] employs  task-specific prompts: (1) Chain-of-Density
(also Transformer decoder-only LM with 280M parameters)                                                       (CoD): Iteratively adds entities to summarize for enhanced
by adjusting the domain data weights through DRO, which                                                                   density. (2) Chain-of-Thought (CoT): Guides reasoning tasks
dynamically adjusts the domain weights and tilt the weights                                                                             (e.g., math) through stepwise logic. Using GSM8K [106] data
toward domains with larger losses (compared to the reference                                                    and Llama-3.1-405B-Instruct, synthetic data  is generated
model). Finally, validate performance of weighted domain                                                                      for fine-tuning smaller models (Llama-3.1-8B/70B-Instruct)
data on large models (Transformer decoder-only LM with 8B                                                             paired with simplified prompts, balancing efficiency and task
parameters).                                                                    specialization.
• For LLM fine-tuning, tDRO [278] defines the worst case                                                        • Code Verification and Error Correction Distillation. Exist-the same as DoReMi, which computes the relative loss for                                                              ing knowledge distillation methods (e.g., Chain-of-Thoughteach domain with a proxy model (e.g. Qwen1.5-0.5B [69]);                                                             Fine-tuning) rely on synthetic data generated by LLMs, butand they compare the training loss of domain data with                                                          such data often contains incorrect intermediate reasoningthe reference model (e.g., Qwen1.5-0.5B), and evaluate each                                                                steps which can mislead small models during learning, hin-domain’s potential for model improvement, and update the                                                             dering the improvement of their reasoning capabilities.domain weights accordingly, giving more attention to high-                                                   Pad [496] proposes Program-aided Distillation (PaD) toloss domains. Finally, the updated weights are normalized to                                                            address error-prone synthetic data in knowledge distillationform a new sampling distribution and repeat the process to                                                         with (i) Programmatic Reasoning: LLMs generate executableget final data distribution.                                                        code (e.g., math problems as Python calculations) instead of
                                                             natural language CoT, with Python compilers auto-filtering
2.3.6  Data Distillation and Synthesis                             logic errors. (ii) Error-Injection Training: Models learn error
Synthetic data, which mimics real-world scenarios,  is par-   correction by fixing synthetically injected AST-based errors
ticularly valuable for resolving problems such as (i) data   (e.g., NameError). (iii) Semantic Validation: Decoding selects
scarcity (e.g., augmenting data for a small dataset) [426], (ii)   steps via semantic alignment scoring (e.g., cosine similarity)
privacy concerns (e.g., replacing sensitive data with synthesis   to prevent error propagation. PaD replaces flawed CoT steps
data) [419], (iii) the need for diverse and high-quality datasets   with verifiable program logic, enhancing small models’ rea-
(e.g., generating examples for underrepresented cases) [260],   soning robustness through code-based distillation and self-
(iv) lack of reasoning data (e.g., for code, chain of thought),   correction mechanisms.
(v) human alignment (e.g., label better LLM’s response by   • Multi-stage Collaboration Distillation Between Student modhuman beings or LLMs).                                               els. In domains with high annotation costs (e.g., biomedical parsing) or complex task structures (e.g., syntactic/sePrinciples                                           mantic parsing), labeled data  is extremely scarce, making
                                                                  traditional supervised fine-tuning ineffective. MCKD [467]
                                                              introduces Multi-stage Collaborative KD (MCKD) for low-    Traditional ML methods use rule-based templates,
                                                              resource generation as 3 steps.  (i) Initialization: GPT-3.5    basic  augmentation   (lexical  substitution,  backgenerates pseudo-labels for unlabeled data. (ii) Collaborative    translation), or statistical models to create limited
                                                                      Distillation: Splits data into two subsets for cross-labeling via    synthetic data, addressing data scarcity/class imbalpaired T5-Base models, reducing noise overfitting. Iteratively    ance. While LLM-driven synthesis employs LLMs
                                                                      refines labels over 3 iterations. (iii) Final Training: Trains a    to produce diverse, high-quality data, tackling data
                                                                    single model on refined labels. Achieves near-supervised per-    scarcity, privacy concerns, and diverse training needs.
                                                        formance with 50 labeled examples (vs. 500 required tradition-   Key paradigms include: (i) sample-driven generation,
                                                                      ally) through multi-stage noise reduction and collaborative     (ii) domain-aligned  synthesis, and  (iii)  reasoningpseudo-label optimization.    centric formatting. Challenges involve ensuring rigorous reasoning chain synthesis and optimizing cost-      Pre-training Data Augmentation. The pre-training stage
    quality balance in data production.                           of LLM requires a vast amount of data and it can be costly
                                                               to synthesize such data with powerful models  like GPT19
4. Therefore, there are techniques like distillation [481], or   3’s Chinese proficiency and scientific reasoning capabilities
simply mixing synthetic data into the whole corpus.            while mitigating catastrophic forgetting. They utilize Mistral-
•  Distilled LLM  for  Mathematical Data  Synthesis.  Ji-  7B [188] to generate multidisciplinary  scientific questionuZhang3.0 [481] proposes an LLM-based synthesis method for   answer pairs (e.g., Q&A on “explaining the electrostatic rehigh-quality math problems: (i) Model Distillation, fine-tunes   pulsion principle of ion double layers in electrolyte solutions”)
DeepSeekMath-7B on GPT-4-generated QA pairs (with cu-  from seed data collected and classified into multiple discirated prompts and math texts) to mimic GPT-4’s generation.   plines by TinyBERT [195] and BERT-Tiny-Chinese [23] from
(ii) Uses gradient similarity to prioritize task-relevant data.  Dolma’s CC [361] and C4 [120]. And generate coding problems
(iii) Refines the model with filtered data to produce aligned   with LeetCode algorithm tasks as seeds by Magicoder-Soutputs. The final math synthetic corpus are generated by  DS-6.7B [409] .These are mixed with Chinese, English, and
the refined model based on the multi-source corpus (e.g.,   synthetic data in a 1:7:2 ratio, significantly boosting scientific
Wikipedia) and prompt sets.                                   reasoning.
• Fintuned LLM for Instruction-Response Pair Synthesis.      Additionally, through substitution experiments (validatIn  order  to study the  effect  of  supervised  pre-training,   ing data strategies using TinyLlama-1.1B [459] as a proxy
Instruction PT [99] introduces an Instruction Synthesizer   model), they find that (1) a 20% synthetic data ratio with an
(Mistral-7B finetuned on 40+ task categories) to augment raw   error rate below 30% yields optimal results; and (2) a curricutext with few-shot multi-task instructions (e.g., ”Summarize  lum progressing from simple to complex topics outperforms
school activities” →QA/reasoning pairs). Unlike GPT-style  random training.
pre-training, it integrates structured task execution (QA, clas-   • Code Interpreter + LLM Prompting for Code Synthesis.
sification) alongside language modeling. This hybrid approach   Current code generation models rely heavily on large teacher
boosts data efficiency (500M model ≈1B baseline) and multi-  models (e.g., GPT-4) to generate synthetic training data,
task adaptability from pre-training.                            leading to poor scalability, high costs. And most datasets
• LLM Prompting for Mathematical Data Synthesis. Current   focus on direct code completion or text-to-code translation,
math-specialized LLMs rely on SFT with problem-solving   but lack Input-Output (I/O) case-based reasoning tasks (e.g.,
data (e.g., step-by-step solutions). However, since CPT im-   inferring code from example mappings like “hello” →“olleh”).
provements in math are far less significant than SFT gains.     This gap results in weak generalization for inductive programTo study the impact of problem-solving data in continual  ming challenges.
pre-training, [98] proposes enhancing models’ mathematical     To bridge  this gap, Case2Code  [344] generates  trainreasoning capabilities by augmenting problem-solving data   ing data through four steps: (i) Extract executable Python
(e.g., step-by-step solutions  for common math problems)   functions (with input/output parameters) from open-source
during pre-training, rather than relying solely on traditional   repositories; (ii) Use lightweight LLMs (e.g., InternLM2-7B)
math corpora (e.g., theorem texts). First, a student model   to analyze function logic and generate diverse input samples;
(Llama2  [386])  is  utilized to generate answers from the    (iii) Execute functions to obtain real outputs and filter invalid
collected math problems. Then,  it uses a teacher model   results; (iv) Convert I/O pairs into natural language prompts
(Llama2 [386] with more parameters) detects errors in a stu-   with diversified templates for improved generalization. This
dent model’s solutions and generates corrective steps guided  method leverages ”code interpreter + lightweight LLM” to
by prompts. This teaches the target LLM self-checking and   cost-effectively produce 1.3M training samples, eliminating
error-correction  skills. Experiments indicate continual pre-   reliance on expensive teacher models.
training excels at learning complex reasoning (e.g., multi-   • LLM-based Clustering for Synthetic Data Evaluation. In
step equation solving) than SFT, where MathGPT-8B using   order to study the impact of diversity of large-scale synthetic
only 100B well-generated math-related tokens can exhibit   data, [92] introduces an LLM-based clustering method to
capabilities comparable to Qwen2-Math-72B [434].             quantify synthetic data diversity and analyze its impact on
• LLM Prompting for Rephrasing Synthesis. To introduce  model performance. (i) Builds hierarchical topic trees from
more  diversity to the data, some methods rephrase the   web-crawled data via GPT-4  (e.g., Quantum Computing
data to different styles of texts like Q&A or concise defini-  →Qubit Types →Superposition);  (ii) Generates diverse
tion. WRAP [282] leverages instruction-tuned models (e.g.,   datasets by varying topics, prompts (styles, target audiences,
Mistral-7B) to rephrase web text (C4) into four formats: (i)   etc.) and LLMs (GPT-4o, Llama-3, etc.). Experiments across
simple vocabulary and sentence structures that are under-   different diversity combinations show synthetic data diversity
standable to young children. (ii) Standardized encyclopedia-   positively correlates with model performance on benchmarks
style expression. (iii) Complex terminology and concise aca-   like HellaSwag [449] and ARC-Challenge [142].
demic sentence structures. (iv) multi-turn dialogue. Mixing   • LLM Prompting for Multimodal Image-Text Synthesis. Currephrased and original data trains LLMs to adapt to diverse   rent approaches for synthesizing multimodal pre-training data
formats (e.g., zero-shot QA), achieving 3× faster training and   typically employ two main approaches: (1) the generation
50% lower perplexity on Pile benchmark [149] via hybrid real-   of images conditioned on textual input using text-to-image
synthetic data synergy.                                      models, and (2) the augmentation of uncaptioned or simple-
• LLM Prompting for Cross-language Synthesis. LLMs like   captioned source images via multimodal models. In the doLlama-3  exhibit  deficiencies  in  cross-language  tasks and  main of text-to-image synthesis, current methods use diffumultidisciplinary  scientific reasoning, while continual pre-   sion models [145] for image generation. Examples include
training often triggers catastrophic forgetting (e.g., perfor-   DiffuseMix [185], which enhances datasets by augmenting
mance degradation in original capabilities like English tasks).  image samples through the blending of original and diffusion-
[93] proposes to synthesize data so as to enhance Llama-   generated images, and EDA [387], which applies diffusion
                                                     20
                                                 TABLE 7: Data Synthesis for LLM.models to produce variations of real images that retain semantic consistency while augmenting the dataset. Concerning im-       Stage          Category                  Methods
age captioning, several studies focus on improving the quality                   Reasoning Augmentation                Cot [353]                                                                                                       Distillation                                Prompt with Tools [496]
of image-text pairs. LaCLIP [133] uses ChatGPT to rewrite                    Data Augmentation         Prompt with Multi-Agent [467]
existing captions, thereby introducing greater diversity in      Pre-Training     Data Augmentation      DistillationPrompt [99],+ Fine[98],Tuning[282], [93],[344],+ Prompt[92][481]
linguistic expression while maintain the core semantic content.                    Data Augmentation         Prompt [233], [179], [260], [290]
                                                                                                       Human Label [253]A limitation of this method is the potential for visual semantic       SFT      Reasoning Augmentation         Prompt [178], [173], [346]
loss due to the language model’s lack of direct access to the im-                                           High QualityAutomatedReasoningLabelData[399][442], [230]
age. To mitigate this, VeCLIP [222] incorporates a multimodal                   Prompts Optimization               Prompt [401]                                                                RL                                 RLHF [71]
LLM (LLaVA) to provide a detailed visual description of the                  Human Feedback           RLHF By LLM [476]
image contents (e.g., color and shape attributes, objects, and      RAG         Privacy Protection                Prompt [450]
relations among objects). This description is then fused with
the original caption by a LLM to yield a more comprehensive                                      MMIQC [260] enhances mathematical reasoning by iterativelyfinal caption. To simultaneously synthesize both image and                                                             generating complex, diverse problems from existing ones fortext samples, CtrlSynth [83] proposes a system comprising                                                                   fine-tuning. Using a seed dataset, GPT-4 creates problems viathree modules: the Florence-large [418] vision tagging model                                                     added constraints, variables, or extended reasoning. A filter-to extract basic visual elements of an image (e.g., color and                                                              ing mechanism ensures logical consistency, problem-solutionshape attributes, objects, and relations among objects), the                                                             alignment, and correctness, with validated data expanding theQwen2-7B-Instruct [434] language model to generate syn-                                                             dataset iteratively.thetic text which meets the requirements in the instruction,                                                        • LLM-based Alignment Data Augmentation. Domain knowl-and the stable-diffusion-x1-base-1.0 [314] text-to-image model
                                                         edge  is one thing, and lead LLM’s knowledge align withto generate novel and diverse image samples based on text                                                                 instruction is another thing that could be done to get betterprompts.                                                         performance through techniques like few-shot prompting.
SFT Data Augmentation. The SFT stage of LLM training      AgentInstruct [290] uses LLMs to create scalable,  dimainly focus on improvement of specific domains (math,   verse Q&A data. GPT-4 converts raw input (text/code) into
medicine, etc.), aligning LLM’s knowledge to instructions, en-   structured formats (argument passages, API lists) to enable
hancing reasoning ability, etc. Current methods take LLMs as   diverse instruction creation. Multiple GPT-4 agents generate
the main method to generate data with some designed frame-   varied task instructions and answers following a detailed
works. Many works [179], [260], [290] take existed datasets as  taxonomy (e.g., reading comprehension, coding tasks). GPTseeds to synthesize mimic datasets.                         4 and Claude-3 then refine tasks by adding complexity (e.g.,
• LLM-based Knowledge and Q&A Pairs Synthesis. To enrich   integrating dense context or escalating difficulty), ensuring
or enhance the diversity of data for better model performance,   high-quality, adaptable outputs.
there are various prompt frameworks such as building topic       Similarly, SELF-INSTRUCT [401] aligns LLM’s knowltaxonomy [233] and iterative synthesis [179].                  edge to prompts by generating task instructions and examFor example, to cover various domains of human knowl-   ples: Starting with a small set of manually written seed tasks,
edge, GLAN  [233]  introduces  a  knowledge-classification   a LLM  (e.g., GPT-3)  is prompted to generate new task
framework for synthetic text generation by GPT-4. (i) Or-   instructions covering various task types, such as classification,
ganize knowledge domains (natural sciences/humanities) into   question-answering, and generation. Next, different strategies
disciplines (math/programming) by; (ii) Develop course out-   are employed to generate inputs and outputs based on the task
lines with units (e.g., ”Intro to Calculus”) and core concepts   type. For instance, for classification tasks, possible class labels
(e.g., ”Limits”); (iii) Use GPT-4 to create diverse questions by   (e.g., ”positive” and ”negative”) are generated first, followed
combining concepts, then generate answers with faster GPT-  by inputs corresponding to each label. For open-ended tasks, a
3.5. This structured approach ensures systematic coverage   question description is generated first, followed by an answer.
of knowledge areas while balancing generation quality and  The generated data undergoes multiple rounds of filtering,
efficiency.                                                     including removing duplicates or invalid data and ensuring
   Though this could enhance understanding of LLM about   input-output alignment.
many domains, but to get better enhancement  still needs  SFT Reasoning Data Augmentation. Synthesize reasonto focus on one aspect, like math, KPDDS [179] identifies   ing data (e.g., code, chain of thought) through techniques like
mathematical problem themes (e.g., algebra, geometry) and   Chain-of-thought(CoT), or utilizing verification tools for more
core skills (e.g., factoring) using GPT-4, then constructs a   rigorous reasoning.
matrix mapping theme co-occurrence probabilities to guide   • Prompting LLM To Math Reasoning With Verify Tool. Also
logical problem generation. GPT-4 synthesizes new questions   for math, MUSTARD [178] utilizes mathematical proof tools
based on these themes and solutions, which are evaluated for   to get reasoning enhancement. First, fundamental concepts
quality (clarity, coherence) and refined via GPT-4 voting. The  from the field of mathematics are selected as seeds, and GPTmethod further diversifies questions through variations and   4 generates corresponding problems through two types of
applies iterative voting to optimize output. This structured   solutions: (1) One is a natural language explanation of the
approach ensures contextually coherent, avoiding random   reasoning process, and (2) the other  is a formal language
combinations.                                                  solution that can be verified  (e.g., code compatible with
   Instead of combining elements like KPDDS (e.g., com-   mathematical proof tools). Next, formal solutions are verified
bining  algebra  and  geometry  to  synthesize  problems),   using mathematical proof tools to ensure the correctness of
                                                     21
the reasoning and answers. For content that fails verification,   step’s ability to derive the correct answer.
the model adjusts based on feedback and re-verifies until a   • High Quality and Well Format Data Are The Keys To Better
correct result is generated.                                   Reasoning. Moreover, LIMO [442] and [230] state that high
• CoT Data Synthesis By LLM Exploring. Works mentioned   quality and well-formatted reasoning data are keys to high
above highly rely GPT-4 for its advanced ability for math   performance. [442] emphasizes stimulating complex reasoning
to generate problems and solutions to fine-tune for higher   capabilities in LLMs through a small number of high-quality
reasoning ability. While more recent research try to enhance   training examples with questions and reasoning chains. PowLLMs’ reasoning ability by technique like Chain-of-Thought   erful models (such as R1, DeepSeek-R1-Distill-Qwen32B) are
(CoT, which let LLMs use tokens to output their reasoning   used for evaluation and synthesis, retaining problems that
steps) and synthesis or label finer reasoning data for training.   remain challenging. Each problem is accompanied by detailed
  By generating CoT data that covers a wide range of rea-   solutions and reasoning chains (from official solutions, expert
soning paths through a trial-and-error self-verification loop,   solutions, and LLMs-generated Cot, etc.) and filtered by
[173] breaks the traditional limitation of relying solely on   rules-based and LLM-assisted methods.
correct reasoning paths. Specifically, multiple LLMs (e.g.,       [230] finds that the overall structure of the reasoning steps
Qwen-7B, Llama-3-8B) are utilized to generate diverse so-    is more important than the specific content. With problems
lutions for the same mathematical problem (20-50 responses  from Numina-Math [235] etc. and long CoT generated by
per problem) to encourage models to explore incorrect paths  DeepSeek-R1 [162] and QwQ-32B-Preview [379] as data to
(e.g., wrong formulas, logical leaps) while retaining complete   fine-tune. With modification of the fine-tune data, reveals that
error analysis. Then a verifier LLM (e.g., GPT-4) performs   training the model with incorrect answer samples results in an
critical analysis on each response: (a) For incorrect paths,   accuracy drop of only 3.2% compared to training with correct
annotate the error steps and generate correction suggestions   samples. However, shuffling 67% of the reasoning steps in the
(e.g., “Step 3 misapplies the cosine theorem, which should   training samples leads to a 13.3% drop in accuracy on AIME
be replaced with the Pythagorean theorem”). (b) For correct   2024 problems relative to training with correct samples.
paths, extract key reasoning steps to form a concise CoT.                                                 Reinforcement Learning The RL stage of LLMs findMerge corrected incorrect attempts with correct paths to                                                            the most human-preferential responses within the multipleconstruct multi-branch CoT.                                                             responses generated by LLM of one instruction. Works like    Similarly,   Satori   [346]  introduces  Chain-of-Action-                                                                            [71], [476] manually label the responses or let LLMs do theThought (COAT), a reasoning framework with meta-action                                                                    job.tokens (Continue / Reflect / Explore) enabling dynamic                                                            Label better LLM’s response by human or LLMs. To alignpauses, logic verification, and strategy shifts with a two-stage                                                            the model’s responses with human expectations, [71] gatherspipeline: (i) Multiple LLM agents generate COAT-formatted                                                                 helpful and harmless data through open-ended conversations.reasoning  chains  to  fine-tune a base model  for COAT-                                                      Then, a preference model is trained to score the responsesformatted syntax mastery. (ii) Partial rollbacks (≤5 steps)                                                                   in the data, providing a basis for reward optimization infrom historical reasoning (correct/incorrect paths) append                                                             reinforcement learning. The preference scores guide the op-<reflect> to trigger revised reasoning with reinforcement                                                               timization of the language model’s responses. Next, the latestlearning (RL) combined with rewards for answer correctness,                                                     model generates new data, continuously updating the pref-error correction, and penalties for failures. The RL-enhanced                                                             erence model to improve performance on high-quality data.model  is  distilled  into base models  (e.g., Llama8B)  for                                                 To improve efficiency, [476] proposes a new chatbot evalua-iterative refinement.                                                                 tion method using language models as ”judges” to compare   These works propose framework by letting LLM reason by                                                    and score chatbot responses, with the goal of automatingthemselves, and we also have works that label reasoning data                                                            the evaluation process and reducing human involvement. Itfor fine tuning to get reasoning ability.                                                              introduces two benchmarks: one focusing on multi-turn con-• Reasoning Data Labeling. [253] compares the  effects of                                                               versation performance and another collecting user preferencesoutcome supervision (provides feedback based solely on the                                                                via crowdsourcing. The method also addresses potential bi-correctness of the final answer) and process supervision (pro-                                                                     ases, such as preferences for answer order or length, throughvides feedback for each step in the reasoning process) on                                                                   strategies like swapping answers, using few-shot examples ormathematical reasoning tasks by comparing manually label-                                                          Chain-of-Thought. The approach demonstrates that languageing the reasoning steps generated by GPT-4 with outcome                                                       models can achieve high consistency with human evaluators,supervision. The  results showed that process supervision                                                             providing a scalable and interpretable framework for efficientmodel achieved significantly higher problem-solving accuracy                                                          chatbot assessment.(78.2%) compared to outcome supervision model (72.4%)
   But this would cost too much manual effort, so MATH-  Retrieval-Augmentation Generation. The RAG stage
SHEPHERD  [399] proposes a method to automatically gen-   mainly offers knowledge and documents from outside to avoid
erate process-annotated data for training Process Reward   additional training cost. Main works in this stage of data
Models (PRM, which evaluate the quality of each reasoning   synthesis focus on privacy issues.
step). First, complete the remaining reasoning and answers      Replace sensitive data with synthesis data. In order to mitmultiple times for the initially generated reasoning steps with   igate the privacy issue, [450] proposes a two-stage synthetic
LLM, then each step is scored based on two metrics: (1) Hard   data generation and privacy-enhancing method for the RAG
Estimation (whether the correct answer is generated, with   stage of LLM.
values of 0 or 1). (2) Soft Estimation (the proportion of correct      In the first stage, key information is extracted from the
answers generated through this step). These scores assess the   original data (such as “symptom description” and “treatment
                                                     22
plan” in medical dialogues), and LLM is used to generate   undesired data such as HTML tags and translate text), filtersynthetic data based on key information but does not contain   ing, and deduplication (using MinHashLSH in Section 2.3.2)
sensitive details.                                               operators; (2) The analyzing module featuring refined data
   In the second stage, LLMs are applied to the synthetic   probing and automatic evaluation.
data, and rewriting strategies are employed to eliminate
potential privacy leaks (such as removing specific names or   2.2.7.2 Typical data pipelines
obfuscating descriptions).
                                                    Data processing pipelines aim to orchestrate a subset of data   This process of evaluation and rewriting is repeated to
                                                              processing operations (in a specific order) that transform rawensure that the generated data retains its key utility while
                                                         data into high-quality LLM training data (mostly for thecompletely avoiding privacy concerns.
                                                                pre-training stage). Here we showcase three representative
2.3.7  End-to-End Data Processing Pipelines                     pipelines.
                                                        • The MacroData Refinement (MDR) pipeline is designed toWith above data processing methods, we separately introduce
                                                              construct the RefinedWeb Dataset, which has been used forexisting frameworks that support common processing operapre-training Falcon LLMs [311]. MDR refines web-scale datations; practices of integrating some of these methods within
                                                       from Common Crawl [11] through three main operations.pipelines in real-world LLM data preparation; together with
some preliminary pipeline orchestration methods.                 (i) Data acquisition: MDR first applies a lightweight URL
                                                                                 filter to exclude irrelevant links before any computationally
                                                                  intensive steps. It then extracts text from WARC files using   Principles                                                           warcio and Trafilatura  [73], followed by language identification (i.e., removing content with limited natural language)
   When designing data processing  pipelines, several                                                             using fastText [199] as implemented in CCNet [410].
    critical factors must be considered: (1) the trade-off                                                                              (ii) Data filtering: To eliminate low-quality content, MDR   between data quality and quantity; (2) dependencies                                                       employs both (1) document-level filtering [328] and (2) line-    across the processing operations (e.g., text extraction                                                                       level filtering, which removes noisy content such as social    necessarily preceding operations  like deduplication                                                     media counters or navigation links.   and filtering); (3) efficiency optimization (e.g., con-                                                                                (iii) Data deduplication: Despite prior filtering, substantial    ducting computationally intensive steps like model-                                                            content duplication remains, which can degrade model per-   based filtering after lightweight processing steps like                                                           formance. MDR performs both fuzzy deduplication using Min-  URL filtering).                                                   Hash and exact deduplication with suffix arrays to minimize
                                                          redundancy. To address computational limits, the Common
2.2.7.1 Typical data processing frameworks                   Crawl corpus is partitioned into 100 segments, with deduplicaData processing frameworks provide built-in libraries, oper-   tion performed per segment. Additionally, to avoid cross-part
ators, and intuitive interfaces that can benefit the design   redundancy, URL-level deduplication is applied by excluding
of data processing pipelines for different LLMs. Here we  URLs already retained in earlier segments.
showcase three typical data processing frameworks.                 Overall, MDR follows three core design principles: (i) scale
    (1) Data-juicer [90] is an open-source framework designed    first, by maximizing data volume from Common Crawl to
for customizable, high-quality, and efficient data processing.   support large model training; (ii) strict deduplication, as rigIt offers a diverse range of pre-built data processing opera-   orous redundancy elimination is critical for training efficiency
tors such as data formatting, mapping, filtering, and dedu-  and generalization; and (iii) heuristic filtering, favoring ruleplication. Additionally, the framework features visualization   based filters over ML-based ones to reduce bias and maintain
and automatic evaluation, enabling users to receive immedi-   transparency.
ate feedback on their data pipeline. To manage large-scale   • The DCLM-Baseline pipeline also processes data from the
datasets effectively, Data-juicer is optimized for distributed  Common Crawl dataset. Different from MDR, in addition
computing, ensuring robust performance and scalability.        to text extraction and language identification, it applies ef-
    (2) Dataverse [305] is an open-source framework designed   ficient heuristic filtering [311] to exclude irregular content
to simplify custom ETL (Extract-Transform-Load) pipeline   (e.g., toxic words or webpages from illegal sources). Next,
development through an easy-to-use block-based interface  DCLM-Baseline adopts a Bloom filter for data deduplication,
that enables users to easily customize by adding, removing,   ensuring its scalability with large datasets. Finally, over the
or rearranging blocks. The platform offers a diverse range of   processed data with much smaller size, it conducts modelpre-built data processing operators, including deduplication,   based quality filtering (most computationally intensive) to
decontamination, bias mitigation, and  toxicity reduction,  remove low-quality content. Specifically, a fastText classiwhile also supporting the integration of data from multiple    fier trained on instruction-formatted data, including OH-2.5
sources. Similar to Data-juicer, Dataverse integrates with  (OpenHermes 2.5) and ELI5 (ExplainLikeImFive), is used to
Apache Spark for distributed processing and supports AWS   retain the top 10% of documents.
integration for cloud scalability.                            • The FineWeb pipeline (for preparing a 15T-token pretrain-
    (3) [368] introduces a data processing framework that   ing dataset) starts with text extraction from WARC  files
allows users to customize data processing pipelines using a   using Trafilatura [73], which is more custom than directly
comprehensive suite of operators categorized in two main   using WET format data and language filtering with fastText.
modules: (1) The processing module consisting of data refor-   Different from the above pipelines, it conducts MassiveText
matting (read and import strctured data), cleaning (removed   filtering,  i.e., heuristic quality  filters and repetition  filters


# 23
   RefinedWeb

CommonCrawl       URL filtering   -3.69%   Language    -48.80%   Repetition    -11.54% Document-level -5.82%    Line-level    -6.81%  Fuzzy&Exact  -11.67%  Pre-training
        (WARC)          Text extraction             filtering             removal                  filtering                  filtering           deduplication         data(11.67%)

    DCLM-Baseline

     CommonCrawl          URL filtering    -0.8%    Language     -50.8%     Heuristic     -28.5%   Bloom filter    -6.2%   Model-based   -12.3%   Pre-training
        (WARC)              Text extraction                  filtering                      filtering               deduplication                  filtering                data(1.4%)

   FineWeb

     CommonCrawl     URL filtering       Language        MassiveText          Fuzzy         C4 quality         Custom                 PII            Pre-training
        (WARC)        Text extraction          filtering              filtering         deduplication           filtering              filtering         reformatting         data

                                      Fig. 6: Typical data processing pipelines for LLMs.

on paragraph, line, and gram level [328]. Besides,  it con-   enhance storage efficiency, accommodate multimodal data,
ducts fuzzy deduplication using individual MinHash dedu-  be suitable for model training, ensure security, and influence
plication for each CommonCrawl snapshot, as this approach   compatibility across different frameworks.
matches RefinedWeb’s performance, whereas global deduplication yields little improvement over non-deduplicated data.      Principles
After deduplication, given the observation that the C4 dataset
yields superior performance on some benchmarks despite its                                                    Compared to  traditional machine  learning, LLMssmaller size, a selection of C4 [330]’s heuristic filters is applied                                                                  place greater demands on data being multi-modal andto drop low-quality content such as unpunctuated lines and                                                                       in a unified format. The main challenge  is how topolicy statements. Finally, to further enhance data quality,                                                                  achieve high data reading efficiency in multi-modaladditional custom heuristic filters are developed through a                                                                      scenarios. Current methods address this using tech-systematic process. Moreover, personal identifiable informa-                                                                niques like sequential storage.tion (PII) such as email addresses is anonymized using regex
patterns in the public release of the dataset.
   Compared to MDR and DCLM-Baseline, the FineWeb  Training  Data  Format.  For  training  data,   file  forpipeline is considerably more complex due to its integration  mats are required to have good storage  efficiency  (e.g.,
of multiple layers of  filtering, each inspired by empirical  TFRecord [44]), be adaptable to large amounts of data (e.g.,
evaluations and comparisons with other datasets such as C4  MindRecord [40]), and sometimes be suitable for model trainand RefinedWeb. Its design reflects a trade-off that prioritizes   ing (e.g., tf.data.Dataset [43]).
performance over simplicity.                                     (1) Pure-Text Formats. Common  formats  such  as CSV,
                                                JSON, TSV, and TXT are often used to store pure-text
2.2.7.3 Orchestration of data pipelines                                   LLM data (though they are not limited to such content).
The above data pipelines are mostly designed by experi-   However, for large-scale training datasets (at the PB scale),
ence. Instead, Data-Juicer Sandbox [91] proposes a “Probe-   these formats incur significant storage overhead due to the
Analyze-Refine” workflow, which involves systematically ex-   lack of compression (e.g., not supporting binary encoding),
ploring the impact of various data processing operations   leading to storage waste and slow data loading during LLM
and their orders on model performance, combining effective   training.
operations into data recipes, and optimizing data utilization     To address these issues, TFRecord [44] is based on Protothrough duplication analysis and diversity analysis. The or-   buf (a highly efficient binary serialization protocol) and stores
chestrated pipelines are validated through applications on   data in a row-based format. As a binary format, its size is
state-of-the-art models like Mini-Gemini (for image-to-text   significantly smaller than JSON or CSV. Besides, data can be
generation) and EasyAnimate (for text-to-video generation).   written and read in a streaming manner, making it especially
                                                                 suitable for scenarios like training where data is consumed
2.4  Data Storage for LLM                              sample by sample.
In this section, we introduce storage techniques for LLMs,   (2) Multimodal Formats. Pure-text formats  are not  wellwhich we categorize accroding to the tasks they address,   suited for multimodal datasets containing images, videos, and
including (1) data formats, (2) data distribution, (3) data   text. To address this, file formats such as TFRecord [44] in
organization, (4) data movement, (5) data fault tolerance, and  TensorFlow and MindRecord [40] in MindSpore have been de-
(6) KV cache.                                              veloped to natively support efficient multimodal data storage.
                                                        • Unlike traditional formats (e.g., COCO JSON [10], which
2.4.1  Data Formats                                             store image metadata in separate JSON files), TFRecord [44]
Data formats are file formats for training data and models.   allows users to encapsulate images, labels, and metadata
For LLMs, appropriate file formats for data and models can   within a single tf.train.Example, eliminating the need for
                                                     24
separate label files. Moreover, as multimodal datasets subApplication   Other Processingstantially increase data volume, TFRecord supports data             LLM Training
                                                                                                                                                                                                        Read       1     2     3      Data Loadingsharding, enabling the creation of distributed files that can be                Data Loading                               Request
assigned across multiple servers to facilitate parallel training.             POSIX                               Client API
• MindRecord organizes data into two types of files: (i) the        FUSE Client      Native Client                              3FS       Asynchronous
                                                                                                                                                                                                                                                                                         File Readingdata  file, which contains a  file header, scalar data pages       Filesystem in Userspace                           Start     Response   Method
(e.g., image labels and filenames), and block data pages (e.g.,                                                             RDMA Network
image and text) to store training data; and (ii) the index file,
which maintains indexing information based on scalar data to       Cluster Manager   Storage Service    Meta Service
support efficient retrieval and dataset analysis.                                         ClusterKey-ValueConfigurationStorageData           Chain ReplicationRaw Data  with              Key-ValueMeta DataStorage
(4) Tensor Data Formats. Compared  to  the  storage  for-                                                 Apportioned Queries
mats mentioned above, tensor formats represent data as
multi-dimensional arrays. On GPUs or TPUs, such multi-            FoundationDB       SSD    SSD    SSD        FoundationDB
dimensional structures can be partitioned and processed in
parallel, making them highly suitable for large-scale computa-                    LLM Large-scale Data Storage
tion. For example, tf.data.Dataset [43] can organize various
raw data types (e.g., images, text) into a unified tensor format,                                                                          Fig. 7: The storage architecture of 3FS [15].
ready for direct use by models. However, tensor formats, due
to their dense multi-dimensional storage, incur large storage
overhead and offer poor readability, and are typically adopted   2.4.2  Data Distribution
only in model training.                                                 With the development of LLMs, the scale of LLM training
Model Data Format. Model storage formats need to pay   datasets and the number of parameters of LLMs themselves
attention to security (e.g., Safetensors [85]) and are usually   are growing rapidly (e.g., 9.5 PB data form Common Crawl
closely tied to their respective model training frameworks [32],   [183], DeepSeek-R1 [162] has 617B parameters). A single node
[42], [22].                                                 cannot store such large-scale data, and the data needs to
                                                      be distributed across multiple nodes. The key technologies• Pickle (.pkl [13])  is a Python-specific format supported
                                                              involved mainly include (1) distributed storage systems andby almost all Python frameworks and can store any Python
                                                                 (2) heterogeneous storage systems.object, not limited to model parameters, making it convenient
for saving model states and other custom information.
                                                           Principles• Safetensors [85] was introduced by Huggingface to address
the security concerns inherent in Python’s Pickle-based serialization. While Pickle serializes both the data and behavior     Compared to traditional machine learning, the data
of Python objects—enabling arbitrary code execution dur-        (e.g., training data and model data) used in LLMs
ing deserialization—safetensors avoids this risk by focusing       including both  is growing exponentially. The main
exclusively on tensors and their associated metadata. This       challenge lies in how to efficiently store and manage
design ensures safe deserialization without the possibility of      such large-scale data. Current approaches address this
executing malicious code. Additionally, safetensors supports      through distributed and heterogeneous storage sysmemory mapping (mmap), which significantly enhances the      tems.
efficiency of model loading.
• PyTorch-specific formats (e.g., .pt, .pth [32]) are optimized  Distributed Storage Systems. Distributed storage sysfor model storage. Typically, .pth  files are used to save  tems refer to storing a large-scale datasets across multiple
training checkpoints, including model parameters, optimizer   nodes (e.g., JuiceFS [16], 3FS [15]). Traditional distributed
states, and epoch information, while .pt files are used to store    file systems (such as HDFS [79]) often come with high costs.
only the model parameters.                                 Moreover, most distributed file systems still use the POSIX
                                                              protocol when loading the training data for LLMs, which• TensorFlow offers two common saving formats [42]: (1)                                                             bring about significant software overhead.SavedModel format for saving the entire model, including
                                                            JuiceFS [16], a typical distributed file system based oncomputation graph, weights, optimizer; (2) .ckpt for storing
                                                               object storage, uses object storage (e.g., S3 [4]) as the backendmodel weights, optimizer states, and training metadata, and
                                                               to store data. Compared to traditional distributed file sys-is used to save and restore progress during training.
                                                      tems (file or block storage), distributed file systems based on
• ONNX [27] is a cross-framework deep learning model for-                                                               object storage enables simpler horizontal scaling. It does not
mat that supports interoperability across frameworks like                                                        need complex directory hierarchy (File Storage) and does not
PyTorch, TensorFlow, and Caffe2. It offers cross-platform and                                                                involve complex management logic (Block Storage), thereby
cross-framework advantages, but does not store training state                                                                     significantly reducing storage costs (approximately 20% of the
information.                                                                cost of traditional file systems).
• The Hugging Face Transformers library [22] adopts a mod-     As shown in Figure 7, 3FS [15] employs a large number
ular storage design, i.e., model weights are stored in binary   of SSDs for distributed data storage and uses the CRAQ
.bin files, model configurations are stored in .json or .txt   algorithm to ensure data consistency. Specifically, a piece of
files.                                                     data is saved as multiple same chunks, which together form
                                                     25
a Chain. For read requests, they can be sent to any chunk   a Memory-Aware Runtime Profiler for monitoring real-time
in the Chain, and the chunk will return the data. For write  memory and compute loads, partitions parameters into persisrequests, the writing operation is carried out sequentially on   tent (resident on GPU) and non-persistent (offloaded/loaded
each chunk. When a certain chunk malfunctions, instead of  on demand) chunks based on their usage patterns, and reduces
using the incremental data generated during the abnormal   redundant data copying via pre-allocated chunk buffers.
period to overwrite the data as in traditional methods, it
first moves the chunk to the end of the chain. Only when   2.4.3  Data Organization
the chunk returns to normal will the entire content of other
                                                    Data organization refers to data operations  (e.g., contentsamples be copied to the abnormal chunk. These operations,
                                                              organization in vector-based organization) during the storagewhile ensuring data consistency, will cause a certain delay in
                                                              stage that are designed to optimize retrieval accuracy andwrite operations. However, they have almost no impact on
                                                                      efficiency in RAG systems. When LLM answers questions,read operations, which are more important for LLM training.
                                                                    issues like hallucination [187] and lack of timeliness often   Meanwhile, 3FS [15] discovers that in the context of LLM                                                                         arise. To address these limitations, RAG [228] (e.g., vector-training, the File Cache significantly consumes system mem-                                                         based retrieval and graph-based retrieval) have been intro-ory, thereby degrading overall I/O performance. To address                                                           duced. They provide models with real-time, reliable contextthis, 3FS adopts an asynchronous data loading approach, dis-                                                           during inference. And both retrieval methods are based onables file caching and exclusively utilizes Direct I/O for data                                                            the relevant data organization operations (e.g., vector-basedaccess, significantly reducing memory pressure. Moreover, it                                                              organization and graph-based organization).performs system-level alignment of buffer pointers, offsets,
and lengths to satisfy Direct I/O requirements, thereby avoiding additional memory copies caused by user-side alignment      Principles
operations.
Heterogeneous Storage Systems. Heterogeneous  stor-     Compared to traditional machine learning, LLMs reage systems refers to deploying the model state across di-       quire RAG knowledge to access real-time information.
verse storage media (e.g., GPUs, CPUs, NVMes Memory).     The main challenge is how to ensure both the efficiency
When deploying the model, The Zero Redundancy Optimizer     and accuracy of retrieval. Current methods address
(ZeRO) [333] deploys model states across multiple GPUs.       this through vector-based and graph-based data orgaHowever, simply distributing the model across multiple GPUs       nization techniques. However, existing RAG systems
often significantly increases computational costs.                          still fall short of meeting the high-quality retrieval
                                                      demands at the enterprise level, where the document   Some methods  [334], [337], [336], [435] alleviate GPU
                                                                       scale can reach millions of pages.memory pressure by storing data in host memory or NVMe
SSD. vDNN [337] utilizes a per-layer memory management
approach based on a sliding window that dynamically allo-  Vector-Based  Organization  Vector-based  organization
cates memory at runtime based on the computational de-   refers to converting data into vector form for efficient retrieval.
mands of the current layer. Its memory transfer mechanism   It processes the original data through multiple stages (e.g.,
includes both static and dynamic policies: the static policy   Content Organization, Chunking, Embedding, Compression
offloads feature maps of all layers or only convolutional layers,  and Storage).
while the dynamic policy determines which layers and con-   (1) Content Organization. For the source data, organizing the
volutional algorithms to offload at runtime, balancing train-   content can enhance its logical structure, thereby facilitating
ability and performance based on network characteristics.  improved efficiency and accuracy in  retrieval. Works  like
vDNN fully utilizes CPU memory by offloading intermediate  Dense x retrieval [97], APS [172] refine text into independent
feature maps that are not immediately needed and prefetching   semantic units, which could be described as the minimal
them prior to backpropagation. ZeRO-Infinity [334] offloads   sentence that include all the necessary context information
model states to CPU (e.g. activations) and NVMe memory,  from the original text to express its meanings, and Thread [57]
effectively alleviating the GPU memory bottleneck. To fur-   reorganizes documents into logical units, with each unit conther reduce memory pressure, it introduces a memory-centric   taining prerequisites, headers, body content, linkers (describtiling technique that lowers the working memory requirements   ing possible paths for next step), and metadata, enabling
for LLM training, enabling the execution of large operators   a logical and structured representation of the document’s
without relying on model parallelism.                           content, which significantly enhances the system’s logical coHowever, both vDNN and ZeRO-Infinity only  utilize   herence and processing efficiency especially in complex tasks
CPU’s memory without leveraging its computational capa-   (e.g., troubleshooting and dynamic operational workflows).
bilities. In contrast, ZeRO-Offload [336] retains the parame-       Similarly, [89] organizes the content of scientific papers
ters and forward/backward computations on the GPU while   into a hierarchical tree structure, where the root node of
offloading the remaining computations (such as optimizer   the tree  is the paper’s  title and child nodes are different
calculations) to the CPU, thereby harnessing the CPU’s com-   sections, such as the introduction and methods. The relationputational power.                                             ship between parent and child nodes represents the globalUnlike the aforementioned methods that often rely on   local content relationships, such as the connection between
manual parameter tuning (e.g., specifying offloading targets   the abstract and introduction. Then it traverses the paths
like CPU or NVMe), ProTrain [435] introduces a model-  from the root node to the leaf nodes to extract important
and hardware-aware automated framework. It incorporates   contextual information.
                                                     26
(2) Chunking. In vector-based retrieval, embedding long texts     LeanVec [380] combines linear dimensionality reduction
may reduce retrieval efficiency. Thus, an effective chunking   with LVQ for vector compression. In ID(In-distribution) scestrategy  is required to divide the text into appropriately   narios, LeanVec uses PCA, while in OOD(Out-of-distribution)
sized segments for encoding. The optimal chunk length needs   scenarios,  it  introduces  the LeanVec-OOD  optimization
to balance retaining fine-grained semantics and maintaining  method, which minimizes the square of the inner product
sufficient context, since a too long text might suffer from   between the query vector and the representation error to find
significant semantic compression during embedding, while too   the optimal projection subspace for both the dataset and the
short a text would increase processing costs.                  query set, thereby reducing the vector dimension. However,
   Allowing overlap between consecutive chunks ensures that  LeanVec is a simple linear dimensionality reduction method,
important information at the boundaries is not lost and the  and its performance may be affected in terms of accuracy
continuity of context is maintained. Different from traditional  when reducing the dimensionality drastically.
chunking, MoG [480] adopts a dynamic chunking strategy,      LeanVec-Sphering [381] modifies the loss function, transwhich chunks data when building the knowledge base, where   forming the problem of finding the projection matrix into an
MoG dynamically determines the optimal granularity (e.g.,   optimization problem under the Mahalanobis distance, which
sentence-level, paragraph-level, or section-level) of the knowl-   allows for more effective discovery of the optimal projection
edge source based on the input query through a trained router.   matrix, thereby better preserving the similarity structure
The router, implemented as an MLP, assigns weights to   between vectors when processing high-dimensional vectors.
different granularities to guide snippet selection. MoGG [480]   • Non-linear Dimensionality Reduction. GleanVec [381]
extends MPG by converting reference documents into graphs   uses spherical k-means clustering in the data partitioning
and redefining granularity as hopping ranges, enabling effec-   stage to group vectors based on direction, capturing the
tive retrieval of dispersed information for complex queries.      data’s structural features. By associating cluster labels with
                                                                   vectors, it narrows the search range and reduces unnecessary(3) Embedding. In vector-based retrieval, the original input
                                                                 calculations during inner product computation. In the local(text, images, audio, or other domains) is transformed into
                                                                    linear dimensionality reduction stage, GleanVec applies thedense vector representations using models specifically adLeanVec-Sphering method to reduce dimensionality withinjusted for each data type. These representations encapsulate
                                                          each cluster, preserving the inner-product relationship, whichthe underlying semantic meaning of the original content, and
                                                                     simplifies calculations while maintaining accuracy.are then stored in a vector database for storage and retrieval.
                                                                 (5) Storage. After the above steps, the data will be stored inVarious embedding models are used to correctly encode sevector form in a vector database. During LLM inference, themantic information:
                                                     model vectorizes the input and uses similarity metrics such as• BGE uses a bilingual joint training framework that com-                                                                cosine similarity or dot product to retrieve the most relevantbines language-specific subword tokenization and specialized                                                         data from the database.adaptation layers. This design aligns semantic representa-                                                                     Faiss [125], when storing vectors, relies on the chosentions across languages, improving cross-lingual retrieval ac-                                                           index type. The Flat Index stores all vectors directly, suchcuracy [94].                                                              as IndexFlatCodes, which stores vectors in a flat array and• STELLA features a cross-instance attention aggregation                                                           supports sequential IDs. It is ideal for small datasets withmechanism that explicitly captures inter-sentence dependen-                                                                high-precision requirements. The IVF Index clusters vectorscies during pretraining. Besides the general embedding model,                                                         with a coarse quantizer and stores them in inverted lists, sup-STELLA offers an extra dialogue model in incomplete query                                                             porting user ID operations and optionally using a DirectMapsituations where the user input has problems such as semantic                                                                      for efficient access. This reduces the search range and speedsomission and reference digestion. This reduces the embedding                                                  up retrieval, making it suitable for large datasets. The PQdimensions and inference latency, making it especially effec-                                                         Index compresses vectors by splitting them into sub-vectorstive for large-scale tasks [24].                                                    and quantizing them with a k-means quantizer (e.g., PQ6x10),
• GTE introduces a dual-negative sampling strategy within                                                             trading accuracy for reduced storage space, making it suitable
its contrastive learning paradigm. Though introducing nega-                                                                      for high storage demands and lower precision needs.
tive samples usually works in series of embedding models, this                                                                In the Milvus [26], vector storage differs based on the
strategy incorporates more reverse contrastive terms within a                                                  number of vectors per entity. For single-vector entities, vectors
fixed batch, strengthening the model’s ability to distinguish                                                              are stored continuously without row IDs. Since vectors are
subtle semantic differences. [249].                                                              sorted by row ID and have the same length, a vector can be
(4) Compression. Vector retrieval in LLMs differs from regu-   directly accessed using its row ID, reducing storage overhead
lar vector retrieval in that semantically similar vectors are of-  and improving query access efficiency. For multi-vector entiten high-dimensional, so dimensionality reduction techniques    ties, vectors are stored in a columnar format. For example, for
are needed to reduce storage pressure.                             entities A and B, each with two vectors, the storage format
• Linear Dimensionality Reduction. Locally-adaptive    is (A.v1, B.v1, A.v2, B.v2). This columnar storage enables
Vector Quantization (LVQ)  [50] centralizes the data and  more efficient data processing by vector dimension, facilitating
scales each vector individually, calculating the quantization   batch operations and improving processing performance.
bounds adaptively in a localized manner, fully utilizing the      Weaviate [34]  utilizes a graph data model to manage
quantization range to compress the vectors. This method is   data entities, storing vectors as node attributes linked to
typically suitable for compressing vectors with around 100   these entities. For example, in the case of text data, vectors
dimensions, but it performs poorly when the vector dimension   generated by a text embedding model are associated with
is very large, such as tens of thousands.                          their corresponding text entity nodes, enabling efficient graph
                                                     27
traversal and multi-hop queries based on vector similarity.   contain attributes (key-value pairs). This model uses query
Additionally, Weaviate can store vectors alongside structured   languages like Cypher and GSQL, designed for relationship
attributes. For instance, the vectors of e-commerce products,   modeling and querying, making them highly suitable for
along with structured attributes such as price and category,  complex relationship queries during RAG in LLMs.
are stored in the corresponding entity nodes. This allows for     Amazon Neptune [65] supports both property graph modhybrid queries that combine vector similarity and structured   els and RDF models for graph-based data storage. The RDF
attribute conditions, enhancing query flexibility and practi-   model, based on triples (subject, predicate, object), represents
cality.                                                                  entities, attributes, and relationships in a way that enhances
   LanceDB [25] uses a columnar storage format called Lance   knowledge reasoning. By combining these two models, Nepto store data. Compared to traditional Parquet formats,   tune can meet diverse knowledge storage needs, such as rapid
Lance introduces the concept of a table schema. A single   queries and deep reasoning.
row in LanceDB can store images, text, audio, video, and     ArangoDB [1] uses a multi-model approach to store graphany number of vectors corresponding to different parts of the   based data. It supports multiple data models (e.g., document,
original data, and it can be dynamically updated. This makes   key-value pair, graph), allowing the selection of appropriate
LanceDB particularly suitable for storing multi-modal data.   storage and query methods depending on the requirements.
Currently, LanceDB is used for handling various RAG tasks.   This allows ArangoDB to store graph data (relationship inGraph-Based Organization. Unlike vector-based organi-   formation), document data (context or factual information),
zation, which helps LLM find knowledge related to a user’s  and key-value pairs (configuration or metadata) in the same
query through fuzzy searching, graph-based data explicitly   database,  facilitating LLMs to extract relationships from
represents entities and their relationships, enabling the iden-   knowledge graphs while also retrieving document-type data
tification of precise matching information in the database.   (e.g., specific context information).
We will introduce graph-based organization from two aspects:
indexing and storage.                                             2.4.4  Data Movement
(1) Indexing. In the indexing phase, it is necessary to establish  Data movement refers to the process of moving data from
an efficient indexing architecture to address the issue that   storage nodes to computing nodes. This process can achieve
directly retrieving raw triples is inefficient for complex queries   high data movement performance by caching data. Meansuch as multi-hop reasoning or path search, because the inher-   while, offloading data and operators to multiple nodes for
ent sparsity in the graph structure often leads to significant   computation can improve the speed of data preprocessing.
query latency.                                                  Additionally, the highest overall performance can be achieved
  GraphRAG [127] adopts community clustering and hierar-  by overlapping data storage and computation operations to
chical summarization strategies. It uses the Leiden algorithm   jointly schedule storage and computing resources.
to detect tightly connected subgraphs, called communities,
in the knowledge graph. Then, it generates hierarchical sum-      Principles
maries for each community. Once a certain element in a triple
is retrieved, the index collects relevant community summaries                                                    Compared to traditional machine learning, LLMs inand sends them for inference. For example, it can condense                                                                  volve massive data transfers from storage nodes to
hundreds of triples related to ”quantum mechanics” into a                                                       compute nodes. The main challenge is how to accelsemantic summary: ”Quantum mechanics is the fundamental                                                                    erate the data moving rate. Current methods address
theory describing the behavior of matter and energy at micro-                                                                         this through data caching, compute-storage overlap,
scopic scales”.                                                       and data/operator offloading.   Furthermore, LightRAG  [164] integrates deduplication
functionality to identify and merge identical entities and
relations from different paragraphs. In real-time update sce-  Caching Data in advance can increase the data moving rate.
narios, LightRAG introduces the Delta Index mechanism,   However, if a fixed cache policy is used, in order to meet the
which builds local indexes only for newly inserted edges and  IO requirements of training, the configured storage capacity
entities, using background merging threads without the need   often far exceeds that required for storing the dataset [469].
for community reconstruction, significantly reducing overhead   Therefore, a dynamically adjustable cache policy is needed.
related to community detection compared to GraphRAG.     Some methods [219], [161], [469] dynamically adjust the cache
  MiniRAG [136] proposes a semantic-aware heterogeneous  mechanism by analyzing the characteristics and requirements
graph indexing mechanism,  integrating  text chunks and   of LLM jobs in real time.
named entities into a unified structure, reducing the reliance      Quiver [219] optimizes cache sharing strategies based on
on large language models for complex semantic understand-   the following IO characters during model training: (1) data
ing. The low semantic calculating requirement while deploying   shareability (due to significant overlap in data access within
grants MiniRAG a more excellent performance on resource-  and across jobs), (2) substitutability (the I/O order does
constrained devices compared to other methods.              not affect job correctness, enabling small caches to improve
(2) Storage. Graph data is usually stored in graph databases   performance by substituting data and reducing thrashing),
in three models: property graph models [292], RDF (Resource  and (3) predictability (using mini-batch processing times to
Description Framework) models [65], and multi-model [1].      estimate job sensitivity to I/O performance for informed cache
   Neo4j, JanusGraph, and TigerGraph use property graph   allocation).
models [292] to store graph-based data. A property graph      Fluid [161] dynamically adjusts cache capacity according
model  consists  of ”nodes” and ”edges,” where both can   to I/O conditions, optimizing the online training speed for
                                                     28
each individual LLM job. Specifically, Fluid uses a coordina-  and AutoOrder, to alleviate input data preprocessing bottletor to monitor the processes of LLM jobs. It calculates the   necks and reduce training costs. The AutoPlacement strategy
number of samples within a specific time window based on   dynamically schedules data preprocessing workers across ML
the batch sizes fed back by the jobs, and thus obtains the real-   accelerator hosts and remote CPU servers. It  first estabtime training speed. Subsequently, based on the concept of   lishes a baseline batch processing time for model training,
the TCP congestion control algorithm [315], it adopts a trial-   incrementally adds local workers, and then prunes redundant
and-error approach to dynamically adjust the cache capacity.   remote workers to determine the optimal combination of local
When the training speed increases, the cache capacity  is  and remote resources. The AutoOrder strategy analyzes the
increased according to the preset scaling-up factor and scaling   transformation operations within the input data pipeline,
step. Conversely, when the training speed decreases, the cache   reordering them to place data-reducing transformations (such
capacity is decreased according to the preset scaling-down   as sampling, filtering, or image cropping) earlier and datafactor and scaling step.                                    expanding ones (such as image padding and one-hot encoding)
   Meta proposes Tectonic-Shift [469], a hybrid storage ar-   later. While adhering to user-specified ordering constraints,
chitecture that integrates flash memory with the traditional   this reorganization improves the preprocessing throughput of
HDD-based distributed file system Tectonic. Tectonic-Shift   individual workers.
organizes data segments into buckets for storage in flash       Different from the works that are only compatible with a
memory and determines segment admission and reinsertion by   single training framework as mentioned above (e.g., Cachew
comparing bucket priorities (computed from both historical  and tf.data service can only work with TensorFlow). Powered
and predicted future access patterns) against dynamically  by native composable operators (e.g., data loading, transadjusted thresholds. It also optimizes the segment size (e.g.,   formation, and filtering functions), Cedar [468] can flexibly
256 KB) of CacheLib [9] to improve flash memory utilization.   support different ML frameworks and libraries, enabling users
                                                               to effortlessly build data pipelines.Data/Operator Offloading refers to offloading data preprocessing operations such as shuffling, sampling, and aug-  Overlapping of storage and computing means that the
mentation, to multiple devices in order to improve processing   data loading and computation processes in LLM training
speed. Currently, data preprocessing pipelines (e.g., tf.data)   alternate. In LLM training, which proceeds in data batches,
are typically performed on the CPU, whose efficiency is often   ideally the data loading unit can prepare the next batch while
lower than the training speed achieved by Machine Learn-   the computing unit processes the current one, reducing overall
ing (ML) accelerators like GPUs and TPUs. So enhancing   training time. However, if a data isn’t cached locally, its need
the efficiency of data preprocessing to match the high-speed   to load the data through remote I/O bandwidth. When this
processing capabilities of ML accelerators has become a chal-  bandwidth is insufficient, computation pauses to wait for data
lenge [159].                                                     loading, creating an IO bottleneck. Some researches optimize
                                                            the pipeline at different training stages (e.g., the pre-training   Some research [158], [67] offload data preprocessing tasks
                                                    and SFT stage [466], the RL stage [479]).to remote CPU servers. Cachew [158] divides the input dataset
of each job into independent subsets for processing by re-      SiloD [466] leverages the characteristics of the pipelined
mote CPU nodes. Additionally, users can specify locations for   execution of data loading and computation at the pre-training
caching and reusing data in the input pipeline. The scheduler  and SFT stage to build an enhanced performance evaluator.
makes decisions during runtime based on specific metrics and  When data loading becomes the bottleneck, it uses a learned
algorithms through automatic scaling and caching strategies.  model (IOPerf) to quantify the cache and remote I/O deThe automatic scaling strategy adjusts the number of worker  mands of different training jobs,providing support for resource
nodes according to client-reported metrics. The automatic   allocation in the pipelined of data loading and computation.
caching strategy compares the processing times of different     Compared with the pre-training and SFT stages, the RL
cache locations and selects the optimal caching scheme. The   stage requires an additional training of the reward model
tf.data service [67] addresses input data bottlenecks by hori-   to evaluate the output of the original model. This leads
zontally scaling CPU nodes and leveraging a coordinated read   to a greater amount of computational resources remaining
mechanism to mitigate straggler issues caused by input size   idle (pipeline bubbles) during the RL stage. RLHFuse [479]
variability in distributed training. Specifically, it is comprised   takes advantage of the independence between the original and
of four key components: a dispatcher, a pool of workers,   reward models during the training stage to break the training
clients, and an orchestrator. The dispatcher manages dataset   task into sub-tasks of micro-batches. In the case of differences
assignment to workers using various sharding strategies, for   in the sizes and parallel strategies of the two models, it first
example, the OFF strategy performs no sharding, the DY-   transforms the problem to ensure that each stage of the two
NAMIC strategy applies disjoint first-come-first-served shard-  models uses the same number of GPU resources, and then
ing, and several static sharding strategies are also supported.   uses the simulated annealing algorithm [213] to generate a
Workers are responsible for actual data processing. Clients   fused pipeline schedule.
issue data processing requests to the workers. Orchestrator
deploys the aforementioned three components as containers
within the same Borg [384] unit.                                  2.4.5  Data Fault Tolerance
   Although the above method of offloading to remote CPU  Data fault tolerance refers to the ability to quickly resume
servers can alleviate data stalls, the cost of remote CPUs is  from the point of interruption during model training by
high, and the resources of ML accelerator nodes are not fully   storing checkpoints or performing redundant computations in
utilized. Pecan [159] introduces two strategies, AutoPlacement   the event of training interruptions.
                                                     29
                                                            the number of machines and checkpoint replicas, it flexibly   Principles                                                          adopts group placement or ring placement to maximize the
                                                                  likelihood of recovery from CPU memory in the event of
   Compared to  traditional machine  learning, LLMs                                                                         failures. ByteCheckpoint [389] manages checkpoint files using
    place greater emphasis on fault tolerance during train-                                                     an architecture combining SSD and HDD storage servers.
    ing due to their large model sizes and the high cost                                            New checkpoint files are stored as ”hot” data on SSDs for
    of retraining. The main challenge is how to quickly                                                            quick access due to evaluation task downloads after creation.
   resume normal training in the event of an interruption.                                                  Once the evaluation is completed and there are no training
   Current methods address this by saving checkpoints or                                                             anomalies, their access frequency drops, and they become
    using redundant computation.                                                             ”cold” data, being migrated to HDDs to free up SSD space
                                                    and ensure the hot storage can efficiently store currently
Checkpoints. Some methods store the model state as check-   frequently accessed checkpoint files.
points to handle training interruptions. However, restoring  Redundant Computations Unlike checkpoint, some methmodel states across multiple platforms or frameworks may   ods [382], [186], [147] are based on parallel computing and
encounter compatibility issues. At the same time, frequently   redundantly compute the state data of the model, enabling
saving model checkpoints can consume a large amount of   quick recovery of the training state from non-failed nodes in
storage space, especially during large-scale model training.      case of failures.
   For compatibility issues, PaddleNLP [29] has developed      Inspired by the RAID disk redundancy technology [307],
a unified model storage technology. It stores model weights,  Bamboo [382] enables each computing node to perform comoptimizer weights, and other data in a unified safetensors for-   putations not only on the neural network layers it is responmat, eliminating the need to differentiate distributed strate-   sible for, but also on some layers of its neighboring nodes
gies during checkpoint storage. Specifically, when the dis-   as redundant computations. When a node is preempted, its
tributed training strategy changes (e.g., switching between   predecessor node has all the information required for training,
data parallelism and model parallelism) or the number of   allowing the training to continue without wasting previous
machines  is adjusted, Unified Checkpoint enables training   computational results.
to resume using only a single complete checkpoint, without      Unlike Bamboo’s node-based redundant computation,
requiring separate checkpoints for each configuration.         Oobleck  [186] uses  pipeline templates to  define  training
(1) Asynchronous Storage. Apart from standardized check-   pipeline execution, specifying node allocation, stage numpoint  storage,  for  frequently  saving  model,  some  re-   bers, and model layer-GPU mappings. During training, at
searches  [291],  [194] aim to accelerate checkpoint saving   least f + 1 logically-equivalent yet physically-heterogeneous
through asynchronous storage without affecting the model’s   pipelines are instantiated from these templates, considering
training speed.                                              the fault tolerance threshold f and batch size. When a pipeline
   CheckFreq [291] employs a two-stage checkpointing tech-  node  fails, Oobleck leverages other pipelines’ model state
nique designed to capture model state copies in memory  redundancy and reinstantiates the pipeline to resume training.
for asynchronous storage while ensuring model parameter      Unlike Bamboo and Oobleck, which use pre-set redundant
consistency through pipelining with subsequent iteration com-   computations in standby, ReCycle [147] leverages the compuputations. Specifically, when idle GPU memory is available, it   tational redundancy inherent in parallel training to reassign
prioritizes snapshotting on the GPU to reduce costs; other-   the tasks of failed nodes to nodes with the same processing
wise, it stores checkpoints in CPU memory and adjusts the   in other data-parallel groups. This unique approach enables
checkpoint frequency accordingly.                             quick resumption of training without the need  for spare
   In the training of LLMs on the MegaScale system [194],   servers.
HDFS is used to store the model state. When storing model
states, there are problems of balancing the checkpoint fre-   2.4.6 KV Cache
quency and dealing with the HDFS bandwidth bottleneck dur-  LLMs use auto-regressive generation, where each token deing model recovery in the training process. To address this,  pends on prior ones. KV Cache avoids redundant computation
MegaScale adopts a two-phase storage approach: (1) GPU  by reusing stored key-value pairs, improving efficiency. Howworker nodes quickly write the on-chip state to the host   ever, its memory grows with sequence length, making efficient
memory and continue training; (2) a background process asyn-   cache management crucial.
chronously transfers the state to HDFS to reduce interference
with training. When resuming training, a worker node in the                                                           Principles
specified data parallel group reads the shared state partition
and broadcasts it to other nodes, reducing the HDFS load and                                                    Compared to traditional machine learning, LLMs re-alleviating bandwidth pressure.                                                                   quire KV cache to accelerate inference. The main(2) Hierarchical Management refers to storing model check-                                                                   challenge lies in efficiently managing the cache as thepoints across a multi-level storage system, storing the check-                                       KV size grows rapidly. Current methods address thispoints that may be needed in the closer storage nodes, aiming                                                        by indexing KV, shrinking KV, and managing KVto improve recovery speed. Gemini [403] stores checkpoints                                                            placement or cache space.in a hierarchical storage system composed of local CPU
memory, remote CPU memory, and remote persistent storage.
It introduces a near-optimal checkpoint placement strategy  Cache Space Management refers to separating the logical
for CPU memory. By analyzing the relationship between   structure of the KV cache from its physical storage imple30
mentation, which facilitates memory allocation and improves   identical prefixes together, further enhancing cache reuse.
memory utilization. vLLM [220] and vTensor [428] divide
the KV cache into fixed-size blocks and store them in a   2.5  Data Serving for LLM
non-contiguous manner. vLLM manages these blocks through                                                    Data service encompasses data preprocessing operations cara mapping mechanism, while vTensor stores the fixed-size                                                                   ried out after data is transferred from storage to computing
KV cache blocks non-contiguously in physical memory. This                                                        nodes and before its actual utilization by the LLM, aiming
decouples the logical and physical KV blocks, utilizing a block                                                               to facilitate more effective data consumption by the LLM.
table to manage dynamic memory allocation by tracking the                                                      These data preprocessing operations include: data shuffling,
mapping relationships and fill states.                                                         data compression, data packing, and data provenance.
KV Placement refers to using a perception strategy to store
frequently used KV in faster storage media (such as GPU   2.5.1  Data Shuffling
memory), while storing less frequently used KV in slower  Data shuffling in data serving means that different data needs
storage media (such as SSD), or releasing them directly.   to be selected and provided to LLMs at various stages (e.g., in
RAGCache [197] provides a prefix-aware PGDSF replacement   different epochs for pretraining). For example, corresponding
policy that prioritizes cache nodes based on access frequency,   training data needs to be supplied according to the training
size, and recomputation cost. And stores frequently accessed   requirements during the training stage; during the RAG stage,
data in fast GPU memory and less frequent data in slower host   corresponding knowledge needs to be supplied based on the
memory, maximizing cache efficiency. CachedAttention [148]   degree of relevance to the questions.
leverages the inference job scheduler to observe the jobs
waiting for execution. To improve cache efficiency, the KV      Principles
cache of a pending job is prefetched into the host memory
from disk before execution. Meanwhile, KV caches that are                                                    Compared to traditional machine learning, LLM apno longer required are evicted, based on the jobs waiting to be                                                                       plications are divided into multiple stages, each requirexecuted.                                                                  ing different types of data to be fed into the model.
KV Shrinking KV Cache Shrinking refers to trimming or     The main challenge is how to select data that meets
reducing the KV Cache in order to lower memory usage      the specific requirements of LLMs. In the training
and improve inference efficiency. CacheGen [265] uses a cus-       stage, current methods provide training data by scortomized tensor encoder to encode the KV cache into a more       ing based on data samples or model states, or by using
efficient bitstream, thereby reducing bandwidth usage. It also       empirical training strategies. In the RAG stage, data
compresses the KV cache using techniques such as block-based         is selected through metrics, rules, or models to supply
encoding, hierarchical quantization, and arithmetic encoding,       relevant knowledge to the LLM.
while dynamically adjusting the compression level and transmission method based on network conditions to ensure low                                             Data  Shuffling  for  Training. As LLMs continuouslylatency and high generation quality.                                                              trained over new tasks, it may begin to lose its ability to retain
   Unlike CacheGen, which only considers intra-layer redun-                                                                 early task knowledge, a phenomenon known as catastrophic
dancy, MiniCache [255] is based on the similarity of KV cache                                                                 forgetting [287], [286]. To address this, some data supply
states in adjacent layers. It decomposes the state vectors into                                                     methods are employed to manage datasets during the trainmagnitude and direction components, calculates the direction                                                              ing process and provide high-quality data. Meanwhile, some
vectors using SLERP [354], and merges the KV caches of adja-                                                        methods, instead of altering the dataset, propose reasonable
cent layers to form a merged cache that contains information                                                               learning strategies.
such as direction vectors, magnitudes, and angles.                                                                 (1) Data Pruning. Data pruning refers that during the trainCompared with the traditional method of storing the com-                                                              ing process, partial shuffling is carried out on the training
plete KV data, HCache [150] only stores the hidden states (the                                                                dataset, and high-quality data is retained, so that the model
size of the hidden states is only half that of the KV cache, and                                                                                   is trained on the data that has not been fully learned and is of
recomputing the KV cache from the hidden states can reduce                                                           high quality.
the computational load). When restoring the state, a bubble-  Sample Scoring. Some methods [137], [66] prune datasets by
free restoration scheduler is used to concurrently execute the                                                               scoring samples, selecting high-scoring samples for subsequent
transmission of hidden states and the recomputation from                                                                   training. [137] applies the EL2N metric to identify important
hidden states, maximizing the overall resource utilization.                                                        examples in a dataset, written as χ(xi, yi) = E∥f(xi) −yi∥2,
KV Indexing refers to the process of constructing an in-  where f(xi)  is the model’s prediction and yi  is the true
dexing architecture for the KV Cache to accelerate the query   sample. Based on the computed EL2N values,  it periodprocess of the KV Cache. ChunkAttention [440] organizes the   ically prunes irrelevant data during training. [66] extends
KV cache into a prefix tree using a prefix-aware KV cache   the EL2N metric to evaluate sample importance, written as
(PAKV), sharing key-value tensors of common prefixes to ac-   ˆχema(x, y) ←α · ˆχnlu(x, y) + (1 −α) · ˆχema(x, y), where α is
celerate the corresponding KV query process.  [478] proposes   a smoothing parameter. Based on extended EL2N values, it
Prefix Sharing Maximization (PSM): By dynamically reorder-   periodically selects data subsets for training.
ing data columns and rows, it maximizes prefix sharing among  Model State Scoring. Unlike the aforementioned approach
requests to improve cache hit rates. Column Reordering sorts   of scoring samples and prune the dataset, some methods [372],
columns based on value frequency and size, prioritizing those   [56], [416], [276] prune the distribution of dataset by scoring
with more shared prefixes. Row Sorting groups requests with   the model’s state (such as training loss and learning status).
                                                     31
   Moving-one-Sample-out (MoSo) [372] identifies and selects   to filtering out documents with poor relevance after retrieval.
the most informative LLM pre-training samples by assessing  Some methods [280], [114], [87] use a model as a judge to
the influence of a specific sample on the training loss. The    filter documents. [280] uses small language models (SLMs)
MoSo score measures how the training loss over the dataset   as filters, performing preliminary predictions and evaluating
S excluding z  (i.e., S \ z) would change when the sample   difficulty. For easy samples, the SLM’s predictions are used
z  is removed. This approximation measures the agreement   as the final decision; for difficult samples, the top N most
between z and S \z, where the sample is considered important   likely labels are selected from the SLM’s predictions for suband receives a higher score if the gradient of z is consistently   sequent re-ranking. In Chatlaw [114], after retrieving relevant
aligned with the average gradient.                             information, the LLM evaluates the retrieved content. Only
    Similarly, Velocitune [276] is a dynamic domain weight   content that is deemed highly relevant after evaluation is used
adjustment method based on learning velocity, which is de-   to generate the final response, effectively reducing interference
fined as Vt[i] = ℓinit[i]−ℓtarget[i]ℓt[i]−ℓtarget[i]  , where Vt[i] denotes the learning  from irrelevant or incorrect information. MAIN-RAG [87]
                                                                 collaboratively filters and scores retrieved documents by lever-velocity for domain i at step t, ℓt[i] is the current loss for
                                                            aging multiple LLM agents to enhance relevance and reducedomain i, ℓtarget[i] is the target loss for domain i, predicted
                                                                    noise. The framework adopts a dynamic filtering mechanismby the scaling law [201], ℓinit[i] is the initial loss for domain
                                                             that uses score distributions to adjust relevance thresholds,i, calculated before training starts. The method calculates
                                                            ensuring high recall of relevant documents while minimizingthe learning velocity of each domain and dynamically adjusts
                                                          computational overhead.the sampling weights, giving more attention to domains with
slower learning progress, thereby achieving a balanced learn-   (2) RAG Knowledge Re-ranking. After filtering, multiple docing effect.                                             uments may remain, requiring re-ranking of the retrieval
   Some methods [56], [416] combine reinforcement learning   results to place the most relevant ones at the top for more
based on scoring the model to adjust the dataset. ODM [56]   accurate model output. Research on [128] shows that using
is based on the multi-armed bandit algorithm. It regards   a large model for re-ranking performs better than methods
each data domain as an arm and uses classical reinforcement   like Maximum Marginal Relevance (MMR) and Cohere relearning methods. By taking the training loss as the reward   ranking. For large model re-ranking, general-purpose large
function, it optimizes the data mixing ratio online to adapt to   language models (e.g., GPT) can be used directly, or specialtraining dynamics. That is, it dynamically adjusts the sam-   ized zero-shot re-ranking models such as Cohere rerank [12] or
pling weights of each data domain and preferentially selects  RankVicuna [318] can be employed. The latest ASRank [47]
data with high information gain and large losses.                leverages pre-trained LLM to compute the matching probability between document answers and answer cues, scoring  MOS [416] proposes a scoring network that dynamically
                                                    and re-ranking the retrieved documents.adjusts the sampling probabilities of different datasets based
on the model’s current learning state, combined with reinforcement learning, to alter the distribution of training   2.5.2  Data Compression
data. This adjustment is guided by three reward functions:
(i) Transferability for measuring the similarity (e.g, cosine  Data compression refers to compressing the input data for the
distance) between datasets as the reward. (ii) Learning dif-   model. Previous studies have shown that prompts are crucial
ficulty for measuring the perplexity changes. (iii) Learning   for triggering LLM domain-specific knowledge, and prompts
trajectory for smoothing the reward values using Exponential   are typically designed based on specific tasks (including chainMoving Average (EMA) to more stably optimize the sampling   of-thought, context learning, and historical dialogues). As
distribution.                                                the complexity of chain-of-thought, context learning, and
                                     RAG increase, longer prompts are required [189]. However,(2) Training Strategy.  In  addition  to  directly prune  the
                                                                overly long prompts may lead to higher response latency,dataset during training, appropriate learning strategies can
                                                              increased costs, and even exceeding the maximum token limit.also alleviate catastrophic forgetting.  [123] found that difExisting methods mainly compress the model inputs in twoferent  abilities vary with data volume, with mixed data
                                                                 aspects. Some methods [427], [101], [348], [200], [335] compressimproving abilities at low resources and causing conflicts at
                                                            the retrieved results in the RAG stage and then put themhigh resources. Thus, DMT [210] is proposed, which first fineinto the prompt, while other methods compress the entiretunes on a specific dataset and then fine-tunes on mixed data
                                                    prompt [189], [190], [303], [293], [102].to effectively balance general and specialized abilities and
mitigate conflicts and forgetting. It proposes a strategy where
training data are sorted based on criteria like input length,      Principles
attention weights and training loss, allowing the model to
gradually learn from simple tasks to more complex ones.                                                    Compared to traditional machine learning, LLMs ofData Selection for RAG. In the RAG stage, it is neces-      ten require longer inputs, and in some cases, the input
sary to retrieve the stored knowledge (see details in 2.4.3)     must be compressed to fit into the model. The main
and provided the retrieved results to the LLM. During this       challenge is how to compress the input without losprocess, it needs to ensure the effectiveness of the retrieved       ing important information. Current methods mainly
results in order to obtain better answers from the LLM [280].      achieve this through compression based on informaCurrently, the retrieval quality is mainly guaranteed through       tion entropy, rule-based templates, or model-driven
RAG knowledge filtering and RAG knowledge re-ranking.          approaches.
(1) RAG Knowledge Filtering. RAG knowledge filtering refers
                                                     32
RAG Knowledge Compression The retrieved RAG knowl-   2.5.3  Data Packing
edge can be compressed by a model to make small texts                                                    Data Packing aims to address the requirement for uniform
carry more information. Techniques  like RECOMP  [427],                                                          sequence lengths in LLMs’ training inputs, which combinesCompAct [348], and FAVICOMP [200] adopt rule-based RAG                                                              short texts in an appropriate way to enhance text coherence
context compression schemes, where predefined rules or tem-                                                    and reduce the number of padding tokens. In this way, we
plates explicitly guide the model to extract key information                                                        can avoid the excessive truncation caused by the drawbacks of
and remove redundant content. Alternatively, methods like                                                            simple concatenation and splitting methods [116].
xRAG [101] and COCOM [335] use soft prompt-based RAG
                                                  Short Sequence Insertion. Some methods [116], [259] in-context compression schemes, where learnable parameters
                                                               volve inserting short sequences into long sequences to min-(such as the modality projector W in xRAG or the overall
                                                             imize padding. The Best-fit Packing [116]  first splits longmodel training in COCOM) enable implicit vector learning.
                                                      documents according to the model’s context length, then sortsThese implicit vectors dynamically adjust attention weights
                                                                               all document blocks in descending order of length. For eachwhen the model processes input, allowing the model to adapdocument block, it selects the training sequence set with thetively optimize context representations under context comsmallest remaining capacity that can accommodate it. [259]pression.
                                                                      prioritizes long documents and uses a greedy algorithm to fill
                                                          remaining space with short document segments (sequences),Prompt Compression. Prompt compression means that
                                                            reducing padding and minimizing document concatenation toafter the retrieved knowledge is put into the Prompt, the
                                                             lower contextual noise.entire Prompt will be compressed.
(1) Metric-Based Compression. Some  studies  [189],  [190],                                                           Principles
based on the hypothesis that a vast amount of knowledge is
stored in the model parameters, have proposed methods to
                                                    Compared to traditional machine learning, LLMscompress prompts while minimizing information loss. LLM-                                                                  place higher demands on the semantic quality of train-Lingua [189] uses a perplexity criterion to remove redundant                                                                  ing data. Additionally, due to the requirement for uni-tokens from the original prompt. By quantifying the negative                                                          form input lengths, a key challenge is maintaining se-logarithmic probability (perplexity) of each token through                                                           mantic integrity without excessive truncation. Exist-a small model, LLMLingua identifies and removes tokens                                                                  ing techniques tackle this through short-sequence in-that can be predicted from the model’s inherent knowledge,                                                                         sertion, sequence concatenation, and semantic-awarethereby shortening the prompt while retaining essential con-                                                                composition. However, it remains crucial to accounttext.                                                                          for the impact of these data packaging operations on
   LLMLingua’s extended version, LongLLMLingua [190],       overall training efficiency.
uses a dual-granularity compression strategy:  (i) Coarsegrained compression initially filters key information at the                                                Sequence  Combination  Optimization. Some  meth-document level to provide more focused content for fine-                                                        ods [218], [316] optimize sequence combinations for efficientgrained compression; (ii) Fine-grained compression further                                                              packing. [218] proposes two  efficient sequence packing  al-optimizes at the token level to precisely retain key informa-                                                             gorithms: (1) The Shortest Pack First Histogram Packingtion. These two strategies work together to improve the qual-                                               (SPFHP) uses a sequence length histogram, sorts sequencesity of the prompt and model performance. LongLLMLingua                                                       from long to short, and applies a worst-fit algorithm toalso assigns different “compression budgets” to documents                                                                      prioritize placing the histogram intervals into the remainingbased on their importance, aiming to achieve the best global                                                                   largest “packs”, while limiting packing depth to avoid creatingcompression effect.                                                                 excessive small packs, thus improving space utilization. (2)
                                                The Non-Negative Least Squares Histogram Packing (NNL-(2) Finetuned-Model-Based Compression. Unlike the aforeSHP) converts the packing problem into a non-negative leastmentioned methods that use a small model’s perplexity for
                                                             squares problem, using dynamic programming to enumeratecompression, some methods [303], [293], [102] directly perform
                                                             reasonable sequence combination strategies, constructing athe compression task end-to-end by fine-tuning a model.
                                                          packing matrix to determine the strategy’s repetition count.LLMLingua-2 [303] defines prompt compression as a problem
                                                                          It also assigns small weights to short sequences’ residuals toof classifying tokens and trains a dedicated model for compresreduce long sequence leftovers, achieving efficient packing.sion. It uses a Transformer encoder to capture bidirectional
                                                                    [316] splits documents into multiple fixed-length “buckets”contextual information, ensuring that the compressed prompt
                                                         based on their length, ensuring that each sequence comes fromis faithful to the original. [293] proposes a technique called
                                                            the same document to avoid cross-document attention issues.’gisting’, where a language model is trained to condense the
                                                                Additionally, by combining Variable Sequence Length Cur-prompt into a compact ’gist token’. These tokens encapsulate
                                                          riculum (VSL), different lengths of sequences are dynamicallythe core semantic content of the prompt and can be cached for
                                                       sampled during training to maintain a consistent total tokenlater use. This method achieves a compression rate of up to 26
                                                              count.times.  [102] suggests a method to transform pre-trained language models into AutoCompressors. The AutoCompressor  Semantic-Based Packing. Some methods [364], [349] imcompresses long contexts into summary vectors, and training   prove data coherence through semantic-based data packing.
is performed on the model parameters using these summary   [349] reorders pretraining data by combining semantically
vectors.                                                         related documents into coherent input contexts, allowing the
                                                     33
LLM to read and reason across document boundaries. Simi-  on token information within a sliding window, and accordlarly, SPLICE [364] randomly selects a document as the root   ingly adjusts the language model’s output distribution. For
document, and in a breadth-first manner, uses retrieval meth-   detection, an LSTM-based network takes the text sequence as
ods like BM25 and Contriever (trained from a mix of Wiki and   input and identifies the watermark, leveraging shared token
CCNet data) to retrieve k similar documents, adding them  embedding parameters with the generation network.
to the training sample until the maximum length is reached.     Compared to methods that require specific keys for detecFinally, the tree structure is flattened using a specific tree   tion, [131] embeds a special type of watermark into text gentraversal strategy to generate the training example.            erated by language models, which can be detected by anyone
                                                         without the need for any secret information. It selects specific
2.5.4  Data Provenance                                             lexical combinations (rejection sampling, ensuring that the
                                                     embedding of the marker does not affect the naturalness of
Data Provenance  is the process  of tracking the sources,                                                            the text) during text generation, in conjunction with an error
transformations, and lineage of data, which is increasingly                                                                correction mechanism (error-correcting codes, allowing the
recognized critical in ensuring the reliability, transparency,                                                      marker to be recovered even after partial modification of the
and accountability of LLM data [54].                                                                     text), to embed an encrypted signature (public key signature,
                                                            ensuring the non-forgeability of the marker) into the text.
   Principles                                          During detection, one only needs to extract these specific
                                                                         lexical combinations from the text and verify the validity of the
   Compared with traditional machine-learning models,       signature to determine whether the text contains the marker.
   LLMs demand heightened safeguards for output se-      Statistical Provenance. Unlike the aforementioned methcurity owing to their powerful generative capabilities.      ods that rely on detecting special markers for tracing the
   The central challenge is to preserve output integrity       origin,  [212] achieve data provenance through the statistical
   without degrading quality. Current solutions embed      information of the vocabulary. Specifically, before generating
   watermarks or deploy statistical-detection techniques      each word, the model randomly divides the vocabulary into
    to reveal any tampering.                              two parts (green-listed and red-listed tokens) and tends to
                                                                favor the shuffling of green-listed tokens during the generation
                                                              process (green-listed tokens are a randomly selected subset ofEmbedding Markers. Current data provenance meth-                                                            the vocabulary). By employing statistical tests (a mathemati-ods [482], [105], [256], [212] generally modify the generation                                                                    cal method used to determine whether text adheres to specificlogic to embed covert markers into the text. This is done in a                                                                       rules), it is possible to detect whether the proportion of green-way that does not disrupt the text itself, thereby providing a                                                                       listed tokens in the text is abnormal, thereby ascertaining ifmedium for tracing the origin of the data.                                                            the text is machine-generated.   Bileve [482] enhances the traceability and integrity of text
by embedding two distinct levels of signals: (1) Statistical
signal embedded globally to detect whether the text origi-  3  LLM for Data Management
nates from a specific model. (2) Content-related signature
embedded within each generation unit to verify  if the text   After preparing the LLMs with carefully processed / stored /
has been tampered with. During detection, the validity of the   served data, we next introduce the LLM techniques that can
signature is first verified; if the signature is invalid, a statistical  be utilized to enhance data management tasks, including data
test is then used to determine whether the text comes from the   manipulation, data analysis, and data system optimization.
target model.
   Unlike Bileve that emphasizes strict traceability after text   3.1  LLM for Data Manipulation
tampering, [105] focuses on embedding watermarks in a way
                                   LLM can be employed to explore and prepare appropri-that preserves the quality of the generated output. It embeds
                                                               ate data for non-LLM-oriented tasks, such as data cleaninghidden markers that can only be detected by individuals
                                                                      for classification tasks, data integration for extracting well-possessing a specific key, while remaining imperceptible to
                                                              structured tables from unstructured sources, and data discov-others that the text has been altered. Specifically, the method
                                                             ery for identifying relevant datasets. Unlike data preparationemploys a pseudo-random function (PRF, used to generate
                                                                  pipelines designed specifically for LLM applications, theseseemingly random numbers) to determine the shuffling of each
                                                     methods focus on enhancing the quality and utility of dataoutput word, ensuring that the generated text is statistically
                                                                      for downstream analytical or machine learning tasks.indistinguishable from the original model’s output. During
detection, the presence of hidden markers is ascertained by
calculating a score for each word in the text (based on the   3.1.1 LLM for Data Cleaning
numbers generated by the pseudo-random function).         Data cleaning focuses on transforming corrupted or lowUnlike previous approaches, UPV  [256] introduces a wa-   quality data into a reliable form suitable for downstream
termarking method that enables detection without requiring   applications  (e.g.,  statistical analysis or training machine
access to the key used during generation, thereby eliminating   learning models). It encompasses a range of tasks such as hanthe risk of key leakage. It employs two independent neural net-   dling missing values, correcting typos, resolving formatting
works for watermarking. During text generation, the water-   inconsistencies, and addressing dependency violations. These
mark generation network utilizes an embedding module and a   tasks are typically categorized into data standardization, error
fully connected classifier to predict watermark signals based   detection and correction, and data imputation.
                                                     34
                                Data Manipulation                     main knowledge. Evaporate [63] employs LLMs to transform
                    1. Data Cleaning                                  2. Data Integration            semi-structured documents into structured views through
                Data Standardization
                                                                              Entity Matching           two main strategies: (i) Evaporate-Direct, which prompts the                     LLM-GDO   Evaporate       Prompt-based
                                                    Prompt-based   MatchGPT    BATCHER        Agent-based    CleanAgent  AutoDCWorkflow                    LLM to extract values directly, and  (ii) Evaporate-Code,
      Pipeline Generation                                  Multi-Model        COMEM                                                             Collaboration                  which guides the LLM to synthesize extraction code and en-                 Data Error Processing
                                                           Localized Multi-Task                                                           sembles multiple candidate functions using weak supervision       Prompt-based    Cocoon     Multi-News+               Fine-tuning                Jellyfish
                                                               to improve output quality while maintaining low cost.        LLM-based
     Context            Enrichment  LLMClean    LLMErrorBench                     Schema Matching                                                      (2) Agent Based Operation and Pipeline GeneraFine-tuning-based        GIDCL                  Prompt-based       LLMSchemaBench        tion. To  address  the  inefficiencies  of LLM-based  soluData Imputation                      Context-Enriched
                                              RAG        Magneto   KG-RAG4SM       tions,  such  as  the  reliance on  multi-turn prompts and
      Prompt-based    RetClean    Multi-News+
                                                         Agent-based      Agent-OM   Harmonia        expert-level prompt engineering, the second method employs
     RAG Assisted    RetClean    LLMErrorBench             Orchestration
                                   LLM agents to automatically generate cleaning operations
                                             3. Data Discovery                       and orchestrate end-to-end pipelines. For instance, CleanAData Annotation                   Data                             Profiling
                                                            CHORUS       Goby         gent [319] integrates domain-specific APIs with autonomous                      AutoDDG                               LEDD             Prompt-based      Prompt-based
       RAG-Assisted           Pneuma                    RAG-Assisted   RACOON        Birdie         agents to execute a standardization pipeline that includes
                                               API  call generation  (e.g., clean  date(df, ‘‘Admission
            Data Analysis                       Data System Optimization        Date’’, ‘‘MM/DD/YYYY’’)) and  iterative code execution.
              1. Structured Data Analysis                                  1. Configuration Tuning             Similarly, AutoDCWorkflow [237] adopts LLM agents to conRelational                     Data Analysis                                                                                            λ-Tune                                                                                  DB-GPT                                                                        LATuner                                                Prompt-based                                                                 struct pipelines for resolving duplicates and inconsistent forPACHINCO                                      DataCoder     NL2SQL                                               RAG-based
                                                                           GPTuner                                                                                        Andromeda     Multi-Step  Extractor   TAPERA  ReAcTable          Enrichment                       mats. The agent performs step-by-step reasoning to identify
      QA                                                Traning-Enhanced
    End-to-end                 TableGPT   CABINET   TabPedia                                                   Alignment         DB-GPT     E2ETune         relevant columns, evaluate data quality, and generate approQA
             Graph Data Analysis                                       2. Query Optimization             priate operations (e.g., upper() and trim()), while leveraging
    NL2GQL   NAT - NL2GQL     -NL2GQL                                                 Prompt-based        GenRewrite      LITHE        tools such as OpenRefine for execution and feedback.
    LLM-based     Semantic UniKGQA   FlexKBQA  GraphGPT      RAG-based Enrichment            R-Bot        Data Error Processing. Given a data entry, error proTraining-Enhanced                                                Improvement       LLM-QO       LLMSteer      cessing typically involves two steps: detecting erroneous val-            2. Semi-structured Data Analysis
                                                            ues                                                       and                                                                         correcting                                                                                  these                                                                                              values.                                                                                           Typical                                                                                                               errors                                                                                                               include                                                                                                                                  ty-                                                                                3. Anomaly Diagnosis   Semi-structured                 SPREADSHEET
                   BENCH      MiMoTable        Tables                                                               pos,                                                                        invalid                                                                          formats,                                                                             type                                                                                 mismatches,                                                                                           numeric                                                                                                                             outliers,                                                                                                  and                                                                            DB-GPT                                                  Prompt-based
              3. Unstructured Data Analysis            RAG-based Enrichment      D-Bot     ByteHTAP      dependency violations. Existing methods generally fall into
   Documents   UDOP     Pix2Struct   DocPedia       Multi-Agent Collaboration     Panda      D-Bot       two categories: employing LLMs for direct end-to-end error
   Programming                                      Localized Specialized     Language      RepoFusion    CoCoMIC                Fine-tuning                  D-Bot           processing, or enhancing context models to better guide the
                                                               detection and correction process.
        Fig. 8: Overview of LLM4DATA Techniques.         (1) Prompt Based End-to-End Error Processing. To
                                                          support end-to-end data error processing, the first approach
   Traditional data cleaning methods depend on rigid rules   employs prompting techniques to either directly handle data
and constraints (e.g., zip code validation), demanding sub-   errors or generate the corresponding processing functions.
stantial manual effort and domain expertise (e.g., schema   For instance, Multi-News+ [103] employs Chain-of-Thought
knowledge in financial data) [237], [432]. Additionally, they  (CoT) prompting, majority voting inspired by human annooften require domain-specific training, which restricts their   tation practices, and self-consistency checks to enhance clasgeneralizability [63]. Recent studies show that large language   sification accuracy and transparency when processing noisy
models (LLMs) can address these limitations by offering nat-   documents. Similarly, Cocoon [461] constructs semantic deural language interfaces that reduce manual and programming   tection prompts and divides datasets into batches, allowing
effort, eliminate the need for complex runtime environments,   the LLM to analyze sampled values (e.g., 1,000 entries per
and support seamless integration of domain knowledge. These  column) and identify typos or inconsistencies (e.g., “mapping
methods primarily target the following tasks.                  English” →“eng”), thereby supporting batch-wise data cleanData Standardization. Data standardization involves con-   ing. GIDCL [432] adopts a creator-critic framework in which
verting diverse, inconsistent, or non-conforming values into   the LLM iteratively refines lightweight error detection models
a consistent format to ensure reliable analysis and effective  and generates pseudo-labeled data using handcrafted prompts
downstream processing. Existing methods use either struc-  and in-context examples to produce both detection and cortured LLM prompting for specific cleaning operations or   rection functions, further enhanced by structural correlation
LLM agents for automated pipeline generation.                learning with Graph Neural Networks (GNNs).
(1) Prompt Based End-to-End Standardization. The  (2) LLM Based Cleaning Context Enrichment. To adfirst approach constructs well-structured prompts with ex-   dress the inefficiencies and limited scalability of manual cleanplicit standardization  instructions and employs advanced   ing context model construction in dynamic environments,
prompting techniques (e.g., Chain-of-Thought) to improve   the second approach leverages LLMs to enrich data cleaning
the effectiveness  of LLM-based standardization methods.   context models and more effectively capture semantic relaFor example, LLM-GDO [279] utilizes user-defined prompts   tionships within the data. For example, LLMClean [78] pro-
(UDPs), including in-context learning examples, to implement   poses an automated LLM-based method for generating conLLM-based operators that replace traditional user-defined   text models by extracting ontological functional dependencies
functions (UDFs) across various standardization tasks (e.g.,  (OFDs) using both prompt ensembling and fine-tuned LLMs
normalizing numerical values). This method simplifies logic   (e.g., Llama-2). The extracted OFDs are then used to identify
implementation and facilitates the seamless integration of do-   data errors (e.g., value inconsistencies) and guide LLM-based
                                                     35
repairs through iterative feedback from integrated correction   Furthermore, classical models (e.g., pretrained models) gentools such as Baran. LLMErrorBench [74] employs LLM   erally require large amounts of task-specific training data and
agents equipped with Python (via IPython) and prompted   tend to degrade in performance when encountering out-ofwith task-specific instructions and contextual hints (e.g., error   distribution entities [308]. In contrast, recent studies have
locations) to explore, modify, and repair datasets iteratively.  shown that LLMs possess strong semantic understanding,
Corrections (e.g., value replacement, missing data handling)   enabling them to uncover correlations across datasets and inare guided by performance feedback from pre-defined code   corporate domain-specific knowledge, thereby offering robust
execution and evaluation pipelines.                             generalization across diverse integration tasks.
(3) Fine-tuning Based End-to-End Error Processing.  Entity Matching. The goal of entity matching is to deterTo improve error correction accuracy while preserving compu-  mine whether two entries refer to the same real-world entity.
tational efficiency and model adaptability, the third approach   Existing methods leverage LLMs through well-structured
fine-tunes LLMs to capture dataset-specific patterns and  prompts and advanced reasoning mechanisms, incorporate
dependencies that are typically difficult to model through   multiple models for collaborative matching, and apply multiprompting alone. For example, GIDCL [432] fine-tunes a local   task fine-tuning to further enhance performance.
LLM (e.g., Mistral-7B) using Low-Rank Adaptation (LoRA)  (1) Prompt Based End-to-End Matching. To improve
to optimize error correction, constructing training data from  LLM’s effectiveness on matching tasks, the first approach
labeled tuples and pseudo-labeled tuples generated via LLM-   crafts well-structured prompts and integrates auxiliary mechbased augmentation, with each training instance formatted as   anisms to strengthen the robustness of the reasoning process.
a context-enriched prompt comprising: (i) an instruction (e.g.,   • Manually-Crafted Prompt. This method incorporates de-
“Correct the ProviderID to a valid numeric format”), (ii) a   tailed instructions and illustrative examples into the prompts
serialized erroneous cell with row and column context (e.g.,   to guide LLM in performing entity matching more effectively.
“<COL>ProviderID<VAL>1x1303...”), (iii) in-context learn-   For example, MatchGPT [308] evaluates the performance of
ing demonstrations (e.g., “bxrmxngham →birmingham”),  both open-source and closed-source LLMs (e.g., Llama 3.1
and (iv) retrieval-augmented examples from the same cluster  and GPT-4o mini) with  (i) different prompt designs,  (ii)
(e.g., clean tuples via k-means).                              the selection of in-context demonstrations,  (iii) automatic
Data Imputation. Given a data entry with missing attribute   generation of matching rules, and (iv) fine-tuning LLMs using
values (e.g., NULL), data imputation aims to infer the miss-   a shared pool of training data. To reduce inference costs,
ing values using available contextual information accurately.  BATCHER [134] introduces a batch prompting method that
Existing methods either (i) use structured prompts to convey   allows multiple entity pairs to be processed simultaneously.
contextual hints to LLM, or (ii) apply retrieval-augmented   It optimizes in-context learning by (i) grouping entity pairs
generation (RAG) to integrate relevant external data.           into a single prompt and (ii) applying a greedy cover-based
(1) Prompt Based End-to-End Imputation. To incorpo-   strategy to select demonstrations such that each query in the
rate contextual information for imputing missing values, the   batch is semantically close to at least one example.
first approach constructs structured prompts. For example,   • Pseudo-Code Guided Reasoning. To mitigate hallucinations
RetClean [129] enhances LLM effectiveness by serializing each   arising from over-reliance on an LLM’s internal knowledge,
tuple into a formatted representation (e.g., “[Name: John;   this method integrates external formalized representations
Age: 25; Gender: NULL]”) and pairing  it with a targeted   to enhance the robustness and reliability of the reasoning
question such as “What is the correct value for Gender?”.   process. For example, KcMF [430] guides LLMs using expertThis prompt design enables the LLM to generate accurate,   designed pseudo-code instructions structured as a sequence of
context-aware missing values.                                      if-then-else logical conditions, combined with external domain
(2) RAG Assisted Localized Imputation. To enable on-   knowledge (e.g., datasets and examples). It further adopts an
line LLMs in handling unseen, domain-specific, or private   ensemble strategy by generating outputs from different knowldatasets, the second approach adopts the retrieval-augmented   edge sources (e.g., Wikidata and domain-specific datasets)
generation (RAG) paradigm. For example, RetClean [129]  and applies a voting mechanism to aggregate results, improvintroduces a retrieval-based data cleaning framework that   ing consistency and accuracy.
indexes a data lake using both syntactic (Elasticsearch) and  (2) End-to-End Matching with Multi-Model Collabsemantic (Faiss/Qdrant) methods. It retrieves the top-k rel-   oration. To  leverage  the  strengths  of  different models
evant tuples, reranks them (e.g., using ColBERT), and then   across tasks, the second approach employs collaborative enleverages an LLM to infer missing values, while maintaining   tity matching using models of varying sizes. For example,
lineage tracking for transparency and traceability.        COMEM [400] introduces a compound entity matching framework that combines multiple strategies with LLM collabo3.1.2 LLM for Data Integration                               ration to address global consistency, which is often ignored
Data integration aims to align elements across heterogeneous   in binary matching. It employs (i) a local strategy using a
datasets to enable unified access, analysis, and knowledge ex-   medium-sized LLM (3B-11B) as a matcher or comparator
traction. For instance, it includes identifying tables or records   to rank top-k candidates via bubble sort, reducing position
that correspond to the same real-world entity. Moreover, it   bias and context length dependency; and (ii) a global selection
facilitates downstream tasks such as data augmentation by   strategy using a stronger LLM (e.g., GPT-4o) to refine top-k
establishing semantic relationships across sources.             candidates by modeling inter-record interactions.
   Traditional integration methods often struggle with se-  (3) Localized LLM Fine-tuning of Multi-Task Learnmantic ambiguities and conflicts, particularly in complex in-   ing. To enhance the generalization capability of local LLMs,
tegration scenarios without domain-specific knowledge [277].   the last approach integrates multiple task-specific datasets
                                                     36
within a unified multi-task instruction tuning framework. For   user feedback for error correction, and declarative pipeline
example, Jellyfish [454] applies parameter-efficient instruction   specifications for reproducibility.
tuning to locally deployed LLMs (7B-13B) across diverse
data processing tasks. It employs techniques such as chain-   3.1.3 LLM for Data Discovery
of-thought prompting over task-specific serialized data and  Data discovery focuses on identifying relationships within
reasoning data distillation, using explanation traces generated   datasets through tasks like data annotation (e.g., column type
by a larger mixture-of-experts model (Mixtral-8x7B-Instruct)   classification) and profiling (e.g., metadata generation). Unto guide the learning process.                                        like data analysis, which emphasizes statistical computations
Schema Matching. The objective of schema matching is   or factual answer generation, data discovery enables deeper
to identify correspondences between elements of different   semantic understanding critical for downstream applications
database schemas (e.g., matching attribute names “employee   such as integration, search, and recommendation.
ID” and “staff number”). Existing approaches directly apply      Existing data discovery methods face two limitations.
prompting techniques to enable LLMs to perform end-to-end   First, they typically consider limited interaction between
matching, utilize retrieval-augmented generation (RAG) to   queries and tables [163]. Second, many of these approaches
enhance contextual understanding, and employ LLM agents   rely heavily on large training datasets, struggle with distrito orchestrate the overall matching workflow.                 bution shifts, and fail to generalize to rare or domain-specific
(1) Prompt Based End-to-End Matching. To facilitate   data [143], [217]. Recent studies have shown that LLMs can
schema matching without requiring rigid code implementa-   effectively address these challenges by generating high-quality
tions, the first method employs various prompting techniques   metadata, enriching dataset context, and supporting natural
to guide LLM in identifying the desired mappings. For exam-   language interfaces for data discovery tasks.
ple, LLMSchemaBench [304] applies prompt engineering tech-  Data Profiling. Data profiling typically involves characterniques to interact with LLMs, defining four task scopes that   izing a given dataset by generating additional information
differ in the level of contextual information included in the   (e.g., dataset descriptions). Recent methods often employ
prompts. The prompts are constructed using established de-  prompting techniques to guide LLM in generating such metasign patterns: the persona pattern (e.g., instructing the LLM   data by leveraging their pretrained knowledge and contextual
to act as a schema matcher), meta language creation (e.g.,   understanding.
explicitly defining valid match criteria), Chain-of-Thought  (1) Manually Crafted Profiling Prompt Engineering.
reasoning, and the output automater (e.g., generating struc-  To profile different aspects of a dataset without extensive
tured JSON outputs for downstream automation).           manual effort or code implementation, the first approach relies
(2) End-to-End Matching via Context-Enriched RAG.  on a set of manually crafted profiling prompts. For example,
To enrich the matching context and improve accuracy, the sec-  AutoDDG [456] utilizes LLM with carefully designed prompts
ond method integrates retrieval-augmented generation (RAG)   to generate two types of descriptions (i.e., User-Focused Dewith various strategies. For example, Magneto [267] employs   scriptions (UFDs) for readability and Search-Focused Dea retrieve-rerank framework that combines small pre-trained   scriptions (SFDs) for search optimization) tailored to the
language models (SLMs) with LLMs to deliver cost-effective   dataset’s content and intended usage. LEDD [58] employs
and generalizable schema matching. SLMs serve as candi-   carefully crafted prompts to support core data discovery tasks
date retrievers, generating an initial ranked list of potential   in data lakes. For hierarchical cataloging, prompts instruct
matches from the target table for each input column, which  LLM to summarize data clusters into semantically meaningful
is then refined by LLMs acting as rerankers to improve   categories. For semantic search, prompts refine natural lanaccuracy. KG-RAG4SM [277] incorporates multiple retrieval   guage queries before embedding and retrieval. For real-time
strategies, including vector-based, graph traversal-based, and   relation analysis, prompts guide LLM in comparing expanded
query-based, to extract relevant subgraphs from knowledge   graph nodes and describing inter-table relationships.
graphs (KGs). These subgraphs are further refined through  (2) RAG Assisted Context Enrichment. To enhance
ranking mechanisms and used to augment LLM prompts,   retrieval effectiveness across diverse query types, the second
thereby improving schema matching performance through  method adopts a hybrid approach that integrates diverse
enriched contextual input.                                         retrieval techniques. For example, Pneuma [72] adopts a RAG
(3) Agent-Based Matching Workflow Orchestration.  framework to retrieve relevant tables from databases, data
To address complex matching patterns, the final approach   lakes, or repositories based on natural language queries. It
leverages LLM-based agents to orchestrate the end-to-end   combines LLMs with traditional retrieval techniques, such
matching workflow. For example, Agent-OM [320] employs   as full-text and vector search, using LLMs for both schema
two LLM agents (i.e., Retrieval Agent and Matching Agent)   narration (i.e., generating meaningful column descriptions)
to control the workflow by decomposing tasks via Chain-of-  and as judges to refine and rerank retrieved results.
Thought (CoT) prompting, invoking specialized tools (e.g.,  Data Annotation. Data annotation involves assigning sesyntactic/lexical/semantic retrievers and matchers), and ac-   mantic or structural labels to data elements, such as idencessing a hybrid database (relational + vector) for memory   tifying column types (e.g., Manufacturer or birthDate from
storage and retrieval. Harmonia [340] leverages LLM-based   the DBPedia ontology). Recent methods leveraging LLM
agents to orchestrate data harmonization tasks, combining   typically design prompts with task-specific annotation inpredefined data integration primitives (e.g., schema matching,   structions. Additionally, some approaches employ retrievalvalue matching) with on-demand code generation when the  augmented generation (RAG) techniques and the contextual
primitives are insufficient. In addition, it employs techniques   reasoning capabilities of LLMs to further enrich the annotalike ReAct for reasoning and action planning, interactive   tion context and improve performance.
                                                     37
(1) Task-Specific Annotation Prompt Engineering.                                           NL2SQL [452],

                                                                                                                                                              [229], [317], [234]To flexibly support diverse annotation tasks, the first ap-                       LLM as                 [247], [370], [234],
                                                                                                                   NL-Interfaceproach encodes task-specific instructions and requirements                                                                                                                                                                                                                                                                               Data                      NL2Code [443],
within  carefully  crafted prompt templates. For example,                                                                 [104], [176], [171]
CHORUS [203] integrates LLMs into the annotation pipeline

                                                                                                                                                           [226], [475], [464], [404]using  task-specific prompts that incorporate  instructions,                                                                                                                                                                              Relational     Semantic-          Multi-Step QA [494],demonstrations, data samples, metadata, domain knowledge,                              Aware
                                                                                                                         End-to-End QA [240],and output formatting guidance. Goby [204] explores the                                                                    [365], [306],
                                                                                                                                                                        [82], [477], [471]use of LLMs for semantic column type annotation in a                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 Structureddomain-specific enterprise setting by crafting a set of tailored                       LLM as         NL2GQL [252], [493]
                                                                                                                   NL-Interfaceprompts. It proposes several techniques to improve perforRetrieval-Then-mance, including tree serialization (providing the full ontology                                                                      Data                        Reasoning [458], [193]
as prompt context), grammar-constrained decoding (enforcing hierarchical structure during generation), and step-by-                                                                                       Graph                          Execution-Thenstep prompting (Chain-of-Thought strategy to guide ontology                                  Semantic-          Reasoning [424], [246]
navigation). LLMCTA [217] evaluates diverse LLMs for gen-                              Aware                 Fine-Tuning
erating and refining label definitions by employing methods                                                Based [441], [397], [375]

                                                                                                                       Agent Based [192], [100]like    knowledge generation                       prompting                                              (e.g., producing                                                                  initial
demonstrations),                   self-refinement                                 (error-based                                                  definition                                                    im-                                                       Analysis
provement), and self-correction (two-step pipeline featuring                           Data               Markup Language
a reviewer model).                                                                                     Semi-Structured
                                                                                                          Tables [165], [281], [245](2) RAG Assisted Annotation Context Enrichment.                                                                                                                                                                                      Semi-Structured
To supply LLM with relevant annotation context, the second
approach utilizes diverse retrieval strategies within retrieval-                         OCR-Dependent [376],
augmented generation (RAG) frameworks to enrich the input.                                        [62]                   Text Masked• Classical Retrieval Technique. To mitigate the shortcom-                                                                                                                                           Document     OCR-Free           Learning [225], [49]
ings  of vanilla LLM-based annotation, such as outdated                                                        Visual Embedded
knowledge, this method augments the context with retrieved                                                     Learning [174], [138]
external knowledge. For example, RACOON [408] performs                                                Program Analysis
                                                                                                                          Based [271], [457]semantic type annotation by leveraging a Knowledge Graph                                                                                                                                                 Unstructured               Vulnerability
                                                                                                                 Detection(KG) to retrieve entity-related information (e.g., labels and                                                       Case-driven Prompt
                                                                                                                                   Engineering [270], [492]triples) associated with column cells. This information is then                                                                                                                                           Language
processed into concise contextual representations and incor-                                              Code Summarization
                                                                                                                                                               [154], [51], [284]porated into LLM prompts to improve annotation accuracy.                                   Semantic-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           Program     Aware• LLM Based Generation. To fully leverage LLM’s internal                                               Code Completion
                                                                                                                                                               [357], [118], [413]knowledge, this method relies on the model itself to generate
relevant contextual information. For example, Birdie [163]
                                                                          Fig. 9: Overview of LLM for Data Analysis.leverages LLMs to automatically generate natural language
queries for training a differentiable search index (DSI), which
facilitates linking relational tables to queryable knowledge
by enriching them with contextual semantics. It supports   3.2.1.1 Relational Data Analysis
scalable structured data annotation, using prompts composed                                  LLM for Natural Language Interfaces. Basic analysisof structured markdown tables comprising captions, headers,                                                               jobs for relational data are typically characterized by well-and sample rows alongside explicit task instructions.                                                               defined operations. These include basic calculations  (e.g.,
                                                      summation, averaging, counting, ranking), statistical analysis
                                                                             (e.g., regression, K-means clustering), and data quality assur3.2  LLM for Data Analysis                               ance processes (e.g., constraint validation, outlier detection).
Apart from data manipulation, LLMs hold the potential  Such tasks can generally be supported by tools like SQL or
to revolutionize traditional data analysis paradigms by sup-  Python libraries (e.g., Pandas).
porting natural language interfaces and enabling advanced,   (1) NL2SQL. With the help of LLM, users can directly persemantic-aware analysis tasks that typically require human  form operations using natural language. NL2SQL focuses on
involvement. In this section, we discuss the challenges and   translating natural language queries into SQL commands by
techniques of LLM-based data analysis, including structured   leveraging techniques such as (i) schema linking, which aligns
data analysis, semi-structured data analysis, and unstruc-   user intents with database schema to resolve ambiguities [452],
tured data analysis.                                                 [247], (ii) content retrieval, which dynamically extracts relevant information from the database to refine query generation [370], [234], and (iii) SQL generation strategies such as
3.2.1 LLM for Structured Data Analysis                       multi-step generation, intermediate SQL representation, and
Structured data refers to data with well-defined schemas like   different decoding strategies [229], [317], [234], [483], [484].
relational (tabular) data [107] and graph data [60].              (2) NL2Code. Different from NL2SQL, NL2Code approaches
                                                     38
                         Iterative                                         equations, and performs the rules or executes the equations to
          Question      Processor                                        get the final answer through LLM prompting. S3HQA [226]                                       Output  (a)                            SQL      LLM                  Intermediate                    trains a retriever which aims to perform initial filtering of
          Table                   Python      Tools     Input        Table                    Answer                                                        LLM           heterogeneous resources, utilizes a selector to select the most
                                                                relevant factual knowledge, and a generation-based reasoner
                                                        Image                      End-to-End                                                  (1)                                           Pre-Train                                                                         Caption               to obtain final answers.          Question                                                                        Recognition                                        (For                                  MLLM)         Table  (b)                        LLM /                                                                 (2) Iterative Decomposition. However, static decomposition
          Table           MLLM   (2) Fine-Tuning      Fact Verification        Answer
                                        (For LLM / MLLM)  Table QA          ...             paradigm performs poorly on multi-hop queries, while LLMdriven  iterative decomposition, which dynamically  refines
                                                            subtasks through recursive reasoning, could effectively ad-  Fig. 10: General Workflows - (a) Multi-Step Relational                                                                dress the issue.      Data QA. (b) End-to-End Relational Data QA.                                         TAPERA [475] introduces the query decomposition step
                                                                  into the question answering process by adopting the LLMdriven approach. The Planner decomposes the query into sub-emphasize enhancing relational data analysis through gener-                                                                   queries, forming an initial plan. The Reasoner then generatesating Python code (e.g., Pandas, NumPy), which includes a                                                             executable programs for each sub-query, while the Answervast number of library APIs characterized by high variability                                                         Generator derives answers based on the program outputs toand complexity, and often requiring the handling of complex                                                                                      fulfill the plan. Finally, the Planner updates or finalizes thechain operations. Recent advancements address these issues                                                           plan as needed.to some extent.                                                                       Similarly, ReAcTable [464] and CHAIN-OF-TABLE [404]• Model Finetuning: PACHINCO [443] fine-tunes a 62B pa-                                                                     iteratively generate  operations and update the  table  torameter PALM [104] model in two stages  (i.e., separately                                                              present a reasoning chain as a proxy for intermediate thoughtsusing a Python source code corpus with 64B tokens and a                                                        through prompting LLMs and in-context learning.Jupyter notebook corpus with 9.6B tokens) so as to improve                                                        • End-to-End QA. End-to-End Question Answering (QA)model performance on analysis-related tasks (e.g., calculate                                                                      refers to approaches in which the answer-generating LLM di-the amount of games added in each year for each month).                                                                   rectly produces the final response without intermediate stepsDataCoder [176] utilizes different types of contexts (e.g., code,                                                              or iterative refinement. Based on the data representation andtext, and data) by employing dual encoders (e.g., data encoder                                                              processing mechanisms, the relevant methods can be classifiedand code + text encoder) and one general decoder to generate                                                                  into table-specific LLM fine-tuning, table content retrieval,code in notebooks.                                                    and table-as-image analysis.
• LLM Based Analysis Agent: Data Interpreter [171], on                                                                 (1) Table-Specific LLM Fine-Tuning. Fine-tuning LLMs onthe other hand, leverages LLMs through APIs to generate                                                                    task-specific  table  datasets  enables  them  to  internaltask and action graphs. Specifically, they utilize LLM’s se-                                                                       ize analytical knowledge directly within their parameters.
mantic reasoning ability to accurately decompose complex                                                TableGPT [240] fine-tunes LLMs like GPT-3.5 using a diverseuser queries into subproblems (e.g., correlation analysis, data                                                                    set of table tasks synthesized from real-world tables. Building
exploration, and anomaly detection), and refine and verify                                                     on Qwen2.5 [324], TableGPT2 [365] introduces a table encoder
each subproblem to improve code generation results for data                                                               to generate a hybrid table representation, an adapter to genscience tasks.                                                                erate query representations, and a LLM decoder generates an
LLM for Semantic Analysis. Moreover, some jobs require   agent workflow (i.e., the tool execution pipeline) to derive the
LLM-based analysis, such as those that involve semantic   final answer. The TableGPT2 model is pre-trained on 593.8K
understanding or demand outputs in natural language for-   tables and fine-tuned 2.36M question-answer pairs.
mat (e.g., table summarization). These challenges call for   (2) Table Content Retrieval. Instead of embedding the whole
methodologies like (1) multi-step question answering (QA)   table, table content retrieval enhances model performance
with diverse decomposition strategies and (2) end-to-end QA  by eliminating noisy parts of the table while retaining inleveraging specifically optimized LLMs.                       formation relevant to question answering. CABINET [306]
• Multi-Step QA. Multi-step question answering (QA) refers   employs a weakly supervised component to produce a parsing
to decomposing complex queries into a sequence of sub-   statement that defines the criteria for selecting relevant rows
questions to facilitate step-by-step reasoning. According to  and columns, emphasizing the corresponding table cell conthe question decomposition mechanisms, existing methods   tent. TableMaster [82] constructs a refined subtable through
can be categorized into two types: (1) static decomposition,  row and column lookup. By leveraging carefully designed
which follows predefined and fixed processing steps  (e.g.,  LLM prompts (e.g., provide objective, table definition, table
retrieve-select-reason), and (2) LLM-driven iterative decom-   information, question, instructions, and response format), it
position, in which the LLM dynamically determines the next   ranks all candidate columns, selects a relevant subset based
operation based on the contextual history of the reasoning  on the query, and then instructs the LLM to generate an SQL
process.                                                  query for extracting the most relevant rows.
(1) Static Decomposition. The static decomposition includes   (3) Table-As-Image Analysis. Due to the limitations of (textRetriever-Selector-Reasoner frameworks and the  variants,   only) LLMs in understanding table structures, the Table-aswhich  partition tasks  into modular components  for bet-  Image approach has been proposed, converting tables into imter multi-step inference and enhanced interpretability. The   ages for analysis using multimodal LLMs. Table-LLaVA [477]
Extractor-Reasoner-Executor paradigm [494] extracts the rel-   applies incremental pretraining to LLaVA-7B [258] on 150K
evant segments from the context, generates the logic rules or   table recognition samples (e.g., input a table image and out39
put table representations in HTML, Markdown, or LaTeX),     To enhance LLMs’ comprehension of the complex synenabling the model to align table structures and elements   tax of Graph Query Language (GQL), R3-NL2GQL [493]
with textual modality. It is further fine-tuned on 232K sam-   proposes a hybrid approach leveraging relatively small LLM
ples on question answering, text generation, fact verification,   (e.g., LLaMA3-7B) as a selector and GQL rewriter, while emand structure understanding tasks to enhance its instruction-   ploying a larger LLM (e.g., GPT-4) as a reasoner. The selector
following ability. To enable a single model to perform vari-   identifies the necessary CRUD functions, clauses, and schema,
ous analytical tasks, TabPedia [471] introduces the concept   while the rewriter refines the query by aligning it with the
synergy mechanism, abstracting all table analysis tasks into   relevant graph data retrieved by minimum edit distance and
concepts. Built on Vicuna-7B [476], it appends meditative   semantic similarity calculation. The LLM then synthesizes the
tokens to the input of the LLM decoder, which adaptively   aligned question, selected operations, and schema to generate
activates different regions of visual tokens and helps the model   the final GQL query.
interpret the intent behind specific task questions. However,     To address the limitations of LLMs in planning and colsuch methods face limitations when processing twisted or   laborating with other LLMs, NAT-NL2GQL [252] introduces
distorted tables, and their performance degrades significantly   a three-agent framework. The Preprocessor agent constructs
when directly handling document images.                     context information, including query rewriting, path linking,
                                                    and the extraction of query-relevant schemas. The Generator
3.2.1.2 Graph Data Analysis                                    agent, an LLM fine-tuned with NL-GQL data, generates
                                      GQL statements based on the rewritten queries and extractedDifferent from relational data, graph data represents enti-                                                          schemas. The Refiner agent iteratively enhances the GQLties (vertices) and their inter-dependencies (relationships) to                                                              or contextual information by leveraging error feedback fromexplicit model of complex network semantics  (e.g., social                                      GQL execution results.networks and knowledge graphs) beyond rigid tabular schema,
                                                        Note  that,  within  the  context  of  AI  for  Sciencewhich presents unique challenges due to the vast search
                                                              (AI4Science), the integration of LLMs with graph data anal-space and complex path reasoning in multi-hop queries [59].
                                                                      ysis has also shown significant potential and wide-rangingCompared with relational data analysis, graph data analysis
                                                                applications (e.g., treat polymers as graphs and predict theirinvolves more complex jobs like summarization based on the
                                                                properties [242], [309]), which is not the primary focus of thismulti-hop relations across the graph vertices and reasoning
                                                                 survey.over text-attributed graphs whose nodes and edges are associated with text [252], [493]. Graph data can not only be  LLM-based Semantic Analysis. Furthermore, certain jobs
stored in relational databases, but also be stored and queried   necessitate semantic-aware analysis, such as summarizing texin knowledge graphs and accessed through SPARQL in RDF   tual paragraphs embedded within graph nodes. Based on
databases (e.g., Blazegraph [8] and GraphDB [21]) or Cypher   the adopted LLM strategies, we classify the relevant methin Neo4j [17].                                             ods into retrieval-then-reasoning methods, execution-thenTraditional graph analysis (e.g., statistical methods, graph   reasoning methods, graph task based fine-tuning methods,
neural network (GNN) based methods) encompasses a spec-  and agent based methods.
trum of tasks, including node classification (e.g., categorizing   •  Retrieval-Then-Reasoning.  Retrieval-then-reasoning
academic papers into research domains), graph classification    first extracts a question-specific subgraph from the graph
(e.g., predicting node properties over molecular graphs), link   to identify the most relevant entities and then generates
prediction (i.e., inferring latent relationships between graph   answers using LLMs. To address the challenge of a vast search
nodes), community detection  (i.e., identifying densely con-   space, [458] introduces a two-stage approach. First, a trainable
nected subgraphs), anomaly detection  (i.e., identifying de-  and decoupled subgraph retriever selects a relevant subgraph
viations from expected patterns), graph clustering, and etc.   based on the query. Then, reasoning is performed over the
However, these methods have their own limitations. Statistics-   retrieved subgraph to derive the final answer. UniKGQA [193]
based methods fail to handle complex semantic information   integrates retrieval and reasoning within a unified model ar-
(e.g., query can be extremely complex and requires human ex-   chitecture. It comprises a semantic matching module, leveragpertise), while graph neural networks (GNNs) exhibit limited   ing a pre-trained RoBERTa [266] for the semantic alignment
generalization capabilities, necessitating task-specific retrain-   between questions and relations in graphs, and a matching
ing on different tasks.                                        information propagation module that propagates matching
   In contrast, the advent of LLMs offers transformative po-   signals along directed edges in graphs.
tential by leveraging their advanced reasoning capacities and   • Execution-Then-Reasoning. Execution-then-reasoning
cross-domain generalization abilities, which can (1) simplify                                                                      refers to the process of parsing natural language queries into
the query writing costs (e.g., NL interfaces) and (2) achieve                                                             executable logical forms (e.g., SPARQL) that align with the
semantic-aware analysis unsupported in traditional ones.                                                       graph data, followed by reasoning based on the output of the
Natural Language To Graph Analysis Query. Different   executed program. Interactive-KBQA [424] introduces an infrom NL2SQL, the syntax of graph query language generation   teractive LLM QA framework with a unified SPARQL-based
is more complex (i.e., MATCH, LOOKUP, GET and other   toolset (e.g., entity search, graph pattern search, SPARQL exoperations unique to graph data manipulation) and there exist   ecution, etc.) designed to address complex queries. FlexKBQA
two operation objects (i.e., vertex and edge) [493]. By inte-   [246] addresses the challenge of lacking high-quality annotated
grating natural language interfaces with graph data, LLMs   data in real-world scenarios. By prompting LLMs as profacilitate flexible and efficient query generation without the  gram translators, it samples program-answer pairs from the
need for specialized model architectures.                     knowledge base and generates corresponding natural language
                                                     40
questions. The synthetic question-program-answer dataset is   significant challenge in aligning queries with the table content
used to train lightweight models through execution-guided  and structure in query answering tasks. The lack of efficient
self-training, which are subsequently employed to annotate   tools (usually using the openpyxl library) and representation
real user queries. This approach addresses the distribution  methods (usually stored in Excel or HTML files) for handling
shifts between synthetic and actual data, leading to significant   semi-structured tables makes it more difficult to process such
improvements in few-shot learning scenarios.                   data.
• Graph Task Based Fine-tuning Methods. Instruct-     Although research on semi-structured table analysis  is
GLM [441] enables generative graph learning by fine-tuning   limited, several studies have compiled various semi-structured
an LLM and leveraging natural language descriptions of   table reasoning datasets, providing valuable data support.
graph structures (e.g., offer the first node and the 1-/2-/3-  TEMPTABQA  [165]  consists  of  11,454  question-answer
hop neighbors’ information). InstructGraph [397] introduces   pairs focused on temporal queries, while SPREADSHEETa stricter code-like graph representation format which con-  BENCH [281] presents a challenging benchmark for spreadstructs entities and triples in the form of list, whose back-   sheet manipulation, with 912 questions derived from realbone LLM (LLaMA2-7B) is fine-tuned on a graph-centric   world  scenarios. MiMoTable  [245] incorporates reasoning
corpus comprising 1.6 million instances. To mitigate the is-   across multiple sheets and  files, containing 1,719 queries
sue of hallucination, it incorporates Direct Preference Op-   within 428 spreadsheets. Evaluation results on these benchtimization (DPO) algorithm [329] for preference alignment.  marks highlight a significant performance gap (ranging from
GraphGPT [375] enhances model performance in zero-shot  20% to 50%) between state-of-the-art models and human
scenarios by incorporating a structural information encoding   performance, calling for further exploration in this area.
module based on Graph-SAGE [166] and GCN [211]. It finetunes the projector bridging the graph encoder and the LLM   3.2.3 LLM for Unstructured Data Analysis
decoder to align the language capabilities of the foundation   Unstructured data refers to data that lacks explicit structure,
LLM (Vicuna-7B) with the graph learning tasks.               as it does not adhere to a predefined schema. Additionally,
• Agent Based Methods. Agent-based methods involve    it exhibits high variability in format, length, and modality,
leveraging LLM-based agents with predefined tools  (e.g.,  which further complicates its processing and analysis.
human-written interfaces or graph processing library APIs)
that iteratively interact with the graph data to retrieve, re-   3.2.3.1 Documents
fine, and operate information. StructGPT [192] introduces an  Documents exhibit complex layouts and styles with diverse
iterative reading-then-reasoning framework, leveraging spe-   elements, including a hybrid of images, tables, charts, plain
cialized interfaces to operate on graph data. It repeatedly   text, and formulas.
applies an invoke-linearize-generate procedure to derive query   • OCR-Dependent Methods. OCR-based methods refer to
results. Another approach is to generate an entire reasoning   approaches that involve performing Optical Character Recogpath based on the query and refine it only when necessary.   nition on document images, followed by the integration of
Readi [100] initially constructs a reasoning path and instanti-   textual, layout, and visual features for reasoning. UDOP [376]
ates it on the graph. When execution errors occur, it collects   integrates text and layout modalities within a unified encoder,
error messages and invokes an LLM to revise the path. The   dynamically fusing image patch tokens and text tokens based
final answer is inferred from the instantiated graphs.          on their spatial information. Specifically, when the center of
                                                        a text token’s bounding box falls within an image patch, the
3.2.2 LLM for Semi-Structured Data Analysis                corresponding image patch embedding is added to the text
Semi-structured data refers to data that are neither with   token embedding, enabling a more cohesive representation
strictly predefined schema like relational models nor raw data   of document structure. DocFormerV2 [62] preserves the in-
(e.g., plain text or images) [48]. Meanwhile, they still maintain   tegrity of layout information by employing a visual encoder.
part of organizational properties (e.g., tags, headers) and have  Image patches and text bounding box positions are embedded
hierarchical or nested representation (e.g., County - Province   through a linear layer and added to the corresponding token
- City in a nested JSON).                                 embeddings as input to the T5 [331] encoder. To achieve local
                                                                feature semantic alignment, the model undergoes pretraining
3.2.2.1 Markup Language                                on token-to-line  (i.e., predict whether a key-value pair  is
Markup languages (e.g., XML, JSON, and HTML) are widely  on the same line or adjacent lines) and token-to-grid (i.e.,
used for structuring and exchanging data across systems.   predict each token located in which image grid) tasks. The
Traditional approaches for processing these formats typically  T5 decoder is then incorporated to fine-tune the whole model
involve transforming them into structured tables or repre-  on downstream tasks.
senting them as hierarchical tree structures. Leveraging the   • OCR Free Methods. However, the OCR step often introreasoning capabilities of LLMs, it becomes possible to directly   duces semantic errors, resulting in suboptimal performance.
extract and interpret hierarchical relationships, attributes,  To  fill this gap, OCR-free methods have emerged, directly
and nested structures from data without the need for inter-   generating the target token sequences with end-to-end mulmediate transformations.                                   timodal LLMs [257], [407]. Based on different approaches to
                                                         enhancing model understanding of textual semantics, related
3.2.2.2 Semi-Structured Tables                              works can be categorized into text masked learning and visual
Compared to structured relational data, semi-structured ta-  embedded learning.
bles exhibit a more complex structural organization charac-   (1) Text Masked Learning. Text Masked Learning involves
terized by merged cells. This inherent complexity presents a  masking textual content within a document and training
                                                     41
the model to predict the missing text. Pix2Struct [225] is a  from the entry node to the exit node. CodeBERT and a CNN
typical vision-encoder-text-decoder pre-trained image-to-text   are employed to capture intra-path and inter-path represenmodel designed for visual language understanding based on   tations, respectively. The extracted feature vectors are then
ViT [124]. It is pretrained to parse masked web pages into  combined as a unified program representation, which serves
simplified HTML. The model introduces a variable-resolution   as input to a MLP classifier for vulnerability detection.
input representation, rescaling input images to maximize the   • Case-driven Prompt Engineering. Leveraging the innumber of patches that can  fit within the given sequence   context learning and few-shot learning capabilities of LLMs
length, to prevent aspect ratio distortion. DUBLIN [49] de-   can significantly improve their accuracy in vulnerability detecsigned multiple fine-tuning tasks  (i.e., bounding box pre-   tion. VUL-GPT [270] uses GPT-3.5 to generate analysis condiction based on given text, text prediction based on given   tent (i.e., the program interpretation) for the input code and
bounding box, masked text generation, and query answering)   retrieves similar code snippets and corresponding vulnerabilto improve the generalization ability.                               ity information through BM25 [338] or TF-IDF. The retrieved
(2) Visual Embedded Learning. In Visual Embedded Learn-   information, along with the original code and analysis, is then
ing, there are no specially designed training objectives. In-   input into GPT to detect vulnerabilities. [492] designs various
stead, the model is directly fine-tuned on downstream tasks to   prompts, such as random code samples and retrieve-based
enhance its understanding of textual content within images.   code samples, and demonstrates that GPT-4 outperforms
mPLUG-DocOwl1.5 [174] introduces a spatial-aware vision-   state-of-the-art models in vulnerability detection.
to-text module designed  for  representing  high-resolution,
                                            LLM-based  Semantic-aware  Analysis.   Traditionaltext-rich images. This module preserves structural informasemantic-aware tasks convert programs into ASTs [362] ortion while reducing the length of visual features. It consists
                                                       graph structures [151] and train Seq2Seq models to learnof a convolution layer to shorten the sequence length and a
                                                     program  syntax,  dependencies, and  semantics. However,fully connected layer that projects visual features into the
                                                              these approaches lack general knowledge, leading to limitedlanguage embedding space. Unlike most methods that crop
                                                                generalization ability. By leveraging the world knowledge andor resize the  initial image before feeding  it into a vision
                                                             few-shot learning capabilities of LLMs, the performance ofencoder, DocPedia [138] directly processes visual input in the
                                                               tasks such as code summarization and code completion hasfrequency domain. It utilizes JPEG DCT [388] extraction to
                                                       been significantly improved.obtain DCT coefficients, which are then processed using a
frequency adapter before being input into the vision encoder.   • LLM as Code Summarizer. Recent advancements in
This approach allows the model to capture more visual and  LLM-powered code summarization focus on retrieving similar
textual information while using a limited number of tokens.   code snippets and leverage LLMs’ few-shot learning capability
The performance improvement observed in the experiment   to enhance performance. [154] retrieves similar code examples
suggests that this method offers a novel approach for process-  by measuring token overlap and the cosine distance between
ing high-resolution images.                               embedding vectors of code snippets. In contrast, [51] employs
                                                            the BM25 algorithm and incorporates repository information,
3.2.3.2 Program Language Analysis                           data flow information, and variable information to construct
Programming language analysis involves multiple levels of   three-shot prompts. SCLA [284] further enhances code semanabstraction, including lexical analysis, parsing, and semantic   tics in LLM prompts by preprocessing the code sample pool to
analysis, each requiring distinct techniques to process source   extract semantic information. By simultaneously leveraging
code effectively. Additionally, it must handle both local and   few-shot learning,  it achieves state-of-the-art performance
global information, such as variable scopes, function  call   based on Gemini-1.5-Pro.
chains, and complex dependencies, which pose significant   • LLM as Repository-Level Code Completer. Repository
challenges for accurate program understanding.                context (e.g., imports, related classes, etc.) plays a crucial role
LLM as Program Vulnerability Detection Tools. Re-   in code completion. Given the strong semantic understanding
cent advancements in LLMs have opened new avenues for  and generative capabilities of LLMs, how to integrate conteximproving vulnerability detection tools. Training LLMs based   tual information into code completion has become a key reon program analysis techniques enhances their ability to un-   search focus. RepoFusion [357] appends the surrounding text
derstand programs at both the lexical and syntactic levels.   of the target code to the repository context retrieved based
Leveraging in-context learning through case-driven prompt  on BM25, encoding and concatenating them as input to the
engineering enhances the model’s accuracy by providing rele-   decoder for code generation. This approach enables the model
vant examples.                                                to produce context-aware code completions by leveraging
• Program Analysis based Training. Static and dy-  both local and repository-level information. CoCoMIC [118]
namic program analysis are commonly used methods for   proposes a more robust retrieval method based on program
detecting vulnerabilities in programs. By assisting these pro-  dependency graphs. Given an incomplete program, it retrieves
cesses, LLMs improve the accuracy of vulnerability detection.   the most relevant context by analyzing file imports within
PDBER [271]  is a model fine-tuned on CodeBERT [141]   the constructed graph. By defining the relevant context as
through three tasks (i.e., Predicting Masked Tokens, Predict-    files within a two-hop neighborhood, this approach mitigates
ing Statement-Level Control Dependencies, and Predicting   the risk of excluding vital dependencies while avoiding the
Token-Level Data Dependencies). This enables more fine-   inclusion of irrelevant information. However, some researchers
grained vulnerability analysis at the statement level. To re-   have found that simple retrieval methods  fail to improve
duce the impact of irrelevant information, [457] decomposes   performance in up to 80% of cases and may even degrade perthe control flow graph (CFG) into multiple execution paths   formance due to the inclusion of irrelevant information [413].
                                                     42
As a result, Repoformer introduces a self-supervised learning  methods enrich the tuning context with detailed informaapproach to enable the model to accurately judge whether   tion. Specifically, prompts are carefully structured to include:
retrieval can improve its output quality. A new <eof> token    (i) Configuration Specifications: list of tunable knobs (e.g.,
is introduced to guide the model in determining whether  names and allowable value ranges) and usage descriptions,
context retrieval is necessary. Based on the output after <eof>   including fixed-task demonstrations (e.g., LLMBench [243],
token, it decides whether to generate the output directly or to  LATuner [132]); (ii) Environment Information: covering workperform retrieval first.                                        load and database characteristics (e.g., compressed SQL snippets with join conditions in λ-Tune [156]), as well as hardware
                                                                  settings (e.g., memory size and CPU core count).3.3  LLM for Data System Optimization
                                                        • Output Tuning Requirement. To ensure accurate parsThis section presents the application of LLM to optimize   ing and interpretation of configurations generated by LLM,
the performance of different data systems across three key                                                         output formats are explicitly specified in the prompt. For
tasks: (1) Configuration Tuning: selecting effective system                                                                 instance, LLMBench [243] requires that recommended knob
configurations, such as database knobs and indexes; (2) Query                                                               values be returned in JSON format, while LATuner [132]
Optimization: accelerating input SQL queries through logical                                                                enforces constraints such as excluding the use of the “None”
rewrites and physical plan selection; (3) Anomaly Diagnosis:                                                              value in the configuration output.
addressing system anomalies, such as spikes in the usage of  (2) Automatic Tuning Prompt Generation. To improve
specific system resources.                                                            the efficiency of prompt generation for different workloads, existing methods propose the following techniques to automate
3.3.1 LLM for Configuration Tuning                         the process of identifying effective prompts.
Configuration tuning aims to identify effective configurations,   • Input Specific Prompt Generation. To identify the most
such as database knobs [231], [474] and indexes [485], [487],   suitable prompts for varying tasks, existing methods automat-
[486], to optimize the system performance. Traditional tuning   ically tailor prompt generation based on specific inputs. For
approaches, including rule-based methods and learning-based   example, DB-GPT [491] introduces an automatic prompt gentechniques with classical machine learning models, often re-   eration framework that leverages LLM to produce multiple
quire extensive explorations without a promising starting   instruction candidates, selecting the optimal ones using scorpoint [231]. Furthermore, they might result in sub-optimal   ing functions associated with the performance improvement.
configurations, despite using advanced techniques such as   Additionally, DB-GPT [491] and LLMIdxAdvis [473] select
transfer learning [463], [402].                                demonstration examples in the prompts based on semantic
  A key limitation of these methods is the failure to incor-   similarity between candidate examples and input queries, as
porate extensive domain knowledge (e.g., information from  computed by a model-based encoder.
system manuals and public forum discussions) into the tuning   • Optimization Problem Formulation. To reduce token
process, relying solely on runtime feedback from benchmark   usage and convey the most relevant context to the LLM,
evaluations to guide optimization. To address this issue, recent  some methods formulate prompt generation as a cost-based
approaches utilize LLM with large-scale domain knowledge to   optimization problem. For instance, λ-Tune [156] compresses
enhance the tuning process via the following methods.         workload representations by modeling the selection of join
Tuning Task-Aware Prompt Engineering. The  first   conditions as an integer linear programming problem, intromethod manually designs prompts with informative details   ducing binary decision variables to capture the positional
(e.g., system status) to assist LLM in configuration tuning   relationships of different columns.
(e.g., database knobs and indexes). Some approaches further RAG Based Tuning Experience Enrichment. The secenhance this by introducing automatic prompt generation  ond method builds an offline knowledge base from diverse
techniques or by formulating it as an optimization problem.     external sources and performs online retrieval to provide LLM
(1) Manually-Crafted Tuning Prompt. Existing methods   with context-specific knowledge (e.g., similar historical tundesign prompts that incorporate essential details (e.g., system   ing cases). This approach addresses the limitations of direct
status) tailored to the characteristics of specific tasks. In   prompting, which often yields overly generic responses lacking
particular, the constructed prompts typically consist of the   concrete commands and effective configurations [96].
following components.                                   (1) LLM Based Tuning Experience Preparation. Given
• Configuration Task Instruction. To convey the overall   that existing tuning knowledge is distributed across heterogetuning objective, existing methods specify task instructions   neous formats, LLMs are employed to construct a knowledge
in the prompts using chain-of-thought (CoT) and role-play-   base by processing and integrating multi-source external exbased guidance. For instance, LLMBench  [243]  explicitly   perience in an offline manner. For example, GPTuner [223]
defines the goals of three key subtasks in knob tuning: (i)  prompts LLM to extract implicit knowledge, remove noisy
knob pruning to retain the most influential knobs, (ii) model   content, and summarize relevant information from multiple
initialization to select promising knobs for warm-starting   sources. Additionally, it introduces a prompt ensemble algobayesian optimization, and  (iii) knob recommendation to   rithm that generates multiple prompts by varying the demonreturn optimal configurations for specific workloads. Similarly,   stration examples, aiming to mitigate hallucination issues.
LATuner [132] instructs LLM to identify critical knobs for  (2) Semantic Based Tuning Experience Retrieval. To
warm-starting the tuning process and select promising knobs   improve the accuracy of relevant experience retrieval, existing
as training samples for boosting the sampling procedure.      methods employ model-based encoders to capture semantic
• Input Tuning Context. To enable LLM to effectively   relationships  (e.g., documents conveying similar meanings
support the tuning process for specific workloads, existing   with different expressions). For instance, Andromeda [96]
                                                     43
utilizes a Sentence-BERT encoder trained with contrastive   • Input Optimization Context. To enable effective query
learning to generate embeddings, which are then used to   optimization for specific workloads, existing methods augperform similarity searches across various sources, including  ment prompts with additional contextual information to
historical queries and troubleshooting manuals.                 better inform LLMs. This includes: (i) Database Statistics:
Training Enhanced Tuning Goal Alignment. The third  column selectivity [363], histograms, distinct value counts,
method introduces additional training to further refine LLMs,  and estimated cardinalities [196]; (ii) Rule Specifications: a list
improving their alignment with tuning objectives. For exam-   of applicable rewrite rules accompanied by usage descriptions
ple, DB-GPT [491] proposes techniques to facilitate effective   (e.g., GenRewrite [261] presents natural language hints as the
fine-tuning, including: (i) heuristic statistical data embedding,   rules) and illustrative examples [248].
(ii) LLM-assisted annotation of high-quality samples,  (iii)   • Output Optimization Requirement. To ensure that
contrastive learning of supplementary training data gener-   the optimizations produced by LLMs are valid and easily
ation, and (iv) delta tuning to minimize trainable parame-   processed for downstream use, some methods explicitly deters while maintaining performance. Similarly, E2ETune [177]   fine output formatting requirements within the prompts. For
fine-tunes LLMs (e.g., Mistral-7B) using training data com-   example, LLM-R2 enforces that selected rewrite rules be
prising “(workload) →(configuration)” pairs, where diverse   returned in the format “rules selected: [rule names]” [248],
workloads are generated via GPT-4 prompting and optimal   while LLM-QO specifies that the generated query plan should
configurations are identified using the HEBO algorithm [112].   follow the “join operator(table1, table2)” format [196].
                                                      (2) In-Context Learning with Optimization Example.
                                                       Rather than relying on fixed examples to illustrate how LLM3.3.2 LLM for Query Optimization
                                                           should perform optimization, some methods automatically
Query optimization aims to accelerate SQL execution through                                                                    retrieve examples that are semantically similar to the inlogical (e.g., query rewriting) and physical (e.g., join order                                                        put query to provide more effective guidance. For instance,
and plan selection) enhancements. Traditional logical opti-                                           LLM-R2 [248] introduces a contrastive representation model
mization relies on predefined rewrite rules or learning-based                                                               to encode query plans based on features such as operators,
approaches to determine rule application order, while physi-                                                                      cardinalities, and costs, and retrieves a set of high-quality
cal optimization employs heuristic algorithms using statisti-                                                            demonstrations, i.e., successfully optimized rewritten queries.
cal data or learning-based techniques leveraging query plan                                RAG Based Optimization Experience Enrichment.
features. However, these approaches often overlook external                                                The second method adopts the retrieval-augmented generaSQL optimization knowledge, limiting their effectiveness and                                                                 tion (RAG) paradigm to equip LLM with relevant contextual
generalizability across diverse SQL patterns.                                                            information for targeted optimization of specific queries. It
   To address these limitations, recent studies investigate   constructs and retrieves optimization knowledge from multithe use of LLM to directly rewrite input SQL queries or   ple sources that are semantically related to the input query.
determine optimal rule application sequences for logical opti-  (1) LLM Based Optimization Experience Preparation.
mization. They also explore leveraging LLM to select optimal  To consolidate optimization experience from multiple sources,
query execution plans for physical optimization, drawing on   existing methods introduce an offline preparation pipeline
the extensive SQL optimization knowledge encoded within the   that leverages LLM to process and integrate data into a unimodel. These methods can be broadly categorized as follows.    fied format. For example, R-Bot [369] employs LLM to genOptimization-Aware Prompt Engineering. The  first   erate rewrite rule specifications by (i) summarizing rule code
method directly employs LLMs to perform query optimiza-   within a hierarchical structure and (ii) extracting information
tion using well-structured prompts composed of two key com-  from structured documentation blocks. It further uses LLM
ponents: (i) manually crafted templates enriched with task-   to standardize the resulting specifications, explicitly outlining
specific details (e.g., explicit task instructions), and (ii) rel-   application conditions and detailed rewrite transformations.
evant optimization examples automatically selected to more  (2) Hybrid Optimization Experience Retrieval. To more
effectively guide the optimization process.                      accurately identify relevant optimization experiences, both
(1) Manually-Crafted Optimization Prompt. Existing   structural and semantic characteristics of the input queries are
methods construct prompts with the following components to   considered during similarity search. For instance, R-Bot [369]
facilitate the query optimization task.                         introduces a hybrid retrieval approach that computes sim-
• Optimization Task Instruction. To clarify the opti-   ilarity using concatenated embeddings capturing structural
mization objective and guide LLMs to produce specific op-   features (e.g., rewrite rule explanations) and semantic repretimization actions, detailed task instructions are included   sentations (e.g., query template structures). Based on the rein the prompts. For logical query optimization, some meth-   trieved experience, R-Bot employs a step-by-step LLM-driven
ods instruct LLMs to directly generate equivalent rewritten   rewrite process, further enhanced through a self-reflection
queries with improved performance (e.g., DB-GPT [491], Gen-  mechanism to improve rewrite quality.
Rewrite [261], and LITHE [363]), while others ask them to  Training Enhanced Optimization Improvement. The
determine the optimal sequence of rewrite rule applications   third method either uses LLM outputs to train smaller models
for a given query (e.g., LLM-R2[248] and R-Bot[369]). For   or fine-tunes LLMs on task-specific data to support various
physical query optimization, some approaches prompt LLMs   query optimization tasks (e.g., query plan generation). For
to generate complete query plans with specified operators and   instance, LLMSteer [53] uses LLM-generated embeddings to
join orders (e.g., LLM-QO [196]), while others instruct LLMs   train a classifier for selecting optimal hints of the input SQL.
to generate optimization hints or select the most effective plan  LLM-QO [196] fine-tunes LLMs to generate execution plans
from a set of candidates (e.g., LLMOpt [438]).                   directly through a two-stage pipeline: (i) Query Instruction
                                                     44
Tuning (QIT) for producing valid plans; (ii) Query Direct   example, D-Bot [490], [489] orchestrates multiple domainPreference Optimization (QDPO) for distinguishing high-   specific LLM agents, each aligned with a cluster of prequality plans. The fine-tuning data is structured as “(query,   processed diagnosis knowledge, to support precise anomaly
task instruction, auxiliary information such as schema and   diagnosis in databases. These agents, coordinated by a chief
statistics, demonstration)” paired with the corresponding effi-   agent, conduct multi-step root cause analysis via a treecient execution plan. LLMOpt [438] fine-tunes two models:   search algorithm. Similarly, Panda [359] emulates experienced
(i) LLMOpt(G), which generates candidate hints, and  (ii)   database engineers by leveraging LLM agents across  five
LLMOpt(S), which selects the optimal hint as a list-wise cost   functional components: (i) question verification to eliminate
model. The fine-tuning data is structured as “(query, statistics   irrelevant queries, (ii) grounding to provide necessary input
such as histograms) →(optimal hint)” for LLMOpt(G) and   query context, (iii) verification to ensure diagnosis accuracy
“(query, statistics such as histograms, candidate hints) →  and source attribution, (iv) feedback integration to incorpo-
(index of optimal hint)” for LLMOpt(S).                        rate user input, and (v) affordance assessment to estimate the
                                                         performance impact of generated solutions.
3.3.3 LLM for Anomaly Diagnosis                        Localized LLM Enhancement via Specialized FineAnomaly diagnosis focuses on analyzing root causes and iden-  Tuning. The last method employs specialized fine-tuning
tifying recovery solutions for anomalies (e.g., spikes in system   strategies for localized LLMs of modest scale (e.g., 6B-14B),
resource usage) during the system runtime, such as databases.   leveraging distilled knowledge to approximate the outputs
Traditional rule-based methods often fail to accurately iden-   of larger models while achieving comparable performance.
tify root causes across diverse scenarios, while classical ma-   For instance, D-Bot [490] applies multi-task fine-tuning to
chine learning models (e.g., random forests) cannot generate   improve the diagnosis capabilities of localized LLMs. Specifcomprehensive reports with detailed recovery solutions.           ically, three models (i.e., Llama2-13B, CodeLlama-13B, and
   Recent studies demonstrate that LLMs, with their ad-   Baichuan2-13B) are fine-tuned to replicate the diagnosis revanced textual understanding and reasoning capabilities, can   sults generated by the GPT-4-powered D-Bot. The fine-tuning
effectively pinpoint root causes and generate detailed diagno-   dataset consists of samples covering D-Bot diagnosis worksis reports with recovery solutions in various formats. These   flows across five sub-tasks (e.g., tool invocation), along with
LLM-based approaches can be categorized as follows.          associated prompts and historical dialogue messages.
Manually Crafted Prompts for Anomaly Diagnosis.
The first method emulates the reasoning process of a human                                                          Practices of LLMs for Data Management
DBA, which involves referencing essential statistical information and conducting an in-depth analysis during diagnosis.                                                            Alibaba Cloud  [5] has integrated Text-to-SQL fea-The information is incorporated into well-structured prompts                                                                    tures into  its BI platform,  facilitating NL queriesto enhance diagnosis accuracy. For example, DBG-PT [155]                                                                 over structured datasets. Amazon Nova [3] employsutilizes LLM to detect query execution slowdowns caused                                                         automated document processing to extract structuredby changes in query plans, using prompts that include: (i)                                                                information from diverse unstructured sources. Ina summary of plan differences,  (ii) a request for feasible                                                            terms of data systems, PawSQL [41], an advancedconfiguration recommendations, and (iii) a specification of the                                                            query optimization platform, offers both SQL rewrit-reasoning process with output formatted in JSON format.                                                                  ing and index recommendation capabilities, adoptedRAG Based Diagnosis Experience Enrichment. The                                                        by over 10,000 professionals. Database diagnosis alsosecond method adopts retrieval-augmented generation (RAG)                                                                      thrives on a robust ecosystem. For instance, DB-paradigm to provide LLM with relevant diagnosis knowledge,                                                           Doctor [35], compatible with mainstream databases,leveraging two key components: a knowledge base and a                                                                        delivers kernel-level performance diagnostics for com-retriever. For instance, D-Bot [490], [489] enhances database                                                                prehensive system analysis and optimization.anomaly diagnosis by preparing a corpus of documents and
tools considering the hierarchical document structure, then
using a fine-tuned Sentence-BERT encoder to retrieve relevant materials and guide LLM via prompts enriched with  4  Challenges and Future Directions
the retrieved content. ByteHTAP [425] supports LLM-based   4.1  Data Management for LLM
diagnosis of query performance regressions in HTAP systems
by first constructing a knowledge base of historical queries and   4.1.1 Task-Specific Data Selection for Efficient Pretraining
their associated performance explanations. It then employs an   In LLM pre-training, vast amounts of general data are typenhanced tree-CNN classifier to encode and retrieve relevant   ically used, but much of this data may not be relevant to
plan pairs. The retrieved information  is incorporated into   the target task. The inclusion of irrelevant data not only
prompts that include: (i) background information (e.g., key   increases training time but also impedes the model’s adaptdifferences among HTAP system engines), (ii) a task descrip-   ability to specific tasks. For instance, when training a model
tion (e.g., retrieved diagnosis knowledge with explicit input-   for the medical domain, unrelated data sources such as news
output specifications), and (iii) additional user-provided con-   articles and social media posts may hinder the learning of
text (e.g., recent index changes).                               domain-specific knowledge. Consequently, the challenge lies
Multi-Agent Mechanism for Collaborative Diagnosis.   in automatically selecting task-relevant data while discarding
The third method adopts an agent-based diagnosis frame-   irrelevant information during pretraining. Currently, most
work, where specialized agents with distinct responsibilities   approaches rely on hand-crafted filtering rules or fixed labeled
collaborate to improve diagnosis accuracy and efficiency. For   datasets for data selection, lacking dynamic strategies that
                                                     45
adapt to the model’s evolving task-specific needs. Exploring   not fully capture a dataset’s quality. The current framework
methods to automatically select relevant data and discard    falls short of providing a comprehensive evaluation that aligns
irrelevant data during pre-training represents a promising   with the model’s capabilities and performance improvements.
avenue for improving task adaptability and training efficiency.   Therefore, a promising direction for future research is the development of a robust dataset evaluation system that does not
                                                                    rely on model training. This system should provide consistent4.1.2 Optimizing Data Processing Pipelines
                                                                quality scores that directly correlate with model performance
Currently, the construction of data processing pipelines for                                                         enhancements, enabling more efficient dataset selection and
LLMs relies heavily on experience and experimentation. For                                                            use without the need for exhaustive training cycles.
instance, in building the FineWeb dataset, decisions such
as whether to use the WET or WARC format for text extraction from CommonCrawl, or whether to apply a global   4.1.5 Hybrid RAG Indexing and Retrieval
MinHash approach for deduplication or perform it separately   Currently, there lacks a single database that integrates fullfor each snapshot, are made only after training models and   text, vector, knowledge graph, and structured search  inbenchmarking their performance. However, this experimental   terfaces into a cohesive indexing and retrieval engine for
methodology is resource-intensive. In the case of FineWeb,   Retrieval-Augmented Generation (RAG) training. While sysover 70 models with 1 billion parameters were trained, con-  tems like Elasticsearch [36] excel in full-text and vector search,
suming a total of 80,000 H100 GPU hours. To improve the  and LightRAG [164] has introduced advanced vector and
efficiency of these pipelines, future research should focus on   graph processing, these solutions remain siloed. They lack a
developing data-driven methods that can predict optimal pre-   unified platform designed specifically for hybrid RAG, where
processing configurations. in advance, reducing the reliance on   multiple indexing and search mechanisms coexist to support
costly trial-and-error approaches. This would not only mini-   efficient downstream applications. Although emerging platmize computational costs but also accelerate the development   forms like AutoRAG [209] provide frameworks for constructof high-quality datasets for LLMs.                             ing RAG pipelines, they focus on workflow management,
                                                     model integration, and automation rather than offering a
                                                                       fully integrated database with indexing and retrieval engines.
4.1.3 LLM Knowledge Update and Version Control      A promising direction for future RAG data serving is the
In  fast-evolving domains  (e.g.,  healthcare,  finance,  law),   development of an integrated platform that provides seamless
knowledge is constantly updated. To ensure the reliability   indexing and retrieval for diverse data types, while also inteof LLMs, the data used for training and fine-tuning must   grating data serving features such as knowledge filtering and
be up-to-date. Delays in incorporating the latest knowledge   re-ranking [47], thereby improving the efficiency and flexibility
can result in outdated or harmful outputs, particularly in   of RAG applications.
fields like medicine where guidelines frequently change. While
there have been various approaches to data synthesis and
augmentation, little attention has been given to efficiently   4.2  LLM for Data Management
managing rapid knowledge updates or resolving contradic-   4.2.1 Unified Data Analysis System
tions when new information conflicts with older data. Existing  One of the major challenges in LLM for Data Analysis is
systems often rely on static datasets, which are problematic   the absence of a unified system capable of handling diverse
in dynamic sectors. Although platforms like ChatGPT and   data types. Currently, analyzing different data formats often
Deepseek allow LLMs to search the web, this approach may   requires designing task-specific models separately. The most
not always guarantee accuracy or relevance, leading to subop-   straightforward approach to enabling a system to process
timal results. A more effective solution would involve a plat-    all types of data is to integrate these models into a single
form that facilitates the creation, sharing, and version control   framework. However, this leads to prohibitively high deployof datasets with real-time knowledge updates. By leveraging  ment and maintenance costs due to the need to manage
community-driven contributions, this platform could enable   multiple models simultaneously. A more promising direction
users to synthesize and share datasets using customizable    is to develop a model that can flexibly accommodate various
methods, such as LLM-generated prompts from documents   data inputs and user requirements while supporting the analor websites, offering continuous, high-quality updates and   ysis of structured, semi-structured, and unstructured data.
improving the overall accuracy and reliability of LLMs.        Such a system would establish a paradigm for LLM for Data
                                                            Analysis at the system level and offer a generalized capability
4.1.4 Comprehensive Dataset Evaluation                       for analyzing data across different structural types, thereby
                                                                       facilitating data automation.The performance enhancement of models is closely tied to the
use of ’high-quality’ datasets. However, determining what constitutes a high-quality dataset remains a challenge. Typically,   4.2.2 Data Analysis with Private Domain Knowledge
the quality of a dataset can only be inferred after training  Another challenge in leveraging LLMs for data analysis is
and evaluating a model, which makes the process indirect   the effective utilization of private domain knowledge. Current
and resource-intensive. When a dataset’s quality is subpar,   approaches primarily rely on RAG to retrieve relevant knowlit can lead to significant computational overhead and ineffi-   edge or fine-tune models on domain-specific datasets. Howciencies. While existing research [393] has proposed a model-   ever, these methods struggle when dealing with novel or highly
agnostic method for evaluating datasets across three aspects:  complex domain knowledge. For example, in Text-to-SQL
reliability, difficulty, and validity. These dimensions alone do   tasks involving large-scale databases with 10,000 columns and
                                                     46
1,000,000 rows, where each column is associated with specific  References
domain knowledge, existing techniques often fail to generalize    [1]   https://arangodb.com/.
effectively. The lack of datasets that explicitly incorporate    [2]    https://arxiv.org/.
domain knowledge further exacerbates this issue, making it    [3]   https://aws.amazon.com/cn/ai/generativeai/nova/understanding/.difficult to meet the demands of real-world industrial applica-                                                                                        [4]   https://aws.amazon.com/s3.
tions. Consequently, developing more advanced mechanisms    [5]    https://bailian.console.aliyun.com/xiyan.
for integrating domain knowledge into LLMs remains a critical    [6]    https://beautiful-soup-4.readthedocs.io/en/latest/.
open research problem.                                                        [7]   https://bitbucket.org/product/.                                                                                        [8]   https://blazegraph.com/.
                                                                                        [9]    https://cachelib.org/.
4.2.3 Representing Non-Sequential and Non-Textual Data    [10]  https://cocodataset.org/.
                                                                                [11]  https://commoncrawl.org/.
Current LLM-based approaches  typically transform non-    [12]  https://docs.cohere.com.
sequential and non-textual data into serialized textual formats    [13]  https://docs.python.org/3/library/pickle.html.
to align with the input requirements of LLMs [129], [196],    [14]  https://github.com/.                                                                                [15]  https://github.com/deepseek-ai/3fs.
[438]. While this enables basic compatibility,  it overlooks    [16]  https://github.com/juicedata/juicefs.
the original structural semantics of the data and can lead    [17]  https://github.com/neo4j/neo4j.
to significant information loss in downstream tasks. For in-    [18]  https://github.com/paddlepaddle/paddleocr.                                                                                [19]  https://github.com/seleniumhq/selenium.stance, in data manipulation and analysis, relational tables                                                                                [20]  https://gitlab.com/.
(originally structured as two-dimensional matrices) are typ-    [21]  https://graphdb.ontotext.com/.
ically flattened into multiple serialized sequences, obscuring    [22]  https://huggingface.co/.
inherent row-column relationships [78], [74], [319]. Similarly,    [23]  https://huggingface.co/ckiplab/bert-tiny-chinese.                                                                                [24]  https://huggingface.co/infgrad/stella-large-zh-v2.
in system optimization tasks, crucial statistical signals such    [25]  https://lancedb.com.
as column selectivities and histograms are either omitted or    [26]  https://milvus.io.
naively encoded as plain texts, limiting their utility in guiding    [27]  https://onnx.ai.
                                                                                [28]  https://openlibrary.org/.optimization decisions [156], [132]. Consequently, a promising                                                                                [29]  https://paddlenlp.readthedocs.io.
future direction is to develop more expressive and task-aware    [30]  https://playwright.dev/.
representations that preserve the structural and statistical    [31]  https://pptr.dev/.
integrity of such data. This includes leveraging multi-modal    [32]  https://pytorch.org/.                                                                                [33]  https://spacy.io/.
LLMs or designing tailored encoding strategies that maintain    [34]  https://weaviate.io.
the uniqueness of these data types, thereby enabling more    [35]  https://www.dbdoctor.cn/.
effective and semantically informed LLM applications.            [36]  https://www.elastic.co/elasticsearch.                                                                                [37]  https://www.eyelevel.ai/post/do-vector-databases-loseaccuracy-at-scale.
4.2.4 Efficient LLM Utilization Under Budget Constraints    [38]  https://www.gutenberg.org/.
                                                                                [39]  https://www.llamaindex.ai/.
While LLMs have shown strong potential across data manip-    [40]  https://www.mindspore.cn/.
ulation, analysis, and system optimization tasks, their high    [41]  https://www.pawsql.com/.
computational cost and latency pose challenges for real-time    [42]  https://www.tensorflow.org.
                                                                                [43]  https://www.tensorflow.org/guide/data.or large-scale applications [196], [53]. For example, relying                                                                                [44]  https://www.tensorflow.org/tutorials/load  data/tfrecord.
solely on LLMs is impractical for processing tens of millions    [45]  A. Abbas, E. Rusak, K. Tirumala, W. Brendel, K. Chaudhuri,
of rows in relational table analysis due to prohibitive resource       and A. S. Morcos.  Effective pruning of web-scale datasets
demands [432], [304]. Similarly, current LLM-based query        based on complexity  of concept  clusters.   arXiv preprint                                                                       arXiv:2401.04578, 2024.
optimizers often require minutes per query, far exceeding    [46]  A. Abbas, K. Tirumala, D. Simig, S. Ganguli, and A. S. Morcos.
the millisecond-level efficiency of traditional statistical meth-        Semdedup: Data-efficient learning at web-scale through semanods [369], [248]. Therefore, a promising direction is to develop           tic deduplication. arXiv preprint arXiv:2303.09540, 2023.
                                                                                [47]  A. Abdallah, J. Mozafari, B. Piryani, and A. Jatowt. Asrank:
hybrid strategies that integrate LLMs with traditional tech-         Zero-shot re-ranking with answer scent for document retrieval.
niques or to devise scheduling mechanisms that allocate tasks        arXiv preprint arXiv:2501.15245, 2025.
across multiple LLMs based on cost-performance trade-offs.    [48]   S. Abiteboul. Querying semi-structured data. In Database TheSuch approaches can enhance the practicality and scalability       ory—ICDT’97: 6th International Conference Delphi, Greece,                                                                  January 8–10, 1997 Proceedings 6, pages 1–18. Springer, 1997.
of LLM-based systems under real-world budget constraints.     [49]  K. Aggarwal, A. Khandelwal, K. Tanmay, O. M. Khan, Q. Liu,
                                                        M. Choudhury, H. H. Chauhan,  S. Som, V. Chaudhary,
                                                               and S. Tiwary.  Dublin: Visual document understanding by
5  Conclusion                                                    language-image network, 2023.
In  this  paper, we summarize  the  recent  techniques on    [50]  C. Aguerrebere,  I. Bhati, M. Hildebrand, M. Tepper, and                                                                   T. Willke.  Similarity search in the blink of an eye with comDATA4LLM and LLM4DATA. The former focuses on uti-         pressed indices, 2023.
lizing data processing, storage, serving techniques to address    [51]  T. Ahmed, K. S. Pai, P. Devanbu, and E. Barr.  Automatic
the data problems in different LLM stages. The latter fo-        semantic augmentation of language model prompts (for code
cuses on using LLM capabilities to reduce the complexity        summarization).national ConferenceIn Proceedingson SoftwareofEngineering,the IEEE/ACMICSE46th’24,Inter-New
of conducting data management,  e.g., data manipulation,         York, NY, USA, 2024. Association for Computing Machinery.
data analysis, and data system optimization. We also provide    [52]  A. Akbik, T. Bergmann, D. Blythe, K. Rasul, S. Schweter,
some research challenges and open problems in DATA4LLM,        and R. Vollgraf.  Flair: An easy-to-use framework for state-                                                                                 of-the-art nlp.  In Proceedings of the 2019 conference of the
LLM4DATA, and hybrid data and LLM optimization.             North American chapter of the association for computational
                                                                                    linguistics (demonstrations), pages 54–59, 2019.

                                                     47
[53]  P. Akioyamen, Z. Yi, and R. Marcus. The unreasonable effec-    [74]  T. Bendinelli, A. Dox, and C. Holz.  Exploring llm agents
      tiveness of llms for query optimization. CoRR, abs/2411.02862,          for cleaning tabular machine learning datasets.   In ICLR
      2024.                                                        2025 Workshop on Foundation Models in the Wild, 2025.
[54]  M. M. Alam and W. Wang. A comprehensive survey on data         arXiv:2503.06664.
      provenance: State-of-the-art approaches and their deployments    [75]  M. Berglund and B. van der Merwe. Formalizing bpe tokenizafor iot security enforcement. J. Comput. Secur., 29(4):423–446,          tion. arXiv preprint arXiv:2309.08715, 2023.
      2021.                                                                   [76]   J. Bevendorff, S. Gupta, J. Kiesel, and B. Stein.  An em-
[55]  A. Albalak, Y. Elazar, S. M. Xie, S. Longpre, N. Lambert,          pirical comparison of web content extraction algorithms.  In
     X. Wang, N. Muennighoff, B. Hou, L. Pan, H. Jeong, et al.         Proceedings of the 46th International ACM SIGIR Conference
   A survey on data selection for language models. arXiv preprint       on Research and Development in Information Retrieval, SIGIR
      arXiv:2402.16827, 2024.                                                     ’23, page 2594–2603, New York, NY, USA, 2023. Association
[56]  A. Albalak, L. Pan, C. Raffel, and W. Y. Wang.  Efficient          for Computing Machinery.
      online data mixing for language model pre-training.  In R0-    [77]   S. Biderman, U. Prashanth, L. Sutawika, H. Schoelkopf, Q. AnFoMo: Robustness of Few-shot and Zero-shot Learning in Large         thony, S. Purohit, and E. Raff.  Emergent and predictable
     Foundation Models, 2023.                                        memorization in large language models.  Advances in Neural
[57]  K. An, F. Yang, L. Li, J. Lu, S. Cheng, S. Si, L. Wang, P. Zhao,        Information Processing Systems, 36, 2024.
      L. Cao, Q. Lin, et al. Thread: A logic-based data organization    [78]  F. Biester, M. Abdelaal, and D. D. Gaudio. Llmclean: Contextparadigm for how-to question answering with retrieval aug-        aware tabular data cleaning via llm-generated ofds. In ADBIS
     mented generation. arXiv preprint arXiv:2406.13372, 2024.            (Short Papers), volume 2186 of Communications in Computer
[58]  Q. An, C. Ying, Y. Zhu, Y. Xu, M. Zhang, and J. Wang. LEDD:        and Information Science, pages 68–78. Springer, 2024.
      large language model-empowered data discovery in data lakes.    [79]  D. Borthakur et al. Hdfs architecture guide. Hadoop apache
    CoRR, abs/2502.15182, 2025.                                              project, 53(1-13):2, 2008.
[59]  R. Angles. A comparison of current graph database models. In    [80]  D. Brandfonbrener, H. Zhang, A. Kirsch, J. R. Schwarz, and
     2012 IEEE 28th International Conference on Data Engineering          S. Kakade.   Color-filter: Conditional loss reduction filtering
     Workshops, pages 171–177, 2012.                                          for targeted language model pre-training.   arXiv preprint
[60]  R. Angles and C. Gutierrez. Survey of graph database models.         arXiv:2406.10670, 2024.
   ACM Comput. Surv., 40(1), Feb. 2008.                              [81]  A. Z. Broder. On the resemblance and containment of docu-
[61]  Z. Ankner, C. Blakeney, K. Sreenivasan, M. Marion, M. L.        ments.  In Proceedings. Compression and Complexity of SELeavitt, and M. Paul.  Perplexed by perplexity: Perplexity-      QUENCES 1997 (Cat. No. 97TB100171), pages 21–29. IEEE,
     based data pruning with small reference models. arXiv preprint         1997.
      arXiv:2405.20541, 2024.                                              [82]  L. Cao. Tablemaster: A recipe to advance table understanding
[62]   S. Appalaraju, P. Tang, Q. Dong, N. Sankaran, Y. Zhou, and        with language models, 2025.
     R. Manmatha.  Docformerv2: Local features for document    [83]  Q. Cao, M. Najibi, and S. Mehta. Ctrlsynth: Controllable image
      understanding, 2023.                                                  text synthesis for data-efficient multimodal learning, 2024.
[63]   S. Arora, B. Yang, S. Eyuboglu, A. Narayan, A. Hojel, I. Trum-    [84]  Y. Cao, Y. Kang, C. Wang, and L. Sun.  Instruction mining:
     mer, and C. R´e. Language models enable simple systems for         Instruction data selection for tuning large language models.
      generating structured views of heterogeneous data lakes. Proc.        arXiv preprint arXiv:2307.06290, 2023.
    VLDB Endow., 17(2):92–105, 2023.                                  [85]  B. Casey, K. Damian, A. Cotaj, and J. C. S. Santos.  An
[64]  M. Artetxe, S. Bhosale, N. Goyal, T. Mihaylov, M. Ott,         empirical study of safetensors’ usage trends and developers’
      S. Shleifer, X. V. Lin, J. Du, S. Iyer, R. Pasunuru, et al. Efficient         perceptions, 2025.
      large scale language modeling with mixtures of experts. arXiv    [86]  C. Chai, J. Wang, Y. Luo, Z. Niu, and G. Li. Data management
      preprint arXiv:2112.10684, 2021.                                          for machine learning: A survey. IEEE Trans. Knowl. Data Eng.,
[65]  G. A. Atemezing. Empirical evaluation of a cloud-based graph         35(5):4646–4667, 2023.
      database: the case of neptune. In Knowledge Graphs and Se-    [87]  C.-Y. Chang, Z. Jiang, V. Rakesh, M. Pan, et al.  Main-rag:
     mantic Web: Third Iberoamerican Conference and Second Indo-         Multi-agent filtering retrieval-augmented generation, 2024.
     American Conference, KGSWC 2021, Kingsville, Texas, USA,    [88]  M. S. Charikar. Similarity estimation techniques from rounding
     November 22–24, 2021, Proceedings 3, pages 31–46. Springer,         algorithms.  In Proceedings of the thiry-fourth annual ACM
      2021.                                                      symposium on Theory of computing, pages 380–388, 2002.
[66]  J.-M. Attendu and J.-P. Corbeil. Nlu on data diets: Dynamic    [89]  T.-Y. Che, X.-L. Mao, T. Lan, and H. Huang. A hierarchical
     data subset selection for nlp classification tasks. arXiv preprint         context augmentation method to improve retrieval-augmented
      arXiv:2306.03208, 2023.                                              llms on scientific papers.  In Proceedings of the 30th ACM
[67]  A. Audibert, Y. Chen, D. Graur, A. Klimovic, J. ˇSimˇsa, and      SIGKDD Conference on Knowledge Discovery and Data MinC. A. Thekkath.   tf. data service: A case for disaggregating          ing, pages 243–254, 2024.
     ml input data processing.  In Proceedings of the 2023 ACM    [90]  D. Chen, Y. Huang, Z. Ma, H. Chen, X. Pan, C. Ge, D. Gao,
     Symposium on Cloud Computing, pages 358–375, 2023.              Y. Xie, Z. Liu, J. Gao, et al.  Data-juicer: A one-stop data
[68]  T. Ayoola, S. Tyagi, J. Fisher, C. Christodoulopoulos, and         processing system for large language models.  In Companion
     A. Pierleoni. Refined: An efficient zero-shot-capable approach          of the 2024 International Conference on Management of Data,
      to end-to-end entity linking, 2022.                                  pages 120–134, 2024.
[69]   J. Bai, S. Bai, Y. Chu, Z. Cui, K. Dang, X. Deng, Y. Fan, W. Ge,    [91]  D. Chen, H. Wang, Y. Huang, C. Ge, Y.  Li, B. Ding,
     Y. Han, F. Huang, et al. Qwen technical report. arXiv preprint       and J. Zhou.  Data-juicer sandbox: A feedback-driven suite
      arXiv:2309.16609, 2023.                                                   for multimodal data-model co-development.  arXiv preprint
[70]   S. Bai, K. Chen, X. Liu, et al.  Qwen2.5-vl technical report.         arXiv:2407.11784, 2024.
    CoRR, abs/2502.13923, 2025.                                        [92]  H. Chen, A. Waheed, X. Li, Y. Wang, J. Wang, B. Raj,
[71]  Y. Bai, A. Jones, K. Ndousse, A. Askell, A. Chen, N. DasSarma,        and M.  I. Abdin.  On the diversity of synthetic data and
     D. Drain, S. Fort, D. Ganguli, T. Henighan, et al. Training a           its impact on training large language models. arXiv preprint
      helpful and harmless assistant with reinforcement learning from         arXiv:2410.15226, 2024.
    human feedback. arXiv preprint arXiv:2204.05862, 2022.          [93]   J. Chen, Z. Chen, J. Wang, K. Zhou, Y. Zhu, J. Jiang, Y. Min,
[72]  M. I. L. Balaka, D. Alexander, Q. Wang, Y. Gong, A. Krisnadhi,      W. X. Zhao, Z. Dou, J. Mao, et al.  Towards effective and
     and R. C. Fernandez. Pneuma: Leveraging llms for tabular data           efficient continual pre-training of large language models. arXiv
      representation and retrieval in an end-to-end system.  arXiv         preprint arXiv:2407.18743, 2024.
      preprint arXiv:2504.09207, 2025.                                    [94]   J.  Chen,  S.  Xiao,  P.  Zhang,  K.  Luo,  D.  Lian,  and
[73]  A.  Barbaresi.    Trafilatura: A web  scraping  library and         Z. Liu.   M3-embedding: Multi-lingual,  multi-functionality,
     command-line tool for text discovery and extraction. In H. Ji,         multi-granularity text embeddings through self-knowledge disJ. C. Park, and R. Xia, editors, Proceedings of the 59th Annual           tillation. ACL, 2024.
     Meeting of the Association for Computational Linguistics and    [95]  M. Chen, J. Tworek, H. Jun, Q. Yuan, H. P. D. O. Pinto,
      the 11th International Joint Conference on Natural Language          J. Kaplan, H. Edwards, Y. Burda, N. Joseph, G. Brockman,
      Processing: System Demonstrations, pages 122–131, Online,          et al. Evaluating large language models trained on code. arXiv
     Aug. 2021. Association for Computational Linguistics.                  preprint arXiv:2107.03374, 2021.
                                                     48
[96]   S. Chen, J. Fan, B. Wu, N. Tang, C. Deng, P. Wang, Y. Li,   [116] H. Ding, Z. Wang, G. Paolini, V. Kumar, A. Deoras, D. Roth,
       J. Tan, F. Li, J. Zhou, and X. Du. Automatic database config-        and S. Soatto. Fewer truncations improve language modeling.
      uration debugging using retrieval-augmented language models.        arXiv preprint arXiv:2404.10830, 2024.
    CoRR, abs/2412.07548, 2024.                                      [117] N. Ding, Y. Chen, B. Xu, Y. Qin, Z. Zheng, S. Hu, Z. Liu,
[97]  T. Chen, H. Wang, S. Chen, W. Yu, K. Ma, X. Zhao, H. Zhang,       M. Sun, and B. Zhou.  Enhancing chat language models by
     and D. Yu. Dense x retrieval: What retrieval granularity should          scaling high-quality instructional conversations. arXiv preprint
     we use? arXiv preprint arXiv:2312.06648, 2023.                      arXiv:2305.14233, 2023.
[98]  Z. Chen, T. Liu, M. Tian, W. Luo, Z. Liu, et al. Advancing   [118] Y. Ding, Z. Wang, W. Ahmad, M. K. Ramanathan, R. Nalmathematical reasoning in language models: The impact of          lapati, P. Bhatia, D. Roth, and B. Xiang. CoCoMIC: Code
      problem-solving data, data synthesis methods, and training        Completion by Jointly Modeling In-file and Cross-file Context.
      stages. In The Thirteenth International Conference on Learn-         In N. Calzolari, M.-Y. Kan, V. Hoste, A. Lenci, S. Sakti,
      ing Representations, 2025.                                     and N. Xue, editors, Proceedings of the 2024 Joint Interna-
[99]  D. Cheng, Y. Gu, S. Huang, J. Bi, M. Huang, and F. Wei.          tional Conference on Computational Linguistics, Language ReInstruction pre-training: Language models are supervised mul-         sources and Evaluation (LREC-COLING 2024), pages 3433–
      titask learners. arXiv preprint arXiv:2406.14491, 2024.                3445, Torino, Italia, May 2024. ELRA and ICCL.
[100] S. Cheng, Z. Zhuang, Y. Xu, F. Yang, C. Zhang, X. Qin,   [119] Y. Ding, Q. Zeng, and T. Weninger. Chatel: Entity linking with
     X. Huang, L. Chen, Q. Lin, D. Zhang, S. Rajmohan, and         chatbots, 2024.
     Q. Zhang.  Call me when necessary: Llms can efficiently and   [120] J. Dodge, M. Sap, A. Marasovi´c, W. Agnew, G. Ilharco,
       faithfully reason over structured environments, 2024.                D. Groeneveld, M. Mitchell, and M. Gardner. Documenting
[101] X. Cheng, X. Wang, X. Zhang, T. Ge, S.-Q. Chen, F. Wei,          large webtext corpora: A case study on the colossal clean
     H. Zhang, and D. Zhao. xrag: Extreme context compression for         crawled corpus. arXiv preprint arXiv:2104.08758, 2021.
      retrieval-augmented generation with one token. arXiv preprint   [121] F. Dong, Y. He, Y. Liang, Z. Liu, Y. Wu, P. Chen, and T. Yang.
      arXiv:2405.13792, 2024.                                              Simisketch: Efficiently estimating similarity of streaming mul-
[102] A. Chevalier, A. Wettig, A. Ajith, and D. Chen.  Adapt-           tisets. arXiv preprint arXiv:2405.19711, 2024.
      ing language models to compress contexts.  arXiv preprint   [122] G. Dong, D. Pan, Y. Sun, S. Zhang, Z. Liang, X. Wu, Y. Shen,
      arXiv:2305.14788, 2023.                                            F. Yang, H. Sun, T. Li, et al.  Baichuanseed: Sharing the
[103] J. Choi, J. Yun, K. Jin, and Y. Kim.  Multi-news+: Cost-         potential of extensive data collection and deduplication by
       efficient dataset cleansing via llm-based data annotation.  In         introducing a competitive large language model baseline. arXiv
    EMNLP, pages 15–29. Association for Computational Linguis-         preprint arXiv:2408.15079, 2024.
       tics, 2024.                                                           [123] G. Dong, H. Yuan, K. Lu, C. Li, M. Xue, D. Liu, W. Wang,
[104] A. Chowdhery, S. Narang, J. Devlin, M. Bosma, G. Mishra,         Z. Yuan, C. Zhou, and J. Zhou. How abilities in large language
     A. Roberts, P. Barham, H. W. Chung, C. Sutton, S. Gehrmann,        models are affected by supervised fine-tuning data composition.
      P. Schuh, K. Shi, S. Tsvyashchenko,  J. Maynez, A. Rao,        arXiv preprint arXiv:2310.05492, 2023.
      P. Barnes, Y. Tay, N. Shazeer, V. Prabhakaran, E. Reif, N. Du,   [124] A. Dosovitskiy, L. Beyer, A. Kolesnikov, D. Weissenborn,
     B. Hutchinson, R. Pope, J. Bradbury, J. Austin, M. Isard,        X.  Zhai,  T.  Unterthiner,  M.  Dehghani,  M.  Minderer,
     G. Gur-Ari, P. Yin, T. Duke, A. Levskaya, S. Ghemawat,        G. Heigold, S. Gelly, J. Uszkoreit, and N. Houlsby. An image
      S. Dev, H. Michalewski, X. Garcia, V. Misra, K. Robinson,            is worth 16x16 words: Transformers for image recognition at
      L. Fedus, D. Zhou, D. Ippolito, D. Luan, H. Lim, B. Zoph,          scale, 2021.
     A. Spiridonov, R. Sepassi, D. Dohan, S. Agrawal, M. Omernick,   [125] M. Douze, A. Guzhva, C. Deng, J. Johnson, G. Szilvasy, P.-E.
     A. M. Dai, T. S. Pillai, M. Pellat, A. Lewkowycz, E. Moreira,         Mazar´e, M. Lomeli, L. Hosseini, and H. J´egou. The faiss library.
     R. Child, O. Polozov, K. Lee, Z. Zhou, X. Wang, B. Saeta,        arXiv preprint arXiv:2401.08281, 2024.
    M. Diaz, O. Firat, M. Catasta, J. Wei, K. Meier-Hellstern,   [126] Q. Du, C. Zong, and  J. Zhang.   Mods: Model-oriented
     D. Eck, J. Dean, S. Petrov, and N. Fiedel.  Palm: Scaling        data  selection  for  instruction  tuning.    arXiv  preprint
     language modeling with pathways, 2022.                             arXiv:2311.15653, 2023.
[105] M. Christ, S. Gunn, and O. Zamir. Undetectable watermarks   [127] D. Edge, H. Trinh, N. Cheng, J. Bradley, A. Chao, A. Mody,
       for language models. In The Thirty Seventh Annual Conference          S. Truitt, and J. Larson. From local to global: A graph rag
     on Learning Theory, pages 1125–1139. PMLR, 2024.                 approach to query-focused summarization.  arXiv preprint
[106] K. Cobbe, V. Kosaraju, M. Bavarian, M. Chen, H. Jun,         arXiv:2404.16130, 2024.
      L. Kaiser, M. Plappert, J. Tworek, J. Hilton, R. Nakano,   [128] M. Eibich, S. Nagpal, and A. Fred-Ojala. Aragog: Advanced
     C. Hesse, and J. Schulman.  Training verifiers to solve math         rag output grading. arXiv preprint arXiv:2404.01037, 2024.
     word problems. arXiv preprint arXiv:2110.14168, 2021.           [129] M. Y. Eltabakh, Z. A. Naeem, M. S. Ahmad, M. Ouzzani, and
[107] E. F. Codd. A relational model of data for large shared data        N. Tang. Retclean: Retrieval-based tabular data cleaning using
      banks. Commun. ACM, 13(6):377–387, June 1970.                     llms and data lakes. Proc. VLDB Endow., 17(12):4421–4424,
[108] B. Colson, P. Marcotte, and G. Savard. An overview of bilevel         2024.
      optimization. Annals of operations research, 153:235–256, 2007.   [130] L. Engstrom, A. Feldmann, and A. Madry.  Dsdm: Model-
[109] T. Computer. Redpajama: An open source recipe to reproduce        aware dataset selection with datamodels.   arXiv preprint
     llama training dataset, 2023.                                        arXiv:2401.12926, 2024.
[110] M. Conover, M. Hayes, A. Mathur, J. Xie, J. Wan, S. Shah,   [131] J. Fairoze, S. Garg, S. Jha, S. Mahloujifar, M. Mahmoody,
     A. Ghodsi, P. Wendell, M. Zaharia, and R. Xin.  Free dolly:        and M. Wang. Publicly detectable watermarking for language
      Introducing the world’s first truly open instruction-tuned llm,         models. arXiv preprint arXiv:2310.18491, 2023.
      2023.                                                                [132] C. Fan, Z. Pan, W. Sun, C. Yang, and W. Chen. Latuner: An
[111] A. Cossu, A. Carta, L. Passaro, V. Lomonaco, T. Tuytelaars,        llm-enhanced database tuning system based on adaptive surand D. Bacciu. Continual pre-training mitigates forgetting in         rogate model. In ECML/PKDD (5), volume 14945 of Lecture
     language and vision. Neural Networks, 179:106492, 2024.             Notes in Computer Science, pages 372–388. Springer, 2024.
[112] A. I. Cowen-Rivers, W. Lyu, Z. Wang, R. Tutunov, J. Hao,   [133] L. Fan, D. Krishnan, P. Isola, D. Katabi, and Y. Tian. ImprovJ. Wang, and H. Bou-Ammar. HEBO: heteroscedastic evolu-         ing clip training with language rewrites, 2023.
      tionary bayesian optimisation. CoRR, abs/2012.03826, 2020.     [134] M. Fan, X. Han, J. Fan, C. Chai, N. Tang, G. Li, and X. Du.
[113] G. Cui, L. Yuan, N. Ding, G. Yao, B. He, W. Zhu, Y. Ni, G. Xie,          Cost-effective in-context learning for entity resolution: A design
     R. Xie, Y. Lin, et al. Ultrafeedback: Boosting language models         space exploration. In ICDE, pages 3696–3709. IEEE, 2024.
     with scaled ai feedback. In Forty-first International Conference   [135] S.  Fan, M.  Pagliardini, and M.  Jaggi.   Doge: Domain
     on Machine Learning, 2024.                                          reweighting with generalization estimation.  arXiv preprint
[114] J. Cui, Z. Li, Y. Yan, B. Chen, and L. Yuan. Chatlaw: Open-         arXiv:2310.15393, 2023.
      source legal large language model with integrated external   [136] T. Fan, J. Wang, X. Ren, and C. Huang. Minirag: Towards exknowledge bases. CoRR, abs/2306.16092, 2023.                      tremely simple retrieval-augmented generation. arXiv preprint
[115] Y. Dai, D. Feng, J. Huang, H. Jia, Q. Xie, Y. Zhang, W. Han,         arXiv:2501.06713, 2025.
    W. Tian, and H. Wang. Laiw: A chinese legal large language   [137] M. Fayyaz, E. Aghazadeh, A. Modarressi, M. T. Pilehvar,
     models benchmark, 2024.                                       Y. Yaghoobzadeh, and S. E. Kahou.  Bert on a data diet:
                                                                      Finding important examples by gradient-based pruning. arXiv
                                                                             preprint arXiv:2211.05610, 2022.
                                                     49
[138] H. Feng, Q. Liu, H. Liu, J. Tang, W. Zhou, H. Li, and C. Huang.   [160] J. Gu, Z. Yang, C. Ding, R. Zhao, and F. Tan. Cmr scaling law:
     Docpedia: Unleashing the power of large multimodal model in         Predicting critical mixture ratios for continual pre-training of
      the frequency domain for versatile document understanding,        language models. arXiv preprint arXiv:2407.17467, 2024.
      2024.                                                                [161] R. Gu, K. Zhang, Z. Xu, Y. Che, B. Fan, H. Hou, H. Dai, L. Yi,
[139] S. Feng,  S. Prabhumoye, K. Kong, D. Su, M. Patwary,        Y. Ding, G. Chen, et al. Fluid: Dataset abstraction and elastic
    M. Shoeybi, and B. Catanzaro. Maximize your data’s potential:         acceleration for cloud-native deep learning training jobs.  In
     Enhancing llm accuracy with two-phase pretraining.  arXiv        2022 IEEE 38th International Conference on Data Engineering
      preprint arXiv:2412.15285, 2024.                                (ICDE), pages 2182–2195. IEEE, 2022.
[140] W. Feng, C. Hao, Y. Zhang, Y. Han, and H. Wang. Mixture-of-   [162] D. Guo, D. Yang, H. Zhang, J. Song, R. Zhang, R. Xu, Q. Zhu,
       loras: An efficient multitask tuning for large language models.          S. Ma, P. Wang, X. Bi, et  al.   Deepseek-r1: Incentivizing
     arXiv preprint arXiv:2403.03432, 2024.                               reasoning capability in llms via reinforcement learning. arXiv
[141] Z. Feng, D. Guo, D. Tang, N. Duan, X. Feng, M. Gong, L. Shou,         preprint arXiv:2501.12948, 2025.
     B. Qin, T. Liu, D. Jiang, and M. Zhou. Codebert: A pre-trained   [163] Y. Guo, Z. Hu, Y. Mao, B. Zheng, Y. Gao, and M. Zhou. Birdie:
     model for programming and natural languages, 2020.                 Natural language-driven table discovery using differentiable
[142] S. Ferr´e. First steps of an approach to the arc challenge based         search index, 2025.
     on descriptive grid models and the minimum description length   [164] Z. GUO, L. Xia, Y. Yu, T. Ao, and C. Huang.  LightRAG:
      principle. arXiv preprint arXiv:2112.00848, 2021.                    Simple and fast retrieval-augmented generation, 2024.
[143] B. Feuer, Y. Liu, C. Hegde, and J. Freire. Archetype: A novel   [165] V.  Gupta,  P.  Kandoi, M.  B.  Vora,  S.  Zhang,  Y.  He,
     framework for open-source column type annotation using large        R. Reinanda, and V. Srikumar. Temptabqa: Temporal question
     language models. Proc. VLDB Endow., 17(9):2279–2292, 2024.        answering for semi-structured tables, 2023.
[144] A. Finn, N. Kushmerick, and B. Smyth. Fact or fiction: Content   [166] W. L. Hamilton, R. Ying, and J. Leskovec.  Inductive repreclassification for digital libraries.  In DELOS Workshops /         sentation learning on large graphs. In Proceedings of the 31st
      Conferences, 2001.                                                    International Conference on Neural Information Processing
[145] M. Fuest, P. Ma, M. Gui, J. Schusterbauer, V. T. Hu, and         Systems, NIPS’17, page 1025–1035, Red Hook, NY, USA, 2017.
     B. Ommer.  Diffusion models and representation learning: A        Curran Associates Inc.
      survey, 2024.                                                        [167] N. He, W. Xiong, H. Liu, Y. Liao, L. Ding, K. Zhang, G. Tang,
[146] S. Y. Gadre, G. Ilharco, A. Fang, J. Hayase, G. Smyrnis,        X. Han, and W. Yang. Softdedup: an efficient data reweighting
     T. Nguyen, R. Marten, M. Wortsman, D. Ghosh, J. Zhang,       method for speeding up language model pre-training.  arXiv
      et al. Datacomp: In search of the next generation of multimodal         preprint arXiv:2407.06654, 2024.
      datasets. Advances in Neural Information Processing Systems,   [168] Y. He, Z. Wang, Z. Shen, G. Sun, Y. Dai, Y. Wu, H. Wang,
      36:27092–27112, 2023.                                        and A. Li. Shed: Shapley-based automated dataset refinement
[147] S. Gandhi, M. Zhao, A. Skiadopoulos, and C. Kozyrakis. Recy-          for instruction fine-tuning. arXiv preprint arXiv:2405.00705,
       cle: Resilient training of large dnns using pipeline adaptation.         2024.
      In Proceedings of the ACM SIGOPS 30th Symposium on Oper-   [169] D. Hernandez, T. Brown, T. Conerly, N. DasSarma, D. Drain,
      ating Systems Principles, pages 211–228, 2024.                          S. El-Showk, N. Elhage, Z. Hatfield-Dodds, T. Henighan,
[148] B. Gao, Z. He, P. Sharma, Q. Kang, D. Jevdjic, J. Deng,        T. Hume, et al.  Scaling laws and interpretability of learning
     X.  Yang,  Z.  Yu,  and  P.  Zuo.    {Cost-Efficient}  large        from repeated data. arXiv preprint arXiv:2205.10487, 2022.
     language model  serving  for multi-turn conversations with   [170] J. Hoffmann, S. Borgeaud, A. Mensch, E. Buchatskaya, T. Cai,
     {CachedAttention}. In 2024 USENIX Annual Technical Con-        E. Rutherford, D. de Las Casas, L. A. Hendricks, J. Welbl,
      ference (USENIX ATC 24), pages 111–126, 2024.                   A. Clark, T. Hennigan, E. Noland, K. Millican, G. van den
[149] L. Gao, S. Biderman, S. Black, L. Golding, T. Hoppe, C. Foster,         Driessche, B. Damoc, A. Guy, S. Osindero, K. Simonyan,
       J. Phang, H. He, A. Thite, N. Nabeshima, et al. The pile: An        E. Elsen, O. Vinyals, J. W. Rae, and L. Sifre. Training compute800gb dataset of diverse text for language modeling.  arXiv        optimal large language models.  In Proceedings of the 36th
      preprint arXiv:2101.00027, 2020.                                      International Conference on Neural Information Processing
[150] S. Gao, Y. Chen, and J. Shu.  Fast state restoration in llm         Systems, NIPS ’22, Red Hook, NY, USA, 2022. Curran Assoserving with hcache, 2024.                                                ciates Inc.
[151] S. Gao, C. Gao, Y. He, J. Zeng, L. Nie, X. Xia, and M. Lyu.   [171] S. Hong, Y. Lin, B. Liu, B. Liu, B. Wu, C. Zhang, C. Wei, D. Li,
     Code structure–guided transformer for source code summa-          J. Chen, J. Zhang, J. Wang, L. Zhang, L. Zhang, M. Yang,
       rization. ACM Transactions on Software Engineering and       M. Zhuge, T. Guo, T. Zhou, W. Tao, X. Tang, X. Lu, X. Zheng,
      Methodology, 32(1):1–32, Jan. 2023.                              X. Liang, Y. Fei, Y. Cheng, Z. Gou, Z. Xu, and C. Wu. Data
[152] C. Ge, Z. Ma, D. Chen, Y. Li, and B. Ding. Bimix: A bivariate          interpreter: An llm agent for data science, 2024.
     data mixing law for language model pretraining, 2025.             [172] M. J. Hosseini, Y. Gao, T. Baumg¨artner, A. Fabrikant, and
[153] Z. Ge, S. Liu, F. Wang, Z. Li, and J. Sun. Yolox: Exceeding yolo        R. K. Amplayo.   Scalable and domain-general abstractive
       series in 2021. arXiv preprint arXiv:2107.08430, 2021.                 proposition segmentation.  arXiv preprint arXiv:2406.19803,
[154] M. Geng, S. Wang, D. Dong, H. Wang, G. Li, Z. Jin, X. Mao,         2024.
     and X. Liao. Large language models are few-shot summarizers:   [173] Z. Hou, X. Lv, R. Lu, J. Zhang, Y. Li, Z. Yao, J. Li, J. Tang,
      Multi-intent comment generation via in-context learning, 2023.        and Y. Dong.  Advancing language model reasoning through
[155] V. Giannakouris and I. Trummer. DBG-PT: A large language         reinforcement learning and inference scaling.  arXiv preprint
     model assisted query performance regression debugger. Proc.         arXiv:2501.11651, 2025.
    VLDB Endow., 17(12):4337–4340, 2024.                           [174] A. Hu, H. Xu, J. Ye, M. Yan, L. Zhang, B. Zhang, C. Li,
[156] V. Giannankouris and  I. Trummer.    λ-tune: Harnessing          J. Zhang, Q. Jin, F. Huang, and J. Zhou. mplug-docowl 1.5:
      large language models for automated database system tuning.         Unified structure learning for ocr-free document understandCoRR, abs/2411.03500, 2024.                                             ing, 2024.
[157] S. Goyal, P. Maini, Z. C. Lipton, A. Raghunathan, and J. Z.   [175] H. Hua, Y. Tang, C. Xu, and J. Luo.  V2xum-llm: CrossKolter.  Scaling laws for data filtering–data curation cannot       modal video summarization with temporal prompt instruction
     be compute agnostic. In Proceedings of the IEEE/CVF Con-         tuning.  In Proceedings of the AAAI Conference on Artificial
      ference on Computer Vision and Pattern Recognition, pages          Intelligence, volume 39, pages 3599–3607, 2025.
     22702–22711, 2024.                                                 [176] J. Huang, D. Guo, C. Wang, J. Gu, S. Lu, J. P. Inala, C. Yan,
[158] D. Graur, D. Aymon, D. Kluser, T. Albrici, C. A. Thekkath,          J. Gao, N. Duan, and M. R. Lyu.   Contextualized dataand A. Klimovic. Cachew: Machine learning input data pro-        wrangling code generation in computational notebooks.  In
      cessing as a service. In 2022 usenix annual technical conference         Proceedings of the 39th IEEE/ACM International Conference
      (usenix atc 22), pages 689–706, 2022.                            on Automated Software Engineering, ASE ’24, page 1282–1294.
[159] D. Graur, O. Mraz, M. Li, S. Pourghannad, C. A. Thekkath,      ACM, Oct. 2024.
     and A. Klimovic.  Pecan:{Cost-Efficient}{ML} data prepro-   [177] X. Huang, H. Li, J. Zhang, X. Zhao, Z. Yao, Y. Li, Z. Yu,
      cessing with automatic transformation ordering and hybrid        T. Zhang, H. Chen, and C. Li.  E2etune: End-to-end knob
      placement.  In 2024 USENIX Annual Technical Conference         tuning via fine-tuned generative language model.  CoRR,
    (USENIX ATC 24), pages 649–665, 2024.                            abs/2404.11581, 2025.

                                                     50
[178] Y. Huang, X. Lin, Z. Liu, Q. Cao, H. Xin, H. Wang, Z. Li,   [200] D. Jung, Q. Liu, T. Huang, B. Zhou, and M. Chen. FamiliarityL. Song, and X. Liang. Mustard: Mastering uniform synthesis        aware evidence compression for retrieval augmented generaof theorem and proof data. arXiv preprint arXiv:2402.08957,          tion. arXiv preprint arXiv:2409.12468, 2024.
      2024.                                                                [201] J. Kaplan, S. McCandlish, T. Henighan, T. B. Brown, B. Chess,
[179] Y. Huang, X. Liu, Y. Gong, Z. Gou, Y. Shen, N. Duan,        R. Child,  S. Gray, A. Radford,  J. Wu, and D. Amodei.
     and W. Chen.   Key-point-driven data synthesis with  its         Scaling laws  for neural language models.   arXiv preprint
     enhancement on mathematical reasoning.   arXiv preprint         arXiv:2001.08361, 2020.
      arXiv:2403.02333, 2024.                                            [202] A. Kay. Tesseract: an open-source optical character recognition
[180] Y. Huang, T. Lv, L. Cui, Y. Lu, and F. Wei. Layoutlmv3: Pre-         engine. Linux J., 2007(159):2, July 2007.
      training for document ai with unified text and image masking,   [203] M. Kayali, A. Lykov, I. Fountalis, N. Vasiloglou, D. Olteanu,
      2022.                                                      and D. Suciu. CHORUS: foundation models for unified data
[181] H.  Husain,  H.-H.  Wu,  T.  Gazit,  M.  Allamanis,  and         discovery and exploration. Proc. VLDB Endow., 17(8):2104–
    M.  Brockschmidt.    CodeSearchNet  challenge:  Evaluat-         2114, 2024.
      ing  the  state  of semantic code  search.   arXiv  preprint   [204] M. Kayali, F. Wenz, N. Tatbul, and C¸. Demiralp. Mind the
      arXiv:1909.09436, 2019.                                          data gap: Bridging llms to enterprise data integration.  In
[182] G. Ilharco, M. Wortsman, N. Carlini, R. Taori, A. Dave,         Proceedings of the 2025 Conference on Innovative Data Systems
     V. Shankar, H. Namkoong, J. Miller, H. Hajishirzi, A. Farhadi,        Research (CIDR), Chaminade, California, 2025. CIDR 2025.
     and L. Schmidt. Openclip, July 2021.                              [205] G. Ke, Q. Meng, T. Finley, T. Wang, W. Chen, W. Ma, Q. Ye,
[183]  I. Ilyankou, M. Wang, S. Cavazzi, and J. Haworth. Cc-gpx: Ex-        and T.-Y. Liu. Lightgbm: A highly efficient gradient boosting
      tracting high-quality annotated geospatial data from common         decision tree. Advances in neural information processing syscrawl, 2024.                                                        tems, 30, 2017.
[184] A. Ilyas, S. M. Park, L. Engstrom, G. Leclerc, and A. Madry.   [206] J. D. M.-W. C. Kenton and L. K. Toutanova. Bert: Pre-training
     Datamodels: Predicting predictions from training data. arXiv          of deep bidirectional transformers for language understanding.
      preprint arXiv:2202.00622, 2022.                                     In Proceedings of naacL-HLT, volume 1, page 2. Minneapolis,
[185] K. Islam, M. Z. Zaheer, A. Mahmood, and K. Nandakumar.        Minnesota, 2019.
      Diffusemix: Label-preserving data augmentation with diffusion   [207] A. Khan, R. Underwood, C. Siebenschuh, Y. Babuji, A. Ajith,
      models, 2024.                                                K. Hippe, O. Gokdemir, A. Brace, K. Chard, and I. Foster.
[186]  I. Jang, Z. Yang, Z. Zhang, X. Jin, and M. Chowdhury. Oobleck:        Lshbloom: Memory-efficient, extreme-scale document dedupliResilient distributed training of large models using pipeline          cation. arXiv preprint arXiv:2411.04257, 2024.
      templates. In Proceedings of the 29th Symposium on Operating   [208] M. A. M. Khan, M. S. Bari, X. L. Do, W. Wang, M. R. Parvez,
     Systems Principles, pages 382–395, 2023.                         and S. Joty.  xcodeeval: A large scale multilingual multitask
[187] Z. Ji, N. Lee, R. Frieske, T. Yu, D. Su, Y. Xu, E. Ishii, Y. J.        benchmark for code understanding, generation, translation and
     Bang, A. Madotto, and P. Fung.  Survey of hallucination          retrieval, 2023.
      in natural language generation. ACM Computing Surveys,   [209] D. Kim, B. Kim, D. Han, and M. Eibich. Autorag: Automated
      55(12):1–38, 2023.                                              framework for optimization of retrieval augmented generation
[188] A. Q. Jiang, A. Sablayrolles, A. Mensch, C. Bamford, D. S.          pipeline, 2024.
      Chaplot, D. de las Casas, F. Bressand, G. Lengyel, G. Lample,   [210] J. Kim and J. Lee. Strategic data ordering: Enhancing large lanL. Saulnier, L. R. Lavaud, M.-A. Lachaux, P. Stock, T. L. Scao,        guage model performance through curriculum learning. arXiv
     T. Lavril, T. Wang, T. Lacroix, and W. E. Sayed. Mistral 7b,         preprint arXiv:2405.07490, 2024.
      2023.                                                                [211] T. N. Kipf and M. Welling. Semi-supervised classification with
[189] H. Jiang, Q. Wu, C.-Y. Lin, Y. Yang, and L. Qiu.  Llmlin-        graph convolutional networks.  In Proceedings of the 5th Ingua: Compressing prompts for accelerated inference of large         ternational Conference on Learning Representations (ICLR),
     language models. arXiv preprint arXiv:2310.05736, 2023.              2017. Published as a conference paper at ICLR 2017.
[190] H. Jiang, Q. Wu, X. Luo, D. Li, C.-Y. Lin, Y. Yang, and   [212] J. Kirchenbauer, J. Geiping, Y. Wen, J. Katz, I. Miers, and
      L. Qiu.  Longllmlingua: Accelerating and enhancing llms in        T. Goldstein. A watermark for large language models.  In
      long context scenarios via prompt compression. arXiv preprint         International Conference on Machine Learning, pages 17061–
      arXiv:2310.06839, 2023.                                            17084. PMLR, 2023.
[191] J. Jiang, F. Wang, J. Shen, S. Kim, and S. Kim. A survey   [213] S. Kirkpatrick, C. D. Gelatt Jr, and M. P. Vecchi. Optimization
     on large language models for code generation. arXiv preprint        by simulated annealing. science, 220(4598):671–680, 1983.
      arXiv:2406.00515, 2024.                                            [214] D. Kocetkov, R. Li, L. Ben Allal, J. Li, C. Mou, C. Mu˜noz Fer-
[192] J. Jiang, K. Zhou, Z. Dong, K. Ye, W. X. Zhao, and J.-R. Wen.          randis, Y. Jernite, M. Mitchell, S. Hughes, T. Wolf, D. BahStructgpt: A general framework for large language model to        danau, L. von Werra, and H. de Vries.  The stack: 3 tb of
      reason over structured data, 2023.                                     permissively licensed source code. Preprint, 2022.
[193] J. Jiang, K. Zhou, W. X. Zhao, and J.-R. Wen.  Unikgqa:   [215] K. Kolluru, M. Mohammed, S. Mittal, S. Chakrabarti, et al.
      Unified retrieval and reasoning for solving multi-hop question        Alignment-augmented consistent translation for multilingual
     answering over knowledge graph, 2023.                            open information extraction.  In Proceedings of the 60th An-
[194] Z. Jiang, H. Lin, Y. Zhong, Q. Huang, Y. Chen, Z. Zhang,         nual Meeting of the Association for Computational Linguistics
     Y. Peng, X. Li, C. Xie, S. Nong, et al. {MegaScale}: Scaling        (Volume 1: Long Papers), pages 2502–2517, 2022.
      large language model training to more than 10,000 {GPUs}. In   [216] W. Kong, Q. Tian, Z. Zhang, R. Min, Z. Dai, J. Zhou, J. Xiong,
      21st USENIX Symposium on Networked Systems Design and        X. Li, B. Wu, J. Zhang, et al.  Hunyuanvideo: A systematic
     Implementation (NSDI 24), pages 745–760, 2024.                   framework for large video generative models.  arXiv preprint
[195] X. Jiao, Y. Yin, L. Shang, X. Jiang, X. Chen, L. Li, F. Wang,         arXiv:2412.03603, 2024.
     and Q. Liu.  Tinybert: Distilling bert for natural language   [217] K. Korini and C. Bizer. Evaluating knowledge generation and
      understanding. arXiv preprint arXiv:1909.10351, 2019.                 self-refinement strategies for llm-based column type annota-
[196] R. L. J. X. Y. C. P. H. C. H. M. D. Z. Jie Tan, Kangfei Zhao          tion. CoRR, abs/2503.02718, 2025.
     and Y. Rong. Can large language models be query optimizer   [218] M. M. Krell, M. Kosec, S. P. Perez, and A. Fitzgibbon. Efficient
       for relational databases? CoRR, abs/2502.05562, 2025.               sequence packing without cross-contamination: Accelerating
[197] C. Jin, Z. Zhang, X. Jiang, F. Liu, X. Liu, X. Liu, and X. Jin.          large language models without impacting performance. arXiv
     Ragcache: Efficient knowledge caching for retrieval-augmented         preprint arXiv:2107.02027, 2021.
      generation. arXiv preprint arXiv:2404.12457, 2024.               [219] A. V. Kumar and M. Sivathanu. Quiver: An informed storage
[198] D. Jin, E. Pan, N. Oufattole, W.-H. Weng, H. Fang, and         cache for deep learning. In 18th USENIX Conference on File
      P. Szolovits. What disease does this patient have? a large-scale        and Storage Technologies (FAST 20), pages 283–296, 2020.
     open domain question answering dataset from medical exams.   [220] W. Kwon, Z. Li, S. Zhuang, Y. Sheng, L. Zheng, C. H. Yu,
      Applied Sciences, 11(14):6421, 2021.                                       J. E. Gonzalez, H. Zhang, and I. Stoica. Efficient memory man-
[199] A. Joulin, E. Grave, P. Bojanowski, and T. Mikolov.  Bag        agement for large language model serving with pagedattention,
      of  tricks  for  efficient  text  classification.   arXiv  preprint         2023.
      arXiv:1607.01759, 2016.                                            [221] J. Lai, W. Gan, J. Wu, Z. Qi, and P. S. Yu. Large language
                                                                   models in law: A survey. AI Open, 2024.
                                                     51
[222] Z. Lai, H. Zhang, B. Zhang, W. Wu, H. Bai, A. Timofeev, X. Du,   [242] X. Li, Z. Wu, J. Wu, H. Cui, J. Jia, R.-H. Li, and G. Wang.
      Z. Gan, J. Shan, C.-N. Chuah, Y. Yang, and M. Cao. Veclip:       Graph learning in the era of llms: A survey from the perspective
     Improving clip training via visual-enriched captions, 2024.               of data, models, and tasks, 2024.
[223] J. Lao, Y. Wang, Y. Li, J. Wang, Y. Zhang, Z. Cheng, W. Chen,   [243] Y. Li, H. Li, P. Zhao, J. Zhang, X. Zhang, T. Ji, L. Sun, C. Li,
    M. Tang, and J. Wang. Gptuner: A manual-reading database        and H. Chen. Is large language model good at database knob
      tuning system via gpt-guided bayesian optimization.  Proc.         tuning? A comprehensive experimental evaluation.  CoRR,
    VLDB Endow., 17(8):1939–1952, 2024.                               abs/2408.02213, 2024.
[224] H. Lauren¸con, L. Saulnier, L. Tronchon, S. Bekman, A. Singh,   [244] Y. LI, G. Zhang, X. Qu, J. Li, Z. Li, Z. Wang, H. Li, R. Yuan,
     A. Lozhkov, T. Wang, S. Karamcheti, A. Rush, D. Kiela,        Y. Ma, K. Zhang, W. Zhou, Y. Liang, L. Zhang, L. Ma,
      et al. Obelics: An open web-scale filtered dataset of interleaved          J. Zhang, Z. Li, S. W. Huang, C. Lin, and J. Fu.  Cif-bench:
      image-text documents. Advances in Neural Information Pro-     A chinese instruction-following benchmark for evaluating the
      cessing Systems, 36, 2024.                                                generalizability of large language models, 2024.
[225] K. Lee, M. Joshi,  I. Turc, H. Hu, F. Liu, J. Eisenschlos,   [245] Z. Li, Y. Du, M. Zheng, and M. Song. Mimotable: A multiU. Khandelwal, P. Shaw, M.-W. Chang, and K. Toutanova.          scale spreadsheet benchmark with meta operations for table
      Pix2struct: Screenshot parsing as pretraining for visual lan-         reasoning, 2024.
     guage understanding, 2023.                                        [246] Z. Li, S. Fan, Y. Gu, X. Li, Z. Duan, B. Dong, N. Liu, and
[226] F. Lei, X. Li, Y. Wei, S. He, Y. Huang, J. Zhao, and K. Liu.          J. Wang. Flexkbqa: A flexible llm-powered framework for fewS3HQA: A three-stage approach for multi-hop text-table hy-         shot knowledge base question answering, 2024.
      brid question answering.  In A. Rogers, J. Boyd-Graber, and   [247] Z. Li, X. Wang, J. Zhao, S. Yang, G. Du, X. Hu, B. Zhang,
     N. Okazaki, editors, Proceedings of the 61st Annual Meeting        Y. Ye, Z. Li, R. Zhao, and H. Mao. Pet-sql: A prompt-enhanced
      of the Association for Computational Linguistics (Volume 2:        two-round refinement  of  text-to-sql with  cross-consistency,
      Short Papers), pages 1731–1740, Toronto, Canada, July 2023.        June 2024.
      Association for Computational Linguistics.                        [248] Z. Li, H. Yuan, H. Wang, G. Cong, and L. Bing. LLM-R2: A
[227] Y. Leviathan, M. Kalman, and Y. Matias. Fast inference from          large language model enhanced rule-based rewrite system for
      transformers via speculative decoding. In ICML, volume 202 of         boosting query efficiency.  Proc. VLDB Endow., 18(1):53–65,
      Proceedings of Machine Learning Research, pages 19274–19286.         2024.
    PMLR, 2023.                                                       [249] Z. Li, X. Zhang, Y. Zhang, D. Long, P. Xie, and M. Zhang.
[228] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin,        Towards general text embeddings with multi-stage contrastive
     N. Goyal, H. K¨uttler, M. Lewis, W.-t. Yih, T. Rockt¨aschel,          learning. arXiv preprint arXiv:2308.03281, 2023.
      et al. Retrieval-augmented generation for knowledge-intensive   [250] J. Lian, X. Liu, Y. Shao, et  al.   Chatbi: Towards natunlp tasks. Advances in Neural Information Processing Systems,          ral language to complex business intelligence SQL.  CoRR,
      33:9459–9474, 2020.                                                abs/2405.00527, 2024.
[229] B. Li, Y. Luo, C. Chai, G. Li, and N. Tang. The dawn of natural   [251] H. Liang, K. Zhao, Y. Yang, B. Cui, G. Dong, Z. Zhou,
     language to sql: Are we fully ready? Proceedings of the VLDB       and W. Zhang.  Data proportion detection for optimized
     Endowment, 17(11):3318–3331, July 2024.                          data management for large language models.  arXiv preprint
[230] D. Li, S. Cao, T. Griggs, S. Liu, X. Mo, S. G. Patil, M. Zaharia,         arXiv:2409.17527, 2024.
       J. E. Gonzalez, and I. Stoica. Llms can easily learn to reason   [252] Y. Liang, T. Xie, G. Peng, Z. Huang, Y. Lan, and W. Qian. Natfrom demonstrations structure, not content, is what matters!          nl2gql: A novel multi-agent framework for translating natural
     arXiv preprint arXiv:2502.07374, 2025.                             language to graph query language, 2024.
[231] G. Li, X. Zhou, S. Li, and B. Gao.  Qtune: A query-aware   [253] H. Lightman, V. Kosaraju, Y. Burda, H. Edwards, B. Baker,
     database tuning system with deep reinforcement learning.        T. Lee, J. Leike, J. Schulman, I. Sutskever, and K. Cobbe. Let’s
      Proc. VLDB Endow., 12(12):2118–2130, 2019.                           verify step by step. arXiv preprint arXiv:2305.20050, 2023.
[232] H. Li, Y. Chen, Q. Ai, Y. Wu, R. Zhang, and Y. Liu. Lexeval:   [254] X. Lin, W. Wang, Y. Li, S. Yang, F. Feng, Y. Wei, and T.-
   A comprehensive chinese legal benchmark for evaluating large          S. Chua.  Data-efficient fine-tuning for llm-based recommenlanguage models. arXiv preprint arXiv:2409.20288, 2024.              dation. In Proceedings of the 47th International ACM SIGIR
[233] H. Li, Q. Dong, Z. Tang, C. Wang, X. Zhang, H. Huang,        Conference on Research and Development in Information ReS. Huang, X. Huang, Z. Huang, D. Zhang, et al.  Synthetic           trieval, pages 365–374, 2024.
     data (almost) from scratch: Generalized instruction tuning for   [255] A. Liu, J. Liu, Z. Pan, Y. He, R. Haffari, and B. Zhuang.
     language models. arXiv preprint arXiv:2402.13064, 2024.             Minicache: Kv cache compression in depth dimension for large
[234] H. Li, J. Zhang, H. Liu, J. Fan, X. Zhang, J. Zhu, R. Wei,        language models. Advances in Neural Information Processing
     H. Pan, C. Li, and H. Chen. Codes: Towards building open-         Systems, 37:139997–140031, 2024.
      source language models for text-to-sql, 2024.                       [256] A. Liu, L. Pan, X. Hu, S. Li, L. Wen, I. King, and S. Y. Philip.
[235] J. LI, E. Beeching, L. Tunstall, B. Lipkin, R. Soletskyi, S. C.      An unforgeable publicly verifiable watermark for large language
     Huang, K. Rasul, L. Yu, A. Jiang, Z. Shen, Z. Qin, B. Dong,         models. In The Twelfth International Conference on Learning
      L. Zhou, Y. Fleureau, G. Lample, and S. Polu. Numinamath.         Representations, 2023.
     [https://huggingface.co/AI-MO/NuminaMath-CoT](https:       [257] C. Liu, H. Wei, J. Chen, L. Kong, Z. Ge, Z. Zhu, L. Zhao, J. Sun,
      //github.com/project-numina/aimo-progress-prize/blob/            C. Han, and X. Zhang. Focus anywhere for fine-grained multimain/report/numina  dataset.pdf), 2024.                          page document understanding, 2024.
[236] J. Li, A. Fang, G. Smyrnis, M. Ivgi, M. Jordan, S. Gadre,   [258] H. Liu, C. Li, Y. Li, and Y. J. Lee. Improved baselines with
     H. Bansal, E. Guha, S. Keh, K. Arora, et al. Datacomp-lm:          visual instruction tuning, 2024.
      In search of the next generation of training sets for language   [259] H. Liu, Q. Peng, Q. Yang, K. Liu, and H. Xu.  Bucket premodels. arXiv preprint arXiv:2406.11794, 2024.                        training is all you need. arXiv preprint arXiv:2407.07495, 2024.
[237] L. Li, L. Fang, and V.  I. Torvik.   Autodcworkflow: Llm-   [260] H. Liu, Y. Zhang, Y. Luo, and A. C.-C. Yao. Augmenting math
     based data cleaning workflow auto-generation and benchmark.        word problems via iterative question composing. arXiv preprint
    CoRR, abs/2412.06724, 2024.                                       arXiv:2401.09003, 2024.
[238] M. Li, Y. Zhang, S. He, Z. Li, H. Zhao, J. Wang, N. Cheng, and   [261] J. Liu and B. Mozafari.  Query rewriting via large language
     T. Zhou. Superfiltering: Weak-to-strong data filtering for fast         models. CoRR, abs/2403.09060, 2024.
      instruction-tuning. arXiv preprint arXiv:2402.00530, 2024.       [262] J. Liu, K. Wang, Y. Chen, X. Peng, Z. Chen, L. Zhang, and
[239] M. Li, Y. Zhang, Z. Li, J. Chen, L. Chen, N. Cheng, J. Wang,        Y. Lou. Large language model-based agents for software engiT. Zhou, and J. Xiao.  From quantity to quality: Boosting         neering: A survey, 2024.
      llm performance with self-guided data selection for instruction   [263] Q. Liu, X. Zheng, N. Muennighoff, G. Zeng, L. Dou, T. Pang,
      tuning. arXiv preprint arXiv:2308.12032, 2023.                           J. Jiang, and M. Lin. Regmix: Data mixture as regression for
[240] P. Li, Y. He, D. Yashar, W. Cui, S. Ge, H. Zhang, D. R.        language model pre-training. arXiv preprint arXiv:2407.01492,
     Fainman, D. Zhang, and S. Chaudhuri. Table-gpt: Table-tuned         2024.
     gpt for diverse table tasks, 2023.                                   [264] W. Liu, W. Zeng, K. He, Y. Jiang, and J. He. What makes
[241] S. Li, X. Ning, L. Wang, T. Liu, X. Shi, S. Yan, G. Dai, H. Yang,        good data for alignment? a comprehensive study of autoand Y. Wang. Evaluating quantized large language models. In        matic data selection in instruction tuning.  arXiv preprint
    ICML. OpenReview.net, 2024.                                      arXiv:2312.15685, 2023.
                                                     52
[265] Y. Liu, H. Li, Y. Cheng, S. Ray, Y. Huang, Q. Zhang, K. Du,        pus and neocortex: insights from the successes and failures of
       J. Yao, S. Lu, G. Ananthanarayanan, et al. Cachegen: Kv cache         connectionist models of learning and memory.  Psychological
     compression and streaming for fast large language model serv-         review, 102(3):419, 1995.
      ing. In Proceedings of the ACM SIGCOMM 2024 Conference,   [287] M. McCloskey and N. J. Cohen. Catastrophic interference in
     pages 38–56, 2024.                                                    connectionist networks: The sequential learning problem.  In
[266] Y. Liu, M. Ott, N. Goyal, J. Du, M. Joshi, D. Chen, O. Levy,        Psychology of learning and motivation, volume 24, pages 109–
    M. Lewis, L. Zettlemoyer, and V. Stoyanov.  Roberta: A ro-         165. Elsevier, 1989.
      bustly optimized bert pretraining approach, 2019.                 [288] D. Mekala, A. Nguyen, and J. Shang. Smaller language models
[267] Y. Liu, E. Pe˜na, A. S. R. Santos, E. Wu, and J. Freire. Mag-         are capable of selecting instruction-tuning training data for
      neto: Combining small and large language models for schema          larger language models.  arXiv preprint arXiv:2402.10430,
     matching. CoRR, abs/2412.08194, 2024.                              2024.
[268] Z. Liu, Y. Huang, X. Yu, L. Zhang, Z. Wu, C. Cao, H. Dai,   [289] S. Minaee, T. Mikolov, N. Nikzad, M. Chenaghlu, R. Socher,
      L. Zhao, Y. Li, P. Shu, et al. Deid-gpt: Zero-shot medical text        X. Amatriain, and J. Gao. Large language models: A survey.
      de-identification by gpt-4.  arXiv preprint arXiv:2303.11032,        arXiv preprint arXiv:2402.06196, 2024.
      2023.                                                                [290] A. Mitra, L. Del Corro, G. Zheng, S. Mahajan, D. Rouhana,
[269] Z. Liu, A. Karbasi, and T. Rekatsinas.   Tsds: Data  se-        A. Codas, Y. Lu, W.-g. Chen, O. Vrousgos, C. Rosset, et al.
      lection  for task-specific model finetuning.   arXiv preprint         Agentinstruct: Toward generative teaching with agentic flows.
      arXiv:2410.11303, 2024.                                          arXiv preprint arXiv:2407.03502, 2024.
[270] Z. Liu, Q. Liao, W. Gu, and C. Gao.  Software vulnerability   [291] J. Mohan, A. Phanishayee, and V. Chidambaram. CheckFreq:
      detection with gpt and in-context learning.  In 2023 8th In-         Frequent, Fine-Grained DNN checkpointing. In 19th USENIX
      ternational Conference on Data Science in Cyberspace (DSC),        Conference on File and Storage Technologies (FAST 21), pages
     pages 229–236, 2023.                                               203–216. USENIX Association, Feb. 2021.
[271] Z. Liu, Z. Tang, J. Zhang, X. Xia, and X. Yang. Pre-training   [292] J. Monteiro, F. S´a, and J. Bernardino. Graph databases asby predicting program dependencies for vulnerability analysis         sessment: Janusgraph, neo4j, and tigergraph. In Perspectives
      tasks, 2024.                                                 and Trends in Education and Technology: Selected Papers from
[272] L. Long, R. Wang, R. Xiao, J. Zhao, X. Ding, G. Chen, and       ICITED 2022, pages 655–665. Springer, 2023.
     H. Wang. On llms-driven synthetic data generation, curation,   [293] J. Mu, X. Li, and N. Goodman. Learning to compress prompts
     and evaluation: A survey.  arXiv preprint arXiv:2406.15126,        with gist tokens. Advances in Neural Information Processing
      2024.                                                             Systems, 36, 2024.
[273] D. Lu, H. Wu, J. Liang, Y. Xu, Q. He, Y. Geng, M. Han,   [294] N. Muennighoff, Q. Liu, A. Zebaze, Q. Zheng, B. Hui, T. Y.
     Y. Xin, and Y. Xiao. Bbt-fin: Comprehensive construction of        Zhuo, S. Singh, X. Tang, L. von Werra, and S. Longpre. Occhinese financial domain pre-trained language model, corpus         topack: Instruction tuning code large language models, 2024.
     and benchmark. arXiv preprint arXiv:2302.09432, 2023.          [295] C. Na, I. Magnusson, A. H. Jha, T. Sherborne, E. Strubell,
[274] W. Lu, J. Zhang, J. Fan, Z. Fu, Y. Chen, and X. Du. Large          J. Dodge, and P. Dasigi. Scalable data ablation approximations
     language model for table processing: A survey.  Frontiers of          for language models through modular training and merging.
     Computer Science, 19(2):192350, 2025.                             arXiv preprint arXiv:2410.15661, 2024.
[275] N. Lukas, A. Salem, R. Sim, S. Tople, L. Wutschitz, and   [296] R. Navigli, S. Conia, and B. Ross.  Biases in large language
      S. Zanella-B´eguelin. Analyzing leakage of personally identifi-         models: origins, inventory, and discussion. ACM Journal of
      able information in language models. In 2023 IEEE Symposium        Data and Information Quality, 15(2):1–21, 2023.
     on Security and Privacy (SP), pages 346–363. IEEE, 2023.        [297] T. Nguyen, C. V. Nguyen, V. D. Lai, H. Man, N. T. Ngo,
[276] Z. Luo, X. Zhang, X. Liu, H.  Li, Y. Gong, C. Qi, and         F. Dernoncourt, R. A. Rossi, and T. H. Nguyen. CulturaX: A
      P. Cheng.   Velocitune: A velocity-based dynamic domain         cleaned, enormous, and multilingual dataset for large language
      reweighting method for continual pre-training. arXiv preprint        models in 167 languages. In N. Calzolari, M.-Y. Kan, V. Hoste,
      arXiv:2411.14318, 2024.                                        A. Lenci, S. Sakti, and N. Xue, editors, Proceedings of the 2024
[277] C. Ma, S. Chakrabarti, A. Khan, and B. Moln´ar. Knowledge         Joint International Conference on Computational Linguistics,
     graph-based retrieval-augmented generation for schema match-        Language Resources and Evaluation (LREC-COLING 2024),
      ing. CoRR, abs/2501.08686, 2025.                                  pages 4226–4237, Torino, Italia, May 2024. ELRA and ICCL.
[278] G. Ma, Y. Ma, X. Wu, Z. Su, M. Zhou, and S. Hu. Task-level   [298]  I. Nunes, M. Heddes, P. Verg´es, D. Abraham, A. Veidenbaum,
      distributionally robust optimization for large language model-        A. Nicolau, and T. Givargis. Dothash: Estimating set similarity
     based dense retrieval. arXiv preprint arXiv:2408.10613, 2024.          metrics for link prediction and document deduplication. In Pro-
[279] L. Ma, N. Thakurdesai, J. Chen, J. Xu, E. K¨orpeoglu, S. Ku-         ceedings of the 29th ACM SIGKDD Conference on Knowledge
     mar, and K. Achan. Llms with user-defined prompts as generic         Discovery and Data Mining, pages 1758–1769, 2023.
     data operators for reliable data processing. In IEEE Big Data,   [299] A. Nystrom, C. Zhang, C. Callison-Burch, D. Ippolito, D. Eck,
     pages 3144–3148. IEEE, 2023.                                  K. Lee, and N. Carlini.  Deduplicating training data makes
[280] Y. Ma, Y. Cao, Y. Hong, and A. Sun. Large language model        language models better. 2022.
        is not a good few-shot information extractor, but a good   [300] M. Oquab, T. Darcet, T. Moutakanni, H. Vo, M. Szafraniec,
      reranker for hard samples!  In Findings of the Association        V. Khalidov, P. Fernandez, D. Haziza, F. Massa, A. El-Nouby,
      for Computational Linguistics: EMNLP 2023. Association for          et al. Dinov2: Learning robust visual features without superviComputational Linguistics, 2023.                                          sion. arXiv preprint arXiv:2304.07193, 2023.
[281] Z. Ma, B. Zhang, J. Zhang, J. Yu, X. Zhang, X. Zhang, S. Luo,   [301] L. Ouyang, J. Wu, X. Jiang, D. Almeida, C. Wainwright,
     X. Wang, and J. Tang. Spreadsheetbench: Towards challenging         P. Mishkin, C. Zhang, S. Agarwal, K. Slama, A. Ray, et al.
      real world spreadsheet manipulation, 2024.                           Training language models to follow instructions with human
[282] P. Maini, S. Seto, H. Bai, D. Grangier, Y. Zhang, and N. Jaitly.         feedback. Advances in neural information processing systems,
     Rephrasing the web: A recipe for compute and data-efficient         35:27730–27744, 2022.
     language modeling. arXiv preprint arXiv:2401.16380, 2024.      [302] R. Pan, J. Zhang, X. Pan, R. Pi, X. Wang, and T. Zhang.
[283] U. Manber and G. Myers. Suffix arrays: a new method for on-         Scalebio: Scalable bilevel optimization for llm data reweighting.
       line string searches. siam Journal on Computing, 22(5):935–        arXiv preprint arXiv:2406.19976, 2024.
      948, 1993.                                                           [303] Z. Pan, Q. Wu, H. Jiang, M. Xia, X. Luo, J. Zhang, Q. Lin,
[284] Y. Mao, X. Li, W. Li, X. Wang, and L. Xie. Scla: Automated        V. R¨uhle, Y. Yang, C.-Y. Lin, et al. Llmlingua-2: Data distillasmart contract summarization via llms and semantic augmen-         tion for efficient and faithful task-agnostic prompt compression.
      tation, 2024.                                                    arXiv preprint arXiv:2403.12968, 2024.
[285] M. Marion, A. ¨Ust¨un, L. Pozzobon, A. Wang, M. Fadaee, and   [304] M. Parciak, B. Vandevoort, F. Neven, L. M. Peeters, and
      S. Hooker. When less is more: Investigating data pruning for          S. Vansummeren. Schema matching with large language modpretraining llms at scale.  arXiv preprint arXiv:2309.04564,            els: an experimental study. In VLDB Workshops. VLDB.org,
      2023.                                                               2024.
[286] J. L. McClelland, B. L. McNaughton, and R. C. O’Reilly. Why   [305] H. Park, S. Lee, G. Gim, Y. Kim, D. Kim, and C. Park.
      there are complementary learning systems in the hippocam-         Dataverse: Open-source etl (extract, transform, load) pipeline
                                                                                     for large language models. arXiv preprint arXiv:2403.19340,
                                                                          2024.
                                                     53
[306] S. Patnaik, H. Changwal, M. Aggarwal, S. Bhatia, Y. Kumar,   [327] A. Radford, J. Wu, R. Child, D. Luan, D. Amodei, I. Sutskever,
     and B. Krishnamurthy. Cabinet: Content relevance based noise          et al. Language models are unsupervised multitask learners.
      reduction for table question answering, 2024.                     OpenAI blog, 1(8):9, 2019.
[307] D. A. Patterson, G. Gibson, and R. H. Katz. A case for redun-   [328] J. W. Rae, S. Borgeaud, T. Cai, K. Millican, J. Hoffmann,
     dant arrays of inexpensive disks (raid). In Proceedings of the         F. Song, J. Aslanides, S. Henderson, R. Ring, S. Young, et al.
     1988 ACM SIGMOD international conference on Management         Scaling language models: Methods, analysis & insights from
      of data, pages 109–116, 1988.                                           training gopher. arXiv preprint arXiv:2112.11446, 2021.
[308] R. Peeters, A. Steiner, and C. Bizer.  Entity matching using   [329] R. Rafailov, A. Sharma, E. Mitchell, S. Ermon, C. D. Manning,
      large language models.  In EDBT, pages 529–541. OpenPro-        and C. Finn.  Direct preference optimization: Your language
      ceedings.org, 2025.                                            model is secretly a reward model, 2024.
[309] Q. Pei, L. Wu, K. Gao, J. Zhu, Y. Wang, Z. Wang, T. Qin, and   [330] C.  Raffel, N.  Shazeer, A.  Roberts, K.  Lee,  S. Narang,
     R. Yan. Leveraging biomolecule and natural language through       M. Matena, Y. Zhou, W. Li, and P. J. Liu. Exploring the limits
     multi-modal learning: A survey, 2024.                                     of transfer learning with a unified text-to-text transformer.
[310] G. Penedo, H. Kydl´ıˇcek, A. Lozhkov, M. Mitchell, C. Raffel,        Journal of machine learning research, 21(140):1–67, 2020.
      L. Von Werra, T. Wolf, et al. The fineweb datasets: Decanting   [331] C.  Raffel, N.  Shazeer, A.  Roberts, K.  Lee,  S. Narang,
      the web for the finest text data at scale.  arXiv preprint       M. Matena, Y. Zhou, W. Li, and P. J. Liu. Exploring the limits
      arXiv:2406.17557, 2024.                                                   of transfer learning with a unified text-to-text transformer,
[311] G. Penedo, Q. Malartic, D. Hesslow, R. Cojocaru, A. Cap-         2023.
       pelli, H. Alobeidli, B. Pannier, E. Almazrouei, and J. Launay.   [332] R. Rahnamoun and M. Shamsfard.  Multi-layered evaluation
     The refinedweb dataset for falcon llm: Outperforming curated         using a fusion of metrics and llms as judges in open-domain
      corpora with web data, and web data only.  arXiv preprint         question answering.  In Proceedings of the 31st International
      arXiv:2306.01116, 2023.                                          Conference on Computational Linguistics, pages 6088–6104,
[312] B. Peng, C. Li, P. He, M. Galley, and J. Gao. Instruction tuning         2025.
     with gpt-4. arXiv preprint arXiv:2304.03277, 2023.               [333] S. Rajbhandari, J. Rasley, O. Ruwase, and Y. He. Zero: Memory
[313] M. E. Peters and D. Lecocq.  Content extraction using di-         optimizations toward training trillion parameter models.  In
      verse feature sets.  In Proceedings of the 22nd International        SC20: International Conference for High Performance ComConference on World Wide Web, WWW ’13 Companion, page         puting, Networking, Storage and Analysis, pages 1–16. IEEE,
      89–90, New York, NY, USA, 2013. Association for Computing         2020.
     Machinery.                                                          [334] S. Rajbhandari, O. Ruwase, J. Rasley, S. Smith, and Y. He.
[314] D. Podell, Z. English, K. Lacey, A. Blattmann, T. Dockhorn,          Zero-infinity: Breaking the gpu memory wall for extreme scale
       J. M¨uller, J. Penna, and R. Rombach. Sdxl: Improving latent        deep learning. In Proceedings of the international conference for
      diffusion models for high-resolution image synthesis, 2023.             high performance computing, networking, storage and analysis,
[315] J. Postel.  Transmission control protocol.  Technical report,        pages 1–14, 2021.
      1981.                                                                [335] D. Rau, S. Wang, H. D´ejean, and S. Clinchant. Context em-
[316] H. Pouransari, C.-L. Li, J.-H. R. Chang, P. K. A. Vasu, C. Koc,        beddings for efficient answer generation in rag. arXiv preprint
     V. Shankar, and O. Tuzel.  Dataset decomposition: Faster         arXiv:2407.09252, 2024.
      llm training with variable sequence length curriculum. arXiv   [336] J. Ren, S. Rajbhandari, R. Y. Aminabadi, O. Ruwase, S. Yang,
      preprint arXiv:2405.13226, 2024.                            M. Zhang, D. Li, and Y. He.   Zero-offload: Democratizing
[317] M. Pourreza and D. Rafiei.  Din-sql: Decomposed in-context          billion-scale model training, 2021.
      learning of text-to-sql with self-correction, 2023.                   [337] M. Rhu, N. Gimelshein, J. Clemons, A. Zulfiqar, and S. W.
[318] R. Pradeep, S. Sharifymoghaddam, and J. Lin. Rankvicuna:         Keckler. vdnn: Virtualized deep neural networks for scalable,
      Zero-shot listwise document reranking with open-source large         memory-efficient neural network design. In 2016 49th Annual
     language models. arXiv preprint arXiv:2309.15088, 2023.         IEEE/ACM International Symposium on Microarchitecture
[319] D. Qi and J. Wang. Cleanagent: Automating data standardiza-       (MICRO), pages 1–13. IEEE, 2016.
      tion with llm-based agents. CoRR, abs/2403.08291, 2024.         [338] S. Robertson and H. Zaragoza.  The probabilistic relevance
[320] Z. Qiang, W. Wang, and K. Taylor.   Agent-om: Lever-        framework: Bm25 and beyond.  Found. Trends Inf. Retr.,
      aging llm agents  for ontology matching.   arXiv preprint         3(4):333–389, Apr. 2009.
      arXiv:2312.00326, 2023.                                            [339] A. E. Roth. The Shapley value: essays in honor of Lloyd S.
[321] R. Qin, J. Xia, Z. Jia, M. Jiang, A. Abbasi, P. Zhou, J. Hu,         Shapley. Cambridge University Press, 1988.
     and Y. Shi.  Enabling on-device large language model per-   [340] A. S. R. Santos, E. H. M. Pena, R. Lopez, and J. Freire.
      sonalization with self-supervised data selection and synthesis.          Interactive data harmonization with LLM agents.  CoRR,
      In Proceedings of the 61st ACM/IEEE Design Automation         abs/2502.07132, 2025.
      Conference, pages 1–6, 2024.                                       [341] C. Schuhmann, R. Vencu, R. Beaumont, R. Kaczmarczyk,
[322] Z. Qin, D. Chen, W. Zhang, L. Yao, Y. Huang, B. Ding, Y. Li,        C. Mullis, A. Katta, T. Coombes, J. Jitsev, and A. Komatand S. Deng. The synergy between data and multi-modal large         suzaki. Laion-400m: Open dataset of clip-filtered 400 million
     language models: A survey from co-development perspective.         image-text pairs. arXiv preprint arXiv:2111.02114, 2021.
     arXiv preprint arXiv:2407.08583, 2024.                            [342] O. Sener and  S. Savarese.   Active learning  for convolu-
[323] H. Que, J. Liu, G. Zhang, C. Zhang, X. Qu, Y. Ma, F. Duan,          tional neural networks: A core-set approach.  arXiv preprint
      Z. Bai, J. Wang, Y. Zhang, et al. D-cpt law: Domain-specific         arXiv:1708.00489, 2017.
      continual pre-training scaling law for large language models.   [343] C. E. Shannon. A mathematical theory of communication. The
     arXiv preprint arXiv:2406.01375, 2024.                                Bell system technical journal, 27(3):379–423, 1948.
[324] Qwen, :, A. Yang, B. Yang, B. Zhang, B. Hui, B. Zheng, B. Yu,   [344] Y. Shao, L. Li, Y. Ma, P. Li, D. Song, Q. Cheng, S. Li, X. Li,
     C. Li, D. Liu, F. Huang, H. Wei, H. Lin, J. Yang, J. Tu,         P. Wang, Q. Guo, et al.  Case2code: Scalable synthetic data
       J. Zhang, J. Yang, J. Yang, J. Zhou, J. Lin, K. Dang, K. Lu,          for code generation.  In Proceedings of the 31st International
     K. Bao, K. Yang, L. Yu, M. Li, M. Xue, P. Zhang, Q. Zhu,        Conference on Computational Linguistics, pages 11056–11069,
     R. Men, R. Lin, T. Li, T. Tang, T. Xia, X. Ren, X. Ren, Y. Fan,         2025.
     Y. Su, Y. Zhang, Y. Wan, Y. Liu, Z. Cui, Z. Zhang, and Z. Qiu.   [345] H. Shen, P.-Y. Chen, P. Das, and T. Chen.   Seal: SafetyQwen2.5 technical report, 2025.                                  enhanced aligned llm fine-tuning via bilevel data selection.
[325] A. Radford, J. W. Kim, C. Hallacy, A. Ramesh, G. Goh,        arXiv preprint arXiv:2410.07471, 2024.
      S. Agarwal, G. Sastry, A. Askell, P. Mishkin, J. Clark, et al.   [346] M. Shen, G. Zeng, Z. Qi, Z.-W. Hong, Z. Chen, W. Lu,
     Learning transferable visual models from natural language su-        G. Wornell, S. Das, D. Cox, and C. Gan. Satori: Reinforcement
      pervision.  In International conference on machine learning,         learning with chain-of-action-thought enhances llm reasoning
     pages 8748–8763. PMLR, 2021.                                        via autoregressive search.  arXiv preprint arXiv:2502.02508,
[326] A. Radford, J. W. Kim, C. Hallacy, A. Ramesh, G. Goh,         2025.
      S. Agarwal, G.  Sastry, A.  Askell,  P. Mishkin,  J.  Clark,   [347] Z. Shen, T. Tao, L. Ma, W. Neiswanger, Z. Liu, H. Wang,
     G. Krueger, and  I. Sutskever.  Learning transferable visual        B.  Tan,  J.  Hestness, N.  Vassilieva, D.  Soboleva,  et  al.
     models from natural language supervision, 2021.                     Slimpajama-dc: Understanding data combinations  for  llm
                                                                                 training. arXiv preprint arXiv:2309.10818, 2023.
                                                     54
[348] K. Shi, X. Sun, Q. Li, and G. Xu. Compressing long context         models. In Proceedings of the 47th International ACM SIGIR
       for enhancing rag with amr-based concept distillation. arXiv        Conference on Research and Development in Information Repreprint arXiv:2405.03085, 2024.                                            trieval, pages 2713–2718, 2024.
[349] W. Shi, S. Min, M. Lomeli, C. Zhou, M. Li, G. Szilvasy,   [369] Z. Sun, X. Zhou, and G. Li. R-bot: An llm-based query rewrite
     R. James, X. V. Lin, N. A. Smith, L. Zettlemoyer, et  al.         system. CoRR, abs/2412.01661, 2024.
      In-context pretraining: Language modeling beyond document   [370] S. Talaei, M. Pourreza, Y.-C. Chang, A. Mirhoseini, and
      boundaries. arXiv preprint arXiv:2310.10638, 2023.                 A. Saberi. Chess: Contextual harnessing for efficient sql syn-
[350] Y. Shi, X. Zi, Z. Shi, H. Zhang, Q. Wu, and M. Xu.  Era-          thesis, 2024.
      gent: Enhancing retrieval-augmented language models with im-   [371] A. Talmor, J. Herzig, N. Lourie, and J. Berant.  Commonproved accuracy, efficiency, and personalization. arXiv preprint         senseqa: A question answering challenge targeting commonarXiv:2405.06683, 2024.                                              sense knowledge. arXiv preprint arXiv:1811.00937, 2018.
[351] Z. Shi, S. Gao, L. Yan, Y. Feng, X. Chen, Z. Chen, D. Yin,   [372] H. Tan, S. Wu, F. Du, Y. Chen, Z. Wang, F. Wang, and X. Qi.
      S. Verberne, and Z. Ren. Tool learning in the wild: Empowering        Data pruning via moving-one-sample-out. Advances in Neural
     language models as automatic tool agents. In Proceedings of the        Information Processing Systems, 36, 2024.
   ACM on Web Conference 2025, pages 2222–2237, 2025.           [373] Z. Tan, D. Li, S. Wang, A. Beigi, B. Jiang, A. Bhattacharjee,
[352] L. Shimabucoro,  S. Ruder,  J. Kreutzer, M. Fadaee, and       M. Karami, J. Li, L. Cheng, and H. Liu. Large language models
      S. Hooker. Llm see, llm do: Guiding data generation to tar-          for data annotation and synthesis: A survey. Proceedings of the
      get non-differentiable objectives (2024). URL https://arxiv.        2024 Conference on Empirical Methods in Natural Language
      org/abs/2407.01490.                                                Processing (EMNLP), 2024. arXiv preprint arXiv:2402.13446.
[353] A. Shirgaonkar, N. Pandey, N. C. Abay, T. Aktas, and V. Aski.   [374] Z. Tan, D. Li, S. Wang, et al. Large language models for data
     Knowledge distillation using frontier open-source llms: Gen-         annotation and synthesis: A survey. In EMNLP, pages 930–957.
       eralizability and the role of synthetic data.  arXiv preprint         Association for Computational Linguistics, 2024.
      arXiv:2410.18588, 2024.                                            [375] J. Tang, Y. Yang, W. Wei, L. Shi, L. Su, S. Cheng, D. Yin,
[354] K. Shoemake.  Animating rotation with quaternion curves.        and C. Huang. Graphgpt: Graph instruction tuning for large
      In Proceedings of the 12th annual conference on Computer        language models, 2024.
      graphics and interactive techniques, pages 245–254, 1985.         [376] Z. Tang, Z. Yang, G. Wang, Y. Fang, Y. Liu, C. Zhu, M. Zeng,
[355] M. Shoeybi, M. Patwary, R. Puri, P. LeGresley, J. Casper, and        C. Zhang, and M. Bansal. Unifying vision, text, and layout for
     B. Catanzaro.  Megatron-lm: Training multi-billion parame-         universal document processing, 2023.
      ter language models using model parallelism. arXiv preprint   [377] K. Team, A. Du, B. Gao, B. Xing, et al. Kimi k1.5: Scaling
      arXiv:1909.08053, 2019.                                             reinforcement learning with llms, 2025.
[356] A. Shrivastava and P. Li. In defense of minhash over simhash.   [378] M. N. Team et  al.   Introducing mpt-7b: A new standard
      In Artificial Intelligence and Statistics, pages 886–894. PMLR,          for open-source, commercially usable llms. DataBricks (May,
      2014.                                                          2023) www. mosaicml. com/blog/mpt-7b, 2023.
[357] D. Shrivastava, D. Kocetkov, H. de Vries, D. Bahdanau, and   [379] Q. Team. Qwq: Reflect deeply on the boundaries of the unT. Scholak. RepoFusion: Training Code Models to Understand        known. Hugging Face, 2024.
     Your Repository, June 2023.                                       [380] M. Tepper, I. S. Bhati, C. Aguerrebere, M. Hildebrand, and
[358] E. Silcock, L. D’Amico-Wong, J. Yang, and M. Dell.  Noise-        T. Willke. Leanvec: Searching vectors faster by making them
      robust de-duplication at scale.   Technical report, National             fit, 2024.
     Bureau of Economic Research, 2022.                               [381] M. Tepper, I. S. Bhati, C. Aguerrebere, and T. Willke. Glean-
[359] V.  Y.  Singh,  K.  Vaidya,  V.  B.  Kumar,  S.  Khosla,          vec: Accelerating vector search with minimalist nonlinear diB. Narayanaswamy, R. Gangadharaiah, and T. Kraska. Panda:         mensionality reduction, 2024.
     Performance debugging for databases using LLM agents.  In   [382] J. Thorpe, P. Zhao, J. Eyolfson, Y. Qiao, Z. Jia, M. Zhang,
     CIDR. www.cidrdb.org, 2024.                                    R. Netravali, and G. H. Xu.  Bamboo: Making preemptible
[360] E. Slyman, S. Lee, S. Cohen, and K. Kafle.  Fairdedup: De-         instances resilient for affordable training of large {DNNs}. In
      tecting and mitigating vision-language fairness disparities in se-         20th USENIX Symposium on Networked Systems Design and
     mantic dataset deduplication. In Proceedings of the IEEE/CVF        Implementation (NSDI 23), pages 497–513, 2023.
     Conference on Computer Vision and Pattern Recognition,   [383] T. Thrush, C. Potts, and T. Hashimoto.  Improving prepages 13905–13916, 2024.                                               training data using perplexity correlations.  arXiv preprint
[361] L. Soldaini, R. Kinney, A. Bhagia, D. Schwenk, D. Atkinson,         arXiv:2409.05816, 2024.
     R. Authur, B. Bogin, K. Chandu, J. Dumas, Y. Elazar, et al.   [384] M. Tirmazi, A. Barker, N. Deng, M. E. Haque, Z. G. Qin,
     Dolma: An open corpus of three trillion tokens for language          S. Hand, M. Harchol-Balter, and J. Wilkes.  Borg: the next
     model pretraining research. arXiv preprint arXiv:2402.00159,         generation. In Proceedings of the fifteenth European conference
      2024.                                                     on computer systems, pages 1–14, 2020.
[362] J. Song, Z. Zhang, Z. Tang, S. Feng, and Y. Gu. Improving code   [385] K. Tirumala, D. Simig, A. Aghajanyan, and A. Morcos. D4:
     summarization with tree transformer enhanced by position-        Improving llm pretraining via document de-duplication and
      related syntax complement. IEEE Transactions on Artificial          diversification.  Advances in Neural Information Processing
      Intelligence, 5:4776–4786, 2024.                                     Systems, 36:53983–53995, 2023.
[363] J. H. Sriram Dharwada, Himanshu Devrani and H. Do-   [386] H. Touvron, L. Martin, K. Stone, P. Albert, A. Almahairi,
     raiswamy. Query rewriting via llms. CoRR, abs/2502.12918,        Y. Babaei, N. Bashlykov, S. Batra, P. Bhargava, S. Bhosale,
      2025.                                                                     et al. Llama 2: Open foundation and fine-tuned chat models.
[364] K.  Staniszewski,  S.  Tworkowski,  S.  Jaszczur,  Y.  Zhao,        arXiv preprint arXiv:2307.09288, 2023.
     H. Michalewski, L. Kuci´nski, and P. Milo´s. Structured packing   [387] B. Trabucco, K. Doherty, M. Gurinas, and R. Salakhutdinov.
      in llm training improves long context utilization. arXiv preprint          Effective data augmentation with diffusion models, 2023.
      arXiv:2312.17296, 2023.                                            [388] G. Wallace.  The jpeg  still picture compression standard.
[365] A. Su, A. Wang, C. Ye, C. Zhou, G. Zhang, G. Chen, G. Zhu,       IEEE Transactions on Consumer  Electronics,  38(1):xviii–
     H. Wang, H. Xu, H. Chen, H. Li, H. Lan, J. Tian, J. Yuan,         xxxiv, 1992.
       J. Zhao, J. Zhou, K. Shou, L. Zha, L. Long, L. Li, P. Wu,   [389] B. Wan, M. Han, Y. Sheng, Y. Peng, H. Lin, M. Zhang, Z. Lai,
     Q. Zhang, Q. Huang, S. Yang, T. Zhang, W. Ye, W. Zhu, X. Hu,       M. Yu, J. Zhang, Z. Song, X. Liu, and C. Wu. Bytecheckpoint:
     X. Gu, X. Sun, X. Li, Y. Yang, and Z. Xiao. Tablegpt2: A large     A unified checkpointing system for large foundation model
     multimodal model with tabular data integration, 2024.                development, 2024.
[366] S. Sudalairaj, A. Bhandwaldar, A. Pareja, K. Xu, D. D. Cox,   [390] A. Wang, B. Ai, B. Wen, C. Mao, C.-W. Xie, D. Chen,
     and A. Srivastava.  Lab: Large-scale alignment for chatbots.         F. Yu, H. Zhao, J. Yang, J. Zeng, et al.  Wan: Open and
     arXiv preprint arXiv:2403.01081, 2024.                            advanced large-scale video generative models. arXiv preprint
[367] L. Sun, K. Zhang, Q. Li, and R. Lou. Umie: Unified multimodal         arXiv:2503.20314, 2025.
      information extraction with instruction tuning, 2024.              [391] A. Wang, H. Chen, L. Liu, K. Chen, Z. Lin, J. Han, and G. Ding.
[368] Y. Sun, F. Wang, Y. Zhu, W. X. Zhao, and J. Mao. An in-         Yolov10: Real-time end-to-end object detection, 2024.
      tegrated data processing framework for pretraining foundation

                                                     55
[392] B. Wang, C. Xu, X. Zhao, L. Ouyang, F. Wu, Z. Zhao, R. Xu,   [415] J. Wu, J. Zhu, and Y. Qi.  Medical graph rag: Towards safe
     K. Liu, Y. Qu, F. Shang, B. Zhang, L. Wei, Z. Sui, W. Li, B. Shi,        medical large language model via graph retrieval-augmented
     Y. Qiao, D. Lin, and C. He. Mineru: An open-source solution         generation. arXiv preprint arXiv:2408.04187, 2024.
       for precise document content extraction, 2024.                     [416] M. Wu, T.-T. Vu, L. Qu, and G. Haffari.  Mixture-of-skills:
[393] C. Wang, Q. Dong, X. Wang, H. Wang, and Z. Sui. Statistical        Learning to optimize data usage for fine-tuning large language
      dataset evaluation: Reliability, difficulty, and validity, 2022.            models. arXiv preprint arXiv:2406.08811, 2024.
[394] C. Wang, M. Li, J. He, Z. Wang, E. Darzi, Z. Chen, J. Ye,   [417] M. Xia, S. Malladi, S. Gururangan, S. Arora, and D. Chen.
     T. Li, Y. Su, J. Ke, et al. A survey for large language models in         Less: Selecting influential data for targeted instruction tuning.
      biomedicine. arXiv preprint arXiv:2409.00133, 2024.                 arXiv preprint arXiv:2402.04333, 2024.
[395] C. Wang, Q. Wu, S. Huang, and A. Saied.  Economic hy-   [418] B. Xiao, H. Wu, W. Xu, X. Dai, H. Hu, Y. Lu, M. Zeng, C. Liu,
     perparameter optimization with blended search strategy.  In        and L. Yuan.  Florence-2: Advancing a unified representation
      International Conference on Learning Representations, 2021.            for a variety of vision tasks, 2023.
[396] H. Wang, J. Wang, C. T. Leong, and W. Li. Steca: Step-level   [419] C. Xie, Z. Lin, A. Backurs, S. Gopi, D. Yu, H. A. Inan, H. Nori,
      trajectory calibration for llm agent learning, 2025.                   H. Jiang, H. Zhang, Y. T. Lee, et al. Differentially private syn-
[397] J. Wang, J. Wu, Y. Hou, Y. Liu, M. Gao, and J. McAuley. In-          thetic data via foundation model apis 2: Text. arXiv preprint
      structgraph: Boosting large language models via graph-centric         arXiv:2403.01749, 2024.
      instruction tuning and preference alignment, 2024.                [420] S. M. Xie, H. Pham, X. Dong, N. Du, H. Liu, Y. Lu, P. S. Liang,
[398] J. Wang, B. Zhang, Q. Du, J. Zhang, and D. Chu. A survey        Q. V. Le, T. Ma, and A. W. Yu.  Doremi: Optimizing data
     on data selection for llm instruction tuning.  arXiv preprint        mixtures speeds up language model pretraining. Advances in
      arXiv:2402.05123, 2024.                                          Neural Information Processing Systems, 36:69798–69818, 2023.
[399] P. Wang, L. Li, Z. Shao, R. Xu, D. Dai, Y. Li, D. Chen,   [421] S. M. Xie, S. Santurkar, T. Ma, and P. S. Liang. Data selection
     Y. Wu, and Z. Sui.   Math-shepherd: Verify and reinforce          for language models via importance resampling. Advances in
      llms step-by-step without human annotations. arXiv preprint        Neural Information Processing Systems, 36:34201–34227, 2023.
      arXiv:2312.08935, 2023.                                            [422] W. Xie. Analysis of the reasoning with redundant information
[400] T. Wang, X. Chen, H. Lin, X. Chen, X. Han, L. Sun, H. Wang,         provided ability of large language models.  arXiv preprint
     and Z. Zeng.  Match, compare, or select? an investigation of         arXiv:2310.04039, 2023.
      large language models for entity matching. In COLING, pages   [423] Y. Xie, K. Aggarwal, and A. Ahmad.  Efficient continual pre96–109. Association for Computational Linguistics, 2025.               training for building domain specific large language models. In
[401] Y. Wang, Y.  Kordi,  S.  Mishra, A.  Liu, N. A.  Smith,        Findings of the Association for Computational Linguistics ACL
     D. Khashabi, and H. Hajishirzi.  Self-instruct: Aligning lan-         2024, pages 10184–10201, 2024.
     guage models with self-generated instructions. arXiv preprint   [424] G. Xiong, J. Bao, and W. Zhao. Interactive-kbqa: Multi-turn
      arXiv:2212.10560, 2022.                                                interactions for knowledge base question answering with large
[402] Z. Wang, X. He, K. Chen, C. Lin, and J. Su. Code-aware cross-        language models, 2024.
     program transfer hyperparameter optimization.   In AAAI,   [425] H. Xiu, L. Zhang, T. Zhang, J. Yang, and J. Chen.  Query
     pages 10297–10305. AAAI Press, 2023.                             performance explanation through large language model for
[403] Z. Wang, Z. Jia, S. Zheng, Z. Zhang, X. Fu, T. E. Ng, and      HTAP systems. CoRR, abs/2412.01709, 2024.
     Y. Wang. Gemini: Fast failure recovery in distributed training   [426] C. Xu, Q. Sun, K. Zheng, X. Geng, P. Zhao, J. Feng, C. Tao,
     with in-memory checkpoints. In Proceedings of the 29th Sym-       and D. Jiang. Wizardlm: Empowering large language models to
     posium on Operating Systems Principles, pages 364–381, 2023.          follow complex instructions. arXiv preprint arXiv:2304.12244,
[404] Z. Wang, H. Zhang, C.-L. Li, J. M. Eisenschlos, V. Perot,         2023.
      Z. Wang, L. Miculicich, Y. Fujii, J. Shang, C.-Y. Lee, and   [427] F. Xu, W. Shi, and E. Choi.  Recomp: Improving retrievalT. Pfister.  Chain-of-table: Evolving tables in the reasoning        augmented lms with compression and selective augmentation.
      chain for table understanding, 2024.                                arXiv preprint arXiv:2310.04408, 2023.
[405] Z. Wang, W. Zhong, Y. Wang, Q. Zhu, F. Mi, B. Wang,   [428] J. Xu, R. Zhang, C. Guo, W. Hu, Z. Liu, F. Wu, Y. Feng, S. Sun,
      L. Shang, X. Jiang, and Q. Liu.   Data management  for        C. Shao, Y. Guo, J. Zhao, K. Zhang, M. Guo, and J. Leng.
      training large language models: A survey.  arXiv preprint         vtensor: Flexible virtual tensor management for efficient llm
      arXiv:2312.01700, 2023.                                                 serving, 2024.
[406] H. Wei, L. Kong, J. Chen, L. Zhao, Z. Ge, J. Yang, J. Sun,   [429] M. Xu.   Medicalgpt: Training medical gpt model.   https:
     C. Han, and X. Zhang. Vary: Scaling up the vision vocabulary        //github.com/shibing624/MedicalGPT, 2023.
       for large vision-language models, 2023.                             [430] Y. Xu, H. Li, K. Chen, and L. Shou.  Kcmf: A knowledge-
[407] H. Wei, C. Liu, J. Chen, J. Wang, L. Kong, Y. Xu, Z. Ge,        compliant framework for schema and entity matching with fineL. Zhao, J. Sun, Y. Peng, C. Han, and X. Zhang. General ocr         tuning-free llms. CoRR, abs/2410.12480, 2024.
      theory: Towards ocr-2.0 via a unified end-to-end model, 2024.     [431] L. Xue, N. Constant, A. Roberts, M. Kale, R. Al-Rfou, A. Sid-
[408] L. Wei, G. Xiao, and M. Balazinska. RACOON: an llm-based         dhant, A. Barua, and C. Raffel. mt5: A massively multilingual
     framework for retrieval-augmented column type annotation         pre-trained text-to-text transformer, 2021.
     with a knowledge graph. CoRR, abs/2409.14556, 2024.            [432] M. Yan, Y. Wang, Y. Wang, X. Miao, and J. Li.  GIDCL:
[409] Y. Wei, Z. Wang, J. Liu, Y. Ding, and L. Zhang. Magicoder:     A graph-enhanced interpretable data cleaning framework with
     Source code is all you need. arXiv preprint arXiv:2312.02120,          large language models. Proc. ACM Manag. Data, 2(6):236:1–
      10, 2023.                                                              236:29, 2024.
[410] G. Wenzek, M.-A. Lachaux, A. Conneau, V. Chaudhary,   [433] A. Yang, B. Xiao, B. Wang, B. Zhang, C. Bian, C. Yin, C. Lv,
      F. Guzm´an, A. Joulin, and E. Grave. Ccnet: Extracting high        D. Pan, D. Wang, D. Yan, et al. Baichuan 2: Open large-scale
      quality monolingual datasets from web crawl data.  arXiv        language models. arXiv preprint arXiv:2309.10305, 2023.
      preprint arXiv:1911.00359, 2019.                                  [434] A. Yang, B. Yang, B. Hui, B. Zheng, B. Yu, C. Zhou, C. Li,
[411] A. Wettig, A. Gupta, S. Malik, and D. Chen.   Qurating:        C. Li, D. Liu, F. Huang, G. Dong, H. Wei, H. Lin, J. Tang,
      Selecting high-quality data for training language models. arXiv          J. Wang, J. Yang, J. Tu, J. Zhang, J. Ma, J. Yang, J. Xu,
      preprint arXiv:2402.09739, 2024.                                          J. Zhou, J. Bai, J. He, J. Lin, K. Dang, K. Lu, K. Chen, K. Yang,
[412] C. Whitehouse, C. Vania, A. F. Aji, C. Christodoulopoulos, and       M. Li, M. Xue, N. Ni, P. Zhang, P. Wang, R. Peng, R. Men,
     A. Pierleoni. Webie: Faithful and robust information extraction        R. Gao, R. Lin, S. Wang, S. Bai, S. Tan, T. Zhu, T. Li, T. Liu,
     on the web. arXiv preprint arXiv:2305.14293, 2023.             W. Ge, X. Deng, X. Zhou, X. Ren, X. Zhang, X. Wei, X. Ren,
[413] D. Wu, W. U. Ahmad, D. Zhang, M. K. Ramanathan, and        X. Liu, Y. Fan, Y. Yao, Y. Zhang, Y. Wan, Y. Chu, Y. Liu,
     X. Ma. Repoformer: Selective Retrieval for Repository-Level         Z. Cui, Z. Zhang, Z. Guo, and Z. Fan. Qwen2 technical report,
     Code Completion, June 2024.                                        2024.
[414] H. Wu, E. Zhang, L. Liao, C. Chen, J. Hou, A. Wang, W. Sun,   [435] H. Yang, J. Zhou, Y. Fu, X. Wang, R. Roane, H. Guan, and
     Q. Yan, and W. Lin. Exploring video quality assessment on user        T. Liu.   Protrain: Efficient llm training via memory-aware
      generated contents from aesthetic and technical perspectives.         techniques. arXiv preprint arXiv:2406.08334, 2024.
      In Proceedings of the IEEE/CVF International Conference on   [436] Y. Yang, S. Mishra, J. Chiang, and B. Mirzasoleiman. SmalltoComputer Vision, pages 20144–20154, 2023.                             large (s2l): Scalable data selection for fine-tuning large language
                                                                   models by summarizing training trajectories of small models.
                                                     56
     Advances in Neural Information Processing Systems, 37:83465–        knowledge base question answering. In S. Muresan, P. Nakov,
      83496, 2024.                                                and A. Villavicencio, editors, Proceedings of the 60th Annual
[437] Z. Yang, J. Teng, W. Zheng, M. Ding, S. Huang, J. Xu, Y. Yang,        Meeting of the Association for Computational Linguistics (VolW. Hong, X. Zhang, G. Feng, et al. Cogvideox: Text-to-video       ume 1: Long Papers), pages 5773–5784, Dublin, Ireland, May
      diffusion models with an expert transformer.  arXiv preprint         2022. Association for Computational Linguistics.
      arXiv:2408.06072, 2024.                                            [459] P. Zhang, G. Zeng, T. Wang, and W. Lu. Tinyllama: An open-
[438] Z. Yao, H. Li, J. Zhang, C. Li, and H. Chen.  A query         source small language model. arXiv preprint arXiv:2401.02385,
      optimization method utilizing large language models. CoRR,         2024.
      abs/2503.06902, 2025.                                              [460] S. Zhang, L. Dong, X. Li, et al.  Instruction tuning for large
[439] J. Ye, P. Liu, T. Sun, Y. Zhou, J. Zhan, and X. Qiu.  Data        language models: A survey. arXiv preprint arXiv:2308.10792,
     mixing laws: Optimizing data mixtures by predicting language         2023.
     modeling performance. arXiv preprint arXiv:2403.16952, 2024.   [461] S. Zhang, Z. Huang, and E. Wu.  Data cleaning using large
[440] L. Ye, Z. Tao, Y. Huang, and Y. Li. Chunkattention: Efficient        language models. CoRR, abs/2410.15547, 2024.
      self-attention with prefix-aware kv cache and two-phase parti-   [462] S. Zhang, S. Roller, N. Goyal, M. Artetxe, M. Chen, S. Chen,
       tion. arXiv preprint arXiv:2402.15220, 2024.                       C. Dewan, M. Diab, X. Li, X. V. Lin, et  al.  Opt: Open
[441] R. Ye, C. Zhang, R. Wang, S. Xu, and Y. Zhang. Language is         pre-trained transformer language models.   arXiv preprint
       all a graph needs, 2024.                                             arXiv:2205.01068, 2022.
[442] Y. Ye, Z. Huang, Y. Xiao, E. Chern, S. Xia, and P. Liu. Limo:   [463] X. Zhang, H. Wu, Y. Li, Z. Tang, J. Tan, F. Li, and B. Cui.
      Less is more for reasoning. arXiv preprint arXiv:2502.03387,      An efficient transfer learning based configuration adviser for
      2025.                                                            database tuning. Proc. VLDB Endow., 17(3):539–552, 2023.
[443] P. Yin, W.-D. Li, K. Xiao, A. Rao, Y. Wen, K. Shi, J. Howland,   [464] Y. Zhang, J. Henkel, A. Floratou, J. Cahoon, S. Deep, and J. M.
      P. Bailey, M. Catasta, H. Michalewski, A. Polozov, and C. Sut-          Patel. Reactable: Enhancing react for table question answering,
      ton. Natural language to code generation in interactive data         2023.
      science notebooks, 2022.                                            [465] Y. Zhang, Y. Luo, Y. Yuan, and A. C. Yao.  Autonomous
[444] S. Yin, C. Fu, S. Zhao, K. Li, X. Sun, T. Xu, and E. Chen.        data selection with language models for mathematical texts.
   A survey on multimodal large language models.  CoRR,         In ICLR 2024 Workshop on Navigating and Addressing Data
      abs/2306.13549, 2023.                                           Problems for Foundation Models, 2024.
[445] S. Yokoo.  Contrastive learning with large memory bank and   [466] H. Zhao, Z. Han, Z. Yang, Q. Zhang, M. Li, F. Yang, Q. Zhang,
      negative embedding subtraction for accurate copy detection.        B. Li, Y. Yang, L. Qiu, et al.  Silod: A co-design of caching
     arXiv preprint arXiv:2112.04323, 2021.                          and scheduling for deep learning clusters. In Proceedings of the
[446] L. Yuan, G. Cui, H. Wang, N. Ding, X. Wang, J. Deng, B. Shan,         Eighteenth European Conference on Computer Systems, pages
     H. Chen, R. Xie, Y. Lin, Z. Liu, B. Zhou, H. Peng, Z. Liu, and         883–898, 2023.
    M. Sun. Advancing llm reasoning generalists with preference   [467] J. Zhao, W. Zhao, A. Drozdov, B. Rozonoyer, M. A. Sultrees, 2024.                                                             tan, J.-Y. Lee, M. Iyyer, and A. McCallum.   Multistage
[447] S. Yue, W. Chen, S. Wang, B. Li, C. Shen, S. Liu, Y. Zhou,         collaborative knowledge  distillation from a  large language
     Y. Xiao, S. Yun, X. Huang, et al. Disc-lawllm: Fine-tuning large        model for semi-supervised sequence generation. arXiv preprint
     language models for intelligent legal services. arXiv preprint         arXiv:2311.08640, 2023.
      arXiv:2309.11325, 2023.                                            [468] M. Zhao, E. Adamiak, and C. Kozyrakis. cedar: Optimized and
[448] X. Yue, Y. Ni, K. Zhang, T. Zheng, R. Liu, G. Zhang,          unified machine learning input data pipelines. arXiv preprint
      S. Stevens, D. Jiang, W. Ren, Y. Sun, et al. Mmmu: A mas-         arXiv:2401.08895, 2024.
      sive multi-discipline multimodal understanding and reasoning   [469] M. Zhao, S. Pan, N. Agarwal, Z. Wen, D. Xu, A. Natarajan,
     benchmark for expert agi.  In Proceedings of the IEEE/CVF         P. Kumar, S. S. P, R. Tijoriwala, K. Asher, H. Wu, A. Basant,
     Conference on Computer Vision and Pattern Recognition,        D. Ford, D. David, N. Yigitbasi, P. Singh, C.-J. Wu, and
     pages 9556–9567, 2024.                                          C. Kozyrakis.  Tectonic-Shift: A composite storage fabric for
[449] R. Zellers, A. Holtzman, Y. Bisk, A. Farhadi, and Y. Choi.         Large-Scale ML training. In 2023 USENIX Annual Technical
      Hellaswag: Can a machine really finish your sentence? arXiv        Conference (USENIX ATC 23), pages 433–449, Boston, MA,
      preprint arXiv:1905.07830, 2019.                                    July 2023. USENIX Association.
[450] S. Zeng, J. Zhang, P. He, J. Ren, T. Zheng, H. Lu, H. Xu,   [470] R. Zhao, Z. L. Thai, Y. Zhang, S. Hu, Y. Ba, J. Zhou, J. Cai,
     H. Liu, Y. Xing, and J. Tang. Mitigating the privacy issues in         Z. Liu, and M. Sun.  Decoratelm: Data engineering through
      retrieval-augmented generation (rag) via pure synthetic data.         corpus rating, tagging, and editing with language models. arXiv
     arXiv preprint arXiv:2406.14773, 2024.                                preprint arXiv:2410.05639, 2024.
[451] S.  Zerhoudi  and M.  Granitzer.    Personarag:  Enhanc-   [471] W. Zhao, H. Feng, Q. Liu, J. Tang, S. Wei, B. Wu, L. Liao,
      ing retrieval-augmented generation systems with user-centric        Y. Ye, H. Liu, W. Zhou, H. Li, and C. Huang. Tabpedia: Toagents. In IR-RAG@SIGIR, volume 3784 of CEUR Workshop        wards comprehensive visual table understanding with concept
      Proceedings, pages 1–11. CEUR-WS.org, 2024.                         synergy, 2024.
[452] C. Zhang, Y. Mao, Y. Fan, Y. Mi, Y. Gao, L. Chen, D. Lou, and   [472] W. X. Zhao, K. Zhou, J. Li, T. Tang, X. Wang, Y. Hou, Y. Min,
       J. Lin. Finsql: Model-agnostic llms-based text-to-sql framework        B. Zhang, J. Zhang, Z. Dong, et al. A survey of large language
       for financial analysis, 2024.                                         models. arXiv preprint arXiv:2303.18223, 2023.
[453] F. Zhang, D. Zhu, J. Ming, Y. Jin, D. Chai, L. Yang, H. Tian,   [473] X. Zhao, H. Li, J. Zhang, X. Huang, T. Zhang, J. Chen, R. Shi,
      Z. Fan, and K. Chen. DH-RAG: A dynamic historical context-        C. Li, and H. Chen.  Llmidxadvis: Resource-efficient index
     powered retrieval-augmented generation method for multi-turn         advisor utilizing large language model. CoRR, abs/2503.07884,
      dialogue. CoRR, abs/2502.13847, 2025.                               2025.
[454] H. Zhang, Y. Dong, C. Xiao, and M. Oyamada.    Jelly-   [474] X. Zhao, X. Zhou, and G. Li. Automatic database knob tuning:
       fish: A large language model for data preprocessing. CoRR,     A survey. IEEE Trans. Knowl. Data Eng., 35(12):12470–12490,
      abs/2312.01678, 2023.                                               2023.
[455] H. Zhang, X. Li, and L. Bing.  Video-llama: An instruction-   [475] Y. Zhao, L. Chen, A. Cohan, and C. Zhao. TaPERA: Enhanctuned audio-visual language model for video understanding.         ing faithfulness and interpretability in long-form table QA by
     arXiv preprint arXiv:2306.02858, 2023.                              content planning and execution-based reasoning. In L.-W. Ku,
[456] H. Zhang, Y. Liu, W. Hung, A. S. R. Santos, and J. Freire. Au-        A. Martins, and V. Srikumar, editors, Proceedings of the 62nd
      toddg: Automated dataset description generation using large        Annual Meeting of the Association for Computational Linguislanguage models. CoRR, abs/2502.01050, 2025.                            tics (Volume 1: Long Papers), pages 12824–12840, Bangkok,
[457] J. Zhang, Z. Liu, X. Hu, X. Xia, and S. Li.  Vulnerability         Thailand, Aug. 2024. Association for Computational Linguisdetection by learning from syntax-based execution paths of           tics.
      code. IEEE Transactions on Software Engineering, 49(8):4196–   [476] L. Zheng, W.-L. Chiang, Y. Sheng,  S. Zhuang,  Z. Wu,
      4212, 2023.                                                   Y. Zhuang, Z. Lin, Z. Li, D. Li, E. Xing, et al. Judging llm-as-
[458] J. Zhang, X. Zhang, J. Yu, J. Tang, J. Tang, C. Li, and         a-judge with mt-bench and chatbot arena. Advances in Neural
     H. Chen.  Subgraph retrieval enhanced model for multi-hop        Information Processing Systems, 36:46595–46623, 2023.
                                                                            [477] M. Zheng, X. Feng, Q. Si, Q. She, Z. Lin, W. Jiang, and
                                                    W. Wang. Multimodal table understanding, 2024.
                                                     57
[478] Z. Zheng, X.  Ji, T. Fang, F. Zhou, C. Liu, and G. Peng.   [489] X. Zhou, G.  Li, and  Z.  Liu.  LLM  as DBA.   CoRR,
      Batchllm: Optimizing large batched llm inference with global         abs/2308.05481, 2023.
      prefix sharing and throughput-oriented token batching. arXiv   [490] X. Zhou, G. Li, Z. Sun, Z. Liu, W. Chen, J. Wu, J. Liu,
      preprint arXiv:2412.03594, 2024.                                 R. Feng, and G. Zeng. D-bot: Database diagnosis system using
[479] Y. Zhong, Z. Zhang, B. Wu, S. Liu, Y. Chen, C. Wan, H. Hu,          large language models. Proc. VLDB Endow., 17(10):2514–2527,
      L. Xia, R. Ming, Y. Zhu, and X. Jin. Optimizing RLHF training         2024.
       for large language models with stage fusion.  In NSDI, pages   [491] X. Zhou, Z. Sun, and G. Li. DB-GPT: large language model
      489–503. USENIX Association, 2025.                              meets database. Data Sci. Eng., 9(1):102–111, 2024.
[480] Z. Zhong, H. Liu, X. Cui, X. Zhang, and Z. Qin.  Mix-of-   [492] X. Zhou, T. Zhang, and D. Lo.  Large language model for
      granularity: Optimize the chunking granularity for retrieval-         vulnerability detection: Emerging results and future directions,
     augmented generation. arXiv preprint arXiv:2406.00456, 2024.         2024.
[481] K. Zhou, B. Zhang, J. Wang, Z. Chen, W. X. Zhao, J. Sha,   [493] Y. Zhou, Y. He, S. Tian, Y. Ni, Z. Yin, X. Liu, C. Ji, S. Liu,
      Z. Sheng, S. Wang, and J.-R. Wen.  Jiuzhang3. 0: Efficiently        X. Qiu, G. Ye, and H. Chai. r3-NL2GQL: A model coordination
     improving mathematical reasoning by training small data syn-        and knowledge graph alignment approach for NL2GQL.  In
      thesis models. arXiv preprint arXiv:2405.14365, 2024.               Y. Al-Onaizan, M. Bansal, and Y.-N. Chen, editors, Findings of
[482] T. Zhou, X. Zhao, X. Xu, and S. Ren.  Bileve: Securing text         the Association for Computational Linguistics: EMNLP 2024,
     provenance in large language models against spoofing with bi-        pages 13679–13692, Miami, Florida, USA, Nov. 2024. Associalevel signature. arXiv preprint arXiv:2406.01946, 2024.                 tion for Computational Linguistics.
[483] W. Zhou, Y. Gao, X. Zhou, and G. Li. Cracking SQL Barriers:   [494] F. Zhu, Z. Liu, F. Feng, C. Wang, M. Li, and T. S. Chua.
    An llm-based dialect transaltion system. Proc. ACM Manag.         Tat-llm: A specialized language model for discrete reasoning
     Data, 3(3 (SIGMOD)), 2025.                                         over financial tabular and textual data. In Proceedings of the
[484] W. Zhou, Y. Gao, X. Zhou, and G. Li. Cracksql: A hybrid sql         5th ACM International Conference on AI in Finance, ICAIF
      dialect translation system powered by large language models.          ’24, page 310–318, New York, NY, USA, 2024. Association for
     arXiv Preprint, 2025.                                        Computing Machinery.
[485] W. Zhou, C. Lin, X. Zhou, and G. Li.  Breaking it down:   [495] X. Zhu, D. Cheng, H. Li, K. Zhang, E. Hua, X. Lv, N. Ding,
    An in-depth study of index advisors.  Proc. VLDB Endow.,         Z. Lin, Z. Zheng, and B. Zhou. How to synthesize text data
      17(10):2405–2418, 2024.                                           without model collapse?  arXiv preprint arXiv:2412.14689,
[486] W. Zhou, C. Lin, X. Zhou, G. Li, and T. Wang. Demonstration         2024.
      of vita: Visualizing, testing and analyzing index advisors.  In   [496] X. Zhu, B. Qi, K. Zhang, X. Long, Z. Lin, and B. Zhou. Pad:
    CIKM, pages 5133–5137. ACM, 2023.                              Program-aided distillation can teach small models reasoning
[487] W. Zhou, C. Lin, X. Zhou, G. Li, and T. Wang. TRAP: tai-         better than chain-of-thought fine-tuning, 2024.
      lored robustness assessment for index advisors via adversarial   [497] Y. Zhu, R. Kiros, R. Zemel, R. Salakhutdinov, R. Urtasun,
      perturbation. In ICDE, pages 42–55. IEEE, 2024.                   A. Torralba, and S. Fidler. Aligning books and movies: Towards
[488] X. Zhou, C. Chai, G. Li, and J. Sun. Database meets artificial          story-like visual explanations by watching movies and reading
       intelligence: A survey. TKDE, 2020.                                 books.  In The IEEE International Conference on Computer
                                                                       Vision (ICCV), December 2015.

                                                     58

