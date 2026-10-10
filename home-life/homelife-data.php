<?php
/**
 * homelife-data.php
 * Backend for the Home Life family app.
 * Place this file in the same folder as homelife.html on your SiteGround server.
 *
 * GET  → returns all saved data as JSON
 * POST → receives updated data, saves to homelife-data.json, returns {"ok":true}
 */

// ── Security: only allow requests from your own domain ──────────────────────
// Replace with your actual domain. Or remove these lines if you hit CORS issues.
$allowed_origin = isset($_SERVER['HTTP_ORIGIN']) ? $_SERVER['HTTP_ORIGIN'] : '';
header('Access-Control-Allow-Origin: ' . $allowed_origin);
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json; charset=UTF-8');

// Handle preflight request
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

// ── Data file path ───────────────────────────────────────────────────────────
// Stored next to this PHP file. SiteGround will protect it — it won't be
// accessible via URL, only readable by PHP.
$dataFile = __DIR__ . '/homelife-data.json';

// ── Default data (used when no file exists yet) ──────────────────────────────
$defaults = [
    'plans'         => new stdClass(),
    'customRecipes' => [],
    'overrides'     => new stdClass(),
    'deletedRecipes'=> [],
    'essentials'    => [
        'Apples','Bananas','Blueberries','Cows Milk','Oat Milk',
        'Greek Yoghurt','Eggs','Brown bread flour','Butter',
        'Cherry Tomatoes','Walnuts','Chia Seeds',
        'Dishwasher cleaner (monthly)','Loo roll (monthly)','Tissues'
    ],
    'shopChecked'   => new stdClass(),
    'shopEdits'     => new stdClass(),
    'shopExtras'    => new stdClass(),
    'shopRemoved'   => new stdClass(), // { weekKey: { itemKey: true } }
    'catOverrides'  => new stdClass(), // { ingredientKey: sectionId }
    'pantry'        => new stdClass(), // { pantryKey: { name, amount, unit, category } }
    'essChecked'    => new stdClass(),
    'adhoc'         => new stdClass(), // { weekKey: [{ id, text }] }
    'adhocChecked'  => new stdClass(),
];

// ── GET: return current data ─────────────────────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (file_exists($dataFile)) {
        $raw = file_get_contents($dataFile);
        // Validate it's real JSON, otherwise return defaults
        $parsed = json_decode($raw);
        echo ($parsed !== null) ? $raw : json_encode($defaults);
    } else {
        echo json_encode($defaults);
    }
    exit;
}

// ── POST: save data ──────────────────────────────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = file_get_contents('php://input');

    // Validate JSON
    $data = json_decode($input);
    if ($data === null) {
        http_response_code(400);
        echo json_encode(['error' => 'Invalid JSON received']);
        exit;
    }

    // Write with exclusive lock so concurrent saves don't corrupt the file
    $fp = fopen($dataFile, 'c+');
    if (!$fp) {
        http_response_code(500);
        echo json_encode(['error' => 'Cannot open data file for writing. Check folder permissions.']);
        exit;
    }

    if (flock($fp, LOCK_EX)) {
        ftruncate($fp, 0);
        rewind($fp);
        fwrite($fp, json_encode($data, JSON_PRETTY_PRINT));
        fflush($fp);
        flock($fp, LOCK_UN);
        fclose($fp);
        echo json_encode(['ok' => true]);
    } else {
        fclose($fp);
        http_response_code(500);
        echo json_encode(['error' => 'Could not lock file for writing']);
    }
    exit;
}

// ── Any other method ─────────────────────────────────────────────────────────
http_response_code(405);
echo json_encode(['error' => 'Method not allowed']);