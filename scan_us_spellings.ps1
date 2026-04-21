$inputPath = "c:\Users\eoin0\AppData\Roaming\Code\User\workspaceStorage\1eef26cbdaac75c9f2fd5c25b853b011\GitHub.copilot-chat\chat-session-resources\976a4288-dc9e-4920-8d41-dacc463b3e16\call_MHxBbk1lODFpRk9pMUdpWmxSbnM__vscode-1776710634666\content.txt"
$lines = Get-Content $inputPath
$data = @()
foreach ($line in $lines) {
    if ($line -match "^(.*):(\d+):(.*)$") {
        $path = $matches[1]; $content = $matches[3]
        if ($path.EndsWith(".drawio") -and ($content -match 'align=\"?center\"?' -or $content -match 'verticalAlign=\"?center\"?')) { continue }
        $patterns = @("visualiz", "localiz", "\btire\b", "center", "meter", "behavior", "optimiz", "analyze")
        foreach ($p in $patterns) {
            if ($content -match "\b\w*$p\w*\b") {
                $word = $matches[0]; $suggested = $word
                if ($word -like "*visualiz*") { $suggested = $word -replace "visualiz", "visualis" }
                elseif ($word -like "*localiz*") { $suggested = $word -replace "localiz", "localis" }
                elseif ($word -eq "tire") { $suggested = "tyre" }
                elseif ($word -match "(?i)\bcentering\b") { $suggested = $word -replace "(?i)\bcentering\b", "centring" }
                elseif ($word -match "(?i)\bcentered\b") { $suggested = $word -replace "(?i)\bcentered\b", "centred" }
                elseif ($word -match "(?i)\bcenters\b") { $suggested = $word -replace "(?i)\bcenters\b", "centres" }
                elseif ($word -match "(?i)\bcenter\b") { $suggested = $word -replace "(?i)\bcenter\b", "centre" }
                elseif ($word -match "(?i)\bmeters\b" -and $word -notmatch "(?i)\b(therm|speed|acceler|volt|am|multi|galvano|para)meters\b") { $suggested = $word -replace "(?i)\bmeters\b", "metres" }
                elseif ($word -match "(?i)\bmeter\b" -and $word -notmatch "(?i)\b(therm|speed|acceler|volt|am|multi|galvano|para)meter\b") { $suggested = $word -replace "(?i)\bmeter\b", "metre" }
                elseif ($word -like "*behavior*") { $suggested = $word -replace "behavior", "behaviour" }
                elseif ($word -like "*optimiz*") { $suggested = $word -replace "optimiz", "optimise" }
                elseif ($word -like "*analyze*") { $suggested = $word -replace "analyze", "analyse" }
                if ($suggested -ne $word) { $data += [PSCustomObject]@{ Path = $path.Replace("C:\Users\eoin0\Documents\Code\FinalProject\FinalProject\", ""); ExactPhrase = $word; Replacement = $suggested } }
            }
        }
    }
}
$data | Select-Object Path, ExactPhrase, Replacement -Unique | ForEach-Object { "$($_.Path) | $($_.ExactPhrase) -> $($_.Replacement)" }
