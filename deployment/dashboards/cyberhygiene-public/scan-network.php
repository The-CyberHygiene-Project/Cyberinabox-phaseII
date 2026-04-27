<?php
/**
 * Network Scanner - Scans the specified network for active devices
 * Used by CyberHygiene AI System Administration Dashboard
 */

// Set headers for JSON response
header('Content-Type: application/json');

// Only allow POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

// Get POST data
$input = file_get_contents('php://input');
$data = json_decode($input, true);

// Validate network parameter
$network = isset($data['network']) ? $data['network'] : '192.168.1.0/24';

// Sanitize input to prevent command injection
if (!preg_match('/^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$/', $network)) {
    echo json_encode(['success' => false, 'error' => 'Invalid network format']);
    exit;
}

// Initialize results array
$devices = [];

// Increase execution time for slow scans
set_time_limit(60);

// Use the network-scan.sh wrapper script
$scanScript = '/usr/local/bin/network-scan.sh';
// Disable nmap/arp-scan due to FIPS mode memory corruption issues
// Force use of ping+ARP fallback method instead
if (false && file_exists($scanScript)) {
    // Use the wrapper script with sudo -n (non-interactive, don't prompt for password)
    $command = "sudo -n " . $scanScript . " " . escapeshellarg($network) . " 2>&1";

    // Use proc_open for reliable output capture
    $descriptors = [
        0 => ['pipe', 'r'],  // stdin
        1 => ['pipe', 'w'],  // stdout
        2 => ['pipe', 'w']   // stderr
    ];

    $process = proc_open($command, $descriptors, $pipes);
    $output = '';

    if (is_resource($process)) {
        // Close stdin
        fclose($pipes[0]);

        // Read stdout
        $output = stream_get_contents($pipes[1]);
        fclose($pipes[1]);

        // Read stderr
        $errors = stream_get_contents($pipes[2]);
        fclose($pipes[2]);

        // Wait for process to finish
        proc_close($process);
    }

    // Parse nmap output
    $lines = explode("\n", $output);
    $currentIP = null;

    foreach ($lines as $line) {
        // Look for IP address lines
        if (preg_match('/Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/', $line, $matches)) {
            $currentIP = $matches[1];
            $devices[] = [
                'ip' => $currentIP,
                'hostname' => '',
                'mac' => '',
                'vendor' => ''
            ];
        }
        // Look for MAC address lines
        else if ($currentIP && preg_match('/MAC Address: ([0-9A-F:]+)\s*\((.+)\)/i', $line, $matches)) {
            $lastIndex = count($devices) - 1;
            if ($lastIndex >= 0 && $devices[$lastIndex]['ip'] === $currentIP) {
                $devices[$lastIndex]['mac'] = $matches[1];
                $devices[$lastIndex]['vendor'] = $matches[2];
            }
        }
    }
}
// Fallback to arp-scan if nmap is not available
else {
    $arpScanPath = shell_exec('which arp-scan 2>/dev/null');
    // Disable arp-scan due to FIPS mode memory corruption
    if (false && !empty($arpScanPath)) {
        $command = "sudo arp-scan --interface=eth0 " . escapeshellarg($network) . " 2>&1";
        $output = shell_exec($command);

        // Parse arp-scan output
        $lines = explode("\n", $output);
        foreach ($lines as $line) {
            // Look for lines with IP, MAC, and vendor
            if (preg_match('/(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+([0-9a-f:]+)\s+(.+)/i', $line, $matches)) {
                $devices[] = [
                    'ip' => $matches[1],
                    'hostname' => '',
                    'mac' => strtoupper($matches[2]),
                    'vendor' => trim($matches[3])
                ];
            }
        }
    }
    // Last resort: use arp cache (read existing network neighbors)
    else {
        // Extract network prefix for filtering
        $networkParts = explode('/', $network);
        $baseIP = $networkParts[0];
        $ipParts = explode('.', $baseIP);
        $basePrefix = $ipParts[0] . '.' . $ipParts[1] . '.' . $ipParts[2];

        // Read ARP/neighbor cache using ip neigh (more reliable than arp command)
        $arpOutput = shell_exec('/usr/sbin/ip neigh 2>&1');
        $lines = explode("\n", $arpOutput);

        foreach ($lines as $line) {
            // Parse ip neigh output format: "IP dev IFACE lladdr MAC STATE"
            if (preg_match('/(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+dev\s+\S+\s+lladdr\s+([0-9a-f:]+)/i', $line, $matches)) {
                $ip = $matches[1];
                $mac = strtoupper($matches[2]);

                // Only include IPs in our target network
                if (strpos($ip, $basePrefix) === 0) {
                    // Try to resolve hostname
                    $hostname = gethostbyaddr($ip);
                    if ($hostname === $ip) {
                        $hostname = '';
                    }

                    $devices[] = [
                        'ip' => $ip,
                        'hostname' => $hostname,
                        'mac' => $mac,
                        'vendor' => ''
                    ];
                }
            }
        }
    }
}

// Load device mapping from configuration file
$deviceMapFile = __DIR__ . '/device-map.json';
$deviceMap = [];
if (file_exists($deviceMapFile)) {
    $deviceMapJson = file_get_contents($deviceMapFile);
    $deviceMap = json_decode($deviceMapJson, true);
}

// Enhanced hostname resolution function
function resolveHostname($ip, $deviceMap = []) {
    // Method 0: Check device mapping file first
    if (isset($deviceMap[$ip]) && !empty($deviceMap[$ip]['hostname'])) {
        return $deviceMap[$ip]['hostname'];
    }

    // Method 1: Try reverse DNS lookup
    $hostname = gethostbyaddr($ip);
    if ($hostname !== $ip && !empty($hostname)) {
        return $hostname;
    }

    // Method 2: Try using host command for DNS lookup
    $hostOutput = shell_exec("/usr/bin/host $ip 2>/dev/null");
    if (!empty($hostOutput) && preg_match('/domain name pointer\s+(.+)\.$/i', $hostOutput, $matches)) {
        return rtrim($matches[1], '.');
    }

    // Method 3: Try nmblookup for NetBIOS names (Windows/Samba)
    $nmblookupPath = '/usr/bin/nmblookup';
    if (file_exists($nmblookupPath)) {
        $nmbOutput = shell_exec("$nmblookupPath -A $ip 2>/dev/null");
        if (!empty($nmbOutput) && preg_match('/<00>\s+-\s+<ACTIVE>/i', $nmbOutput, $matches)) {
            // Extract the computer name before <00>
            if (preg_match('/^\s*([^\s<]+)\s+<00>/im', $nmbOutput, $nameMatches)) {
                return trim($nameMatches[1]);
            }
        }
    }

    // Method 4: Check /etc/hosts file
    $hostsFile = file_get_contents('/etc/hosts');
    if (preg_match("/^$ip\s+(.+?)(\s|$)/m", $hostsFile, $matches)) {
        return trim($matches[1]);
    }

    return '';
}

// Try to resolve hostnames for devices that don't have them
foreach ($devices as &$device) {
    if (empty($device['hostname'])) {
        $hostname = resolveHostname($device['ip'], $deviceMap);
        if (!empty($hostname)) {
            $device['hostname'] = $hostname;
        }
    }
}

// Sort devices by IP address
usort($devices, function($a, $b) {
    return ip2long($a['ip']) - ip2long($b['ip']);
});

// Return results
echo json_encode([
    'success' => true,
    'network' => $network,
    'devices' => $devices,
    'count' => count($devices)
]);
?>
