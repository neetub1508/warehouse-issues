# 04 — Service-Parts Planning Engine: Complete Methods Catalogue

Scope: every method, formula, parameter default, data requirement and known pitfall a service-parts planning (SPP) engine needs, from raw transactions to automated order release. Notation is plain-text/LaTeX-lite. Numbered citations `[n]` refer to the reference list at the end. Parameter defaults are **starting values for configuration**, not universal truths; where a default is practitioner convention rather than a published result, it is marked *(practice)*.

Notation used throughout:

| Symbol | Meaning |
|---|---|
| `x_t` | demand observed in bucket t |
| `D`, `λ` | mean demand per unit time (annual D; per-bucket λ) |
| `σ_D` | std dev of demand per bucket |
| `L`, `σ_L` | lead time (buckets) and its std dev |
| `R` | review period (buckets) |
| `v` | unit cost; `h` holding-cost rate per year (fraction of v); `r` sometimes used for same |
| `A` | fixed ordering cost per order |
| `Q` | order quantity; `s` reorder point; `S` order-up-to level |
| `k` | safety factor |
| `G(k)` | standard normal loss function `= φ(k) − k(1 − Φ(k))` |
| `EBO(S)` | expected backorders at base-stock S |
| `ADI` | average inter-demand interval; `CV²` squared coefficient of variation of non-zero demand sizes |

---

## 1. Demand data preparation

Demand preparation decides the quality ceiling of every downstream method. In service parts, 50–80% of SKUs are intermittent [1][2], so errors here (e.g. treating "not stocked" as "zero demand") silently bias every parameter.

### 1.1 Demand vs sales vs shipments vs consumption

| Signal | What it measures | Bias vs true demand | Use |
|---|---|---|---|
| **Demand (requests)** | Customer/technician requests at the requested date and location, qty requested | Unbiased if captured | Primary forecast input |
| **Sales / invoices** | Qty invoiced | Censored by availability (lost sales, substitutions), shifted by invoice lag | Fallback when requests not captured |
| **Shipments / issues** | Qty physically shipped/issued | Censored + shifted by backorder fill date + possibly shipped from a different location | Fallback; must be re-dated to request date |
| **Consumption** | Parts consumed in workshop jobs (job card / repair order) | Includes internal use; may be kitted (pre-issued and returned) | Primary for workshop-driven parts |
| **Orders from downstream stock points** | Branch replenishment orders to DC | Dependent demand; batched (bullwhip) | Never forecast DC from branch orders — aggregate branch *demand* instead [3] |

Rules:
- **Date = request date, location = requesting location**, not fulfilling location. If a branch request was filled from the DC or by transfer, the demand belongs to the branch.
- **Quantity = requested qty**, not shipped qty. Backorders that were later filled must not appear as two demands.
- **Kits/BOM explosion:** if parts are sold as kits, explode kit demand to component demand for components that are also stocked individually (dependent demand).

### 1.2 Lost sales and unconstrained demand

When a part is out of stock the customer may (a) wait (backorder — captured), (b) buy elsewhere (lost sale — usually not captured), (c) accept a substitute (captured under the wrong part).

- **Capture at source:** a "lost demand"/"quote not converted — no stock" reason code at the counter/workshop. This is the only reliable method. *(practice)*
- **Statistical unconstraining** when not captured: treat periods where on-hand = 0 for part of the bucket as censored. Estimate the demand rate from in-stock time only:
  `λ̂ = Σ demand in in-stock periods / Σ in-stock time` (exposure-based Poisson estimator). For more precision, use a censored-likelihood (Tobit / Kaplan-Meier-type) estimator [4][5].
- **Substitution:** if a superseding/alternate part was issued instead, attribute demand to the requested part (via the substitution link) for forecasting, and to the issued part for stock movement.
- Pitfall: unconstraining a genuinely declining part inflates forecasts. Unconstrain only when the stockout share of the history window is material (e.g. > 10% of periods) *(practice)*.

### 1.3 Demand streams

Keep separate streams with separate flags because they behave differently and have different service targets:

| Stream | Characteristics | Treatment |
|---|---|---|
| **Paid / retail / counter** | Customer-driven, price sensitive | Forecast; main service target |
| **Workshop / repair-order** | Driven by service visits; correlated with installed base age | Forecast; often higher criticality (vehicle off road) |
| **Warranty** | Driven by failure rate × units in warranty; campaigns/recalls cause spikes | Forecast separately with installed-base model; recalls are *planned* demand, not forecast |
| **Internal / own-use** | Company fleet, demo, tooling | Forecast or plan; exclude from customer KPIs |
| **Emergency / VOR (vehicle off road)** | Urgent, often filled cross-location or by supplier direct ship | Include in demand; tag so emergency % KPI is computable |
| **Campaign / recall / project** | Known in advance, one-off | Enter as firm future demand; **exclude from history** used for statistical forecasting |
| **Inter-location transfers** | Not end demand | Exclude (see 1.5) |

### 1.4 Returns netting

- Net **customer returns** against demand only when the return is linked to an original sale and occurs within a window (e.g. 30–90 days) *(practice)*; attribute the netting to the **original sale's bucket**, not the return date — otherwise a return creates negative demand in a later bucket.
- **Do not net**: core returns (repairables, section 6), warranty returns (defective parts going to supplier), stock-rotation returns to supplier, returns of wrong-picked items (these were never demand — remove the original transaction instead).
- Floor per-bucket net demand at 0. Negative net demand is a data error signal.

### 1.5 Transfer exclusion

- Inter-branch and DC→branch transfers are **not** end demand at the network level. At the DC they are **dependent demand** (derived from branch demand).
- Single-echelon engine: forecast each location from its own end demand; DC forecast = own direct end demand + Σ branch replenishment *requirements* computed from branch forecasts and policies (DRP logic), not historical transfer volumes.
- Double-count trap: if branch demand was filled by transfer from another branch, count it once, at the requesting branch.

### 1.6 Outlier detection and cleansing

Intermittent series make classical outlier rules (±3σ) useless because σ is dominated by the zeros.

Recommended approach:
1. Detect on **non-zero demand sizes** only, per SKU-location.
2. Robust z-score (Iglewicz & Hoaglin [6]): `M_i = 0.6745 (y_i − median(y)) / MAD`, flag if `|M_i| > 3.5`. Requires ≥ 5–8 non-zero observations; otherwise use a rule such as "size > max(3 × median non-zero size, P95 of family)" *(practice)*.
3. Classify the outlier before acting: one-off project/fleet order (remove, or move to planned-demand stream), data error (correct), genuine large customer (keep but flag — lumpy is real in service parts).
4. **Winsorize** (cap to threshold) rather than delete for statistical forecasting; keep the raw value for the empirical distribution if it is a genuine repeatable pattern.
5. Also detect **level shifts** (supersession, new model launch, contract win/loss) — these are not outliers; they need a history truncation or a regime marker.

Pitfall: auto-cleansing the top spikes of lumpy parts systematically under-forecasts and under-stocks the very parts that cause emergency orders. Always log the original and the cleansed value; cleansing is an override and should be measured by FVA (section 9).

### 1.7 Zero vs missing periods

| Situation | Treat as |
|---|---|
| Part active and stockable, nobody requested it | **0** (true zero) |
| Part not yet introduced / not in catalogue / before first receipt | **Missing** (history starts later) |
| Location closed / system outage / data migration gap | **Missing** |
| Part blocked / on sales stop | **Missing** (or censored) |
| Part out of stock and demand not captured | **Censored** (see 1.2) |

Pitfall: padding pre-introduction months with zeros drags down the forecast of a new part for years and misclassifies it as intermittent. Store a `history_start_date` per SKU-location = first of {first receipt, first demand, catalogue introduction date}.

### 1.8 Time buckets and bucket choice

- **Store daily**, aggregate on demand. Storage is cheap; re-bucketing is impossible if you only keep monthly.
- **Forecast bucket:** monthly is standard for slow movers; weekly for fast movers and for short lead times (< 4 weeks); daily only for replenishment execution and very fast movers.
- **Intermittent demand:** coarser buckets reduce the share of zeros and can move an item from "lumpy" to "smooth" (temporal aggregation, section 3.7). The *decision-relevant* horizon is `L + R`; forecasting directly at that aggregation level is often most accurate for inventory purposes [7][8].
- ADI/CV² classification depends on the bucket; always record which bucket a classification used.
- Rule of thumb *(practice)*: bucket length ≤ min(review period, lead time); at least 24 buckets of history for classification; 36+ for seasonality.

### 1.9 Supersession history roll-up

Parts are superseded (A→B), often in chains (A→B→C), sometimes with ratios (1 A = 2 B) or one-to-many (A → B + C kit).

Data needed per link: `old_part, new_part, ratio (new qty per old qty), effective_date, interchangeability (two-way | one-way forward | not interchangeable), use_up_flag (sell old stock first)`.

Rules:
- **History transfer:** demand of old part before `effective_date` is converted `x_new = x_old × ratio` and added to the new part's history. Resolve chains recursively to the **terminal** (current) part number.
- **Two-way interchangeable:** pool history, pool stock, plan on terminal part.
- **One-way (old can be replaced by new, not vice versa):** old stock is consumed first (use-up); stop replenishing old; new part's forecast covers total demand minus projected old-part stock depletion.
- **Not interchangeable (new model only):** do *not* transfer history; old part enters phase-out/LTB logic (section 7), new part uses analogue/NPI (7.1).
- **One-to-many / kit supersession:** explode by ratio to each component.
- Effective dates matter: demand after the effective date recorded against the old part (due to catalogue lag) must also be mapped.
- Pitfall: cycles in supersession data (A→B→A) — detect and break. Also mismatched units of measure across the chain.

### 1.10 New-part analogues

- **Analogue (like-part) method:** new part inherits the demand profile of an existing part with the same function on a predecessor model, scaled by installed-base ratio: `λ_new(t) = λ_analogue(t_age) × (N_new(t) / N_analogue(t_age))`, where `t_age` aligns by months since model launch.
- Use analogue until the new part has enough own history (e.g. 6–12 months or ≥ 5 non-zero buckets), then **blend**: `F = w·F_own + (1 − w)·F_analogue`, with `w` rising linearly from 0 to 1 over the transition window *(practice)*.
- Group/hierarchical approach: forecast at part family × model level and allocate top-down by mix.

### 1.11 Calendar and working days

- Normalize demand per **working day** before modelling where working days vary materially by month (holidays, festive seasons, Sundays closed): `x_t^norm = x_t × (standard_days / working_days_t)`; re-apply the calendar when producing the forecast.
- Location-specific calendars (branch holidays), supplier calendars (for lead time in working days), DC calendars (for release dates).
- Lead time must be converted to the same bucket basis as demand (calendar days vs working days) — mixing them is a classic error that under- or over-states lead-time demand by ~15–30%.

