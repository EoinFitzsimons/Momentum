# Issue #8 - Team Management
gh api graphql -f query="mutation { updateProjectV2ItemFieldValue(input: {projectId: \"PVT_kwHOAlngOs4BJdL9\" itemId: \"PVTI_lAHOAlngOs4BJdL9zgh-LVE\" fieldId: \"PVTF_lAHOAlngOs4BJdL9zg5nRLQ\" value: { date: \"2026-01-15\" }}) { projectV2Item { id }}}"
gh api graphql -f query="mutation { updateProjectV2ItemFieldValue(input: {projectId: \"PVT_kwHOAlngOs4BJdL9\" itemId: \"PVTI_lAHOAlngOs4BJdL9zgh-LVE\" fieldId: \"PVTF_lAHOAlngOs4BJdL9zg5nRLU\" value: { date: \"2026-03-01\" }}) { projectV2Item { id }}}"
Write-Host "Issue #8 dates set"

# Issue #9 - Personnel Management
gh api graphql -f query="mutation { updateProjectV2ItemFieldValue(input: {projectId: \"PVT_kwHOAlngOs4BJdL9\" itemId: \"PVTI_lAHOAlngOs4BJdL9zgh-Lbg\" fieldId: \"PVTF_lAHOAlngOs4BJdL9zg5nRLQ\" value: { date: \"2026-02-01\" }}) { projectV2Item { id }}}"
gh api graphql -f query="mutation { updateProjectV2ItemFieldValue(input: {projectId: \"PVT_kwHOAlngOs4BJdL9\" itemId: \"PVTI_lAHOAlngOs4BJdL9zgh-Lbg\" fieldId: \"PVTF_lAHOAlngOs4BJdL9zg5nRLU\" value: { date: \"2026-03-15\" }}) { projectV2Item { id }}}"
Write-Host "Issue #9 dates set"

# Issue #10 - Financial System
gh api graphql -f query="mutation { updateProjectV2ItemFieldValue(input: {projectId: \"PVT_kwHOAlngOs4BJdL9\" itemId: \"PVTI_lAHOAlngOs4BJdL9zgh-LdU\" fieldId: \"PVTF_lAHOAlngOs4BJdL9zg5nRLQ\" value: { date: \"2026-02-15\" }}) { projectV2Item { id }}}"
gh api graphql -f query="mutation { updateProjectV2ItemFieldValue(input: {projectId: \"PVT_kwHOAlngOs4BJdL9\" itemId: \"PVTI_lAHOAlngOs4BJdL9zgh-LdU\" fieldId: \"PVTF_lAHOAlngOs4BJdL9zg5nRLU\" value: { date: \"2026-03-30\" }}) { projectV2Item { id }}}"
Write-Host "Issue #10 dates set"

# Issue #15 - Polish Features
gh api graphql -f query="mutation { updateProjectV2ItemFieldValue(input: {projectId: \"PVT_kwHOAlngOs4BJdL9\" itemId: \"PVTI_lAHOAlngOs4BJdL9zgh-L5w\" fieldId: \"PVTF_lAHOAlngOs4BJdL9zg5nRLQ\" value: { date: \"2026-04-01\" }}) { projectV2Item { id }}}"
gh api graphql -f query="mutation { updateProjectV2ItemFieldValue(input: {projectId: \"PVT_kwHOAlngOs4BJdL9\" itemId: \"PVTI_lAHOAlngOs4BJdL9zgh-L5w\" fieldId: \"PVTF_lAHOAlngOs4BJdL9zg5nRLU\" value: { date: \"2026-05-01\" }}) { projectV2Item { id }}}"
Write-Host "Issue #15 dates set"

# Issue #16 - Final Documentation
gh api graphql -f query="mutation { updateProjectV2ItemFieldValue(input: {projectId: \"PVT_kwHOAlngOs4BJdL9\" itemId: \"PVTI_lAHOAlngOs4BJdL9zgh-MHA\" fieldId: \"PVTF_lAHOAlngOs4BJdL9zg5nRLQ\" value: { date: \"2026-03-15\" }}) { projectV2Item { id }}}"
gh api graphql -f query="mutation { updateProjectV2ItemFieldValue(input: {projectId: \"PVT_kwHOAlngOs4BJdL9\" itemId: \"PVTI_lAHOAlngOs4BJdL9zgh-MHA\" fieldId: \"PVTF_lAHOAlngOs4BJdL9zg5nRLU\" value: { date: \"2026-05-01\" }}) { projectV2Item { id }}}"
Write-Host "Issue #16 dates set"

# Issue #17 - Final Presentation
gh api graphql -f query="mutation { updateProjectV2ItemFieldValue(input: {projectId: \"PVT_kwHOAlngOs4BJdL9\" itemId: \"PVTI_lAHOAlngOs4BJdL9zgh-MNI\" fieldId: \"PVTF_lAHOAlngOs4BJdL9zg5nRLQ\" value: { date: \"2026-05-01\" }}) { projectV2Item { id }}}"
gh api graphql -f query="mutation { updateProjectV2ItemFieldValue(input: {projectId: \"PVT_kwHOAlngOs4BJdL9\" itemId: \"PVTI_lAHOAlngOs4BJdL9zgh-MNI\" fieldId: \"PVTF_lAHOAlngOs4BJdL9zg5nRLU\" value: { date: \"2026-05-10\" }}) { projectV2Item { id }}}"
Write-Host "Issue #17 dates set"

Write-Host "`nAll remaining issue dates updated successfully!"
