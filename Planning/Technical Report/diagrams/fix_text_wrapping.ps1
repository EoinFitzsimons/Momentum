# Fix text wrapping in all draw.io files
$files = Get-ChildItem -Filter "*.drawio"

foreach ($file in $files) {
    Write-Host "Processing: $($file.Name)"
    $content = Get-Content $file.FullName -Raw
    
    # Replace all style attributes that have fillColor but lack whiteSpace=wrap
    # Pattern: style="rounded=1;fillColor=... that doesn't already have whiteSpace
    $pattern = 'style="(rounded=[^"]*fillColor=[^"]*)"(?![^<]*whiteSpace)'
    $replacement = {
        $match = $args[0]
        $styleContent = $match.Groups[1].Value
        
        # Add whiteSpace=wrap;html=1 after rounded=1;
        $newStyle = $styleContent -replace '(rounded=1;)', '$1whiteSpace=wrap;html=1;'
        
        # Add proper alignment attributes if not present
        if ($newStyle -notmatch 'align=') {
            if ($styleContent -match 'fontSize=\d+') {
                # For boxes with text, add left alignment
                $newStyle += ';align=left;verticalAlign=top;spacing=10'
            }
        }
        
        return "style=`"$newStyle`""
    }
    
    $newContent = [regex]::Replace($content, $pattern, $replacement)
    
    if ($content -ne $newContent) {
        Set-Content -Path $file.FullName -Value $newContent -NoNewline
        Write-Host "  ✓ Updated: $($file.Name)" -ForegroundColor Green
    } else {
        Write-Host "  - No changes needed" -ForegroundColor Yellow
    }
}

Write-Host "`nDone! All diagrams fixed." -ForegroundColor Cyan
