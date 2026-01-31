/**
 * API配置文件
 * 用于管理前后端分离时的API地址
 */

// API配置
const API_CONFIG = {
    // 开发环境API地址
    development: 'http://localhost:5000/api',
    
    // 生产环境API地址
    // 部署到PythonAnywhere后，修改为你的地址
    // 格式: https://你的用户名.pythonanywhere.com
    production: 'https://your-username.pythonanywhere.com/api'
};

// 自动选择环境
// 如果在localhost上运行，使用development
// 否则使用production
const isDevelopment = window.location.hostname === 'localhost' || 
                      window.location.hostname === '127.0.0.1' ||
                      window.location.protocol === 'file:';

// 当前API地址
const API_URL = isDevelopment ? API_CONFIG.development : API_CONFIG.production;

// 导出配置（如果需要模块化）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API_CONFIG, API_URL, isDevelopment };
}

/**
 * API请求封装函数
 * 统一处理API请求、错误处理、添加必要头信息
 */
const apiRequest = async (endpoint, options = {}) => {
    const url = `${API_URL}${endpoint}`;
    
    // 默认配置
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include', // 包含cookies
        ...options
    };
    
    try {
        const response = await fetch(url, defaultOptions);
        
        // 检查响应状态
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // 解析JSON响应
        const data = await response.json();
        
        return data;
    } catch (error) {
        console.error('API请求失败:', error);
        throw error;
    }
};

/**
 * 常用API方法
 */
const API = {
    // GET请求
    get: (endpoint) => apiRequest(endpoint),
    
    // POST请求
    post: (endpoint, data) => apiRequest(endpoint, {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    
    // PUT请求
    put: (endpoint, data) => apiRequest(endpoint, {
        method: 'PUT',
        body: JSON.stringify(data)
    }),
    
    // DELETE请求
    delete: (endpoint) => apiRequest(endpoint, {
        method: 'DELETE'
    })
};

// 在全局作用域中可用
window.API_CONFIG = API_CONFIG;
window.API_URL = API_URL;
window.API = API;

console.log(`当前API地址: ${API_URL}`);
console.log(`环境: ${isDevelopment ? '开发环境' : '生产环境'}`);
