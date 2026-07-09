document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const promptInput = document.getElementById('prompt-input');
    const btnExecute = document.getElementById('btn-execute');
    const liveStatus = document.getElementById('live-status');
    const progressIndicator = document.getElementById('progress-indicator');
    const jsonOutput = document.getElementById('json-output');

    const statusPlanner = document.getElementById('status-planner').querySelector('.indicator');
    const statusExecutor = document.getElementById('status-executor').querySelector('.indicator');
    const statusOllama = document.getElementById('status-ollama').querySelector('.indicator');
    const statusActive = document.getElementById('status-active').querySelector('.indicator');

    // Live clock update
    function updateClock() {
        const now = new Date();
        const timeStr = now.toTimeString().split(' ')[0];
        document.getElementById('live-clock').textContent = timeStr;
    }
    setInterval(updateClock, 1000);
    updateClock();

    // Event listener for execute mission button
    btnExecute.addEventListener('click', () => {
        const promptText = promptInput.value.trim();
        if (!promptText) return;

        btnExecute.disabled = true;
        btnExecute.querySelector('span').textContent = 'Sending command...';

        fetch('/send_prompt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: promptText })
        })
        .then(response => response.json())
        .then(data => {
            btnExecute.disabled = false;
            btnExecute.querySelector('span').textContent = 'Execute Mission';
            if (data.success) {
                promptInput.value = '';
            } else {
                alert('Error processing prompt: ' + data.error);
            }
        })
        .catch(err => {
            btnExecute.disabled = false;
            btnExecute.querySelector('span').textContent = 'Execute Mission';
            console.error('Network Error:', err);
            alert('Failed to connect to backend server.');
        });
    });

    // Establish Server-Sent Events (SSE) stream
    const eventSource = new EventSource('/status_stream');

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        // Update system connection indicator states
        updateIndicator(statusPlanner, data.planner_connected);
        updateIndicator(statusExecutor, data.executor_connected);
        updateIndicator(statusOllama, data.ollama_connected);
        updateIndicator(statusActive, data.mission_active);

        // Update live status text and progress bar
        if (data.status) {
            liveStatus.textContent = data.status;
            
            if (data.status === 'IDLE') {
                progressIndicator.style.width = '0%';
            } else if (data.status.startsWith('RUNNING')) {
                progressIndicator.style.width = '60%';
                progressIndicator.style.background = 'linear-gradient(to right, var(--primary-color), var(--accent-success))';
            } else if (data.status === 'SUCCESS') {
                progressIndicator.style.width = '100%';
                progressIndicator.style.background = 'var(--accent-success)';
            } else if (data.status === 'CANCELLED') {
                progressIndicator.style.width = '100%';
                progressIndicator.style.background = 'var(--text-muted)';
            } else if (data.status.startsWith('FAILED') || data.status.startsWith('REJECTED')) {
                progressIndicator.style.width = '100%';
                progressIndicator.style.background = 'var(--accent-danger)';
            }
        }

        // Display updated JSON structure
        if (data.json) {
            try {
                const formattedJson = JSON.stringify(JSON.parse(data.json), null, 4);
                jsonOutput.textContent = formattedJson;
            } catch (e) {
                jsonOutput.textContent = data.json;
            }
        } else if (data.status.startsWith('RUNNING')) {
            // Keep current JSON structure displayed during execution
        } else {
            jsonOutput.textContent = '// Awaiting next mission request...';
        }
    };

    eventSource.onerror = (err) => {
        console.error('SSE connection lost:', err);
        // Reset all states to offline/disconnected
        updateIndicator(statusPlanner, false);
        updateIndicator(statusExecutor, false);
        updateIndicator(statusOllama, false);
        updateIndicator(statusActive, false);
        liveStatus.textContent = 'DISCONNECTED';
        progressIndicator.style.width = '0%';
    };

    function updateIndicator(element, connected) {
        if (connected) {
            element.classList.remove('red');
            element.classList.add('green');
        } else {
            element.classList.remove('green');
            element.classList.add('red');
        }
    }
});