---

## 2. Classification

Classification drives method selection, service targets and review frequency. Keep several orthogonal dimensions rather than one composite code.

### 2.1 ABC

| Variant | Criterion | Typical cut-offs |
|---|---|---|
| **Value ABC** | Annual usage value `D × v` | A = top ~80% of value (≈10–20% of SKUs), B next 15%, C last 5% *(practice)* |
| **Hits / pick-frequency ABC** (FMR, "velocity") | Number of order lines per year | A = top 50% of lines, B next 30%, C rest *(practice)*; drives warehouse slotting and stocking decisions |
| **Margin ABC** | Gross margin contribution | For commercial prioritization |
| **Cost-based criterion** (Teunter, Babai & Syntetos [9]) | `c_i × D_i / (h_i × Q_i)` where c = shortage cost | Shown to outperform value ABC for cost-service trade-off; low-cost items should get *higher* service levels |
| **Multi-criteria ABC** | Weighted combination: value, hits, criticality, lead time, obsolescence risk | AHP weights (Flores & Whybark [10]; Partovi), or DEA-like weighted linear optimization (Ramanathan [11]; Ng [12]) |

Pitfall: classic value ABC assigning the highest service level to A items is cost-*inefficient* — the cheapest way to raise aggregate fill rate is high service on cheap, fast items [9][13].

### 2.2 XYZ (variability)

`CV = σ_D / mean_D` per bucket (including zeros).

| Class | CV (practice defaults) | Meaning |
|---|---|---|
| X | < 0.5 | Stable |
| Y | 0.5 – 1.0 | Variable / seasonal |
| Z | > 1.0 | Erratic / intermittent |

XYZ is a coarse proxy; for method selection use SBC (2.5) instead.

### 2.3 FSN (movement)

Based on days since last issue or annual turnover *(practice)*:
- **F**ast: issued in ≥ N of last 12 months or turnover > 3.
- **S**low: some issue in last 12 months but below F.
- **N**on-moving: no issue in last 12 (or 24) months → review for obsolescence (7.3).

### 2.4 VED (criticality)

- **V**ital: absence stops the equipment/vehicle (VOR), safety-related, or regulatory.
- **E**ssential: degraded operation.
- **D**esirable: cosmetic/convenience.

Used with ABC in a VED×ABC matrix to set service targets (e.g. V×C → 99% because cheap; D×A → 85%). Criticality is usually a master-data attribute (from engineering/FMEA), not derived from demand.

### 2.5 Syntetos–Boylan–Croston (SBC) demand patterns

Syntetos, Boylan & Croston [14] derived cut-offs from comparing MSE of Croston/SBA vs SES:

`ADI = (number of buckets in window) / (number of non-zero buckets)`
`CV² = (σ of non-zero sizes / mean of non-zero sizes)²`

| Pattern | ADI | CV² | Recommended method |
|---|---|---|---|
| **Smooth** | < 1.32 | < 0.49 | SES / Holt / Holt-Winters |
| **Erratic** | < 1.32 | ≥ 0.49 | SES or SBA |
| **Intermittent** | ≥ 1.32 | < 0.49 | SBA (or Croston/TSB) |
| **Lumpy** | ≥ 1.32 | ≥ 0.49 | SBA / TSB / bootstrap; empirical LTD |

Notes:
- Kostenko & Hyndman [15] showed the SBC cut-offs are approximations; the exact boundary is a curve `ADI > 4/3 − ... ` depending on α; a simpler practical rule is "use SBA when `ADI > 1.32` or `CV² > 0.49`". Petropoulos & Kourentzes [16] recommend combining rather than hard-switching.
- Minimum data: at least ~4–5 non-zero observations to estimate CV² meaningfully; below that, class = "insufficient/very slow" → Poisson/NB or rule-based stocking.
- Add a **"very slow / sporadic"** class (e.g. ≤ 2 hits in 24 months) handled by stock/no-stock rules (4.12), not forecasting.

### 2.6 Lifecycle stages

| Stage | Detection rule *(practice)* | Planning mode |
|---|---|---|
| **Pre-launch / NPI** | No history; installed base launching | Initial provisioning (7.1), analogue |
| **Introduction / ramp-up** | < 12 months history, rising installed base | Analogue blend; installed-base model; frequent review |
| **Maturity** | Stable level, ≥ 24 months | Statistical forecast per SBC |
| **Decline** | Significant negative trend over 12–24 months (e.g. slope test p < 0.1 or 12M/prior-12M < 0.7) | Damped/declining model (TSB handles obsolescence well [17]); lower max levels |
| **Phase-out / EOL** | Supersession one-way, supplier EOL notice, model discontinued | Use-up, LTB (7.2), no replenishment |
| **Obsolete / dead** | No demand for 24–36 months or no installed base | Disposal decision (7.3) |

---

## 3. Forecasting

### 3.1 Moving average

`F_{t+1} = (1/N) Σ_{i=0}^{N−1} x_{t−i}`. Default N = 12 (monthly). Robust baseline; biased on trend; for intermittent demand behaves similarly to SES with α ≈ 2/(N+1). Use as **benchmark** in backtests.

### 3.2 Simple exponential smoothing (SES)

`F_{t+1} = α x_t + (1 − α) F_t`. Defaults: α = 0.1–0.3 for smooth; **0.05–0.2 for intermittent** [14][18]. Optimize α per SKU only with enough data; otherwise fix by class (overfitting risk). Bias on intermittent data: SES forecasts are highest right after a demand and decay in between — "decision point bias" when orders are triggered right after demand [19].

### 3.3 Holt (trend) and damped trend

Level `l_t = α x_t + (1−α)(l_{t−1} + φ b_{t−1})`
Trend `b_t = β(l_t − l_{t−1}) + (1−β) φ b_{t−1}`
Forecast `F_{t+h} = l_t + (φ + φ² + … + φ^h) b_t`.
Defaults: α 0.1–0.3, β 0.01–0.1, damping φ 0.8–0.98 (Gardner & McKenzie [20]). Always prefer **damped trend** for parts — undamped trend extrapolation on decline produces negative forecasts; on ramp-up it overshoots.

### 3.4 Holt-Winters (seasonal)

Multiplicative: `l_t = α x_t / s_{t−m} + (1−α)(l_{t−1}+b_{t−1})`; `s_t = γ x_t / l_t + (1−γ) s_{t−m}`; `F_{t+h} = (l_t + h b_t) s_{t+h−m}`. Defaults γ 0.05–0.3, m = 12 (monthly).
Requirements/pitfalls: ≥ 2–3 full seasons; multiplicative seasonality breaks with zeros (division by zero) → **never on intermittent SKUs**. For seasonal intermittent parts (batteries in winter, AC parts in summer) estimate seasonal indices at **family/group level** and apply to the SKU level (group seasonal indices; Dekker, van Donselaar & Ouwehand [21]).

### 3.5 Croston's method

Croston [22]: update only in periods with demand (`x_t > 0`):
`z_t = α x_t + (1 − α) z_{t−1}` (size)
`p_t = α q_t + (1 − α) p_{t−1}` (interval since last demand, `q_t`)
Forecast per period: `F = z_t / p_t`. No update in zero periods.
Default α = 0.05–0.2 (same α for both, or separate α_z, α_p).
Known issue: **positively biased** because `E[z/p] ≠ E[z]/E[p]` [23].

### 3.6 SBA, SBJ, TSB

- **SBA (Syntetos–Boylan Approximation)** [23]: `F = (1 − α_p/2) · z_t / p_t`. The default choice for intermittent demand in most empirical studies.
- **SBJ (Shale–Boylan–Johnston)** [24]: for Poisson arrivals, `F = (1 − α_p/(2 − α_p)) · z_t / p_t`.
- **TSB (Teunter–Syntetos–Babai)** [17]: updates *probability of demand occurrence* every period, size only on demand:
  `d_t = β · 1(x_t > 0) + (1 − β) d_{t−1}`
  `z_t = α x_t + (1 − α) z_{t−1}` if `x_t > 0`, else `z_t = z_{t−1}`
  `F = d_t · z_t`. Defaults: α 0.1–0.3, β 0.01–0.1 (β small, α larger).
  Advantage: forecast **decays during long zero runs** → handles obsolescence/decline; Croston/SBA never decrease until the next demand. Recommended for parts in decline or with obsolescence risk [25].
- Other variants: Levén–Segerstedt (modified Croston, biased [26]), iMAPA [16], "Croston with Poisson/Bernoulli" probabilistic variants (Snyder, Ord & Beaumont [27]).

### 3.7 Temporal aggregation: ADIDA, MAPA, IMAPA

- **ADIDA** (Aggregate–Disaggregate Intermittent Demand Approach) [28]: aggregate to non-overlapping buckets of size m (commonly m = L + R or m = ADI), forecast with SES/SBA at the aggregate level, disaggregate equally (`F/m`). Reduces intermittency and variance.
- **Overlapping vs non-overlapping** aggregation: Boylan & Babai [8] — overlapping (rolling LTD sums) gives more observations but correlated ones; both beat per-period forecasting for LTD.
- **MAPA / IMAPA** [29][16]: forecast at multiple aggregation levels and combine; robust default for intermittent series.

### 3.8 Bootstrapping (Willemain)

Willemain, Smart & Schwarz [30] — directly generates the **lead-time demand (LTD) distribution**:
1. Estimate a 2-state Markov chain for zero/non-zero occurrence from history (transition probs P(0→0), P(0→1), P(1→0), P(1→1)).
2. For each of B replications (default B = 1,000): simulate occurrence over L (+R) periods starting from the last state.
3. For each non-zero period sample a size from historical non-zero sizes, then **jitter**: `x* = 1 + INT(x + Z √x)`, Z ~ N(0,1); if `x* ≤ 0` use x.
4. Sum → one LTD sample. The empirical distribution of B sums gives quantiles for s/S.

Evidence: mixed. Gardner & Koehler criticised the original study; Syntetos et al. [31] and Zhu et al. [32] show bootstrapping helps mainly for long lead times with lumpy demand and enough history; plain empirical/SBA-parametric often comparable. Pitfall: cannot generate sizes never observed (tail truncated); poor with < ~10 non-zero points.

### 3.9 Parametric distributions for slow movers

