/**
 * 主要JavaScript逻辑
 */

// 模型选项配置
const modelOptions = {
    "deepseek": [
        {value: "deepseek-chat", text: "DeepSeek Chat"},
        {value: "deepseek-reasoner", text: "DeepSeek Reasoner"}
    ],
    "openai": [
        {value: "gpt-4o", text: "GPT-4o"},
        {value: "gpt-4o-mini", text: "GPT-4o mini"}
    ]
};

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化模式选择器
    initModeSelector();
    
    // 初始化模型选择器
    initModelSelector();
    
    // 同步轮次选择器
    syncRoundSelectors();
    
    // 绑定按钮事件
    document.getElementById('start-button').addEventListener('click', handleStartButtonClick);
    
    // 绑定流式输出切换事件
    document.getElementById('stream-toggle').addEventListener('change', function() {
        // 在切换时可以添加一些额外逻辑
        console.log('流式输出状态:', this.checked);
    });
});

// 同步轮次选择器
function syncRoundSelectors() {
    const debateRounds = document.getElementById('rounds');
    const chatRounds = document.getElementById('chat-rounds');
    
    if (debateRounds && chatRounds) {
        // 确保两个选择器有相同的选项
        debateRounds.addEventListener('change', function() {
            chatRounds.value = this.value;
        });
        
        chatRounds.addEventListener('change', function() {
            debateRounds.value = this.value;
        });
    }
}

// 初始化模型选择器
function initModelSelector() {
    const providerSelect = document.getElementById('provider-select');
    const modelSelect = document.getElementById('model-select');
    
    // 首次加载默认提供商的模型
    updateModelOptions(providerSelect.value);
    
    // 当提供商改变时更新模型选项
    providerSelect.addEventListener('change', function() {
        updateModelOptions(this.value);
    });
    
    // 更新模型选项的函数
    function updateModelOptions(provider) {
        // 清空当前选项
        modelSelect.innerHTML = '';
        
        // 添加新选项
        if (modelOptions[provider]) {
            modelOptions[provider].forEach(model => {
                const option = document.createElement('option');
                option.value = model.value;
                option.textContent = model.text;
                modelSelect.appendChild(option);
            });
        }
    }
}

// 初始化模式选择器
function initModeSelector() {
    const modeOptions = document.querySelectorAll('.mode-option');
    const debateSettings = document.getElementById('debate-settings');
    const chatSettings = document.getElementById('chat-settings');
    const qaSettings = document.getElementById('qa-settings');
    
    // 设置初始状态
    setActiveMode('debate');
    
    // 为每个选项添加点击事件
    modeOptions.forEach(option => {
        option.addEventListener('click', function() {
            const mode = this.getAttribute('data-mode');
            setActiveMode(mode);
        });
    });
    
    // 设置激活的模式
    function setActiveMode(mode) {
        // 更新按钮状态
        modeOptions.forEach(opt => {
            if (opt.getAttribute('data-mode') === mode) {
                opt.classList.add('active');
            } else {
                opt.classList.remove('active');
            }
        });
        
        // 更新设置面板可见性
        debateSettings.style.display = mode === 'debate' ? 'block' : 'none';
        chatSettings.style.display = mode === 'chat' ? 'block' : 'none';
        qaSettings.style.display = mode === 'qa' ? 'block' : 'none';
        
        // 更新按钮文本和图标
        const startButton = document.getElementById('start-button');
        if (mode === 'debate') {
            startButton.innerHTML = '<i class="fas fa-play mr-2"></i>开始辩论';
            document.getElementById('topic-label').textContent = '辩论主题';
            document.getElementById('topic').placeholder = ' ';
        } else if (mode === 'chat') {
            startButton.innerHTML = '<i class="fas fa-comments mr-2"></i>开始对话';
            document.getElementById('topic-label').textContent = '对话主题';
            document.getElementById('topic').placeholder = ' ';
        } else if (mode === 'qa') {
            startButton.innerHTML = '<i class="fas fa-question mr-2"></i>提交问题';
            document.getElementById('topic-label').textContent = '问题';
            document.getElementById('topic').placeholder = ' ';
        }
    }
}

// 处理开始按钮点击事件
async function handleStartButtonClick() {
    // 获取当前激活的模式
    const activeMode = document.querySelector('.mode-option.active').getAttribute('data-mode');
    
    // 获取用户输入
    const topic = document.getElementById('topic').value.trim();
    if (!topic) {
        showNotification('请输入内容', 'error');
        showError('请输入内容');
        return;
    }
    
    // 清除错误信息
    document.getElementById('error').classList.add('hidden');
    
    // 显示加载状态
    const startButton = document.getElementById('start-button');
    const originalButtonText = startButton.innerHTML;
    startButton.disabled = true;
    startButton.innerHTML = `
        <div class="flex items-center justify-center">
            <div class="w-3 h-3 bg-white rounded-full pulse mr-2"></div>
            <span>${getLoadingText(activeMode)}</span>
        </div>
    `;
    
    // 清除历史内容
    const historyContainer = document.getElementById('history');
    historyContainer.innerHTML = '';
    
    try {
        // 获取模型设置
        const provider = document.getElementById('provider-select').value;
        const model = document.getElementById('model-select').value;
        
        // 根据不同模式处理
        if (activeMode === 'debate') {
            // 辩论模式
            const rounds = parseInt(document.getElementById('rounds').value, 10);
            const streamMode = document.getElementById('stream-toggle').checked;
            
            if (streamMode) {
                await streamDebate(topic, rounds, historyContainer, provider, model);
            } else {
                await regularDebate(topic, rounds, historyContainer, provider, model);
            }
        } else if (activeMode === 'chat') {
            // 对话模式
            const rounds = parseInt(document.getElementById('chat-rounds').value, 10);
            const role1 = document.getElementById('role1').value;
            const role2 = document.getElementById('role2').value;
            const streamMode = document.getElementById('stream-toggle').checked;
            
            await startChat(topic, rounds, historyContainer, role1, role2, streamMode, provider, model);
        } else if (activeMode === 'qa') {
            // 问答模式
            const style = document.getElementById('qa-style').value;
            
            await processQuestion(topic, style, historyContainer, provider, model);
        }
        
        // 显示成功通知
        showNotification('处理完成！', 'success');
        
    } catch (error) {
        console.error('处理请求失败:', error);
        showError(error.message || '发生错误，请重试');
        showNotification('处理失败: ' + (error.message || '未知错误'), 'error');
    } finally {
        // 恢复按钮状态
        startButton.disabled = false;
        startButton.innerHTML = originalButtonText;
    }
}

// 获取加载文本
function getLoadingText(mode) {
    switch (mode) {
        case 'debate':
            return '正在生成辩论...';
        case 'chat':
            return '正在生成对话...';
        case 'qa':
            return '正在思考问题...';
        default:
            return '处理中...';
    }
} 