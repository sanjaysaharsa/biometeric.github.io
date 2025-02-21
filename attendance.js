const serverURL = "http://127.0.0.1:5000"; // Flask server URL

// Simulated Fingerprint Capture
async function captureFingerprint() {
    return new Promise((resolve) => {
        setTimeout(() => {
            const fingerprintData = "fingerprint_" + Math.floor(Math.random() * 100000);
            resolve(fingerprintData);
        }, 2000); // Simulated 2s fingerprint scan
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
