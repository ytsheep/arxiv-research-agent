# MultiHop-RAG: Benchmarking Retrieval-Augmented Generation for

## Document Header

MultiHop-RAG: Benchmarking Retrieval-Augmented Generation for
                               Multi-Hop Queries

                                    Yixuan Tang and Yi Yang
                         Hong Kong University of Science and Technology
                                  {yixuantang,imyiyang}@ust.hk


## Abstract

Retrieval-augmented generation (RAG) augments large language models (LLM) by retrieving relevant knowledge, showing promising potential in mitigating LLM hallucinations
                and enhancing response quality, thereby facil-2024              itating the great adoption of LLMs in practice. However, we find that existing RAG systems are inadequate in answering multi-hopJan                    queries, which require retrieving and reasoning
                 over multiple pieces of supporting evidence.                                                                            Figure 1: RAG with multi-hop query.27                 Furthermore, to our knowledge, no existing
           RAG benchmarking dataset focuses on multihop queries. In this paper, we develop a novel       nAI, 2023). One promising use case is Retrievaldataset, MultiHop-RAG, which consists of a                                                    Augmented Generation (RAG) (Asai et al., 2023),
                knowledge base, a large collection of multiwhich optimizes the output of a large language
               hop queries, their ground-truth answers, and[cs.CL]                                                 model by referencing an external knowledge base                   the associated supporting evidence. We detail
                   the procedure of building the dataset, utiliz-       outside of the LLM training data sources before
                  ing an English news article dataset as the un-       generating a response. RAG improves LLM’s rederlying RAG knowledge base. We demon-      sponse (Borgeaud et al., 2022) and also mitigates
                     strate the benchmarking utility of MultiHop-       the occurrence of hallucinations, thereby enhancing
           RAG in two experiments. The first experiment                                                                 the models’ credibility (Gao et al., 2023). LLMcompares different embedding models for rebased frameworks, such as LlamaIndex (Liu, 2022)
                    trieving evidence for multi-hop queries. In the
                                                       and LangChain (Chase, 2022), specialize in sup-                second experiment, we examine the capabilities of various state-of-the-art LLMs, includ-       porting RAG pipelines.
                  ing GPT-4, PaLM, and Llama2-70B, in rea-         In real-world Retrieval-Augmented Generation
                 soning and answering multi-hop queries given      (RAG) applications, a user’s query often necessithe evidence. Both experiments reveal that ex-        tates retrieving and reasoning over evidence from
                    isting RAG methods perform unsatisfactorily                                                                  multiple documents, a process known as multi-hop
                    in retrieving and answering multi-hop queries.arXiv:2401.15391v1                                                       query. For instance, consider financial analysis usWe hope MultiHop-RAG will be a valuable reing a database of financial reports. A financial ana-                  source for the community in developing effeclyst might query, Which company among Google,                     tive RAG systems, thereby facilitating greater
                 adoption of LLMs in practice. The MultiHop-       Apple, and Nvidia reported the largest profit marRAG and implemented RAG system is publicly       gins in their third-quarter reports for 2023? or
                    available at https://github.com/yixuantt/       inquire about a specific company’s performance
                MultiHop-RAG/.                               over time, such as How does Apple’s sales trend
                                                              look over the past three years? These queries re1  Introduction
                                                                  quire evidence from multiple documents to formuThe emergence of large language models (LLMs),    late an answer. Due to the multifaceted nature of
            such as ChatGPT, has fostered a wide range of inno-   such queries, involving information from various
              vations, powering intelligent chatbots and other nat-   sources, traditional similarity matching methods
              ural language processing (NLP) applications (Ope-    like cosine similarity between query and financial
 News source     Fortune Magazine                            The Sydney Morning Herald
 Evidence       Back then, just like today, home prices had boomed  Postponements of such reports could complicate
                    for years before Fed officials were ultimately forced   things for the Fed, which has insisted it will make
                    to hike interest rates aggressively in an attempt to  upcoming decisions on interest rates based on what
                      fight inflation.                                  incoming data say about the economy.
 Claim            Federal Reserve officials were forced to aggressively  The Federal Reserve has insisted that it will base its
                  hike interest rates to combat inflation after years of  upcoming decisions on interest rates on the incoming
                booming home prices.                           economic data.
 Bridge-Topic     Interest rate hikes to combat inflation                   Interest rate decisions based on economic data
 Bridge-Entity    Federal Reserve                                    Federal Reserve
 Query         Does the article from Fortune suggest that the Federal Reserve’s interest rate hikes are a response to past
                   conditions, such as booming home prices, while The Sydney Morning Herald article indicates that the
                  Federal Reserve’s future interest rate decisions will be based on incoming economic data?
 Answer         Yes

Table 1: An example of a multi-hop query, including supporting evidence from two news articles, the paraphrased
claim, the bridge-topic and bridge-entity, and the corresponding answer.

report chunk embeddings might not yield optimal    factual sentences from each news article as eviresults. We demonstrate this multi-hop retrieval    dence. For example, an extracted piece of evidence
process in Figure 1.                            from an article may state: “Back then, just like
  However, existing RAG benchmarks, such as    today, home prices had boomed for years before
RGB (Chen et al., 2023) and RECALL (Liu et al.,   Fed officials were ultimately forced to hike interest
2023), mainly evaluate a simple case where the an-    rates aggressively in an attempt to fight inflation.”
swer of a query can be retrieved and solved using   Second, we input each evidence piece into GPT-4,
one single piece of evidence. None of these bench-   prompting it to rephrase the evidence into a claim.
marks assess the retrieval and reasoning capability   This claim is clarified with a disambiguated topic
of LLMs for complex multi-hop queries. To ad-   and entity. For instance, GPT-4 might rephrase the
dress this gap and make RAG benchmarking more   aforementioned evidence into: “Federal Reserve
closely resemble real-world scenarios, in this paper,    officials were forced to aggressively hike interest
we introduce MultiHop-RAG. To our knowledge,    rates to combat inflation after years of booming
MultiHop-RAG is one of the first RAG datasets   home prices”, identifying “Interest rate hikes to
focusing specifically on multi-hop queries.         combat inflation” as the topic and “Federal Reserve” as the entity. These topics and entities act as  Based on the RAG queries commonly encounbridges for constructing multi-hop queries, knowntered in real-world scenarios, we first categorize
                                                     as bridge-topic or bridge-entity. Next, we use GPT-multi-hop queries into four types: Inference query,
                                           4 to generate specific multi-hop queries related toComparison query, Temporal query, and Null
                                                    the same bridge-topic or bridge-entity, accompa-query. The first three types — Inference, Comnied by the correct answers. Lastly, we undertakeparison, and Temporal — require the retrieval and
                                                 a validation step to ensure the data quality.analysis of evidence from multiple sources, encompassing tasks like inferring relationships, compar-    We demonstrate the benchmarking capabilities
ing data points, and sequencing events over time.   of MultiHop-RAG using two experiments, utilizing
The Null query represents a scenario where the    a RAG system implemented with LlamaIndex (Liu,
query cannot be derived from the knowledge base.   2022). The first experiment involves a comparison
This category is crucial for assessing whether an    of different embedding models for retrieving releLLM might hallucinate an answer to a multi-hop    vant evidence for multi-hop queries. In the second
query when the retrieved text lacks relevance.        experiment, we assess the reasoning and answering
  We construct our RAG knowledge base using a     abilities of various state-of-the-art LLMs, including
collection of news articles. Using GPT-4 as a data   GPT-4, GPT-3.5, PaLM, Claude-2, Llama2-70B,
generator, we then take an extensive procedure to   and Mixtral-8x7B, for multi-hop queries when reconstruct a diverse set of multi-hop queries, each    trieved text is provided. The results from both exrequiring the retrieval and reasoning over multiple    periments indicate that the current RAG implemendocuments. An example of query construction is    tations are inadequate for effectively retrieving and
shown in Table 1.  First, we begin by extracting   answering multi-hop queries. We publicly release
this challenging MultiHop-RAG dataset and hope it    be: Which report discusses the supply chain risk of
will be a valuable resource for the community in de-   Apple, the 2019 annual report or the 2020 annual
veloping and benchmarking RAG systems, thereby    report?
unleashing the great potential of generative AI in   Comparison query: For such a query q, the anpractice.                                       swer requires a comparison of evidence within the
                                                           retrieval set Rq. For instance, a comparison query
2 RAG with multi-Hop queries                                             might ask: Did Netflix or Google report higher
                                                 revenue for the year 2023?"2.1  Retrieval-augmented Generation (RAG)
                                         Temporal query: For such a query q, the answerIn an RAG application, we utilize an external correquires an analysis of the temporal informationpus, denoted as D, which comprises multiple docuof the retrieved chunks. For example, a temporalments and serves as the knowledge base. Each docquery may ask: Did Apple introduce the AirTag
ument within this corpus, represented as di ∈D, is
                                                      tracking device before or after the launch of the 5th
segmented into a set of chunks.These chunks are
                                                  generation iPad Pro?
then transformed into vector representations using
an embedding model and stored in an embedding   Null query: For such as query q, the answer cannot
database. Given a user query q, the system typi-   be derived from the retrieved set Rq. We include
cally retrieves the top-K chunks that best match the    the null query to assess the generation quality, esquery. These chunks constitute the retrieval set    pecially regarding the issue of hallucination. For a
for query q, represented as Rq = {r1, r2, ..., rK}.    null query, even though a retrieved set is provided,
The retrieved chunks, combined with the query   an LLM should produce a null response instead
and an optional prompt, are then fed into an LLM    of hallucinating an answer. For example, assumto generate a final answer, following the format:   ing ABCD is a non-existent company, a null query
LLM(q, Rq, prompt) →answer.                   might ask: What are the sales of company ABCD
                                                 as reported in its 2022 and 2023 annual reports?


## 2.2  Multi-Hop Query

We define a multi-hop query as one that requires    2.3  Evaluation Metrics
retrieving and reasoning over multiple pieces of
                                    An RAG system handling multi-hop queries can besupporting evidence to provide an answer. In other
                                                    assessed from two key aspects: retrieval evaluationwords, for a multi-hop query q, the chunks in the
                                             and generation evaluation.retrieval set Rq collectively provide an answer
to q. For example, the query "Which company      Retrieval Evaluation: Evidently, the quality of
among Google, Apple, and Nvidia reported the    the retrieval set Rq determines the final generalargest profit margins in their third-quarter reports    tion quality. We compare the retrieved set with
for 2023?" requires 1) retrieving relevant pieces of    the ground truth evidence associated with each
evidence related to profit margins from the reports    query, except for the null queries, as they have
of the three companies; 2) generating an answer by   no evidence to derive from. Assuming the topcomparing and reasoning from the multiple pieces  K chunks are retrieved, i.e., |Rq| = K, we use
of retrieved evidence. This differs from a single-    retrieval evaluation metrics including Mean Averhop query such as "What is Google’s profit margin   age Precision at K (MAP@K), Mean Reciprocal
in the third-quarter reports for 2023," where the   Rank at K (MRR@K), and Hit Rate at K (Hit@K).
answer can be directly derived from a single piece  MAP@K measures the average top-K retrieval preof evidence.                                         cision across all queries. MRR@K calculates the
  Based on the queries commonly used in real-   average of the reciprocal ranks of the first relevant
