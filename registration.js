const serverURL = "https://your-deployed-url.onrender.com";

// Simulated Fingerprint Capture (Replace this with actual fingerprint hardware integration)
async function captureFingerprint() {
    return new Promise((resolve) => {
        setTimeout(() => {
            const fingerprintData = "fingerprint_" + Math.floor(Math.random() * 100000);
            resolve(fingerprintData);
        }, 2000); // Simulated 2s fingerprint scan
    });
}

// Register Student with Fingerprint
async function registerStudent() {
    const name = document.getElementById("name").value;
    const rollNumber = document.getElementById("rollNumber").value;
    const bloodGroup = document.getElementById("bloodGroup").value;
    const classValue = document.getElementById("class").value;
    const academicYear = document.getElementById("academicYear").value;

    document.getElementById("registerStatus").style.display = "block";

    let fingerprint = await captureFingerprint();
    if (!fingerprint) {
        alert("Fingerprint scan failed.");
        document.getElementById("registerStatus").style.display = "none";
        return;
    }

    const studentData = {
        name,
        rollNumber,
        bloodGroup,
        class: classValue,
        academicYear,
        fingerprint
    };

    try {
        let response = await fetch(`${serverURL}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(studentData)
        });

        let result = await response.json();
        alert(result.message);
        console.log(result);

    } catch (error) {
        console.error("Error registering student:", error);
        alert("Server error: Could not register student.");
    }

    document.getElementById("registerStatus").style.display = "none";
}
