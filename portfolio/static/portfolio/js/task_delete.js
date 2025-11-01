// 任务删除功能实现
function setupDeleteFunctionality() {
    // 获取DOM元素
    const deleteTaskButton = document.getElementById('delete-task-button');
    const deleteConfirmModal = document.getElementById('deleteConfirmModal');
    const confirmDeleteButton = document.getElementById('confirm-delete');
    const cancelDeleteButton = document.getElementById('cancel-delete');
    const closeModalButtons = document.querySelectorAll('[data-dismiss="modal"]');
    
    // 打开删除确认模态框
    function openDeleteModal() {
        if (deleteConfirmModal) {
            deleteConfirmModal.classList.add('show');
            deleteConfirmModal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        }
    }
    
    // 关闭删除确认模态框
    function closeDeleteModal() {
        if (deleteConfirmModal) {
            deleteConfirmModal.classList.remove('show');
            deleteConfirmModal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }
    
    // 执行任务删除
    function executeDelete() {
        // 获取任务ID
        const taskId = document.getElementById('task-id').value;
        
        if (!taskId) {
            showMessage('无法获取任务ID', 'error');
            return;
        }
        
        // 构建删除URL
        const deleteUrl = `/portfolio/task/${taskId}/delete/`;
        
        // 显示加载状态
        showLoading(true);
        
        // 发送删除请求
        fetch(deleteUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({})
        })
        .then(response => {
            showLoading(false);
            
            if (!response.ok) {
                throw new Error('删除任务失败');
            }
            
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // 关闭模态框
                closeDeleteModal();
                
                // 显示成功消息
                showMessage('任务已成功删除', 'success');
                
                // 延迟重定向到任务列表页
                setTimeout(() => {
                    window.location.href = '/portfolio/tasks/';
                }, 1500);
            } else {
                showMessage(data.message || '删除任务失败', 'error');
            }
        })
        .catch(error => {
            showLoading(false);
            showMessage('网络错误，请稍后重试', 'error');
            console.error('删除任务时发生错误:', error);
        });
    }
    
    // 获取CSRF Token
    function getCsrfToken() {
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        return csrftoken;
    }
    
    // 显示加载状态
    function showLoading(show) {
        const loadingElement = document.getElementById('delete-loading');
        const buttonText = document.getElementById('delete-button-text');
        
        if (loadingElement && buttonText) {
            if (show) {
                loadingElement.style.display = 'inline-block';
                buttonText.textContent = '删除中...';
                confirmDeleteButton.disabled = true;
            } else {
                loadingElement.style.display = 'none';
                buttonText.textContent = '确认删除';
                confirmDeleteButton.disabled = false;
            }
        }
    }
    
    // 显示消息提示
    function showMessage(message, type = 'success') {
        // 创建消息元素
        const messageContainer = document.createElement('div');
        messageContainer.className = `alert alert-${type} fixed-top text-center mb-0`;
        messageContainer.style.zIndex = '9999';
        messageContainer.textContent = message;
        
        // 添加到页面
        document.body.prepend(messageContainer);
        
        // 自动移除
        setTimeout(() => {
            messageContainer.style.opacity = '0';
            messageContainer.style.transition = 'opacity 0.5s ease';
            setTimeout(() => {
                messageContainer.remove();
            }, 500);
        }, 3000);
    }
    
    // 初始化函数
    function init() {
        // 设置删除按钮点击事件
        if (deleteTaskButton) {
            deleteTaskButton.addEventListener('click', openDeleteModal);
        }
        
        // 设置确认删除按钮点击事件
        if (confirmDeleteButton) {
            confirmDeleteButton.addEventListener('click', executeDelete);
        }
        
        // 设置取消删除按钮点击事件
        if (cancelDeleteButton) {
            cancelDeleteButton.addEventListener('click', closeDeleteModal);
        }
        
        // 设置关闭模态框按钮事件
        closeModalButtons.forEach(button => {
            button.addEventListener('click', closeDeleteModal);
        });
        
        // 处理ESC键关闭模态框
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && deleteConfirmModal?.classList.contains('show')) {
                closeDeleteModal();
            }
        });
        
        // 处理点击模态框外部关闭
        if (deleteConfirmModal) {
            deleteConfirmModal.addEventListener('click', function(e) {
                if (e.target === deleteConfirmModal) {
                    closeDeleteModal();
                }
            });
        }
    }
    
    // 执行初始化
    init();
}