world RAG systems, we identify four types of   chunk for each query, considering the top-K remulti-hop queries. For each type, we present a    trieved set. Hit@K metric measures the fraction of
hypothetical query within the context of a financial    evidence that appears in the top-K retrieved set.
RAG system, where the knowledge base consists     Response Evaluation:  Since the multi-hop
of a collection of annual reports.                  query requires reasoning over multiple pieces of
Inference query: For such a query q, the answer    retrieved chunks, we can also evaluate the reasonis deduced through reasoning from the retrieval    ing capability of the LLM by comparing the LLM
set Rq. An example of an inference query might    response with the ground truth answer of the query.
                                           news article is paired with metadata, including the
                                                                         title, publish date, author, category, URL, and news
                                                     source.
                                               Step 2: Evidence Extraction. For each article, we
                                                         extract factual or opinion sentences using a trained
                                                 language model 2. These factual sentences are later
                                               used as evidence for answering multi-hop queries.
                                We retain only those news articles containing evidence that may have overlapping keywords with
                                                    other news articles. This allows us to later create
                                                multi-hop queries where the answer’s evidences
                                                     are drawn from multiple sources.
                                               Step 3: Claim, Bridge-Entity, Bridge-Topic Generation. Our goal is to use GPT-4 to automatically
                                                  generate high-quality multi-hop queries using the
                                                 evidence set. However, the raw evidence obtained
                                            from Step 2 is not ideal for query generation due
                                                       to inconsistency in linguistic structure. For example, some pieces of evidence use pronouns to refer
                                                      to subjects and lack the actual entity in the text.   Figure 2: MultiHop-RAG Construction Pipeline.
                                         To address this, we employ GPT-4 to paraphrase
                                                    the evidence, which we refer to as claims, given
