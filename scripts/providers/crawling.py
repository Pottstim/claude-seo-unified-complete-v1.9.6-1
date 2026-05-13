"""
Crawling Provider abstraction
Supports: Playwright, Selenium, Firecrawl, Browserless, Scrapy
"""

from typing import Any, Dict, List, Optional
from .base import BaseProvider, ProviderConfig
import asyncio


class CrawlingProvider(BaseProvider):
    """Base crawling provider for web scraping and JS rendering"""
    
    @property
    def provider_type(self) -> str:
        return "crawling"
    
    def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """Scrape a single page"""
        raise NotImplementedError("Subclasses must implement scrape()")
    
    def crawl(self, start_url: str, max_pages: int = 50, **kwargs) -> List[Dict[str, Any]]:
        """Crawl multiple pages from start URL"""
        raise NotImplementedError("Subclasses must implement crawl()")


class PlaywrightProvider(CrawlingProvider):
    """
    Playwright provider (open source, local, no API key required)
    Best for: JS rendering, screenshots, browser automation
    """
    
    def is_available(self) -> bool:
        try:
            from playwright.sync_api import sync_playwright
            return True
        except ImportError:
            return False
    
    def _create_client(self) -> Any:
        from playwright.sync_api import sync_playwright
        return sync_playwright()
    
    def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """Scrape a page using Playwright"""
        from playwright.sync_api import sync_playwright
        
        browser_type = self.config.extra.get("browser", "chromium")
        headless = self.config.extra.get("headless", True)
        viewport = self.config.extra.get("viewport", {"width": 1920, "height": 1080})
        user_agent = self.config.extra.get("user_agent")
        disable_images = self.config.extra.get("disable_images", False)
        
        with sync_playwright() as p:
            # Select browser
            if browser_type == "firefox":
                browser = p.firefox.launch(headless=headless)
            elif browser_type == "webkit":
                browser = p.webkit.launch(headless=headless)
            else:
                browser = p.chromium.launch(headless=headless)
            
            context_args = {"viewport": viewport}
            if user_agent:
                context_args["user_agent"] = user_agent
            
            if disable_images:
                context_args["java_script_enabled"] = False
            
            context = browser.new_context(**context_args)
            page = context.new_page()
            
            # Navigate
            response = page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Get content
            html = page.content()
            title = page.title()
            
            # Screenshot if requested
            screenshot = None
            if kwargs.get("screenshot"):
                screenshot = page.screenshot(full_page=True)
            
            browser.close()
        
        return {
            "url": url,
            "html": html,
            "title": title,
            "status": response.status if response else None,
            "screenshot": screenshot,
            "provider": "playwright",
        }
    
    def crawl(self, start_url: str, max_pages: int = 50, **kwargs) -> List[Dict[str, Any]]:
        """Crawl site starting from URL"""
        from playwright.sync_api import sync_playwright
        from urllib.parse import urlparse, urljoin
        from bs4 import BeautifulSoup
        
        results = []
        visited = set()
        to_visit = [start_url]
        base_domain = urlparse(start_url).netloc
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            
            while to_visit and len(visited) < max_pages:
                url = to_visit.pop(0)
                if url in visited:
                    continue
                
                visited.add(url)
                
                try:
                    page = context.new_page()
                    response = page.goto(url, wait_until="networkidle", timeout=30000)
                    
                    if response and response.status == 200:
                        html = page.content()
                        soup = BeautifulSoup(html, "lxml")
                        
                        results.append({
                            "url": url,
                            "html": html,
                            "title": page.title(),
                            "status": 200,
                        })
                        
                        # Find links
                        for link in soup.find_all("a", href=True):
                            href = urljoin(url, link["href"])
                            parsed = urlparse(href)
                            
                            # Same domain only
                            if parsed.netloc == base_domain and href not in visited:
                                to_visit.append(href)
                    
                    page.close()
                except Exception as e:
                    results.append({
                        "url": url,
                        "error": str(e),
                    })
            
            browser.close()
        
        return results


