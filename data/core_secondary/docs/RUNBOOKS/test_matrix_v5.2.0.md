# Realms2Riches - Test Matrix v5.2.0

## 1. Unit & Logic Tests
- **Backend Units**: `pytest tests/unit`
- **Frontend Units**: (Currently integrated into E2E)
- **Configuration**: `pytest tests/matrix/test_config.py`

## 2. Integration Tests
- **System Integrity**: `pytest tests/comprehensive/test_system_integrity.py`
- **Pricing & Social**: `pytest tests/integration/test_pricing_pipeline.py`, `pytest tests/integration/test_social_monetization.py`
- **Voice Flow**: `pytest tests/integration/test_voice_flow.py`

## 3. Agent Intelligence Tests
- **Agent Capabilities**: `pytest tests/agents/test_agent_capabilities.py`
- **Agent Scenarios**: `pytest tests/agent_scenarios/test_self_healing_core.py`
- **Matrix Tests**: `pytest tests/matrix/test_agent.py`, `pytest tests/matrix/test_orchestrator.py`

## 4. E2E & Live Tests
- **Live Frontend**: `python tests/e2e/test_live_frontend.py`
- **Full System Flow**: `pytest tests/e2e/test_full_flow.py`
- **Launch Readiness**: `pytest tests/e2e/test_launch_readiness.py`

## 5. Execution Summary (Status)
| Test Category | Command | Status | Notes |
|---------------|---------|--------|-------|
| Agent Capabilities | `pytest tests/agents` | PENDING | Verifies reasoning & tool use. |
| Self-Healing | `pytest tests/agent_scenarios` | PENDING | Verifies core redundancy. |
| Live Frontend | `python tests/e2e/test_live_frontend.py` | PENDING | Verifies Vercel/ngrok link. |
| Unit Tests | `pytest tests/unit` | PENDING | Verifies basic logic. |
