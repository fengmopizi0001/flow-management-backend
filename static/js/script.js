// ============ API配置导入 ============
// 确保config.js已加载
if (typeof API_URL === 'undefined') {
    console.error('API配置未加载，请确保config.js在script.js之前加载');
}

// ============ 工具函数 ============

// 格式化货币
function formatCurrency(amount) {
    return new Intl.NumberFormat('zh-CN', {
        style: 'currency',
        currency: 'CNY'
    }).format(amount);
}

// 格式化日期
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

// 显示提示消息
function showAlert(message, type) {
    type = type || 'info';
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-' + type;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        setTimeout(function() {
            alertDiv.style.opacity = '0';
            setTimeout(function() {
                alertDiv.remove();
            }, 300);
        }, 3000);
    }
}

// ============ 操作人选择 ============

const operatorSelector = {
    operators: [],
    
    saveOperator: function(name) {
        // 保存新操作员到数据库（使用API_URL）
        const apiUrl = typeof API_URL !== 'undefined' ? API_URL : '/api';
        return fetch(apiUrl + '/customer/operators/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: name
            })
        }).then(function(response) {
            if (!response.ok) {
                throw new Error('保存失败');
            }
            return response.json();
        }).then(function(result) {
            if (result.success) {
                // 添加到本地列表
                const newOperator = {
                    id: result.operator_id,
                    name: name,
                    channels: []
                };
                operatorSelector.operators.push(newOperator);
                console.log('操作员保存成功:', name, 'ID:', result.operator_id);
                return result.operator_id;
            } else {
                console.error('保存失败:', result.error);
                throw new Error(result.error || '保存失败');
            }
        }).catch(function(error) {
            console.error('保存操作员失败:', error);
            throw error;
        });
    },
    
    loadOperators: function() {
        // 检测当前用户角色
        const isCustomer = document.querySelector('a[href^="/customer/"]');
        
        const baseUrl = typeof API_URL !== 'undefined' ? API_URL : '/api';
        let apiUrl;
        if (isCustomer) {
            // 客户角色：使用客户API
            apiUrl = baseUrl + '/customer/operators/list';
        } else {
            // 管理员角色：使用管理员API
            apiUrl = baseUrl + '/admin/operators/list';
        }
        
        fetch(apiUrl)
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                // 保存完整的操作员对象（包含ID和名称）
                operatorSelector.operators = data.operators;
            })
            .catch(function(error) {
                console.error('加载操作人列表失败:', error);
                operatorSelector.operators = [];
            });
    },
    
    initButtons: function() {
        // 此函数保留用于兼容性，但不再使用
        console.log('initButtons called - no action needed for new datalist implementation');
    },
    
    showSelector: function(recordId, callback) {
        const modal = document.getElementById('operatorModal');
        const input = document.getElementById('operatorInput');
        const operatorIdField = document.getElementById('operatorId');
        const datalist = document.getElementById('operatorList');
        // 从当前模态框中查找按钮，避免找到其他对话框的同名按钮
        const confirmBtn = modal.querySelector('#confirmOperatorBtn');
        const cancelBtn = modal.querySelector('#closeOperatorModalBtn');
        const closeBtn = modal.querySelector('.modal-close');
        
        if (!modal) {
            console.error('找不到 operatorModal 对话框');
            return;
        }
        
        // 填充历史操作人列表到datalist（桌面端）
        if (datalist) {
            datalist.innerHTML = '';
            operatorSelector.operators.forEach(function(op) {
                const option = document.createElement('option');
                option.value = op.name;
                option.setAttribute('data-id', op.id);
                datalist.appendChild(option);
            });
        }
        
        // 填充快速选择标签（移动端备选）
        const operatorTags = document.getElementById('operatorTags');
        if (operatorTags && operatorSelector.operators.length > 0) {
            operatorTags.innerHTML = '';
            operatorSelector.operators.forEach(function(op) {
                const tag = document.createElement('span');
                tag.className = 'operator-tag';
                tag.textContent = op.name;
                tag.dataset.operatorId = op.id;
                tag.dataset.operatorName = op.name;
                
                // 点击标签，填入input
                tag.addEventListener('click', function() {
                    if (input) {
                        input.value = op.name;
                        // 触发input事件，确保数据更新
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                });
                
                operatorTags.appendChild(tag);
            });
        } else if (operatorTags) {
            operatorTags.innerHTML = '<span style="color: #6c757d; font-size: 12px;">暂无历史操作员</span>';
        }
        
        // 清空输入和隐藏字段
        if (input) input.value = '';
        if (operatorIdField) operatorIdField.value = '';
        
        // 清空渠道选择
        document.querySelectorAll('input[name="channel"]').forEach(function(radio) {
            radio.checked = false;
        });
        
        const handleConfirm = function() {
            // 获取操作人ID和名称
            let operatorId = null;
            let operatorName = null;
            
            if (input && input.value.trim()) {
                operatorName = input.value.trim();
                
                // 检查操作员是否已存在
                const existingOperator = operatorSelector.operators.find(function(op) {
                    return op.name === operatorName;
                });
                
                if (existingOperator) {
                    // 操作员已存在，使用现有ID
                    operatorId = existingOperator.id;
                    console.log('使用现有操作员:', operatorName, 'ID:', operatorId);
                    
                    // 直接调用回调，传递现有操作员信息
                    finalizeSelection(operatorId, operatorName);
                } else {
                    // 新操作员，保存到数据库
                    console.log('保存新操作员:', operatorName);
                    
                    operatorSelector.saveOperator(operatorName)
                        .then(function(newOperatorId) {
                            console.log('新操作员保存成功，ID:', newOperatorId);
                            finalizeSelection(newOperatorId, operatorName);
                        })
                        .catch(function(error) {
                            console.error('保存新操作员失败:', error);
                            alert('保存新操作员失败：' + error.message);
                        });
                    
                    // 异步保存，直接返回
                    return;
                }
            } else {
                // 不选择操作员，设置为999（自己）
                operatorId = 999;
                operatorName = '自己';
                finalizeSelection(operatorId, operatorName);
            }
        };
        
        // 完成选择后的处理
        function finalizeSelection(finalOperatorId, finalOperatorName) {
            // 获取选中的渠道
            const channelRadio = document.querySelector('input[name="channel"]:checked');
            let channelId = null;
            let channelName = null;
            
            if (channelRadio) {
                // 使用parseInt转换为数字ID（1=微信, 2=支付宝, 3=其他）
                channelId = parseInt(channelRadio.value);
                channelName = channelRadio.dataset.channelName || channelRadio.value;
            }
            
            // 调用回调，传递ID和名称
            if (typeof callback === 'function') {
                callback({
                    operator_id: finalOperatorId,
                    operator_name: finalOperatorName,
                    channel_id: channelId,
                    channel_name: channelName
                });
            }
            
            operatorSelector.closeModal();
        };
        
        const handleCancel = function() {
            operatorSelector.closeModal();
        };
        
        // 移除旧的事件监听器（如果有的话）
        if (confirmBtn && cancelBtn && closeBtn) {
            const newConfirmBtn = confirmBtn.cloneNode(true);
            const newCancelBtn = cancelBtn.cloneNode(true);
            const newCloseBtn = closeBtn.cloneNode(true);
            
            confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
            cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
            closeBtn.parentNode.replaceChild(newCloseBtn, closeBtn);
            
            newConfirmBtn.addEventListener('click', handleConfirm);
            newCancelBtn.addEventListener('click', handleCancel);
            newCloseBtn.addEventListener('click', handleCancel);
        } else {
            console.error('模态框按钮未找到:', { confirmBtn, cancelBtn, closeBtn });
        }
        
        
        // 输入框回车事件（如果输入框存在）
        if (input) {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    handleConfirm();
                }
            });
        }
        
        operatorSelector.closeModal = function() {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        };
        
        operatorSelector.openModal = function() {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        };
        
        operatorSelector.openModal();
    }
};

