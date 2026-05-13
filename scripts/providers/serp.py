"""
SERP Provider abstraction
Supports: DataForSEO, SerpAPI, ValueSERP, ScraperAPI, Custom scraping
"""

from typing import Any, Dict, List, Optional
from .base import BaseProvider, ProviderConfig


class SERPProvider(BaseProvider):
    """Base SERP provider for keyword research and ranking data"""
    
    @property
    def provider_type(self) -> str:
        return "serp"
    
    def search(self, query: str, location: str = "United States", **kwargs) -> Dict[str, Any]:
        """Get SERP results for a query"""
        raise NotImplementedError("Subclasses must implement search()")
    
    def get_keyword_data(self, keyword: str, **kwargs) -> Dict[str, Any]:
        """Get keyword volume and difficulty data"""
        raise NotImplementedError("Subclasses must implement get_keyword_data()")


class DataForSEOProvider(SERPProvider):
    """DataForSEO provider (comprehensive, pay-per-use)"""
    
    def is_available(self) -> bool:
        return bool(self.config.extra.get("username") and self.config.extra.get("password"))
    
    def _create_client(self) -> Any:
        return None
    
    def search(self, query: str, location: str = "United States", **kwargs) -> Dict[str, Any]:
        """Get SERP results via DataForSEO"""
        import requests
        
        username = self.config.extra.get("username")
        password = self.config.extra.get("password")
        
        response = requests.post(
            "https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
            auth=(username, password),
            json=[{
                "keyword": query,
                "location_name": location,
                "language_name": "English",
            }],
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        return self._parse_dataforseo_response(data, query)
    
    def _parse_dataforseo_response(self, data: Dict, query: str) -> Dict[str, Any]:
        """Parse DataForSEO SERP response"""
        tasks = data.get("tasks", [])
        if not tasks:
            return {"query": query, "error": "No results"}
        
        result = tasks[0].get("result", [])
        if not result:
            return {"query": query, "error": "No results"}
        
        items = result[0].get("items", [])
        
        organic_results = []
        for item in items:
            if item.get("type") == "organic":
                organic_results.append({
                    "position": item.get("rank_group"),
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "domain": item.get("domain"),
                    "description": item.get("description"),
                })
        
        return {
            "query": query,
            "provider": "dataforseo",
            "total_results": result[0].get("items_count", 0),
            "results": organic_results,
        }


class SerpAPIProvider(SERPProvider):
    """SerpAPI provider (popular, good free tier)"""
    
    def is_available(self) -> bool:
        return bool(self.config.api_key)
    
    def _create_client(self) -> Any:
        return None
    
    def search(self, query: str, location: str = "United States", **kwargs) -> Dict[str, Any]:
        """Get SERP results via SerpAPI"""
        import requests
        
        api_key = self.config.api_key
        
        response = requests.get(
            "https://serpapi.com/search",
            params={
                "q": query,
                "location": location,
                "api_key": api_key,
                "engine": "google",
            },
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        return self._parse_serpapi_response(data, query)
    
    def _parse_serpapi_response(self, data: Dict, query: str) -> Dict[str, Any]:
        """Parse SerpAPI response"""
        organic_results = data.get("organic_results", [])
        
        results = []
        for item in organic_results:
            results.append({
                "position": item.get("position"),
                "title": item.get("title"),
                "url": item.get("link"),
                "domain": item.get("displayed_link", "").split("/")[0] if item.get("displayed_link") else None,
                "description": item.get("snippet"),
            })
        
        return {
            "query": query,
            "provider": "serpapi",
            "total_results": data.get("search_information", {}).get("total_results", 0),
            "results": results,
        }


class CustomScraperProvider(SERPProvider):
    """
    Custom scraper provider (self-hosted, open source)
    Uses Playwright with rotating proxies
    """
    
    def is_available(self) -> bool:
        return True  # Always available, uses local Playwright
    
    def _create_client(self) -> Any:
        return None
    
    def search(self, query: str, location: str = "United States", **kwargs) -> Dict[str, Any]:
        """Scrape Google SERP using Playwright"""
        from playwright.sync_api import sync_playwright
        from urllib.parse import quote_plus
        from bs4 import BeautifulSoup
        
        encoded_query = quote_plus(query)
        url = f"https://www.google.com/search?q={encoded_query}&num=100"
        
        results = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
                html = page.content()
                
                soup = BeautifulSoup(html, "lxml")
                
                for i, result in enumerate(soup.select("#search .g"), 1):
                    title_elem = result.select_one("h3")
                    link_elem = result.select_one("a[href^='http']")
                    desc_elem = result.select_one("[data-sncf]")
                    
                    if title_elem and link_elem:
                        results.append({
                            "position": i,
                            "title": title_elem.get_text(strip=True),
                            "url": link_elem.get("href"),
                            "description": desc_elem.get_text(strip=True) if desc_elem else None,
                        })
            except Exception as e:
                return {"query": query, "error": str(e)}
            finally:
                browser.close()
        
        return {
            "query": query,
            "provider": "custom_scrape",
            "total_results": len(results),
            "results": results,
        }


# Provider registry
SERP_PROVIDERS = {
    "dataforseo": DataForSEOProvider,
    "serpapi": SerpAPIProvider,
    "valueserp": SerpAPIProvider,  # Similar API
    "scraperapi": SerpAPIProvider,  # Similar usage
    "custom_scrape": CustomScraperProvider,
}


def get_serp_provider(provider_name: str = None, config: Dict = None) -> SERPProvider:
    """Get SERP provider by name or from config"""
    if config is None:
        config = BaseProvider.load_config()
    
    serp_config = config.get("serp", {})
    
    if provider_name is None:
        provider_name = serp_config.get("active_provider")
        if not provider_name:
            # Fall back to custom scraper (free, no API key)
            return CustomScraperProvider(ProviderConfig(name="custom_scrape"))
    
    providers_config = serp_config.get("providers", {})
    provider_config = providers_config.get(provider_name, {})
    
    provider_class = SERP_PROVIDERS.get(provider_name, CustomScraperProvider)
    return provider_class(ProviderConfig.from_dict(provider_name, provider_config))