| Distribution | When | Parameters | Notes |
|---|---|---|---|
| **Poisson** | Unit-sized, independent demands; VMR ≈ 1 | λ | Classical for very slow movers; Palm's theorem (4.8) |
| **Negative binomial (NB)** | Over-dispersed, VMR > 1 | mean μ, variance σ² (> μ) → `p = μ/σ²`, `r = μ²/(σ² − μ)` | Good general-purpose for slow movers [33] |
| **Compound Poisson ("stuttering Poisson")** | Poisson order arrivals, random order sizes; stuttering = geometric sizes | λ (order rate), size distribution | Stuttering Poisson = geometric-compound Poisson, equivalent to NB class. Common in spare parts (Ward 1978; Silver et al. [13]) |
| **Poisson–logarithmic** | Compound Poisson with log sizes | = NB | |
| **Gamma** | Continuous approximation for LTD with high CV | shape, scale | Dunsmuir & Snyder [34]; avoids negative values of normal |
| **Binomial / Bernoulli-compound** | Under-dispersed (VMR < 1), per-period demand occurrence | | Adan, van Eenige & Resing [35]: fit by mean and variance: VMR < 1 → binomial, = 1 → Poisson, > 1 → NB |
| **Normal** | Only for fast movers where LTD mean ≳ 10–20 units | μ, σ | Otherwise negative mass and wrong tails |

Fitting rule (practice, after [35]): compute LTD mean μ_LTD and variance σ²_LTD; choose family by VMR; fall back to Poisson if variance estimate unreliable (< 5 non-zero points).

### 3.10 Empirical distributions

Use observed (overlapping) LTD sums from history directly, or the bootstrap. Porras & Dekker [36] found empirical LTD methods performed best in a refinery spare parts case. Requirement: history length ≫ lead time (e.g. ≥ 3 × (L+R) windows). Pitfall: with short history, quantile estimates at 95–99% are the max observed value — understates the tail.

### 3.11 Causal / installed-base forecasting

`λ(t) = Σ_k N_k(t) × u_k(t) × fr_k(a) × q_k`
- `N_k(t)`: installed base (units in field) of equipment/model k at time t (from sales, registrations, service contracts, minus scrapped).
- `u_k`: usage intensity (km/year, hours/year).
- `fr_k(a)`: failure / replacement rate per unit usage at age a (from reliability data; Weibull hazard `h(a) = (β/η)(a/η)^{β−1}`); for wear parts, a scheduled replacement interval.
- `q_k`: parts per replacement × share of replacements done through own network ("capture rate", often 30–70% and falling with equipment age).
Review: Van der Auweraer, Boute & Syntetos [37]; Dekker et al. [38]; Jalil et al. [39]. Most valuable for: new models (no history), end-of-life (declining base), warranty, and planned-maintenance parts. Pitfall: capture rate and installed-base decay are the dominant errors, not the failure rate.

### 3.12 IoT / condition-based

With telematics / condition monitoring, demand becomes partly **advance demand information**: predicted failures (remaining useful life, RUL) generate probabilistic future demands at known locations. Methods: convert RUL distributions to per-bucket demand probabilities, sum over the installed base (Poisson-binomial), or use as leading indicator in regression. Topan et al. [40] review. Pitfall: prediction lead time must exceed replenishment lead time to be useful; false-positive alerts inflate stock.

### 3.13 NPI and EOL curves

- **NPI ramp**: installed base grows with sales (Bass-type diffusion or plan), demand for wear parts lags installation by first-service interval; failure parts follow bathtub (infant mortality then flat).
- **EOL decay**: after production stops, `N(t) = N_0 e^{−δt}` or survival curve `S(a)`; demand `λ(t) = λ_0 · N(t)/N_0` or a fitted exponential decline `λ(t) = λ_0 e^{−γt}` [41][42]. Used for LTB (7.2).

### 3.14 Machine learning

| Approach | Strength | Failure modes on sparse service-parts data |
|---|---|---|
| Gradient boosting (LightGBM/XGBoost) global model with Tweedie/Poisson loss | Won M5 (retail, heavily intermittent) accuracy track [43]; uses cross-series features (price, calendar, hierarchy) | Needs thousands of related series and rich covariates; point forecasts optimized for MSE/Tweedie; no calibrated quantiles unless trained with quantile loss; leakage via features |
| DeepAR / probabilistic RNN [44] | Native probabilistic output (NB likelihood), global learning, cold start via covariates | Data hungry; unstable training; poor on very short / < 5 non-zero series; hard to explain to planners |
| MLP for intermittent (Kourentzes [45]) | Can capture interval-size interaction | Mixed results vs SBA |

When ML fails: small SKU counts (< ~5,000 series), few covariates, lumpy demand driven by unobserved events, frequent regime changes (supersessions), and when evaluated with MAE/MAPE (rewards zero forecasts). Pragmatic stance: statistical methods first; ML as an ensemble member for smooth/erratic fast movers with covariates; always benchmark against SBA/TSB with **inventory-based** metrics (3.17) [46].

### 3.15 Model selection and ensembles

- **Rule-based selection** by SBC class (2.5) is robust and explainable — recommended default.
- **Backtest-based selection** per SKU (choose the method with best out-of-sample metric) overfits for noisy series; Kourentzes [47] shows in-sample selection criteria for intermittent demand are unreliable.
- **Ensembles / combinations** (e.g. median or mean of SES, SBA, TSB, MAPA) are consistently robust [16][48]. Equal weights beat estimated weights for short series ("forecast combination puzzle").
- **Parameter optimization**: optimize smoothing constants on a **pooled** basis per class rather than per SKU for sparse data.
- Retain the selected model for a minimum period (e.g. 3–6 months) unless error degrades significantly — prevents model-switching nervousness (section 10).

### 3.16 Backtesting (rolling origin)

- Rolling-origin evaluation (Tashman [49]): forecast origins `T_0, T_0+1, …`; each forecast uses only data up to origin; horizons 1…H where H covers `L + R`.
- Evaluate on **lead-time-demand sums** as well as per-period forecasts, since inventory decisions depend on LTD.
- Hold-out ≥ 12 origins; exclude periods affected by known events (recalls) from scoring.
- Simulate the actual inventory policy on the hold-out (inventory simulation backtest) to get achieved fill rate vs stock — the decision-relevant test [50][51].

### 3.17 Error metrics for intermittent demand

| Metric | Formula | Notes |
|---|---|---|
| **MAPE** | `mean(|e_t| / x_t)` | **Undefined when x_t = 0** — unusable for intermittent; asymmetric; never use [52] |
| **sMAPE** | `mean(2|e|/(|x|+|F|))` | = 200% whenever x = 0 and F > 0; unstable |
| **MAE / scaled MAE** | `mean|e|` ; `MAE / mean(x)` (a.k.a. MAD/mean) | MAE is minimized by the **median**, which is 0 for intermittent series → rewards a zero forecast [53][54] |
| **MASE** (Hyndman & Koehler [52]) | `mean|e_t| / ((1/(n−1)) Σ |x_i − x_{i−1}|)` | Scale-free, defined with zeros; still median-optimal |
| **RMSSE** (M5 [43]) | `sqrt( mean(e_t²) / ((1/(n−1)) Σ (x_i − x_{i−1})²) )` | Mean-optimal → appropriate for inventory (mean-based); use this or scaled MSE |
| **Scaled MSE / Relative MSE** | `MSE / mean(x)²` | Mean-optimal; sensitive to outliers |
| **Bias / mean error, scaled** | `mean(e)/mean(x)`; cumulative error | Most important for inventory; tracking signal (10.1) |
| **PIS (periods in stock)** (Wallström & Segerstedt [55]) | `PIS = −Σ_{t} Σ_{i≤t} e_i` (cumulative forecast error accumulated over time) | Measures stock-holding/stockout implied by bias over time; scaled version `sPIS = PIS / mean(x)` |
| **Pinball (quantile) loss** | `L_τ(y, q) = τ(y−q) if y ≥ q else (1−τ)(q−y)` | Evaluates quantile forecasts (the reorder point *is* a quantile). M5 uncertainty track used scaled pinball loss |
| **Probabilistic scores** | Rank probability score (RPS), CRPS, log score | For full predictive distributions of counts (Kolassa [54]) |
| **Inventory/service-based** | Achieved fill rate / CSL vs target, average stock value, trade-off curves (stock vs fill rate) | The decisive evaluation (Syntetos & Boylan [50]; Teunter & Duncan [51]; Kourentzes [47]) |

Guidance: report RMSSE + scaled bias + PIS for point forecasts; pinball loss at the target quantiles for distributions; choose methods on **inventory trade-off curves**. Why MAPE fails: division by zero, explodes on small actuals, penalizes over- and under-forecast asymmetrically, and is not tied to cost.

Also account for **parameter uncertainty**: plugging estimated μ, σ into safety-stock formulas as if known under-delivers service, especially with short histories; Prak & Teunter [56] give corrections (inflate variance of LTD by estimation variance of forecast error).

---

## 4. Inventory policies

References: Silver, Pyke & Thomas [13]; Axsäter [57]; Sherbrooke [58]; Muckstadt [59].

### 4.1 Policy catalogue

| Policy | Rule | Fits |
|---|---|---|
| **(s, Q)** | Continuous review; when inventory position (IP) ≤ s, order Q | Fast/medium movers, fixed lot sizes (MOQ, pack) |
| **(s, S)** | Continuous review; when IP ≤ s, order up to S | Variable order sizes (lumpy), minimizes ordering + holding; handles undershoot |
| **(R, S)** | Every R, order up to S | Periodic ordering cycles (weekly supplier run), coordination of many items per supplier |
| **(R, s, S)** | Every R, if IP ≤ s order up to S | Most common ERP "min/max with review cycle"; cost-optimal among periodic policies (Scarf) but harder to compute |
| **Min/Max** | Practitioner (R, s, S): min = s, max = S | ERP-native; set `max = min + EOQ` (or pack-rounded) |
| **Base stock (S−1, S)** | One-for-one replenishment; order a unit each time one is demanded | Slow, expensive, critical parts; repairables (METRIC) |

**Inventory position** `IP = on hand + on order (open POs, in-transit) − backorders − committed/allocated`. Always trigger on IP, never on on-hand.

### 4.2 EOQ and the K-curve (exchange curve)

`EOQ = sqrt(2 A D / (h v))`.
Pitfalls: A and h are rarely known — so use the **exchange curve** (Silver et al. [13]): with common `K = sqrt(2A/h)`, `Q_i = K sqrt(D_i / v_i)`, and aggregate
- Total cycle stock value `TCS = (K/2) Σ sqrt(D_i v_i)`
- Total orders per year `N = (1/K) Σ sqrt(D_i v_i)`
- Hence `TCS × N = (Σ sqrt(D_i v_i))² / 2` — a hyperbola. Management picks the operating point (e.g. warehouse ordering capacity) and backs out the implied A/h.
Service parts reality: Q is often dominated by MOQ/pack size; for slow movers Q = 1 or pack; for fast movers apply EOQ bounded by `[MOQ, max months of supply (e.g. 3–6 months) *(practice)*]`, round to pack multiple.

