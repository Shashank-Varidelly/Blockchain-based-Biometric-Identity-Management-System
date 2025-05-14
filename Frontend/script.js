const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
const result = document.getElementById('result');
const fileHashLink = document.getElementById('fileHashLink');

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => video.srcObject = stream)
    .catch(err => {
        console.error('Error accessing webcam:', err);
        result.textContent = 'Error: Could not access webcam';
    });

function captureImage() {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg');
}

document.getElementById('registerBtn').addEventListener('click', () => {
    const name = document.getElementById('name').value.trim();
    const age = document.getElementById('age').value;
    const gender = document.getElementById('gender').value;
    const image = captureImage();

    if (!name || !age || !gender) {
        result.textContent = 'Please fill all fields';
        console.log('Missing fields:', { name, age, gender });
        return;
    }
    console.log('Register button clicked', { name, age, gender });

    sendRegisterRequest(name, age, gender, image);
});

function sendRegisterRequest(name, age, gender, image) {
    const requestData = { image, name, age, gender };
    console.log('Sending registration request:', requestData);

    fetch('http://127.0.0.1:5000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        console.log('Register response status:', response.status, response.statusText);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status} ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Register response data:', data);
        result.textContent = data.message || 'No message returned';
    })
    .catch(error => {
        console.error('Registration error:', error.message);
        result.textContent = `Error: Registration failed - ${error.message}`;
    });
}

document.getElementById('loginBtn').addEventListener('click', () => {
    const image = captureImage();
    console.log('Login button clicked with image data');

    fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image })
    })
    .then(response => {
        console.log('Login response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Login response data:', data);
        if (data.details) {
            result.textContent = data.message;
            fileHashLink.style.display = 'block';
            fileHashLink.textContent = `Face Hash: ${data.details.face_hash}`;
            // Store user data
            const userData = {
                name: data.details.name || 'Unknown',
                age: data.details.age || 'N/A',
                gender: data.details.gender || 'N/A',
                face_hash: data.details.face_hash || 'N/A'
            };
            console.log('Storing userData in localStorage:', userData);
            localStorage.setItem('userData', JSON.stringify(userData));
            // Delay redirection to ensure localStorage is updated
            setTimeout(() => {
                console.log('Redirecting to dashboard.html');
                window.location.href = 'dashboard.html';
            }, 1000);
        } else {
            result.textContent = data.message || 'Login failed';
            fileHashLink.style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Login error:', error.message);
        result.textContent = `Error: Login failed - ${error.message}`;
    });
});