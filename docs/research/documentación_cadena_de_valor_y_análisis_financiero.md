# Documentación: Cadena de Valor y Análisis Financiero

> **Guía completa del sistema de análisis competitivo de Solstein**

---

## Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Cadena de Valor (Value Chain Analysis)](#cadena-de-valor)
3. [Análisis Financiero](#análisis-financiero)
4. [Sistema de Scoring](#sistema-de-scoring)
5. [Implementación Técnica](#implementación-técnica)
6. [Referencias](#referencias)

---

## Resumen Ejecutivo

Solstein implementa un sistema de análisis competitivo que combina el **modelo de cadena de valor de Porter** con un **sistema de scoring financiero multidimensional**. Esta dualidad permite evaluar empresas tanto desde la perspectiva operativa (actividades primarias y de apoyo) como desde la salud financiera y posición competitiva.

### Las Tres Dimensiones de Análisis

| Dimensión | Descripción | Rango |
|-----------|-------------|-------|
| **Growth Score** | Trajectoria de crecimiento de ingresos | 0-10 |
| **Financial Health** | Estabilidad financiera y capital | 0-10 |
| **Competitive Position** | Posición de mercado y madurez tecnológica | 0-10 |

---

## Cadena de Valor

### Marco Teórico: Porter's Value Chain

La cadena de valor de Michael Porter identifica las actividades que generan valor en una organización:

```
┌─────────────────────────────────────────────────────────────┐
│                    ACTIVIDADES DE APOYO                     │
├─────────────────────────────────────────────────────────────┤
│  • Infraestructura de la firma                              │
│  • Gestión de recursos humanos                              │
│  • Desarrollo tecnológico                                   │
│  • Adquisiciones                                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   ACTIVIDADES PRIMARIAS                     │
├─────────────────────────────────────────────────────────────┤
│  Logística     Operaciones    Logística    Marketing    │
│  Entrante      →              Saliente     → y Ventas   │
│                              Servicio      →             │
└─────────────────────────────────────────────────────────────┘
```

### Mapeo en Solstein

Solstein adapta este modelo para empresas de software:

#### Actividades Primarias

| Actividad | Métricas en Solstein | Fuentes de Datos |
|-----------|---------------------|------------------|
| **Logística Entrante** | Costo de adquisición de clientes (CAC), calidad de datos | Crunchbase, SEC EDGAR |
| **Operaciones** | Eficiencia operativa (revenue/employee), margen de beneficio | Financials, Companies House |
| **Logística Saliente** | Canales de distribución, presencia geográfica | LinkedIn, sitios web |
| **Marketing y Ventas** | Crecimiento de ingresos, market penetration | News, SEC filings |
| **Servicio** | Soporte al cliente, retención (implied) | GitHub issues, reviews |

#### Actividades de Apoyo

| Actividad | Métricas en Solstein | Fuentes de Datos |
|-----------|---------------------|------------------|
| **Infraestructura** | Tamaño de empresa, funding raised | Crunchbase, PitchBook |
| **RRHH** | Número de empleados, crecimiento de headcount | LinkedIn, SEC filings |
| **Tecnología** | AI maturity, SaaS maturity, tech stack | GitHub, API analysis |
| **Adquisiciones** | Partnerships, integrations ecosystem | News, API docs |

### Presencia Geográfica (Geographic Footprint)

El sistema evalúa la extensión de la cadena de valor:

```python
# Configuración de umbrales
geo_global_count = 5      # >5 regiones = presencia global
geo_regional_count = 2    # >2 regiones = presencia regional

# Puntuación
if regiones > 5:    bonus = +0.5   # Global presence
elif regiones > 2:  bonus = +0.3   # Regional presence
```

### Diversidad Tecnológica (Stack Diversity)

```python
# Stack diversity indica madurez tecnológica
tech_diverse_count = 8

if tecnologías > 8:
    bonus = +0.3   # Diversas capacidades técnicas
```

---

## Análisis Financiero

### Métricas Financieras Core

Solstein analiza las siguientes métricas financieras:

#### 1. Escala de Ingresos (Revenue Scale)

| Umbral | Descripción | Ajuste al Score |
|--------|-------------|-----------------|
| < €1M | Startup/revenue temprana | -1.0 |
| €1M - €10M | Early growth | 0.0 (neutral) |
| €10M - €100M | Scale-up | +1.0 |
| > €100M | Enterprise | +2.0 |

#### 2. Rentabilidad (Profitability)

```python
# Métricas de rentabilidad
profit_margin: float  # Margen de beneficio (%)

# Umbrales
margin_high_threshold = 30    # >30% = +1.5
margin_med_threshold = 15     # >15% = +0.5
margin_negative_penalty = -1.5  # <0% = -1.5
```

#### 3. Eficiencia Operativa

Calculada como ingresos por empleado:

```python
# Fórmula
revenue_per_employee = (revenue_millions × 1,000,000) / employees

# Umbrales (en EUR)
efficiency_exceptional = 1_000_000  # €1M+ = +1.0
efficiency_good = 500_000           # €500K+ = +0.5
efficiency_low = 100_000            # <€100K = -0.5
```

#### 4. Colchón de Capital (Funding Cushion)

Ratio de capitalización vs. ingresos:

```python
# Fórmula
cushion_ratio = funding_raised / revenue

# Interpretación
ratio > 10.0   # Bien capitalizada (+2.5)
ratio 3.0-10.0 # Capitalización adecuada (+1.0)
ratio < 3.0    # Capitalización limitada (-1.0)
```

### Integración de Facts (Fact Repository)

Solstein integra datos verificados de múltiples fuentes:

```python
# Mapeo de facts a métricas financieras
fact_map = {
    "annual_revenue": ("revenue", "revenue_confidence"),
    "revenue_growth_yoy": ("growth_rate", "growth_confidence"),
    "employee_count": ("employees", "employees_confidence"),
    "gross_margin": ("profit_margin", "margin_confidence"),
    "total_funding_raised": ("funding_raised", "funding_confidence"),
    "company_valuation": ("valuation", "valuation_confidence"),
}
```

### Niveles de Confianza

| Nivel | Confianza | Descripción |
|-------|-----------|-------------|
| **CONFIRMED** | ≥ 90% | Datos auditados o fuente primaria |
| **ESTIMATED** | 70-90% | Estimaciones de fuentes confiables |
| **UNKNOWN** | < 70% | Datos faltantes o poco confiables |

---

## Sistema de Scoring

### Financial Health Scorer

Ubicación: `src/solstein/analytics/scorers/financial_health.py`

```python
class FinancialHealthScorer:
    """Calcula el score de salud financiera (0-10)."""

    def score(
        self,
        financials: FinancialMetric,
        fact_repo: FactRepository | None = None,
        company_id: str | None = None,
    ) -> tuple[float, ScoringExplanation]:
        """
        Calcula el score con explicación detallada.

        Args:
            financials: Métricas financieras tradicionales
            fact_repo: Repositorio de facts verificados (opcional)
            company_id: ID de empresa para buscar facts

        Returns:
            (score_final, explicación_detallada)
        """
```

### Componentes del Financial Health Score

| Componente | Peso | Descripción |
|------------|------|-------------|
| Revenue Scale | Variable | Escala de operaciones |
| Profitability Health | Variable | Salud de márgenes |
| Operating Efficiency | Variable | Ingresos por empleado |
| Funding Cushion | Variable | Reservas de capital |

### Competitive Position Scorer

Ubicación: `src/solstein/analytics/scorers/competitive_position.py`

```python
class CompetitivePositionScorer:
    """Calcula el score de posición competitiva (0-10)."""

    def score(self, profile: Company) -> tuple[float, ScoringExplanation]:
        """Evalúa:
        - Market Tier (posición de mercado)
        - AI Maturity (madurez en IA)
        - SaaS Maturity (madurez SaaS)
        - Geographic Footprint (alcance geográfico)
        - Stack Diversity (diversidad tecnológica)
        """
```

### Growth Momentum Scorer

El tercer pilar del sistema de scoring:

| Factor | Descripción |
|--------|-------------|
| YoY Revenue Growth | Crecimiento año sobre año |
| Revenue Acceleration | Aceleración/desaceleración |
| Market Expansion | Señales de expansión de mercado |

---

## Implementación Técnica

### Estructura de Archivos

```
src/solstein/analytics/
├── scorers/
│   ├── financial_health.py      # Salud financiera
│   ├── competitive_position.py  # Posición competitiva
│   └── growth_momentum.py       # Momentum de crecimiento
├── scoring.py                   # Coordinador principal
├── activities.py                # Actividades de análisis
└── signals/                     # Modelos de señales
    └── models.py
```

### Configuración de Scoring

Ubicación: `src/solstein/core/scoring_config.py`

```python
class ScoringSettings:
    """Configuración centralizada de umbrales y pesos."""

    # Umbrales de revenue (en millones EUR)
    revenue_large_threshold = 100.0    # €100M
    revenue_med_threshold = 10.0       # €10M
    revenue_small_threshold = 1.0      # €1M

    # Bonos/penalizaciones
    revenue_large_bonus = 2.0
    revenue_med_bonus = 1.0
    revenue_small_penalty = -1.0

    # Umbrales de eficiencia
    efficiency_exceptional_threshold = 1_000_000  # €1M/empleado
    efficiency_good_threshold = 500_000           # €500K/empleado
    efficiency_low_threshold = 100_000            # €100K/empleado
```

### Unidades y Estándares

| Métrica | Unidad | Ejemplo |
|---------|--------|---------|
| Revenue | Millones EUR | `5.0` = €5M |
| Funding | Millones EUR | `2.0` = €2M |
| Valuation | Millones EUR | `50.0` = €50M |
| Employees | Count | `150` = 150 empleados |
| Margins | Porcentaje | `25.5` = 25.5% |

### Flujo de Datos

```
┌─────────────────────────────────────────────────────────────┐
│                    FUENTES DE DATOS                          │
├─────────────────────────────────────────────────────────────┤
│  SEC EDGAR │ Companies House │ Crunchbase │ LinkedIn │ GitHub│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   FACT REPOSITORY                            │
│              (Datos verificados + confianza)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                FINANCIAL METRIC MODEL                        │
│           (revenue, margin, employees, funding)              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   SCORING ENGINE                             │
│     ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│     │   Growth     │  │   Financial  │  │ Competitive  │   │
│     │   Scorer     │  │   Health     │  │   Position   │   │
│     └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              CLASSIFICATION SYSTEM                           │
│                                                              │
│     🔥 PHOENIX (≥7.0)    🧂 SALT (4-7)    ⚖️ LEAD (≤4)       │
└─────────────────────────────────────────────────────────────┘
```

---

## Ejemplos de Uso

### Ejemplo 1: Scoring de Empresa

```python
from solstein.analytics.scorers import FinancialHealthScorer
from solstein.domain.models import FinancialMetric

# Crear métricas financieras
financials = FinancialMetric(
    revenue=30.0,          # €30M
    growth_rate=22.0,      # 22% YoY
    employees=130,
    profit_margin=15.5,    # 15.5%
    funding_raised=45.0,   # €45M
)

# Calcular score
scorer = FinancialHealthScorer()
score, explanation = scorer.score(financials)

print(f"Financial Health Score: {score}/10")
print(f"Componentes: {explanation.components}")
```

### Ejemplo 2: Análisis Completo con Facts

```python
from solstein.infrastructure.repositories import FactRepository

# Conectar repositorio de facts
fact_repo = FactRepository()

# Scoring con verificación de datos
score, explanation = scorer.score(
    financials=financials,
    fact_repo=fact_repo,
    company_id="eneve-energy21"
)

# Los facts con mayor confianza sobrescriben los datos base
```

---

## Referencias

### Documentación Relacionada

| Documento | Descripción |
|-----------|-------------|
| [GLOSSARY.md](./reference/GLOSSARY.md) | Glosario de términos |
| [EPIC-001-FIX-FINANCIAL-SCORING.md](./epics/EPIC-001-FIX-FINANCIAL-SCORING.md) | Historia de corrección del sistema financiero |
| [API_DOCUMENTATION.md](./reference/API_DOCUMENTATION.md) | Documentación de API |
| [DATABASE_SCHEMA.md](./reference/DATABASE_SCHEMA.md) | Esquema de base de datos |

### Implementación de Referencia

- **Financial Health Scorer**: `src/solstein/analytics/scorers/financial_health.py`
- **Competitive Position Scorer**: `src/solstein/analytics/scorers/competitive_position.py`
- **Growth Scorer**: `src/solstein/analytics/scoring.py`
- **Configuración**: `src/solstein/core/scoring_config.py`

### Recursos Externos

- [Porter's Value Chain - Harvard Business Review](https://hbr.org/1985/11/how-competitive-forces-shape-strategy)
- [Competitive Advantage - Michael Porter (1985)](https://www.amazon.com/Competitive-Advantage-Creating-Sustaining-Performance/dp/0743260872)

---

## Changelog

| Fecha | Versión | Cambios |
|-------|---------|---------|
| 2026-03-05 | 1.0 | Documentación inicial creada |

---

*Documentación generada para Solstein Competitive Intelligence Platform*
*Basada en implementación actual del sistema de scoring v3.0*
