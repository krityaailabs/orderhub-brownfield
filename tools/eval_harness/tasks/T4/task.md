# T4: Correct the billing record layout document

`legacy/billing/docs/RECORD_LAYOUT.txt` (2017) says the three amounts in a detail record are 10 characters at positions 47–56, 57–66 and 67–76. The code writes 11 characters each. Update the document to match the code (positions 47–57, 58–68, 69–79), and note that records are space-padded to 80. Documentation only: no code changes.
