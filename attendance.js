const serverURL = "https://biometric-attendance-1uz9.onrender.com";

// Simulated Fingerprint Capture
async function captureFingerprint() {
    return new Promise((resolve) => {
        setTimeout(() => {
            const fingerprintData = "MOCK_FINGERPRINT_123"; // Use a consistent mock fingerprint
            resolve(fingerprintData);
        }, 2000);
    });
}

// Mark Attendance
async function markAttendance() {
    const fingerprint = await captureFingerprint();

    const attendanceData = {
        fingerprint,
        time: new Date().toLocaleTimeString(),
        date: new Date().toLocaleDateString()
    };

    try {
        const response = await fetch(`${serverURL}/attendance`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(attendanceData)
        });

        const result = await response.json();
        alert(result.message);
    } catch (error) {
        console.error("Error marking attendance:", error);
        alert("Error connecting to server.");
    }
}