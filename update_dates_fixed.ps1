# Issue #8 - Team Management (Start: Jan 15, Target: Mar 1, 2026)
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: {projectId: "PVT_kwHOAlngOs4BJdL9" itemId: "PVTI_lAHOAlngOs4BJdL9zgh-LVE" fieldId: "PVTF_lAHOAlngOs4BJdL9zg5nRLQ" value: { date: "2026-01-15" }}) { projectV2Item { id }}}'
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: {projectId: "PVT_kwHOAlngOs4BJdL9" itemId: "PVTI_lAHOAlngOs4BJdL9zgh-LVE" fieldId: "PVTF_lAHOAlngOs4BJdL9zg5nRLU" value: { date: "2026-03-01" }}) { projectV2Item { id }}}'
Write-Host "✓ Issue #8 dates set"

# Issue #9 - Personnel Management (Start: Feb 1, Target: Mar 15, 2026)
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: {projectId: "PVT_kwHOAlngOs4BJdL9" itemId: "PVTI_lAHOAlngOs4BJdL9zgh-Lbg" fieldId: "PVTF_lAHOAlngOs4BJdL9zg5nRLQ" value: { date: "2026-02-01" }}) { projectV2Item { id }}}'
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: {projectId: "PVT_kwHOAlngOs4BJdL9" itemId: "PVTI_lAHOAlngOs4BJdL9zgh-Lbg" fieldId: "PVTF_lAHOAlngOs4BJdL9zg5nRLU" value: { date: "2026-03-15" }}) { projectV2Item { id }}}'
Write-Host "✓ Issue #9 dates set"

# Issue #10 - Financial System (Start: Feb 15, Target: Mar 30, 2026)
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: {projectId: "PVT_kwHOAlngOs4BJdL9" itemId: "PVTI_lAHOAlngOs4BJdL9zgh-LdU" fieldId: "PVTF_lAHOAlngOs4BJdL9zg5nRLQ" value: { date: "2026-02-15" }}) { projectV2Item { id }}}'
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: {projectId: "PVT_kwHOAlngOs4BJdL9" itemId: "PVTI_lAHOAlngOs4BJdL9zgh-LdU" fieldId: "PVTF_lAHOAlngOs4BJdL9zg5nRLU" value: { date: "2026-03-30" }}) { projectV2Item { id }}}'
Write-Host "✓ Issue #10 dates set"

# Issue #15 - Polish Features (Start: Apr 1, Target: May 1, 2026)
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: {projectId: "PVT_kwHOAlngOs4BJdL9" itemId: "PVTI_lAHOAlngOs4BJdL9zgh-L5w" fieldId: "PVTF_lAHOAlngOs4BJdL9zg5nRLQ" value: { date: "2026-04-01" }}) { projectV2Item { id }}}'
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: {projectId: "PVT_kwHOAlngOs4BJdL9" itemId: "PVTI_lAHOAlngOs4BJdL9zgh-L5w" fieldId: "PVTF_lAHOAlngOs4BJdL9zg5nRLU" value: { date: "2026-05-01" }}) { projectV2Item { id }}}'
Write-Host "✓ Issue #15 dates set"

# Issue #16 - Final Documentation (Start: Mar 15, Target: May 1, 2026)
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: {projectId: "PVT_kwHOAlngOs4BJdL9" itemId: "PVTI_lAHOAlngOs4BJdL9zgh-MHA" fieldId: "PVTF_lAHOAlngOs4BJdL9zg5nRLQ" value: { date: "2026-03-15" }}) { projectV2Item { id }}}'
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: {projectId: "PVT_kwHOAlngOs4BJdL9" itemId: "PVTI_lAHOAlngOs4BJdL9zgh-MHA" fieldId: "PVTF_lAHOAlngOs4BJdL9zg5nRLU" value: { date: "2026-05-01" }}) { projectV2Item { id }}}'
Write-Host "✓ Issue #16 dates set"

# Issue #17 - Final Presentation (Start: May 1, Target: May 10, 2026)
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: {projectId: "PVT_kwHOAlngOs4BJdL9" itemId: "PVTI_lAHOAlngOs4BJdL9zgh-MNI" fieldId: "PVTF_lAHOAlngOs4BJdL9zg5nRLQ" value: { date: "2026-05-01" }}) { projectV2Item { id }}}'
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: {projectId: "PVT_kwHOAlngOs4BJdL9" itemId: "PVTI_lAHOAlngOs4BJdL9zgh-MNI" fieldId: "PVTF_lAHOAlngOs4BJdL9zg5nRLU" value: { date: "2026-05-10" }}) { projectV2Item { id }}}'
Write-Host "✓ Issue #17 dates set"

Write-Host "`n✓ All remaining issue dates updated successfully!"
Write-Host "`nGantt chart timeline:"
Write-Host "  Midpoint (Dec 2-12, 2025): Issues #2-6, #11-14"
Write-Host "  Post-Midpoint (Dec 23 - May 10, 2026): Issues #7-10, #15-17"
