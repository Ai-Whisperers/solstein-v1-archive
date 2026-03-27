"""Locust load testing configuration.

Usage:
    locust -f tests/performance/locustfile.py --host=http://localhost:8000
"""

from locust import HttpUser, between, task


class APIUser(HttpUser):
    """Simulate API user behavior."""

    wait_time = between(1, 3)

    def on_start(self):
        """Login on start."""
        # Authenticate if needed
        pass

    @task(10)
    def get_companies(self):
        """Browse companies list."""
        self.client.get("/api/v1/companies")

    @task(5)
    def get_company_detail(self):
        """View company details."""
        self.client.get("/api/v1/companies/123")

    @task(3)
    def search_companies(self):
        """Search companies."""
        self.client.get("/api/v1/companies/search?q=test")

    @task(1)
    def create_research(self):
        """Create research run."""
        self.client.post("/api/v1/research", json={"market": "energy", "filters": {}})

    @task(1)
    def generate_export(self):
        """Generate export."""
        self.client.post("/api/v1/exports", json={"format": "xlsx", "company_ids": ["123"]})


class HeavyUser(HttpUser):
    """Simulate heavy API user."""

    wait_time = between(0.5, 1)

    @task(1)
    def bulk_operations(self):
        """Perform bulk operations."""
        for i in range(10):
            self.client.get(f"/api/v1/companies/{i}")
