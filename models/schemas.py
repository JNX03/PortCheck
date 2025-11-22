"""
Data models and schemas for the Thai Portfolio Analyzer
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class LanguageIssue(BaseModel):
    """Represents a formal/informal language issue"""
    text: str = Field(..., description="The informal text found")
    start_pos: int = Field(..., description="Start position in the document")
    end_pos: int = Field(..., description="End position in the document")
    issue_type: str = Field(..., description="Type of issue (e.g., 'informal_word', 'spoken_language')")
    severity: str = Field(..., description="Severity level: 'low', 'medium', 'high'")
    suggestion: str = Field(..., description="Suggested formal alternative")
    explanation: str = Field(..., description="Explanation of why this is an issue")
    context: Optional[str] = Field(None, description="Surrounding context")


class FieldMatch(BaseModel):
    """Represents field/position matching analysis"""
    target_field: str = Field(..., description="The target field/position")
    matches: bool = Field(..., description="Whether the portfolio matches the target field")
    confidence: float = Field(..., description="Confidence score (0-1)")
    detected_fields: List[str] = Field(..., description="Fields detected in the portfolio")
    evidence: List[str] = Field(..., description="Evidence supporting the match/mismatch")
    recommendations: List[str] = Field(..., description="Recommendations for improvement")


class AnalysisResult(BaseModel):
    """Complete analysis result"""
    success: bool = Field(True, description="Whether analysis was successful")
    text_length: int = Field(..., description="Length of extracted text")
    extraction_method: Optional[str] = Field(None, description="Method used for text extraction")
    pages_processed: Optional[int] = Field(None, description="Number of pages processed")

    # Language analysis
    language_issues: List[LanguageIssue] = Field(
        default_factory=list,
        description="List of formal/informal language issues"
    )
    overall_formality_score: float = Field(
        ...,
        description="Overall formality score (0-1, where 1 is most formal)"
    )
    formality_level: str = Field(
        ...,
        description="Formality level: 'highly_formal', 'formal', 'mixed', 'informal', 'highly_informal'"
    )

    # Field matching
    field_match: FieldMatch = Field(..., description="Field matching analysis")

    # Summary
    summary: str = Field(..., description="Overall summary of the analysis")
    key_findings: List[str] = Field(default_factory=list, description="Key findings")


class ExtractionResult(BaseModel):
    """PDF text extraction result"""
    text: str = Field(..., description="Extracted text")
    method: str = Field(..., description="Extraction method used")
    pages: int = Field(..., description="Number of pages processed")
    success: bool = Field(..., description="Whether extraction was successful")
