<?php

function recognizeLicensePlate($imagePath) {
    // Command to run Tesseract OCR on the uploaded image
    $command = "tesseract " . escapeshellarg($imagePath) . " stdout -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    $output = shell_exec($command);
    return trim($output);
}

// Process the uploaded image
if (isset($_FILES['license_plate_image'])) {
    $imagePath = $_FILES['license_plate_image']['tmp_name'];
    $plateNumber = recognizeLicensePlate($imagePath);

    // Redirect to the main page with the plate number in the URL
    header("Location: index.php?plate=" . urlencode($plateNumber));
    exit();
} else {
    echo "No image uploaded.";
}
?>
