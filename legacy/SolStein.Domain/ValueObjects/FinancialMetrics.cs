namespace SolStein.Domain.ValueObjects;

using SolStein.Domain.Enums;

/// <summary>
/// Financial metrics for a company.
/// Immutable value object.
/// </summary>
public record FinancialMetrics
{
    public decimal? Revenue { get; init; }
    public ConfidenceLevel RevenueConfidence { get; init; } = ConfidenceLevel.Unknown;
    
    public decimal? GrowthRate { get; init; }
    public ConfidenceLevel GrowthConfidence { get; init; } = ConfidenceLevel.Unknown;
    
    public int? Employees { get; init; }
    public ConfidenceLevel EmployeesConfidence { get; init; } = ConfidenceLevel.Unknown;
    
    public decimal? ProfitMargin { get; init; }
    public ConfidenceLevel MarginConfidence { get; init; } = ConfidenceLevel.Unknown;
    
    public decimal? FundingRaised { get; init; }
    public ConfidenceLevel FundingConfidence { get; init; } = ConfidenceLevel.Unknown;
    
    public decimal? Valuation { get; init; }
    public ConfidenceLevel ValuationConfidence { get; init; } = ConfidenceLevel.Unknown;

    /// <summary>
    /// Validates that at least one financial metric is provided.
    /// </summary>
    public bool HasAnyData => 
        Revenue.HasValue || 
        GrowthRate.HasValue || 
        Employees.HasValue || 
        ProfitMargin.HasValue || 
        FundingRaised.HasValue || 
        Valuation.HasValue;

    /// <summary>
    /// Checks if the company is publicly traded (valuation > 100M).
    /// </summary>
    public bool IsPublic => Valuation.HasValue && Valuation.Value > 100_000_000;

    /// <summary>
    /// Checks if the company is high growth (>20% annually).
    /// </summary>
    public bool IsHighGrowth => GrowthRate.HasValue && GrowthRate.Value > 20;

    /// <summary>
    /// Checks if the company is profitable.
    /// </summary>
    public bool IsProfitable => ProfitMargin.HasValue && ProfitMargin.Value > 0;
}
