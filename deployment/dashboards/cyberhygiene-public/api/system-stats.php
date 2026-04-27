<?php
header('Content-Type: application/json');
header('Cache-Control: no-cache, must-revalidate');

// Get uptime
$uptime_output = shell_exec('uptime -p');
$uptime = trim(str_replace('up ', '', $uptime_output));

// Get load average
$uptime_full = shell_exec('uptime');
if (preg_match('/load average: ([\d.]+), ([\d.]+), ([\d.]+)/', $uptime_full, $matches)) {
    $loadAvg = $matches[1] . ' / ' . $matches[2] . ' / ' . $matches[3];
} else {
    $loadAvg = 'N/A';
}

// Return JSON response
echo json_encode([
    'uptime' => $uptime,
    'loadAvg' => $loadAvg,
    'timestamp' => date('c')
]);
?>
