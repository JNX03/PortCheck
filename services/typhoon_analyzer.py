"""
Typhoon AI Analyzer Service
Analyzes Thai text for formal/informal language and field matching using Typhoon AI
"""

import logging
import json
import re
from typing import Dict, List, Optional
from openai import OpenAI

from models.schemas import AnalysisResult, LanguageIssue, FieldMatch

logger = logging.getLogger(__name__)


class TyphoonAnalyzer:
    """Analyzes Thai portfolios using Typhoon AI model"""

    def __init__(self, api_key: str, api_url: str, model: str):
        """
        Initialize Typhoon analyzer

        Args:
            api_key: Typhoon API key
            api_url: Typhoon API URL
            model: Model name to use
        """
        if not api_key:
            raise ValueError("TYPHOON_API_KEY is required")

        self.client = OpenAI(
            api_key=api_key,
            base_url=api_url
        )
        self.model = model
        logger.info(f"Initialized Typhoon analyzer with model: {model}")

    async def analyze_portfolio(self, text: str, target_field: str) -> AnalysisResult:
        """
        Analyze portfolio text for formal language and field matching

        Args:
            text: Extracted text from portfolio
            target_field: Target field/position

        Returns:
            AnalysisResult with complete analysis
        """
        logger.info(f"Analyzing portfolio for target field: {target_field}")

        # Analyze formal vs informal language
        language_analysis = await self._analyze_language(text)

        # Analyze field matching
        field_analysis = await self._analyze_field_match(text, target_field)

        # Generate overall summary
        summary = await self._generate_summary(
            text=text,
            language_analysis=language_analysis,
            field_analysis=field_analysis
        )

        # Build result
        result = AnalysisResult(
            success=True,
            text_length=len(text),
            language_issues=language_analysis["issues"],
            overall_formality_score=language_analysis["formality_score"],
            formality_level=language_analysis["formality_level"],
            field_match=field_analysis,
            summary=summary["summary"],
            key_findings=summary["key_findings"]
        )

        return result

    async def _analyze_language(self, text: str) -> Dict:
        """
        Analyze text for formal vs informal Thai language

        Args:
            text: Text to analyze

        Returns:
            Dict with language analysis results
        """
        prompt = f"""คุณเป็นผู้เชี่ยวชาญด้านภาษาไทย วิเคราะห์ข้อความต่อไปนี้และหาส่วนที่เป็น "ภาษาพูด" (informal/spoken language) ที่ไม่เหมาะสมในเอกสารทางการ

ข้อความที่ต้องวิเคราะห์:
{text[:3000]}

โปรดระบุ:
1. คำหรือวลีที่เป็นภาษาพูด (ไม่เป็นทางการ)
2. ตำแหน่งที่พบในข้อความ (ประมาณ)
3. คำแนะนำที่เป็นภาษาเขียน (ทางการ) ที่ควรใช้แทน
4. ระดับความรุนแรง (high, medium, low)
5. คำอธิบายว่าทำไมถึงเป็นปัญหา

กรุณาตอบกลับในรูปแบบ JSON ดังนี้:
{{
  "formality_score": 0.75,
  "formality_level": "formal",
  "issues": [
    {{
      "text": "คำหรือวลีที่เป็นภาษาพูด",
      "position_description": "อยู่ในย่อหน้าที่ 2",
      "issue_type": "informal_word",
      "severity": "medium",
      "suggestion": "คำที่เป็นทางการที่ควรใช้แทน",
      "explanation": "คำอธิบายว่าทำไมถึงไม่เหมาะสม",
      "context": "ประโยคที่มีคำนี้อยู่"
    }}
  ]
}}

หมายเหตุ:
- formality_score: คะแนนความเป็นทางการ (0-1, โดย 1 คือเป็นทางการมากที่สุด)
- formality_level: ระดับความเป็นทางการ (highly_formal, formal, mixed, informal, highly_informal)
- ภาษาพูดที่ควรหลีกเลี่ยง เช่น: "เจ๋ง", "เท่ห์", "เก่ง", "อะไรก็แล้วแต่", "ไม่รู้ซิ", "ชอบมาก", "สุดยอด" เป็นต้น
- คำลงท้ายประโยคแบบพูด เช่น: "ครับผม", "จ้า", "นะ", "เนอะ" เป็นต้น
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "คุณเป็นผู้เชี่ยวชาญด้านภาษาไทยที่มีความชำนาญในการวิเคราะห์ภาษาเขียนและภาษาพูด โปรดวิเคราะห์อย่างละเอียดและให้ข้อมูลในรูปแบบ JSON เท่านั้น"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )

            result_text = response.choices[0].message.content
            logger.info(f"Language analysis response: {result_text[:200]}...")

            # Parse JSON response
            result = self._parse_json_response(result_text)

            # Find positions in original text
            issues = []
            for issue_data in result.get("issues", []):
                # Try to find the text in the original document
                found_positions = self._find_text_positions(text, issue_data["text"])

                for start_pos, end_pos in found_positions[:3]:  # Limit to 3 occurrences
                    issue = LanguageIssue(
                        text=issue_data["text"],
                        start_pos=start_pos,
                        end_pos=end_pos,
                        issue_type=issue_data.get("issue_type", "informal_language"),
                        severity=issue_data.get("severity", "medium"),
                        suggestion=issue_data.get("suggestion", ""),
                        explanation=issue_data.get("explanation", ""),
                        context=issue_data.get("context", "")
                    )
                    issues.append(issue)

            return {
                "formality_score": result.get("formality_score", 0.7),
                "formality_level": result.get("formality_level", "formal"),
                "issues": issues
            }

        except Exception as e:
            logger.error(f"Language analysis error: {e}", exc_info=True)
            # Return default analysis if API fails
            return {
                "formality_score": 0.7,
                "formality_level": "formal",
                "issues": []
            }

    async def _analyze_field_match(self, text: str, target_field: str) -> FieldMatch:
        """
        Analyze if portfolio matches target field

        Args:
            text: Portfolio text
            target_field: Target field/position

        Returns:
            FieldMatch with analysis results
        """
        # Field mapping
        field_mapping = {
            "doctor": "แพทย์, การแพทย์, สาธารณสุข",
            "engineer": "วิศวกร, วิศวกรรม, เทคโนโลยี",
            "ai": "AI, ปัญญาประดิษฐ์, วิทยาการข้อมูล, Data Science, Machine Learning",
            "business": "ธุรกิจ, การจัดการ, บริหาร, การตลาด",
            "teacher": "ครู, การศึกษา, การสอน, อาจารย์",
            "nurse": "พยาบาล, การพยาบาล, สาธารณสุข",
            "architect": "สถาปนิก, สถาปัตยกรรม, ออกแบบอาคาร",
            "designer": "นักออกแบบ, ดีไซน์, การออกแบบ",
            "lawyer": "ทนายความ, นิติศาสตร์, กฎหมาย",
            "accountant": "นักบัญชี, บัญชี, การเงิน"
        }

        target_keywords = field_mapping.get(target_field, target_field)

        prompt = f"""วิเคราะห์ portfolio ต่อไปนี้ว่าเหมาะสมกับสาขา "{target_field}" ({target_keywords}) หรือไม่

