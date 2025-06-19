# 语义搜索桌面应用

基于 Vue 3 + TypeScript + Electron 构建的语义搜索桌面应用。

## 功能特性

- 🔍 **智能搜索** - 支持BM25和TF-IDF混合搜索算法，精确匹配用户需求
- 📄 **文档管理** - 支持PDF、Word、TXT、Markdown等多种格式文件
- 📊 **搜索分析** - 详细的评分信息和搜索时间统计
- 👤 **用户系统** - 完整的注册、登录、权限管理功能
- 🎨 **现代设计** - 玻璃拟态效果、渐变色彩、流畅动画
- 🖥️ **跨平台** - Windows、macOS、Linux全平台支持
- 🔐 **安全认证** - JWT token认证，路由守卫保护
- ⚙️ **个性化** - 用户偏好设置，自定义搜索参数

## 技术栈

- **前端框架**: Vue 3 + TypeScript
- **UI组件库**: Element Plus
- **桌面框架**: Electron
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP客户端**: Axios

## 开发环境设置

### 前置要求

- Node.js >= 16
- npm 或 yarn

### 安装依赖

\`\`\`bash
cd frontend
npm install
\`\`\`

### 开发模式

\`\`\`bash
# 启动开发服务器
npm run dev

# 启动Electron开发模式
npm run electron:dev
\`\`\`

### 生产构建

\`\`\`bash
# 构建Web应用
npm run build

# 构建Electron应用
npm run electron:build
\`\`\`

## 项目结构

\`\`\`
frontend/
├── electron/                 # Electron相关文件
│   ├── main.ts              # 主进程
│   └── preload.ts           # 预加载脚本
├── src/
│   ├── components/          # 公共组件
│   ├── views/               # 页面组件
│   │   ├── SearchView.vue   # 搜索页面
│   │   ├── DocumentsView.vue # 文档管理页面
│   │   └── UploadView.vue   # 文档上传页面
│   ├── services/            # API服务
│   │   └── api.ts           # API接口
│   ├── types/               # 类型定义
│   │   └── api.ts           # API类型
│   ├── router/              # 路由配置
│   ├── stores/              # 状态管理
│   ├── assets/              # 静态资源
│   ├── App.vue              # 根组件
│   └── main.ts              # 入口文件
├── scripts/                 # 构建脚本
├── package.json
└── README.md
\`\`\`

## 配置说明

### API配置

在 \`src/services/api.ts\` 中修改后端API地址：

\`\`\`typescript
const API_BASE_URL = 'http://localhost:8500/api'
\`\`\`

### Electron配置

在 \`package.json\` 中的 \`build\` 字段配置打包选项：

\`\`\`json
{
  "build": {
    "appId": "com.semantic.search",
    "productName": "语义搜索",
    "win": {
      "target": "nsis"
    },
    "mac": {
      "category": "public.app-category.productivity"
    },
    "linux": {
      "target": "AppImage"
    }
  }
}
\`\`\`

## 使用说明

1. **搜索功能**
   - 在搜索页面输入关键词进行搜索
   - 可调整BM25和TF-IDF权重
   - 查看详细的搜索结果和评分

2. **文档管理**
   - 查看已上传的文档列表
   - 删除不需要的文档
   - 在特定文档中搜索

3. **文档上传**
   - 支持拖拽上传
   - 批量上传多个文件
   - 实时显示上传进度

## 开发指南

### 添加新页面

1. 在 \`src/views/\` 创建新的Vue组件
2. 在 \`src/router/index.ts\` 添加路由配置
3. 在导航菜单中添加对应项目

### 添加新API

1. 在 \`src/types/api.ts\` 定义类型
2. 在 \`src/services/api.ts\` 添加API方法
3. 在组件中调用API方法

### 样式自定义

- 全局样式在 \`src/assets/styles/main.css\`
- 组件样式使用 scoped CSS
- 可自定义 Element Plus 主题

## 部署说明

### 打包桌面应用

\`\`\`bash
# 打包所有平台
npm run electron:build

# 仅打包当前平台
npm run electron:build -- --publish=never
\`\`\`

生成的安装包在 \`dist-app/\` 目录下。

## 故障排除

### 常见问题

1. **依赖安装失败**
   - 使用国内镜像源：\`npm config set registry https://registry.npmmirror.com\`

2. **Electron下载失败**
   - 设置环境变量：\`ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/\`

3. **API连接失败**
   - 检查后端服务是否启动
   - 确认API地址配置正确

4. **打包失败**
   - 清理node_modules重新安装
   - 检查Node.js版本兼容性

## 许可证

MIT License