3 A Benchmarking Dataset:                   the original evidence and its context. To ensure
   MultiHop-RAG                             consistency between the generated claim and the
                                                   evidence, we further perform fact-checking usingIn this section, we provide detailed information
                                                      the UniEval (Zhong et al., 2022) framework to ver-on the construction of the MultiHop-RAG dataset.
                                                          ify the alignment between the evidence and claim.Specifically, we describe the process of creating a
                                           Appendix A presents the prompt used for GPT-4set of multi-hop queries, along with the correspondfor claim generation.ing ground truth evidence sets and answers derived
                                                Bridge-Entity and Bridge-Topic: The shared en-from a collection of news articles.
                                                                  tity or topic across pieces of evidence is referred to
3.1  MultiHop-RAG Construction                as the bridge-entity or bridge-topic. These bridgeStep 1: Dataset Collection. We download a news    entities or bridge-topics can be used to link difdataset using the mediastack API 1, a REST API in-    ferent pieces of evidence from which a multi-hop
                                                    query’s answer is derived. For example, in a claimterface delivering worldwide news data. The news
                                                such as “Google reports its third-quarter results fordata source comprises various English-language
                                                2023, showcasing a detailed overview of its finan-websites covering a range of news categories: encial performance, including revenue growth, profittertainment, business, sports, technology, health,
                                                margins”, the term profit margin can be viewed asand science. To mimic real-world RAG scenarios,
                                                 a bridge-topic and the term Google can be viewedwhere the knowledge base data, such as an enterprise’s internal data, may differ from the LLMs’   as a bridge-entity that links the different pieces of
training data, we select news articles published    evidence. We prompt GPT-4 to identify the bridgefrom September 26, 2023, to December 26, 2023.    entity and bridge-topic for each claim. Appendix A
                                                       also presents the prompt used for GPT-4 for bridgeThis timeframe extends beyond the knowledge cutoff of some widely-used LLMs, including Chat-   generation.
GPT and LLaMA, as of the time of writing. This   Step 4: Query and Answer Generation. In this
selection also helps in teasing out the possibility    step, we leverage the bridge-entity or bridge-topic
of the underlying LLM having been exposed to    to generate multi-hop queries. Specifically, we first
these news articles. We only keep articles with a   group the claims having the same bridge-entity or
token length greater than or equal to 1,024. Every
                                                                      2https://huggingface.co/lighteternal/fact-or-opinion-xlmr1https://mediastack.com/                                         el
bridge-topic into a claim set. We restrict the claim      Category    Avg. Tokens  Entry Count
set to have at least two claims but no more than four      technology      2262.3        172
claims. For each type of query, we feed the claim     entertainment     2084.3        114
set to GPT-4 and prompt it with an instruction to         sports        2030.6        211
generate a query with information from each claim.       science        1745.5        21
Below, we explain the specifications for different                                                     business       1723.8        81
multi-hop query types. In the construction of each                                                        health        1481.1        10
query, we also include the source of the news article                                                                 total         2046.5        609
where the supporting evidence is associated with
to mimic real-world RAG scenarios. Appendix    Table 2: Descriptive statistics of the news article knowlA presents the prompts used for GPT-4 for query    edge base in MultiHop-RAG.
generation.
                                               Query Category    Entry Count  Percentage   Inference Query: These queries are formulated
                                                        Inference Query       816       31.92%by synthesizing the various characterizations of the
                                               Comparison Query      856       33.49%bridge-entity across multiple claims, with the final
                                                 Temporal Query       583       22.81%answer being the identification of the entity itself.
                                                       Null Query         301       11.78%
  Comparison Query: These queries are strucTotal            2,556      100.00 %
tured to compare the similarities and differences
related to the bridge entity or topic. The resultant    Table 3: The distribution of query types in MultiHopanswer to such queries is typically a definitive “yes”   RAG.
or “no”, based on the comparison.
  Temporal Query: These queries explore the


## 3.2  Descriptive Statistics
temporal ordering of events across different points

in time. The answer to such queries is typically a   The MultiHop-RAG dataset contains six different
“yes” or “no” or a single temporal indicator word    types of news articles, covering 609 distinct news,
like “before” or “after”.                            with an average of 2,046 tokens. The distribution of
                                                      the news categories is shown in Table 2. MultiHop-  Null Query: Null query is a query whose anRAG contains four types of multi-hop queries andswer cannot be derived from the retrieved set. To
                                                     the distribution of these queries is shown in Tablecreate null queries, we generate multi-hop queries
                                                          3. In total, about 88% of queries in the dataset areusing entities that do not exist in the existing bridgenon-null queries where answers can be retrievedentities. To add complexity, we also include ficand reasoned from the knowledge base. In addition,tional news source metadata when formulating
                                                     the form of queries exhibits considerable diversity.these questions, ensuring that the questions do not
                                              Approximately 27% of interrogative queries startreference any contextually relevant content from
                                                with "does," around 15% initiate with "what," athe knowledge base. The answer to the null query
                                                      similar proportion start "which," and 14% beginshould be “insufficient information” or similar.
                                                with "who," with the remainder incorporating a
Step 5: Quality Assurance. Finally, we use two
                                                   small percentage of other interrogative words such
approaches to reassure the dataset quality. First, we
                                                   as "when." Moreover, the number of evidence remanually review a subset sample of the generated
                                                  quired to answer a multi-hop query varies. Table
