function login() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    let formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            window.location.href = "upload.html";
        } else {
            document.getElementById("login-msg").innerText = "Login Failed";
        }
    });
}

function detectFall() {
    let fileInput = document.getElementById("image");
    let file = fileInput.files[0];

    let formData = new FormData();
    formData.append("file", file);

    fetch("http://127.0.0.1:8000/detect-fall", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("result").innerText =
            data.result + " – " + data.message;
    });
}