// ============ 流水记录管理 ============

const recordManager = {
    init: function() {
        recordManager.initButtons();
        recordManager.initRefreshStats();
    },
    
    initButtons: function() {
        const buttons = document.querySelectorAll('.record-toggle-btn');
        
        buttons.forEach(function(button) {
            // 根据当前状态初始化按钮样式
            const currentStatus = button.dataset.status;
            if (currentStatus === 'done') {
                button.className = 'btn btn-sm btn-success record-toggle-btn';
            } else {
                button.className = 'btn btn-sm btn-danger record-toggle-btn';
            }
            
            button.addEventListener('click', async function(e) {
                const recordId = button.dataset.recordId;
                const currentStatus = button.dataset.status;
                
                if (currentStatus === 'pending') {
                    operatorSelector.showSelector(recordId, async function(data) {
                        await recordManager.updateStatus(recordId, 'done', data);
                        recordManager.updateDisplay(recordId, data, 'done');
                    });
                } else {
                    await recordManager.updateStatus(recordId, 'pending', null);
                    recordManager.updateDisplay(recordId, null, 'pending');
                }
            });
        });
    },
    
    updateStatus: function(recordId, status, data) {
        const requestBody = {
            record_id: recordId,
            status: status,
            operator_id: data ? data.operator_id : null,
            channel_id: data ? data.channel_id : null
        };
        
        const apiUrl = typeof API_URL !== 'undefined' ? API_URL : '/api';
        return fetch(apiUrl + '/update_record', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(requestBody)
        }).then(function(response) {
            if (!response.ok) {
                throw new Error('更新失败');
            }
            return response.json();
        }).catch(function(error) {
            console.error('更新记录状态失败:', error);
            showAlert('更新失败，请重试', 'danger');
            throw error;
        });
    },
    
    updateDisplay: function(recordId, data, status) {
        const row = document.querySelector('tr[data-record-id="' + recordId + '"]');
        if (!row) return;
        
        const statusCell = row.querySelector('[data-field="status"]');
        const operatorCell = row.querySelector('[data-field="operator"]');
        const button = row.querySelector('.record-toggle-btn');
        
        if (statusCell) {
            if (status === 'done') {
                statusCell.innerHTML = '<span class="badge badge-success">已刷</span>';
            } else {
                statusCell.innerHTML = '<span class="badge badge-pending">待刷</span>';
            }
        }
        
        if (operatorCell) {
            // 显示操作员名称
            if (data && data.operator_name) {
                operatorCell.textContent = data.operator_name;
            } else {
                operatorCell.textContent = '-';
            }
        }
        
        if (button) {
            button.dataset.status = status;
            if (status === 'done') {
                button.textContent = '已刷';
                button.className = 'btn btn-sm btn-success record-toggle-btn';
            } else {
                button.textContent = '待刷';
                button.className = 'btn btn-sm btn-danger record-toggle-btn';
            }
        }
        
        recordManager.refreshStats();
    },
    
    refreshStats: function() {
        if (!document.getElementById('completedValue')) return;
        
        const apiUrl = typeof API_URL !== 'undefined' ? API_URL : '/api';
        fetch(apiUrl + '/customer/stats')
            .then(function(response) {
                return response.json();
            })
            .then(function(stats) {
                const completedValue = document.getElementById('completedValue');
                const pendingValue = document.getElementById('pendingValue');
                const progressBar = document.getElementById('progressBar');
                
                if (completedValue) {
                    completedValue.textContent = formatCurrency(stats.completed);
                }
                if (pendingValue) {
                    pendingValue.textContent = formatCurrency(stats.pending);
                }
                if (progressBar) {
                    progressBar.style.width = stats.progress + '%';
                    progressBar.textContent = stats.progress.toFixed(1) + '%';
                }
                
                const completedCount = document.getElementById('completedCount');
                const pendingCount = document.getElementById('pendingCount');
                
                if (completedCount) completedCount.textContent = stats.completed_count;
                if (pendingCount) pendingCount.textContent = stats.pending_count;
            })
            .catch(function(error) {
                console.error('刷新统计数据失败:', error);
            });
    },
    
    initRefreshStats: function() {
        setInterval(function() {
            recordManager.refreshStats();
        }, 30000);
    }
};

