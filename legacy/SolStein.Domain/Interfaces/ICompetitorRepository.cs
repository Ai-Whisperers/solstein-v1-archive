namespace SolStein.Domain.Interfaces;

using SolStein.Domain.Entities;

public interface ICompetitorRepository
{
    Task<Competitor?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default);
    Task<Competitor?> GetByNameAsync(string name, CancellationToken cancellationToken = default);
    Task<IEnumerable<Competitor>> GetAllAsync(CancellationToken cancellationToken = default);
    Task<IEnumerable<Competitor>> GetByTierAsync(Enums.CompanyTier tier, CancellationToken cancellationToken = default);
    Task<IEnumerable<Competitor>> GetByThreatLevelAsync(Enums.ThreatLevel threatLevel, CancellationToken cancellationToken = default);
    Task<IEnumerable<Competitor>> SearchAsync(string searchTerm, CancellationToken cancellationToken = default);
    
    Task AddAsync(Competitor competitor, CancellationToken cancellationToken = default);
    Task UpdateAsync(Competitor competitor, CancellationToken cancellationToken = default);
    Task DeleteAsync(Guid id, CancellationToken cancellationToken = default);
    
    Task<bool> ExistsAsync(Guid id, CancellationToken cancellationToken = default);
    Task<bool> ExistsByNameAsync(string name, CancellationToken cancellationToken = default);
    
    Task<int> CountAsync(CancellationToken cancellationToken = default);
}
