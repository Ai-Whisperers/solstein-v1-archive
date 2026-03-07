# Guide para Jonatan: Implementación de APIs OSINT en Solstein

## TL;DR - Qué hacer

Estás investigando APIs OSINT para Solstein. Cuando tengas tu spreadsheet filtrado, implementá los adapters siguiendo el patrón que describo abajo. **El key insight**: extendé `BaseRefreshConnector` y registrá el adapter en `registry.py`. Eso es todo.

---

## Arquitectura Actual (Simplificado)

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  API Externa    │────▶│   Adapter    │────▶│  RawDataSource  │
│  (OSINT Tool)   │     │ (Vos hacés)  │     │  (Datos crudos) │
└─────────────────┘     └──────────────┘     └─────────────────┘
                                                      │
                       ┌──────────────────────────────┘
                       ▼
              ┌─────────────────┐
              │  Aggregator     │  ◀── Cruzá fuentes, validá
              │  (Ya existe)    │      calculá confianza
              └─────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Company Profile│  ◀── Resultado final
              │  (Enriquecido)  │      con metadatos de fuente
              └─────────────────┘
```

---

## Pattern para Nuevos Adapters (Template)

### Paso 1: Crear el archivo del adapter

**Ubicación**: `src/solstein/adapters/enrichment/{nombre}_unified.py`

**Template completo**:

```python
"""{Nombre} OSINT adapter for Solstein.

Fetches {qué datos provee} from {nombre del servicio}.
Confidence: {0.0-1.0}
Authority: {SourceAuthority.XXX}
"""

from datetime import datetime
from typing import Any

import requests
from loguru import logger

from solstein.domain.models import RawDataSource
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.refresh import BaseRefreshConnector
from solstein.research.discovery import DiscoveryCandidate


class {Nombre}UnifiedAdapter(BaseRefreshConnector):
    """Unified {nombre} adapter implementing the full protocol."""

    def __init__(self, db_manager=None, api_key: str | None = None):
        super().__init__(
            source_name="{nombre}_unified",  # snake_case
            source_type="{tipo}",  # ej: "infrastructure", "people", "security"
            db_manager=db_manager,
            confidence={0.0-1.0},  # Base confidence de esta fuente
        )
        self.api_key = api_key
        self.base_url = "https://api.{servicio}.com/v1"

    # ═══════════════════════════════════════════════════════════════
    # MÉTODO 1: Discovery (Opcional - si la API puede descubrir companies)
    # ═══════════════════════════════════════════════════════════════
    def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        """Discover companies via {servicio}."""
        logger.info(f"Discovering companies in {market} via {self.source_name}")

        # Implementar llamada a API de búsqueda
        # Retornar list[DiscoveryCandidate]

        candidates = []
        # ... lógica de búsqueda ...

        return candidates

    # ═══════════════════════════════════════════════════════════════
    # MÉTODO 2: Enrichment (REQUERIDO - lo más importante)
    # ═══════════════════════════════════════════════════════════════
    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        """Enrich company with {servicio} data."""
        logger.info(f"Enriching {company_name} with {self.source_name} data")

        if not self.api_key:
            logger.warning(f"No API key for {self.source_name}, skipping")
            return self._empty_source(company_id)

        try:
            # 1. Llamar a la API
            data = self._fetch_from_api(company_name, website)

            # 2. Transformar a formato estándar
            processed_data = self._transform_data(data)

            # 3. Retornar RawDataSource
            return RawDataSource(
                source_name=self.source_name,
                source_type=self.source_type,
                company_id=company_id,
                fetch_timestamp=datetime.now(),
                data=processed_data,
                metadata={
                    "api_version": "v1",
                    "records_fetched": len(processed_data.get("items", [])),
                },
            )

        except Exception as e:
            logger.error(f"{self.source_name} enrichment failed: {e}")
            return self._empty_source(company_id)

    def _fetch_from_api(self, company_name: str, website: str | None) -> dict:
        """Call {servicio} API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Ejemplo - ajustar según la API específica
        params = {
            "q": company_name,
            "domain": website,
        }

        response = requests.get(
            f"{self.base_url}/search",
            headers=headers,
            params=params,
            timeout=10,
        )
        response.raise_for_status()

        return response.json()

    def _transform_data(self, raw_data: dict) -> dict:
        """Transform API response to standardized format."""
        return {
            "raw_response": raw_data,
            "extracted_signals": self._extract_signals(raw_data),
            "confidence_factors": {
                "data_freshness": "high",
                "source_authority": "high",
            },
        }

    def _extract_signals(self, data: dict) -> list[dict]:
        """Extract investment-relevant signals from raw data."""
        signals = []
        # ... extraer señales específicas ...
        return signals

    # ═══════════════════════════════════════════════════════════════
    # MÉTODO 3: Fact Fetching (Opcional - para refresh incremental)
    # ═══════════════════════════════════════════════════════════════
    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch facts for multiple companies."""
        facts = []

        for company_id in company_ids:
            data = self._fetch_from_api(company_id, None)
            if data:
                facts.append({
                    "company_id": company_id,
                    "fact_type": f"{self.source_name}_data",
                    "value": data,
                    "confidence": self.confidence,
                    "extracted_at": datetime.now(),
                    "source": self.source_name,
                })

        return facts

    # ═══════════════════════════════════════════════════════════════
    # PROPIEDADES REQUERIDAS
    # ═══════════════════════════════════════════════════════════════
    def get_confidence(self) -> float:
        return {0.0-1.0}  # Mismo valor que en __init__

    def get_authority(self) -> SourceAuthority:
        return SourceAuthority.{XXX}  # Ver opciones abajo

    def supports_incremental(self) -> bool:
        return True  # o False si no soporta fetch incremental

    def supports_discovery(self) -> bool:
        return True  # o False si no tiene capacidad de discovery

    def _empty_source(self, company_id: str) -> RawDataSource:
        """Return empty source when enrichment fails."""
        return RawDataSource(
            source_name=self.source_name,
            source_type=self.source_type,
            company_id=company_id,
            fetch_timestamp=datetime.now(),
            data={},
            metadata={"error": "Enrichment failed or no API key"},
        )