class SeleniumProvider(CrawlingProvider):
    """Selenium provider (open source, local)"""
    
    def is_available(self) -> bool:
        try:
            from selenium import webdriver
            return True
        except ImportError:
            return False
    
    def _create_client(self) -> Any:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        if self.config.extra.get("headless", True):
            options.add_argument("--headless")
        
        return webdriver.Chrome(options=options)
    
    def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """Scrape using Selenium"""
        driver = self.get_client()
        
        try:
            driver.get(url)
            html = driver.page_source
            title = driver.title
            
            return {
                "url": url,
                "html": html,
                "title": title,
                "provider": "selenium",
            }
        finally:
            driver.quit()


class FirecrawlProvider(CrawlingProvider):
    """Firecrawl provider (managed service, bypasses anti-bot)"""
    
    def is_available(self) -> bool:
        return bool(self.config.api_key)
    
    def _create_client(self) -> Any:
        return None
    
    def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """Scrape using Firecrawl API"""
        import requests
        
        api_key = self.config.api_key
        base_url = self.config.api_base or "https://api.firecrawl.dev/v1"
        
        response = requests.post(
            f"{base_url}/scrape",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"url": url},
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        return {
            "url": url,
            "html": data.get("data", {}).get("html"),
            "markdown": data.get("data", {}).get("markdown"),
            "content": data.get("data", {}).get("content"),
            "metadata": data.get("data", {}).get("metadata", {}),
            "provider": "firecrawl",
        }
    
    def crawl(self, start_url: str, max_pages: int = 50, **kwargs) -> List[Dict[str, Any]]:
        """Crawl site using Firecrawl"""
        import requests
        import time
        
        api_key = self.config.api_key
        base_url = self.config.api_base or "https://api.firecrawl.dev/v1"
        
        # Start crawl
        response = requests.post(
            f"{base_url}/crawl",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "url": start_url,
                "limit": max_pages,
            },
            timeout=60
        )
        response.raise_for_status()
        
        job_id = response.json().get("id")
        
        # Poll for results
        while True:
            status_response = requests.get(
                f"{base_url}/crawl/{job_id}",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            status_response.raise_for_status()
            
            status_data = status_response.json()
            
            if status_data.get("status") == "completed":
                return status_data.get("data", [])
            elif status_data.get("status") == "failed":
                raise Exception("Crawl failed")
            
            time.sleep(5)


class RequestsProvider(CrawlingProvider):
    """Simple requests-based provider (no JS rendering, fastest)"""
    
    def is_available(self) -> bool:
        return True
    
    def _create_client(self) -> Any:
        return None
    
    def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """Scrape using requests"""
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            "User-Agent": self.config.extra.get(
                "user_agent",
                "Mozilla/5.0 (compatible; SEO-Bot/1.0)"
            )
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "lxml")
        
        return {
            "url": url,
            "html": response.text,
            "title": soup.title.string if soup.title else None,
            "status": response.status_code,
            "provider": "requests",
        }


# Provider registry
CRAWLING_PROVIDERS = {
    "playwright": PlaywrightProvider,
    "selenium": SeleniumProvider,
    "firecrawl": FirecrawlProvider,
    "requests": RequestsProvider,
}


def get_crawling_provider(provider_name: str = None, config: Dict = None) -> CrawlingProvider:
    """Get crawling provider by name or from config"""
    if config is None:
        config = BaseProvider.load_config()
    
    crawl_config = config.get("crawling", {})
    
    if provider_name is None:
        provider_name = crawl_config.get("active_provider", "playwright")
    
    providers_config = crawl_config.get("providers", {})
    provider_config = providers_config.get(provider_name, {})
    
    provider_class = CRAWLING_PROVIDERS.get(provider_name, PlaywrightProvider)
    return provider_class(ProviderConfig.from_dict(provider_name, provider_config))
