namespace SolStein.Domain.Enums;

/// <summary>
/// Confidence levels for data points.
/// </summary>
public enum ConfidenceLevel
{
    Unknown,
    Estimated,
    Confirmed
}

/// <summary>
/// AI adoption maturity levels.
/// </summary>
public enum AIMaturity
{
    None,
    Low,
    Moderate,
    Strong,
    VeryStrong
}

/// <summary>
/// Competitive threat levels.
/// </summary>
public enum ThreatLevel
{
    Low,
    Medium,
    High,
    Critical
}

/// <summary>
/// Company size/market position tiers.
/// </summary>
public enum CompanyTier
{
    Tier4,  // Emerging/startups
    Tier3,  // Niche players
    Tier2,  // Strong competitors
    Tier1   // Market leaders
}
