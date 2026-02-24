export interface Company {
    id?: string;
    company_id?: string;
    name: string;
    tier?: string;
    classification?: string;
    growth_score?: number;
    financial_health_score?: number;
    competitive_position_score?: number;
    revenue?: number;
    growth_rate?: number;
    employees?: number | string;
    headquarters?: string;
    industry?: string;
    financials?: {
        revenue?: number;
        growth_rate?: number;
        employees?: number | string;
    };
    extracted_signals?: Array<{
        signal_name: string;
        signal_value: string;
        source_facts: string[];
        calculation_method: string;
    }>;
}

export interface AuditTrail {
    confidence_level?: string;
    extracted_signals?: Array<{
        signal_name: string;
        signal_value: string;
        source_facts: string[];
        calculation_method: string;
    }>;
}
