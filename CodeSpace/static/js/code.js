// Initialize CodeMirror for the textarea
var editor = CodeMirror.fromTextArea(document.getElementById("code"), {
    mode: "xml",  // Use XML mode for HTML
    theme: "dracula",  // Optional theme
    lineNumbers: true,  // Show line numbers
    keyMap: "sublime",  // Optional keymap for keyboard shortcuts
    matchBrackets: true,  // Match brackets
    autoCloseTags: true,  // Automatically close HTML tags
    autoCloseBrackets: true,  // Automatically close brackets
    tabSize: 2,  // Set tab size
    indentUnit: 2,  // Indent unit size
    styleActiveLine: true,  // Highlight active line
    gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],  // Display line numbers and fold gutter
    foldGutter: true  // Enable code folding
});

// Function to update the live preview iframe
function updatePreview() {
    var iframe = document.getElementById("preview");
    var doc = iframe.contentDocument || iframe.contentWindow.document;
    doc.open();
    doc.write(editor.getValue());
    doc.close();
}

// Update preview on CodeMirror content change
editor.on("change", function () {
    updatePreview();
});

// Initial preview update on page load
updatePreview();

// Ensure content is saved properly on form submission
document.querySelector("form").addEventListener("submit", function () {
    var codeContent = editor.getValue();
    document.querySelector("#code").value = codeContent;
});



    const callButtons = document.querySelectorAll('.call-btn');
    callButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const username = btn.getAttribute('data-username');
        const userId = btn.getAttribute('data-user-id');

        // Logic to initiate WebRTC call
        alert(`Calling ${username}...`);

        // Redirect to call.html or start WebRTC signaling
        window.location.href = `/call/${userId}/`;
    });
});

     // JavaScript to handle liking a question
function likeQuestion(questionId) {
        fetch(`/question/${questionId}/like/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById(`likes-count-${questionId}`).innerText = data.likes_count;
        });
    }

    // JavaScript to handle liking a reply
function likeReply(replyId) {
        fetch(`/reply/${replyId}/like/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById(`reply-likes-count-${replyId}`).innerText = data.likes_count;
        });
    }

