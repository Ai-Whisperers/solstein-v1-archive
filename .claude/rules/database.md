# Database Rules

## Database Design Principles
- **Normalization**: Follow normalization rules (1NF, 2NF, 3NF) to reduce redundancy.
- **Naming Conventions**: Use consistent naming for tables, columns, and constraints.
- **Data Types**: Choose appropriate data types for storage efficiency and integrity.
- **Indexes**: Create indexes on frequently queried columns and foreign keys.
- **Constraints**: Use constraints (PK, FK, UNIQUE, CHECK) to enforce data integrity.

## PostgreSQL Specific Guidelines
- **Extensions**: Use PostgreSQL extensions when appropriate (PostGIS, UUID, etc.).
- **JSONB**: Use JSONB for semi-structured data with indexing capabilities.
- **Array Types**: Use array types for one-to-many relationships when appropriate.
- **Window Functions**: Leverage window functions for complex aggregations.
- **Partitioning**: Implement table partitioning for large datasets.

## Migration Management
- **Migration Files**: Use version-controlled migration files (Alembic, Flyway, etc.).
- **Rollback Capability**: Ensure migrations can be rolled back safely.
- **Data Migration**: Handle data migration scripts separately from schema changes.
- **Testing**: Test migrations in staging before applying to production.
- **Documentation**: Document migration purpose and impact.

## Performance Optimization
- **Query Analysis**: Use EXPLAIN ANALYZE to optimize slow queries.
- **Index Strategy**: Create composite indexes for multi-column queries.
- **Connection Pooling**: Use connection pooling for database connections.
- **Caching**: Implement query result caching for frequently accessed data.
- **Read Replicas**: Use read replicas for read-heavy workloads.

## Security Practices
- **Least Privilege**: Grant database users only necessary permissions.
- **Encryption**: Use encryption for sensitive data at rest and in transit.
- **Auditing**: Implement audit logging for critical operations.
- **Backup Strategy**: Maintain regular backups with point-in-time recovery.
- **Access Control**: Use database-level access control and row-level security.

## Data Integrity
- **Foreign Keys**: Use foreign keys to maintain referential integrity.
- **Unique Constraints**: Enforce uniqueness where required.
- **Check Constraints**: Use check constraints for business rule validation.
- **Triggers**: Use triggers sparingly for complex business logic.
- **Transactions**: Use transactions for atomic operations.

## Development Workflow
- **Schema Design**: Design schemas with future growth in mind.
- **Code Reviews**: Review database changes with the same rigor as code.
- **Performance Testing**: Test database performance under realistic loads.
- **Monitoring**: Monitor database metrics (connections, queries, locks).
- **Documentation**: Document database schema and relationships.

## Anti-Patterns to Avoid
- **N+1 Queries**: Avoid N+1 query problems with proper joins or eager loading.
- **Select ***: Don't use SELECT *; specify required columns explicitly.
- **Missing Indexes**: Don't forget to create indexes on frequently queried columns.
- **Long Transactions**: Avoid long-running transactions that block other operations.
- **Database Logic in Application**: Keep business logic in the application layer.

## NoSQL Considerations
- **Document Databases**: Use for flexible schemas and hierarchical data.
- **Key-Value Stores**: Use for simple lookups and caching.
- **Graph Databases**: Use for complex relationship queries.
- **Time Series**: Use specialized time series databases for time-based data.
- **Search Engines**: Use dedicated search engines for full-text search.

## Backup and Recovery
- **Automated Backups**: Schedule regular automated backups.
- **Backup Testing**: Regularly test backup restoration procedures.
- **Retention Policy**: Implement appropriate backup retention policies.
- **Offsite Storage**: Store backups in geographically separate locations.
- **Point-in-Time Recovery**: Enable point-in-time recovery capabilities.