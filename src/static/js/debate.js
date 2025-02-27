/**
 * 辩论模式相关功能
 */

// 常规非流式辩论
async function regularDebate(topic, rounds, historyContainer) {
    try {
        // 创建轮次容器
        let roundContainers = {};
        for (let i = 1; i <= rounds; i++) {
            const roundContainer = document.createElement('div');
            roundContainer.className = 'mb-6 animate__animated animate__fadeIn';
            roundContainer.style.animationDelay = `${(i-1)*0.3}s`;
            roundContainer.innerHTML = `<h3 class="text-lg font-semibold mb-3">第 ${i} 轮</h3>`;
            historyContainer.appendChild(roundContainer);
            roundContainers[i] = roundContainer;
        }
        
        let currentMessage = topic;
        
        // 逐轮生成辩论内容
        for (let round = 1; round <= rounds; round++) {
            // 创建正方容器
            const positiveKey = `${round}-正方`;
            const positiveElement = document.createElement('div');
            positiveElement.className = `card p-6 mb-4 animate__animated animate__fadeIn`;
            positiveElement.style.animationDelay = `${(round-1)*0.3 + 0.1}s`;
            
            positiveElement.innerHTML = `
                <h4 class="text-lg font-semibold mb-2 text-blue-600">正方观点</h4>
                <div id="content-${positiveKey}" class="text-gray-700 markdown-content">
                    <div class="flex items-center space-x-2">
                        <div class="w-3 h-3 bg-blue-500 rounded-full pulse"></div>
                        <span>正在生成中...</span>
                    </div>
                </div>
            `;
            roundContainers[round].appendChild(positiveElement);
            
            // 发起正方API请求
            const positiveResponse = await fetch('/api/debate/single', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    topic: currentMessage, 
                    side: '正方',
                    round: round
                })
            });
            
            if (!positiveResponse.ok) {
                throw new Error(`正方发言请求失败: ${positiveResponse.statusText}`);
            }
            
            const positiveData = await positiveResponse.json();
            const positiveContent = positiveData.content;
            
            // 显示正方观点
            const positiveContentElement = document.getElementById(`content-${positiveKey}`);
            positiveContentElement.innerHTML = '';
            typeWriter(positiveContentElement, positiveContent);
            
            // 等待正方观点显示完毕
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // 更新当前消息为正方的回应，用于反方回应
            currentMessage = positiveContent;
            
            // 创建反方容器
            const negativeKey = `${round}-反方`;
            const negativeElement = document.createElement('div');
            negativeElement.className = `card p-6 mb-4 animate__animated animate__fadeIn`;
            negativeElement.style.animationDelay = `${(round-1)*0.3 + 0.2}s`;
            
            negativeElement.innerHTML = `
                <h4 class="text-lg font-semibold mb-2 text-red-600">反方观点</h4>
                <div id="content-${negativeKey}" class="text-gray-700 markdown-content">
                    <div class="flex items-center space-x-2">
                        <div class="w-3 h-3 bg-red-500 rounded-full pulse"></div>
                        <span>正在生成中...</span>
                    </div>
                </div>
            `;
            roundContainers[round].appendChild(negativeElement);
            
            // 发起反方API请求
            const negativeResponse = await fetch('/api/debate/single', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    topic: currentMessage, 
                    side: '反方',
                    round: round
                })
            });
            
            if (!negativeResponse.ok) {
                throw new Error(`反方发言请求失败: ${negativeResponse.statusText}`);
            }
            
            const negativeData = await negativeResponse.json();
            const negativeContent = negativeData.content;
            
            // 显示反方观点
            const negativeContentElement = document.getElementById(`content-${negativeKey}`);
            negativeContentElement.innerHTML = '';
            typeWriter(negativeContentElement, negativeContent);
            
            // 等待反方观点显示完毕，然后进入下一轮
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // 更新当前消息为反方的回应，用于下一轮
            currentMessage = negativeContent;
        }
        
    } catch (error) {
        console.error('非流式辩论请求失败:', error);
        showError(error.message || '生成辩论内容时出错');
    }
}