multi-hop queries, their corresponding evidence


# 4 shows the distribution of evidence numbers for

sets, and the final answers. The results of the maneach query in the dataset. Around 42% of queries
ual examination indicate a high degree of accuracy
                                              can be answered using two pieces of evidence,
and data quality. Second, we utilize GPT-4 to aswhile approximately 30% and 15% of queries can
sess each example in the dataset against the followbe answered using three or four pieces of evidence,
ing criteria: 1) The generated query must utilize
                                                         respectively.
all provided evidence in formulating the response;
2) The query should be answerable solely based                                        4  Benchmarking RAG system using
on the provided evidence; 3) The response to the                                      MultiHop-RAG
generated query should be either a single word or
a specific entity; 4) The query must conform to its   MultiHop-RAG can be used as a benchmark for vardesignated query type.                              ious RAG-related tasks. Broadly speaking, RAGNum. of Evidence Needed  Count  Percentage     bedding model, we further select the top-K chunks
      0 (Null Query)        301    11.78%       using the Reranker.
           2             1078    42.18%                                          Experiment Result: Table 5 shows the retrieval
           3             779    30.48%                                                         result of using different embedding models.   It
           4             398    15.56%                                            shows that there is still a significant gap in retrievTotal            2,556   100.00 %
                                                  ing relevant evidence for the multi-hop queries.
                                             While Rerank can effectively improve retrieval rel-Table 4: The distribution of the number of evidence
required to answer multi-hop queries in MultiHop-RAG.    evance, the highest Hits@10 is only 0.7467 when
                                                      the Reranker technique is used. Moreover, the drop
                                                      in the highest Hits@4 to 0.6625 is worrisome. In
related tasks can be categorized as retrieval-related    practical RAG systems, the underlying LLM oftasks and generation-related tasks. A retrieval-   ten has a context window limit. As a result, the
related task focuses on retrieving relevant text from   number of retrieved chunks is usually restricted to
the knowledge base, while a generation-related task   a small number. The low values of the retrieval
focuses on generating high-quality responses given    metrics highlight the challenges in retrieving relethe retrieved text. In this section, we showcase two    vant pieces of evidence for multi-hop queries when
use cases for each task where MultiHop-RAG can    using direct similarity matching between the multibe employed.                                hop query and text chunks.

4.1  Retrieval-related Task                                                    4.2  Generation-related Task
An important design choice in an RAG system is
                                         The underlying LLMs play a crucial role in genthe selection of the embedding model. An embederating responses in an RAG system. In this exding model converts data into numerical vectors
                                                  periment, we evaluate the quality of generated reand subsequently stores these vectors in embedding
                                                sponses under two different settings. In the first
databases. In this experiment, we evaluate differsetting, we employ the best-performing retrieval
ent embedding models by examining their retrieval
                                                model, namely voyage-02 with bge-reranker-large,
quality.
                                                   as indicated in Table 5, to retrieve the top-K texts
Experiment Setup: We implement an RAG sysand then feed them into the LLM. In the second
tem using the LlamaIndex framework (Liu, 2022).
                                                          setting, we use the ground-truth evidence associWe partition the documents in the MultiHop-RAG
                                                   ated with each query as the retrieved text for the
knowledge base into chunks, each consisting of 256
                                     LLM. This setting represents a ceiling performance
tokens. We then convert the chunks using an emfor testing the LLM’s response capabilities, as it
bedding model and save the embeddings into a vecutilizes the actual evidences.
tor database. Similarly, in the retrieval step, we conExperiment Setup: In the first experiment, we
vert a query using the same embedding model and
                                                          retrieve top-6 chunks so that the total length of the
retrieve the top-K most relevant chunks that have
                                                      retrieved text does not exceed 2,048. All queries
the highest cosine similarity with the query embedin MultiHop-RAG are tested in the experiment.
ding. In this experiment, we test a variety set of emIn the second experiment, since the null queries
bedding models, including the ada-embeddings by
                                          do not have associated evidence, we exclude this
OpenAI (text-embedding-ada-002, text-search-adatype of query in the experiment. For the LLMsquery-001), voyage-02 3, llm-embedder (Zhang
                                              used in the experiment, we consider state-of-theet al., 2023), bge-large-en-v1.5 (Xiao et al., 2023),
                                                              art commercial models, including GPT-4 (OpenAI,
jina-embeddings-v2-base-en (Günther et al., 2023),
                                                  2023), GPT-3.5, Claude-2 (Anthropic, 2023), and
e5-base-v2 (Wang et al., 2022), and instructor-large
                                          Google-PaLM (Google, 2023). We obtain answers
(Su et al., 2023). NULL queries are excluded in
                                                 using the provided API of the respective models.
this experiment because there is no matching eviWe also assess some open-source models, includdence to the query. Additionally, we also include
                                                  ing Mixtral-8x7b-instruct (Jiang et al., 2024) and
a Reranker module to examine the retrieval perforLlama-2-70b-chat-hf (Touvron et al., 2023).
mance, using bge-reranker-large (Xiao et al., 2023).
                                           Experiment Results: Table 6 shows the responseAfter retrieving 20 related chunks using the emaccuracy of different LLMs.  First, we can see
   3https://www.voyageai.com/                             that the response accuracy rate using the retrieved
                                        Without Reranker                      With bge-reranker-large
 Embedding
                   MRR@10  MAP@10  Hits@10  Hits@4  MRR@10  MAP@10  Hits@10  Hits@4

 text-embedding-ada-002         0.4203     0.3431    0.6381    0.504     0.5477     0.4625    0.7059   0.6169
 text-search-ada-query-001       0.4203     0.3431    0.6399   0.5031     0.5483     0.4625    0.7064   0.6174
 llm-embedder                  0.2558     0.1725    0.4499   0.3189       0.425     0.3059    0.5478   0.4756
 bge-large-en-v1.5               0.4298     0.3423    0.6718   0.5221       0.563     0.4759    0.7183   0.6364
 jina-embeddings-v2-base-en     0.0621       0.031    0.1479   0.0802     0.1412     0.0772    0.1909   0.1639
 intfloat/e5-base-v2              0.1843     0.1161    0.3556   0.2334     0.3237     0.2165    0.4176   0.3716
 voyage-02                     0.3934     0.3143    0.6506   0.4619       0.586     0.4795    0.7467   0.6625
 hkunlp/instructor-large          0.3458       0.265    0.5717   0.4229     0.5115     0.4118     0.659   0.5775

                       Table 5: Retrieval performance of different embedding models.

                                   Accuracy
 Models
                         Retrieved Chunk  Ground-truth Chunk

 GPT-4                       0.56                0.89
 ChatGPT                    0.44                0.57
 Llama-2-70b-chat-hf         0.28                0.32
 Mixtral-8x7B-Instruct        0.32                0.36
 Claude-2.1                  0.52                0.56
 Google-PaLM               0.47                0.74

       Table 6: Generation accuracy of LLMs.

