# Launch Checklist

## REQUIRED BEFORE LAUNCH

- [ ] **Start Backend Stack**:
    ```powershell
    cd infra/docker
    docker compose -f docker-compose.prod.yml up -d
    ```
- [ ] **Deploy SaaS Platform**:
    ```powershell
    cd projects/templates/landing-page
    vercel --prod
    ```
- [ ] **Verify Platform**:
    - Visit `https://frontend-two-xi-gal9lkptfi.vercel.app/`.
    - **Pricing**: Click "Select Plan" to test Stripe checkout flow.
    - **Cockpit**: Test Voice interaction.
    - **Store/Affiliates**: Verify data loading.
    - **Legal**: Check Footer links (Privacy, Terms, Affiliate Disclosure).
- [ ] **Seed Catalog** (if empty):
    ```powershell
    python -m orchestrator.src.core.catalog.ingest
    ```

## OPTIONAL / POST-LAUNCH

- [ ] **Content Automation**: Set up cron job to generate blog posts.
- [ ] **Analytics**: Add Google Analytics ID to `index.html`.
