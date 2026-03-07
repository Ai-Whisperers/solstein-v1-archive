#!/usr/bin/env python3
"""Client SDK Generator for EPIC-024 Story 5.

Generates Python and TypeScript SDKs from OpenAPI spec.

Usage:
    python scripts/generate_sdk.py --language python --output ./sdk/python
    python scripts/generate_sdk.py --language typescript --output ./sdk/typescript
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def generate_python_sdk(openapi_spec: dict, output_dir: Path) -> None:
    """Generate Python SDK from OpenAPI spec."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate client.py
    client_code = '''"""Solstein API Python SDK.

Auto-generated from OpenAPI spec.
"""

from __future__ import annotations

import httpx
from typing import Any, Optional


class SolsteinClient:
    """Solstein API client."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.solstein.ai"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(
            headers={"X-API-Key": api_key},
            timeout=30.0
        )
    
    def _request(self, method: str, path: str, **kwargs) -> Any:
        """Make API request."""
        url = f"{self.base_url}{path}"
        response = self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    # Companies
    def list_companies(self) -> list[dict]:
        """List all companies."""
        return self._request("GET", "/api/v1/companies")
    
    def get_company(self, company_id: str) -> dict:
        """Get company by ID."""
        return self._request("GET", f"/api/v1/companies/{company_id}")
    
    def create_company(self, data: dict) -> dict:
        """Create new company."""
        return self._request("POST", "/api/v1/companies", json=data)
    
    # Scoring
    def get_company_score(self, company_id: str) -> dict:
        """Get company scores."""
        return self._request("GET", f"/api/v1/scoring/company/{company_id}/score")
    
    def calculate_score(self, company_id: str) -> dict:
        """Calculate company scores."""
        return self._request("POST", f"/api/v1/scoring/company/{company_id}/score")
    
    # Export
    def export_company(self, company_id: str, format: str = "json") -> bytes:
        """Export company data."""
        response = self.client.get(
            f"{self.base_url}/api/v1/export/{format}/{company_id}",
            headers={"X-API-Key": self.api_key}
        )
        response.raise_for_status()
        return response.content
    
    def close(self) -> None:
        """Close client."""
        self.client.close()
    
    def __enter__(self) -> SolsteinClient:
        return self
    
    def __exit__(self, *args) -> None:
        self.close()
'''

    (output_dir / "client.py").write_text(client_code)

    # Generate __init__.py
    init_code = '''"""Solstein API Python SDK.

Usage:
    from solstein import SolsteinClient
    
    client = SolsteinClient(api_key="your-api-key")
    companies = client.list_companies()
"""

from .client import SolsteinClient

__version__ = "1.0.0"
__all__ = ["SolsteinClient"]
'''

    (output_dir / "__init__.py").write_text(init_code)

    # Generate pyproject.toml
    pyproject = """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "solstein"
version = "1.0.0"
description = "Solstein API Python SDK"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "httpx>=0.24.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black>=23.0",
]
"""

    (output_dir / "pyproject.toml").write_text(pyproject)

    print(f"✅ Python SDK generated at {output_dir}")


def generate_typescript_sdk(openapi_spec: dict, output_dir: Path) -> None:
    """Generate TypeScript SDK from OpenAPI spec."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate client.ts
    client_code = '''"""Solstein API TypeScript SDK.

Auto-generated from OpenAPI spec.
"""

export interface Company {
  id: string;
  name: string;
  industry?: string;
  revenue?: number;
  growth_score?: number;
  financial_health_score?: number;
  competitive_position_score?: number;
  composite_score?: number;
  classification?: string;
}

export interface ScoreResult {
  company_id: string;
  growth_score: number;
  financial_health_score: number;
  competitive_position_score: number;
  composite_score: number;
  classification: string;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
    timestamp: string;
    request_id?: string;
  };
}

export class SolsteinClient {
  private apiKey: string;
  private baseUrl: string;

  constructor(apiKey: string, baseUrl: string = "https://api.solstein.ai") {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.replace(/\\/$/, "");
  }

  private async request<T>(method: string, path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers: {
        "X-API-Key": this.apiKey,
        "Content-Type": "application/json",
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json() as ApiError;
      throw new Error(error.error.message);
    }

    return response.json() as Promise<T>;
  }

  // Companies
  async listCompanies(): Promise<Company[]> {
    return this.request<Company[]>("GET", "/api/v1/companies");
  }

  async getCompany(companyId: string): Promise<Company> {
    return this.request<Company>("GET", `/api/v1/companies/${companyId}`);
  }

  async createCompany(data: Partial<Company>): Promise<Company> {
    return this.request<Company>("POST", "/api/v1/companies", {
      body: JSON.stringify(data),
    });
  }

  // Scoring
  async getCompanyScore(companyId: string): Promise<ScoreResult> {
    return this.request<ScoreResult>("GET", `/api/v1/scoring/company/${companyId}/score`);
  }

  async calculateScore(companyId: string): Promise<ScoreResult> {
    return this.request<ScoreResult>("POST", `/api/v1/scoring/company/${companyId}/score`);
  }
}

export default SolsteinClient;
'''

    (output_dir / "client.ts").write_text(client_code)

    # Generate package.json
    package_json = """{
  "name": "@solstein/api",
  "version": "1.0.0",
  "description": "Solstein API TypeScript SDK",
  "main": "dist/client.js",
  "types": "dist/client.d.ts",
  "scripts": {
    "build": "tsc",
    "test": "jest"
  },
  "dependencies": {},
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0"
  }
}
"""

    (output_dir / "package.json").write_text(package_json)

    # Generate tsconfig.json
    tsconfig = """{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "declaration": true,
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["*.ts"],
  "exclude": ["node_modules", "dist"]
}
"""

    (output_dir / "tsconfig.json").write_text(tsconfig)

    print(f"✅ TypeScript SDK generated at {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Generate Solstein API SDKs")
    parser.add_argument(
        "--language", choices=["python", "typescript", "both"], default="both", help="SDK language to generate"
    )
    parser.add_argument("--output", type=Path, default=Path("./sdk"), help="Output directory")
    parser.add_argument("--spec", type=Path, help="OpenAPI spec file (optional, will generate from app)")

    args = parser.parse_args()

    # Get OpenAPI spec
    if args.spec:
        openapi_spec = json.loads(args.spec.read_text())
    else:
        # Generate from FastAPI app
        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from solstein.api.main import app

        openapi_spec = app.openapi()

    # Generate SDKs
    if args.language in ("python", "both"):
        generate_python_sdk(openapi_spec, args.output / "python")

    if args.language in ("typescript", "both"):
        generate_typescript_sdk(openapi_spec, args.output / "typescript")

    print(f"\n✅ SDK generation complete!")
    print(f"   Install Python SDK: pip install {args.output}/python")
    print(f"   Install TypeScript SDK: npm install {args.output}/typescript")


if __name__ == "__main__":
    main()
