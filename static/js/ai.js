const messages = document.querySelector('.messages');
const sendButton = document.getElementById('send-message');
const messageInput = document.getElementById('msg');
const result = document.getElementById('result');

sendButton.addEventListener('click', async () => {
    const message = messageInput.value.trim();
    const data = result.textContent.trim();

    if (!message) {
        return;
    }

    sendButton.disabled = true;

    try {
        const params = new URLSearchParams({
            message: message,
            data: data
        });

        messages.innerHTML += `
<div class='user-q'>
    <pre>${message}</pre>
</div>
`

        const response = await fetch(`/ai/send?${params.toString()}`);
        const raw = await response.text();

        const responseBox = document.createElement('div');
        responseBox.className = 'ai-response';

        const pre = document.createElement('pre');
        pre.textContent = raw;

        responseBox.appendChild(pre);
        messages.appendChild(responseBox);

        messageInput.value = '';
        messages.scrollTop = messages.scrollHeight;

        document.getElementById('msg').value = '';

    } catch (error) {
        console.error(error);
    } finally {
        sendButton.disabled = false;
    }
});