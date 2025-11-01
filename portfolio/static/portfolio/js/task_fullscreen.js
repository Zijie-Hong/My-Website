// 全屏功能实现
function setupFullscreenFunctionality() {
    const fullscreenToggle = document.getElementById('fullscreen-toggle');
    const exitFullscreen = document.getElementById('exit-fullscreen');
    const fullscreenContainer = document.getElementById('fullscreen-process-container');
    const fullscreenContent = document.getElementById('fullscreen-process-content');
    
    // 打开全屏
    fullscreenToggle.addEventListener('click', function() {
        // 清空全屏容器
        fullscreenContent.innerHTML = '';
        
        // 创建标题元素
        const titleElement = document.createElement('h3');
        titleElement.textContent = '实现过程 - 全屏查看';
        titleElement.style.marginBottom = '1.5rem';
        fullscreenContent.appendChild(titleElement);
        
        // 获取所有步骤并克隆到全屏容器
        const allSteps = document.querySelectorAll('.process-step');
        allSteps.forEach(step => {
            const clonedStep = step.cloneNode(true);
            fullscreenContent.appendChild(clonedStep);
        });
        
        // 显示全屏容器
        fullscreenContainer.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    });
    
    // 退出全屏
    exitFullscreen.addEventListener('click', function() {
        fullscreenContainer.style.display = 'none';
        document.body.style.overflow = '';
    });
    
    // 按ESC键退出全屏
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && fullscreenContainer.style.display === 'flex') {
            fullscreenContainer.style.display = 'none';
            document.body.style.overflow = '';
        }
    });
}

// 处理图片标签，将[IMAGE:filename]替换为实际图片
function processImageTags() {
    const steps = document.querySelectorAll('.process-step .step-content');
    const imageTagRegex = /\[IMAGE:([^\[\]]+)\]/g;
    
    steps.forEach(step => {
        const content = step.innerHTML;
        let hasImages = false;
        
        const newContent = content.replace(imageTagRegex, function(match, filename) {
            hasImages = true;
            // 清理文件名，移除多余的字符
            const cleanFilename = filename.trim().replace(/[\[\]]/g, '');
            // 创建图片HTML
            return `<div class="task-image-container"><img src="/media/task_step_images/${cleanFilename}" alt="实现过程图片" class="task-image"></div>`;
        });
        
        // 如果有图片，更新内容
        if (hasImages) {
            step.innerHTML = newContent;
        }
    });
}