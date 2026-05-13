"""Report tool: generate card summaries and deep reading reports."""

import os
import re
import json
from datetime import datetime
from app.core.config import settings
from app.core.logging import logger
from app.storage.file_manager import FileManager
from app.tools.llm_client import llm_client
from app.agent.prompts import (
    CARD_SUMMARY_SYSTEM,
    build_card_summary_prompt,
    DEEP_REPORT_SYSTEM,
)


class ReportTool:
    def __init__(self):
        self.file_manager = FileManager()

    async def generate_card_summary(
        self,
        paper: dict,
        query: str = "",
        language: str = "zh-CN",
    ) -> dict:
        """Generate card summary. Uses LLM when available, falls back to regex."""
        abstract = paper.get("abstract", "")
        title = paper.get("title", "")

        # Try LLM first
        if llm_client.available:
            llm_result = await self._llm_card_summary(title, abstract, query)
            if llm_result.get("success"):
                return {"success": True, "summary": llm_result["summary"]}

        # Fallback to regex extraction
        summary = self._extract_summary(abstract)
        core_problem = self._extract_core_problem_statement(abstract)
        method = self._extract_method_statement(abstract)
        result = self._extract_result_statement(abstract)

        return {
            "success": True,
            "summary": {
                "summary": summary,
                "core_problem": core_problem,
                "method": method,
                "result": result,
                "recommendation_reason": "",
                "summary_source": "metadata_only",
            },
        }

    async def _llm_card_summary(self, title: str, abstract: str, query: str = "") -> dict:
        """Generate card summary using LLM."""
        prompt = build_card_summary_prompt(title=title, abstract=abstract, query=query)
        result = await llm_client.chat_json(
            messages=[
                {"role": "system", "content": CARD_SUMMARY_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
        )

        if result["success"]:
            data = result["content"]
            if isinstance(data, dict):
                return {
                    "success": True,
                    "summary": {
                        "summary": data.get("summary", ""),
                        "core_problem": data.get("core_problem", ""),
                        "method": data.get("method", ""),
                        "result": data.get("result", ""),
                        "recommendation_reason": data.get("recommendation_reason", ""),
                        "summary_source": "abstract_intro_llm",
                    },
                }
        return {"success": False}

    def _extract_summary(self, abstract: str) -> str:
        """Extract 2-3 sentence summary from abstract."""
        if not abstract:
            return "摘要不可用"
        sentences = re.split(r"[.。!！?？]\s*", abstract)
        meaningful = [s.strip() for s in sentences if len(s.strip()) > 15]
        summary_sentences = meaningful[:3]
        return "。".join(summary_sentences) + "。"

    def _extract_core_problem_statement(self, abstract: str) -> str:
        """Extract core problem from abstract."""
        if not abstract:
            return "详见论文"
        patterns = [
            r"(?:challenge|problem|issue|limitation|瓶颈|挑战|问题|不足|局限)\s*(?:is|are|在于|是|：|:)?\s*(.+?)(?:[.。]|$)",
            r"(?:However|But|Unfortunately|然而|但是|但),?\s*(.+?)(?:[.。]|$)",
        ]
        for p in patterns:
            m = re.search(p, abstract, re.IGNORECASE)
            if m:
                return m.group(1).strip()[:200]
        return "详见论文摘要"

    def _extract_method_statement(self, abstract: str) -> str:
        """Extract method from abstract."""
        if not abstract:
            return "详见论文"
        patterns = [
            r"(?:propose|present|introduce|develop|提出|提出了一种|介绍了|设计)\s*(?:a |an )?(.+?)(?:[.。]|$)",
            r"(?:approach|method|framework|方法|框架|架构)\s*(?:is |are |：|: |是)?(.+?)(?:[.。]|$)",
        ]
        for p in patterns:
            m = re.search(p, abstract, re.IGNORECASE)
            if m:
                return m.group(1).strip()[:200]
        return "详见论文"

    def _extract_result_statement(self, abstract: str) -> str:
        """Extract results from abstract."""
        if not abstract:
            return "详见论文"
        patterns = [
            r"(?:result|finding|show|demonstrate|achieve|实验|结果|表明|显示|证明)\s*(?:that |：|: )?(.+?)(?:[.。]|$)",
            r"(?:outperform|improve|提升|超过|优于)\s*(?:by |了)?(.+?)(?:[.。]|$)",
        ]
        for p in patterns:
            m = re.search(p, abstract, re.IGNORECASE)
            if m:
                return m.group(1).strip()[:200]
        return "详见论文"

    async def generate_deep_report(
        self,
        arxiv_id: str,
        parsed_markdown: str,
        metadata: dict,
        sections: list[dict] | None = None,
    ) -> dict:
        """Generate deep Chinese reading report. Uses LLM when available."""
        if not parsed_markdown:
            return {
                "success": False,
                "report_path": "",
                "error": "解析内容为空，无法生成报告",
            }

        paper_dir = self.file_manager.ensure_paper_dir(arxiv_id)
        report_path = os.path.join(paper_dir, "report.md")

        # Try LLM first
        if llm_client.available:
            llm_result = await self._llm_deep_report(parsed_markdown, metadata)
            if llm_result.get("success"):
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(llm_result["report"])
                logger.info(f"LLM deep report generated for {arxiv_id}")
                return {"success": True, "report_path": report_path, "error": None}

        # Fallback: template-based
        section_map = {}
        if sections:
            for sec in sections:
                heading = sec.get("heading", "").lower()
                content = sec.get("content", "")
                section_map[heading] = content

        # Generate report sections
        title = metadata.get("title", "")
        authors = metadata.get("authors", [])
        if isinstance(authors, list):
            authors_str = ", ".join(authors[:5])
            if len(authors) > 5:
                authors_str += " 等"
        else:
            authors_str = str(authors)

        published = metadata.get("published_date", "")
        abstract = metadata.get("abstract", "")

        report = self._build_report(
            arxiv_id=arxiv_id,
            title=title,
            authors=authors_str,
            published=published,
            abstract=abstract,
            section_map=section_map,
        )

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"Deep report generated for {arxiv_id}: {len(report)} chars")
        return {
            "success": True,
            "report_path": report_path,
            "error": None,
        }

    def _build_report(
        self,
        arxiv_id: str,
        title: str,
        authors: str,
        published: str,
        abstract: str,
        section_map: dict[str, str],
    ) -> str:
        """Build structured Chinese report."""
        lines = []

        # Header
        lines.append(f"# 论文精读报告\n")
        lines.append(f"**arXiv ID**: `{arxiv_id}`")
        if title:
            lines.append(f"**标题**: {title}")
        if authors:
            lines.append(f"**作者**: {authors}")
        if published:
            lines.append(f"**发布日期**: {published}")
        lines.append(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append("---\n")

        # 1. One-line summary
        lines.append("## 一句话总结\n")
        lines.append(self._generate_one_liner(title, abstract))
        lines.append("")

        # 2. Research background
        lines.append("## 研究背景\n")
        lines.append(self._generate_background(section_map, abstract))
        lines.append("")

        # 3. Core problem
        lines.append("## 核心问题\n")
        lines.append(self._generate_core_problem(section_map, abstract))
        lines.append("")

        # 4. Method
        lines.append("## 方法详解\n")
        lines.append(self._generate_method_detail(section_map, abstract))
        lines.append("")

        # 5. Key innovations
        lines.append("## 关键创新点\n")
        lines.append(self._generate_innovations(section_map))
        lines.append("")

        # 6. Experimental design
        lines.append("## 实验设计\n")
        lines.append(self._generate_experiments(section_map))
        lines.append("")

        # 7. Main results
        lines.append("## 主要结果\n")
        lines.append(self._generate_results(section_map))
        lines.append("")

        # 8. Limitations
        lines.append("## 局限性\n")
        lines.append(self._generate_limitations(section_map))
        lines.append("")

        # 9. Reproducibility
        lines.append("## 可复现性判断\n")
        lines.append(self._generate_reproducibility(section_map))
        lines.append("")

        # 10. Disclaimer
        lines.append("---\n")
        lines.append(
            "*本报告由 arXiv Paper Agent 自动生成。"
            "当前版本基于规则和模板生成，未使用 LLM 进行深度分析。"
            "配置 LLM API Key 后可获得更高质量的精读报告。*"
        )

        return "\n".join(lines)

    async def _llm_deep_report(self, parsed_markdown: str, metadata: dict) -> dict:
        """Generate deep report using LLM."""
        title = metadata.get("title", "")
        authors = metadata.get("authors", [])
        if isinstance(authors, list):
            authors_str = ", ".join(authors[:5])
        else:
            authors_str = str(authors)

        prompt = f"""论文标题：{title}
作者：{authors_str}

论文全文内容（节选）：
{parsed_markdown[:8000]}

请基于以上内容生成中文精读报告。"""

        result = await llm_client.chat(
            messages=[
                {"role": "system", "content": DEEP_REPORT_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            max_tokens=4096,
            temperature=0.3,
        )

        if result["success"]:
            report = result["content"]
            header = f"# 论文精读报告\n\n**arXiv ID**: `{metadata.get('arxiv_id', '')}`\n**标题**: {title}\n**作者**: {authors_str}\n**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n"
            return {"success": True, "report": header + report}

        return {"success": False}

    def _find_section_content(self, section_map: dict[str, str], *keywords: str) -> str:
        """Find content from section map by keywords."""
        for heading, content in section_map.items():
            heading_lower = heading.lower()
            for kw in keywords:
                if kw.lower() in heading_lower:
                    return content
        return ""

    def _generate_one_liner(self, title: str, abstract: str) -> str:
        """Generate one-line summary."""
        if not abstract:
            return f"本文《{title}》提出了一个新的研究方向。"
        first_sentence = abstract.split(".")[0].strip()
        # Try to translate/adapt common patterns
        key_patterns = [
            (r"(propose|present|introduce|develop)\s+(a |an )?(.+?)(?:for|to|that|which|\.)", "本文提出了"),
            (r"(study|investigate|explore|examine)\s+(.+?)(?:and|\.|in)", "本文研究了"),
            (r"(address|solve|tackle)\s+(.+?)(?:problem|challenge|issue)", "本文解决了"),
        ]
        for pattern, prefix in key_patterns:
            m = re.search(pattern, abstract, re.IGNORECASE)
            if m:
                return f"本文{m.group(1)}了{m.group(3).strip()[:80]}"

        return f"本文《{title}》{first_sentence[:150]}"

    def _generate_background(self, section_map: dict[str, str], abstract: str) -> str:
        """Generate research background section."""
        content = self._find_section_content(section_map, "introduction", "background", "related work")
        if content and len(content) > 100:
            # Extract first few meaningful paragraphs
            paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 50]
            return "\n\n".join(paragraphs[:3]) if paragraphs else content[:1500]

        if abstract:
            return f"基于论文摘要：{abstract[:1000]}"

        return "未能提取到研究背景信息，请查阅原文。"

    def _generate_core_problem(self, section_map: dict[str, str], abstract: str) -> str:
        """Generate core problem section."""
        content = self._find_section_content(section_map, "problem", "challenge", "motivation")
        if content and len(content) > 50:
            return content[:1500]

        # Extract from abstract
        problem = self._extract_core_problem_statement(abstract)
        if problem and problem != "详见论文":
            return problem

        return "未能自动识别核心问题描述，请参考引言部分。"

    def _generate_method_detail(self, section_map: dict[str, str], abstract: str) -> str:
        """Generate method details section."""
        content = self._find_section_content(section_map, "method", "approach", "framework", "proposed", "model", "architecture")
        if content and len(content) > 200:
            return content[:3000]

        if abstract:
            return f"基于摘要提取的方法信息：\n\n{abstract[:1500]}"

        return "未能提取到方法细节，请查阅原文。"

    def _generate_innovations(self, section_map: dict[str, str]) -> str:
        """Generate key innovations section."""
        content = self._find_section_content(section_map, "contribution", "novel", "innovation")
        if content and len(content) > 100:
            # Try to find bullet points
            bullets = re.findall(r"(?:[-•*]|\d+\.)\s*(.+?)(?:\n|$)", content)
            if bullets:
                return "\n".join(f"- {b.strip()}" for b in bullets[:5])
            return content[:1500]

        # Scan all sections for contributions
        for heading, content in section_map.items():
            if "contribution" in heading.lower():
                return content[:1500]

        return "未能自动识别创新点。请参考 Method 和 Conclusion 部分，或配置 LLM 进行深度分析。"

    def _generate_experiments(self, section_map: dict[str, str]) -> str:
        """Generate experimental design section."""
        content = self._find_section_content(section_map, "experiment", "evaluation", "result", "setup", "dataset", "implementation")
        if content and len(content) > 200:
            return content[:2500]

        return "未能提取到实验设计细节，请查阅原文 Experiment 部分。"

    def _generate_results(self, section_map: dict[str, str]) -> str:
        """Generate main results section."""
        content = self._find_section_content(section_map, "result", "evaluation", "performance", "comparison", "ablation")
        if content and len(content) > 200:
            return content[:2500]

        return "未能提取到主要结果，请查阅原文 Results 部分。"

    def _generate_limitations(self, section_map: dict[str, str]) -> str:
        """Generate limitations section."""
        content = self._find_section_content(section_map, "limitation", "future work", "discussion", "conclusion")
        if content and len(content) > 50:
            return content[:1500]

        return "本文未能自动识别局限性讨论。请参考 Discussion 和 Conclusion 部分，或配置 LLM 进行深度分析。"

    def _generate_reproducibility(self, section_map: dict[str, str]) -> str:
        """Generate reproducibility assessment."""
        all_text = " ".join(section_map.values()).lower()
        indicators = []

        # Check for code availability
        if any(w in all_text for w in ["code", "github", "open source", "repository", "available at"]):
            indicators.append("- ✅ 论文提供了代码/仓库链接")
        else:
            indicators.append("- ❓ 未检测到代码开源声明")

        # Check for dataset
        if any(w in all_text for w in ["dataset", "benchmark", "cifar", "imagenet", "mnist"]):
            indicators.append("- ✅ 使用了公开数据集/基准")
        else:
            indicators.append("- ❓ 数据集信息不明确")

        # Check for hyperparameters
        if any(w in all_text for w in ["learning rate", "batch size", "epoch", "hyperparameter", "optimizer"]):
            indicators.append("- ✅ 提供了关键超参数信息")
        else:
            indicators.append("- ❓ 超参数信息不完整")

        # Check for hardware
        if any(w in all_text for w in ["gpu", "cpu", "tpu", "hardware", "nvidia"]):
            indicators.append("- ✅ 说明了硬件环境")

        return "\n".join(indicators) if indicators else "无法自动评估可复现性。"
