# API Design Rules

## REST API Design Principles
- **Resource-Oriented**: Design APIs around resources, not actions.
- **Consistent Naming**: Use nouns for endpoints, plural for collections.
- **HTTP Methods**: Use appropriate HTTP methods (GET, POST, PUT, DELETE, PATCH).
- **Status Codes**: Return meaningful HTTP status codes (200, 201, 400, 404, 500).
- **Versioning**: Include API versioning in the URL or headers.

## Request/Response Patterns
- **Request Format**: Use JSON for request bodies, query parameters for filtering.
- **Response Format**: Consistent JSON structure with `data`, `meta`, and `errors` fields.
- **Pagination**: Implement cursor-based or offset-based pagination for collections.
- **Filtering/Sorting**: Support filtering and sorting through query parameters.
- **Error Handling**: Return structured error responses with error codes and messages.

## Security Considerations
- **Authentication**: Implement token-based authentication (JWT, OAuth2).
- **Authorization**: Use role-based access control (RBAC) for resource access.
- **Rate Limiting**: Implement rate limiting to prevent abuse.
- **Input Validation**: Validate all input data to prevent injection attacks.
- **CORS**: Configure CORS properly for cross-origin requests.

## Performance Guidelines
- **Caching**: Implement caching for static resources and frequent queries.
- **Compression**: Use GZIP compression for response payloads.
- **Lazy Loading**: Load related resources on demand, not eagerly.
- **Batch Operations**: Support batch operations for efficiency.
- **Monitoring**: Include metrics for API performance and usage.

## Documentation Standards
- **API Documentation**: Provide comprehensive API documentation (OpenAPI/Swagger).
- **Example Requests**: Include example requests and responses.
- **Error Documentation**: Document all possible error responses.
- **Changelog**: Maintain a changelog for API updates and breaking changes.
- **SDK Generation**: Consider generating client SDKs from API specifications.

## Development Workflow
- **API First**: Design APIs before implementing backend services.
- **Contract Testing**: Use contract testing to verify API contracts.
- **Backward Compatibility**: Maintain backward compatibility for existing clients.
- **Deprecation Policy**: Have a clear deprecation policy for old endpoints.
- **Monitoring**: Monitor API usage, errors, and performance in production.

## Anti-Patterns to Avoid
- **Action-Based URLs**: Avoid URLs like `/api/users/create` instead of POST `/api/users`.
- **Inconsistent Responses**: Don't mix response formats across endpoints.
- **Missing Validation**: Never trust client input without validation.
- **Over-Pagination**: Don't paginate everything; use infinite scrolling for large datasets.
- **Leaky Abstraction**: Hide internal implementation details from API consumers.

## GraphQL Specific Rules
- **Schema Design**: Design clear, intuitive GraphQL schemas.
- **Resolvers**: Implement efficient resolvers with proper error handling.
- **Batching**: Use DataLoader for batching and caching database queries.
- **Subscriptions**: Implement real-time updates with GraphQL subscriptions.
- **Security**: Apply field-level security and input validation.