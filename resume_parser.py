import re
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Dict, List, Any, Optional
import json

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class ResumeParser:
    def __init__(self):
        # Load spaCy model (install with: python -m spacy download en_core_web_sm)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Please install spaCy English model: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        self.stop_words = set(stopwords.words('english'))
        
        # Common skills keywords
        self.tech_skills = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'mongodb',
            'postgresql', 'mysql', 'html', 'css', 'git', 'docker', 'kubernetes',
            'aws', 'azure', 'machine learning', 'deep learning', 'tensorflow',
            'pytorch', 'scikit-learn', 'pandas', 'numpy', 'fastapi', 'django',
            'flask', 'spring boot', 'microservices', 'rest api', 'graphql'
        ]
        
        # Education keywords
        self.education_keywords = [
            'bachelor', 'master', 'phd', 'degree', 'university', 'college',
            'education', 'graduation', 'b.tech', 'm.tech', 'mba', 'b.sc', 'm.sc'
        ]
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract name, email, and phone from resume text"""
        contact_info = {
            'name': None,
            'email': None,
            'phone': None
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Extract phone
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()
        
        # Extract name (assume first line or first few words)
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line.split()) <= 4 and not any(char.isdigit() for char in line):
                if '@' not in line and not any(keyword in line.lower() for keyword in ['resume', 'cv', 'curriculum']):
                    contact_info['name'] = line
                    break
        
        return contact_info
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from resume text"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.tech_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # Remove duplicates and return
        return list(set(found_skills))
    
    def extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience information"""
        experience = []
        
        # Look for common experience patterns
        experience_patterns = [
            r'(\d{4})\s*[-–]\s*(\d{4}|present|current)',
            r'(\d{1,2}/\d{4})\s*[-–]\s*(\d{1,2}/\d{4}|present|current)'
        ]
        
        sentences = sent_tokenize(text)
        for sentence in sentences:
            for pattern in experience_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                if matches:
                    for match in matches:
                        exp_entry = {
                            'period': f"{match[0]} - {match[1]}",
                            'description': sentence.strip()
                        }
                        experience.append(exp_entry)
        
        return experience
    
    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education information"""
        education = []
        text_lower = text.lower()
        
        sentences = sent_tokenize(text)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in self.education_keywords):
                education.append({
                    'description': sentence.strip()
                })
        
        return education
    
    def calculate_experience_years(self, experience: List[Dict[str, Any]]) -> int:
        """Calculate total years of experience"""
        total_years = 0
        
        for exp in experience:
            period = exp.get('period', '')
            # Simple calculation - extract years from period
            years = re.findall(r'\d{4}', period)
            if len(years) >= 2:
                try:
                    start_year = int(years[0])
                    end_year = int(years[1]) if years[1].isdigit() else 2024
                    total_years += (end_year - start_year)
                except:
                    continue
        
        return total_years
    
    def parse_resume(self, text: str) -> Dict[str, Any]:
        """Main parsing function that combines all extraction methods"""
        
        # Extract all information
        contact_info = self.extract_contact_info(text)
        skills = self.extract_skills(text)
        experience = self.extract_experience(text)
        education = self.extract_education(text)
        experience_years = self.calculate_experience_years(experience)
        
        # Combine all parsed data
        parsed_data = {
            'contact_info': contact_info,
            'skills': skills,
            'experience': experience,
            'education': education,
            'experience_years': experience_years,
        }
        
        return parsed_data