namespace SolStein.Domain.Entities;

using SolStein.Domain.Enums;
using SolStein.Domain.ValueObjects;

public class Competitor
{
    public Guid Id { get; private set; }
    public string Name { get; private set; } = string.Empty;
    public string Industry { get; private set; } = "Energy Software";
    public string? Description { get; private set; }
    public string? Website { get; private set; }
    public string? Headquarters { get; private set; }
    public int? FoundedYear { get; private set; }
    public CompanyTier Tier { get; private set; } = CompanyTier.Tier3;
    public ThreatLevel ThreatLevel { get; private set; } = ThreatLevel.Medium;
    public AIMaturity AIMaturity { get; private set; } = AIMaturity.None;
    public int SaaSMaturity { get; private set; } = 1;
    public List<string> TechStack { get; private set; } = new();
    public FinancialMetrics Financials { get; private set; } = new();
    public List<string> GeographicPresence { get; private set; } = new();
    public List<string> KeyCustomers { get; private set; } = new();
    public string? ParentCompany { get; private set; }
    public List<string> Subsidiaries { get; private set; } = new();
    public List<Acquisition> Acquisitions { get; private set; } = new();
    public DateTime CreatedAt { get; private set; }
    public DateTime LastUpdated { get; private set; }
    public string? DataSource { get; private set; }
    public string? Notes { get; private set; }
    public double? GrowthScore { get; private set; }
    public double? FinancialHealthScore { get; private set; }
    public double? CompetitivePositionScore { get; private set; }

    protected Competitor() { }

    public Competitor(string name, string? id = null)
    {
        Id = id is not null ? Guid.Parse(id) : Guid.NewGuid();
        Name = name ?? throw new ArgumentNullException(nameof(name));
        CreatedAt = DateTime.UtcNow;
        LastUpdated = DateTime.UtcNow;
    }

    public void UpdateBasicInfo(
        string? description = null,
        string? website = null,
        string? headquarters = null,
        int? foundedYear = null)
    {
        Description = description ?? Description;
        Website = website ?? Website;
        Headquarters = headquarters ?? Headquarters;
        FoundedYear = foundedYear ?? FoundedYear;
        LastUpdated = DateTime.UtcNow;
    }

    public void UpdateCompetitivePositioning(CompanyTier tier, ThreatLevel threatLevel)
    {
        Tier = tier;
        ThreatLevel = threatLevel;
        LastUpdated = DateTime.UtcNow;
    }

    public void UpdateTechnologyAssessment(AIMaturity aiMaturity, int saasMaturity, List<string>? techStack = null)
    {
        if (saasMaturity < 1 || saasMaturity > 10)
            throw new ArgumentOutOfRangeException(nameof(saasMaturity), "SaaS maturity must be between 1 and 10");
        
        AIMaturity = aiMaturity;
        SaaSMaturity = saasMaturity;
        if (techStack is not null)
            TechStack = techStack;
        LastUpdated = DateTime.UtcNow;
    }

    public void UpdateFinancials(FinancialMetrics financials)
    {
        Financials = financials ?? throw new ArgumentNullException(nameof(financials));
        LastUpdated = DateTime.UtcNow;
    }

    public void AddAcquisition(Acquisition acquisition)
    {
        if (acquisition is null)
            throw new ArgumentNullException(nameof(acquisition));
        
        Acquisitions.Add(acquisition);
        LastUpdated = DateTime.UtcNow;
    }

    public void AddGeographicPresence(string region)
    {
        if (!GeographicPresence.Contains(region))
            GeographicPresence.Add(region);
        LastUpdated = DateTime.UtcNow;
    }

    public void AddKeyCustomer(string customer)
    {
        if (!KeyCustomers.Contains(customer))
            KeyCustomers.Add(customer);
        LastUpdated = DateTime.UtcNow;
    }

    public void UpdateScores(double? growthScore, double? financialHealthScore, double? competitivePositionScore)
    {
        GrowthScore = growthScore;
        FinancialHealthScore = financialHealthScore;
        CompetitivePositionScore = competitivePositionScore;
        LastUpdated = DateTime.UtcNow;
    }

    // Domain logic properties
    public bool IsPublic => Financials.IsPublic;
    public bool IsHighGrowth => Financials.IsHighGrowth;
    public bool IsProfitable => Financials.IsProfitable;
    public bool HasAcquisitionHistory => Acquisitions.Any();
}
