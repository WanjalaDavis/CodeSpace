    // Dark mode toggle functionality
const themeToggleButton = document.getElementById('themeToggle');
const body = document.body;

themeToggleButton.addEventListener('click', () => {
 body.classList.toggle('dark-theme');
  if (body.classList.contains('dark-theme')) {
           themeToggleButton.innerHTML = '<i class="fas fa-eye-slash"></i>';
        } else {
            themeToggleButton.innerHTML = '<i class="fas fa-eye"></i>';
        }
    });

    // Initialize Ace editor
    var editor = ace.edit("editor");
    editor.setTheme("ace/theme/monokai");
    editor.session.setMode("ace/mode/python");  // Default to Python mode

    // Toggle between Python and Java modes
    function switchLanguage(language) {
        if (language === 'python') {
            editor.session.setMode("ace/mode/python");
        } else if (language === 'java') {
            editor.session.setMode("ace/mode/java");
        }
    }

    // Execute code (Python or Java)
document.getElementById('runBtn').addEventListener('click', function() {
const code = editor.getValue();
const language = editor.session.getMode().$id.includes('python') ? 'python' : 'java';

        // Send the code to Django backend for execution
        axios.post('/execute_code/', { code: code, language: language })
            .then(response => {
                alert('Code executed successfully: ' + response.data.result);
            })
            .catch(error => {
                alert('Error executing code: ' + error.response.data.error);
            });
    });

    // Save the file
document.getElementById('saveFileForm').addEventListener('submit', function(e) {
 e.preventDefault();
const fileName = document.getElementById('fileName').value;
const fileContent = editor.getValue();

        // Send the file content to Django backend for saving
        axios.post('/save_file/', { file_name: fileName, content: fileContent })
            .then(response => {
                alert('File saved successfully');
                loadFiles();  // Reload the list of project files
            })
            .catch(error => {
                alert('Error saving file: ' + error.response.data.error);
            });
    });

    // Load project files based on the project ID
    function loadFiles(projectId) {
        axios.get(`/project_files/${projectId}/`)
            .then(response => {
                const fileList = document.getElementById('fileList');
                fileList.innerHTML = '';
                response.data.files.forEach(file => {
                    const fileDiv = document.createElement('div');
                    fileDiv.innerHTML = `<a href="#" onclick="loadFile('${file}')">${file}</a>`;
                    fileList.appendChild(fileDiv);
                });
            })
            .catch(error => {
                alert('Error loading files: ' + error.response.data.error);
            });
    }

    // Load a specific file into the editor
    function loadFile(fileName) {
        axios.get(`/load_file/${fileName}`)
            .then(response => {
                editor.setValue(response.data.content, -1);  // -1 keeps the cursor position at the start
                const fileExtension = fileName.split('.').pop();
                if (fileExtension === 'java') {
                    switchLanguage('java');
                } else if (fileExtension === 'py') {
                    switchLanguage('python');
                }
            })
            .catch(error => {
                alert('Error loading file: ' + error.response.data.error);
            });
    }