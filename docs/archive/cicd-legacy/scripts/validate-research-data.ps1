#!/usr/bin/env pwsh
<#
.SYNOPSIS
Validates SolStein research data against John-level quality standards

.DESCRIPTION
This script validates research outputs against the 8-category methodology,
ensuring source attribution, confidence scoring, and data freshness.

.PARAMETER ResearchPath
Path to research directory (default: research/)

.PARAMETER Threshold
Minimum quality score threshold (0-100, default: 85)

.PARAMETER OutputPath
Path for validation report (default: validation-report/)

.EXAMPLE
./validate-research-data.ps1 -ResearchPath "research/outputs" -Threshold 90

.EXAMPLE
./validate-research-data.ps1 -OutputPath "$(Build.ArtifactStagingDirectory)/validation"
#>

param(
    [string]$ResearchPath = "research/",
    [int]$Threshold = 85,
    [string]$OutputPath = "validation-report/"
)

# Create output directory
New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

# Initialize validation results
$validationResults = @()
$overallScore = 0
$totalReports = 0
$passedReports = 0

Write-Host "🔍 Validating SolStein Research Data" -ForegroundColor Cyan
Write-Host "Research Path: $ResearchPath" -ForegroundColor Gray
Write-Host "Quality Threshold: $Threshold%" -ForegroundColor Gray
Write-Host ""

# Define 8 categories (MANDATORY)
$mandatoryCategories = @(
    "Company Fundamentals",
    "Market Position", 
    "Product & Technology",
    "AI & Innovation",
    "Growth & Trajectory",
    "Specialization",
    "Pricing & Business Model",
    "Threat Assessment"
)

# Find all research reports
$researchFiles = Get-ChildItem -Path $ResearchPath -Filter "*.md" -Recurse

if ($researchFiles.Count -eq 0) {
    Write-Host "❌ No research files found in $ResearchPath" -ForegroundColor Red
    exit 1
}

Write-Host "Found $($researchFiles.Count) research file(s)" -ForegroundColor Green

