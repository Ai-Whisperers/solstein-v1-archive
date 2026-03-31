# Field Data Flow Diagram

**Last Updated**: 2026-03-27
**Reflects**: Post-STORY-125/126/127 architecture

```mermaid
flowchart LR
    subgraph Ingestion["Ingestion Adapters"]
        SEC["SEC EDGAR"]
        CH["Companies House"]
        WEB["Web Research Pipeline"]
        CB["Crunchbase/LinkedIn"]
        MAN["Manual Entry / JSON"]
    end

    subgraph Domain["Domain Models"]
        CO["Company (76 fields)"]
        FM["FinancialMetric (15 fields)"]
        CO -->|financials| FM
    end

    subgraph Analytics["Analytics Engine"]
        SCORE["Scoring Engine"]
        SIGNAL["Signal Detection"]
        CLASS["Classification"]
    end

    subgraph Export["Export Engine"]
        ES["Executive Summary\n(11 columns)"]
        MR["Market Rankings\n(6 columns)"]
        FI["Financial Intelligence\n(12 columns)"]
        RH["Revenue History\n(4 columns)"]
        AD["Advanced Data\n(8 columns)"]
    end

    SEC --> FM
    CH --> FM
    WEB --> CO
    CB --> CO
    MAN --> CO

    SEC --> CO
    CH --> CO

    CO --> SCORE
    CO --> SIGNAL
    FM --> SCORE
    SCORE --> CLASS

    CO --> ES
    CO --> MR
    CO --> FI
    CO --> RH
    CO --> AD
    FM --> ES
    FM --> MR
    FM --> FI

    subgraph Validation["Schema Validation (STORY-126)"]
        SCHEMA["ExportSchema v1.0\n41 required fields"]
    end

    ES --> SCHEMA
    MR --> SCHEMA
    FI --> SCHEMA
    RH --> SCHEMA
    AD --> SCHEMA
```

## Layer Descriptions

**Ingestion Adapters** fetch raw company data from external sources. Each adapter writes to specific fields on Company or FinancialMetric.

**Domain Models** hold the canonical data. `Company` is the root entity (76 fields). `FinancialMetric` is the canonical source for revenue, profit_margin, employees, and growth metrics (STORY-127).

**Analytics Engine** reads from domain models to compute scores, detect signals, and classify companies. Outputs (ai_score, threat_level, tier, classification) are written back to Company.

**Export Engine** reads from Company and FinancialMetric to produce the Excel dashboard. After generation, the ExportSchema validation (STORY-126) verifies all 41 required field headers are present on their correct sheets.
