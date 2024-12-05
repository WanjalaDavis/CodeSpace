document.addEventListener('DOMContentLoaded', function() {
    const callButtons = document.querySelectorAll('.call-btn');
    const callNotification = document.getElementById('call-notification');
    const acceptCallBtn = document.getElementById('accept-call');
    const rejectCallBtn = document.getElementById('reject-call');

    // Create WebSocket connection
    const socket = new WebSocket('ws://' + window.location.host + '/ws/call/');

    // Handle call notification for the recipient
    socket.onmessage = function(event) {
        const message = JSON.parse(event.data);

        if (message.type === 'call') {
            // Show the call notification modal
            document.getElementById('call-notification-text').innerText = `${message.caller_name} is calling you!`;
            callNotification.style.display = 'block';

            // Handle accept or reject
            acceptCallBtn.onclick = function() {
                socket.send(JSON.stringify({
                    'type': 'accept_call',
                    'caller_id': message.caller_id
                }));
                window.location.href = '/call/' + message.caller_id; // Redirect to call page
            };

            rejectCallBtn.onclick = function() {
                socket.send(JSON.stringify({
                    'type': 'reject_call',
                    'caller_id': message.caller_id
                }));
                callNotification.style.display = 'none'; // Close the notification
            };
        }
    };

    // Initiate call when the "Call" button is clicked
    callButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const userId = button.getAttribute('data-user-id');
            const username = button.getAttribute('data-username');

            // Send call notification to the user
            socket.send(JSON.stringify({
                'type': 'call',
                'receiver_id': userId,
                'caller_name': username
            }));
        });
    });
});


const localVideo = document.getElementById('localVideo');
const remoteVideos = document.getElementById('remoteVideos');
const participantList = document.getElementById('participantList');

// Dummy function to simulate adding participants
function addParticipant(name) {
    const li = document.createElement('li');
    li.classList.add('list-group-item');
    li.textContent = name;
    participantList.appendChild(li);
}

// Example: Simulating participants joining
addParticipant("Alice");
addParticipant("Bob");
const canvas = document.getElementById('whiteboard');
const ctx = canvas.getContext('2d');
let drawing = false;

canvas.width = 800;
canvas.height = 600;

canvas.addEventListener('mousedown', () => drawing = true);
canvas.addEventListener('mouseup', () => drawing = false);
canvas.addEventListener('mousemove', draw);

function draw(event) {
    if (!drawing) return;
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.strokeStyle = 'black';

    ctx.lineTo(event.clientX - canvas.offsetLeft, event.clientY - canvas.offsetTop);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(event.clientX - canvas.offsetLeft, event.clientY - canvas.offsetTop);
}
const shareScreenButton = document.getElementById('shareScreen');

shareScreenButton.addEventListener('click', async () => {
    try {
        const stream = await navigator.mediaDevices.getDisplayMedia();
        const videoElement = document.createElement('video');
        videoElement.srcObject = stream;
        videoElement.play();
        remoteVideos.appendChild(videoElement);
    } catch (error) {
        console.error("Error sharing screen:", error);
    }
});
function toggleMute(participantId) {
    // Placeholder for real mute logic
    console.log(`Toggled mute for ${participantId}`);
}
