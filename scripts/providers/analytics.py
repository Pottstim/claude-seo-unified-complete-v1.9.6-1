"""
Analytics Provider abstraction
Supports: Google Search Console, Google Analytics, Plausible, Matomo, Custom
"""

from typing import Any, Dict, List, Optional
from .base import BaseProvider, ProviderConfig


class AnalyticsProvider(BaseProvider):
    """Base analytics provider for search console and traffic data"""
    
    @property
    def provider_type(self) -> str:
        return "analytics"
    
    def get_search_analytics(self, url: str, days: int = 30, **kwargs) -> Dict[str, Any]:
        """Get search console / organic traffic data"""
        raise NotImplementedError("Subclasses must implement get_search_analytics()")


class GoogleSearchConsoleProvider(AnalyticsProvider):
    """Google Search Console API provider"""
    
    def is_available(self) -> bool:
        # Check for credentials file
        creds_path = self.config.extra.get("credentials_path")
        return bool(creds_path)
    
    def _create_client(self) -> Any:
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            return build, service_account
        except ImportError:
            raise ImportError("Install with: pip install google-api-python-client google-auth")
    
    def get_search_analytics(self, url: str, days: int = 30, **kwargs) -> Dict[str, Any]:
        """Get search analytics from GSC"""
        from datetime import datetime, timedelta
        
        build, service_account = self.get_client()
        
        creds_path = self.config.extra.get("credentials_path")
        credentials = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
        
        service = build("searchconsole", "v1", credentials=credentials)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        request = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "dimensions": ["query", "page"],
            "rowLimit": 1000,
        }
        
        response = service.searchanalytics().query(siteUrl=url, body=request).execute()
        
        rows = response.get("rows", [])
        
        queries = []
        for row in rows:
            queries.append({
                "query": row["keys"][0],
                "page": row["keys"][1],
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": row.get("ctr", 0),
                "position": row.get("position", 0),
            })
        
        return {
            "url": url,
            "provider": "google_search_console",
            "period": f"{days} days",
            "queries": queries,
        }


class PlausibleProvider(AnalyticsProvider):
    """Plausible Analytics provider (privacy-focused, self-hostable)"""
    
    def is_available(self) -> bool:
        return bool(self.config.api_key and self.config.extra.get("site_id"))
    
    def _create_client(self) -> Any:
        return None
    
    def get_search_analytics(self, url: str, days: int = 30, **kwargs) -> Dict[str, Any]:
        """Get analytics from Plausible"""
        import requests
        from datetime import datetime, timedelta
        
        api_key = self.config.api_key
        site_id = self.config.extra.get("site_id")
        base_url = self.config.api_base or "https://plausible.io"
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get top pages
        response = requests.get(
            f"{base_url}/api/v1/stats/breakdown",
            headers={"Authorization": f"Bearer {api_key}"},
            params={
                "site_id": site_id,
                "period": "custom",
                "date": f"{start_date.strftime('%Y-%m-%d')},{end_date.strftime('%Y-%m-%d')}",
                "property": "event:page",
            },
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        pages = []
        for item in data.get("results", []):
            pages.append({
                "page": item.get("page"),
                "visitors": item.get("visitors", 0),
                "pageviews": item.get("pageviews", 0),
            })
        
        return {
            "url": url,
            "provider": "plausible",
            "period": f"{days} days",
            "pages": pages,
        }


class MatomoProvider(AnalyticsProvider):
    """Matomo Analytics provider (open source, self-hosted)"""
    
    def is_available(self) -> bool:
        return bool(self.config.api_base and self.config.extra.get("auth_token"))
    
    def _create_client(self) -> Any:
        return None
    
    def get_search_analytics(self, url: str, days: int = 30, **kwargs) -> Dict[str, Any]:
        """Get analytics from Matomo"""
        import requests
        from datetime import datetime, timedelta
        
        base_url = self.config.api_base
        site_id = self.config.extra.get("site_id")
        auth_token = self.config.extra.get("auth_token")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        response = requests.get(
            f"{base_url}/index.php",
            params={
                "module": "API",
                "method": "Actions.getPageUrls",
                "idSite": site_id,
                "period": "range",
                "date": f"{start_date.strftime('%Y-%m-%d')},{end_date.strftime('%Y-%m-%d')}",
                "format": "JSON",
                "token_auth": auth_token,
            },
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        pages = []
        for item in data:
            pages.append({
                "page": item.get("label"),
                "visits": item.get("nb_visits", 0),
                "hits": item.get("nb_hits", 0),
                "avg_time": item.get("avg_time_on_page", 0),
            })
        
        return {
            "url": url,
            "provider": "matomo",
            "period": f"{days} days",
            "pages": pages,
        }


# Provider registry
ANALYTICS_PROVIDERS = {
    "google_search_console": GoogleSearchConsoleProvider,
    "plausible": PlausibleProvider,
    "matomo": MatomoProvider,
}


def get_analytics_provider(provider_name: str = None, config: Dict = None) -> Optional[AnalyticsProvider]:
    """Get analytics provider by name or from config"""
    if config is None:
        config = BaseProvider.load_config()
    
    analytics_config = config.get("analytics", {})
    
    if provider_name is None:
        provider_name = analytics_config.get("active_provider")
        if not provider_name:
            return None  # Analytics is optional
    
    providers_config = analytics_config.get("providers", {})
    provider_config = providers_config.get(provider_name, {})
    
    provider_class = ANALYTICS_PROVIDERS.get(provider_name)
    if not provider_class:
        return None
    
    return provider_class(ProviderConfig.from_dict(provider_name, provider_config))