chunks is not satisfactory, with the state-of-theart GPT-4 model achieving only 0.56 accuracy.
This is expected, because the retrieval component
falls short in retrieving relevant evidences from the
knowledge base. Second, even when we provide
the LLM with the ground-truth evidences, we can    Figure 3: Generation accuracy for different query types.
see that the response accuracy is far from being perfect. Open source LLM such as Llama02-70B and                                                     the chronological order of events, which is crucial
Mixtral-8x7B only achieve an accuracy of 0.32 and                                                      for answering temporal queries where timing is a
0.36 respectively. GPT-4 achieves strong reason-                                              key factor. Taken together, this experiment demoning capability with an accuracy of 0.89, followed                                                          strates that there is still room for improvement in
by the second-based LLM Google-PaLM with an                                                    the reasoning capabilities of LLMs, particularly
accuracy of 0.74.                                                   those that are open-source, for multi-hop queries.
  Figure 3 shows the detailed results of different
                                                    4.3  Other Use Casesquery types for GPT-4 and Mixtral-8x7B-instruct.
Both models show relatively high robustness on   Beyond embedding models and LLM generation,
null queries, meaning they are generally good at    there are other areas worth exploring. For examdetermining when a query cannot be answered    ple, query decomposition is a widely utilized techbased on the retrieved text. This is encouraging be-   nique in RAG frameworks, such as LLamaIndex.
cause one benefit of RAG is to mitigating the LLM   This process involves breaking down the query
hallucination issue by augmenting LLM with re-    into smaller segments; it targets a single document
trieval knowledge. However, Mixtral-8x7B model    for retrieval and integrates the information subseperforms significantly worse than the GPT-4 in    quently, thereby potentially enhancing retrieval accomparison and temporal queries. Upon reviewing    curacy. Another advanced and promising approach
the incorrect responses, we find that Mixtral-8x7B    involves building LLM-based agents that can aufails to accurately handle logical negation, leading    tomatically plan and execute multi-hop queries,
to misinterpretation of statements and thus a low   such as AutoGPT (Gravitas, 2023). Another area
performance in the comparison queries. In addi-   of interest is the hybrid retrieval approach, which
tion, Mixtral-8x7B often fails to correctly identify   combines keyword and embedding matching techniques. We believe that there are many potential    large knowledge base. Separately, (Kamalloo et al.,
areas for enhancing RAG’s performance on multi-   2023) evaluates a range of commercial embedding
hop queries, and the curated dataset MultiHop-   APIs for information retrieval, but this evaluation
RAG can be a valuable resource to the community.    is not contextualized within the framework of RAG
                                                systems either.
5  Related Work                          Multi-document QA  datasets:    Questionanswering (QA) is a fundamental task in NLP, and
RAG Evaluation: As RAG systems gain increas-                                                     several popular benchmarks, such as HotpotQA
ing popularity, a variety of RAG benchmarking                                            (Yang et al., 2018), MultiRC (Khashabi et al.,
datasets and evaluation tools have been developed.                                                 2018), and 2WikiMultiHopQA (Ho et al., 2020),
For instance, RGB (Chen et al., 2023) and RE-                                          aim to achieve QA from multiple sources of
CALL (Liu et al., 2023) evaluate the performance                                              documents. This task is similar to our multi-hop
of LLMs in generating responses for RAG systems                                               query RAG task, as both involve reasoning from
under conditions involving noisy, integrative, and                                                   multiple sources of information. However, these
counterfactual queries. However, both datasets pri-                                                      datasets primarily focus on assessing a model’s
marily focus on evaluating the generation aspect                                                 reasoning skills, and they do not emphasize the
of RAG systems without specifically addressing                                                          retrieval of evidence from a knowledge base.
their retrieval accuracy.  In addition, recent ad-                                                       Additionally, their primary data sources Wikipedia,
vancements have been made in automated RAG                                                        significantly overlap with the training data of
evaluation tools, such as ARES (Saad-Falcon et al.,                                            most existing LLMs. If we use these sources for
2023) and RAGAS (Es et al., 2023). These tools                                            benchmarking RAG systems, there is a potential
utilize LLMs to automatically assess the quality of                                                 concern that LLM responses might rely on training
RAG generation, yet they do not introduce bench-                                              knowledge rather than reasoning from the retrieved
marking datasets. Our work introduces one of the                                             knowledge base.
first RAG benchmarking datasets, consisting of a
knowledge base, a large collection of multi-hop   6  Conclusion
queries, their ground-truth answers, and the associIn this work, we introduce MultiHop-RAG, a novelated supporting evidence, thereby complementing
                                            and unique dataset designed for queries that re-existing RAG evaluations.
                                                    quire retrieval and reasoning from multiple pieces
Retrieval datasets: Apart from the context of
                                                   of supporting evidence. These types of multi-hop
RAG, several benchmarking datasets exist for inqueries represent user queries commonly encounformation retrieval evaluation. The FEVER (Fact
                                                       tered in real-world scenarios. MultiHop-RAG conExtraction and VERification) dataset, for instance,
                                                             sists of a knowledge base, a large collection of
contains claims classified as Supported, Refuted,
                                                  multi-hop queries, their ground-truth answers, and
or NotEnoughInfo by the given Wikipedia article
                                                    the associated supporting evidence.  This paper
