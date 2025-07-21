
document.addEventListener('DOMContentLoaded', function () {
    const chatDisplay = document.getElementById('chatDisplay');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const resetButton = document.getElementById('resetButton');
    const progressBar = document.getElementById('progressBar');
    const hintText = document.getElementById('hintText');
    const turnCount = document.getElementById('turnCount');
    const trustBar = document.getElementById('trustBar');
    const trustValue = document.getElementById('trustValue');
    const gameOverModal = new bootstrap.Modal(document.getElementById('gameOverModal'), {
        backdrop: false
    });


    // 初始系统消息
    appendMessage('System', '欢迎来到医生模拟器!', 'system');
    fetch('/get_persona/')
        .then(response => response.json())
        .then(data => {
            if (data.persona) {
                appendMessage('System', `这是一个${data.persona}的家伙。`, 'system');
            }
        })
        .catch(error => {
            console.error('获取人格信息失败:', error);
            appendMessage('System', '无法获取病人人格信息，但游戏可以继续。', 'system');
        });

    // 设置初始信任度进度条为绿色
    trustBar.className = 'progress-bar bg-success';
    updateTrust(100);
    // 聚焦输入框
    messageInput.focus();

    // 发送消息
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 重置对话
    resetButton.addEventListener('click', function () {
        if (confirm('确定要清除当前对话记忆吗？这将开始一个新的游戏。')) {
            fetch('/handle_chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: 'reset=true'
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        chatDisplay.innerHTML = '';
                        appendMessage('System', '对话历史已清除，新的对话已准备开始。\n', 'system');
                        appendMessage('System', '欢迎来到医生模拟器!', 'system');
                        fetch('/get_persona/')
                            .then(response => response.json())
                            .then(data => {
                                if (data.persona) {
                                    appendMessage('System', `这是一个${data.persona}的家伙。`, 'system');
                                }
                            });
                        turnCount.textContent = '回合: 0';
                        updateTrust(data.trust || 100);
                    }
                })
                .catch(error => {
                    console.error('重置失败:', error);
                    appendMessage('System', '重置游戏失败，请刷新页面重试。', 'system');
                });
        }
    });

    function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        // 显示用户消息
        appendMessage('医生', message, 'user');
        messageInput.value = '';

        // 显示加载状态
        const progressBar = document.getElementById('progressBar');
        const progressInner = progressBar.querySelector('.progress-bar');
        progressBar.style.display = 'block';
        progressInner.style.width = '100%';
        progressInner.style.transition = 'width 1.5s linear'; // 启用过渡效果

        hintText.textContent = '等待AI回复...';
        sendButton.disabled = true;

        // 发送到服务器
        fetch('/handle_chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: `message=${encodeURIComponent(message)}`
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.win) {
                    // 游戏胜利
                    window.location.href = `/win/?score=${data.score}`;
                } else if (data.game_over) {
                    // 游戏结束
                    appendMessage('System', data.reply, 'system');
                    gameOverModal.show();
                } else {
                    // 显示AI回复
                    appendMessage('病人', data.reply, 'ai');
                    turnCount.textContent = `回合: ${data.turn}`;
                    updateTrust(data.trust);
                }
            })
            .catch(error => {
                console.error('请求失败:', error);
                appendMessage('System', '请求失败: ' + error.message, 'system');
                appendMessage('System', '请检查网络连接后重试', 'system');
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
                        progressInner.style.width = '0%'; // 重置进度条宽度
                    }
                };
                fadeOut();
                hintText.textContent = '轮到你发言了！';
                sendButton.disabled = false;
                messageInput.focus();
            });
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
});
