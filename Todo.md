# Context
（1）这是一个前后端分离的Docker-compose项目。
（2）目前项目中存在一些问题，等待修复，主要是颜色标注的效果不佳。
（3）目前后端核心用到的文件是：app\utils\document_compare.py app\utils\document_parser.py app\utils\pdf_highlighter.py
（4）PDF是写入的方式标注颜色，但是目前标注的效果不佳，这是目前的：temp_files\ 一些标注的效果
（5）前端页面主要是这个：frontend\src\views\CompareView.vue
# Log
2025-09-02 14:29:48,261 - app.routers.compare - INFO - 开始比较已上传文件: 【用户运营_成都 9-14K】方卉泽 4年.pdf vs 【用户运营_成都 9-14K】方卉泽 4年.pdf
2025-09-02 14:29:48,261 - app.utils.document_compare - INFO - 开始比较文档: 【用户运营_成都 9-14K】方卉泽 4年.pdf vs 【用户运营_成都 9-14K】方卉泽 4年.pdf
2025-09-02 14:29:48,374 - app.utils.document_compare - INFO - 找到 1 个连续匹配块
2025-09-02 14:29:48,374 - app.utils.document_compare - INFO - 文档比对完成，整体相似度: 0.955
2025-09-02 14:29:48,375 - app.routers.compare - INFO - 为文件B生成高亮PDF: 【用户运营_成都 9-14K】方卉泽 4年.pdf
2025-09-02 14:29:48,375 - app.utils.pdf_highlighter - INFO - 打开PDF文档: /tmp/tmp0a56pifd.pdf, 页数: 2
2025-09-02 14:29:48,376 - app.utils.pdf_highlighter - INFO - 待高亮文本数量: 1
2025-09-02 14:29:48,384 - app.utils.pdf_highlighter - WARNING - 1 个文本块未在PDF中找到匹配项。
2025-09-02 14:29:48,395 - app.utils.pdf_highlighter - INFO - PDF高亮完成，总共添加0个高亮，保存到: /app/temp_files/tmp0a56pifd_tmpj0tdus1u_highlighted.pdf
2025-09-02 14:29:48,411 - app.routers.compare - INFO - ✓ 高亮PDF已生成并缓存: 59ac285f-b403-4073-ba39-3a48e8d946fb_highlighted
2025-09-02 14:29:48,411 - app.routers.compare - INFO - ✓ 高亮文件大小: 674686 bytes
2025-09-02 14:29:48,411 - app.routers.compare - INFO - ✓ highlighted_file_ids 当前值: {'file_b': '59ac285f-b403-4073-ba39-3a48e8d946fb_highlighted'}
2025-09-02 14:29:48,411 - app.routers.compare - INFO - ✓ 缓存键列表: ['8a19b593-a344-49bf-a866-81992f01964a', '3e8bbdf8-d1d2-4c9d-8b0a-0ee71bfe7d3c', '3e8bbdf8-d1d2-4c9d-8b0a-0ee71bfe7d3c_highlighted', '36ae29cd-1fa8-492e-a0d9-10d6cbd3fbe7', '1108b155-62bc-449c-952f-dd96c7dd306e', '1108b155-62bc-449c-952f-dd96c7dd306e_highlighted', '370c8cbd-5d12-43e0-bd34-683fa659b8a1', '59ac285f-b403-4073-ba39-3a48e8d946fb', '59ac285f-b403-4073-ba39-3a48e8d946fb_highlighted']
2025-09-02 14:29:48,411 - app.routers.compare - INFO - highlighted_file_ids: {'file_b': '59ac285f-b403-4073-ba39-3a48e8d946fb_highlighted'}
2025-09-02 14:29:48,411 - app.routers.compare - INFO - result['metadata'] 当前内容: {'algorithm_params': {'similarity_threshold_high': 0.9, 'similarity_threshold_medium': 0.7, 'min_block_length': 3}, 'comparison_time': datetime.datetime(2025, 9, 2, 14, 29, 48, 411592)}
2025-09-02 14:29:48,411 - app.routers.compare - INFO - 已添加highlighted_files到结果: {'file_b': '59ac285f-b403-4073-ba39-3a48e8d946fb_highlighted'}
2025-09-02 14:29:48,411 - app.routers.compare - INFO - 最终metadata内容: {'algorithm_params': {'similarity_threshold_high': 0.9, 'similarity_threshold_medium': 0.7, 'min_block_length': 3}, 'comparison_time': datetime.datetime(2025, 9, 2, 14, 29, 48, 411592), 'highlighted_files': {'file_b': '59ac285f-b403-4073-ba39-3a48e8d946fb_highlighted'}}
2025-09-02 14:29:48,411 - app.routers.compare - INFO - 文件比较完成，整体相似度: 0.955
INFO:     172.19.0.4:37652 - "POST /api/compare/files HTTP/1.0" 200 OK
INFO:     172.19.0.4:37666 - "GET /api/compare/download/370c8cbd-5d12-43e0-bd34-683fa659b8a1?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhNTIwMWNmMy05NzY1LTRhZjAtOWJlNy1lZWM3Mzc5YTdiNWUiLCJleHAiOjE3NTY3OTQ4MzZ9.ydyRxkY0yobcQHkZ2bIkQwmiLAn1g0YmNMT6hGDusPM HTTP/1.0" 200 OK
2025-09-02 14:29:48,529 - app.routers.compare - INFO - 请求高亮文件: 59ac285f-b403-4073-ba39-3a48e8d946fb, 缓存键: 59ac285f-b403-4073-ba39-3a48e8d946fb_highlighted
2025-09-02 14:29:48,529 - app.routers.compare - INFO - 缓存中的文件键: ['8a19b593-a344-49bf-a866-81992f01964a', '3e8bbdf8-d1d2-4c9d-8b0a-0ee71bfe7d3c', '3e8bbdf8-d1d2-4c9d-8b0a-0ee71bfe7d3c_highlighted', '36ae29cd-1fa8-492e-a0d9-10d6cbd3fbe7', '1108b155-62bc-449c-952f-dd96c7dd306e', '1108b155-62bc-449c-952f-dd96c7dd306e_highlighted', '370c8cbd-5d12-43e0-bd34-683fa659b8a1', '59ac285f-b403-4073-ba39-3a48e8d946fb', '59ac285f-b403-4073-ba39-3a48e8d946fb_highlighted']
2025-09-02 14:29:48,529 - app.routers.compare - INFO - 返回高亮文件: highlighted_【用户运营_成都 9-14K】方卉泽 4年.pdf, 大小: 674686 bytes
INFO:     172.19.0.4:37668 - "GET /api/compare/download/59ac285f-b403-4073-ba39-3a48e8d946fb/highlighted?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhNTIwMWNmMy05NzY1LTRhZjAtOWJlNy1lZWM3Mzc5YTdiNWUiLCJleHAiOjE3NTY3OTQ4MzZ9.ydyRxkY0yobcQHkZ2bIkQwmiLAn1g0YmNMT6hGDusPM&t=1756794588432 HTTP/1.0" 200 OK
INFO:     172.19.0.4:37670 - "GET /api/compare/download/370c8cbd-5d12-43e0-bd34-683fa659b8a1?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhNTIwMWNmMy05NzY1LTRhZjAtOWJlNy1lZWM3Mzc5YTdiNWUiLCJleHAiOjE3NTY3OTQ4MzZ9.ydyRxkY0yobcQHkZ2bIkQwmiLAn1g0YmNMT6hGDusPM HTTP/1.0" 200 OK
INFO:     172.19.0.4:37684 - "GET /api/compare/download/370c8cbd-5d12-43e0-bd34-683fa659b8a1?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhNTIwMWNmMy05NzY1LTRhZjAtOWJlNy1lZWM3Mzc5YTdiNWUiLCJleHAiOjE3NTY3OTQ4MzZ9.ydyRxkY0yobcQHkZ2bIkQwmiLAn1g0YmNMT6hGDusPM HTTP/1.0" 200 OK
2025-09-02 14:29:48,675 - app.routers.compare - INFO - 请求高亮文件: 59ac285f-b403-4073-ba39-3a48e8d946fb, 缓存键: 59ac285f-b403-4073-ba39-3a48e8d946fb_highlighted
2025-09-02 14:29:48,675 - app.routers.compare - INFO - 缓存中的文件键: ['8a19b593-a344-49bf-a866-81992f01964a', '3e8bbdf8-d1d2-4c9d-8b0a-0ee71bfe7d3c', '3e8bbdf8-d1d2-4c9d-8b0a-0ee71bfe7d3c_highlighted', '36ae29cd-1fa8-492e-a0d9-10d6cbd3fbe7', '1108b155-62bc-449c-952f-dd96c7dd306e', '1108b155-62bc-449c-952f-dd96c7dd306e_highlighted', '370c8cbd-5d12-43e0-bd34-683fa659b8a1', '59ac285f-b403-4073-ba39-3a48e8d946fb', '59ac285f-b403-4073-ba39-3a48e8d946fb_highlighted']
2025-09-02 14:29:48,675 - app.routers.compare - INFO - 返回高亮文件: highlighted_【用户运营_成都 9-14K】方卉泽 4年.pdf, 大小: 674686 bytes
INFO:     172.19.0.4:37698 - "GET /api/compare/download/59ac285f-b403-4073-ba39-3a48e8d946fb/highlighted?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhNTIwMWNmMy05NzY1LTRhZjAtOWJlNy1lZWM3Mzc5YTdiNWUiLCJleHAiOjE3NTY3OTQ4MzZ9.ydyRxkY0yobcQHkZ2bIkQwmiLAn1g0YmNMT6hGDusPM&t=1756794588567 HTTP/1.0" 200 OK
2025-09-02 14:29:48,680 - app.routers.compare - INFO - 请求高亮文件: 59ac285f-b403-4073-ba39-3a48e8d946fb, 缓存键: 59ac285f-b403-4073-ba39-3a48e8d946fb_highlighted
2025-09-02 14:29:48,680 - app.routers.compare - INFO - 缓存中的文件键: ['8a19b593-a344-49bf-a866-81992f01964a', '3e8bbdf8-d1d2-4c9d-8b0a-0ee71bfe7d3c', '3e8bbdf8-d1d2-4c9d-8b0a-0ee71bfe7d3c_highlighted', '36ae29cd-1fa8-492e-a0d9-10d6cbd3fbe7', '1108b155-62bc-449c-952f-dd96c7dd306e', '1108b155-62bc-449c-952f-dd96c7dd306e_highlighted', '370c8cbd-5d12-43e0-bd34-683fa659b8a1', '59ac285f-b403-4073-ba39-3a48e8d946fb', '59ac285f-b403-4073-ba39-3a48e8d946fb_highlighted']
2025-09-02 14:29:48,680 - app.routers.compare - INFO - 返回高亮文件: highlighted_【用户运营_成都 9-14K】方卉泽 4年.pdf, 大小: 674686 bytes
INFO:     172.19.0.4:37700 - "GET /api/compare/download/59ac285f-b403-4073-ba39-3a48e8d946fb/highlighted?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhNTIwMWNmMy05NzY1LTRhZjAtOWJlNy1lZWM3Mzc5YTdiNWUiLCJleHAiOjE3NTY3OTQ4MzZ9.ydyRxkY0yobcQHkZ2bIkQwmiLAn1g0YmNMT6hGDusPM&t=1756794588567 HTTP/1.0" 200 OK
## Todo
1. 当我发现了还有一个问题，就是我上传一些PDF格式比较奇怪，比如说简历这种
2，虽然是完全相同的文本（两个相同的PDF）,但是没有进行标注
3. 我分析的原因，可能是Markitdown解析文档的时候是有Markdown格式导致的。这种是不是可以用我设计的一些过滤算法，获取出文本，因为Markitdown解析的方法还是很好的,只是有Markdown格式
（是不是可以用正则表达式来过滤掉！）