foreach ($file in $researchFiles) {
    Write-Host "`n📄 Analyzing: $($file.Name)" -ForegroundColor Yellow
    
    $content = Get-Content $file.FullName -Raw
    $reportResults = @{
        FileName = $file.Name
        FilePath = $file.FullName
        Categories = @{}
        Sources = 0
        ConfidenceScore = 0
        DataFreshness = $true
        Issues = @()
        Score = 0
    }
    
    # Check 1: 8-Category Completeness
    $categoryScore = 0
    foreach ($category in $mandatoryCategories) {
        $hasCategory = $content -match $category -or $content -match [regex]::Escape($category)
        $reportResults.Categories[$category] = $hasCategory
        
        if ($hasCategory) {
            $categoryScore += 12.5  # 100/8 = 12.5 per category
            Write-Host "  ✅ $category" -ForegroundColor Green
        } else {
            $reportResults.Issues += "Missing category: $category"
            Write-Host "  ❌ $category" -ForegroundColor Red
        }
    }
    
    # Check 2: Source Attribution
    $sourcePattern = '\[Source:.*?\]'
    $sources = [regex]::Matches($content, $sourcePattern)
    $reportResults.Sources = $sources.Count
    
    if ($sources.Count -gt 0) {
        $sourceScore = [math]::Min(100, ($sources.Count * 10))  # Up to 10 sources = 100%
        Write-Host "  ✅ Sources: $($sources.Count) found" -ForegroundColor Green
        
        # Check source format
        $validSources = 0
        foreach ($source in $sources) {
            if ($source.Value -match '\[Source:.*?\-.*?\-.*?\-.*?\]') {
                $validSources++
            }
        }
        
        if ($validSources -eq $sources.Count) {
            Write-Host "  ✅ All sources have correct format" -ForegroundColor Green
        } else {
            $reportResults.Issues += "$($sources.Count - $validSources) sources have invalid format"
            Write-Host "  ⚠️  $($sources.Count - $validSources) sources have invalid format" -ForegroundColor Yellow
        }
    } else {
        $sourceScore = 0
        $reportResults.Issues += "No source attribution found"
        Write-Host "  ❌ No sources found" -ForegroundColor Red
    }
    
    # Check 3: Confidence Scoring
    if ($content -match 'Confidence.*?:.*?(High|Medium|Low|high|medium|low)') {
        $reportResults.ConfidenceScore = 100
        Write-Host "  ✅ Confidence scoring present" -ForegroundColor Green
    } else {
        $reportResults.Issues += "No confidence scoring found"
        Write-Host "  ❌ No confidence scoring" -ForegroundColor Red
    }
    
    # Check 4: Data Freshness
    $currentYear = (Get-Date).Year
    $yearPattern = '20\d{2}'
    $years = [regex]::Matches($content, $yearPattern) | ForEach-Object { $_.Value } | Select-Object -Unique
    
    $freshData = $true
    foreach ($year in $years) {
        if ([int]$year -lt ($currentYear - 2)) {
            $freshData = $false
            $reportResults.Issues += "Contains data from $year (more than 2 years old)"
            Write-Host "  ⚠️  Contains data from $year" -ForegroundColor Yellow
        }
    }
    
    $reportResults.DataFreshness = $freshData
    if ($freshData) {
        Write-Host "  ✅ Data is fresh (within 2 years)" -ForegroundColor Green
    }
    
    # Check 5: Dashboard-Ready Data
    $hasJson = $content -match '```json' -or $content -match '\{.*?"company".*?\}'
    if ($hasJson) {
        Write-Host "  ✅ Dashboard-ready JSON found" -ForegroundColor Green
    } else {
        $reportResults.Issues += "No dashboard-ready JSON data"
        Write-Host "  ❌ No dashboard-ready JSON" -ForegroundColor Red
    }
    
    # Check 6: Executive Summary
    $hasSummary = $content -match 'Executive Summary|executive summary|Summary'
    if ($hasSummary) {
        Write-Host "  ✅ Executive summary found" -ForegroundColor Green
    } else {
        $reportResults.Issues += "No executive summary"
        Write-Host "  ❌ No executive summary" -ForegroundColor Red
    }
    
    # Calculate overall score
    $weights = @{
        Categories = 40  # 40% of total score
        Sources = 30     # 30% of total score  
        Confidence = 10  # 10% of total score
        Freshness = 10   # 10% of total score
        Dashboard = 5    # 5% of total score
        Summary = 5      # 5% of total score
    }
    
    $categoryWeighted = ($categoryScore / 100) * $weights.Categories
    $sourceWeighted = ($sourceScore / 100) * $weights.Sources
    $confidenceWeighted = ($reportResults.ConfidenceScore / 100) * $weights.Confidence
    $freshnessWeighted = ($reportResults.DataFreshness ? 100 : 0) / 100 * $weights.Freshness
    $dashboardWeighted = ($hasJson ? 100 : 0) / 100 * $weights.Dashboard
    $summaryWeighted = ($hasSummary ? 100 : 0) / 100 * $weights.Summary
    
    $reportResults.Score = [math]::Round($categoryWeighted + $sourceWeighted + $confidenceWeighted + $freshnessWeighted + $dashboardWeighted + $summaryWeighted)
    
    # Determine pass/fail
    $passed = $reportResults.Score -ge $Threshold
    $reportResults.Passed = $passed
    
    if ($passed) {
        $passedReports++
        Write-Host "  ✅ PASS: Score $($reportResults.Score)%" -ForegroundColor Green
    } else {
        Write-Host "  ❌ FAIL: Score $($reportResults.Score)% (Threshold: $Threshold%)" -ForegroundColor Red
    }
    
    $overallScore += $reportResults.Score
    $totalReports++
    $validationResults += $reportResults
}

# Calculate overall statistics
if ($totalReports -gt 0) {
    $overallAverage = [math]::Round($overallScore / $totalReports)
    $passRate = [math]::Round(($passedReports / $totalReports) * 100)
} else {
    $overallAverage = 0
    $passRate = 0
}

# Generate detailed report
$reportContent = @"
# SolStein Research Validation Report
## Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Summary
- **Total Reports**: $totalReports
- **Passed Reports**: $passedReports
- **Pass Rate**: $passRate%
- **Average Score**: $overallAverage%
- **Threshold**: $Threshold%

## Overall Status
$(
if ($passRate -ge 90) {
    "✅ **EXCELLENT** - Research quality meets enterprise standards"
} elseif ($passRate -ge 80) {
    "⚠️ **GOOD** - Research quality is good but needs minor improvements"
} elseif ($passRate -ge 70) {
    "⚠️ **FAIR** - Research quality needs attention"
} else {
    "❌ **POOR** - Research quality requires significant improvement"
}
)

## Detailed Results

