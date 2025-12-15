# Run tests and open Allure report

Write-Host "Running docker tests..."

docker compose down

docker compose build tests

docker compose up --abort-on-container-exit tests

$exitCode = $LASTEXITCODE

Write-Host "Tests finished. Exit code: $exitCode"

Start-Sleep -Seconds 2

if (Test-Path "allure-results") {

    $files = Get-ChildItem "allure-results" -Recurse -File

    if ($files.Count -gt 0) {

        Write-Host "Starting Allure report..."

        $allure = Get-Command allure -ErrorAction SilentlyContinue

        if ($allure) {
            Start-Process powershell -ArgumentList "-NoExit", "-Command", "allure serve allure-results"
        }
        else {
            Start-Process powershell -ArgumentList "-NoExit", "-Command", "npx -p allure-commandline allure serve allure-results"
        }

    }
    else {
        Write-Host "Allure results directory is empty"
    }

}
else {
    Write-Host "Allure results directory not found"
}

exit $exitCode