```

---

## Paso 2: Registrar el Adapter

**Archivo**: `src/solstein/adapters/registry.py`

Agregá el import y el registro condicional:

```python
def build_default_registry(settings: Settings) -> SourceRegistry:
    registry = SourceRegistry()

    # ... adapters existentes ...

    # ═══════════════════════════════════════════════════════════════
    # TU NUEVO ADAPTER
    # ═══════════════════════════════════════════════════════════════
    if settings.{NOMBRE}_API_KEY:  # Ver docs/API_PROVIDERS_GUIDE.md para env vars
        from solstein.adapters.enrichment.{nombre}_unified import {Nombre}UnifiedAdapter

        registry.register_unified(
            {Nombre}UnifiedAdapter(
                api_key=settings.{NOMBRE}_API_KEY
            )
        )

    return registry
```

---

## Paso 3: Agregar Configuración

**Archivo**: `src/solstein/config/settings.py` (o donde esté Settings)

Agregá el campo para el API key:

```python
class Settings(BaseSettings):
    # ... configuraciones existentes ...

    # ═══════════════════════════════════════════════════════════════
    # OSINT APIs
    # ═══════════════════════════════════════════════════════════════
    {NOMBRE}_API_KEY: str | None = None  # API key para {servicio}
```

---

## SourceAuthority Values (para get_authority())

Elegí el que corresponda según la fuente:

```python
class SourceAuthority(Enum):
    SEC_EDGAR = auto()      # Datos gubernamentales oficiales (US)
    COMPANIES_HOUSE = auto()  # Datos gubernamentales (UK)
    YAHOO_FINANCE = auto()   # Datos de mercado
    NEWS_API = auto()        # Noticias/sentiment
    GITHUB = auto()          # Repositorios/código
    WEBSITE = auto()         # Scraping de website
    PATENT = auto()          # Patentes
    FUNDING = auto()         # Datos de funding
    CRUNCHBASE = auto()      # Crunchbase específicamente
    LINKEDIN = auto()        # Datos de LinkedIn/empleados
    INFRASTRUCTURE = auto()  # Shodan, SecurityTrails, etc.
    SECURITY = auto()        # Breach data, security posture
    LEGAL = auto()           # Court records, litigation
    OSINT = auto()           # Fuentes OSINT genéricas
