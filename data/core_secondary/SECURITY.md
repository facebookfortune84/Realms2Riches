# Security Policy

## Introduction
This document outlines the security policies and practices for the Realms2Riches project. Adherence to these guidelines is mandatory for all contributors to ensure the integrity, confidentiality, and availability of the system and its data.

## Sensitive Data Handling

-   **Secrets Management:**
    *   **NEVER** commit API keys, database credentials, encryption keys, or any other sensitive information directly to the Git repository.
    *   Utilize `.env.prod` for production secrets and `.env.local` for local development secrets.
    *   Environment variables should be loaded securely via the configuration system (e.g., Pydantic `BaseSettings`).
    *   Production secrets must be managed through secure secrets management solutions (e.g., environment variables in deployment platforms like Vercel, Docker secrets, or dedicated secret managers).
-   **Data Encryption:** Sensitive data at rest (e.g., passwords, API keys) should be encrypted using robust algorithms. Ensure encryption keys are managed securely and are not hardcoded.
-   **Data Transmission:** All communication, especially involving sensitive data (API calls, webhook payloads), must use HTTPS.

## Code Security Practices

-   **Dependency Auditing:**
    *   Regularly scan project dependencies for known vulnerabilities using tools like `safety check` (if integrated with Poetry) or `npm audit`.
    *   Keep dependencies updated to patch security vulnerabilities.
-   **Input Validation:**
    *   Rigorously validate all external input (API requests, webhook payloads, user-generated content) to prevent injection attacks (e.g., SQL injection, XSS). Utilize Pydantic models for FastAPI data validation.
-   **Authentication & Authorization:**
    *   Implement robust authentication mechanisms for API endpoints and user interfaces.
    *   Use proper authorization checks to ensure users can only access resources and perform actions they are permitted to.
-   **Webhook Security:**
    *   **Signature Verification:** ALWAYS verify webhook signatures (e.g., Stripe's `stripe.Webhook.construct_event`) to ensure requests originate from the trusted source and have not been tampered with. Use the `STRIPE_WEBHOOK_SECRET`.
    *   **Idempotency:** Design webhook handlers to be idempotent, preventing unintended side effects from duplicate event deliveries.
-   **Secure Coding Practices:**
    *   Follow OWASP guidelines for secure software development.
    *   Avoid common vulnerabilities like insecure direct object references, security misconfigurations, and cross-site scripting (XSS).
-   **Error Handling:** Avoid exposing sensitive information in error messages. Log detailed errors internally but provide generic messages externally.

## Agent Security Considerations

-   **Tool Execution Sandboxing:** When agents execute external commands or code, ensure they run in a secure, isolated environment (e.g., Docker containers with minimal privileges).
-   **Data Access Control:** Agents should operate with the least privilege necessary. Limit their access to sensitive data or system resources.
-   **Prompt Injection:** Be mindful of potential prompt injection attacks when agents process user-provided input or external data for LLM prompts. Sanitize inputs and use LLM provider safeguards where available.

## Incident Response

-   **Reporting:** Any security vulnerabilities discovered should be reported responsibly according to the process outlined in `CONTRIBUTING.md`.
-   **Patching:** Critical vulnerabilities in dependencies or core components must be addressed promptly.

## Testing

-   **Security Testing:** Incorporate security testing into the CI pipeline (e.g., dependency scanning, static analysis security testing - SAST).
-   **Penetration Testing:** Conduct periodic penetration tests on production environments.

---
*Security Policy Version: 1.0 | Last Updated: March 10, 2026*
*Authored by: Realms2Riches AI Core*