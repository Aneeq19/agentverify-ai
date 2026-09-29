# Day 6 — AgentVerify Pro demo and pilot offer

## Honest product status

AgentVerify currently has a fictional workflow-preparation app and a saved Stedi synthetic example. The public Streamlit app does **not** send an eligibility request for an arbitrary patient. The GitHub example response was recreated from observed sandbox output; it is not a raw production response. The local home-PC `stedi_mock_response.json` is a saved synthetic sandbox response and is excluded from Git.

The Stedi example reports Dental Care as NON_COVERED and includes a payer message to view the contract. It does not establish overall patient eligibility or live dental benefits. The normalized sheet leaves absent values as “Not returned by eligibility source.” The 10/10 agent evaluation and 5/5 parser tests use fictional cases and are not evidence of real payer accuracy.

## Narrow customer hypothesis

Start with a **small US dental insurance verification or remote dental billing team** that already performs authorized checks for dental offices. The buyer is its owner or operations manager; the user is the benefits verification specialist or QA lead. Your own hands-on verification experience is the advantage: you can distinguish a missing annual max, frequency or crown history from a benefit explicitly returned by a source.

This is a hypothesis to validate in conversations, not established demand. DentalXChange already offers eligibility and automated verification, Zuub offers dental benefits data via API, and pVerify offers eligibility APIs. Do not promise payer coverage, faster turnaround or cost savings until measured.

## Three-minute fictional demo

1. Open https://agentverify-ai.streamlit.app/ and state: “This is a synthetic demonstration; please do not enter real patient information.”
2. Run the fictional preparation form, showing missing-field detection and payer questions. Explain this prepares the verifier; it does not contact a payer.
3. Click **Show Stedi test example**. Point to the source label, Dental Care NON_COVERED and the exact source message.
4. Point to annual maximum, deductible, frequencies and other absent fields labeled **Not returned by eligibility source**. Explain that the human verifier would follow up through the team's authorized workflow.
5. Download the synthetic Markdown sheet. Explain that the report is a draft format for reviewer feedback, not a patient-ready verified benefits document.
6. Ask what would make this sheet usable in their actual workflow, and what data provenance/QA they require.

## Proposed validation offer

**15-minute workflow review + fictional sample sheet.** Show the demo and ask the prospective team to critique the sheet: missing fields, exceptions, payer question order and documentation format. No patient data or system access is needed.

If they want a live pilot later, propose a *separately scoped* human-reviewed workflow: their authorized staff perform payer checks; an approved process maps source evidence into a reviewable sheet; a human signs off before delivery. Agree on data handling, roles, security, access and any applicable HIPAA/BAA obligations before processing PHI. Do not run live cases in this public Streamlit demo.

Pricing: discovery call first. Ask current volume, time per case, repeat checks, QA errors and budget owner; quote only after scope and data handling are agreed. No unsupported price or savings claim.

## Five discovery questions

1. Who owns verification quality and pays for tools or outsourced help?
2. Which three dental benefit fields are most often absent or ambiguous in your current source?
3. For a crown case, what exactly must be documented before a report is acceptable?
4. What evidence, timestamps and reviewer signoff do you need?
5. Would your team trial a fictional sample and provide feedback on the format?

## Day 6 done criterion

A prospective buyer/user can watch the synthetic demo and understand its limitations, and there is a specific invitation to a 15-minute workflow review. Day 7 begins when actual prospective teams are identified and contacted with permission; outreach and demand are not yet validated.
