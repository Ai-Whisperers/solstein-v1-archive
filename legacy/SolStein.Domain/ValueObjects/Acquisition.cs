namespace SolStein.Domain.ValueObjects;

/// <summary>
/// M&A transaction record.
/// Immutable value object.
/// </summary>
public record Acquisition
{
    public string CompanyName { get; init; } = string.Empty;
    public DateTime? Date { get; init; }
    public decimal? Value { get; init; }
    public string? Notes { get; init; }
}
