<?php
// Simple script to test MaxMind GeoIP directly

require_once '/var/www/html/vendor/autoload.php';

use GeoIp2\Database\Reader;

try {
    $reader = new Reader('/var/lib/GeoIP/GeoLite2-City.mmdb');

    $testIps = ['8.8.8.8', '1.1.1.1', '208.67.222.222'];

    foreach ($testIps as $ip) {
        echo "Testing IP: $ip\n";
        try {
            $record = $reader->city($ip);

            echo "Country: " . $record->country->isoCode . " (" . $record->country->name . ")\n";
            echo "Region: " . $record->subdivisions[0]->isoCode . " (" . $record->subdivisions[0]->name . ")\n";
            echo "City: " . $record->city->name . "\n";
            echo "Latitude: " . $record->location->latitude . "\n";
            echo "Longitude: " . $record->location->longitude . "\n";
            echo "----\n";
        } catch (Exception $e) {
            echo "Error for IP $ip: " . $e->getMessage() . "\n";
        }
    }
} catch (Exception $e) {
    echo "Failed to open database: " . $e->getMessage() . "\n";
}