ข้อความ portfolio:
{text[:4000]}

กรุณาวิเคราะห์และตอบกลับในรูปแบบ JSON ดังนี้:
{{
  "matches": true,
  "confidence": 0.85,
  "detected_fields": ["สาขาที่ตรวจพบ 1", "สาขาที่ตรวจพบ 2"],
  "evidence": [
    "หลักฐานที่สนับสนุนว่าเหมาะสม/ไม่เหมาะสม 1",
    "หลักฐานที่สนับสนุนว่าเหมาะสม/ไม่เหมาะสม 2"
  ],
  "recommendations": [
    "คำแนะนำในการปรับปรุง 1",
    "คำแนะนำในการปรับปรุง 2"
  ]
}}

หมายเหตุ:
- matches: true ถ้า portfolio ตรงกับสาขาที่ต้องการ, false ถ้าไม่ตรง
- confidence: ระดับความมั่นใจ (0-1)
- detected_fields: สาขาที่ตรวจพบใน portfolio
- evidence: หลักฐานที่สนับสนุนการตัดสิน
- recommendations: คำแนะนำในการปรับปรุง portfolio
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "คุณเป็นผู้เชี่ยวชาญด้านการวิเคราะห์ portfolio และการจับคู่สาขาอาชีพ โปรดวิเคราะห์อย่างละเอียดและให้ข้อมูลในรูปแบบ JSON เท่านั้น"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1500
            )

            result_text = response.choices[0].message.content
            logger.info(f"Field match response: {result_text[:200]}...")

            result = self._parse_json_response(result_text)

            return FieldMatch(
                target_field=target_field,
                matches=result.get("matches", True),
                confidence=result.get("confidence", 0.7),
                detected_fields=result.get("detected_fields", []),
                evidence=result.get("evidence", []),
                recommendations=result.get("recommendations", [])
            )

        except Exception as e:
            logger.error(f"Field match analysis error: {e}", exc_info=True)
            # Return default match if API fails
            return FieldMatch(
                target_field=target_field,
                matches=True,
                confidence=0.5,
                detected_fields=[],
                evidence=["Unable to analyze due to an error"],
                recommendations=["Please try again"]
            )

    async def _generate_summary(
        self,
        text: str,
        language_analysis: Dict,
        field_analysis: FieldMatch
    ) -> Dict:
        """
        Generate overall summary of analysis

        Args:
            text: Portfolio text
            language_analysis: Language analysis results
            field_analysis: Field matching analysis

        Returns:
            Dict with summary and key findings
        """
        num_issues = len(language_analysis["issues"])
        formality_score = language_analysis["formality_score"]
        matches = field_analysis.matches

        # Generate summary
        summary_parts = []

        # Language summary
        if num_issues == 0:
            summary_parts.append("✅ Portfolio ใช้ภาษาเขียนที่เป็นทางการอย่างเหมาะสม")
        elif num_issues <= 3:
            summary_parts.append(f"⚠️ พบการใช้ภาษาพูดบางส่วน ({num_issues} จุด) ที่ควรปรับปรุง")
        else:
            summary_parts.append(f"⚠️ พบการใช้ภาษาพูดค่อนข้างมาก ({num_issues} จุด) ควรแก้ไขเพื่อความเป็นทางการ")

        # Field match summary
        if matches:
            summary_parts.append(f"✅ Portfolio สอดคล้องกับสาขา {field_analysis.target_field} (ความมั่นใจ {field_analysis.confidence:.0%})")
        else:
            summary_parts.append(f"❌ Portfolio อาจไม่สอดคล้องกับสาขา {field_analysis.target_field} (ความมั่นใจ {field_analysis.confidence:.0%})")

        summary = " | ".join(summary_parts)

        # Key findings
        key_findings = []

        if formality_score >= 0.8:
            key_findings.append("ภาษาที่ใช้มีความเป็นทางการสูง")
        elif formality_score >= 0.6:
            key_findings.append("ภาษาที่ใช้มีความเป็นทางการในระดับพอใช้")
        else:
            key_findings.append("ภาษาที่ใช้ยังไม่เป็นทางการเพียงพอ")

        if field_analysis.detected_fields:
            key_findings.append(f"ตรวจพบความเชี่ยวชาญใน: {', '.join(field_analysis.detected_fields[:3])}")

        if num_issues > 0:
            key_findings.append(f"พบจุดที่ควรปรับปรุง {num_issues} จุด")

        return {
            "summary": summary,
            "key_findings": key_findings
        }

    def _parse_json_response(self, text: str) -> Dict:
        """
        Parse JSON from AI response

        Args:
            text: Response text

        Returns:
            Parsed JSON dict
        """
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        else:
            # Try to extract JSON from plain text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                text = json_match.group(0)

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}, text: {text[:500]}")
            return {}

    def _find_text_positions(self, full_text: str, search_text: str) -> List[tuple]:
        """
        Find all positions of search_text in full_text

        Args:
            full_text: Full text to search in
            search_text: Text to find

        Returns:
            List of (start_pos, end_pos) tuples
        """
        positions = []
        start = 0

        while True:
            pos = full_text.find(search_text, start)
            if pos == -1:
                break
            positions.append((pos, pos + len(search_text)))
            start = pos + 1

        return positions
