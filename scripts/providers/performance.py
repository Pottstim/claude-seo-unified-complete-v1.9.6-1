"""
Performance Provider abstraction
Supports: Lighthouse CLI (local), PageSpeed API, CrUX API, Web Vitals JS
"""

from typing import Any, Dict, List, Optional
from .base import BaseProvider, ProviderConfig
import subprocess
import json
import os


class PerformanceProvider(BaseProvider):
    """Base performance provider for Core Web Vitals and PageSpeed data"""
    
    @property
    def provider_type(self) -> str:
        return "performance"
    
    def analyze(
        self,
        url: str,
        categories: List[str] = None,
        strategy: str = "mobile",
        **kwargs
    ) -> Dict[str, Any]:
        """Run performance analysis on URL"""
        raise NotImplementedError("Subclasses must implement analyze()")
    
    def get_core_web_vitals(self, url: str, **kwargs) -> Dict[str, Any]:
        """Get Core Web Vitals metrics"""
        raise NotImplementedError("Subclasses must implement get_core_web_vitals()")


class LighthouseProvider(PerformanceProvider):
    """
    Lighthouse CLI provider (open source, no API key required)
    Runs locally via Node.js
    """
    
    def is_available(self) -> bool:
        """Check if lighthouse is installed"""
        try:
            result = subprocess.run(
                ["lighthouse", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def _create_client(self) -> Any:
        return None  # CLI-based, no client needed
    
    def analyze(
        self,
        url: str,
        categories: List[str] = None,
        strategy: str = "mobile",
        **kwargs
    ) -> Dict[str, Any]:
        """Run lighthouse analysis"""
        if categories is None:
            categories = ["performance", "accessibility", "best-practices", "seo"]
        
        # Map categories to lighthouse flags
        category_flags = []
        category_map = {
            "performance": "--only-categories=performance",
            "accessibility": "--only-categories=accessibility",
            "best-practices": "--only-categories=best-practices",
            "seo": "--only-categories=seo",
        }
        
        if len(categories) == 4:
            # All categories, no flag needed
            pass
        else:
            for cat in categories:
                if cat in category_map:
                    category_flags.append(category_map[cat])
        
        # Build command
        output_path = kwargs.get("output_path", "/tmp/lighthouse-report.json")
        
        cmd = [
            "lighthouse",
            url,
            "--output=json",
            f"--output-path={output_path}",
            f"--preset={'mobile' if strategy == 'mobile' else 'desktop'}",
            "--chrome-flags=--headless --no-sandbox --disable-gpu",
            "--quiet",
        ] + category_flags
        
        # Run lighthouse
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Lighthouse failed: {result.stderr}")
        
        # Parse results
        with open(output_path) as f:
            report = json.load(f)
        
        # Extract key metrics
        return self._parse_lighthouse_report(report, url)
    
    def _parse_lighthouse_report(self, report: Dict, url: str) -> Dict[str, Any]:
        """Parse lighthouse report into standardized format"""
        categories = report.get("categories", {})
        audits = report.get("audits", {})
        
        def get_score(cat_name: str) -> Optional[float]:
            cat = categories.get(cat_name, {})
            score = cat.get("score")
            return round(score * 100, 1) if score is not None else None
        
        def get_metric(metric_id: str) -> Optional[float]:
            audit = audits.get(metric_id, {})
            value = audit.get("numericValue")
            return round(value, 0) if value is not None else None
        
        return {
            "url": url,
            "provider": "lighthouse",
            "scores": {
                "performance": get_score("performance"),
                "accessibility": get_score("accessibility"),
                "best_practices": get_score("best-practices"),
                "seo": get_score("seo"),
            },
            "core_web_vitals": {
                "lcp": get_metric("largest-contentful-paint"),
                "fid": get_metric("max-potential-fid"),  # Lab approximation
                "cls": get_metric("cumulative-layout-shift"),
                "inp": get_metric("interaction-to-next-paint"),
                "fcp": get_metric("first-contentful-paint"),
                "ttfb": get_metric("server-response-time"),
                "tbt": get_metric("total-blocking-time"),
                "si": get_metric("speed-index"),
            },
            "lighthouse_version": report.get("lighthouseVersion"),
            "fetch_time": report.get("fetchTime"),
            "audits": audits,  # Full audit details
        }
    
    def get_core_web_vitals(self, url: str, **kwargs) -> Dict[str, Any]:
        """Get Core Web Vitals from lighthouse"""
        result = self.analyze(url, categories=["performance"], **kwargs)
        return result.get("core_web_vitals", {})


class PageSpeedAPIProvider(PerformanceProvider):
    """Google PageSpeed Insights API provider"""
    
    def is_available(self) -> bool:
        return bool(self.config.api_key)
    
    def _create_client(self) -> Any:
        return None  # Use requests
    
    def analyze(
        self,
        url: str,
        categories: List[str] = None,
        strategy: str = "mobile",
        **kwargs
    ) -> Dict[str, Any]:
        """Run PageSpeed analysis via API"""
        import requests
        
        if categories is None:
            categories = ["performance", "accessibility", "best-practices", "seo"]
        
        api_key = self.config.api_key
        if not api_key:
            raise ValueError("GOOGLE_PAGESPEED_API_KEY required")
        
        params = {
            "url": url,
            "key": api_key,
            "strategy": strategy,
            "category": categories,
        }
        
        response = requests.get(
            "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
            params=params,
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        return self._parse_pagespeed_response(data, url, strategy)
    
    def _parse_pagespeed_response(self, data: Dict, url: str, strategy: str) -> Dict[str, Any]:
        """Parse PageSpeed API response"""
        lighthouse = data.get("lighthouseResult", {})
        categories = lighthouse.get("categories", {})
        audits = lighthouse.get("audits", {})
        
        def get_score(cat_name: str) -> Optional[float]:
            cat = categories.get(cat_name, {})
            score = cat.get("score")
            return round(score * 100, 1) if score is not None else None
        
        def get_metric(metric_id: str) -> Optional[float]:
            audit = audits.get(metric_id, {})
            value = audit.get("numericValue")
            return round(value, 0) if value is not None else None
        
        return {
            "url": url,
            "provider": "pagespeed_api",
            "strategy": strategy,
            "scores": {
                "performance": get_score("performance"),
                "accessibility": get_score("accessibility"),
                "best_practices": get_score("best-practices"),
                "seo": get_score("seo"),
            },
            "core_web_vitals": {
                "lcp": get_metric("largest-contentful-paint"),
                "fid": get_metric("max-potential-fid"),
                "cls": get_metric("cumulative-layout-shift"),
                "inp": get_metric("interaction-to-next-paint"),
                "fcp": get_metric("first-contentful-paint"),
                "ttfb": get_metric("server-response-time"),
            },
            "loading_experience": data.get("loadingExperience", {}),
            "origin_loading_experience": data.get("originLoadingExperience", {}),
        }
    
    def get_core_web_vitals(self, url: str, **kwargs) -> Dict[str, Any]:
        """Get Core Web Vitals from PageSpeed API"""
        result = self.analyze(url, categories=["performance"], **kwargs)
        return result.get("core_web_vitals", {})


class CrUXAPIProvider(PerformanceProvider):
    """Chrome UX Report API provider (real user data)"""
    
    def is_available(self) -> bool:
        return bool(self.config.api_key)
    
    def _create_client(self) -> Any:
        return None
    
    def analyze(self, url: str, **kwargs) -> Dict[str, Any]:
        """Get CrUX data for URL"""
        import requests
        
        api_key = self.config.api_key
        if not api_key:
            raise ValueError("GOOGLE_CRUX_API_KEY required")
        
        response = requests.get(
            f"https://chromeuxreport.googleapis.com/v1/records:queryRecord?key={api_key}",
            json={"url": url},
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        return self._parse_crux_response(data, url)
    
    def _parse_crux_response(self, data: Dict, url: str) -> Dict[str, Any]:
        """Parse CrUX API response"""
        record = data.get("record", {})
        metrics = record.get("metrics", {})
        
        def get_histogram(metric_name: str) -> List[Dict]:
            metric = metrics.get(metric_name, {})
            return metric.get("histogram", [])
        
        def get_percentile(metric_name: str, percentile: int = 75) -> Optional[float]:
            metric = metrics.get(metric_name, {})
            percentiles = metric.get("percentiles", {})
            return percentiles.get(str(percentile))
        
        return {
            "url": url,
            "provider": "crux_api",
            "data_type": "real_user_data",
            "collection_period": record.get("collectionPeriod", {}),
            "core_web_vitals": {
                "lcp": {
                    "p75": get_percentile("largest_contentful_paint"),
                    "histogram": get_histogram("largest_contentful_paint"),
                },
                "inp": {
                    "p75": get_percentile("interaction_to_next_paint"),
                    "histogram": get_histogram("interaction_to_next_paint"),
                },
                "cls": {
                    "p75": get_percentile("cumulative_layout_shift"),
                    "histogram": get_histogram("cumulative_layout_shift"),
                },
                "fcp": {
                    "p75": get_percentile("first_contentful_paint"),
                    "histogram": get_histogram("first_contentful_paint"),
                },
                "ttfb": {
                    "p75": get_percentile("experimental_time_to_first_byte"),
                    "histogram": get_histogram("experimental_time_to_first_byte"),
                },
            },
        }
    
    def get_core_web_vitals(self, url: str, **kwargs) -> Dict[str, Any]:
        """Get Core Web Vitals from CrUX"""
        result = self.analyze(url, **kwargs)
        return result.get("core_web_vitals", {})


# Provider registry
PERFORMANCE_PROVIDERS = {
    "lighthouse": LighthouseProvider,
    "pagespeed_api": PageSpeedAPIProvider,
    "crux_api": CrUXAPIProvider,
}


def get_performance_provider(provider_name: str = None, config: Dict = None) -> PerformanceProvider:
    """Get performance provider by name or from config"""
    if config is None:
        config = BaseProvider.load_config()
    
    perf_config = config.get("performance", {})
    
    if provider_name is None:
        provider_name = perf_config.get("active_provider", "lighthouse")
    
    providers_config = perf_config.get("providers", {})
    provider_config = providers_config.get(provider_name, {})
    
    provider_class = PERFORMANCE_PROVIDERS.get(provider_name, LighthouseProvider)
    return provider_class(ProviderConfig.from_dict(provider_name, provider_config))
