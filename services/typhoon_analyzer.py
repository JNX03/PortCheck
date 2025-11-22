"""
Typhoon AI Analyzer Service
Analyzes Thai text for formal/informal language and field matching using Typhoon AI
"""

import logging
import json
import re
from typing import Dict, List, Optional
from openai import OpenAI

from models.schemas import AnalysisResult, LanguageIssue, FieldMatch, Certificate

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

    async def analyze_portfolio(
        self,
        text: str,
        target_field: str,
        judgment_criteria: str = ""
    ) -> AnalysisResult:
        """
        Analyze portfolio text for formal language and field matching

        Args:
            text: Extracted text from portfolio
            target_field: Target field/position
            judgment_criteria: Custom selection criteria (เกณฑ์การเลือก)

        Returns:
            AnalysisResult with complete analysis
        """
        logger.info(f"Analyzing portfolio for target field: {target_field}")
        if judgment_criteria:
            logger.info(f"Using custom judgment criteria: {judgment_criteria[:100]}...")

        # Analyze formal vs informal language
        language_analysis = await self._analyze_language(text)

        # Analyze field matching with criteria
        field_analysis = await self._analyze_field_match(text, target_field, judgment_criteria)

        # Analyze certificates and achievements
        certificates = await self._analyze_certificates(text, target_field, judgment_criteria)

        # Generate overall summary
        summary = await self._generate_summary(
            text=text,
            language_analysis=language_analysis,
            field_analysis=field_analysis,
            certificates=certificates,
            judgment_criteria=judgment_criteria
        )

        # Build result
        result = AnalysisResult(
            success=True,
            text_length=len(text),
            language_issues=language_analysis["issues"],
            overall_formality_score=language_analysis["formality_score"],
            formality_level=language_analysis["formality_level"],
            field_match=field_analysis,
            certificates=certificates,
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

    async def _analyze_field_match(
        self,
        text: str,
        target_field: str,
        judgment_criteria: str = ""
    ) -> FieldMatch:
        """
        Analyze if portfolio matches target field

        Args:
            text: Portfolio text
            target_field: Target field/position
            judgment_criteria: Custom selection criteria

        Returns:
            FieldMatch with analysis results
        """
        # Expanded field mapping
        field_mapping = {
            # Medical & Health
            "doctor": "แพทย์, การแพทย์, สาธารณสุข, โรงพยาบาล",
            "nurse": "พยาบาล, การพยาบาล, สาธารณสุข",
            "dentist": "ทันตแพทย์, ทันตกรรม",
            "pharmacist": "เภสัชกร, เภสัชศาสตร์, ยา",
            "medical_tech": "เทคนิคการแพทย์, ห้องปฏิบัติการ",
            "physical_therapist": "กายภาพบำบัด, ฟื้นฟูสมรรถภาพ",
            "veterinarian": "สัตวแพทย์, สัตวแพทยศาสตร์",

            # Engineering & Technology
            "engineer": "วิศวกร, วิศวกรรม, เทคโนโลยี",
            "software_engineer": "วิศวกรซอฟต์แวร์, โปรแกรมมิ่ง, พัฒนาซอฟต์แวร์",
            "civil_engineer": "วิศวกรโยธา, ก่อสร้าง, โครงสร้าง",
            "mechanical_engineer": "วิศวกรเครื่องกล, กลศาสตร์",
            "electrical_engineer": "วิศวกรไฟฟ้า, ไฟฟ้า, อิเล็กทรอนิกส์",
            "chemical_engineer": "วิศวกรเคมี, เคมี, กระบวนการเคมี",
            "industrial_engineer": "วิศวกรอุตสาหการ, การผลิต, ระบบ",

            # IT & Computer Science
            "ai": "AI, ปัญญาประดิษฐ์, วิทยาการข้อมูล, Data Science, Machine Learning, Deep Learning",
            "data_scientist": "วิทยาศาสตร์ข้อมูล, วิเคราะห์ข้อมูล, Big Data",
            "programmer": "โปรแกรมเมอร์, เขียนโปรแกรม, coding",
            "web_developer": "พัฒนาเว็บ, web development, frontend, backend",
            "mobile_developer": "แอปพลิเคชัน, mobile app, iOS, Android",
            "devops": "DevOps, CI/CD, deployment, automation",
            "cybersecurity": "ความปลอดภัย, security, hacking, penetration testing",
            "network_engineer": "เครือข่าย, network, infrastructure",

            # Business & Finance
            "business": "ธุรกิจ, การจัดการ, บริหาร, การตลาด",
            "accountant": "นักบัญชี, บัญชี, การเงิน",
            "auditor": "สอบบัญชี, audit, ตรวจสอบ",
            "financial_analyst": "วิเคราะห์การเงิน, การเงิน, การลงทุน",
            "marketing": "การตลาด, marketing, brand, digital marketing",
            "hr": "ทรัพยากรบุคคล, HR, การบริหารงานบุคคล",
            "entrepreneur": "ผู้ประกอบการ, startup, ธุรกิจส่วนตัว",
            "investment_banker": "นักลงทุน, ธนาคารการลงทุน, investment",

            # Education
            "teacher": "ครู, การศึกษา, การสอน, อาจารย์",
            "professor": "อาจารย์, มหาวิทยาลัย, สอน",
            "researcher": "นักวิจัย, research, วิจัย",
            "tutor": "ติวเตอร์, สอนพิเศษ",

            # Creative & Design
            "designer": "นักออกแบบ, ดีไซน์, การออกแบบ",
            "graphic_designer": "กราฟิกดีไซน์, ออกแบบกราฟิก",
            "ux_ui_designer": "UX, UI, ออกแบบ interface, user experience",
            "architect": "สถาปนิก, สถาปัตยกรรม, ออกแบบอาคาร",
            "interior_designer": "ตกแต่งภายใน, interior design",
            "animator": "แอนิเมชั่น, animation, 3D",
            "video_editor": "ตัดต่อวิดีโอ, video editing",
            "photographer": "ช่างภาพ, photography",

            # Legal & Government
            "lawyer": "ทนายความ, นิติศาสตร์, กฎหมาย",
            "judge": "ผู้พิพากษา, ศาล, กฎหมาย",
            "government_officer": "ข้าราชการ, ราชการ, ภาครัฐ",
            "diplomat": "การทูต, ต่างประเทศ, diplomat",

            # Science
            "scientist": "นักวิทยาศาสตร์, วิทยาศาสตร์, วิจัย",
            "biologist": "ชีววิทยา, biology, สิ่งมีชีวิต",
            "chemist": "เคมี, chemistry, สารเคมี",
            "physicist": "ฟิสิกส์, physics",

            # Media & Communication
            "journalist": "นักข่าว, สื่อมวลชน, journalism",
            "content_creator": "ครีเอเตอร์, content, social media",
            "public_relations": "ประชาสัมพันธ์, PR, communication",
            "translator": "นักแปล, translator, ล่าม",

            # Hospitality & Tourism
            "chef": "เชฟ, ทำอาหาร, culinary",
            "hotel_manager": "โรงแรม, hospitality",
            "tour_guide": "ไกด์, นำเที่ยว, tourism",

            # Other
            "pilot": "นักบิน, การบิน, aviation",
            "athlete": "นักกีฬา, กีฬา, sports",
            "artist": "ศิลปิน, ศิลปะ, art",
            "musician": "นักดนตรี, ดนตรี, music",
        }

        target_keywords = field_mapping.get(target_field, target_field)

        criteria_text = f"\n\nเกณฑ์การเลือกเพิ่มเติม: {judgment_criteria}" if judgment_criteria else ""

        prompt = f"""วิเคราะห์ portfolio ต่อไปนี้ว่าเหมาะสมกับสาขา "{target_field}" ({target_keywords}) หรือไม่{criteria_text}

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

    async def _analyze_certificates(
        self,
        text: str,
        target_field: str,
        judgment_criteria: str = ""
    ) -> List[Certificate]:
        """
        Analyze certificates and achievements in portfolio

        Args:
            text: Portfolio text
            target_field: Target field/position
            judgment_criteria: Custom selection criteria

        Returns:
            List of Certificate objects with importance rankings
        """
        criteria_text = f"\n\nเกณฑ์การเลือก: {judgment_criteria}" if judgment_criteria else ""

        prompt = f"""วิเคราะห์ใบรับรอง, รางวัล, การแข่งขัน และผลงานที่กล่าวถึงใน portfolio นี้

สาขาเป้าหมาย: {target_field}{criteria_text}

ข้อความ portfolio:
{text[:4000]}

โปรดค้นหาและวิเคราะห์:
1. ชื่อของใบรับรอง/รางวัล/การแข่งขัน/คอร์ส
2. ความสำคัญต่อสาขาเป้าหมาย
3. ความเกี่ยวข้อง (relevance score 0-1)
4. คำแนะนำว่าควรแสดง, เน้น, หรือไม่แสดง

กรุณาตอบกลับในรูปแบบ JSON:
{{
  "certificates": [
    {{
      "name": "ชื่อใบรับรอง/รางวัล",
      "type": "certificate|competition|award|course",
      "importance": "critical|high|medium|low",
      "relevance_score": 0.9,
      "reason": "เหตุผลว่าทำไมสำคัญ/ไม่สำคัญ",
      "recommendation": "ควรเน้นในส่วนต้น|ควรแสดง|ไม่ควรแสดง"
    }}
  ]
}}

หมายเหตุ:
- critical: สำคัญมาก เกี่ยวข้องโดยตรงกับสาขา
- high: สำคัญ ช่วยเสริมความน่าเชื่อถือ
- medium: ค่อนข้างสำคัญ ช่วยเสริม
- low: ไม่ค่อยสำคัญ อาจเอาออกได้
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "คุณเป็นผู้เชี่ยวชาญการวิเคราะห์ portfolio ที่สามารถประเมินความสำคัญของใบรับรอง รางวัล และผลงาน โปรดวิเคราะห์และตอบกลับในรูปแบบ JSON เท่านั้น"
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
            logger.info(f"Certificate analysis response: {result_text[:200]}...")

            result = self._parse_json_response(result_text)
            certificates = []

            for cert_data in result.get("certificates", []):
                try:
                    cert = Certificate(
                        name=cert_data.get("name", "Unknown"),
                        type=cert_data.get("type", "certificate"),
                        importance=cert_data.get("importance", "medium"),
                        relevance_score=cert_data.get("relevance_score", 0.5),
                        reason=cert_data.get("reason", ""),
                        recommendation=cert_data.get("recommendation", "ควรแสดง"),
                        source_info=None  # Will be populated by web search if needed
                    )
                    certificates.append(cert)
                except Exception as e:
                    logger.warning(f"Could not parse certificate: {e}")

            logger.info(f"Found {len(certificates)} certificates/achievements")
            return certificates

        except Exception as e:
            logger.error(f"Certificate analysis error: {e}", exc_info=True)
            return []

    async def _generate_summary(
        self,
        text: str,
        language_analysis: Dict,
        field_analysis: FieldMatch,
        certificates: List[Certificate] = None,
        judgment_criteria: str = ""
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
        certificates = certificates or []

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

        # Certificate summary
        if certificates:
            critical_count = sum(1 for c in certificates if c.importance == "critical")
            high_count = sum(1 for c in certificates if c.importance == "high")
            if critical_count > 0 or high_count > 0:
                summary_parts.append(f"📜 พบใบรับรอง/รางวัลสำคัญ {critical_count + high_count} รายการ")

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

        # Certificate findings
        if certificates:
            critical_certs = [c for c in certificates if c.importance == "critical"]
            if critical_certs:
                key_findings.append(f"มีใบรับรอง/รางวัลสำคัญมาก: {', '.join([c.name for c in critical_certs[:2]])}")

            low_certs = [c for c in certificates if c.importance == "low"]
            if low_certs:
                key_findings.append(f"มีใบรับรอง/รางวัลที่ไม่ค่อยเกี่ยวข้อง {len(low_certs)} รายการ")

        if judgment_criteria:
            key_findings.append(f"วิเคราะห์ตามเกณฑ์: {judgment_criteria[:50]}...")

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