// ============ 日期选择器（独立下拉框） ============

const datePicker = {
    init: function() {
        datePicker.initYearSelect();
        datePicker.initMonthSelect();
        datePicker.initDaySelect();
        datePicker.setDefaults();
        datePicker.initEvents();
    },
    
    initYearSelect: function() {
        const currentYear = new Date().getFullYear();
        const years = [];
        
        // 显示前后5年
        for (let i = -5; i <= 5; i++) {
            years.push(currentYear + i);
        }
        
        document.querySelectorAll('.year-select').forEach(function(select) {
            select.innerHTML = '';
            years.forEach(function(year) {
                const option = document.createElement('option');
                option.value = year;
                option.textContent = year + '年';
                select.appendChild(option);
            });
        });
    },
    
    initMonthSelect: function() {
        document.querySelectorAll('.month-select').forEach(function(select) {
            if (select.options.length > 0) return;
            
            select.innerHTML = '';
            for (let i = 1; i <= 12; i++) {
                const option = document.createElement('option');
                option.value = String(i).padStart(2, '0');
                option.textContent = i + '月';
                select.appendChild(option);
            }
        });
    },
    
    initDaySelect: function() {
        document.querySelectorAll('.day-select').forEach(function(select) {
            if (select.options.length > 0) return;
            
            select.innerHTML = '';
            for (let i = 1; i <= 31; i++) {
                const option = document.createElement('option');
                option.value = String(i).padStart(2, '0');
                option.textContent = i + '日';
                select.appendChild(option);
            }
        });
    },
    
    setDefaults: function() {
        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonth = String(now.getMonth() + 1).padStart(2, '0');
        const currentDay = String(now.getDate()).padStart(2, '0');
        
        // 设置默认年份
        document.querySelectorAll('.year-select').forEach(function(select) {
            select.value = currentYear;
        });
        
        // 设置默认月份
        document.querySelectorAll('.month-select').forEach(function(select) {
            select.value = currentMonth;
        });
        
        // 设置默认日期
        document.querySelectorAll('.day-select').forEach(function(select) {
            select.value = currentDay;
        });
    },
    
    initEvents: function() {
        // 当月份或年份变化时，更新日期选项（考虑不同月份的天数）
        document.querySelectorAll('.month-select, .year-select').forEach(function(select) {
            select.addEventListener('change', datePicker.updateDays);
        });
        
        // 当任何日期选择器变化时，同步到隐藏的input字段
        document.querySelectorAll('.date-picker-container').forEach(function(container) {
            const yearSelect = container.querySelector('.year-select');
            const monthSelect = container.querySelector('.month-select');
            const daySelect = container.querySelector('.day-select');
            const hiddenInput = container.querySelector('input[type="hidden"]');
            
            if (yearSelect && monthSelect && daySelect && hiddenInput) {
                const updateHiddenInput = function() {
                    const year = yearSelect.value;
                    const month = monthSelect.value;
                    const day = daySelect.value;
                    
                    if (year && month && day) {
                        hiddenInput.value = year + '-' + month + '-' + day;
                    }
                };
                
                yearSelect.addEventListener('change', updateHiddenInput);
                monthSelect.addEventListener('change', updateHiddenInput);
                daySelect.addEventListener('change', updateHiddenInput);
                
                // 初始同步
                updateHiddenInput();
            }
        });
        
        // 初始更新
        datePicker.updateDays();
    },
    
    updateDays: function() {
        const yearSelects = document.querySelectorAll('.year-select');
        const monthSelects = document.querySelectorAll('.month-select');
        const daySelects = document.querySelectorAll('.day-select');
        
        yearSelects.forEach(function(yearSelect, index) {
            const monthSelect = monthSelects[index];
            const daySelect = daySelects[index];
            
            if (!yearSelect || !monthSelect || !daySelect) return;
            
            const year = parseInt(yearSelect.value);
            const month = parseInt(monthSelect.value);
            
            // 获取该月有多少天
            const daysInMonth = new Date(year, month, 0).getDate();
            
            // 保存当前选中的日期
            const currentDay = daySelect.value;
            
            // 清空并重新填充日期
            daySelect.innerHTML = '';
            for (let i = 1; i <= daysInMonth; i++) {
                const option = document.createElement('option');
                option.value = String(i).padStart(2, '0');
                option.textContent = i + '日';
                daySelect.appendChild(option);
            }
            
            // 恢复之前选中的日期（如果存在）
            if (currentDay && parseInt(currentDay) <= daysInMonth) {
                daySelect.value = currentDay;
            } else {
                // 否则选择该月的最后一天
                daySelect.value = String(daysInMonth).padStart(2, '0');
            }
        });
    },
    
    // 获取完整日期字符串
    getDateValue: function(container) {
        const yearSelect = container.querySelector('.year-select');
        const monthSelect = container.querySelector('.month-select');
        const daySelect = container.querySelector('.day-select');
        
        if (!yearSelect || !monthSelect || !daySelect) return null;
        
        return yearSelect.value + '-' + monthSelect.value + '-' + daySelect.value;
    }
};

