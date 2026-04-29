let editingId = null;

async function login() {
    const username = document.getElementById("loginUsername").value;
    const password = document.getElementById("loginPassword").value;

    const response = await fetch("/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, password})
    });

    const result = await response.json();

    if (result.success) {
        document.getElementById("loginPage").style.display = "none";
        document.getElementById("appPage").style.display = "block";
        loadFlightLogs();
    } else {
        document.getElementById("loginMessage").innerText = result.message;
    }
}

async function logout() {
    await fetch("/logout", {method: "POST"});

    document.getElementById("loginPage").style.display = "block";
    document.getElementById("appPage").style.display = "none";
}

async function loadFlightLogs() {
    const searchFlightID = document.getElementById("searchFlightID").value;

    let url = "/flightlogs";

    if (searchFlightID) {
        url = "/flightlogs?flightID=" + encodeURIComponent(searchFlightID);
    }

    const response = await fetch(url);
    const logs = await response.json();

    const table = document.getElementById("flightLogTable");
    table.innerHTML = "";

    logs.forEach(log => {
        table.innerHTML += `
            <tr>
                <td>${log.id}</td>
                <td>${log.tailNumber}</td>
                <td>${log.flightID}</td>
                <td>${log.takeoff}</td>
                <td>${log.landing}</td>
                <td>${log.duration}</td>
                <td>
                    <button onclick='editFlightLog(${JSON.stringify(log)})'>Edit</button>
                    <button class="delete" onclick="deleteFlightLog(${log.id})">Delete</button>
                </td>
            </tr>
        `;
    });
}

async function saveFlightLog() {
    const data = {
        tailNumber: document.getElementById("tailNumber").value,
        flightID: document.getElementById("flightID").value,
        takeoff: document.getElementById("takeoff").value,
        landing: document.getElementById("landing").value,
        duration: document.getElementById("duration").value
    };

    let url = "/flightlogs";
    let method = "POST";

    if (editingId !== null) {
        url = "/flightlogs/" + editingId;
        method = "PUT";
    }

    await fetch(url, {
        method: method,
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    });

    clearForm();
    loadFlightLogs();

    document.getElementById("formMessage").innerText = "Flight log saved successfully.";
}

function editFlightLog(log) {
    editingId = log.id;

    document.getElementById("formTitle").innerText = "Update Flight Log";
    document.getElementById("tailNumber").value = log.tailNumber;
    document.getElementById("flightID").value = log.flightID;
    document.getElementById("takeoff").value = log.takeoff;
    document.getElementById("landing").value = log.landing;
    document.getElementById("duration").value = log.duration;
}

async function deleteFlightLog(id) {
    if (!confirm("Delete this flight log?")) {
        return;
    }

    await fetch("/flightlogs/" + id, {
        method: "DELETE"
    });

    loadFlightLogs();
}

function clearForm() {
    editingId = null;

    document.getElementById("formTitle").innerText = "Create Flight Log";
    document.getElementById("tailNumber").value = "";
    document.getElementById("flightID").value = "";
    document.getElementById("takeoff").value = "";
    document.getElementById("landing").value = "";
    document.getElementById("duration").value = "";
}

function clearSearch() {
    document.getElementById("searchFlightID").value = "";
    loadFlightLogs();
}

async function createUser() {
    const username = document.getElementById("newUsername").value;
    const password = document.getElementById("newPassword").value;

    const response = await fetch("/users", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, password})
    });

    const result = await response.json();

    if (result.success) {
        document.getElementById("userMessage").innerText = "User created successfully.";
    } else {
        document.getElementById("userMessage").innerText = result.message;
    }
}
