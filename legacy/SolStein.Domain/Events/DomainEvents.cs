namespace SolStein.Domain.Events;

public abstract class DomainEvent
{
    public Guid Id { get; } = Guid.NewGuid();
    public DateTime OccurredAt { get; } = DateTime.UtcNow;
}

public class CompetitorCreated : DomainEvent
{
    public Guid CompetitorId { get; }
    public string Name { get; }

    public CompetitorCreated(Guid competitorId, string name)
    {
        CompetitorId = competitorId;
        Name = name;
    }
}

public class CompetitorUpdated : DomainEvent
{
    public Guid CompetitorId { get; }
    public string UpdateType { get; }

    public CompetitorUpdated(Guid competitorId, string updateType)
    {
        CompetitorId = competitorId;
        UpdateType = updateType;
    }
}

public class CompetitorFinancialsUpdated : DomainEvent
{
    public Guid CompetitorId { get; }
    public decimal? Revenue { get; }
    public decimal? GrowthRate { get; }

    public CompetitorFinancialsUpdated(Guid competitorId, decimal? revenue, decimal? growthRate)
    {
        CompetitorId = competitorId;
        Revenue = revenue;
        GrowthRate = growthRate;
    }
}

public class CompetitorScoresCalculated : DomainEvent
{
    public Guid CompetitorId { get; }
    public double? GrowthScore { get; }
    public double? FinancialHealthScore { get; }
    public double? CompetitivePositionScore { get; }

    public CompetitorScoresCalculated(
        Guid competitorId, 
        double? growthScore, 
        double? financialHealthScore, 
        double? competitivePositionScore)
    {
        CompetitorId = competitorId;
        GrowthScore = growthScore;
        FinancialHealthScore = financialHealthScore;
        CompetitivePositionScore = competitivePositionScore;
    }
}

public class AcquisitionRecorded : DomainEvent
{
    public Guid CompetitorId { get; }
    public string AcquiredCompanyName { get; }
    public DateTime? AcquisitionDate { get; }

    public AcquisitionRecorded(Guid competitorId, string acquiredCompanyName, DateTime? acquisitionDate)
    {
        CompetitorId = competitorId;
        AcquiredCompanyName = acquiredCompanyName;
        AcquisitionDate = acquisitionDate;
    }
}
