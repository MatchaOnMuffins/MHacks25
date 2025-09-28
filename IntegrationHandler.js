// IntegrationHandler.js
// Version: 1.0.0
// Event: OnStart
// Description: Captures transcribed text every 5 seconds and sends to integration

//@input string integrationUrl {"label": "Integration API URL", "description": "URL to send transcribed text for processing"}
//@input int sendInterval = 5 {"label": "Send Interval (seconds)", "widget": "slider", "min": 1, "max": 60, "step": 1, "description": "How often to send text in seconds"}
//@input bool enableIntegration {"label": "Enable Integration"}
//@input Component.Text outputTextComponent {"label": "Output Text Component", "description": "Text component to display integration results"}
//@input Component.Text transcriptionTextComponent {"label": "Speech Recognition Text Component", "description": "Text component that shows the transcribed speech"}
//@input Asset.InternetModule serviceModule  {"label": "Service Module", "description": "Service Module component for HTTP requests"}

//@ui {"widget":"separator"}
//@input bool debug {"label": "Debug Mode"}

var accumulatedText = "";
var lastSentText = "";
var isIntegrationEnabled = false;
var updateEvent = null;
var lastSendTime = 0;

// Initialize the integration handler
function initialize() {
    if (!script.enableIntegration) {
        if (script.debug) {
            print("Integration Handler: Integration disabled");
        }
        return;
    }
    
    if (!script.outputTextComponent) {
        print("ERROR: Output text component not assigned");
        return;
    }
    
    if (!script.transcriptionTextComponent) {
        print("ERROR: Speech Recognition Text Component not assigned");
        return;
    }
    
    if (!script.serviceModule) {
        print("ERROR: Service Module not assigned");
        return;
    }
    
    if (script.sendInterval < 1) {
        print("ERROR: Send interval must be at least 1 second");
        return;
    }
    
    // Start the update event for periodic checking
    updateEvent = script.createEvent("UpdateEvent");
    updateEvent.bind(onUpdate);
    
    isIntegrationEnabled = true;
    lastSendTime = Date.now();
    
    if (script.debug) {
        print("Integration Handler: Initialized with " + script.sendInterval + " second interval");
    }
    
    // Display initial status
    script.outputTextComponent.text = "Integration ready - listening for speech...";
}


// Update function to check if it's time to send
function onUpdate() {
    if (!isIntegrationEnabled) {
        return;
    }
    
    var currentTime = Date.now();
    var intervalMs = script.sendInterval * 1000;
    
    // Check if enough time has passed since last send
    if (currentTime - lastSendTime >= intervalMs) {
        // Get current transcribed text from Speech Recognition
        captureCurrentTranscription();
        sendTextToIntegration();
        lastSendTime = currentTime;
    }
}

// Function to capture current transcription from Speech Recognition text component
function captureCurrentTranscription() {
    if (script.transcriptionTextComponent && script.transcriptionTextComponent.text) {
        var currentText = script.transcriptionTextComponent.text.trim();
        if (currentText !== "" && currentText !== lastSentText) {
            accumulatedText = currentText; // Replace with latest transcription
            
            if (script.debug) {
                print("Integration Handler: Captured transcription: " + currentText);
            }
        }
    }
}

// Function to send accumulated text to integration
function sendTextToIntegration() {
    if (!isIntegrationEnabled || !accumulatedText || accumulatedText.trim() === "") {
        if (script.debug) {
            print("Integration Handler: No text to send");
        }
        return;
    }
    
    var textToSend = accumulatedText.trim();
    
    // Don't send if it's the same as last sent text
    if (textToSend === lastSentText) {
        if (script.debug) {
            print("Integration Handler: Text unchanged, skipping send");
        }
        return;
    }
    
    if (script.debug) {
        print("Integration Handler: Sending text to integration: " + textToSend);
    }
    
    // Update UI to show sending status
    script.outputTextComponent.text = "Sending to integration...";
    
    // Send to integration URL
    sendToIntegrationAPI(textToSend);
    
    // Update last sent text
    lastSentText = textToSend;
}