(Thorne et al., 2018). Similarly, the SciFact dataset
                                                           details the creation process of MultiHop-RAG, emcomprises scientific claims paired with evidenceploying a hybrid approach that integrates human
containing abstracts (Wadden et al., 2020). Howeffort with GPT-4. Additionally, we explore two
ever, the claims in both datasets are single-hop
                                                use cases of MultiHop-RAG in the benchmarking
statements, and the supporting evidence is from one
                                                     of RAG systems, thereby highlighting the potential
single article, in contrast to the multi-hop queries
                                                     applications of this dataset. By publicly releasdiscussed in this paper. Another dataset, HoVer,
                                                  ing MultiHop-RAG, we aim to provide a valuable
involves claims that require extracting and reasonresource to the community, contributing to the ading from multiple Wikipedia articles (Jiang et al.,
                                             vancement and benchmarking of RAG systems.
2020). However, unlike our dataset, HoVer focuses
solely on classifying claims as either supported or                                            Limitations
not supported by the articles without evaluating
an LLM generation step. Moreover, in HoVer, the   This work has several limitations that can be imWikipedia articles from which evidence is drawn   proved in future research. First, our ground truth
are given for claim verification, which is signifi-   answers are restricted to simple responses such as
cantly different from our setting, where relevant   “yes", “no", entity names, or temporal indicators
pieces of evidence need to be extracted from a    like “before" or “after" to facilitate the use of a
straightforward accuracy metric for evaluating gen-   Michael Günther, Jackmin Ong, Isabelle Mohr, Alaederation performance. Future work could consider      dine Abdessalem, Tanguy Abel, Mohammad Kalim
                                                 Akram, Susana Guzman, Georgios Mastrapas, Sabaallowing free text as answers and employing more
                                                           Sturua, Bo Wang, Maximilian Werk, Nan Wang,
sophisticated metrics to assess generation quality.     and Han Xiao. 2023.  Jina embeddings 2: 8192Second, the current dataset limits supporting ev-      token general-purpose text embeddings for long docidence for a query to a maximum of four pieces.      uments.
Future work can extend the dataset by including
                                           Xanh Ho, Anh-Khoa Duong Nguyen, Saku Sugawara,
queries that require retrieving and reasoning from                                                  and Akiko Aizawa. 2020.  Constructing a multieven more evidence. Lastly, while our experiments     hop QA dataset for comprehensive evaluation of
utilize a basic RAG framework using LlamaIndex,      reasoning steps.  In Proceedings of the 28th Interfuture work could involve evaluating the answering       national Conference on Computational Linguistics,
                                                      pages 6609–6625, Barcelona, Spain (Online). Interof multi-hop queries using more advanced RAG
                                                             national Committee on Computational Linguistics.
frameworks or LLM-agent frameworks.
                                                      Albert Q. Jiang, Alexandre Sablayrolles, Antoine
                                                  Roux,  Arthur Mensch,  Blanche  Savary,  Chris
References                                       Bamford, Devendra Singh Chaplot, Diego de las
                                                        Casas, Emma Bou Hanna, Florian Bressand, GiAnthropic. 2023. Claude 2.1 (May version). https:                                                   anna Lengyel, Guillaume Bour, Guillaume Lam-
  //api.anthropic.com/v1/messages. Claude 2.1.                                                                  ple, Lélio Renard Lavaud, Lucile Saulnier, MarieAnne Lachaux, Pierre Stock, Sandeep Subramanian,
Akari Asai, Sewon Min, Zexuan Zhong, and Danqi                                                    Sophia Yang, Szymon Antoniak, Teven Le Scao,
  Chen. 2023. Retrieval-based language models and                                                      Théophile Gervet, Thibaut Lavril, Thomas Wang,
   applications. In Proceedings of the 61st Annual MeetTimothée Lacroix, and William El Sayed. 2024. Mixing of the Association for Computational Linguistics
                                                                          tral of experts.
  (Volume 6: Tutorial Abstracts), pages 41–46.

                                                 Yichen Jiang, Shikha Bordia, Zheng Zhong, CharlesSebastian Borgeaud, Arthur Mensch, Jordan HoffDognin, Maneesh Singh, and Mohit Bansal. 2020.  mann, Trevor Cai, Eliza Rutherford, Katie MilliHoVer: A dataset for many-hop fact extraction and   can, George Bm Van Den Driessche, Jean-Baptiste
                                                        claim verification. In Findings of the Conference on   Lespiau, Bogdan Damoc, Aidan  Clark, Diego
                                                        Empirical Methods in Natural Language Processing  De Las Casas, Aurelia Guy, Jacob Menick, Roman
                                               (EMNLP).  Ring, Tom Hennigan, Saffron Huang, Loren Maggiore, Chris Jones, Albin Cassirer, Andy Brock,
  Michela Paganini, Geoffrey Irving, Oriol Vinyals,   Ehsan Kamalloo, Xinyu Zhang, Odunayo Ogundepo,
  Simon Osindero, Karen Simonyan, Jack Rae, Erich     Nandan Thakur, David Alfonso-Hermelo, Mehdi
   Elsen, and Laurent Sifre. 2022. Improving language      Rezagholizadeh, and Jimmy Lin. 2023.  Evaluatmodels by retrieving from trillions of tokens.  In      ing embedding apis for information retrieval. arXiv
  Proceedings of the 39th International Conference       preprint arXiv:2305.06300.
  on Machine Learning, volume 162 of Proceedings
   of Machine Learning Research, pages 2206–2240.   Daniel Khashabi, Snigdha Chaturvedi, Michael Roth,
  PMLR.                                    Shyam Upadhyay, and Dan Roth. 2018. Looking
                                               Beyond the Surface: A Challenge Set for Reading
Harrison Chase. 2022. LangChain.                      Comprehension over Multiple Sentences. In Proc. of
                                                             the Annual Conference of the North American ChapJiawei Chen, Hongyu Lin, Xianpei Han, and Le Sun.       ter of the Association for Computational Linguistics
  2023.  Benchmarking large language models in      (NAACL).
   retrieval-augmented generation.
                                                           Jerry Liu. 2022. LlamaIndex.
