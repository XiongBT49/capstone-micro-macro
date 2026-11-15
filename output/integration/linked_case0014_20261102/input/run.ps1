param([string]$OutputDirectory = (Join-Path $PSScriptRoot 'runtime'))
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $OutputDirectory) {
    throw 'Choose a new output directory; existing journals must be preserved.'
}
Push-Location -LiteralPath 'D:\hkura\codedemo_v2'
try {
    $ErrorActionPreference = 'Continue'
    & '.venv-integration/Scripts/python.exe' -m integration.contractor_tender_development --verify $PSScriptRoot
    $tenderNativeExitCode = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    if ($tenderNativeExitCode -ne 0) { throw 'Input bundle changed; generate a new independent bundle.' }
    $ErrorActionPreference = 'Continue'
    & '.venv-integration/Scripts/python.exe' -m integration.run `
        --input (Join-Path $PSScriptRoot 'macro-request.json') --output $OutputDirectory `
        --llm --input-format gba_request --macro-mode gba_v1_module --allow-native-project-generation --allow-native-initial-projects-with-generation `
        --agent-client-factory integration.model_tender_native:build_agent_client `
        --agent-client-config (Join-Path $PSScriptRoot 'native-host.json') `
        --module-assembly-hook integration.origin_model_lifecycle:configure_assembly `
        --module-assembly-config (Join-Path $PSScriptRoot 'assembly-host.json')
    $tenderNativeExitCode = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    if ($tenderNativeExitCode -ne 0) { throw 'Integration run failed; inspect the original error and journal.' }
} finally { Pop-Location }
