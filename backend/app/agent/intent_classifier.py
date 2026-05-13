"""
Intent classifier with keyword rule fallback.

Priority: small model → keyword rules as fallback.
When confidence < 0.7, use keyword rules.
"""

import re

# Keyword rules for each intent
INTENT_RULES: list[tuple[str, list[str]]] = [
    ("paper_search", [
        r"找|搜|推荐|论文|paper|arxiv|检索",
        r"(给我|帮我|想要|需要).*(找|搜|推荐|检索)",
    ]),
    ("paper_collect", [
        r"收藏|保存|加入本地库|下载",
    ]),
    ("paper_parse", [
        r"解析|精读|总结全文|深度阅读|全文解析",
    ]),
    ("library_search", [
        r"(查看|查找|搜索).*(本地|已收藏|库)",
        r"本地.*(论文|文献)",
    ]),
    ("library_delete", [
        r"(删除|移除).*(论文|文献|paper)",
    ]),
    ("report_view", [
        r"(查看|打开).*(解析|报告|report|精读)",
    ]),
    ("report_delete", [
        r"(删除|移除).*(解析|报告|report)",
    ]),
    ("report_regenerate", [
        r"(重新|重新生成|再).*(解析|生成|报告|report)",
    ]),
    ("subscription_create", [
        r"每天|每周|定时|早上|推送|订阅|发送",
        r"(每天早上|每天早上|定时发送|每日推送)",
    ]),
    ("subscription_list", [
        r"(查看|列出).*(订阅|推送任务)",
    ]),
    ("subscription_delete", [
        r"(删除|取消).*(订阅|推送)",
    ]),
    ("trace_search", [
        r"流程|记录|报错|日志|任务|trace|追踪",
    ]),
]

# Typo correction map
TYPO_MAP: dict[str, str] = {
    "agnet": "agent",
    "agentic": "agent",
    "llm": "LLM",
    "rag": "RAG",
    "gpt": "GPT",
    "transformer": "Transformer",
    "bert": "BERT",
    "gcn": "GCN",
    "lstm": "LSTM",
    "cnn": "CNN",
    "rnn": "RNN",
    "gan": "GAN",
    "vae": "VAE",
    "nlp": "NLP",
    "cv": "CV",
}


def classify_intent(message: str) -> dict:
    """Classify user intent. Returns structured result with intent, confidence, entities."""
    message_lower = message.lower().strip()

    # Try keyword rules (used as primary for MVP, or fallback when no LLM)
    intent, confidence, entities = _keyword_classify(message_lower)

    return {
        "intent": intent,
        "confidence": confidence,
        "entities": entities,
    }


def _keyword_classify(message: str) -> tuple[str, float, dict]:
    """Keyword-based intent classification."""
    scores: dict[str, float] = {}

    for intent_name, patterns in INTENT_RULES:
        score = 0.0
        for pattern in patterns:
            if re.search(pattern, message):
                score += 0.5
        if score > 0:
            scores[intent_name] = min(score, 1.0)

    if not scores:
        return ("general_chat", 0.5, {})

    best_intent = max(scores, key=scores.get)
    confidence = scores[best_intent]

    entities = _extract_entities(best_intent, message)

    return (best_intent, confidence, entities)


def _extract_entities(intent: str, message: str) -> dict:
    """Extract entities from message based on intent."""
    entities: dict = {}

    # Extract top_n
    top_n_match = re.search(r"(\d+)\s*[篇个]", message)
    if top_n_match:
        entities["top_n"] = int(top_n_match.group(1))
    else:
        entities["top_n"] = 2

    # Extract candidate_k
    cand_match = re.search(r"候选[池]?\s*(\d+)|从\s*(\d+)\s*篇", message)
    if cand_match:
        entities["candidate_k"] = int(cand_match.group(1) or cand_match.group(2))
    else:
        entities["candidate_k"] = 20

    # Extract topic
    if intent == "paper_search":
        topic = _extract_topic(message)
        if topic:
            entities["topic"] = topic

    # Extract time for subscription
    if intent in ("subscription_create", "subscription_update"):
        time_match = re.search(r"(\d{1,2})[点:：](\d{2})?", message)
        if time_match:
            h = time_match.group(1)
            m = time_match.group(2) or "00"
            entities["schedule"] = {
                "type": "daily",
                "time": f"{int(h):02d}:{m}",
                "timezone": "Asia/Shanghai",
            }

        # Extract channels
        entities["channels"] = {}
        if re.search(r"邮箱|邮件|email|mail", message):
            entities["channels"]["email"] = {"enabled": True, "to": ""}
        if re.search(r"飞书|feishu|lark", message):
            entities["channels"]["feishu"] = {"enabled": True, "target": ""}

    return entities


def _extract_topic(message: str) -> str:
    """Extract research topic from message."""
    # Pattern: "关于 X 的" or "关于 X"
    match = re.search(r"关于\s*(.+?)\s*[的论文]", message)
    if match:
        return normalize_query(match.group(1))

    # Pattern: "找 X 论文" or "搜 X"
    match = re.search(r"[找搜推荐].*?(\S+)\s*(论文|paper)", message)
    if match:
        return normalize_query(match.group(1))

    return ""


def normalize_query(query: str) -> str:
    """Normalize query by fixing typos and standardizing terms."""
    words = query.split()
    normalized = []
    for word in words:
        word_lower = word.lower()
        if word_lower in TYPO_MAP:
            normalized.append(TYPO_MAP[word_lower])
        else:
            normalized.append(word)
    return " ".join(normalized)