$(foreach ($result in $validationResults) {
    $status = if ($result.Passed) { "✅ PASS" } else { "❌ FAIL" }
    @"
### $($result.FileName)
**Status**: $status
**Score**: $($result.Score)%

**Categories Found**: $($result.Categories.Values | Where-Object { $_ } | Measure-Object).Count/8
**Sources**: $($result.Sources)
**Confidence Scoring**: $(if ($result.ConfidenceScore -gt 0) { "✅ Present" } else { "❌ Missing" })
**Data Freshness**: $(if ($result.DataFreshness) { "✅ Good" } else { "❌ Stale data" })

$(if ($result.Issues.Count -gt 0) {
    "**Issues**:"
    foreach ($issue in $result.Issues) {
        "- $issue"
    }
})

---
"@
})

## Recommendations
$(
if ($passRate -lt 90) {
    @"
1. **Ensure all 8 categories are complete** in every report
2. **Add source attribution** for every factual claim
3. **Include confidence scoring** (High/Medium/Low)
4. **Update stale data** (nothing older than 2 years)
5. **Add dashboard-ready JSON** for integration
6. **Include executive summary** in every report
"@
} else {
    "✅ Research quality meets all standards. Continue maintaining high quality."
}
)

## Validation Criteria
1. **8-Category Completeness (40%)**: All 8 categories must be present
2. **Source Attribution (30%)**: Every fact must have source with format: [Source: Type - Name - Date - Confidence]
3. **Confidence Scoring (10%)**: Overall confidence must be specified
4. **Data Freshness (10%)**: No data older than 2 years
5. **Dashboard Integration (5%)**: JSON data for dashboard integration
6. **Executive Summary (5%)**: One-paragraph summary of key findings

## Next Steps
1. Address issues in failing reports
2. Run validation again after fixes
3. Update research templates if patterns emerge
4. Train team on quality standards
"@

# Save report
$reportPath = Join-Path $OutputPath "research-validation-report.md"
$reportContent | Out-File -FilePath $reportPath -Encoding UTF8

# Generate JSON for CI/CD integration
$jsonReport = @{
    timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    summary = @{
        totalReports = $totalReports
        passedReports = $passedReports
        passRate = $passRate
        averageScore = $overallAverage
        threshold = $Threshold
    }
    reports = $validationResults | ForEach-Object {
        @{
            fileName = $_.FileName
            score = $_.Score
            passed = $_.Passed
            categoriesFound = ($_.Categories.Values | Where-Object { $_ } | Measure-Object).Count
            sources = $_.Sources
            hasConfidence = $_ConfidenceScore -gt 0
            dataFresh = $_.DataFreshness
            issues = $_.Issues
        }
    }
}

$jsonPath = Join-Path $OutputPath "research-validation-results.json"
$jsonReport | ConvertTo-Json -Depth 10 | Out-File -FilePath $jsonPath -Encoding UTF8

# Output summary
Write-Host "`n📊 Validation Complete" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host "Total Reports: $totalReports" -ForegroundColor White
Write-Host "Passed: $passedReports" -ForegroundColor $(if ($passedReports -eq $totalReports) { "Green" } else { "Yellow" })
Write-Host "Failed: $($totalReports - $passedReports)" -ForegroundColor $(if (($totalReports - $passedReports) -eq 0) { "Green" } else { "Red" })
Write-Host "Pass Rate: $passRate%" -ForegroundColor $(if ($passRate -ge 90) { "Green" } elseif ($passRate -ge 80) { "Yellow" } else { "Red" })
Write-Host "Average Score: $overallAverage%" -ForegroundColor White
Write-Host ""

# Set pipeline variables
Write-Host "##vso[task.setvariable variable=researchValidationPassRate]$passRate"
Write-Host "##vso[task.setvariable variable=researchValidationAverageScore]$overallAverage"
Write-Host "##vso[task.setvariable variable=researchValidationTotalReports]$totalReports"
Write-Host "##vso[task.setvariable variable=researchValidationPassedReports]$passedReports"

# Check if overall pass rate meets threshold
$overallPassed = $passRate -ge 90  # Require 90% pass rate overall

if ($overallPassed) {
    Write-Host "✅ Overall research quality PASSES validation" -ForegroundColor Green
    Write-Host "##vso[task.setvariable variable=researchValidationOverallPassed]true"
    exit 0
} else {
    Write-Host "❌ Overall research quality FAILS validation" -ForegroundColor Red
    Write-Host "##vso[task.setvariable variable=researchValidationOverallPassed]false"
    
    # Check if we should fail the build
    if ($passRate -lt 70) {
        Write-Host "##vso[task.logissue type=error]Research quality critically low ($passRate% pass rate)"
        exit 1
    } else {
        Write-Host "⚠️ Research quality needs improvement ($passRate% pass rate)" -ForegroundColor Yellow
        exit 0  # Warning but not failure
    }
}