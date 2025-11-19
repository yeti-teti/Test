"""
Exa AI Web Search Integration for Medical Chatbot

Uses Exa API to search the web for medical information.
Only returns results for medical queries.
"""

import os
import re
from typing import Dict, List, Any, Optional
from exa_py import Exa

class MedicalWebSearcher:
    """Search the web for medical information using Exa AI."""
    
    def __init__(self):
        """Initialize Exa client with API key."""
        self.api_key = os.getenv("EXA_API_KEY")
        if not self.api_key:
            print("⚠️  Warning: EXA_API_KEY not set. Web search will be disabled.")
            self.exa = None
        else:
            try:
                self.exa = Exa(api_key=self.api_key)
            except Exception as e:
                print(f"❌ Error initializing Exa: {e}")
                self.exa = None
    
    def is_medical_query(self, query: str) -> bool:
        """
        Check if query is medical-related.
        
        Args:
            query: User query
            
        Returns:
            True if medical query, False otherwise
        """
        medical_keywords = [
            # General medical terms
            "disease", "symptom", "treatment", "medication", "drug",
            "condition", "illness", "health", "medical", "diagnosis",
            "doctor", "hospital", "surgery", "pain", "fever",
            "diabetes", "heart", "cancer", "pneumonia", "virus",
            "infection", "vaccine", "therapy", "cure", "medicine",
            "patient", "clinical", "healthcare", "disorder", "syndrome",
            "hypertension", "asthma", "arthritis", "depression",
            "anxiety", "nutrition", "vitamin", "supplement", "exercise",
            "wellness", "epidemic", "pandemic",
            # Common symptoms and conditions
            "diarrhea", "diarrhoea", "nausea", "vomiting", "headache",
            "cough", "sneeze", "rash", "itch", "swelling", "bleeding",
            "dizziness", "fatigue", "weakness", "numbness", "tingling",
            "shortness of breath", "chest pain", "abdominal pain",
            "stomach ache", "back pain", "joint pain", "muscle pain",
            # Common diseases and conditions
            "flu", "cold", "allergy", "asthma", "bronchitis",
            "pneumonia", "tuberculosis", "malaria", "dengue",
            "hepatitis", "kidney", "liver", "lung", "brain",
            "stroke", "heart attack", "hypertension", "diabetes",
            "obesity", "anemia", "osteoporosis", "migraine",
            "epilepsy", "parkinson", "alzheimer", "dementia",
            # Body parts and systems
            "blood", "bone", "muscle", "nerve", "skin", "eye",
            "ear", "nose", "throat", "teeth", "gum", "tongue",
            "stomach", "intestine", "colon", "bladder", "kidney",
            "liver", "pancreas", "thyroid", "adrenal", "pituitary",
            # Medical procedures and tests
            "x-ray", "mri", "ct scan", "ultrasound", "biopsy",
            "surgery", "operation", "procedure", "test", "scan",
            # Medications and treatments
            "antibiotic", "antiviral", "antifungal", "antidepressant",
            "painkiller", "analgesic", "anti-inflammatory", "steroid",
            "chemotherapy", "radiation", "physiotherapy", "rehabilitation"
        ]
        
        query_lower = query.lower()
        
        # Check if any medical keyword is in the query
        if any(keyword in query_lower for keyword in medical_keywords):
            return True
        
        # Also check for "what is" queries - these are often medical questions
        # when asking about a specific term
        if re.search(r'what\s+is\s+(\w+)', query_lower):
            # If it's asking "what is X", be more permissive
            # Assume it's medical unless it's clearly not
            non_medical_words = ["weather", "time", "date", "color", "food",
                                "restaurant", "movie", "song", "book", "game",
                                "sport", "team", "player", "city", "country"]
            if not any(word in query_lower for word in non_medical_words):
                return True
        
        return False
    
    def search_medical_web(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Search the web for medical information using Exa.
        
        Args:
            query: Medical search query
            num_results: Number of results to return
            
        Returns:
            Dictionary with search results
        """
        if not self.exa:
            return {
                "success": False,
                "error": "Web search not configured. Set EXA_API_KEY environment variable."
            }
        
        # Check if query is medical
        if not self.is_medical_query(query):
            return {
                "success": False,
                "medical_query": False,
                "error": "Query does not appear to be medical-related. Only medical queries are supported."
            }
        
        try:
            # Search the web for medical information
            search_query = f"{query} medical health information"
            
            results = self.exa.search(
                query=search_query,
                num_results=num_results,
                type="neural",  # Use neural search for better semantic understanding
            )
            
            if not results or not results.results:
                return {
                    "success": True,
                    "found": False,
                    "message": "No medical web results found for your query."
                }
            
            # Format results
            formatted_results = []
            for idx, result in enumerate(results.results, 1):
                formatted_results.append({
                    "rank": idx,
                    "title": result.title,
                    "url": result.url,
                    "summary": result.text[:300],  # First 300 chars
                    "source": self._extract_domain(result.url)
                })
            
            return {
                "success": True,
                "found": True,
                "query": query,
                "results_count": len(formatted_results),
                "results": formatted_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Web search error: {str(e)}"
            }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            domain = url.split("//")[1].split("/")[0]
            # Clean up www
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except:
            return url
    
    def search_with_content(self, query: str, num_results: int = 3) -> Dict[str, Any]:
        """
        Search and get detailed content from web results.
        
        Args:
            query: Medical search query
            num_results: Number of results with content
            
        Returns:
            Dictionary with results and content
        """
        if not self.exa:
            return {
                "success": False,
                "error": "Web search not configured. Set EXA_API_KEY environment variable."
            }
        
        # Check if medical query
        if not self.is_medical_query(query):
            return {
                "success": False,
                "medical_query": False,
                "error": "Only medical queries are supported."
            }
        
        try:
            # Search with content for medical information
            search_query = f"{query} medical health information"
            
            print(f"🔍 Exa: Searching for '{search_query}' with {num_results} results")
            
            # Use search_and_contents to get both results and content
            results = self.exa.search_and_contents(
                query=search_query,
                num_results=num_results,
                type="neural",
                text={"max_characters": 2000},  # Get more content
            )
            
            print(f"🔍 Exa: Got response, checking results...")
            
            if not results or not results.results:
                print(f"❌ Exa: No results found")
                return {
                    "success": True,
                    "found": False,
                    "message": "No results found"
                }
            
            print(f"✅ Exa: Found {len(results.results)} results")
            
            formatted_results = []
            for idx, result in enumerate(results.results, 1):
                content = result.text if hasattr(result, 'text') and result.text else ""
                print(f"📄 Exa Result {idx}: {result.title} - content length: {len(content)}")
                
                formatted_results.append({
                    "rank": idx,
                    "title": result.title,
                    "url": result.url,
                    "content": content[:1500] if content else "",  # More content for better answers
                    "source": self._extract_domain(result.url)
                })
            
            return {
                "success": True,
                "found": True,
                "query": query,
                "results_count": len(formatted_results),
                "results": formatted_results
            }
            
        except Exception as e:
            print(f"❌ Exa Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }


# Global searcher instance
_searcher = None

def get_medical_searcher() -> MedicalWebSearcher:
    """Get or create medical web searcher instance."""
    global _searcher
    if _searcher is None:
        _searcher = MedicalWebSearcher()
    return _searcher


# Standalone function for easy access
def search_medical_web(query: str) -> Dict[str, Any]:
    """
    Search the web for medical information.
    
    Args:
        query: Medical search query
        
    Returns:
        Dictionary with search results
    """
    searcher = get_medical_searcher()
    return searcher.search_medical_web(query)

