document.getElementById('submitButton').addEventListener('click', function() {
    const inputText = document.getElementById('inputText').value;

    fetch('http://klopta.vinnievirtuoso.online/api/rewrite', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: inputText })
    })
    .then(response => response.json())
    .then(data => {
        if (data.rewritten_text) {
            document.getElementById('responseWindow').innerText = data.rewritten_text;
        } else if (data.error) {
            document.getElementById('responseWindow').innerText = 'Error: ' + data.error;
        }
    })
    .catch(error => {
        document.getElementById('responseWindow').innerText = 'An error occurred:\n' + error;
    });
});
