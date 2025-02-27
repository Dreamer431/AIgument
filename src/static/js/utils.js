/**
 * 实用工具函数
 */

// 打字机效果函数
function typeWriter(element, text, speed = 10) {
    // 检查是否包含markdown格式，如果包含则先通过marked解析
    const parsedText = marked.parse(text);
    
    // 设置内容
    element.innerHTML = parsedText;
    
    // 应用代码高亮
    element.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
    
    // 添加打字机动画类
    element.classList.add('typing-effect');
    
    // 一段时间后移除动画类
    setTimeout(() => {
        element.classList.remove('typing-effect');
    }, text.length * speed + 1000);
}

// 显示错误信息
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
    
    // 添加动画类
    errorDiv.classList.add('animate__animated', 'animate__shakeX');
    
    // 移除动画类以便将来可以再次触发
    setTimeout(() => {
        errorDiv.classList.remove('animate__animated', 'animate__shakeX');
    }, 1000);
} 