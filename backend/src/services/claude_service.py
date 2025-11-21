"""
Claude API Service
Handles resume analysis and student categorization using Anthropic Claude API
"""
import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Optional, List
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None
    print("Warning: anthropic package not installed. Install with: pip install anthropic")

from config.settings import PATHS, DATABASE
from src.utils.logger import get_logger

logger = get_logger('claude_service')


class ClaudeService:
    """Service for interacting with Claude API for resume analysis and categorization"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude service
        
        Args:
            api_key: Anthropic API key. If not provided, reads from environment variable ANTHROPIC_API_KEY
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
        
        if Anthropic is None:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")
        
        self.client = Anthropic(api_key=self.api_key)
        self.db_path = os.path.join(PATHS['database'], DATABASE['name'])
        
        # Model configuration
        self.extraction_model = "claude-3-5-sonnet-20241022"  # Fast and accurate for extraction
        self.categorization_model = "claude-3-5-sonnet-20241022"  # Good for categorization
    
    def analyze_resume(self, resume_text: str, student_id: str) -> Dict:
        """
        Stage 1: Analyze resume and extract structured data
        
        Returns:
            {
                'skills': List[str],
                'experience_level': str,
                'years_of_experience': float,
                'projects': List[Dict],
                'certifications': List[Dict],
                'education': List[Dict],
                'languages': List[str],
                'status': 'success' or 'error',
                'error': str (if error)
            }
        """
        start_time = time.time()
        
        extraction_prompt = f"""You are an expert resume analyzer. Analyze the following resume text and extract structured information.

Resume Text:
{resume_text}

Extract and return a JSON object with the following structure:
{{
    "skills": ["skill1", "skill2", ...],  // Technical and soft skills
    "experience_level": "fresher" | "junior" | "mid" | "senior",  // Based on years and complexity
    "years_of_experience": 0.0,  // Numeric value
    "projects": [
        {{
            "name": "Project Name",
            "description": "Brief description",
            "technologies": ["tech1", "tech2"],
            "duration": "X months"
        }}
    ],
    "certifications": [
        {{
            "name": "Certification Name",
            "issuer": "Issuing Organization",
            "date": "YYYY-MM"
        }}
    ],
    "education": [
        {{
            "degree": "Degree Name",
            "institution": "Institution Name",
            "year": "YYYY",
            "field": "Field of Study"
        }}
    ],
    "languages": ["English", "Hindi", ...]  // Programming languages and spoken languages
}}

Be thorough and extract all relevant information. If information is not available, use empty arrays or null values.
Return ONLY valid JSON, no additional text."""

        try:
            response = self.client.messages.create(
                model=self.extraction_model,
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": extraction_prompt
                    }
                ]
            )
            
            # Extract text from response
            response_text = response.content[0].text if response.content else ""
            
            # Parse JSON from response
            # Sometimes Claude wraps JSON in markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            extraction_result = json.loads(response_text)
            
            execution_time = time.time() - start_time
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            # Calculate cost (approximate, based on Claude 3.5 Sonnet pricing)
            cost_usd = (response.usage.input_tokens * 0.003 + response.usage.output_tokens * 0.015) / 1000
            
            # Log the analysis
            self._log_resume_analysis(
                student_id, 'success', 'success', tokens_used, cost_usd,
                extraction_result, None, execution_time
            )
            
            return {
                'status': 'success',
                'skills': extraction_result.get('skills', []),
                'experience_level': extraction_result.get('experience_level', 'fresher'),
                'years_of_experience': extraction_result.get('years_of_experience', 0.0),
                'projects': extraction_result.get('projects', []),
                'certifications': extraction_result.get('certifications', []),
                'education': extraction_result.get('education', []),
                'languages': extraction_result.get('languages', []),
                'tokens_used': tokens_used,
                'cost_usd': cost_usd
            }
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON response: {str(e)}"
            logger.error(error_msg)
            self._log_resume_analysis(student_id, 'failed', 'failed', 0, 0, None, None, 
                                     time.time() - start_time, error_msg)
            return {
                'status': 'error',
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Error analyzing resume: {str(e)}"
            logger.error(error_msg)
            self._log_resume_analysis(student_id, 'failed', 'failed', 0, 0, None, None,
                                     time.time() - start_time, error_msg)
            return {
                'status': 'error',
                'error': error_msg
            }
    
    def categorize_student(self, student_data: Dict) -> Dict:
        """
        Stage 2: Categorize student based on extracted resume data
        
        Categories:
        - job-ready: Ready for immediate placement
        - needs-training: Needs additional training
        - advanced: Highly skilled, senior level
        - beginner: Just starting, needs mentorship
        
        Returns:
            {
                'category': str,
                'confidence': float (0-1),
                'reasoning': str,
                'status': 'success' or 'error'
            }
        """
        start_time = time.time()
        
        # Prepare student summary
        student_summary = f"""
Student Profile:
- Name: {student_data.get('name', 'N/A')}
- Experience Level: {student_data.get('experience_level', 'N/A')}
- Years of Experience: {student_data.get('years_of_experience', 0)}
- Skills: {', '.join(student_data.get('skills', []))}
- Projects: {len(student_data.get('projects', []))} projects
- Certifications: {len(student_data.get('certifications', []))} certifications
- Education: {len(student_data.get('education', []))} degrees/qualifications
"""
        
        categorization_prompt = f"""You are an expert career counselor and placement advisor. Categorize this student based on their profile.