```

---

## Best Practices

### 1. Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_minute: int):
    """Decorator para rate limiting simple."""
    min_interval = 60.0 / calls_per_minute
    last_call_time = {}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Esperar si es necesario
            if func.__name__ in last_call_time:
                elapsed = time.time() - last_call_time[func.__name__]
                if elapsed < min_interval:
                    time.sleep(min_interval - elapsed)

            result = func(*args, **kwargs)
            last_call_time[func.__name__] = time.time()
            return result
        return wrapper
    return decorator

# Uso:
@rate_limit(calls_per_minute=60)
def _fetch_from_api(self, ...):
    ...
```

### 2. Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
)
def _fetch_from_api(self, ...):
    ...
```

### 3. Caching (Opcional pero recomendado)

```python
from functools import lru_cache

# Cache resultados por 1 hora
@lru_cache(maxsize=128)
def _fetch_from_api_cached(self, company_name: str) -> dict:
    ...
```

### 4. Error Handling Específico

```python
def _fetch_from_api(self, company_name: str, website: str | None) -> dict:
    try:
        response = requests.get(...)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        if response.status_code == 429:
            logger.warning(f"Rate limit hit for {self.source_name}")
            raise  # Reintentar via tenacity
        elif response.status_code == 401:
            logger.error(f"Invalid API key for {self.source_name}")
            return {}  # No reintentar
        else:
            logger.error(f"HTTP error {response.status_code}: {e}")
            return {}

    except requests.exceptions.Timeout:
        logger.warning(f"Timeout calling {self.source_name}")
        raise  # Reintentar

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {}
```

---

## Ejemplo Real: Proxycurl (LinkedIn)

Acá tenés un ejemplo concreto basado en el OSINT guide:

```python
"""Proxycurl adapter for LinkedIn-derived people intelligence."""

from datetime import datetime
from typing import Any

import requests
from loguru import logger

from solstein.domain.models import RawDataSource
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.refresh import BaseRefreshConnector