// ============ 今天按钮功能 ============

const todayButton = {
    init: function() {
        const todayBtn = document.getElementById('todayBtn');
        if (!todayBtn) return;
        
        todayBtn.addEventListener('click', function() {
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            
            // 设置起始日期
            const startYearSelect = document.querySelector('select[name="start_year"]');
            const startMonthSelect = document.querySelector('select[name="start_month"]');
            const startDaySelect = document.querySelector('select[name="start_day"]');
            
            if (startYearSelect) startYearSelect.value = year;
            if (startMonthSelect) startMonthSelect.value = month;
            if (startDaySelect) startDaySelect.value = day;
            
            // 设置结束日期
            const endYearSelect = document.querySelector('select[name="end_year"]');
            const endMonthSelect = document.querySelector('select[name="end_month"]');
            const endDaySelect = document.querySelector('select[name="end_day"]');
            
            if (endYearSelect) endYearSelect.value = year;
            if (endMonthSelect) endMonthSelect.value = month;
            if (endDaySelect) endDaySelect.value = day;
            
            // 提交表单
            const filterForm = document.getElementById('filterForm');
            if (filterForm) {
                filterForm.submit();
            }
        });
    }
};

// ============ 页面加载初始化 ============

document.addEventListener('DOMContentLoaded', function() {
    operatorSelector.loadOperators();
    operatorSelector.initButtons();
    
    datePicker.init();
    
    todayButton.init();
    
    const buttons = document.querySelectorAll('.record-toggle-btn');
    if (buttons.length > 0) {
        recordManager.init();
    }
});

// ============ 导出函数 ============

window.showAlert = showAlert;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
