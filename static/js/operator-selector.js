// ============ API配置导入 ============
// 确保config.js已加载
if (typeof API_URL === 'undefined') {
    console.error('API配置未加载，请确保config.js在operator-selector.js之前加载');
}

// ============ 操作员和渠道选择器 - 新版本 ============

const operatorChannelSelector = {
    operators: [],
    currentRecordId: null,
    currentCallback: null,
    
    // 加载操作员列表
    loadOperators: function() {
        const apiUrl = typeof API_URL !== 'undefined' ? API_URL : '/api';
        fetch(apiUrl + '/customer/operators/list')
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                operatorChannelSelector.operators = data.operators || [];
                console.log('已加载操作员列表:', operatorChannelSelector.operators);
            })
            .catch(function(error) {
                console.error('加载操作人列表失败:', error);
                operatorChannelSelector.operators = [];
            });
    },
    
    // 显示选择对话框
    showSelector: function(recordId, callback) {
        operatorChannelSelector.currentRecordId = recordId;
        operatorChannelSelector.currentCallback = callback;
        
        const modal = document.getElementById('operatorChannelModal');
        const operatorOptions = document.getElementById('operatorOptions');
        const channelContainer = document.getElementById('channelContainer');
        const channelOptions = document.getElementById('channelOptions');
        
        // 清空之前的选择
        operatorOptions.innerHTML = '';
        channelOptions.innerHTML = '';
        channelContainer.style.display = 'none';
        
        // 添加"我自己操作"选项
        const selfOption = document.createElement('div');
        selfOption.className = 'operator-option-item selected';
        selfOption.dataset.type = 'self';
        selfOption.innerHTML = '<strong>👤 我自己操作</strong>';
        selfOption.addEventListener('click', function() {
            operatorChannelSelector.selectOperator(this, null);
        });
        operatorOptions.appendChild(selfOption);
        
        // 添加已有操作员选项
        operatorChannelSelector.operators.forEach(function(op) {
            const option = document.createElement('div');
            option.className = 'operator-option-item';
            option.dataset.type = 'operator';
            option.dataset.operatorId = op.id;
            option.dataset.operatorName = op.name;
            option.innerHTML = `<strong>👥 ${op.name}</strong>`;
            option.addEventListener('click', function() {
                operatorChannelSelector.selectOperator(this, op);
            });
            operatorOptions.appendChild(option);
        });
        
        // 添加"新建操作员"选项
        const newOption = document.createElement('div');
        newOption.className = 'operator-option-item';
        newOption.dataset.type = 'new';
        newOption.innerHTML = '<strong>➕ 新建操作员</strong>';
        newOption.addEventListener('click', function() {
            operatorChannelSelector.showNewOperatorForm();
        });
        operatorOptions.appendChild(newOption);
        
        // 显示模态框
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    },
    
    // 选择操作员
    selectOperator: function(element, operator) {
        // 移除其他选项的选中状态
        document.querySelectorAll('.operator-option-item').forEach(function(item) {
            item.classList.remove('selected');
        });
        element.classList.add('selected');
        
        const channelContainer = document.getElementById('channelContainer');
        const channelOptions = document.getElementById('channelOptions');
        channelOptions.innerHTML = '';
        
        if (operator && operator.channels && operator.channels.length > 0) {
            // 显示支付渠道
            channelContainer.style.display = 'block';
            
            operator.channels.forEach(function(channel) {
                const option = document.createElement('div');
                option.className = 'channel-option-item';
                option.dataset.channelId = channel.id;
                option.dataset.channelName = channel.name;
                option.innerHTML = `<span>💳 ${channel.name}</span>`;
                option.addEventListener('click', function() {
                    operatorChannelSelector.confirmSelection(operator, channel);
                });
                channelOptions.appendChild(option);
            });
        } else {
            // 没有渠道，直接确认
            channelContainer.style.display = 'none';
            if (operatorChannelSelector.currentCallback) {
                operatorChannelSelector.currentCallback({
                    operatorId: operator ? operator.id : null,
                    operatorName: operator ? operator.name : '我自己操作',
                    channelId: null,
                    channelName: null
                });
            }
            operatorChannelSelector.closeModal();
        }
    },
    
    // 显示新建操作员表单
    showNewOperatorForm: function() {
        const modal = document.getElementById('operatorChannelModal');
        const formContainer = document.getElementById('newOperatorFormContainer');
        
        // 隐藏操作员列表
        document.getElementById('operatorOptions').parentElement.style.display = 'none';
        document.getElementById('channelContainer').style.display = 'none';
        
        // 显示表单
        formContainer.style.display = 'block';
    },
    
    // 保存新建操作员
    saveNewOperator: function() {
        const name = document.getElementById('newOperatorName').value.trim();
        const channelCheckboxes = document.querySelectorAll('input[name="newChannels"]:checked');
        const channels = Array.from(channelCheckboxes).map(cb => cb.value);
        
        if (!name) {
            showAlert('请输入操作员姓名', 'danger');
            return;
        }
        
        const apiUrl = typeof API_URL !== 'undefined' ? API_URL : '/api';
        fetch(apiUrl + '/customer/operators/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: name,
                channels: channels
            })
        })
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            if (data.success) {
                showAlert('操作员添加成功！', 'success');
                // 重新加载操作员列表
                operatorChannelSelector.loadOperators();
                // 重新显示选择器
                setTimeout(function() {
                    operatorChannelSelector.showSelector(
                        operatorChannelSelector.currentRecordId,
                        operatorChannelSelector.currentCallback
                    );
                }, 500);
            } else {
                showAlert('添加失败：' + data.error, 'danger');
            }
        })
        .catch(function(error) {
            showAlert('添加失败：' + error.message, 'danger');
        });
    },
    
    // 取消新建
    cancelNewOperator: function() {
        // 隐藏表单，显示操作员列表
        document.getElementById('newOperatorFormContainer').style.display = 'none';
        document.getElementById('operatorOptions').parentElement.style.display = 'block';
        document.getElementById('newOperatorName').value = '';
        document.querySelectorAll('input[name="newChannels"]').forEach(cb => cb.checked = false);
    },
    
    // 确认选择
    confirmSelection: function(operator, channel) {
        if (operatorChannelSelector.currentCallback) {
            operatorChannelSelector.currentCallback({
                operatorId: operator.id,
                operatorName: operator.name,
                channelId: channel.id,
                channelName: channel.name
            });
        }
        operatorChannelSelector.closeModal();
    },
    
    // 关闭模态框
    closeModal: function() {
        const modal = document.getElementById('operatorChannelModal');
        modal.classList.remove('active');
        document.body.style.overflow = '';
        
        // 重置表单
        document.getElementById('newOperatorFormContainer').style.display = 'none';
        document.getElementById('operatorOptions').parentElement.style.display = 'block';
        document.getElementById('channelContainer').style.display = 'none';
    }
};