Shahul Es, Jithin James, Luis Espinosa-Anke, and
  Steven Schockaert. 2023. Ragas: Automated evalua-                                                   Yi Liu, Lianzhe Huang, Shicheng Li, Sishuo Chen, Hao
   tion of retrieval augmented generation.                                                   Zhou, Fandong Meng, Jie Zhou, and Xu Sun. 2023.
                                                            Recall: A benchmark for llms robustness againstTianyu Gao, Howard Yen, Jiatong Yu, and Danqi Chen.
                                                              external counterfactual knowledge.  2023. Enabling large language models to generate
   text with citations.
                                                OpenAI. 2023. GPT4 (Nov 7 version). https://chat.
Google.  2023.     PaLM  2  (May   version).     openai.com/chat. gpt-4-1106-preview.
  https://generativelanguage.googleapis.
  com/v1beta2/models/. Chat-bison-002.             Jon Saad-Falcon, Omar Khattab, Christopher Potts, and
                                                    Matei Zaharia. 2023. Ares: An automated evaluaSignificant Gravitas. 2023. Autogpt. https://github.      tion framework for retrieval-augmented generation
  com/Significant-Gravitas/AutoGPT.                 systems.
Hongjin Su, Weijia Shi, Jungo Kasai, Yizhong Wang,      Jiawei Han. 2022.   Towards a  unified  multiYushi Hu, Mari Ostendorf, Wen tau Yih, Noah A.      dimensional evaluator for text generation.
  Smith, Luke Zettlemoyer, and Tao Yu. 2023. One
  embedder, any task: Instruction-finetuned text em-  A  Appendix A: GPT-4 Prompts Used for
   beddings.                                          Data Generation
James   Thorne,   Andreas   Vlachos,    Christos
                                  We present the prompts used for guiding GPT-4 for   Christodoulopoulos,  and  Arpit  Mittal.  2018.
   Fever: a large-scale dataset for fact extraction and    data generation. Table 7 shows the prompt used for
   verification.                                     claim generation, along with the corresponding topics and entities within these claims. Table 8, TableHugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yasmine Babaei, Nikolay    9, and Table 10 respectively show the prompts used
   Bashlykov, Soumya Batra, Prajjwal Bhargava, Shruti    for generating multi-hop queries of the inference,
   Bhosale, Dan Bikel, Lukas Blecher, Cristian Canton   comparison, and temporal types.
   Ferrer, Moya Chen, Guillem Cucurull, David Esiobu,
  Jude Fernandes, Jeremy Fu, Wenyin Fu, Brian Fuller,                              B  Appendix B: Dataset Examples
  Cynthia Gao, Vedanuj Goswami, Naman Goyal, Anthony Hartshorn, Saghar Hosseini, Rui Hou, Hakan                                                   In this appendix, we present an example of each
   Inan, Marcin Kardas, Viktor Kerkez, Madian Khabsa,
                                                  type of multi-hop query included in the MultiHop-   Isabel Kloumann, Artem Korenev, Punit Singh Koura,
  Marie-Anne Lachaux, Thibaut Lavril, Jenya Lee, Di-  RAG dataset. These examples are illustrated in the
  ana Liskovich, Yinghai Lu, Yuning Mao, Xavier Mar-   respective tables: Table 12 for Inference Queries,
   tinet, Todor Mihaylov, Pushkar Mishra, Igor Moly-   Table 13 for Comparison Queries, Table 14 for
  bog, Yixin Nie, Andrew Poulton, Jeremy ReizenTemporal Queries, and Table 15 for Null Queries.   stein, Rashi Rungta, Kalyan Saladi, Alan Schelten,
  Ruan Silva, Eric Michael Smith, Ranjan Subrama-   Each query is paired with a ground-truth answer
   nian, Xiaoqing Ellen Tan, Binh Tang, Ross Tay-    for the evaluation of generation accuracy, while
   lor, Adina Williams, Jian Xiang Kuan, Puxin Xu,    multiple pieces of supporting evidence are included
  Zheng Yan, Iliyan Zarov, Yuchen Zhang, Angela Fan,
                                                      for assessing retrieval performance. Additionally,
  Melanie Kambadur, Sharan Narang, Aurelien Rodriguez, Robert Stojnic, Sergey Edunov, and Thomas   metadata such as the title, source, and publication
  Scialom. 2023. Llama 2: Open foundation and fine-   time of the news articles are provided as references.
  tuned chat models.

David Wadden, Shanchuan Lin, Kyle Lo, Lucy Lu
  Wang, Madeleine van Zuylen, Arman Cohan, and
  Hannaneh Hajishirzi. 2020. Fact or fiction: Verifying
   scientific claims. In Proceedings of the 2020 Conference on Empirical Methods in Natural Language
  Processing (EMNLP), pages 7534–7550, Online. Association for Computational Linguistics.

Liang Wang, Nan Yang, Xiaolong Huang, Binxing
   Jiao, Linjun Yang, Daxin Jiang, Rangan Majumder,
  and Furu Wei. 2022. Text embeddings by weaklysupervised contrastive pre-training. arXiv preprint
  arXiv:2212.03533.

Shitao Xiao, Zheng Liu, Peitian Zhang, and Niklas
  Muennighoff. 2023.  C-pack: Packaged resources
   to advance general chinese embedding.

Zhilin Yang, Peng Qi, Saizheng Zhang, Yoshua Bengio, William W. Cohen, Ruslan Salakhutdinov, and
   Christopher D. Manning. 2018. HotpotQA: A dataset
   for diverse, explainable multi-hop question answering. In Conference on Empirical Methods in Natural
  Language Processing (EMNLP).

Peitian Zhang, Shitao Xiao, Zheng Liu, Zhicheng Dou,
  and Jian-Yun Nie. 2023. Retrieve anything to augment large language models.

Ming Zhong, Yang Liu, Da Yin, Yuning Mao, Yizhu
   Jiao, Pengfei Liu, Chenguang Zhu, Heng Ji, and
A "claim" is a statement or assertion made within a text expressing a belief, opinion, or fact. Given
evidence from the original context, please extract one claim and its associated topics.