// 流式辩论
async function streamDebate(topic, rounds, historyContainer) {
    try {
        // 初始化辩论
        const initResponse = await fetch('/api/debate/init', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic, rounds })
        });

        if (!initResponse.ok) {
            const error = await initResponse.json();
            throw new Error(error.message || '初始化辩论失败');
        }
        
        // 创建轮次容器
        let roundContainers = {};
        for (let i = 1; i <= rounds; i++) {
            const roundContainer = document.createElement('div');
            roundContainer.className = 'mb-6 animate__animated animate__fadeIn';
            roundContainer.style.animationDelay = `${(i-1)*0.3}s`;
            roundContainer.innerHTML = `<h3 class="text-lg font-semibold mb-3">第 ${i} 轮</h3>`;
            historyContainer.appendChild(roundContainer);
            roundContainers[i] = roundContainer;
        }
        
        // 为每轮每个辩论方创建内容容器
        let contentElements = {};
        for (let round = 1; round <= rounds; round++) {
            for (let side of ['正方', '反方']) {
                const key = `${round}-${side}`;
                const viewElement = document.createElement('div');
                viewElement.className = `card p-6 mb-4 animate__animated animate__fadeIn`;
                viewElement.style.animationDelay = `${(round-1)*0.3 + (side==='正方'?0.1:0.2)}s`;
                
                const sideClass = side === '正方' ? 'text-blue-600' : 'text-red-600';
                viewElement.innerHTML = `
                    <h4 class="text-lg font-semibold mb-2 ${sideClass}">${side}观点</h4>
                    <div id="content-${key}" class="text-gray-700 markdown-content">
                        <div class="flex items-center space-x-2">
                            <div class="w-3 h-3 bg-${side === '正方' ? 'blue' : 'red'}-500 rounded-full pulse"></div>
                            <span>正在思考中...</span>
                        </div>
                    </div>
                `;
                roundContainers[round].appendChild(viewElement);
                contentElements[key] = document.getElementById(`content-${key}`);
            }
        }
        
        // 开始流式接收辩论内容
        const eventSource = new EventSource(`/api/debate/stream?topic=${encodeURIComponent(topic)}&rounds=${rounds}`);
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'content') {
                const key = `${data.round}-${data.side}`;
                const contentElement = contentElements[key];
                
                // 使用打字机效果逐步显示内容
                if (contentElement) {
                    // 如果是第一次更新内容，清除"正在思考中..."的提示
                    if (contentElement.querySelector('.pulse')) {
                        contentElement.innerHTML = '';
                    }
                    
                    // 使用打字机效果显示内容
                    contentElement.innerHTML = marked.parse(data.content);
                    
                    // 应用代码高亮
                    contentElement.querySelectorAll('pre code').forEach((block) => {
                        hljs.highlightElement(block);
                    });
                }
            }
        };
        
        eventSource.onerror = (error) => {
            console.error('EventSource错误:', error);
            eventSource.close();
            showError('辩论流式生成过程中发生错误，请重试');
        };
        
        // 当辩论完成时关闭事件源
        eventSource.addEventListener('debate_complete', (event) => {
            eventSource.close();
        });
        
        return new Promise((resolve) => {
            eventSource.addEventListener('debate_complete', () => {
                resolve();
            });
        });
    } catch (error) {
        console.error('流式辩论请求失败:', error);
        showError(error.message || '生成辩论内容时出错');
    }
}

// 逐步显示辩论历史（带有动画效果）
async function renderDebateHistoryWithAnimation(history) {
    // 按时间顺序逐个显示
    for (const item of history) {
        const key = `${item.round}-${item.side}`;
        const contentElement = document.getElementById(`content-${key}`);
        
        if (contentElement) {
            // 清除加载指示器
            contentElement.innerHTML = '';
            
            // 使用打字机效果显示内容
            typeWriter(contentElement, item.content);
            
            // 等待一段时间再显示下一个，模拟真实辩论过程
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    }
}

// 渲染辩论历史
function renderDebateHistory(history, container) {
    // 按轮次分组
    const rounds = {};
    history.forEach(item => {
        if (!rounds[item.round]) {
            rounds[item.round] = [];
        }
        rounds[item.round].push(item);
    });
    
    // 渲染每一轮
    for (const [round, items] of Object.entries(rounds)) {
        const roundContainer = document.createElement('div');
        roundContainer.className = 'mb-6 animate__animated animate__fadeIn';
        roundContainer.innerHTML = `<h3 class="text-lg font-semibold mb-3">第 ${round} 轮</h3>`;
        container.appendChild(roundContainer);
        
        // 渲染该轮的观点
        items.forEach(item => {
            const viewElement = document.createElement('div');
            viewElement.className = 'card p-6 mb-4 animate__animated animate__fadeIn';
            
            const sideClass = item.side === '正方' ? 'text-blue-600' : 'text-red-600';
            viewElement.innerHTML = `
                <h4 class="text-lg font-semibold mb-2 ${sideClass}">${item.side}观点</h4>
                <div class="text-gray-700 markdown-content">${marked.parse(item.content)}</div>
            `;
            
            roundContainer.appendChild(viewElement);
            
            // 应用代码高亮
            viewElement.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
        });
    }
} 