// 基于chat.js修改，确保使用每日挑战的特殊逻辑
document.addEventListener('DOMContentLoaded', function () {
    const chatDisplay = document.getElementById('chatDisplay');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const resetButton = document.getElementById('resetButton');
    const trustValue = document.getElementById('trustValue');
    const trustBar = document.getElementById('trustBar');
    const turnCount = document.getElementById('turnCount').querySelector('span');
    const hintText = document.getElementById('hintText');

    // 添加进度条元素
    const progressBar = document.createElement('div');
    progressBar.id = 'progressBar';
    progressBar.className = 'progress';
    progressBar.style.display = 'none';
    progressBar.style.height = '6px';
    progressBar.innerHTML = `
        <div class="progress-bar progress-bar-striped progress-bar-animated" 
             role="progressbar" 
             style="width: 100%; background-color: var(--primary-light);"></div>
    `;
    document.querySelector('.game-info').prepend(progressBar);

    // 初始系统消息
    appendMessage('System', '欢迎来到每日挑战!', 'system');
    appendMessage('System', `这是一个${document.querySelector('.daily-badge').textContent.replace('患者性格: ', '')}的患者。`, 'system');

    // 设置初始信任度进度条为绿色
    trustBar.className = 'progress-bar bg-success';
    updateTrust(100);

    // 聚焦输入框
    messageInput.focus();

    function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        // 显示用户消息
        appendMessage('医生', message, 'user');
        messageInput.value = '';

        // 显示加载状态
        progressBar.style.display = 'block';
        const progressInner = progressBar.querySelector('.progress-bar');
        progressInner.style.width = '100%';
        progressInner.style.transition = 'width 1.5s linear';

        hintText.textContent = '等待AI回复...';
        sendButton.disabled = true;

        // 发送到服务器
        fetch('/handle_daily_challenge/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: `message=${encodeURIComponent(message)}`
        })
            .then(response => response.json())
            .then(data => {
                if (data.win) {
                    handleWin(data.score, data.disease);
                } else if (data.game_over) {
                    appendMessage('System', data.reply, 'system');
                    showGameOverModal();
                } else {
                    // 显示AI回复
                    appendMessage('病人', data.reply, 'assistant');
                    updateTrust(data.trust);
                }
            })
            .catch(error => {
                console.error('请求失败:', error);
                appendMessage('System', '请求失败: ' + error.message, 'system');
            })
            .finally(() => {
                // 隐藏进度条时添加淡出效果
                progressBar.style.opacity = '1';
                const fadeOut = () => {
                    progressBar.style.opacity = (parseFloat(progressBar.style.opacity) - 0.1).toString();
                    if (progressBar.style.opacity > '0') {
                        requestAnimationFrame(fadeOut);
                    } else {
                        progressBar.style.display = 'none';
                        progressBar.style.opacity = '1';
                        progressBar.querySelector('.progress-bar').style.width = '0%';
                    }
                };
                fadeOut();
                hintText.textContent = '轮到你发言了！';
                sendButton.disabled = false;
                messageInput.focus();
            });
    }

    function appendMessage(sender, message, type) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', type);

        const senderElement = document.createElement('span');
        senderElement.classList.add('sender');
        senderElement.textContent = `${sender}: `;

        const contentElement = document.createElement('span');
        contentElement.classList.add('content');
        contentElement.textContent = message;

        messageElement.appendChild(senderElement);
        messageElement.appendChild(contentElement);
        chatDisplay.appendChild(messageElement);

        // 滚动到底部
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }

    function updateTrust(value) {
        trustBar.style.width = `${value}%`;
        trustValue.textContent = `${value}%`;

        // 根据信任度改变颜色
        if (value > 70) {
            trustBar.className = 'progress-bar bg-success';
        } else if (value > 30) {
            trustBar.className = 'progress-bar bg-warning';
        } else {
            trustBar.className = 'progress-bar bg-danger';
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function handleWin(score, disease) {
        const leaderboardUrl = document.getElementById('leaderboardUrl').value;

        appendMessage('System', `恭喜你，猜对了病名！\n${disease}\n得分：${score}`, 'system');

        const winButton = document.createElement('a');
        winButton.href = leaderboardUrl;
        winButton.className = 'btn btn-success mt-2';
        winButton.innerHTML = '<i class="fas fa-trophy me-1"></i>查看排行榜';

        chatDisplay.appendChild(winButton);
        messageInput.disabled = true;
        sendButton.disabled = true;
    }

    function showGameOverModal() {
        const modal = new bootstrap.Modal(document.getElementById('gameOverModal'));
        modal.show();
    }

    // 事件监听
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    resetButton.addEventListener('click', function () {
        if (confirm('确定要放弃本次挑战吗？')) {
            const dailyChallengeUrl = document.getElementById('dailyChallengeUrl').value;
            window.location.href = dailyChallengeUrl;
        }
    });
});