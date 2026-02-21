# Security Rules

## General Security Principles
- **Defense in Depth**: Implement multiple layers of security controls.
- **Least Privilege**: Grant minimum necessary permissions to users and services.
- **Defense in Depth**: Implement multiple layers of security controls.
- **Security by Design**: Consider security throughout the development lifecycle.
- **Continuous Monitoring**: Implement continuous security monitoring and assessment.

## Authentication and Authorization
- **Multi-Factor Authentication**: Require MFA for all user accounts.
- **Strong Password Policies**: Enforce strong password requirements and rotation.
- **OAuth2/OpenID Connect**: Use industry-standard authentication protocols.
- **Role-Based Access Control**: Implement RBAC with principle of least privilege.
- **Session Management**: Implement secure session management with timeouts.

## Data Protection
- **Encryption at Rest**: Encrypt sensitive data at rest using strong algorithms.
- **Encryption in Transit**: Use TLS 1.3+ for all data in transit.
- **Data Classification**: Classify data based on sensitivity and apply appropriate controls.
- **Data Minimization**: Collect and retain only necessary data.
- **Data Masking**: Implement data masking for non-production environments.

## Application Security
- **Input Validation**: Validate and sanitize all user inputs.
- **Output Encoding**: Encode output to prevent XSS attacks.
- **SQL Injection Prevention**: Use parameterized queries or ORMs.
- **CSRF Protection**: Implement CSRF tokens for state-changing operations.
- **Security Headers**: Implement security headers (CSP, HSTS, X-Frame-Options).

## Infrastructure Security
- **Network Segmentation**: Implement proper network segmentation and firewalls.
- **Patch Management**: Keep all systems and dependencies up to date.
- **Vulnerability Scanning**: Regularly scan for vulnerabilities in applications and infrastructure.
- **Intrusion Detection**: Implement intrusion detection and prevention systems.
- **Logging and Monitoring**: Maintain comprehensive security logging and monitoring.

## API Security
- **API Authentication**: Implement proper authentication for all API endpoints.
- **Rate Limiting**: Implement rate limiting to prevent abuse.
- **Input Validation**: Validate all API inputs to prevent injection attacks.
- **API Keys**: Use secure API key management and rotation.
- **CORS Configuration**: Configure CORS properly to prevent unauthorized access.

## Cloud Security
- **Identity and Access Management**: Implement proper IAM with least privilege.
- **Network Security**: Use VPCs, security groups, and network ACLs.
- **Data Protection**: Implement encryption and access controls for cloud data.
- **Compliance**: Ensure cloud deployments meet compliance requirements.
- **Shared Responsibility**: Understand and implement the shared responsibility model.

## Container Security
- **Image Security**: Use trusted base images and scan for vulnerabilities.
- **Runtime Security**: Implement runtime security policies and monitoring.
- **Network Policies**: Use network policies to control container communication.
- **Secrets Management**: Use secure secrets management for containers.
- **Resource Limits**: Set resource limits to prevent resource exhaustion.

## DevSecOps Practices
- **Shift Left Security**: Integrate security early in the development process.
- **Automated Security Testing**: Include security testing in CI/CD pipelines.
- **Security Code Reviews**: Conduct security-focused code reviews.
- **Security Training**: Provide regular security training for developers.
- **Security Metrics**: Track and measure security program effectiveness.

## Incident Response
- **Incident Response Plan**: Maintain a documented incident response plan.
- **Detection and Analysis**: Implement detection and analysis capabilities.
- **Containment and Eradication**: Have procedures for containment and eradication.
- **Recovery**: Implement recovery procedures to restore normal operations.
- **Post-Incident Review**: Conduct post-incident reviews to improve processes.

## Compliance and Governance
- **Regulatory Compliance**: Ensure compliance with relevant regulations (GDPR, HIPAA, etc.).
- **Security Policies**: Maintain and enforce security policies and standards.
- **Audit Trails**: Maintain comprehensive audit trails for security events.
- **Third-Party Risk**: Assess and manage third-party security risks.
- **Security Awareness**: Maintain security awareness across the organization.

## Anti-Patterns to Avoid
- **Security Through Obscurity**: Don't rely on security through obscurity.
- **Hardcoded Secrets**: Never hardcode secrets in code or configuration.
- **Missing Input Validation**: Always validate and sanitize user inputs.
- **Weak Authentication**: Don't implement weak or custom authentication mechanisms.
- **Ignoring Security Updates**: Always apply security patches promptly.

## Security Testing
- **Static Application Security Testing (SAST)**: Analyze source code for vulnerabilities.
- **Dynamic Application Security Testing (DAST)**: Test running applications for vulnerabilities.
- **Interactive Application Security Testing (IAST)**: Combine SAST and DAST approaches.
- **Penetration Testing**: Conduct regular penetration testing.
- **Dependency Scanning**: Scan dependencies for known vulnerabilities.

## Secure Development Lifecycle
- **Threat Modeling**: Conduct threat modeling for new features and systems.
- **Secure Coding Standards**: Establish and enforce secure coding standards.
- **Security Requirements**: Include security requirements in project specifications.
- **Security Testing**: Include security testing in quality assurance processes.
- **Security Metrics**: Track security metrics and KPIs.