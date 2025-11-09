import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class SRSService:
    def __init__(self):
        pass
    
    def parse_user_stories(self, srs_content: str) -> List[Dict]:
        """
        Parse user stories from SRS content
        
        Args:
            srs_content: SRS document content
            
        Returns:
            List of user stories
        """
        user_stories = []
        lines = srs_content.split("\n")
        
        current_story = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for user story patterns
            if "US-" in line or "User Story" in line or "As a" in line:
                if current_story:
                    user_stories.append(current_story)
                
                current_story = {
                    "title": line,
                    "description": "",
                    "acceptanceCriteria": []
                }
            elif current_story and ("Acceptance Criteria" in line or "Criteria:" in line):
                continue
            elif current_story and line.startswith("-") or line.startswith("*"):
                current_story["acceptanceCriteria"].append(line.lstrip("- *"))
            elif current_story:
                current_story["description"] += line + " "
        
        if current_story:
            user_stories.append(current_story)
        
        return user_stories

