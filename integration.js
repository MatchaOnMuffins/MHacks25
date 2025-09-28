// Spectacles Lens Script
var BACKEND_BASE_URL = "https://mhacks25-225120046451.us-east1.run.app/";

// Upload Text for Analysis
function uploadTextForAnalysis(text) {
    var url = BACKEND_BASE_URL + "/upload/text";
    var body = JSON.stringify({ text: text });

    fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: body
    })
    .then(function(response) { return response.json(); })
    .then(function(json) {
        print("Text uploaded:", json.message);
        pollAnalysisReport();
    })
    .catch(function(error) {
        print("Error uploading text:", error);
    });
}

// Poll latest feedback report
function pollAnalysisReport() {
    var url = BACKEND_BASE_URL + "/feedback/report";

    fetch(url)
        .then(function(response) { return response.json(); })
        .then(function(json) {
            if (json.message && json.message.length > 0) {
                print("Analysis Summary:", json.message);
                showAROverlay(json.message);
            } else {
                print("No feedback yet, retrying...");
                // Retry after 2 seconds if processing is async
                script.createEvent("DelayedCallbackEvent").bind(function() {
                    pollAnalysisReport();
                }).reset(2);
            }
        })
        .catch(function(error) {
            print("Error fetching report:", error);
        });
}

// Optional: Upload an image (future features)
function uploadImage(filePath) {
    var url = BACKEND_BASE_URL + "/upload/image";
    var formData = new FormData();
    formData.append("image", filePath);

    fetch(url, {
        method: "POST",
        body: formData
    })
    .then(function(response) { return response.json(); })
    .then(function(json) {
        print("Image uploaded:", json.message);
    })
    .catch(function(error) {
        print("Error uploading image:", error);
    });
}

// Display text overlay in AR scene
function showAROverlay(text) {
    var overlay = global.scene.getObjectByName("TextOverlay");
    if (overlay) {
        overlay.text = text;
    }
}

// Example usage
uploadTextForAnalysis("Um, I think, like, the project went well.");