// Function to send text to the integration API
function sendToIntegrationAPI(text) {
    try {
        // Prepare request data
        var requestData = {
            "text": text,
            "timestamp": Date.now(),
            "source": "snapchat_lens"
        };
        
        var requestBody = JSON.stringify(requestData);
        
        if (script.debug) {
            print("Integration Handler: Sending to URL: " + script.integrationUrl);
            print("Integration Handler: Request body: " + requestBody);
        }
        
        // Check if we have a valid URL
        if (!script.integrationUrl || script.integrationUrl === "") {
            // Simulate local processing if no URL provided
            simulateLocalProcessing(text);
            return;
        }
        
        // Create HTTP request using Lens Studio's RemoteServiceHttpRequest
        var req = RemoteServiceHttpRequest.create();
        req.url = script.integrationUrl;
        req.method = RemoteServiceHttpRequest.HttpRequestMethod.Post;
        req.body = requestBody;
        req.headers = {
            'Content-Type': 'application/json'
        };
        
        // Perform the HTTP request
        script.serviceModule.request(req, function(res) {
            if (res.statusCode === 200) {
                if (script.debug) {
                    print("Integration Handler: Success response: " + res.body);
                }
                handleIntegrationResponse({status: 200, body: res.body}, text);
            } else if (res.statusCode === 400 && res.headers['x-camera-kit-error-type']) {
                var errorMsg = "Error: " + res.body;
                if (script.debug) {
                    print("Integration Handler: " + errorMsg);
                }
                handleIntegrationError(errorMsg, text);
            } else {
                var errorMsg = "Error: Unexpected HTTP status code " + res.statusCode;
                if (script.debug) {
                    print("Integration Handler: " + errorMsg);
                }
                handleIntegrationError(errorMsg, text);
            }
        });
        
    } catch (error) {
        handleIntegrationError(error, text);
    }
}

// Function to simulate local processing when HTTP is not available
function simulateLocalProcessing(text) {
    if (script.debug) {
        print("Integration Handler: Simulating local processing for: " + text);
    }
    
    // Simulate processing delay
    setTimeout(function() {
        var result = "Local Processing Result:\n";
        result += "Text: " + text + "\n";
        result += "Word count: " + text.split(" ").length + "\n";
        result += "Character count: " + text.length + "\n";
        result += "Processed at: " + new Date().toLocaleTimeString() + "\n";
        
        // Create mock response
        var mockResponse = {
            status: 200,
            body: JSON.stringify({
                result: result,
                original_text: text,
                timestamp: Date.now(),
                processed: true
            })
        };
        
        handleIntegrationResponse(mockResponse, text);
    }, 500); // 500ms delay to simulate processing
}

// Handle successful integration response
function handleIntegrationResponse(response, originalText) {
    try {
        var responseText = "";
        
        if (response && response.status === 200) {
            var responseData = JSON.parse(response.body);
            
            // Extract response based on common API patterns
            if (responseData.result) {
                responseText = responseData.result;
            } else if (responseData.output) {
                responseText = responseData.output;
            } else if (responseData.text) {
                responseText = responseData.text;
            } else if (responseData.response) {
                responseText = responseData.response;
            } else if (typeof responseData === "string") {
                responseText = responseData;
            } else {
                responseText = "Integration processed: " + originalText;
            }
            
            // Display the response
            script.outputTextComponent.text = "Integration Result:\n" + responseText;
            
            if (script.debug) {
                print("Integration Handler: Received response: " + responseText);
            }
            
        } else {
            script.outputTextComponent.text = "Integration Error: HTTP " + (response ? response.status : "unknown");
            
            if (script.debug) {
                print("Integration Handler: HTTP error " + (response ? response.status : "unknown"));
            }
        }
        
    } catch (parseError) {
        script.outputTextComponent.text = "Integration Error: Invalid response format";
        
        if (script.debug) {
            print("Integration Handler: Response parse error: " + parseError);
        }
    }
}

// Handle integration error
function handleIntegrationError(error, originalText) {
    var errorMessage = "Integration Error: ";
    
    if (error && error.message) {
        errorMessage += error.message;
    } else if (typeof error === "string") {
        errorMessage += error;
    } else {
        errorMessage += "Unknown error occurred";
    }
    
    script.outputTextComponent.text = errorMessage;
    
    if (script.debug) {
        print("Integration Handler: Error: " + errorMessage);
    }
}

// Function to stop integration
function stopIntegration() {
    if (updateEvent) {
        updateEvent.enabled = false;
        updateEvent = null;
    }
    
    isIntegrationEnabled = false;
    
    if (script.debug) {
        print("Integration Handler: Stopped");
    }
}

// Function to start integration
function startIntegration() {
    if (!isIntegrationEnabled) {
        initialize();
    } else if (updateEvent) {
        updateEvent.enabled = true;
    }
}

// Public API functions
script.stopIntegration = stopIntegration;
script.startIntegration = startIntegration;

// Initialize when script starts
script.createEvent("OnStartEvent").bind(function() {
    initialize();
});

// Clean up when script is destroyed
script.createEvent("OnDestroyEvent").bind(function() {
    stopIntegration();
});
