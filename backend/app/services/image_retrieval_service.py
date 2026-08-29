import urllib.request
import urllib.parse
import re
import ssl
import json
from typing import List

class ImageRetrievalService:
    @classmethod
    def search_bing_thumbnails(cls, query: str, count: int = 15) -> List[str]:
        """Search Bing Images and extract stable thumbnail CDN URLs."""
        url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        ssl_ctx = ssl._create_unverified_context()
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12, context=ssl_ctx) as response:
                body = response.read().decode('utf-8')
                
                # Find CDN image source URLs containing bing.net/th
                matches = re.findall(r'src="(https?://[^"]*bing\.net/th/[^"]+)"', body)
                
                urls = []
                for m in matches:
                    clean_url = m.replace('&amp;', '&')
                    if clean_url not in urls:
                        urls.append(clean_url)
                        if len(urls) >= count:
                            break
                return urls
        except Exception as e:
            print(f"Error searching Bing thumbnails for query '{query}': {e}")
            return []

    @classmethod
    def get_unique_property_images(cls, prop_id: int, title: str, locality: str, property_type: str) -> List[str]:
        """Retrieve a list of unique, realistic property images using property title, locality, and type."""
        # Clean title to avoid code strings or codes
        clean_title = (title or "").strip()
        if "bhk" in clean_title.lower() or "bedroom" in clean_title.lower():
            clean_title = f"{property_type} in {locality}"

        # 1. Search for specific property building exterior
        query_specific = f"{clean_title} {locality} Bengaluru exterior"
        urls = cls.search_bing_thumbnails(query_specific, count=15)
        if urls:
            start_idx = prop_id % len(urls)
            rotated_urls = urls[start_idx:] + urls[:start_idx]
            return rotated_urls[:5]
            
        # 2. Fallback to locality + property type exterior
        query_locality = f"{locality} Bengaluru {property_type} building exterior"
        urls = cls.search_bing_thumbnails(query_locality, count=15)
        if urls:
            start_idx = prop_id % len(urls)
            rotated_urls = urls[start_idx:] + urls[:start_idx]
            return rotated_urls[:5]
            
        # 3. Generic Bangalore real estate fallback
        query_generic = f"luxury {property_type} building Bangalore"
        urls = cls.search_bing_thumbnails(query_generic, count=15)
        if urls:
            start_idx = prop_id % len(urls)
            rotated_urls = urls[start_idx:] + urls[:start_idx]
            return rotated_urls[:5]
            
        # 4. Ultimate static fallback (using original local Prestige/Sobha images if search fails)
        fallbacks = [
            "/static/images/original_prestige.jpg",
            "/static/images/original_sobha.jpg",
            "/static/images/original_lnt.jpg"
        ]
        return [fallbacks[prop_id % len(fallbacks)]]