### 4.3 Service-level definitions

| Measure | Definition | Notes |
|---|---|---|
| **α — cycle service level (CSL)** | P(no stockout during a replenishment cycle) = P(LTD ≤ s) | Easy, ignores order size & frequency; poor for intermittent (most cycles have zero demand) |
| **β — fill rate** | Fraction of demand (units) filled immediately from stock | Preferred customer-facing measure; also line fill rate (fraction of lines) |
| **γ — ready rate** (Schneider [60]) | Fraction of time on-hand > 0 | For Poisson unit demand, ready rate = fill rate (PASTA) |
| **Availability (equipment)** | Fraction of time equipment not waiting on parts: `A = MTBF/(MTBF + MTTR + MWT)` with MWT = mean waiting time for parts `= EBO / λ` (Little's law) | Multi-item system objective (4.14) |
| **Order fill rate** | Fraction of customer orders filled completely | Multi-line orders; lower than line fill rate |
| **Expected waiting time / backorder time** | `EBO/λ` | Service-contract metric |

Always specify which measure, which level (unit/line/order), and at which point (location, network, first-pass).

### 4.4 Safety stock — normal approximations

- Known constant L: `σ_LTD = σ_1 sqrt(L)` (σ_1 = std dev of one-bucket forecast error; assumes independence).
- Variable L: `σ_LTD = sqrt( L σ_D² + D² σ_L² )` (Silver et al. [13]).
- Periodic review: replace L by `L + R`.
- **CSL target α:** `s = μ_LTD + k σ_LTD` with `k = Φ^{−1}(α)`.
- **Fill-rate target β, (s,Q):** expected shortage per replenishment cycle `ESPRC = σ_LTD G(k)`; `β = 1 − ESPRC / Q` → solve `G(k) = (1 − β) Q / σ_LTD`.
- **Fill-rate, (R,S):** `β = 1 − [ESPRC(L+R) − ESPRC(L)] / (μ_R)`; the second term is often dropped (conservative), but must be kept when R is short relative to L or service is low [13].
- **Use forecast error, not demand variability** for σ_1 (RMSE of 1-step forecast errors, or `1.25 × MAD` under normality).
- Floor safety stock: minimum 0; if the normal gives `μ_LTD − 3σ < 0` substantially (i.e. μ_LTD < ~10–20 units or CV_LTD > 0.5), switch to a discrete distribution.

### 4.5 Safety stock — discrete (Poisson/NB/empirical)

Choose the smallest `s` (or S) satisfying the target:
- CSL: `P(LTD ≤ s) ≥ α`.
- Fill rate for (S−1,S) with unit demand: `β = P(LTD ≤ S − 1)`.
- General discrete fill rate for (R,S) or (s,Q): computed from expected backorders
  `EBO(S) = Σ_{x > S} (x − S) p(x)` over the relevant LTD distribution,
  `β(R,S) = 1 − [EBO_{L+R}(S) − EBO_L(S)] / (λ R)` (units).
- For (s,Q) with discrete demand: `β = 1 − [EBO_L(s) − EBO_L(s+Q)] / Q` (Hadley–Whitin form) [57].

### 4.6 Fill rate for intermittent demand — the pitfall

Standard formulas assume demand occurs every period. With intermittent demand:
- Many review periods have zero demand; a classical CSL target is met "for free" and says nothing about customer experience.
- Fill-rate formulas must **condition on demand occurring**: Teunter, Syntetos & Babai [61] show the traditional (R,S) fill-rate approximation badly misestimates fill rate for compound-Bernoulli (intermittent) demand, and give the corrected expression: expected unfilled demand in a period given demand occurs, using `P(demand > 0)` and the size distribution. Practically: compute fill rate as `1 − E[units short in periods with demand] / E[demand]` by exact enumeration or simulation of the compound distribution.
- Large order sizes: a single order of 10 against S = 6 fills 6 or 0 depending on partial-fill policy. Model **whether partial fills are allowed** (line fill rate vs unit fill rate differ).
- Undershoot in (s,S)/(s,Q) with lumpy demand: IP jumps below s; add expected undershoot `E[U] ≈ (σ_x² + μ_x²)/(2 μ_x) − 1/2` (x = transaction size, renewal approximation) to the reorder point or model it directly [13][57].

### 4.7 Lead-time demand distribution

LTD = Σ demand over L (+R) buckets, L random. Options:
1. Parametric: mean `μ_LTD = λ E[L]`, variance `σ²_LTD = E[L] σ_D² + λ² σ_L²`; fit normal/gamma/NB by moments.
2. Compound over L distribution (mixture): `P(LTD = x) = Σ_l P(L=l) P(D_l = x)` — exact when L empirical distribution is available.
3. Empirical overlapping sums / bootstrap (3.8, 3.10).
Pitfall: using expected L only ignores lead-time variability, which for imported parts (σ_L ~ 20–50% of L) often dominates demand variability.

### 4.8 Base-stock (S−1, S) for slow movers — Palm's theorem

For Poisson demand λ and i.i.d. replenishment times with mean T (any distribution), the number of units in resupply (pipeline) is **Poisson(λT)** in steady state (Palm's theorem; Feeney & Sherbrooke [62]). Hence:
- `P(pipeline = x) = e^{−λT}(λT)^x / x!`
- `Fill rate = P(X ≤ S − 1)`, `EBO(S) = Σ_{x>S} (x−S) P(X=x)`, `Expected on hand = S − λT + EBO(S)`.
- For compound Poisson demand the pipeline is compound Poisson (use NB fit).
Default: use for items with mean LTD < ~2–5 units and unit value high relative to order cost *(practice)*.

### 4.9 Review period

- R set by supplier ordering calendar (e.g. weekly per supplier), DC→branch delivery schedule (daily/2×week), or planner workload.
- Longer R raises safety stock `∝ sqrt(L+R)` and cycle stock; shorter R raises order lines/handling.
- Joint replenishment (can-order policies, (S, c, s)) for supplier consolidation to reach freight minimums.

### 4.10 MOQ and pack rounding effects

- Effective Q = `max(MOQ, round_up_to_pack(Q_calc))`. Larger effective Q **raises fill rate** for a given s (fewer exposures) — compute s **after** rounding, using the effective Q in the fill-rate formula; otherwise systematic overstock.
- Rounding the reorder point/min to packs: round s to integer (units), not to pack, unless the part is only sold/issued in packs.
- MOQ ≫ annual demand → excess and obsolescence risk. Rule: if MOQ > X months of demand (e.g. 12–24), flag for sourcing review/no-stock decision *(practice)*.
- Pack-size-issued parts (bolts sold by 10): forecast and stock in issue units, convert to purchase UoM with conversion factor; many errors come from UoM mismatches.

### 4.11 Criticality and differentiated targets

Service target matrix example *(practice)*:

| | A (value) | B | C |
|---|---|---|---|
| Vital | 97% | 98% | 99% |
| Essential | 93% | 95% | 97% |
| Desirable | 85% | 90% | 95% |

(higher targets on cheaper items per [9]). Better: replace the matrix with **cost-optimal** targets `β*` from the newsvendor critical ratio on shortage cost `b` vs holding `h v`: for backorders with (R,S), `P(LTD ≤ S) = b / (b + h v R)` approximately [57]; or with system optimization (4.14).

### 4.12 Stock / no-stock decisions and hits rules

Decide per SKU × location whether to hold stock at all.

- **Hits rule** *(practice)*: stock at branch if ≥ H_b hits (order lines) in the last 12 months (typical H_b = 3–6) **and** hits in ≥ 2 of the last 4 quarters (recency); stock at DC if network hits ≥ 1–2 in 12 months. Hysteresis: add at H_b, remove below H_b − 2 to avoid flip-flop.
- **Break-even economic rule**: stock one unit (S = 1) if
  `annual cost of stocking = h v × E[on hand | S=1] + obsolescence risk × v`
  `< annual cost of not stocking = λ × (c_emergency + c_delay) × (1 − fill rate from upstream)`.
  With Poisson and S = 1: `E[on hand] = 1 − λT + EBO(1)`, fill rate `= e^{−λT}`.
- **Criticality override**: Vital items with long lead time and any installed base → stock ≥ 1 regardless of hits (insurance stock).
- **Non-stock items**: planned as special orders; measure demand to re-evaluate.

### 4.13 Budget-constrained marginal allocation (greedy)

Objective: minimize total expected backorders (or maximize fill rate/availability) subject to budget `Σ v_i S_i ≤ B` (Sherbrooke [58]).
Algorithm:
1. Start `S_i = 0` (or minimum from rules).
2. For each item compute marginal benefit per cost: `δ_i = [EBO_i(S_i) − EBO_i(S_i + 1)] / v_i` (or fill-rate gain × λ_i / v_i).
3. Increment the item with largest δ_i; update; repeat until budget exhausted or target reached.
Because EBO is convex decreasing in S for Poisson/NB, greedy yields points on the efficient frontier (exactly optimal at the frontier points). Output: **cost vs service curve** for management — very high value for a planning product.
Complexity: use a priority heap; O(N log N × increments).

### 4.14 System availability optimization

For a system with Z_j installed of part j per system and N systems, approximate availability [58]:
`A ≈ Π_j (1 − EBO_j(S_j) / (N Z_j))^{Z_j}`
Maximize `log A` via greedy marginal analysis on `Δ log A / v_j`. Van Houtum & Kranenburg [63] give Lagrangian/column-generation methods for multi-location with availability constraints; Basten & van Houtum [64] review. Needed only for customers with fleet/uptime contracts (e.g. performance-based logistics); mid-market typically uses fill rate.

---

## 5. Multi-echelon

### 5.1 METRIC (Sherbrooke 1968 [65])

Two-echelon (depot 0, bases j), repairables, Poisson demand λ_j, one-for-one (S−1,S).
- Depot demand `λ_0 = Σ_j λ_j (1 − r_j)` (r_j = fraction repaired at base).
- Depot pipeline mean `μ_0 = λ_0 T_0` → `EBO_0(S_0)` via Poisson.
- Average depot delay `= EBO_0(S_0) / λ_0` (Little's law).
- Base pipeline mean `μ_j = λ_j [ r_j T_j + (1 − r_j)(O_j + EBO_0(S_0)/λ_0) ]` (O_j = order-and-ship time from depot).
- `EBO_j(S_j)` from Poisson(μ_j). Optimize S_0, S_j jointly by marginal analysis on system EBO per cost.
For consumables: set r_j = 0, T_0 = supplier lead time.

### 5.2 VARI-METRIC (Slay 1984; Sherbrooke 1986 [66])

METRIC assumes base pipeline is Poisson — underestimates variance because depot delays are correlated. VARI-METRIC matches two moments. With `f_j = λ_j (1 − r_j) / λ_0`:
- `E[X_j] = λ_j r_j T_j + λ_j (1 − r_j) O_j + f_j EBO_0`
- `Var[X_j] = λ_j r_j T_j + λ_j (1 − r_j) O_j + f_j (1 − f_j) EBO_0 + f_j² VBO_0`
Fit NB to (E, Var). VBO_0 = variance of depot backorders. Considerably more accurate than METRIC for low depot stock.

### 5.3 Graves (1985 [67])

Exact/approximate multi-echelon model with NB approximation of base outstanding orders (two-moment fit) and a heuristic for the depot; results close to VARI-METRIC. Also Axsäter's exact recursive evaluation for one-for-one policies [57].

### 5.4 Echelon stock (Clark & Scarf 1960 [68])

Echelon inventory position at a node = IP at the node + all downstream IPs. Serial systems: echelon base-stock policies are optimal. Used in practical DRP: DC reorders on echelon (network) IP so that stock sitting at branches suppresses DC orders — prevents DC from over-ordering when branches are full. Pitfall: echelon policy needs allocation rules at DC when stock is short (fair-share or priority allocation).

### 5.5 Lateral transshipment and emergency shipments

- **Emergency (reactive) transshipment**: when a branch stocks out, fill from a sister branch (pooling) or emergency supplier/DC shipment. Models: Lee [69], Axsäter [70], Wong et al.; review Paterson et al. [71].
- Effect: pooling groups of nearby locations raises effective fill rate; stock levels can be lowered. Approximate modelling: treat the pool's shortage as overflow to other members (Erlang-loss-like approximations).
- Decision rule (practice): transship if `(emergency supplier cost − transshipment cost) + downtime cost saving > 0` and donor keeps IP ≥ its own reorder point (donor protection).
- **Emergency-order supply mode**: dual sourcing with regular (long, cheap) and expedited (short, expensive) lead times; "dual-index" policies (Veeraraghavan & Scheller-Wolf) are optimal-ish; practical: expedite only when projected stockout before regular receipt for Vital items.

### 5.6 Practical 2-echelon DC–branch heuristics (mid-market)

1. **Forecast at branch** from branch end demand; **DC forecast** = Σ branch forecasts + DC direct demand (not branch order history).
2. **Branch policy**: (R, s, S) with R = DC delivery frequency, L = DC→branch transit; branch safety stock protects branch LT only *plus* expected DC delay `EBO_0/λ_0` (METRIC idea) when DC service < ~99%.
3. **DC policy**: (R, s, S) on supplier cycle with L = supplier LT; DC safety stock sized on **aggregated** branch variance: `σ_DC = sqrt(Σ σ_j²)` (independent) — risk pooling.
4. **DC service target** high (e.g. 95–98%) because DC stockouts propagate to all branches; branch targets set by class.
5. **Slow movers stocked centrally only** (DC) with fast branch replenishment (next-day); branches stock only by hits rule (4.12).
6. **Allocation under shortage**: DC allocates to branches by priority (VOR/backorders first) then fair-share (equal projected days of cover).
7. Periodically calibrate with a simulation of the two-echelon system to check realized branch fill rates.

### 5.7 Rebalancing / redeployment of excess

- Excess at location j: `E_j = OH_j − (S_j + buffer)` where buffer covers e.g. 1–3 months of forecast *(practice)*; deficit at k: `D_k = s_k − IP_k` (or projected shortage).
- Transfer if `value of avoided purchase/obsolescence + service gain > transfer cost + handling`. Solve as transportation problem (min cost flow) or greedy by value.
- Constraints: donor retains ≥ S_j; minimum transfer value; no ping-pong (item not transferred again within N months); pack/handling units.
- Return excess to DC or to supplier (stock rotation allowances) as alternatives.

---

## 6. Repairables (rotables)

### 6.1 Repair pipeline

For a rotable pool: failures λ; fraction repairable `(1 − c)` where c = **condemnation rate** (scrap/beyond economic repair).
Pipeline mean: `μ = λ [ (1 − c) T_repair + c T_buy ]` — repaired units return after repair turnaround time (TAT, including removal, transport to repair shop, repair, test, return); condemned units must be replaced by new purchases.
Pool size S via Poisson/NB on μ (Palm), same EBO/fill-rate formulas (4.8). Multi-echelon: METRIC with r_j = base repair fraction.

### 6.2 Core returns

Exchange units: customer receives a reman/repaired unit and returns a core.
- Core return rate `ρ` (fraction of issued units whose cores come back), return lag distribution.
- Net new-buy requirement = demand − (returns × (1 − c) arriving within horizon).
- Remanufacturing inventory models: Fleischmann et al. [72]; Van der Laan et al. push/pull remanufacturing policies. Pitfall: core return timing is highly variable; model returns as a separate stochastic supply with its own lead-time distribution.

### 6.3 Repair vs buy

Repair if `c_repair + h v × (TAT_repair − L_buy)⁺ + reliability penalty < c_new` (compare expected cost per serviceable unit, including lower MTBF of repaired units if applicable). Also: repair capacity constraints (repair shop as queue; TAT grows with load — M/G/c).

### 6.4 Rotable pool management

Track serial numbers, states (serviceable, unserviceable awaiting repair, in repair, in transit, condemned), TAT per repair vendor, NFF (no fault found) rate. Pool size reviewed periodically; unserviceable backlog is a key KPI.

---

## 7. Lifecycle

### 7.1 Initial provisioning

For parts of new equipment with no history:
- **Reliability-based**: expected failures over horizon t: `λ t = N × Z × U × t / MTBF` (N units, Z installed per unit, U utilization); stock S from Poisson(λ × resupply time) to target fill rate or availability. MTBF from supplier/engineering (often optimistic by 2–3× in practice).
- **Analogue**: 1.10 / 3.11.
- **Recommended Spare Parts List (RSPL)** from OEM as starting point; apply hits/criticality filters.
- Commissioning / warranty period demand separately (infant mortality).
- Review after first 3–6 months of actual demand; Bayesian updating (Poisson–gamma conjugate: prior λ ~ Gamma(a, b) from analogue/reliability, posterior after x demands in time t: Gamma(a + x, b + t)) — blends prior and data naturally [73].

### 7.2 Last time buy (LTB / final order)

At supplier EOL, buy one quantity Q_LTB to cover the remaining service period (often 7–15 years, contractual).
- Demand model: installed base decay `N(t)` and failure rate → `λ(t)`; cumulative demand over remaining horizon `M = ∫_0^H λ(t) dt`, distributed Poisson(M) (or NB for uncertainty in λ).
- Newsvendor: `P(D_H ≤ Q) = (c_u) / (c_u + c_o)`, with `c_u` = cost per unit short (alternative sourcing: redesign, repair, used-part harvesting, expensive re-manufacture) and `c_o` = unit cost + holding over horizon − salvage [41][42][74].
- Include: returns/repair as alternative supply (Teunter & Fortuin [41]; van Kooten & Tan [75]), holding cost over long horizon, discounting, obsolescence of the equipment itself (installed base drop), and remaining stock/on-order.
- Behfard et al. [76] LTB with repair and phase-out; Pourakbar et al. [77] end-of-life inventory with alternative policies.
- Pitfall: point forecasts over 10 years are highly uncertain; present Q_LTB as a range with risk curve.

### 7.3 Obsolescence and dead stock

- Detect: no demand in N months (e.g. 24), no installed base, superseded not interchangeable, EOL model.
- Estimate obsolescence risk: van Jaarsveld & Dekker [78] — estimate probability that an item becomes obsolete from demand-data inter-arrival patterns; include in holding cost (`h = cost of capital + storage + obsolescence rate`). For spare parts, obsolescence rate often 5–20%/yr of value *(practice)*.
- Actions: stop replenishment, return to supplier (rotation allowance), transfer to locations with demand, discount/sell, scrap. Provisioning for E&O is a finance KPI.
- TSB forecasting (3.6) decays forecasts toward zero during zero runs — early warning.

### 7.4 Phase-in / phase-out

- Phase-out (one-way supersession): stop ordering old part; forecast total demand on new part; project old-part depletion (`OH_old / F`); start ordering new part to arrive when old runs out (timed phase-in). If old part is not interchangeable, keep it in its own lifecycle (LTB).
- Phase-in (new part): initial stock by analogue; staged branch roll-out; transfer remaining old-part stock to use-up locations.
- Pitfall: ordering both old and new during overlap (double stock) — the engine must see the supersession chain in the net requirements.

---

## 8. Supplier side

### 8.1 Lead-time estimation from receipt history

- Observed LT per receipt: `LT = receipt_date (goods available/put-away) − PO_date (order placed)`; per supplier × part (or supplier × part-category when sparse), in **calendar or working days consistently**.
- Also compute **promised vs actual** (confirmation date vs receipt) for supplier reliability, and **internal lead time** components (PO approval delay, receiving/put-away time, transit).
- Partial receipts: LT for each partial line; use the receipt that completes 90–100% of qty for "complete" LT, first receipt for "first availability".
- Robust statistics: trimmed mean / median; drop outliers (e.g. POs placed with future requested date — use requested date as start, not order date).
- Hierarchical fallback: part-supplier (≥ 5 receipts) → supplier-category → supplier → master-data quoted LT *(practice)*. Exponentially weighted update (α ≈ 0.1–0.2) to follow drift.
- Use requested delivery date when the PO was deliberately placed early — otherwise LT is overstated.

### 8.2 Lead-time variability

`σ_L` from same data; or use the empirical LT distribution in the LTD compounding (4.7). Seasonal LT (e.g. Chinese New Year, monsoon) → time-dependent LT.

### 8.3 OTIF and supplier performance

- **OTIF** = fraction of PO lines received on time (within tolerance window, e.g. −2/+0 days of confirmed date) **and** in full (qty within tolerance). Define against confirmed date *and* against originally requested date (two KPIs).
- Also: fill rate from supplier (unit), average delay, backorder age at supplier, quality reject rate.
- Feed σ_L and OTIF into safety stock (either via σ_L or via an explicit supplier-reliability buffer).

### 8.4 Supplier-specific MOQ and pricing

Per supplier-part: MOQ, order multiple (pack), price breaks (quantity discounts → modify EOQ with all-units discount algorithm [13]), minimum order value per PO, freight thresholds, order days. Joint replenishment to reach free-freight value.

### 8.5 Multi-sourcing

- Primary/secondary sources with allocation percentages or rules (primary unless lead time/availability insufficient).
- OEM vs aftermarket/alternate brands — treat as alternates with own LT/cost; demand stays on the part (or interchangeable group).
- Dual sourcing for emergency (5.5). Data: `supplier_priority, share %, LT, cost, MOQ` per source.

---

## 9. KPIs

| KPI | Definition | Notes |
|---|---|---|
| **Line fill rate** | Order lines filled completely from stock at the requested location / total lines | Headline service KPI |
| **Unit fill rate** | Units filled / units demanded | |
| **Order fill rate** | Orders fully filled / orders | Multi-line orders |
| **First-pass (first-time) fill rate** | Filled from the **first** (requested) location without transfer/emergency | Measures stocking-decision quality |
| **Network fill rate** | Filled within agreed time from any network location | Customer view |
| **Backorders** | Count/value/age of open backorder lines; average backorder duration | Age buckets: 0–2, 3–7, 8–30, 30+ days |
| **Availability / VOR rate** | Equipment waiting-on-parts time; VOR orders | Service-contract KPI |
| **Inventory turns** | Annual COGS (issues at cost) / average inventory value | Or days of supply = 365/turns |
| **Excess %** | Value of stock above max (or > N months of forecast) / total | |
| **Obsolete / dead %** | Value with no demand in 24 months (or flagged obsolete) / total | E&O = excess + obsolete |
| **Inventory investment** | Total value, by class, vs budget/target | |
| **Emergency order %** | Emergency/expedited PO lines (or value) / total PO lines | Also emergency freight cost |
| **Forecast accuracy/bias** | RMSSE, scaled bias, PIS per class (3.17) | |
| **Planner touchless rate** | Suggested orders released without manual change / total suggestions | Automation KPI; target 80–95% *(practice)* |
| **Override rate & FVA** | Share of forecasts/parameters overridden; FVA = error(stat) − error(final) | Gilliland [79]; Fildes et al. [80] |
| **Supplier OTIF / LT adherence** | (8.3) | |
| **Stock-out rate** | SKU-locations with OH = 0 and demand pending / stocked SKU-locations | |

**Forecast Value Added (FVA)** [79]: measure accuracy at each step (naive → statistical → planner override → consensus). FVA of a step = metric(previous) − metric(step). Negative FVA steps should be removed or restricted. Fildes et al. [80]: large and downward adjustments tend to add value; small, frequent, upward adjustments typically destroy it.

---

## 10. Automation

### 10.1 Exception thresholds

| Exception | Trigger (defaults *(practice)*) |
|---|---|
| **Forecast bias** | Tracking signal `TS = Σ e_t / MAD_t` outside ±4 (±6 for noisy); or Trigg's smoothed signal `|E_t / M_t| > 0.5–0.7` (E, M exponentially smoothed error and absolute error, α ≈ 0.1–0.2) [81] |
| **Forecast jump** | New forecast differs > 30–50% from last cycle and value impact > threshold |
| **Projected stockout** | Projected IP < 0 (or < s) within L for Vital/A items with no open PO in time |
| **Excess** | OH > max + N months of forecast; value > threshold |
| **Parameter change** | s/S change > 20% and value > threshold |
| **Data** | Missing LT, missing cost, supersession cycle, UoM mismatch, negative demand, history gap |
| **Demand spike** | Outlier (1.6) on high-value part |
| **Supplier** | PO past due, OTIF drop, LT drift > 25% |
| **Lifecycle** | No demand 12 months on stocked item; new part without analogue |

Rank exceptions by **value at risk** (e.g. shortage value × criticality, excess value) so planners work the top of the list; suppress duplicates and repeated exceptions already acknowledged.

### 10.2 Auto-approval rules

Release suggested orders automatically when: no open exception on the SKU; order value < threshold (by class/supplier); quantity within ±X% of the last similar order or of forecast × cover; supplier on approved list; not in phase-out. Everything else to a review queue. Track touchless rate and post-hoc error of auto-approved orders.

### 10.3 Parameter stability and nervousness dampening

Recomputing s/S every run causes "system nervousness" (Sridharan et al. [82]; Kazan et al. [83]): orders churn, planners lose trust.
- **Hysteresis/dead band**: update min/max only if change > max(1 unit, 10–20%) *(practice)*.
- **Smoothing**: `param_new = w · param_calc + (1 − w) · param_old`, w = 0.3–0.5.
- **Rate limit**: cap change per cycle (e.g. ±25%) except on lifecycle events.
- **Recompute frequency**: parameters monthly (or on event), order proposals daily/weekly.
- **Model persistence**: keep selected forecasting method ≥ 3–6 months unless significant degradation (3.15).
- Stock/no-stock hysteresis (4.12).

### 10.4 Frozen horizon

- Within frozen horizon (e.g. inside supplier LT / confirmed POs), do not reschedule or cancel automatically; only expedite suggestions for Vital shortages. Slushy zone: reschedule suggestions require approval. Free zone: engine plans freely.
- Frozen horizons reduce nervousness at the cost of responsiveness; typical: frozen = confirmed POs; slushy = until next review.

### 10.5 Override management and decay

- Store every override with: user, timestamp, target (forecast/parameter/order), old value, new value, reason code (promotion, known project, customer info, recall, data error, "gut"), **start and end date**.
- **Expiry**: all overrides expire by default (e.g. 3 months for forecast overrides, 6–12 for parameter overrides) *(practice)*.
- **Decay**: `F_final(t) = F_stat(t) + (O − F_stat(t)) × δ^{(t − t_0)}` with δ ≈ 0.5–0.8 per period, or linear fade over the override window — so stale overrides fade back to the statistical forecast.
- **Lock** overrides for known future events (recall campaigns) as separate planned-demand entries rather than forecast edits.
- Measure FVA per user/reason; restrict override rights for classes where FVA is negative.

---

## 11. Pitfall checklist (cross-cutting)

1. Forecasting shipments instead of demand (censoring, wrong dates).
2. Padding pre-introduction history with zeros.
3. Supersession not rolled up → new part looks new; old part stocked in parallel.
4. Counting transfers as demand (double counting network demand).
5. Normal distribution for slow movers (negative LTD, wrong tails).
6. Using demand σ instead of forecast-error σ; ignoring lead-time variability.
7. Using CSL as target for intermittent items (met trivially).
8. Classic fill-rate formula for intermittent/lumpy demand without conditioning on occurrence [61].
9. Computing s before MOQ/pack rounding.
10. Evaluating forecasts with MAPE/MAE (favors zero forecasts).
11. Per-SKU optimization of smoothing constants on sparse data (overfit).
12. Ignoring parameter-estimation uncertainty with short histories [56].
13. DC forecast from branch orders (bullwhip).
14. Model switching and parameter churn each run (nervousness).
15. Overrides without expiry.
16. Lead time in calendar days mixed with demand in working-day buckets.
17. UoM mismatches (issue vs purchase unit).
18. Cleansing genuine lumps away → emergency orders.
19. Highest service targets on high-value A items (cost-inefficient) [9].
20. Not tagging planned/campaign demand separately → forecast inflated after a recall.

---

## 12. Minimum viable method set for a mid-market release, and the exact data fields each method needs

Target: a mid-market dealer/distributor network (1 DC + N branches, 10k–200k SKUs, mostly consumable parts, ERP-level data quality). The MVP deliberately excludes METRIC/VARI-METRIC optimization, repairables, IoT, ML, LTB optimization and system-availability optimization — these are phase-2 add-ons.

### 12.1 MVP method set

| # | Area | MVP method | Why this one |
|---|---|---|---|
| M1 | Demand prep | Request-date demand history per SKU-location (daily stored, monthly bucket; weekly for top-velocity), stream tagging, returns netting to original bucket, transfer exclusion, history start date, zero vs missing | Foundation; prevents the biggest biases |
| M2 | Supersession | Chain resolution to terminal part with ratio + effective date + interchangeability; history roll-up; use-up of old stock | Service parts are unusable without it |
| M3 | Outliers | Robust z (MAD, 3.5) on non-zero sizes; winsorize with audit trail; campaign demand excluded | Simple, explainable |
| M4 | Classification | Value ABC + hits (FMR) + SBC (ADI 1.32 / CV² 0.49) + lifecycle stage + VED (master data) | Drives method and targets |
| M5 | Forecasting | By SBC class: smooth → SES / damped Holt (+ group seasonal indices where ≥ 24 months); erratic/intermittent/lumpy → SBA; decline/obsolescence risk → TSB; very slow (< 5 non-zero) → Poisson rate estimate; new parts → analogue blend. Class-level fixed/pooled parameters | Robust, literature-backed, explainable |
| M6 | Backtest & metrics | Rolling-origin, 12 origins; RMSSE, scaled bias, PIS; inventory simulation of achieved fill rate vs stock | Mean-based and inventory-relevant |
| M7 | Distribution of LTD | Normal for high-volume (μ_LTD ≥ ~20 & CV_LTD < 0.5); NB/Poisson (VMR fit, Adan et al.) otherwise; LT variability compounded | Correct tails for slow movers |
| M8 | Policy | (R, s, S) min/max: s from fill-rate target (discrete EBO formula, or normal G(k)), S = s + max(EOQ, MOQ) rounded to pack, capped months-of-supply; base-stock S−1,S for slow expensive items | ERP-native, fits dealer ordering cycles |
| M9 | Service targets | Class matrix (VED × ABC) with cheap-item-higher-target principle; configurable | Simple governance |
| M10 | Stock / no-stock | Hits rule with hysteresis + break-even check + Vital override | Controls branch breadth |
| M11 | Budget allocation | Greedy marginal allocation producing cost-vs-fill-rate curve (single-echelon, per location) | High perceived value, simple |
| M12 | 2-echelon | DC–branch heuristic (5.6): DC forecast = Σ branch forecasts; DC SS on pooled σ; branch LT = DC transit + DC delay; priority/fair-share allocation | Covers 90% of multi-echelon value without METRIC |
| M13 | Rebalancing | Excess/deficit matching greedy with donor protection and anti-ping-pong | Reduces E&O quickly |
| M14 | Lead time | Receipt-history LT per supplier-part with hierarchical fallback, median + σ_L, OTIF | Replaces stale master-data LT |
| M15 | Lifecycle | Phase-in/phase-out timing; dead-stock detection (no demand 24 months); simple LTB = Poisson/NB quantile of cumulative decayed demand (exponential decline fit) | Common dealer need at model change |
| M16 | KPIs | Line/unit/first-pass fill rate, backorders & age, turns, excess/obsolete %, emergency order %, touchless rate, FVA | |
| M17 | Automation | Tracking-signal and value-ranked exceptions, auto-approval thresholds, dead-band + smoothing on parameters, frozen horizon = confirmed POs, overrides with reason/expiry/decay | Planner productivity & trust |

### 12.2 Exact data fields per method

**Master data (shared by all methods)**

| Entity | Fields |
|---|---|
| Part | `part_id, part_number, description, part_family/group, uom_stock, uom_purchase, uom_conversion, unit_cost (standard/moving avg), currency, criticality_ved, stockable_flag, lifecycle_status, introduction_date, eol_date, obsolete_flag, hazardous/shelf_life (optional)` |
| Location | `location_id, type (DC/branch), parent_location_id (supply source), calendar_id, region` |
| Part-location | `part_id, location_id, stock_flag, min, max, review_period_days, service_target, planner_id, history_start_date, abc_value, abc_hits, sbc_class, lifecycle_stage, manual_lock_flags` |
| Calendar | `calendar_id, date, is_working_day` (per location and per supplier) |
| Supersession | `old_part_id, new_part_id, ratio, effective_date, interchangeability (TWO_WAY/ONE_WAY/NONE), use_up_flag, created_at` |
| Supplier-part | `supplier_id, part_id, priority, share_pct, quoted_lead_time_days, moq, order_multiple (pack), price, price_breaks (qty, price), min_order_value, order_days, active_flag` |
| Model / installed base (for analogue & LTB) | `model_id, part_id (fitment), qty_per_unit, launch_date, production_end_date, units_in_field by month (or sales/registrations by month), analogue_part_id` |

**Transactional data**

| Transaction | Fields |
|---|---|
| Demand line (request) | `demand_line_id, part_id (as requested), location_id (requesting), request_datetime, qty_requested, qty_filled_immediately, qty_backordered, qty_lost (if captured), fill_source_location_id, fill_datetime, stream (PAID/WORKSHOP/WARRANTY/INTERNAL/EMERGENCY/CAMPAIGN), customer_id / order_id (for order fill rate), emergency_flag, substituted_part_id` |
| Return | `return_line_id, original_demand_line_id, part_id, location_id, return_date, qty, return_type (CUSTOMER/CORE/WARRANTY/STOCK_ROTATION/MISPICK)` |
| Transfer | `transfer_id, part_id, from_location_id, to_location_id, qty, ship_date, receipt_date, reason (REPLENISHMENT/REBALANCE/EMERGENCY)` |
| Stock snapshot | `part_id, location_id, date, on_hand, allocated, in_transit, blocked/quarantine` (daily; needed for stockout/censoring and turns) |
| Purchase order line | `po_line_id, supplier_id, part_id, location_id, order_date, requested_date, confirmed_date, qty_ordered, qty_received, status, emergency_flag` |
| Receipt | `receipt_id, po_line_id, receipt_date (available-to-use), qty_received, qty_rejected` |
| Planned demand | `part_id, location_id, date, qty, source (CAMPAIGN/RECALL/PROJECT), campaign_id` |
| Override | `override_id, object_type (FORECAST/PARAMETER/ORDER), part_id, location_id, user_id, created_at, old_value, new_value, reason_code, valid_from, valid_to, decay_rate` |

**Method → required fields**

| Method | Required fields (beyond part/location keys) |
|---|---|
| M1 Demand history | demand line: `request_datetime, qty_requested, stream, location_id (requesting)`; returns: `original_demand_line_id, return_type, qty`; transfers: `reason` (to exclude); part-location `history_start_date`; calendar `is_working_day`; stock snapshot `on_hand` (for censoring flag) |
| M2 Supersession | `old_part_id, new_part_id, ratio, effective_date, interchangeability, use_up_flag`; on-hand of old part |
| M3 Outliers | demand size series; `stream`, planned-demand `campaign_id` |
| M4 Classification | 12-month `qty × unit_cost`; demand line count (hits); bucketed series (ADI, CV²); `criticality_ved`; `introduction_date, eol_date`, supersession status |
| M5 Forecasting | bucketed cleansed demand, `sbc_class`, `lifecycle_stage`, `part_family` (group seasonality), `analogue_part_id` + installed base (new parts), planned demand |
| M6 Backtest | full bucketed history ≥ 24 buckets; forecast snapshots per origin (store forecast history: `part, location, forecast_date, bucket, value, method`) |
| M7 LTD distribution | forecast mean, forecast-error RMSE (from forecast history), non-zero size variance, `lead_time mean & σ` (M14), `review_period_days` |
| M8 Policy | LTD distribution, `service_target`, `unit_cost`, holding-cost rate (global/class), ordering cost (global/supplier), `moq, order_multiple`, max months-of-supply cap, `review_period_days` |
| M9 Service targets | `abc_value, criticality_ved` (+ optional shortage cost) |
| M10 Stock/no-stock | hits (12 months, per quarter), `criticality_ved`, `unit_cost`, emergency cost/premium, upstream LT and fill rate |
| M11 Budget allocation | per item EBO curve (from M7), `unit_cost`, budget per location |
| M12 2-echelon | `parent_location_id`, DC→branch transit LT and delivery days, branch forecasts, DC achieved fill rate (for delay), backorder priorities |
| M13 Rebalancing | on-hand, max, forecast per location; transfer cost matrix (location × location, per line/value); last transfer date per part-location |
| M14 Lead time | PO line: `order_date, requested_date, confirmed_date, qty_ordered`; receipts: `receipt_date, qty_received`; supplier calendar; `quoted_lead_time_days` fallback |
| M15 Lifecycle / LTB | `eol_date`, production end, installed base or decline fit window, remaining service obligation (years), holding cost, salvage value, alternative-sourcing cost |
| M16 KPIs | demand lines with `qty_filled_immediately, fill_source_location_id, fill_datetime`; backorder open/close dates; stock snapshots valued at cost; COGS (issues × cost); PO `emergency_flag`; order-proposal log (`suggested_qty, released_qty, released_by, auto_flag`); forecast history + override log |
| M17 Automation | tracking-signal state (smoothed error, MAD) per SKU-location; parameter history (`param, value, effective_date`); thresholds config (by class/supplier); confirmed PO list (frozen horizon); override log with `valid_to, decay_rate` |

**Global configuration parameters (with defaults)**
`bucket = MONTH`, `history_window = 24–36 months`, `sbc_adi_cut = 1.32`, `sbc_cv2_cut = 0.49`, `alpha_intermittent = 0.1`, `tsb_alpha = 0.2, tsb_beta = 0.05`, `ses_alpha = 0.2`, `holt_phi = 0.9`, `outlier_mad_z = 3.5`, `normal_switch_min_ltd = 20`, `holding_rate = 20–30%/yr`, `max_months_supply = 6`, `hits_stock_branch = 4/12m (remove < 2)`, `dead_stock_months = 24`, `param_dead_band = 15%`, `param_smoothing_w = 0.5`, `ts_limit = ±4`, `override_expiry = 3 months`, `rebalance_min_value`, `auto_approve_max_value` (by class).

---

## References

1. Hu, Q., Boylan, J.E., Chen, H., Labib, A. (2018). OR in spare parts management: A review. *European Journal of Operational Research* 266(2), 395–414.
2. Boylan, J.E., Syntetos, A.A. (2021). *Intermittent Demand Forecasting: Context, Methods and Applications*. Wiley.
3. Lee, H.L., Padmanabhan, V., Whang, S. (1997). Information distortion in a supply chain: the bullwhip effect. *Management Science* 43(4), 546–558.
4. Nahmias, S. (1994). Demand estimation in lost sales inventory systems. *Naval Research Logistics* 41(6), 739–757.
5. Conrad, S.A. (1976). Sales data and the estimation of demand. *Operational Research Quarterly* 27(1), 123–127.
6. Iglewicz, B., Hoaglin, D.C. (1993). *How to Detect and Handle Outliers*. ASQC Quality Press.
7. Nikolopoulos, K., Syntetos, A.A., Boylan, J.E., Petropoulos, F., Assimakopoulos, V. (2011). An aggregate–disaggregate intermittent demand approach (ADIDA) to forecasting. *Journal of the Operational Research Society* 62(3), 544–554.
8. Boylan, J.E., Babai, M.Z. (2016). On the performance of overlapping and non-overlapping temporal demand aggregation approaches. *International Journal of Production Economics* 181, 136–144.
9. Teunter, R.H., Babai, M.Z., Syntetos, A.A. (2010). ABC classification: service levels and inventory costs. *Production and Operations Management* 19(3), 343–352.
10. Flores, B.E., Whybark, D.C. (1986). Multiple criteria ABC analysis. *International Journal of Operations & Production Management* 6(3), 38–46.
11. Ramanathan, R. (2006). ABC inventory classification with multiple-criteria using weighted linear optimization. *Computers & Operations Research* 33(3), 695–700.
12. Ng, W.L. (2007). A simple classifier for multiple criteria ABC analysis. *European Journal of Operational Research* 177(1), 344–353.
13. Silver, E.A., Pyke, D.F., Thomas, D.J. (2017). *Inventory and Production Management in Supply Chains*, 4th ed. CRC Press.
14. Syntetos, A.A., Boylan, J.E., Croston, J.D. (2005). On the categorization of demand patterns. *Journal of the Operational Research Society* 56(5), 495–503.
15. Kostenko, A.V., Hyndman, R.J. (2006). A note on the categorization of demand patterns. *Journal of the Operational Research Society* 57(10), 1256–1257.
16. Petropoulos, F., Kourentzes, N. (2015). Forecast combinations for intermittent demand. *Journal of the Operational Research Society* 66(6), 914–924.
17. Teunter, R.H., Syntetos, A.A., Babai, M.Z. (2011). Intermittent demand: linking forecasting to inventory obsolescence. *European Journal of Operational Research* 214(3), 606–615.
18. Johnston, F.R., Boylan, J.E. (1996). Forecasting for items with intermittent demand. *Journal of the Operational Research Society* 47(1), 113–121.
19. Teunter, R.H., Sani, B. (2009). On the bias of Croston's forecasting method. *European Journal of Operational Research* 194(1), 177–183.
20. Gardner, E.S., McKenzie, E. (1985). Forecasting trends in time series. *Management Science* 31(10), 1237–1246.
21. Dekker, M., van Donselaar, K., Ouwehand, P. (2004). How to use aggregation and combined forecasting to improve seasonal demand forecasts. *International Journal of Production Economics* 90(2), 151–167.
22. Croston, J.D. (1972). Forecasting and stock control for intermittent demands. *Operational Research Quarterly* 23(3), 289–303.
23. Syntetos, A.A., Boylan, J.E. (2005). The accuracy of intermittent demand estimates. *International Journal of Forecasting* 21(2), 303–314.
24. Shale, E.A., Boylan, J.E., Johnston, F.R. (2006). Forecasting for intermittent demand: the estimation of an unbiased average. *Journal of the Operational Research Society* 57(5), 588–592.
25. Babai, M.Z., Syntetos, A.A., Teunter, R.H. (2014). Intermittent demand forecasting: an empirical study on accuracy and the risk of obsolescence. *International Journal of Production Economics* 157, 212–219.
26. Levén, E., Segerstedt, A. (2004). Inventory control with a modified Croston procedure and Erlang distribution. *International Journal of Production Economics* 90(3), 361–367.
27. Snyder, R.D., Ord, J.K., Beaumont, A. (2012). Forecasting the intermittent demand for slow-moving inventories: a modelling approach. *International Journal of Forecasting* 28(2), 485–496.
28. Nikolopoulos et al. (2011) — see [7].
29. Kourentzes, N., Petropoulos, F., Trapero, J.R. (2014). Improving forecasting by estimating time series structural components across multiple frequencies. *International Journal of Forecasting* 30(2), 291–302.
30. Willemain, T.R., Smart, C.N., Schwarz, H.F. (2004). A new approach to forecasting intermittent demand for service parts inventories. *International Journal of Forecasting* 20(3), 375–387.
31. Syntetos, A.A., Babai, M.Z., Gardner, E.S. (2015). Forecasting intermittent inventory demands: simple parametric methods vs. bootstrapping. *Journal of Business Research* 68(8), 1746–1752.
32. Zhu, S., Dekker, R., van Jaarsveld, W., Renjie, R.W., Koning, A.J. (2017). An improved method for forecasting spare parts demand using extreme value theory. *European Journal of Operational Research* 261(1), 169–181.
33. Syntetos, A.A., Babai, M.Z., Altay, N. (2012). On the demand distributions of spare parts. *International Journal of Production Research* 50(8), 2101–2117.
34. Dunsmuir, W.T.M., Snyder, R.D. (1989). Control of inventories with intermittent demand. *European Journal of Operational Research* 40(1), 16–21.
35. Adan, I., van Eenige, M., Resing, J. (1995). Fitting discrete distributions on the first two moments. *Probability in the Engineering and Informational Sciences* 9(4), 623–632.
36. Porras, E., Dekker, R. (2008). An inventory control system for spare parts at a refinery: an empirical comparison of different re-order point methods. *European Journal of Operational Research* 184(1), 101–132.
37. Van der Auweraer, S., Boute, R.N., Syntetos, A.A. (2019). Forecasting spare part demand with installed base information: a review. *International Journal of Forecasting* 35(1), 181–196.
38. Dekker, R., Pinçe, Ç., Zuidwijk, R., Jalil, M.N. (2013). On the use of installed base information for spare parts logistics: a review of ideas and industry practice. *International Journal of Production Economics* 143(2), 536–545.
39. Jalil, M.N., Zuidwijk, R.A., Fleischmann, M., van Nunen, J.A.E.E. (2011). Spare parts logistics and installed base information. *Journal of the Operational Research Society* 62(3), 442–457.
40. Topan, E., Eruguz, A.S., Ma, W., van der Heijden, M.C., Dekker, R. (2020). A review of operational spare parts service logistics in service control towers. *European Journal of Operational Research* 282(2), 401–414.
41. Teunter, R.H., Fortuin, L. (1999). End-of-life service. *International Journal of Production Economics* 59(1–3), 487–497.
42. Teunter, R.H., Klein Haneveld, W.K. (2002). Inventory control of service parts in the final phase. *European Journal of Operational Research* 137(3), 497–511.
43. Makridakis, S., Spiliotis, E., Assimakopoulos, V. (2022). M5 accuracy competition: results, findings, and conclusions. *International Journal of Forecasting* 38(4), 1346–1364.
44. Salinas, D., Flunkert, V., Gasthaus, J., Januschowski, T. (2020). DeepAR: probabilistic forecasting with autoregressive recurrent networks. *International Journal of Forecasting* 36(3), 1181–1191.
45. Kourentzes, N. (2013). Intermittent demand forecasts with neural networks. *International Journal of Production Economics* 143(1), 198–206.
46. Van Wingerden, E., Basten, R.J.I., Dekker, R., Rustenburg, W.D. (2014). More grip on inventory control through improved forecasting: a comparative study at three companies. *International Journal of Production Economics* 157, 220–237.
47. Kourentzes, N. (2014). On intermittent demand model optimisation and selection. *International Journal of Production Economics* 156, 180–190.
48. Petropoulos, F. et al. (2022). Forecasting: theory and practice. *International Journal of Forecasting* 38(3), 705–871 (sections on intermittent demand and combinations).
49. Tashman, L.J. (2000). Out-of-sample tests of forecasting accuracy: an analysis and review. *International Journal of Forecasting* 16(4), 437–450.
50. Syntetos, A.A., Boylan, J.E. (2006). On the stock control performance of intermittent demand estimators. *International Journal of Production Economics* 103(1), 36–47.
51. Teunter, R.H., Duncan, L. (2009). Forecasting intermittent demand: a comparative study. *Journal of the Operational Research Society* 60(3), 321–329.
52. Hyndman, R.J., Koehler, A.B. (2006). Another look at measures of forecast accuracy. *International Journal of Forecasting* 22(4), 679–688.
53. Morlidge, S. (2015). Measuring the quality of intermittent demand forecasts: it's worse than we've thought! *Foresight* 37, 37–42.
54. Kolassa, S. (2016). Evaluating predictive count data distributions in retail sales forecasting. *International Journal of Forecasting* 32(3), 788–803.
55. Wallström, P., Segerstedt, A. (2010). Evaluation of forecasting error measurements and techniques for intermittent demand. *International Journal of Production Economics* 128(2), 625–636.
56. Prak, D., Teunter, R.H. (2019). A general method for addressing forecasting uncertainty in inventory models. *International Journal of Forecasting* 35(1), 224–238.
57. Axsäter, S. (2015). *Inventory Control*, 3rd ed. Springer.
58. Sherbrooke, C.C. (2004). *Optimal Inventory Modeling of Systems: Multi-Echelon Techniques*, 2nd ed. Kluwer.
59. Muckstadt, J.A. (2005). *Analysis and Algorithms for Service Parts Supply Chains*. Springer.
60. Schneider, H. (1981). Effect of service-levels on order-points or order-levels in inventory models. *International Journal of Production Research* 19(6), 615–631.
61. Teunter, R.H., Syntetos, A.A., Babai, M.Z. (2010). Determining order-up-to levels under periodic review for compound binomial (intermittent) demand. *European Journal of Operational Research* 203(3), 619–624.
62. Feeney, G.J., Sherbrooke, C.C. (1966). The (s−1, s) inventory policy under compound Poisson demand. *Management Science* 12(5), 391–411.
63. Van Houtum, G.J., Kranenburg, B. (2015). *Spare Parts Inventory Control under System Availability Constraints*. Springer.
64. Basten, R.J.I., van Houtum, G.J. (2014). System-oriented inventory models for spare parts. *Surveys in Operations Research and Management Science* 19(1), 34–55.
65. Sherbrooke, C.C. (1968). METRIC: a multi-echelon technique for recoverable item control. *Operations Research* 16(1), 122–141.
66. Sherbrooke, C.C. (1986). VARI-METRIC: improved approximations for multi-indenture, multi-echelon availability models. *Operations Research* 34(2), 311–319. (Builds on Slay, F.M. 1984, LMI working paper.)
67. Graves, S.C. (1985). A multi-echelon inventory model for a repairable item with one-for-one replenishment. *Management Science* 31(10), 1247–1256.
68. Clark, A.J., Scarf, H. (1960). Optimal policies for a multi-echelon inventory problem. *Management Science* 6(4), 475–490.
69. Lee, H.L. (1987). A multi-echelon inventory model for repairable items with emergency lateral transshipments. *Management Science* 33(10), 1302–1316.
70. Axsäter, S. (1990). Modelling emergency lateral transshipments in inventory systems. *Management Science* 36(11), 1329–1338.
71. Paterson, C., Kiesmüller, G., Teunter, R., Glazebrook, K. (2011). Inventory models with lateral transshipments: a review. *European Journal of Operational Research* 210(2), 125–136.
72. Fleischmann, M., Bloemhof-Ruwaard, J.M., Dekker, R., van der Laan, E., van Nunen, J.A.E.E., Van Wassenhove, L.N. (1997). Quantitative models for reverse logistics: a review. *European Journal of Operational Research* 103(1), 1–17.
73. Aronis, K.-P., Magou, I., Dekker, R., Tagaras, G. (2004). Inventory control of spare parts using a Bayesian approach: a case study. *European Journal of Operational Research* 154(3), 730–739.
74. Pinçe, Ç., Dekker, R. (2011). An inventory model for slow moving items subject to obsolescence. *European Journal of Operational Research* 213(1), 83–95.
75. Van Kooten, J.P.J., Tan, T. (2009). The final order problem for repairable spare parts under condemnation. *Journal of the Operational Research Society* 60(10), 1449–1461.
76. Behfard, S., van der Heijden, M.C., Al Hanbali, A., Zijm, W.H.M. (2015). Last time buy and repair decisions for spare parts. *European Journal of Operational Research* 244(2), 498–510.
77. Pourakbar, M., Frenk, J.B.G., Dekker, R. (2012). End-of-life inventory decisions for consumer electronics service parts. *Production and Operations Management* 21(5), 889–906.
78. Van Jaarsveld, W., Dekker, R. (2011). Estimating obsolescence risk from demand data to enhance inventory control — a case study. *International Journal of Production Economics* 133(1), 423–431.
79. Gilliland, M. (2010). *The Business Forecasting Deal*. Wiley (Forecast Value Added).
80. Fildes, R., Goodwin, P., Lawrence, M., Nikolopoulos, K. (2009). Effective forecasting and judgmental adjustments: an empirical evaluation and strategies for improvement in supply-chain planning. *International Journal of Forecasting* 25(1), 3–23.
81. Trigg, D.W. (1964). Monitoring a forecasting system. *Operational Research Quarterly* 15(3), 271–274.
82. Sridharan, V., Berry, W.L., Udayabhanu, V. (1987). Freezing the master production schedule under rolling planning horizons. *Management Science* 33(9), 1137–1149.
83. Kazan, O., Nagi, R., Rump, C.M. (2000). New lot-sizing formulations for less nervous production schedules. *Computers & Operations Research* 27(13), 1325–1345.

*Citation note:* references were compiled from domain knowledge without live verification in this session; volume/page numbers should be spot-checked before external publication. Items marked *(practice)* are practitioner conventions, not published optima, and should be exposed as configurable parameters.
