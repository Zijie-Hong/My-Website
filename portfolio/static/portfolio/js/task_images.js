// 加载步骤图片数据
// 日志系统 - 用于更好地追踪和调试
const logSystem = {
    // 日志级别：0 - 禁用, 1 - 错误, 2 - 警告, 3 - 信息, 4 - 调试
    level: 4,
    
    // 获取带时间戳的当前时间
    getTimestamp: function() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        const ms = String(now.getMilliseconds()).padStart(3, '0');
        return `${hours}:${minutes}:${seconds}.${ms}`;
    },
    
    // 记录调试日志
    debug: function(message, data = null) {
        if (this.level >= 4) {
            console.log(`[DEBUG] ${this.getTimestamp()} - ${message}`, data !== null ? data : '');
        }
    },
    
    // 记录信息日志
    info: function(message, data = null) {
        if (this.level >= 3) {
            console.log(`[INFO] ${this.getTimestamp()} - ${message}`, data !== null ? data : '');
        }
    },
    
    // 记录警告日志
    warn: function(message, data = null) {
        if (this.level >= 2) {
            console.warn(`[WARN] ${this.getTimestamp()} - ${message}`, data !== null ? data : '');
        }
    },
    
    // 记录错误日志
    error: function(message, data = null) {
        if (this.level >= 1) {
            console.error(`[ERROR] ${this.getTimestamp()} - ${message}`, data !== null ? data : '');
        }
    },
    
    // 开始一个日志组
    group: function(title) {
        if (this.level >= 3) {
            console.group(`[GROUP] ${this.getTimestamp()} - ${title}`);
        }
    },
    
    // 结束一个日志组
    groupEnd: function() {
        if (this.level >= 3) {
            console.groupEnd();
        }
    }
};