class ProxycurlUnifiedAdapter(BaseRefreshConnector):
    """Proxycurl adapter for LinkedIn employee and hiring data.

    Confidence: 0.75 (LinkedIn data quality)
    Authority: LINKEDIN
    Cost: ~$0.01-0.05 per lookup
    """

    def __init__(self, db_manager=None, api_key: str | None = None):
        super().__init__(
            source_name="proxycurl_unified",
            source_type="people",
            db_manager=db_manager,
            confidence=0.75,
        )
        self.api_key = api_key
        self.base_url = "https://nubela.co/proxycurl/api"

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        """Enrich with LinkedIn data via Proxycurl."""
        if not self.api_key:
            return self._empty_source(company_id)

        try:
            # Buscar LinkedIn URL de la empresa
            linkedin_url = self._find_linkedin_company(company_name, website)
            if not linkedin_url:
                return self._empty_source(company_id)

            # Obtener perfil de empresa
            company_profile = self._get_company_profile(linkedin_url)

            # Extraer signals
            data = {
                "linkedin_url": linkedin_url,
                "employee_count": company_profile.get('staff_count'),
                "employee_range": company_profile.get('staff_count_range'),
                "follower_count": company_profile.get('follower_count'),
                "founded_year": company_profile.get('founded_year'),
                "specialties": company_profile.get('specialties', []),
                "hiring_velocity": self._calculate_hiring_velocity(company_profile),
                "ai_talent_percentage": self._estimate_ai_talent(company_profile),
            }

            return RawDataSource(
                source_name=self.source_name,
                source_type=self.source_type,
                company_id=company_id,
                fetch_timestamp=datetime.now(),
                data=data,
                metadata={"linkedin_url": linkedin_url},
            )

        except Exception as e:
            logger.error(f"Proxycurl failed: {e}")
            return self._empty_source(company_id)

    def _find_linkedin_company(self, name: str, website: str | None) -> str | None:
        """Find company LinkedIn URL."""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        # Usar website si está disponible
        if website:
            domain = website.replace('https://', '').replace('http://', '').split('/')[0]
            params = {"domain": domain}
        else:
            params = {"name": name}

        response = requests.get(
            f"{self.base_url}/linkedin/company/resolve",
            headers=headers,
            params=params,
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            return data.get('url')
        return None

    def _get_company_profile(self, linkedin_url: str) -> dict:
        """Get full company profile from Proxycurl."""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.get(
            f"{self.base_url}/linkedin/company",
            headers=headers,
            params={"url": linkedin_url, "use_cache": "if-present"},
            timeout=10,
        )

        response.raise_for_status()
        return response.json()

    def _calculate_hiring_velocity(self, profile: dict) -> str:
        """Calculate hiring trend from employee count history."""
        # Lógica simplificada - ajustar según datos reales
        staff_count = profile.get('staff_count', 0)

        if staff_count == 0:
            return "unknown"
        elif staff_count < 50:
            return "early_stage"
        elif staff_count < 200:
            return "growth"
        else:
            return "established"

    def _estimate_ai_talent_percentage(self, profile: dict) -> float | None:
        """Estimate AI talent % from specialties and company description."""
        specialties = ' '.join(profile.get('specialties', [])).lower()
        description = profile.get('description', '').lower()

        ai_keywords = ['artificial intelligence', 'machine learning', 'ai/ml',
                       'deep learning', 'neural networks', 'nlp', 'computer vision']

        matches = sum(1 for kw in ai_keywords if kw in specialties or kw in description)

        # Estimación conservadora
        if matches >= 3:
            return 0.15  # ~15% AI talent
        elif matches >= 1:
            return 0.05  # ~5% AI talent
        return 0.0

    def get_authority(self) -> SourceAuthority:
        return SourceAuthority.LINKEDIN

    def supports_incremental(self) -> bool:
        return True

    def supports_discovery(self) -> bool:
        return False  # Proxycurl no tiene búsqueda de discovery
```

---

## Checklist para Cada API

Cuando implementes un nuevo adapter:

- [ ] Crear archivo en `adapters/enrichment/{nombre}_unified.py`
- [ ] Extender `BaseRefreshConnector`
- [ ] Implementar `enrich()` (REQUERIDO)
- [ ] Implementar `discover()` (opcional)
- [ ] Implementar `fetch_facts()` (opcional)
- [ ] Definir `get_confidence()` y `get_authority()`
- [ ] Implementar error handling robusto
- [ ] Agregar rate limiting
- [ ] Registrar en `registry.py`
- [ ] Agregar env var a Settings
- [ ] Documentar en `API_PROVIDERS_GUIDE.md`
- [ ] Testear con una company real

---

## Referencias

1. **API Providers Guide**: `docs/API_PROVIDERS_GUIDE.md` - Cómo obtener cada API key
2. **OSINT Guide**: `docs/OSINT_IMPLEMENTATION_GUIDE.md` - Qué APIs implementar y por qué
3. **Ejemplo existente**: `src/solstein/adapters/enrichment/news_unified.py`
4. **Registry**: `src/solstein/adapters/registry.py` - Cómo registrar adapters
5. **Protocols**: `src/solstein/adapters/protocols.py` - Interfaces

---

## Prioridades Sugeridas

Basado en el OSINT research, implementá en este orden:

1. **Proxycurl** (LinkedIn data) - Mayor impacto, hiring signals
2. **BuiltWith** (Tech stack) - Mejora technical DD
3. **HaveIBeenPwned** (Breach data) - Gratis, security risk
4. **OpenCorporates** (Global registry) - Cobertura geográfica
5. **SecurityTrails** (DNS/infrastructure) - Technical signals
6. **Shodan** (Infrastructure) - Advanced technical DD

---

¿Dudas? Pegame un grito. Cuando tengas el spreadsheet filtrado lo revisamos y definimos cuáles implementar primero.

**Key takeaway**: Un adapter = una clase que extiende `BaseRefreshConnector` + registro en `registry.py`. El resto del sistema ya sabe cómo usarlo.
