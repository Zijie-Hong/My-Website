// 移动端菜单切换
const menuToggle = document.getElementById('menu-toggle');
const mobileNav = document.getElementById('mobile-nav');

if (menuToggle && mobileNav) {
    menuToggle.addEventListener('click', () => {
        mobileNav.style.display = mobileNav.style.display === 'block' ? 'none' : 'block';
        menuToggle.textContent = mobileNav.style.display === 'block' ? '✕' : '☰';
    });
}

// 点击移动导航链接后关闭菜单
const mobileLinks = mobileNav.querySelectorAll('a');
mobileLinks.forEach(link => {
    link.addEventListener('click', () => {
        mobileNav.style.display = 'none';
        if (menuToggle) {
            menuToggle.textContent = '☰';
        }
    });
});

// 页面滚动时导航栏样式变化
window.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    if (window.scrollY > 50) {
        header.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
        header.style.padding = '0';
    } else {
        header.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        header.style.padding = '';
    }
});

// 平滑滚动到锚点
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            targetElement.scrollIntoView({ 
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// 项目卡片悬停效果增强
const projectCards = document.querySelectorAll('.project-card');
projectCards.forEach(card => {
    card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-10px) scale(1.02)';
        card.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)';
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = '';
        card.style.boxShadow = '';
    });
});

// 表单提交处理
const contactForm = document.querySelector('.contact-form');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const submitBtn = this.querySelector('.submit-btn');
        const originalText = submitBtn.textContent;
        
        // 简单的表单验证
        const nameInput = this.querySelector('input[name="name"]');
        const emailInput = this.querySelector('input[name="email"]');
        const messageInput = this.querySelector('textarea[name="message"]');
        
        if (!nameInput.value.trim()) {
            alert('请输入您的姓名');
            nameInput.focus();
            return;
        }
        
        if (!emailInput.value.trim()) {
            alert('请输入您的邮箱');
            emailInput.focus();
            return;
        }
        
        // 简单的邮箱验证
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailInput.value.trim())) {
            alert('请输入有效的邮箱地址');
            emailInput.focus();
            return;
        }
        
        if (!messageInput.value.trim()) {
            alert('请输入您的留言');
            messageInput.focus();
            return;
        }
        
        // 模拟表单提交
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading"></span> 发送中...';
        
        setTimeout(() => {
            // 这里可以添加实际的表单提交逻辑
            alert('留言发送成功！我们会尽快回复您。');
            contactForm.reset();
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }, 1500);
    });
}

// 图片懒加载（简化版）
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    images.forEach(img => {
        const imgTop = img.getBoundingClientRect().top;
        if (imgTop < window.innerHeight + 100) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        }
    });
}

// 初始加载和滚动时检查
window.addEventListener('load', lazyLoadImages);
window.addEventListener('scroll', lazyLoadImages);

// 页面加载动画
window.addEventListener('load', () => {
    // 添加页面加载完成的类
    document.body.classList.add('loaded');
    
    // 为各个部分添加渐入动画
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        section.classList.add('fade-in-up');
    });
});

// 技术筛选功能增强
const filterSelects = document.querySelectorAll('.filter-select');
filterSelects.forEach(select => {
    select.addEventListener('change', function() {
        // 构建筛选URL
        const category = document.getElementById('category-filter')?.value || '';
        const technology = document.getElementById('technology-filter')?.value || '';
        
        let url = '/projects/?';
        const params = [];
        
        if (category) params.push(`category=${encodeURIComponent(category)}`);
        if (technology) params.push(`technology=${encodeURIComponent(technology)}`);
        
        if (params.length > 0) {
            url += params.join('&');
        } else {
            url = '/projects/';
        }
        
        // 跳转到筛选结果页
        window.location.href = url;
    });
});

// 返回顶部按钮
const backToTopBtn = document.createElement('button');
backToTopBtn.textContent = '↑';
backToTopBtn.id = 'back-to-top';
backToTopBtn.style.position = 'fixed';
backToTopBtn.style.bottom = '30px';
backToTopBtn.style.right = '30px';
backToTopBtn.style.width = '50px';
backToTopBtn.style.height = '50px';
backToTopBtn.style.borderRadius = '50%';
backToTopBtn.style.backgroundColor = 'var(--primary-color)';
backToTopBtn.style.color = 'white';
backToTopBtn.style.border = 'none';
backToTopBtn.style.fontSize = '1.5rem';
backToTopBtn.style.cursor = 'pointer';
backToTopBtn.style.boxShadow = '0 4px 10px rgba(0, 0, 0, 0.2)';
backToTopBtn.style.display = 'none';
backToTopBtn.style.zIndex = '999';
backToTopBtn.style.transition = 'all 0.3s ease';
document.body.appendChild(backToTopBtn);

// 返回顶部功能
window.addEventListener('scroll', () => {
    if (window.scrollY > 500) {
        backToTopBtn.style.display = 'block';
    } else {
        backToTopBtn.style.display = 'none';
    }
});

backToTopBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// 项目卡片动画延迟
projectCards.forEach((card, index) => {
    card.style.animationDelay = `${index * 0.1}s`;
});

// 任务分类卡片折叠功能
const categoryHeaders = document.querySelectorAll('.category-header');
categoryHeaders.forEach(header => {
    // 确保只处理属于task-category-card的header
    const categoryCard = header.closest('.task-category-card');
    if (categoryCard) {
        header.addEventListener('click', () => {
            const tasksContainer = categoryCard.querySelector('.category-tasks');
            if (tasksContainer) {
                // 切换任务列表的显示/隐藏状态
                tasksContainer.style.display = tasksContainer.style.display === 'none' ? 'block' : 'none';
                
                // 可以添加箭头图标变化或其他视觉反馈
                // 这里可以根据需要添加更多的视觉效果
            }
        });
    }
});