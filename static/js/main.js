document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    socket.on('connect', () => {
        console.log('Connected to WebSocket');
    });

    socket.on('new_result', (results) => {
        const tableBody = document.getElementById('results-table');
        if (tableBody) {
            results.forEach(result => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="border px-4 py-2">${result.url}</td>
                    <td class="border px-4 py-2">${result.content}</td>
                    <td class="border px-4 py-2">${result.timestamp}</td>
                `;
                tableBody.prepend(row);
            });
        }
    });

    socket.on('status', (data) => {
        const startButton = document.querySelector('a[href="/start_monitoring"]');
        const stopButton = document.querySelector('a[href="/stop_monitoring"]');
        if (startButton && stopButton) {
            startButton.style.display = data.is_monitoring ? 'none' : 'block';
            stopButton.style.display = data.is_monitoring ? 'block' : 'none';
        }
    });
});
