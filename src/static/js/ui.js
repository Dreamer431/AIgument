/**
 * UI交互和动画控制模块
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化UI动画
    initializeAnimations();

    // 初始化卡片悬停效果
    initializeHoverEffects();

    // 添加浮动标签效果
    initializeFloatingLabels();

    // 初始化页面元素
    initializePageElements();
    
    // 设置当前页面的底部导航高亮
    setActiveNavigation();
});

/**
 * 设置当前页面的底部导航高亮
 */
function setActiveNavigation() {
    // 获取当前页面的路径
    const currentPath = window.location.pathname;
    
    // 找到所有底部导航项
    const navItems = document.querySelectorAll('.bottom-nav .nav-item');
    
    // 移除所有激活状态
    navItems.forEach(item => {
        item.classList.remove('active');
    });
    
    // 根据当前路径设置激活状态
    if (currentPath === '/' || currentPath.includes('index.html')) {
        // 首页
        document.querySelector('.bottom-nav a[href="/"]')?.classList.add('active');
    } else if (currentPath.includes('history')) {
        // 暂时不需要高亮历史图标，因为我们已经移除了它
    }
}

/**
 * 初始化页面动画效果
 */
function initializeAnimations() {
    // 主页元素淡入
    const elementsToAnimate = document.querySelectorAll('.animate__fadeIn, .animate__fadeInUp');
    elementsToAnimate.forEach((element, index) => {
        element.style.animationDelay = `${index * 0.1}s`;
    });

    // 滚动时淡入效果
    const fadeElements = document.querySelectorAll('.fade-in-element');
    if ('IntersectionObserver' in window && fadeElements.length > 0) {
        const appearOnScroll = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    appearOnScroll.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        fadeElements.forEach(element => {
            appearOnScroll.observe(element);
        });
    }
}

/**
 * 初始化卡片悬停效果
 */
function initializeHoverEffects() {
    // 卡片悬停效果增强
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', e => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);
        });
    });
}

/**
 * 初始化浮动标签效果
 */
function initializeFloatingLabels() {
    // 查找所有浮动标签的输入框
    const floatingInputs = document.querySelectorAll('.floating-label input');
    
    floatingInputs.forEach(input => {
        // 检查输入框是否已有值
        if (input.value.trim() !== '') {
            input.classList.add('has-value');
        }
        
        // 添加输入事件监听
        input.addEventListener('input', function() {
            if (this.value.trim() !== '') {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });
    });
}

/**
 * 初始化页面元素
 */
function initializePageElements() {
    // 设置历史记录项的淡入效果
    const historyItems = document.querySelectorAll('.history-item');
    historyItems.forEach((item, index) => {
        item.classList.add('fade-in-element');
        item.style.animationDelay = `${index * 0.1}s`;
    });

    // 初始化消息项的淡入效果
    const messages = document.querySelectorAll('.message');
    messages.forEach((message, index) => {
        message.classList.add('fade-in-element');
        setTimeout(() => {
            message.classList.add('visible');
        }, index * 300);
    });

    // 添加波纹效果到按钮
    const buttons = document.querySelectorAll('button, .btn-primary, .btn-secondary');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            
            button.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

/**
 * 显示通知消息
 * @param {string} message - 通知内容 
 * @param {string} type - 通知类型 (success, error, info, warning)
 * @param {number} duration - 显示时长(毫秒)
 */
function showNotification(message, type = 'info', duration = 3000) {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    // 添加图标
    let icon = '';
    switch (type) {
        case 'success':
            icon = '<i class="fas fa-check-circle"></i>';
            break;
        case 'error':
            icon = '<i class="fas fa-exclamation-circle"></i>';
            break;
        case 'warning':
            icon = '<i class="fas fa-exclamation-triangle"></i>';
            break;
        case 'info':
        default:
            icon = '<i class="fas fa-info-circle"></i>';
            break;
    }
    
    // 设置通知内容
    notification.innerHTML = `
        <div class="notification-icon">${icon}</div>
        <div class="notification-content">${message}</div>
        <div class="notification-close"><i class="fas fa-times"></i></div>
    `;
    
    // 添加到页面
    const notificationContainer = document.querySelector('.notification-container');
    if (!notificationContainer) {
        const container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
        container.appendChild(notification);
    } else {
        notificationContainer.appendChild(notification);
    }
    
    // 添加关闭按钮事件
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', () => {
        notification.classList.add('notification-hide');
        setTimeout(() => {
            notification.remove();
        }, 300);
    });
    
    // 显示通知
    setTimeout(() => {
        notification.classList.add('notification-show');
    }, 10);
    
    // 自动关闭
    setTimeout(() => {
        notification.classList.add('notification-hide');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, duration);
} 