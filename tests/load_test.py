#!/usr/bin/env python3
"""
Load testing suite for claude-seo-unified API
Run with: locust -f tests/load_test.py --host http://localhost:5000
"""

import random
import string
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, WorkerRunner


class SEOAnalysisUser(HttpUser):
    """Simulates a user performing SEO analysis"""
    
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    
    # Sample URLs for testing
    test_urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://www.wikipedia.org",
        "https://www.github.com",
        "https://www.python.org",
        "https://news.ycombinator.com",
        "https://www.reddit.com",
        "https://www.stackoverflow.com",
    ]
    
    def on_start(self):
        """Called when user starts - create API key"""
        response = self.client.post("/api/keys", json={
            "name": f"load_test_user_{random.randint(1000, 9999)}",
            "email": f"loadtest{random.randint(1000, 9999)}@example.com"
        })
        if response.status_code == 200:
            self.api_key = response.json().get("api_key")
        else:
            self.api_key = None
    
    @task(10)
    def health_check(self):
        """Check API health (most common)"""
        self.client.get("/api/health", name="/api/health")
    
    @task(5)
    def analyze_page(self):
        """Analyze a random page"""
        url = random.choice(self.test_urls)
        self.client.post(
            "/api/analyze",
            json={"url": url},
            headers={"X-API-Key": self.api_key} if self.api_key else {},
            name="/api/analyze"
        )
    
    @task(2)
    def get_report(self):
        """Get report by ID"""
        # Use a fake report ID to test 404 response
        report_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
        self.client.get(f"/api/report/{report_id}", name="/api/report/[id]")
    
    @task(1)
    def create_api_key(self):
        """Create a new API key"""
        self.client.post("/api/keys", json={
            "name": f"test_user_{random.randint(10000, 99999)}",
            "email": f"test{random.randint(10000, 99999)}@example.com"
        }, name="/api/keys")


class BatchAnalysisUser(HttpUser):
    """Simulates a user performing batch analysis"""
    
    wait_time = between(5, 15)
    
    def on_start(self):
        """Create API key for batch operations"""
        response = self.client.post("/api/keys", json={
            "name": f"batch_user_{random.randint(1000, 9999)}",
            "email": f"batch{random.randint(1000, 9999)}@example.com"
        })
        if response.status_code == 200:
            self.api_key = response.json().get("api_key")
        else:
            self.api_key = None
    
    @task(3)
    def batch_analyze(self):
        """Analyze multiple URLs at once"""
        urls = random.sample(SEOAnalysisUser.test_urls, min(5, len(SEOAnalysisUser.test_urls)))
        self.client.post(
            "/api/batch",
            json={"urls": urls},
            headers={"X-API-Key": self.api_key} if self.api_key else {},
            name="/api/batch"
        )


class HeavyAnalysisUser(HttpUser):
    """Simulates heavy API usage - for stress testing"""
    
    wait_time = between(0.5, 2)
    
    @task
    def rapid_analyze(self):
        """Rapid fire analysis requests"""
        url = random.choice(SEOAnalysisUser.test_urls)
        self.client.post(
            "/api/analyze",
            json={"url": url},
            name="/api/analyze [heavy]"
        )


# Custom event handlers for reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    print("\n" + "=" * 60)
    print("SEO Unified API Load Test Starting")
    print("=" * 60)
    if isinstance(environment.runner, MasterRunner):
        print("Running in distributed mode (master)")
    elif isinstance(environment.runner, WorkerRunner):
        print("Running in distributed mode (worker)")
    else:
        print("Running in standalone mode")
    print(f"Target host: {environment.host}")
    print("=" * 60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    print("\n" + "=" * 60)
    print("SEO Unified API Load Test Complete")
    print("=" * 60)
    
    # Print summary stats
    if hasattr(environment, 'stats'):
        stats = environment.stats
        print(f"\nTotal Requests: {stats.total.num_requests}")
        print(f"Total Failures: {stats.total.num_failures}")
        print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
        print(f"Median Response Time: {stats.total.median_response_time:.2f}ms")
        print(f"95th Percentile: {stats.total.get_response_time_percentile(0.95):.2f}ms")
        print(f"Requests/sec: {stats.total.total_rps:.2f}")
    
    print("=" * 60 + "\n")


# Configuration for different load profiles
LOAD_PROFILES = {
    "smoke": {
        "users": 1,
        "spawn_rate": 1,
        "run_time": "1m"
    },
    "average": {
        "users": 10,
        "spawn_rate": 2,
        "run_time": "5m"
    },
    "high": {
        "users": 50,
        "spawn_rate": 5,
        "run_time": "10m"
    },
    "stress": {
        "users": 100,
        "spawn_rate": 10,
        "run_time": "15m"
    },
    "spike": {
        "users": 200,
        "spawn_rate": 50,
        "run_time": "3m"
    }
}


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load test SEO Unified API")
    parser.add_argument(
        "--profile",
        choices=list(LOAD_PROFILES.keys()),
        default="average",
        help="Load profile to use"
    )
    parser.add_argument(
        "--host",
        default="http://localhost:5000",
        help="Target host URL"
    )
    
    args = parser.parse_args()
    profile = LOAD_PROFILES[args.profile]
    
    print(f"\nRunning load test with profile: {args.profile}")
    print(f"Users: {profile['users']}, Spawn Rate: {profile['spawn_rate']}/s, Duration: {profile['run_time']}")
    print(f"Target: {args.host}\n")
    
    # In production, this would invoke locust CLI
    print("Run with: locust -f tests/load_test.py --host " + args.host)
