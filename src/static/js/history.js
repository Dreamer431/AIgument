/**
 * 历史记录页面的JavaScript逻辑
 */

// 全局变量
let currentPage = 1;
let currentType = 'all';
let totalPages = 1;
let currentSessionId = null;

// 获取DOM元素
const sessionsContainer = document.getElementById('sessions-container');
const sessionModal = document.getElementById('session-modal');
const modalTitle = document.getElementById('modal-title');
const modalContent = document.getElementById('modal-content');
const closeBtn = document.querySelector('.close');

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化加载会话列表
    loadSessions();
    
    // 绑定类型切换按钮事件
    document.querySelectorAll('.session-type-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            // 更新按钮状态
            document.querySelectorAll('.session-type-btn').forEach(b => b.classList.remove('active', 'bg-blue-500', 'text-white'));
            document.querySelectorAll('.session-type-btn').forEach(b => b.classList.add('bg-gray-200'));
            this.classList.remove('bg-gray-200');
            this.classList.add('active', 'bg-blue-500', 'text-white');
            
            // 更新类型并重新加载
            currentType = this.dataset.type;
            currentPage = 1;
            loadSessions();
        });
    });
    
    // 绑定分页按钮事件
    document.getElementById('prev-page').addEventListener('click', function() {
        if (currentPage > 1) {
            currentPage--;
            loadSessions();
        }
    });
    
    document.getElementById('next-page').addEventListener('click', function() {
        if (currentPage < totalPages) {
            currentPage++;
            loadSessions();
        }
    });
});

// 加载会话列表
async function loadSessions() {
    try {
        sessionsContainer.innerHTML = '<div class="text-center py-8">加载中...</div>';
        
        // 构建请求URL
        let url = `/api/history?page=${currentPage}`;
        if (currentType !== 'all') {
            url += `&type=${currentType}`;
        }
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('获取历史记录失败');
        }
        
        const data = await response.json();
        
        // 更新分页信息
        totalPages = Math.ceil(data.history.length / 10);
        updatePagination();
        
        // 清空容器
        sessionsContainer.innerHTML = '';
        
        // 渲染会话卡片
        const startIndex = (currentPage - 1) * 10;
        const endIndex = startIndex + 10;
        const currentPageSessions = data.history.slice(startIndex, endIndex);
        
        currentPageSessions.forEach(session => {
            const card = createSessionCard(session);
            sessionsContainer.appendChild(card);
        });
        
        if (currentPageSessions.length === 0) {
            sessionsContainer.innerHTML = '<div class="text-center py-8 text-gray-500">暂无记录</div>';
        }
    } catch (error) {
        console.error('加载会话列表失败:', error);
        sessionsContainer.innerHTML = 
            '<div class="text-center py-8 text-red-500">加载失败，请刷新重试</div>';
    }
}

// 创建会话卡片
function createSessionCard(session) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-lg shadow-md p-6 mb-4 hover:shadow-lg transition-shadow';
    
    const date = new Date(session.start_time).toLocaleString('zh-CN');
    
    card.innerHTML = `
        <div class="flex justify-between items-start">
            <div>
                <h3 class="text-xl font-semibold mb-2">${session.topic}</h3>
                <div class="text-gray-600">
                    <span class="text-sm">${date}</span>
                    <span class="ml-4 text-sm">消息数：${session.message_count}</span>
                </div>
            </div>
            <div class="flex space-x-2">
                <button onclick="viewSessionDetail('${session.session_id}')" 
                        class="px-4 py-2 rounded bg-blue-500 text-white text-sm">
                    查看详情
                </button>
            </div>
        </div>
    `;
    
    return card;
}

// 更新分页控制
function updatePagination() {
    document.getElementById('page-info').textContent = `第 ${currentPage} / ${totalPages} 页`;
    document.getElementById('prev-page').disabled = currentPage <= 1;
    document.getElementById('next-page').disabled = currentPage >= totalPages;
}

// 查看会话详情
async function viewSessionDetail(sessionId) {
    try {
        currentSessionId = sessionId;
        const response = await fetch(`/api/history/${sessionId}`);
        if (!response.ok) {
            throw new Error('获取会话详情失败');
        }
        
        const data = await response.json();
        
        // 检查必要的 DOM 元素是否存在
        if (!modalTitle || !modalContent || !sessionModal) {
            console.error('找不到必要的 DOM 元素:', {
                modalTitle: !!modalTitle,
                modalContent: !!modalContent,
                sessionModal: !!sessionModal
            });
            throw new Error('找不到必要的 DOM 元素');
        }
        
        // 更新模态框内容
        if (data.messages && data.messages.length > 0) {
            modalTitle.textContent = data.messages[0].content || '未知主题';
            modalContent.innerHTML = '';
            
            // 添加消息记录
            data.messages.forEach(msg => {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'mb-4 p-4 border-l-4 border-blue-500';
                messageDiv.innerHTML = `
                    <div class="text-sm text-gray-600 mb-2">${msg.role}</div>
                    <div class="prose">${msg.content}</div>
                `;
                modalContent.appendChild(messageDiv);
            });
            
            // 显示模态框
            sessionModal.classList.remove('hidden');
        } else {
            throw new Error('没有找到会话消息');
        }
    } catch (error) {
        console.error('加载会话详情失败:', error);
        alert('加载详情失败：' + error.message);
    }
}

// 关闭模态框
function closeModal() {
    if (sessionModal) {
        sessionModal.classList.add('hidden');
    }
    currentSessionId = null;
}

// 导出会话
async function exportSession(format) {
    if (!currentSessionId) return;
    
    try {
        const response = await fetch(`/api/history/${currentSessionId}/export?format=${format}`);
        if (!response.ok) {
            throw new Error('导出失败');
        }
        
        if (format === 'json') {
            const data = await response.json();
            // 创建并下载JSON文件
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `session_${currentSessionId}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } else if (format === 'markdown') {
            const text = await response.text();
            // 创建并下载Markdown文件
            const blob = new Blob([text], { type: 'text/markdown' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `session_${currentSessionId}.md`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }
    } catch (error) {
        console.error('导出失败:', error);
        alert('导出失败，请重试');
    }
}

// 点击模态框外部关闭
window.onclick = function(event) {
    if (event.target == sessionModal) {
        closeModal();
    }
}

// 格式化日期时间
function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
} 