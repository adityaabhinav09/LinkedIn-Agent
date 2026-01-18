"""LinkedIn API wrapper for posting content."""

import requests
from typing import Optional, Dict, Any
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_ID, LINKEDIN_API_BASE_URL


class LinkedInAPI:
    """Wrapper for LinkedIn API to create posts."""
    
    def __init__(self, access_token: str = None, person_id: str = None):
        """
        Initialize LinkedIn API client.
        
        Args:
            access_token: LinkedIn OAuth access token
            person_id: LinkedIn person URN (format: urn:li:person:XXXXX)
        """
        self.access_token = access_token or LINKEDIN_ACCESS_TOKEN
        self.person_id = person_id or LINKEDIN_PERSON_ID
        self.base_url = LINKEDIN_API_BASE_URL
        
        if not self.person_id.startswith("urn:li:person:"):
            self.person_id = f"urn:li:person:{self.person_id}"
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202401"
        }
    
    def create_text_post(self, text: str, visibility: str = "PUBLIC") -> Dict[str, Any]:
        """
        Create a text-only post on LinkedIn.
        
        Args:
            text: The post content
            visibility: Post visibility (PUBLIC, CONNECTIONS)
            
        Returns:
            API response with post details
        """
        url = f"{self.base_url}/ugcPosts"
        
        payload = {
            "author": self.person_id,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            # Extract post ID from response header
            post_id = response.headers.get("x-restli-id", "")
            
            return {
                "success": True,
                "post_id": post_id,
                "message": "Post created successfully!",
                "response": response.json() if response.text else {}
            }
            
        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_detail = response.json()
            except:
                error_detail = response.text
                
            return {
                "success": False,
                "error": str(e),
                "detail": error_detail,
                "status_code": response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "detail": "Network error occurred"
            }
    
    def verify_credentials(self) -> Dict[str, Any]:
        """
        Verify that the credentials are valid.
        
        Returns:
            Dict with verification status and profile info
        """
        url = f"{self.base_url}/me"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            profile = response.json()
            return {
                "valid": True,
                "profile": {
                    "id": profile.get("id"),
                    "firstName": profile.get("localizedFirstName"),
                    "lastName": profile.get("localizedLastName")
                }
            }
        except requests.exceptions.RequestException as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Get details of a specific post.
        
        Args:
            post_id: The post URN
            
        Returns:
            Post details
        """
        url = f"{self.base_url}/ugcPosts/{post_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return {
                "success": True,
                "post": response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_post(self, post_id: str) -> Dict[str, Any]:
        """
        Delete a post.
        
        Args:
            post_id: The post URN
            
        Returns:
            Deletion status
        """
        url = f"{self.base_url}/ugcPosts/{post_id}"
        
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return {
                "success": True,
                "message": "Post deleted successfully"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }


class MockLinkedInAPI:
    """Mock LinkedIn API for testing without actual posting."""
    
    def __init__(self, *args, **kwargs):
        self.post_counter = 0
    
    def create_text_post(self, text: str, visibility: str = "PUBLIC") -> Dict[str, Any]:
        """Simulate creating a post."""
        self.post_counter += 1
        return {
            "success": True,
            "post_id": f"mock_post_{self.post_counter}",
            "message": "[MOCK] Post would be created",
            "content_preview": text[:100] + "..."
        }
    
    def verify_credentials(self) -> Dict[str, Any]:
        """Simulate credential verification."""
        return {
            "valid": True,
            "profile": {
                "id": "mock_user",
                "firstName": "Test",
                "lastName": "User"
            }
        }