Note: The claim should not contain ambiguous references, such as ’he’,’ she,’ and’ it’, and should use
complete names. If there are multiple topics, give the most dominant one. The target of the claim (one
entity)is the specific individual, group, or organization that the statement or assertion within a text is
directed towards or about which it is making a case. The topic of the claim should be a simple phrase
representing the claim’s central argument concept. If there is no claim, please leave it blank. Please
generate a claim based on the given evidence. Don’t generate the evidence yourself.

Please give the response following this format:
Evidence: [original context]
Claims: [extract claim]
Claim Target: [target]
Claim Topic: [topic]

Here are examples:
<examples>
Now, it’s your turn.
<News>
<evidence>

                                 Table 7: Claim Generation Prompting

A multi-hop question is a query requiring multiple inferential leaps or accessing several pieces of
information from different locations or sources to arrive at an answer. The following are news articles’
metadata and claims come from the articles. All the claims from the article are related to a similar
target. Your task is to generate one multi-hop inference question based on the claims. Here are some
instructions:
1. Find the Connection: The connection between claims is <target>, which is how these key pieces of
information are related or how they can be combined to form a more complex idea.
2. Formulate the Question: Create a question that cannot be answered by relying on just one of the
sentences but instead requires understanding and linking the information from all of the sources. The
answer is <target>.
3. Ensure Coherence: Make sure the question flows logically from the combined information and is
clear and unambiguous.
4. Use the keywords: <key set>

<examples>
Context:
<Context>

                             Table 8: Inference Query Generation Prompting
<Context>

The above are news articles’ metadata and claims come from the articles. All the claims from the
articles are related to a similar target. Your task is to generate one comparison question based on all the
claims from different sources. This question needs to compare some factual elements of the claims that
are explicitly stated to find where they agree or differ. The correct answer to this question is expressed
as a comparative adjective, a statement of alignment, a simple yes or no. To generate a comparative
question from claims, you need to use the following keywords: <key set>

The Good Comparison Questions:
<examples>
Your Comparison Question:

                           Table 9: Comparison Query Generation Prompting

<Context>

Please create a time-sensitive comparison question using metadata and excerpts from multiple news
articles. That is to compare the consistency or sequence of reports on similar topics at multiple different
time points. If it is to compare the consistency, please clearly mention the news source and time in the
question using <time frame>. If it is to compare sequences of reports, just clearly mention the news
source and do not mention the timeline. Utilize the following keywords provided in the <key set> to
construct the question. The correct answer should based on the factual excerpts and is only one word.

<examples>
Your time-sensitive comparison question:

                            Table 10: Temporal Query Generation Prompting

A multi-hop question is a query requiring multiple inferential leaps or accessing several pieces of
information from different locations or sources to arrive at an answer. Considering you have read
at least two news articles on <entity>, construct a multi-hop question that incorporates all the news
sources. The source of the news should be stated in the question. Also, ensure that the answer to the
question is a single word/entity. Do not answer this question directly. Just give me the question:

                              Table 11: Null Query Generation Prompting
Query: Which platform is at the center of discussions in articles from Music Business Worldwide,
Polygon, and FOX News - Health, concerning the policing of AI-driven voice replication, the debate
over "reaction" content, and being the most used app overnight by young people?
Answer: YouTube
Evidence List:
Title: Sony Music’s artists aren’t involved in YouTube’s new voice-cloning AI experiment.
Source: Music Business Worldwide
Published Time: 2023-11-23T18:48:48+00:00
Fact: During this period of discussion, YouTube has made a number of positive announcements
regarding the biggest issue for any rightsholder regarding AI-driven voice replication of artists: their
ability to police it.

Title: YouTube demonetizes popular content creator SSSniperwolf after doxxing accusations
Source: Polygon
Published Time: 2023-10-25T18:18:06+00:00
Fact: The debate over "reaction" content on YouTube has been brewing for years, but a recent incident
between two creators has refueled the urgency of the conversation.

Title: Cell phone shocker as 97% of kids use their device during school hours and beyond, says study
Source: FOX News - Health
Published Time: 2023-10-01T09:05:26+00:00
Fact: Overnight phone use was primarily spent engaging with the same media, although YouTube
appeared to be the longest-running app because videos were often left playing during the night.

                              Table 12: The example of inference questions

Query: Did the Cnbc | World Business News Leader report on Nike’s net income and the article from
The Age on the 10-year Treasury yield both report a decrease in their respective financial metrics?
Answer: Yes
Evidence List:
Title: Nike misses revenue expectations for the first time in two years, beats on earnings and gross
margin
Source: Cnbc | World Business News Leader
Published Time: 2023-09-28T20:31:00+00:00
Fact: The company’s reported net income for the three-month period that ended August 31 was $1.45
billion, or 94 cents per share, compared with $1.47 billion, or 93 cents per share, a year earlier.

Title: ASX set to open higher as Wall Street rebounds; $A rises
Source: The Age
Published Time: 2023-10-04T21:01:01+00:00
Fact: The yield on the 10-year Treasury, which is the centrepiece of the bond market, pulled back from
its highest level since 2007, down to 4.73 per cent from 4.80 per cent late on Tuesday.

                             Table 13: The example of comparison questions
Query: Was the performance of the Chicago Bears’ defense reported as improved by Yardbarker after
Sporting News highlighted a sack by the Bears’ defense on Joshua Dobbs during the NFL ’Monday
Night Football’ game?
Answer: Yes
Evidence List:
Title: Bears vs. Vikings live score, updates, highlights from NFL ’Monday Night Football’ game
Source: Sporting News
Published Time: 2023-11-27T23:32:04+00:00
Fact: The Bears answer right back and sack Dobbs, with Sweat and Brisker in there to take him down.

Title: Hottest seat on each NFC team: Buns burning for these four head coaches
Source: Yardbarker
Published Time: 2023-11-30T22:29:33+00:00
Fact: In his second season as HC, the defense has improved, but positive results are hard to come by
behind a lackluster offense ranked 19th in yards (323.2) and 21st in points per game (20.2).

                           Table 14: The example of time-sensitive questions

Query: What is the first letter of the CEO’s last name in the news article from Bloomberg on TomTom,
and what is the first letter of the city where the company’s headquarters is located in the news article
from Reuters?
Answer: Insufficient information.

                          Table 15: The example of negative rejection questions

