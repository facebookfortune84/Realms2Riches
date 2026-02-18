# Onboarding a New Project

1.  **Create a Project Spec**:
    *   Create a JSON file in `projects/slots/<project-id>/spec.json`.
    *   Example:
        ```json
        {
          "name": "My Web App",
          "type": "web_app",
          "description": "A simple Flask app."
        }
        ```

2.  **Submit to Orchestrator**:
    *   Run:
        ```bash
        python -m orchestrator.src.core.orchestrator --submit projects/slots/<project-id>/spec.json
        ```

3.  **Monitor Progress**:
    *   Check logs: `docker-compose logs -f orchestrator`
    *   Check DB: `sqlite3 orchestrator.db "SELECT * FROM runs;"`