function loadStepImages() {
    logSystem.info('===== 开始加载步骤图片 =====');
    
    // 检查window.task是否存在及内容
    logSystem.debug('window.task存在:', !!window.task);
    if (window.task) {
        logSystem.debug('window.task的类型:', typeof window.task);
        logSystem.debug('window.task是否有step_images属性:', 'step_images' in window.task);
        logSystem.debug('step_images的数据类型:', Array.isArray(window.task.step_images) ? '数组' : typeof window.task.step_images);
        if (Array.isArray(window.task.step_images)) {
            logSystem.debug('step_images的长度:', window.task.step_images.length);
            if (window.task.step_images.length > 0) {
                logSystem.debug('第一个图片数据示例:', JSON.stringify(window.task.step_images[0]));
            }
        }
    }
    
    // 初始化图片数据数组
    let stepImages = [];
    
    // 检查window.task是否存在及内容
    if (!window.task) {
        logSystem.warn('window.task对象不存在');
        stepImages = [];
    } else if (!window.task.step_images) {
        logSystem.warn('window.task.step_images属性不存在');
        stepImages = [];
    } else if (!Array.isArray(window.task.step_images)) {
        logSystem.warn('window.task.step_images不是数组类型');
        logSystem.debug('step_images的实际类型:', typeof window.task.step_images);
        logSystem.debug('step_images的实际内容:', JSON.stringify(window.task.step_images));
        stepImages = [];
    } else if (window.task.step_images.length === 0) {
        logSystem.info('window.task.step_images数组为空');
        stepImages = [];
    } else {
        stepImages = window.task.step_images;
        logSystem.debug('使用window.task中的真实数据，共有', stepImages.length, '张图片');
        logSystem.debug('第一张图片示例:', JSON.stringify(stepImages[0]));
    }
    logSystem.debug('步骤图片数据完整内容:', stepImages);
    
    // 按步骤分组图片
    const imagesByStep = {};
    let totalImages = 0;
    
    // 确保step字段是数字类型
    logSystem.info('开始处理每张图片数据:');
    stepImages.forEach((image, index) => {
        logSystem.debug(`处理图片${index + 1}:`, JSON.stringify(image));
        
        // 检查image对象是否有step属性
        if (!image.step) {
            logSystem.warn(`图片${index + 1}没有step属性`);
            return;
        }
        
        const stepNum = parseInt(image.step);
        logSystem.debug(`图片${index + 1}的step值:`, image.step, '转成数字后:', stepNum);
        
        if (!isNaN(stepNum)) {
            if (!imagesByStep[stepNum]) {
                imagesByStep[stepNum] = [];
            }
            imagesByStep[stepNum].push(image);
            totalImages++;
            logSystem.debug(`添加到步骤${stepNum}，该步骤现有${imagesByStep[stepNum].length}张图片`);
        } else {
            logSystem.warn(`图片${index + 1}的step值无法转换为有效数字:`, image.step);
        }
    });
    
    logSystem.debug('按步骤分组后的图片:', imagesByStep);
    logSystem.info('总计处理图片数量:', totalImages);
    
    // 为每个步骤创建图片显示区域
    logSystem.info('开始为每个步骤创建图片显示区域:');
    const sortedSteps = Object.keys(imagesByStep).sort((a, b) => parseInt(a) - parseInt(b));
    logSystem.debug('排序后的步骤:', sortedSteps);
    
    sortedSteps.forEach(stepNum => {
        logSystem.group(`===== 处理步骤 ${stepNum} =====`);
        const images = imagesByStep[stepNum];
        logSystem.info(`步骤${stepNum}有${images.length}张图片`);
        
        // 查找对应步骤的容器 - 使用data-step属性选择器
        logSystem.debug(`尝试查找步骤${stepNum}的容器，选择器: [data-step="${stepNum}"]`);
        let stepContainer = document.querySelector(`[data-step="${stepNum}"]`);
        
        // 调试当前页面的所有步骤容器
        const allStepElements = document.querySelectorAll('.process-step');
        logSystem.debug(`页面上找到${allStepElements.length}个.process-step元素`);
        allStepElements.forEach((el, index) => {
            const dataStep = el.getAttribute('data-step');
            logSystem.debug(`步骤元素${index + 1}: data-step=${dataStep}, 内容摘要:`, el.textContent.substring(0, 50) + '...');
        });
        
        if (!stepContainer) {
            logSystem.debug(`未找到步骤 ${stepNum} 的容器，使用类名查找备用`);
            // 尝试备用选择器 - 直接查找所有.process-step元素并按顺序匹配
            const stepElements = document.querySelectorAll('.process-step');
            let foundContainer = null;
            
            stepElements.forEach((stepElement, index) => {
                const currentStep = index + 1;
                logSystem.debug(`检查步骤元素${index + 1}，索引+1=${currentStep}，目标stepNum=${stepNum}`);
                if (currentStep === parseInt(stepNum)) {
                    foundContainer = stepElement;
                    logSystem.debug(`找到匹配的步骤元素，索引=${index}`);
                }
            });
            
            if (!foundContainer) {
                logSystem.warn(`未找到步骤 ${stepNum} 的容器`);
                logSystem.groupEnd();
                return;
            }
            stepContainer = foundContainer;
            logSystem.debug(`使用备用方法找到步骤容器`);
        }
        
        // 尝试查找现有的图片容器或创建新的
        logSystem.debug('查找步骤容器中的.step-image子元素');
        let imageContainer = stepContainer.querySelector('.step-image');
        
        if (!imageContainer) {
            logSystem.debug('未找到现有图片容器，创建新的');
            imageContainer = document.createElement('div');
            imageContainer.className = 'step-image';
            imageContainer.setAttribute('data-step', stepNum);
            logSystem.debug('创建了新的图片容器');
            
            // 在步骤容器的适当位置插入图片容器
            const lastChild = stepContainer.lastElementChild;
            logSystem.debug('步骤容器的最后一个子元素:', lastChild ? lastChild.tagName : '无');
            
            if (lastChild && lastChild.tagName === 'BUTTON') {
                logSystem.debug('在按钮前插入图片容器');
                stepContainer.insertBefore(imageContainer, lastChild);
            } else {
                logSystem.debug('在步骤容器末尾添加图片容器');
                stepContainer.appendChild(imageContainer);
            }
            logSystem.debug('图片容器已添加到步骤容器');
        } else {
            logSystem.debug('找到现有的图片容器');
            // 清空现有内容
            imageContainer.innerHTML = '';
            logSystem.debug('已清空现有图片容器内容');
        }
        
        // 创建图片网格容器 - 改为自适应行布局
        const imageGrid = document.createElement('div');
        imageGrid.style.cssText = `
            display: flex;
            gap: 8px;
            flex-wrap: nowrap;
            overflow-x: auto;
            margin-top: 10px;
            padding-bottom: 8px;
            scrollbar-width: thin;
            scrollbar-color: var(--primary-color) transparent;
        `;
        
        // 为imageGrid添加滚动条样式
        const styleId = 'imageGridScrollbarStyle';
        if (!document.getElementById(styleId)) {
            const style = document.createElement('style');
            style.id = styleId;
            style.textContent = `
                .step-image div::-webkit-scrollbar {
                    height: 6px;
                }
                .step-image div::-webkit-scrollbar-track {
                    background: transparent;
                }
                .step-image div::-webkit-scrollbar-thumb {
                    background-color: var(--primary-color);
                    border-radius: 10px;
                }
            `;
            document.head.appendChild(style);
        }
        
        // 显示所有图片作为缩略图
        images.forEach((image, index) => {
            // 处理图片URL格式 - 简化逻辑并改进调试
            logSystem.group(`===== 处理图片${index + 1}的URL =====`);
            
            // 打印完整的image对象，确保我们看到所有可能的属性
            logSystem.debug('完整的图片对象:', image);
            
            // 尝试多种可能的URL属性
            let imageUrl = image.image_url || image.url || image.file_url || image.path || image.file || '';
            logSystem.debug('原始图片URL:', imageUrl);
            
            // 如果没有URL，跳过
            if (!imageUrl) {
                logSystem.warn(`图片${index + 1}没有有效的URL属性`);
                // 尝试从对象中查找任何包含URL的属性
                for (let key in image) {
                    if (typeof image[key] === 'string' && 
                        (image[key].includes('http') || image[key].includes('.jpg') || image[key].includes('.png') || image[key].includes('media/'))) {
                        logSystem.debug(`发现可能的URL属性: ${key} = ${image[key]}`);
                    }
                }
                logSystem.groupEnd();
                return;
            }
            
            // 修正URL格式 - 简化逻辑
            if (!imageUrl.startsWith('http://') && !imageUrl.startsWith('https://')) {
                // 如果URL不是绝对路径，添加斜杠开头
                if (!imageUrl.startsWith('/')) {
                    imageUrl = '/' + imageUrl;
                }
                // 添加当前网站的域名
                imageUrl = window.location.origin + imageUrl;
            }
            
            logSystem.debug('最终处理后的图片URL:', imageUrl);
            logSystem.groupEnd();
            
            const thumbnailContainer = document.createElement('div');
            thumbnailContainer.style.cssText = `
                width: 120px;
                height: 120px;
                flex-shrink: 0;
                overflow: hidden;
                border-radius: 4px;
                border: 1px solid var(--border-color);
                position: relative;
                display: flex;
                flex-direction: column;
                background-color: white;
                box-shadow: var(--shadow-sm);
                transition: all 0.2s ease;
                /* 确保单张图片也能明显显示为缩略图 */
                min-width: 120px;
                cursor: pointer;
            `;
            
            // 图片容器
            const imgContainer = document.createElement('div');
            imgContainer.style.cssText = `
                width: 100%;
                height: 85px;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: #f9f9f9;
                overflow: hidden;
            `;
            
            const img = document.createElement('img');
            img.src = imageUrl;
            img.alt = `步骤${stepNum}的图片${index + 1}`;
            img.style.cssText = `
                max-width: 100%;
                max-height: 100%;
                object-fit: cover;
                transition: transform 0.2s ease;
            `;
            
            // 添加鼠标悬停效果
            thumbnailContainer.addEventListener('mouseenter', () => {
                thumbnailContainer.style.transform = 'scale(1.05)';
                thumbnailContainer.style.boxShadow = 'var(--shadow-md)';
                thumbnailContainer.style.zIndex = '10';
                img.style.transform = 'scale(1.05)';
            });
            
            thumbnailContainer.addEventListener('mouseleave', () => {
                thumbnailContainer.style.transform = 'scale(1)';
                thumbnailContainer.style.boxShadow = 'var(--shadow-sm)';
                thumbnailContainer.style.zIndex = '1';
                img.style.transform = 'scale(1)';
            });
            
            // 添加图片加载状态
            const loadingIndicator = document.createElement('div');
            loadingIndicator.textContent = '加载中...';
            loadingIndicator.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(255, 255, 255, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                color: #666;
                font-size: 12px;
                z-index: 2;
            `;
            imgContainer.appendChild(loadingIndicator);
            
            img.onload = function() {
                loadingIndicator.remove();
            };
            
            img.onerror = function() {
                loadingIndicator.textContent = '加载失败';
                loadingIndicator.style.color = '#f44336';
                logSystem.error('图片加载失败:', imageUrl);
            };
            
            // 移除点击查看大图功能
            
            // 添加图片到图片容器
            imgContainer.appendChild(img);
            
            // 添加图片容器到缩略图容器
            thumbnailContainer.appendChild(imgContainer);
            
            // 添加图片计数
            const imageCount = document.createElement('div');
            imageCount.textContent = `图${index + 1}`;
            imageCount.style.cssText = `
                padding: 4px 6px;
                font-size: 11px;
                color: var(--text-secondary);
                background-color: white;
                text-align: center;
                border-top: 1px solid var(--border-color);
            `;
            thumbnailContainer.appendChild(imageCount);
            
            // 如果图片有描述，添加到容器中
            if (image.description) {
                const desc = document.createElement('div');
                desc.textContent = image.description;
                desc.style.cssText = `
                    position: absolute;
                    top: 85px;
                    left: 0;
                    right: 0;
                    background: rgba(0, 0, 0, 0.7);
                    color: white;
                    padding: 2px 5px;
                    font-size: 11px;
                    overflow: hidden;
                    white-space: nowrap;
                    text-overflow: ellipsis;
                    opacity: 0;
                    transition: opacity 0.2s;
                    z-index: 3;
                `;
                
                thumbnailContainer.appendChild(desc);
            }
            
            imageGrid.appendChild(thumbnailContainer);
        });
        
        // 添加图片总数提示
        if (images.length > 0) {
            const totalHint = document.createElement('div');
            totalHint.textContent = `共${images.length}张图片`;
            totalHint.style.cssText = `
                margin-top: 8px;
                padding: 5px;
                text-align: center;
                font-size: 12px;
                color: var(--text-secondary);
                background-color: var(--bg-color);
                border-radius: 4px;
            `;
            imageContainer.appendChild(totalHint);
        }
        
        imageContainer.appendChild(imageGrid);
    });
}

// 初始化图片数据
function initializeTaskImages() {
    // 直接使用window.task中的数据
    logSystem.info('初始化任务图片数据');
    loadStepImages();
}

// 暴露一个公共方法，允许其他模块调用重新加载图片数据
window.reloadStepImages = function() {
    logSystem.info('手动触发重新加载步骤图片数据');
    // 清空所有步骤图片容器
    document.querySelectorAll('.step-image').forEach(container => {
        container.innerHTML = '';
    });
    // 重新加载图片
    loadStepImages();
}

// 暴露initializeTaskImages函数，确保全局可访问
window.initializeTaskImages = initializeTaskImages;

// 确保在DOM加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTaskImages);
} else {
    // 如果DOM已经加载完成，直接初始化
    setTimeout(initializeTaskImages, 100);
}