{student_summary}

Categorize the student into one of these categories:
1. "job-ready" - Student has sufficient skills and experience to be placed immediately. They have completed projects, have relevant certifications, and demonstrate competency.
2. "needs-training" - Student has basic skills but needs additional training or mentorship before placement. They may have gaps in their skill set.
3. "advanced" - Student is highly skilled with significant experience. Suitable for senior roles or specialized positions.
4. "beginner" - Student is just starting their journey. Needs foundational training and mentorship.

Return a JSON object:
{{
    "category": "job-ready" | "needs-training" | "advanced" | "beginner",
    "confidence": 0.0-1.0,  // Your confidence in this categorization
    "reasoning": "Detailed explanation of why this category was chosen, what strengths they have, and what gaps exist (if any)"
}}

Return ONLY valid JSON, no additional text."""

        try:
            response = self.client.messages.create(
                model=self.categorization_model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": categorization_prompt
                    }
                ]
            )
            
            response_text = response.content[0].text if response.content else ""
            
            # Parse JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            categorization_result = json.loads(response_text)
            
            execution_time = time.time() - start_time
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            cost_usd = (response.usage.input_tokens * 0.003 + response.usage.output_tokens * 0.015) / 1000
            
            return {
                'status': 'success',
                'category': categorization_result.get('category', 'needs-training'),
                'confidence': categorization_result.get('confidence', 0.5),
                'reasoning': categorization_result.get('reasoning', ''),
                'tokens_used': tokens_used,
                'cost_usd': cost_usd
            }
            
        except Exception as e:
            error_msg = f"Error categorizing student: {str(e)}"
            logger.error(error_msg)
            return {
                'status': 'error',
                'error': error_msg
            }
    
    def analyze_and_categorize(self, resume_text: str, student_id: str, 
                               existing_data: Optional[Dict] = None) -> Dict:
        """
        Complete pipeline: Analyze resume and categorize student
        
        Returns combined results from both stages
        """
        # Stage 1: Extract resume data
        extraction_result = self.analyze_resume(resume_text, student_id)
        
        if extraction_result['status'] != 'success':
            return extraction_result
        
        # Stage 2: Categorize based on extracted data
        student_data = {
            'name': existing_data.get('name', '') if existing_data else '',
            'experience_level': extraction_result['experience_level'],
            'years_of_experience': extraction_result['years_of_experience'],
            'skills': extraction_result['skills'],
            'projects': extraction_result['projects'],
            'certifications': extraction_result['certifications'],
            'education': extraction_result['education']
        }
        
        categorization_result = self.categorize_student(student_data)
        
        # Combine results
        result = {
            'status': 'success' if categorization_result['status'] == 'success' else 'partial',
            'extraction': extraction_result,
            'categorization': categorization_result
        }
        
        # Update database with results
        if result['status'] == 'success':
            self._update_student_with_analysis(student_id, extraction_result, categorization_result)
        
        return result
    
    def _update_student_with_analysis(self, student_id: str, extraction_result: Dict, 
                                    categorization_result: Dict):
        """Update student record with analysis results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE students
                SET skills = ?,
                    experience_level = ?,
                    years_of_experience = ?,
                    projects = ?,
                    certifications = ?,
                    education = ?,
                    languages = ?,
                    category = ?,
                    category_confidence = ?,
                    category_reasoning = ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE student_id = ?
            ''', (
                json.dumps(extraction_result.get('skills', [])),
                extraction_result.get('experience_level', 'fresher'),
                extraction_result.get('years_of_experience', 0.0),
                json.dumps(extraction_result.get('projects', [])),
                json.dumps(extraction_result.get('certifications', [])),
                json.dumps(extraction_result.get('education', [])),
                json.dumps(extraction_result.get('languages', [])),
                categorization_result.get('category', 'needs-training'),
                categorization_result.get('confidence', 0.0),
                categorization_result.get('reasoning', ''),
                student_id
            ))
            
            conn.commit()
            logger.info(f"Updated student {student_id} with analysis results")
            
        except Exception as e:
            logger.error(f"Error updating student with analysis: {e}")
        finally:
            conn.close()
    
    def _log_resume_analysis(self, student_id: str, extraction_status: str, 
                            categorization_status: str, tokens_used: int,
                            cost_usd: float, extraction_result: Optional[Dict],
                            categorization_result: Optional[Dict], execution_time: float,
                            error_message: Optional[str] = None):
        """Log resume analysis activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO resume_analysis_logs
                (student_id, extraction_status, categorization_status, tokens_used,
                 cost_usd, extraction_result, categorization_result, error_message,
                 processing_time_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                student_id,
                extraction_status,
                categorization_status,
                tokens_used,
                cost_usd,
                json.dumps(extraction_result) if extraction_result else None,
                json.dumps(categorization_result) if categorization_result else None,
                error_message,
                execution_time
            ))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error logging resume analysis: {e}")
        finally:
            conn.close()

