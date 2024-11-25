<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Automatic Number Plate Reader</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Quick ANPR</h2>
        </div>

        <!-- Input Section for Camera and File Selection -->
        <div class="input-section">
            <form action="process_image.php" method="POST" enctype="multipart/form-data">
                <button type="button" id="openCameraBtn">Open Camera</button>
                <input type="file" name="license_plate_image" id="chooseFileBtn" accept="image/*">
                <button type="submit">Upload & Recognize</button>
            </form>
        </div>

        <!-- Navigation Buttons for Results -->
        <div class="buttons">
            <button id="next">Next</button>
            <button id="previous">Previous</button>
            <button id="list">List</button>
        </div>

        <!-- Display Section for Image and Output -->
        <div class="display-section">
            <div class="image-container">
                <h3>Selected Image</h3>
                <img id="capturedImage" src="" alt="Captured Image" style="display: none; max-width: 100%; height: auto;"/>
            </div>
            <div class="output-container">
                <h3>Processed Output</h3>
                <p id="recognized-plate-number">
                    <?php echo isset($_GET['plate']) ? htmlspecialchars($_GET['plate']) : 'No plate detected yet'; ?>
                </p>
            </div>
        </div>
    </div>

    <script src="script.js"></script>
</body>
</html>
