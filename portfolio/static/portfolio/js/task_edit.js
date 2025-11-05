// 任务编辑功能实现 - 修复版
function setupProcessEditFunctionality() {
    // 获取DOM元素
    const editProcessButton = document.getElementById('edit-process-button');
    const editProcessModal = document.getElementById('editProcessModal');
    const processContent = document.getElementById('processContent');
    const stepSelect = document.getElementById('step-select');
    const fileInput = document.getElementById('step-image-upload');
    const stepDescription = document.getElementById('step-description');
    const uploadButton = document.getElementById('upload-step-image');
    const uploadedImagesContainer = document.getElementById('uploaded-step-images');
    const uploadedCount = document.getElementById('uploaded-count');
    
    // 初始化数据结构
    let uploadedImages = [];
    let imagesToDelete = new Set();
    let pendingUploads = [];
    
    // ===== 关键修复1: 改进步骤选择下拉框 =====
    function populateStepSelect() {
        const processText = processContent.value.trim();
        const processLines = processText.split('\n').filter(line => line.trim());
        
        // 清空现有选项
        stepSelect.innerHTML = '';
        
        // 如果没有步骤,至少添加一个
        if (processLines.length === 0) {
            const option = document.createElement('option');
            option.value = '1';
            option.textContent = '步骤 1';
            stepSelect.appendChild(option);
            return;
        }
        
        // 添加步骤选项 - 修复：只显示步骤编号
        processLines.forEach((line, index) => {
            const stepNumber = index + 1;
            const option = document.createElement('option');
            option.value = stepNumber;
            // 只显示步骤编号，不包含内容预览
            option.textContent = `步骤 ${stepNumber}`;
            stepSelect.appendChild(option);
        });
    }
    
    // ===== 关键修复2: 改进图片显示逻辑 =====
    function displayUploadedStepImages() {
        console.log('开始显示图片...');
        console.log('window.task:', window.task);
        console.log('待删除图片:', Array.from(imagesToDelete));
        console.log('待上传图片:', pendingUploads);
        
        // 清空容器
        uploadedImagesContainer.innerHTML = '';
        
        // 从window.task中获取现有图片数据
        const existingImages = (window.task && Array.isArray(window.task.step_images)) 
            ? window.task.step_images 
            : [];
        
        console.log('现有图片数据:', existingImages);
        
        // 构建完整的图片列表
        uploadedImages = [];
        
        // 1. 添加现有图片(未被标记删除的)
        existingImages.forEach(img => {
            const imageKey = `${img.step}_${img.id}`;
            if (!imagesToDelete.has(imageKey)) {
                uploadedImages.push({
                    ...img,
                    isPending: false
                });
            }
        });
        
        // 2. 添加待上传图片
        pendingUploads.forEach(pending => {
            uploadedImages.push({
                step: pending.step,
                url: pending.previewUrl,
                description: pending.description,
                isPending: true,
                file: pending.file,
                id: 'pending_' + Date.now() + Math.random()
            });
        });
        
        console.log('最终显示的图片列表:', uploadedImages);
        
        // 显示图片或空状态
        if (uploadedImages.length > 0) {
            // 按步骤分组显示图片
            const imagesByStep = {};
            uploadedImages.forEach(img => {
                if (!imagesByStep[img.step]) {
                    imagesByStep[img.step] = [];
                }
                imagesByStep[img.step].push(img);
            });
            
            // 为每个步骤创建图片行
            Object.keys(imagesByStep).sort((a, b) => parseInt(a) - parseInt(b)).forEach(stepNum => {
                // 创建步骤标题行
                const stepHeader = document.createElement('div');
                stepHeader.className = 'mb-2 mt-4';
                stepHeader.innerHTML = `<h5>步骤 ${stepNum}</h5>`;
                uploadedImagesContainer.appendChild(stepHeader);
                
                // 创建图片容器行 - 使用flex确保图片在同一行
                const imagesRow = document.createElement('div');
                imagesRow.style.cssText = 'display: flex; gap: 10px; flex-wrap: nowrap; overflow-x: auto; padding-bottom: 5px;';
                
                // 为当前步骤的每个图片创建缩略图
                imagesByStep[stepNum].forEach(imageData => {
                    const imageWrapper = document.createElement('div');
                    imageWrapper.style.cssText = 'width: 120px; flex-shrink: 0;';
                    
                    const card = createImageCard(imageData);
                    imageWrapper.appendChild(card);
                    imagesRow.appendChild(imageWrapper);
                });
                
                uploadedImagesContainer.appendChild(imagesRow);
            });
            
            // 添加删除事件监听(使用事件委托)
            uploadedImagesContainer.removeEventListener('click', handleDeleteClick);
            uploadedImagesContainer.addEventListener('click', handleDeleteClick);
        } else {
            showEmptyState();
        }
        
        // 更新计数
        updateImageCount(uploadedImages.length);
    }
    
    // ===== 关键修复3: 使用事件委托处理删除 =====
    function handleDeleteClick(event) {
        const deleteBtn = event.target.closest('.delete-image-btn');
        if (deleteBtn) {
            const step = deleteBtn.getAttribute('data-step');
            const imageId = deleteBtn.getAttribute('data-image-id');
            console.log('点击删除按钮:', { step, imageId });
            deleteImage(step, imageId);
        }
    }
    
    // ===== 关键修复4: 改进图片卡片创建 =====
    function createImageCard(imageData) {
        const imageId = imageData.id || 'unknown';
        
        // 处理图片URL
        let imageUrl = imageData.url || imageData.image_url || imageData.previewUrl || '';
        if (imageUrl && !imageUrl.startsWith('http') && !imageUrl.startsWith('data:') && !imageUrl.startsWith('/')) {
            imageUrl = '/media/' + imageUrl;
        }
        
        const isPending = imageData.isPending || false;
        
        // 创建卡片容器
        const card = document.createElement('div');
        card.className = 'task-thumbnail-card';
        card.style.cssText = 'position: relative; width: 100%;';
        
        // 图片容器 - 固定尺寸
        const imageContainer = document.createElement('div');
        imageContainer.style.cssText = 'width: 100%; height: 100px; background-color: #f3f4f6; border-radius: 4px; overflow: hidden; display: flex; align-items: center; justify-content: center; position: relative;';
        
        const img = document.createElement('img');
        img.src = imageUrl;
        img.alt = `步骤 ${imageData.step} 图片`;
        img.style.cssText = 'width: 100%; height: 100%; object-fit: cover; transition: transform 0.2s;';
        img.onerror = function() {
            this.style.objectFit = 'contain';
            this.style.backgroundColor = '#f9fafb';
        };
        
        // 待上传标记
        if (isPending) {
            const pendingBadge = document.createElement('span');
            pendingBadge.style.cssText = 'position: absolute; bottom: 2px; left: 2px; background-color: rgba(0,0,0,0.7); color: white; font-size: 10px; padding: 2px 4px; border-radius: 2px;';
            pendingBadge.textContent = '待上传';
            imageContainer.appendChild(pendingBadge);
        }
        
        // 步骤标签
        const stepTag = document.createElement('span');
        stepTag.style.cssText = 'position: absolute; top: 2px; left: 2px; background-color: rgba(67, 97, 238, 0.9); color: white; font-size: 10px; padding: 2px 6px; border-radius: 10px; font-weight: bold;';
        stepTag.textContent = `步骤 ${imageData.step}`;
        imageContainer.appendChild(stepTag);
        
        imageContainer.appendChild(img);
        
        // 文件名（如果有）
        if (imageData.file && imageData.file.name) {
            const filename = document.createElement('div');
            filename.style.cssText = 'font-size: 10px; color: #666; margin-top: 4px; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;';
            // 截断长文件名
            const maxLength = 15;
            filename.textContent = imageData.file.name.length > maxLength 
                ? imageData.file.name.substring(0, maxLength) + '...' 
                : imageData.file.name;
            card.appendChild(filename);
        }
        
        // 删除按钮
        const deleteBtn = document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.className = 'delete-image-btn';
        deleteBtn.dataset.step = imageData.step;
        deleteBtn.dataset.imageId = imageId;
        deleteBtn.style.cssText = 'position: absolute; top: -6px; right: -6px; width: 20px; height: 20px; border-radius: 50%; background-color: #ff4444; color: white; border: none; font-size: 12px; line-height: 1; cursor: pointer; z-index: 10;';
        deleteBtn.textContent = '×';
        
        card.appendChild(imageContainer);
        card.appendChild(deleteBtn);
        
        // 悬停效果
        card.addEventListener('mouseenter', () => {
            img.style.transform = 'scale(1.05)';
        });
        
        card.addEventListener('mouseleave', () => {
            img.style.transform = 'scale(1)';
        });
        
        return card;
    }
    
    // ===== 关键修复5: 改进删除逻辑 =====
    function deleteImage(step, imageId) {
        console.log('执行删除:', { step, imageId });
        
        // 如果是待上传的图片,从pendingUploads中移除
        if (imageId.toString().startsWith('pending_')) {
            const index = pendingUploads.findIndex(p => 
                p.step == step && (p.id === imageId || !p.id)
            );
            if (index !== -1) {
                pendingUploads.splice(index, 1);
                console.log('从待上传列表中移除图片');
            }
        } else {
            // 如果是已存在的图片,添加到删除列表
            const imageKey = `${step}_${imageId}`;
            imagesToDelete.add(imageKey);
            console.log('添加到删除列表:', imageKey);
            console.log('当前删除列表:', Array.from(imagesToDelete));
        }
        
        // 重新显示图片列表
        displayUploadedStepImages();
        
        // 显示提示
        showMessage('已标记图片为删除,保存后生效', 'info');
    }
    
    // 显示空状态
    function showEmptyState() {
        const emptyState = document.createElement('div');
        emptyState.className = 'text-center py-10 w-full';
        emptyState.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" 
                 fill="#9ca3af" viewBox="0 0 16 16" 
                 style="display: block; margin: 0 auto 16px;">
                <path d="M6.002 5.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/>
                <path d="M2.002 1a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V3a2 2 0 0 0-2-2h-12zm12 1a1 1 0 0 1 1 1v6.5l-3.777-1.947a.5.5 0 0 0-.577.093l-3.71 3.71-2.66-1.772a.5.5 0 0 0-.63.062L1.002 12V3a1 1 0 0 1 1-1h12z"/>
            </svg>
            <h4 style="margin: 0 0 8px; font-size: 16px; color: #374151; font-weight: 500;">
                暂无步骤图片
            </h4>
            <p style="margin: 0; font-size: 14px; color: #6b7280;">
                使用上方上传区域为步骤添加图片说明
            </p>
        `;
        uploadedImagesContainer.appendChild(emptyState);
    }
    
    // 更新图片计数
    function updateImageCount(count) {
        if (uploadedCount) {
            uploadedCount.textContent = `共 ${count} 张图片`;
        }
    }
    
    // 设置图片上传功能
    function setupImageUpload() {
        if (!uploadButton || !fileInput) {
            console.error('上传按钮或文件输入框不存在');
            return;
        }
        
        // 设置文件输入框支持多选
        fileInput.multiple = true;
        
        uploadButton.addEventListener('click', handleImageUpload);
        
        // 文件选择变化时的反馈
        fileInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                const filesCount = this.files.length;
                console.log('选择了文件数量:', filesCount);
                
                
            }
        });
    }
    
    // 处理图片上传 - 支持多文件并添加进度指示器
    function handleImageUpload() {
        const stepNumber = stepSelect.value;
        const files = fileInput.files;
        const description = stepDescription.value.trim();
        
        console.log('准备上传图片:', { stepNumber, filesCount: files.length, description });
        
        // 验证输入
        if (!stepNumber) {
            showMessage('请选择步骤', 'error');
            return;
        }
        
        if (files.length === 0) {
            showMessage('请选择要上传的图片', 'error');
            return;
        }
        
        // 显示处理中状态
        showProgressIndicator();
        
        // 定义验证函数
        function isValidImage(file) {
            // 验证文件类型
            const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
            if (!validTypes.includes(file.type)) {
                showMessage(`文件 ${file.name} 不是有效的图片文件(JPG, PNG, GIF, WebP)`, 'error');
                return false;
            }
            
            // 验证文件大小(5MB)
            if (file.size > 5 * 1024 * 1024) {
                showMessage(`文件 ${file.name} 大小超过5MB限制`, 'error');
                return false;
            }
            
            return true;
        }
        
        // 计算成功添加的文件数量
        let addedCount = 0;
        let processedCount = 0;
        const totalFiles = files.length;
        
        // 处理每个文件
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            
            if (!isValidImage(file)) {
                processedCount++;
                updateProgressIndicator(processedCount, totalFiles);
                continue; // 跳过无效文件
            }
            
            // 创建预览URL
            const reader = new FileReader();
            reader.file = file; // 保存对当前文件的引用
            reader.index = i;
            
            reader.onload = function(e) {
                // 添加到待上传列表
                const pendingId = 'pending_' + Date.now() + Math.random() + '_' + this.index;
                pendingUploads.push({
                    id: pendingId,
                    step: stepNumber,
                    file: this.file,
                    previewUrl: e.target.result,
                    description: description
                });
                
                addedCount++;
                processedCount++;
                updateProgressIndicator(processedCount, totalFiles);
                
                console.log('添加到待上传列表:', { fileName: this.file.name, pendingUploadsCount: pendingUploads.length });
                
                // 刷新显示
                displayUploadedStepImages();
                
                // 当处理完所有文件后
                if (processedCount === totalFiles) {
                    // 隐藏进度指示器
                    hideProgressIndicator();
                    
                    // 清空表单
                    fileInput.value = '';
                    stepDescription.value = '';
                    
                    // 清除文件名反馈
                    const feedback = document.getElementById('file-feedback');
                    if (feedback) {
                        feedback.remove();
                    }
                    
                    showMessage(`成功添加 ${addedCount} 张图片到上传队列`, 'success');
                }
            };
            
            reader.onerror = function() {
                processedCount++;
                updateProgressIndicator(processedCount, totalFiles);
                showMessage(`读取图片 ${file.name} 失败,请重试`, 'error');
                
                // 如果所有文件都处理完了
                if (processedCount === totalFiles) {
                    hideProgressIndicator();
                }
            };
            
            reader.readAsDataURL(file);
        }
    }
    
    // 显示进度指示器
    function showProgressIndicator() {
        let indicator = document.getElementById('upload-progress');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'upload-progress';
            indicator.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(255, 255, 255, 0.95);
                padding: 24px;
                border-radius: 8px;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                z-index: 9999;
                text-align: center;
                min-width: 250px;
            `;
            
            const progressBar = document.createElement('div');
            progressBar.id = 'progress-bar';
            progressBar.style.cssText = `
                width: 100%;
                height: 8px;
                background: #e5e7eb;
                border-radius: 4px;
                margin-top: 12px;
                overflow: hidden;
            `;
            
            const progressFill = document.createElement('div');
            progressFill.id = 'progress-fill';
            progressFill.style.cssText = `
                height: 100%;
                width: 0%;
                background: #10b981;
                transition: width 0.3s ease;
            `;
            
            const progressText = document.createElement('div');
            progressText.id = 'progress-text';
            progressText.style.cssText = 'margin-top: 8px; font-size: 14px; color: #4b5563;';
            progressText.textContent = '处理中...';
            
            progressBar.appendChild(progressFill);
            indicator.appendChild(document.createTextNode('批量上传中'));
            indicator.appendChild(progressBar);
            indicator.appendChild(progressText);
            
            document.body.appendChild(indicator);
        } else {
            // 重置进度条
            document.getElementById('progress-fill').style.width = '0%';
            document.getElementById('progress-text').textContent = '处理中...';
            indicator.style.display = 'block';
        }
    }
    
    // 更新进度指示器
    function updateProgressIndicator(current, total) {
        const percent = Math.round((current / total) * 100);
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        
        if (progressFill) {
            progressFill.style.width = `${percent}%`;
        }
        
        if (progressText) {
            progressText.textContent = `已处理 ${current}/${total} 个文件 (${percent}%)`;
        }
    }
    
    // 隐藏进度指示器
    function hideProgressIndicator() {
        const indicator = document.getElementById('upload-progress');
        if (indicator) {
            setTimeout(() => {
                indicator.style.display = 'none';
            }, 500);
        }
    }
    
    // ===== 关键修复6: 改进保存逻辑 =====
    async function saveProcessChanges() {
        const process = processContent.value.trim();
        const taskId = window.task?.id;
        const projectId = window.project?.id;
        
        console.log('开始保存,数据状态:', {
            taskId,
            projectId,
            processLength: process.length,
            imagesToDelete: Array.from(imagesToDelete),
            pendingUploads: pendingUploads.length
        });
        
        if (!taskId || !projectId) {
            if (!taskId && !projectId) {
                showMessage('任务和项目信息丢失,请刷新页面重试', 'error');
            } else if (!taskId) {
                showMessage('任务信息丢失,请刷新页面重试', 'error');
            } else {
                showMessage('项目信息丢失,请刷新页面重试', 'error');
            }
            return;
        }
        
        // 准备FormData
        const formData = new FormData();
        formData.append('process', process);
        
        // 获取CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (csrfToken) {
            formData.append('csrfmiddlewaretoken', csrfToken);
        }
        
        // 添加待删除的图片信息
        imagesToDelete.forEach(imageKey => {
            formData.append('delete_step_image[]', imageKey);
        });
        
        // 添加待上传的图片
        pendingUploads.forEach((pending, index) => {
            // 使用唯一的键名，避免覆盖相同步骤的多张图片
            const uniqueImageKey = `step_image_${pending.step}_${index}`;
            formData.append(uniqueImageKey, pending.file);
            formData.append(`step_description_${pending.step}_${index}`, pending.description);
        });
        
        // 打印FormData内容(调试用)
        console.log('FormData内容:');
        for (let [key, value] of formData.entries()) {
            console.log(key, value);
        }
        
        try {
            // 显示加载状态
            const saveButton = document.querySelector('[onclick="saveProcessChanges()"]');
            if (saveButton) {
                saveButton.innerHTML = '<span>保存中...</span>';
                saveButton.disabled = true;
            }
            
            // 发送请求
            const url = `/projects/${projectId}/tasks/${taskId}/update-process/`;
            console.log('发送请求到:', url);
            
            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });
            
            console.log('响应状态:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('服务器错误:', errorText);
                throw new Error(`保存失败 (${response.status})`);
            }
            
            const result = await response.json();
            console.log('服务器响应:', result);
            
            if (result.status === 'success') {
                showMessage('保存成功,即将刷新页面...', 'success');
                
                // 重定向到任务详情页
                setTimeout(() => {
                    window.location.href = `/projects/${projectId}/tasks/${taskId}/`;
                }, 1000);
            } else {
                showMessage(result.message || '保存失败', 'error');
                
                // 恢复按钮状态
                if (saveButton) {
                    saveButton.disabled = false;
                    saveButton.innerHTML = '<span>保存修改</span>';
                }
            }
        } catch (error) {
            console.error('保存过程中出现错误:', error);
            showMessage('保存失败: ' + error.message, 'error');
            
            // 恢复按钮状态
            const saveButton = document.querySelector('[onclick="saveProcessChanges()"]');
            if (saveButton) {
                saveButton.disabled = false;
                saveButton.innerHTML = '<span>保存修改</span>';
            }
        }
    }
    
    // 关闭模态框
    function closeEditProcessModal() {
        if (editProcessModal) {
            editProcessModal.classList.remove('show');
            document.body.style.overflow = '';
            
            // 移除背景遮罩
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
        }
        
        // 重置状态
        uploadedImages = [];
        imagesToDelete.clear();
        pendingUploads = [];
    }
    
    // 初始化函数
    function init() {
        console.log('初始化编辑功能...');
        
        // 设置编辑按钮事件
        editProcessButton?.addEventListener('click', function() {
            console.log('打开编辑模态框');
            
            // 重置所有状态
            uploadedImages = [];
            imagesToDelete.clear();
            pendingUploads = [];
            
            // 加载当前数据
            if (window.task) {
                processContent.value = window.task.process || '';
                console.log('加载任务数据:', window.task);
            } else {
                console.warn('window.task不存在');
                processContent.value = '';
            }
            
            // 填充步骤选择框
            populateStepSelect();
            
            // 监听process内容变化,自动更新步骤选择框
            processContent.addEventListener('input', populateStepSelect);
            
            // 显示已上传的图片
            displayUploadedStepImages();
            
            // 显示模态框
            editProcessModal.classList.add('show');
            document.body.style.overflow = 'hidden';
        });
        
        // 初始化图片上传功能
        setupImageUpload();
        
        // 暴露全局函数
        window.saveProcessChanges = saveProcessChanges;
        window.closeEditProcessModal = closeEditProcessModal;
        
        console.log('编辑功能初始化完成');
    }
    
    // 执行初始化
    init();
}

// 改进的消息提示函数
function showMessage(message, type = 'success') {
    // 移除现有消息
    const existingMessage = document.getElementById('toast-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // 创建新消息
    const toast = document.createElement('div');
    toast.id = 'toast-message';
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        border-radius: 8px;
        color: white;
        font-size: 14px;
        font-weight: 500;
        z-index: 10000;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        animation: slideIn 0.3s ease;
    `;
    
    // 设置背景色
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        info: '#3b82f6',
        warning: '#f59e0b'
    };
    toast.style.backgroundColor = colors[type] || colors.info;
    
    toast.textContent = message;
    
    // 添加动画
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(toast);
    
    // 3秒后自动移除
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupProcessEditFunctionality);
} else {
    setupProcessEditFunctionality();
}