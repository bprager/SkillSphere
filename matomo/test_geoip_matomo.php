<?php
// Test script to check if Matomo's GeoIP provider is working

// Set the path to Matomo
define('PIWIK_INCLUDE_PATH', '/var/www/html/');
define('PIWIK_USER_PATH', '/var/www/html/');

// Include Matomo core
require_once PIWIK_INCLUDE_PATH . '/core/bootstrap.php';

if (!defined('PIWIK_INCLUDE_PATH')) {
    define('PIWIK_INCLUDE_PATH', '/var/www/html/');
}

// Bootstrap Matomo
\Piwik\FrontController::getInstance()->init();

// Get the location provider
$provider = \Piwik\Plugins\UserCountry\LocationProvider::getCurrentProvider();

echo "Current GeoIP Provider: " . get_class($provider) . "\n";
echo "Provider ID: " . $provider->getId() . "\n";
echo "Is Available: " . ($provider->isAvailable() ? "Yes" : "No") . "\n";
echo "Is Working: " . ($provider->isWorking() ? "Yes" : "No") . "\n";

// Test with a known IP
$testIps = ['8.8.8.8', '1.1.1.1', '208.67.222.222'];

foreach ($testIps as $ip) {
    echo "\n--- Testing IP: $ip ---\n";
    try {
        $location = $provider->getLocation(['ip' => $ip]);
        echo "Country: " . ($location['country_code'] ?? 'NULL') . "\n";
        echo "Region: " . ($location['region_code'] ?? 'NULL') . "\n";
        echo "City: " . ($location['city'] ?? 'NULL') . "\n";
        echo "Latitude: " . ($location['latitude'] ?? 'NULL') . "\n";
        echo "Longitude: " . ($location['longitude'] ?? 'NULL') . "\n";
    } catch (Exception $e) {
        echo "Error: " . $e->getMessage() . "\n";
    }
}
