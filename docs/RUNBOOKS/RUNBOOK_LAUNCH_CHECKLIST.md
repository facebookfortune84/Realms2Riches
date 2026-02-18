# Launch Checklist

This runbook is the final verification before deploying to production.

## Pre-Launch Checks
- [ ] **Tests Passing**: Run `pytest tests/` and verify 100% green.
- [ ] **Groq Connectivity**: Verify `GROQ_API_KEY` is non-placeholder.
- [ ] **DB Reachable**: Run `python -m orchestrator.src.tools.db_health` and confirm "SUCCESS".
- [ ] **Marketing Ready**: Run `python -m orchestrator.src.tools.marketing_check` and confirm "Real-world values detected".
- [ ] **Voice Verified**: Start API and use the `voice_client` template to test barge-in.
- [ ] **Environment**: Verify `.env.example` is sync'd with all new keys.

## Launch Tasks
- [ ] **Build Docker**: `docker-compose -f infra/docker/docker-compose.yml build`.
- [ ] **Tag Images**: Apply `swarm.project.version` and `swarm.build.sha256`.
- [ ] **Push Tags**: `git tag -a v0.1.0 -m "Initial launch" && git push origin v0.1.0`.
- [ ] **Deploy SaaS**: Point the SaaS DNS to the production load balancer.

## Post-Launch Monitoring
- [ ] **Watch Logs**: `docker logs -f orchestrator` for `ERROR` or `CRITICAL`.
- [ ] **Monitor Lineage**: Check `data/lineage/launch_manifest.json` after the first run.
- [ ] **Check Latency**: Measure time-to-first-token in Groq logs.

## Rollback Steps
1.  Revert git tags: `git checkout v0.1.0-last-working`.
2.  Redeploy previous Docker image tags.
3.  Notify team via Slack/Email.
