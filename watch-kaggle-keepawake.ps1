$Kernel = "mobashshirzainuddin1/02-baselines-and-ml-benchmark"
$IntervalSeconds = 60

Add-Type @"
using System;
using System.Runtime.InteropServices;

public static class PowerState
{
    [DllImport("kernel32.dll")]
    public static extern uint SetThreadExecutionState(uint esFlags);

    public const uint ES_CONTINUOUS       = 0x80000000;
    public const uint ES_SYSTEM_REQUIRED  = 0x00000001;
    public const uint ES_DISPLAY_REQUIRED = 0x00000002;
}
"@

function Keep-Awake {
    [PowerState]::SetThreadExecutionState(
        [PowerState]::ES_CONTINUOUS `
        -bor [PowerState]::ES_SYSTEM_REQUIRED `
        -bor [PowerState]::ES_DISPLAY_REQUIRED
    ) | Out-Null
}

function Allow-Sleep {
    [PowerState]::SetThreadExecutionState(
        [PowerState]::ES_CONTINUOUS
    ) | Out-Null
}

Write-Host "============================================"
Write-Host " Kaggle Keep-Awake Monitor"
Write-Host "============================================"
Write-Host "Kernel: $Kernel"
Write-Host "Checking every $IntervalSeconds seconds"
Write-Host "No downloads. No Kaggle modifications."
Write-Host ""

try {
    while ($true) {

        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

        $statusOutput = kaggle kernels status $Kernel 2>&1 |
            Out-String

        $status = $statusOutput.Trim()

        Write-Host "[$timestamp] $status"

        if ($status -match 'KernelWorkerStatus\.(RUNNING|QUEUED)') {

            Keep-Awake
            Write-Host "  -> ACTIVE: Windows sleep prevented."

        }
        elseif ($status -match 'KernelWorkerStatus\.(COMPLETE|ERROR|FAILED|CANCEL_REQUESTED|CANCEL_ACKNOWLEDGED)') {

            Allow-Sleep
            Write-Host "  -> TERMINAL/CANCELLING: Windows sleep restored."
            break

        }
        else {

            # Unknown state: keep awake temporarily
            Keep-Awake
            Write-Host "  -> UNKNOWN: keeping Windows awake temporarily."
        }

        Start-Sleep -Seconds $IntervalSeconds
    }
}
finally {
    Allow-Sleep
    Write-Host ""
    Write-Host "Normal Windows power behavior restored."
}