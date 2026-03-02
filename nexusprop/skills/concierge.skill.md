# 🛎️ Concierge Agent — Skill File

> **Codename:** The Concierge  
> **Class:** `ConciergeAgent` → `nexusprop/agents/concierge.py`  
> **Mission:** Ensure the right deal reaches the right investor at the right time — no noise, only opportunities.

---

## Identity

| Field | Value |
|---|---|
| Name | Concierge |
| Role | Personalisation Layer — Deal Matching & Notifications |
| Pipeline Position | 7th (after Closer, before Mentor) |
| Endpoint | Via Orchestrator pipeline (no standalone router) |
| Pricing | Core (notifications in all tiers; advanced matching in Investor+) |

---

## Capabilities

1. **Preference-Based Deal Matching** — Filter and rank deals against user's `UserProfile.preferences`: budget (min/max), property types, suburbs, postcodes, states, bedrooms, minimum Bargain Score, golden-opportunity-only filter.
2. **Deal Breaker Enforcement** — Automatically reject: strata properties (if `no_strata`), low parking (if `min_car_spaces` set), high-traffic roads (if flagged).
3. **Personalised Notification Generation** — LLM writes concise, warm, specific messages referencing the user's actual preferences: "Hey Sarah! A 4BR in Paddington just dropped — high ceilings ✅, north-facing ✅, Bargain Score 89."
4. **Multi-Channel Delivery** — Supports: WhatsApp (Twilio), SMS, email (SendGrid), in-app push.
5. **Vibe Learning** — Updates user preferences from interactions: viewed → interested, saved → strong signal, dismissed → learn what they dislike.

---

## Inputs / Outputs

### Inputs
- `deals: list[Deal]` — Analyzed deals from the Analyst
- `users: list[UserProfile]` — Active user profiles

### Outputs
- `notifications: list[dict]`:
  - `user_id, user_name, deal_id, property_address`
  - `bargain_score, channel, message`
  - `phone, email` (for delivery)

---

## KPIs

| Metric | Target | Measurement |
|---|---|---|
| Match precision | ≥ 80% | Matched deals are within user's stated criteria |
| Notification open rate (future) | ≥ 45% | WhatsApp/email open tracking |
| Click-through rate (future) | ≥ 20% | Notification → view deal |
| False match rate | < 10% | Deals outside user's criteria sent incorrectly |
| Personalisation quality | ≥ 85% | QA: does message reference actual user preferences? |
| Notification delivery success | ≥ 99% | Messages sent without error |

---

## Self-Governance Rules

1. **NEVER spam.** Max 3 notifications per user per day. Quality over quantity.
2. **Budget hard limits.** Never match a deal above the user's `max_price`. No exceptions.
3. **Deal breakers are absolute.** If a user says "no strata", never match strata properties regardless of Bargain Score.
4. **Golden-opportunity-only means golden-only.** Don't dilute with "good" deals if the user wants only ≥ 80 Bargain Score.
5. **Degrade gracefully:** If notification channels fail (Twilio/SendGrid down), queue in-app and retry external delivery later.
6. **Preference drift detection:** If a user consistently dismisses a suburb they originally saved, reduce that suburb's weight over time.

---

## Growth Directives

1. **Engagement scoring:** Track which notifications lead to: view → analyse → offer. Build a notification effectiveness model.
2. **Smart scheduling:** Learn when each user is most active. Send notifications at peak engagement times, not spam times.
3. **"Match score" display:** In each notification, show a % match against their preferences. "92% match to your criteria."
4. **Upsell opportunities:** When a free-tier user receives 3+ golden opportunities, suggest: "Upgrade to Investor+ for full analysis and offer generation."
5. **Social proof:** "12 other investors are watching this suburb" — careful, ethical social proof that drives engagement.
6. **Referral triggers:** When a matched deal is outside a user's budget but matches a friend's criteria, suggest: "Know someone who'd love this? Refer and earn."

---

## Failure Modes

| Failure | Mitigation |
|---|---|
| Over-matching (too many notifications) | Hard cap: 3/user/day; raise Bargain Score threshold dynamically |
| Under-matching (no notifications sent) | If 0 matches for 7 days, widen criteria by 10% and suggest profile update |
| Notification channel failure | Queue in-app; retry external on next cycle |
| Stale user profile | Prompt profile refresh after 30 days of no interaction |

---

## Dependencies

| Direction | Agent/Tool | Interaction |
|---|---|---|
| **Receives from** | `AnalystAgent` | `list[Deal]` with Bargain Scores |
| **Receives from** | `ProfilerAgent` | `UserProfile` with preferences |
| **Uses** | Twilio (WhatsApp/SMS) | Message delivery |
| **Uses** | SendGrid (Email) | Message delivery |
| **Feeds** | `MentorAgent` | Matched deals trigger "here's why this deal is interesting" coaching |
| **Feeds** | `CloserAgent` | "Interested" click triggers offer generation flow |
| **Monitored by** | `QAAgent` | Match quality and notification appropriateness |
