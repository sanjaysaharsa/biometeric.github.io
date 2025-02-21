const serverURL = "http://127.0.0.1:5000"; // Flask server URL

// WebAuthn Fingerprint Capture
async function captureFingerprint() {
    try {
        // Requesting the device to scan the fingerprint using WebAuthn
        const credential = await navigator.credentials.create({
            publicKey: {
                challenge: new Uint8Array(32), // Random challenge
                rp: { name: "Fingerprint Attendance System" },
                user: { 
                    id: new Uint8Array(16), 
                    name: document.getElementById("rollNumber").value, 
                    displayName: document.getElementById("name").value 
                },
                pubKeyCredParams: [{ type: "public-key", alg: -7 }],
                authenticatorSelection: { authenticatorAttachment: "platform" },
                timeout: 60000 // Timeout of 1 minute for the fingerprint scan
            }
        });

        return credential.id; // Return fingerprint data (credential ID)
    } catch (error) {
        console.error("Fingerprint scan failed:", error);
        alert("Fingerprint scan failed.");
        return null;
    }
}

// Register Student with Fingerprint
async function registerStudent() {
    const name = document.getElementById("name").value;
    const rollNumber = document.getElementById("rollNumber").value;
    const bloodGroup = document.getElementById("bloodGroup").value;
    const classValue = document.getElementById("class").value;
    const academicYear = document.getElementById("academicYear").value;

    document.getElementById("registerStatus").style.display = "block";

    // Real fingerprint capture using WebAuthn
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
        let response = await fetch("http://127.0.0.1:5000/register", {
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
