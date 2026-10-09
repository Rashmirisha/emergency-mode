import subprocess

def get_windows_gps():
    ps_script = """
    Add-Type -AssemblyName System.Device
    $watcher = New-Object System.Device.Location.GeoCoordinateWatcher([System.Device.Location.GeoPositionAccuracy]::High)
    $watcher.Start()
    $timeout = 0
    while ($watcher.Status -ne 'Ready' -and $timeout -lt 20) {
        Start-Sleep -Milliseconds 500
        $timeout++
    }
    if ($watcher.Position.Location.IsUnknown) {
        Write-Output "UNAVAILABLE"
    } else {
        Write-Output "$($watcher.Position.Location.Latitude),$($watcher.Position.Location.Longitude)"
    }
    $watcher.Stop()
    """

    try:
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=15
        )

        output = result.stdout.strip()

        if output and output != "UNAVAILABLE" and "," in output:
            lat, lon = map(float, output.split(","))
            return lat, lon
        else:
            return None

    except Exception as e:
        print("GPS Error:", e)
        return None
