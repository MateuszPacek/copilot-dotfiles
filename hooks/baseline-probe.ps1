param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('sessionStart', 'userPromptSubmitted')]
    [string]$EventName
)

$ErrorActionPreference = 'Stop'
try {
    $raw = [Console]::In.ReadToEnd()
    if ($raw.Length -gt 1048576) {
        throw 'Diagnostic input exceeds the size limit.'
    }
    $event = $raw | ConvertFrom-Json
    if (-not $raw.TrimStart().StartsWith('{') -or $event -isnot [PSCustomObject]) {
        throw 'Expected a hook event object.'
    }
    $keys = @($event.PSObject.Properties.Name | Sort-Object)
    $record = [ordered]@{
        event = $EventName
        recordedAtUtc = [DateTime]::UtcNow.ToString('o')
        keys = $keys
        hasSessionId = $keys -contains 'sessionId'
        hasAgentId = $keys -contains 'agentId'
        hasParentAgentId = $keys -contains 'parentAgentId'
    }
    $json = $record | ConvertTo-Json -Compress -Depth 4
    $logDirectory = Join-Path ([IO.Path]::GetTempPath()) 'copilot-hook-diagnostics'
    [IO.Directory]::CreateDirectory($logDirectory) | Out-Null
    $logPath = Join-Path $logDirectory ($EventName + '-' + [Guid]::NewGuid().ToString('N') + '.jsonl')
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($json + [Environment]::NewLine)
    $stream = [IO.File]::Open($logPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::Read)
    try {
        $stream.Write($bytes, 0, $bytes.Length)
    }
    finally {
        $stream.Dispose()
    }
    [Console]::Out.Write('{}')
}
catch {
    [Console]::Error.WriteLine('Baseline diagnostic failed: ' + $_.Exception.Message)
    exit 1
}