// ============ 流水记录管理器 - 更新版本 ============

const recordManager = {
    init: function() {
        recordManager.initButtons();
        recordManager.initRefreshStats();
    },
    
    initButtons: function() {
        const buttons = document.querySelectorAll('.record-toggle-btn');
        
        buttons.forEach(function(button) {
            button.addEventListener('click', async function() {
                const recordId = button.dataset.recordId;
                const currentStatus = button.dataset.status;
                
                if (currentStatus === 'pending') {
                    // 显示操作员选择对话框
                    operatorChannelSelector.showSelector(recordId, async function(selection) {
                        await recordManager.updateStatus(recordId, 'done', selection);
                        recordManager.updateDisplay(recordId, selection, 'done');
                    });
                } else {
                    // 取消标记
                    await recordManager.updateStatus(recordId, 'pending', null);
                    recordManager.updateDisplay(recordId, null, 'pending');
                }
            });
        });
    },
    
    updateStatus: function(recordId, status, selection) {
        const data = {
            record_id: recordId,
            status: status
        };
        
        if (selection) {
            data.operator_id = selection.operatorId;
            data.channel_id = selection.channelId;
        }
        
        const apiUrl = typeof API_URL !== 'undefined' ? API_URL : '/api';
        return fetch(apiUrl + '/update_record', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(function(response) {
            if (!response.ok) {
                throw new Error('更新失败');
            }
            return response.json();
        })
        .catch(function(error) {
            console.error('更新记录状态失败:', error);
            showAlert('更新失败，请重试', 'danger');
            throw error;
        });
    },
    
    updateDisplay: function(recordId, selection, status) {
        const row = document.querySelector('tr[data-record-id="' + recordId + '"]');
        if (!row) return;
        
        const operatorCell = row.querySelector('[data-field="operator"]');
        const button = row.querySelector('.record-toggle-btn');
        
        // 更新操作员和渠道显示
        if (operatorCell) {
            if (selection) {
                let text = selection.operatorName;
                if (selection.channelName) {
                    text += ` (${selection.channelName})`;
                }
                operatorCell.textContent = text;
            } else {
                operatorCell.textContent = '-';
            }
        }
        
        // 更新按钮状态
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
        // 统计数据刷新逻辑保持不变
    },
    
    initRefreshStats: function() {
        setInterval(function() {
            recordManager.refreshStats();
        }, 30000);
    }
};

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    operatorChannelSelector.loadOperators();
    if (document.querySelector('.record-toggle-btn')) {
        recordManager.init();
    }
    
    // 绑定新建操作员按钮
    const saveOperatorBtn = document.getElementById('saveOperatorBtn');
    const cancelNewOperatorBtn = document.getElementById('cancelNewOperatorBtn');
    
    if (saveOperatorBtn) {
        saveOperatorBtn.addEventListener('click', operatorChannelSelector.saveNewOperator);
    }
    
    if (cancelNewOperatorBtn) {
        cancelNewOperatorBtn.addEventListener('click', operatorChannelSelector.cancelNewOperator);
    }
});
