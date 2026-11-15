param([string]$OutputDirectory = (Join-Path $PSScriptRoot 'runtime'))
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $OutputDirectory) {
    throw 'Choose a new output directory; existing journals must be preserved.'
}
Push-Location -LiteralPath 'D:\hkura\codedemo_v2'
try {
    & '.venv-integration/Scripts/python.exe' -m integration.contractor_tender_development --verify $PSScriptRoot
    if ($LASTEXITCODE -ne 0) { throw 'Input bundle changed; generate a new independent bundle.' }
    & '.venv-integration/Scripts/python.exe' -m integration.run `
        --input (Join-Path $PSScriptRoot 'macro-request.json') --output $OutputDirectory `
        --offline --input-format gba_request --macro-mode gba_v1_module --allow-native-project-generation `
        --agent-client-factory integration.native_routes:build_agent_client `
        --agent-client-config (Join-Path $PSScriptRoot 'native-host.json') `
        --module-assembly-hook integration.front_to_closeout_case:configure_assembly `
        --module-assembly-config (Join-Path $PSScriptRoot 'assembly-host.json')
    if ($LASTEXITCODE -ne 0) { throw 'Integration run failed; inspect the original error and journal.' }
} finally { Pop-Location }
