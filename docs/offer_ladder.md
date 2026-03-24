# Realms2Riches Offer Ladder Strategy

This document describes the strategic sales funnel (Offer Ladder) implemented in the Realms2Riches catalog.

## Funnel Stages

The 18 products are categorized into five distinct stages designed to maximize customer lifetime value (LTV) and minimize acquisition friction.

### 1. Entry Stage (Low Friction)
*Goal: Convert a lead into a customer with minimal risk.*
- **Primary Offers:** `jarvis_basic` ($29/mo), `business_consultation` ($300).
- **Secondary Offers:** `elite_support` ($250/mo).

### 2. Foundation Stage (Core Infrastructure)
*Goal: Establish the customer's base digital assets.*
- **Offers:** `brand_kit` ($450), `website_basic` ($1500), `seo_package` ($800), `social_media_mgmt` ($600/mo).

### 3. Growth Stage (Optimization)
*Goal: Scale the customer's existing assets for better ROI.*
- **Offers:** `marketing_campaign` ($700), `jarvis_custom` ($299/mo), `website_advanced` ($3000).

### 4. Scale Stage (High-Ticket Automation)
*Goal: Deliver massive value through industrial-grade automation.*
- **Offers:** `startup_accelerator` ($1999), `jarvis_premium` ($999/mo), `ai_workflow` ($999/mo).

### 5. Enterprise Stage (Industrial)
*Goal: Long-term high-value bespoke partnerships.*
- **Offers:** `biz_automation` ($2499/mo), `digital_domination` ($4499), `custom_dev` ($4999), `ecommerce_dev` ($5000), `infra_setup` ($7500).

## Example Customer Flows

### Flow A: The AI-First Lead
1. **Entry:** User signs up for `jarvis_basic` ($29/mo).
2. **Upsell:** User is recommended `jarvis_custom` ($299/mo) after 30 days.
3. **Cross-sell:** User is offered `business_consultation` ($300) to optimize their Jarvis setup.
4. **High-Ticket:** User upgrades to `jarvis_premium` ($999/mo).

### Flow B: The New Entrepreneur
1. **Entry:** User books a `business_consultation` ($300).
2. **Upsell:** User purchases the `startup_accelerator` ($1999).
3. **Cross-sell:** User adds `elite_support` ($250/mo) for ongoing coaching.
4. **Enterprise:** User eventually moves to `biz_automation` ($2499/mo) as they scale.

## Implementation Details

The ladder is implemented via metadata in `data/catalog/products.json`:
- `funnel_stage`: String (entry, foundation, growth, scale, enterprise).
- `primary_entry_offer`: Boolean.
- `upsell_to`: List of IDs.
- `cross_sell_with`: List of IDs.

### Querying via API

- **Get all entry offers:** `GET /products?entry_only=true`
- **Get products by stage:** `GET /products?stage=growth`
- **Get recommendations for a product:** `GET /products?recommendations_for=website_basic`
