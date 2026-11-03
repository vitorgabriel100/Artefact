# Technical decisions and source ambiguities

This existing filename is retained to avoid leaving an obsolete document when applying
checkpoint ZIPs. The contents and submitted explanations are in English.

| Decision | Reason | Trade-off |
|---|---|---|
| Python and standard-library runtime | Small, inspectable baseline | Some validation is explicit application code |
| SQLite in memory | Local reproducible relationships and parameterized queries | Reloaded snapshots are not live inventory |
| Decimal and integer cents | Deterministic monetary calculations | Formatting remains a presentation responsibility |
| Allowlisted tool functions | Keep data access bounded | Each supported operation needs a declared contract |
| Lexical PDF retrieval with page references | Adequate starting point for eight pages | Synonyms and multilingual queries need evaluation |
| CLI first | Meets challenge interface requirements with minimal setup | Customer-friendly dialogue comes in Checkpoint 03 |
| Optional local LLM later | No mandatory paid credentials | Hardware and model behavior must be checked |

## Availability and promotions

Only `active` products with positive stock are available. Discontinued products and
upcoming products remain unavailable even with positive stock. Only `is_active=1`
promotions apply. No dates exist in the promotion CSV, so no campaign dates are inferred.
Multiple active promotions for one product fail ingestion rather than selecting one
arbitrarily. PIX gives 5% off regular prices only when no active promotion applies.
These calculations do not reserve stock or process purchases.

## Policy ambiguities

- Page 2 and page 6 give different phone/WhatsApp contact details. Retrieval includes
  both for contact questions; a future answer must distinguish source labels and flag
  uncertainty instead of silently declaring one universally correct.
- General installment terms and section 3.1 differ; the below-BRL-50 exception is also
  ambiguous. Installment calculation is not implemented or approved by this checkpoint.
- The manual does not define the regional shipping fee at exactly BRL 500.
- Orders have no actual receipt date or purchase channel. Estimated delivery is not
  receipt. Return eligibility cannot be approved automatically from these records.
- The manual is the supplied policy source, not an independently reviewed legal opinion.
- There is no ticketing integration: never claim a complaint was forwarded or a return
  approved unless an actual integration confirms it.

## Order privacy boundary

Existing ToolBox code restricts order retrieval to a customer ID supplied by the
application session, not a model argument. This is a query boundary, **not user
authentication**. A production identity flow is outside the prototype. Checkpoint 02
will validate this boundary and choose an explicitly documented demonstration flow.
Do not expose complete customer lists or accept a name alone as proof of identity.
