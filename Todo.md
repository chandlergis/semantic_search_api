# Context
（1）这是一个前后端分离的Docker-compose项目。
（2）目前后端核心用到的文件是：app\utils\document_compare.py app\utils\document_parser.py app\utils\pdf_highlighter.py
（3）前端页面主要是这个：frontend\src\views\CompareView.vue
# Log
2025-09-04 10:52:47,544 - app.routers.compare - INFO - 开始解析文件: 教师酬金信息 -黄毅豪.docx
2025-09-04 10:52:47,546 - app.utils.document_parser - INFO - Created temporary file: /tmp/tmpvvv77yxs_教师酬金信息 -黄毅豪.docx
2025-09-04 10:52:47,546 - app.utils.document_parser - INFO - Converting file: /tmp/tmpvvv77yxs_教师酬金信息 -黄毅豪.docx (original: 教师酬金信息 -黄毅豪.docx)
2025-09-04 10:52:47,546 - app.utils.document_parser - INFO - Starting MarkItDown conversion for: /tmp/tmpvvv77yxs_教师酬金信息 -黄毅豪.docx
2025-09-04 10:52:47,596 - app.utils.document_parser - INFO - MarkItDown conversion completed in 0.05 seconds
2025-09-04 10:52:47,596 - app.utils.document_parser - INFO - Conversion successful, content length: 526
2025-09-04 10:52:47,596 - app.utils.document_parser - INFO - Content preview: 教师简介：（一段话，约150字）

*\*\*\*，男/女，公司及职位，……*

黄毅豪，人工智能方向硕士，毕业于江西师范大学。长期深耕AI技术研发与产业落地，现就职于南瑞信通，担任大模型实施工程师，致力于为企业提供高效、创新的AIGC解决方 案。拥有多年一线研发与项目管理经验，主导了多个企业级AI项目的成功部署，因其在技术创新与应用实践中的卓越表现，荣获“2024年川渝地区效率先锋”称号，并获得工信部AIGC导师级专家认证。

职称证明材料：

*![](data:image/jpeg;base64...)![](data:image/jpeg;base64...)*

身份证正反面照片：

![](data:image/jpeg;base64...)![](data:image/jpeg;base64...)

银行卡照片：

![](data:image/jpeg;base64...)

姓名：黄毅豪 身份证号：362525199901180010

电话：13117855518 单位：南京南瑞信息通信科技有限公司

账号：6214830379712663

开户银行：招商银行南昌
2025-09-04 10:52:47,596 - app.utils.document_parser - INFO - Temporary file deleted: /tmp/tmpvvv77yxs_教师酬金信息 -黄毅豪.docx
2025-09-04 10:52:47,599 - app.routers.compare - INFO - 文件上传成功: 教师酬金信息 -黄毅豪.docx, ID: f4b328d9-4ac7-46a5-a7d2-81c60b4f31b2
INFO:     172.19.0.2:36460 - "POST /api/compare/upload HTTP/1.0" 200 OK
2025-09-04 10:52:47,628 - app.routers.compare - INFO - 开始解析文件: 教师酬金信息 -黄毅豪.docx
2025-09-04 10:52:47,629 - app.utils.document_parser - INFO - Created temporary file: /tmp/tmpnxorbunt_教师酬金信息 -黄毅豪.docx
2025-09-04 10:52:47,629 - app.utils.document_parser - INFO - Converting file: /tmp/tmpnxorbunt_教师酬金信息 -黄毅豪.docx (original: 教师酬金信息 -黄毅豪.docx)
2025-09-04 10:52:47,629 - app.utils.document_parser - INFO - Starting MarkItDown conversion for: /tmp/tmpnxorbunt_教师酬金信息 -黄毅豪.docx
2025-09-04 10:52:47,673 - app.utils.document_parser - INFO - MarkItDown conversion completed in 0.04 seconds
2025-09-04 10:52:47,673 - app.utils.document_parser - INFO - Conversion successful, content length: 526
2025-09-04 10:52:47,673 - app.utils.document_parser - INFO - Content preview: 教师简介：（一段话，约150字）

*\*\*\*，男/女，公司及职位，……*

黄毅豪，人工智能方向硕士，毕业于江西师范大学。长期深耕AI技术研发与产业落地，现就职于南瑞信通，担任大模型实施工程师，致力于为企业提供高效、创新的AIGC解决方 案。拥有多年一线研发与项目管理经验，主导了多个企业级AI项目的成功部署，因其在技术创新与应用实践中的卓越表现，荣获“2024年川渝地区效率先锋”称号，并获得工信部AIGC导师级专家认证。

职称证明材料：

*![](data:image/jpeg;base64...)![](data:image/jpeg;base64...)*

身份证正反面照片：

![](data:image/jpeg;base64...)![](data:image/jpeg;base64...)

银行卡照片：

![](data:image/jpeg;base64...)

姓名：黄毅豪 身份证号：362525199901180010

电话：13117855518 单位：南京南瑞信息通信科技有限公司

账号：6214830379712663

开户银行：招商银行南昌
2025-09-04 10:52:47,674 - app.utils.document_parser - INFO - Temporary file deleted: /tmp/tmpnxorbunt_教师酬金信息 -黄毅豪.docx
2025-09-04 10:52:47,676 - app.routers.compare - INFO - 文件上传成功: 教师酬金信息 -黄毅豪.docx, ID: ea4f93b3-19c3-4c6a-a82e-36682dd3afef
INFO:     172.19.0.2:36464 - "POST /api/compare/upload HTTP/1.0" 200 OK
2025-09-04 10:52:47,682 - app.routers.compare - INFO - 开始比较已上传文件: 教师酬金信息 -黄毅豪.docx vs 教师酬金信息 -黄毅豪.docx
2025-09-04 10:52:47,682 - app.utils.document_compare - INFO - 开始比较文档: 教师酬金信息 -黄毅豪.docx vs 教师酬金信息 -黄毅豪.docx
2025-09-04 10:52:47,693 - app.utils.document_compare - INFO - 找到 3 个连续匹配块
2025-09-04 10:52:47,693 - app.utils.document_compare - INFO - 文档比对完成，整体相似度: 1.160
2025-09-04 10:52:47,693 - app.routers.compare - INFO - 为文件B生成高亮PDF: 教师酬金信息 -黄毅豪.docx
2025-09-04 10:52:47,720 - app.utils.file_converter - ERROR - DOCX转PDF失败: PDF.__init__() takes 1 positional argument but 3 were given
2025-09-04 10:52:47,720 - app.utils.file_converter - ERROR - DOCX转PDF失败: PDF.__init__() takes 1 positional argument but 3 were given
2025-09-04 10:52:47,720 - app.routers.compare - ERROR - 创建高亮PDF失败: PDF.__init__() takes 1 positional argument but 3 were given
2025-09-04 10:52:47,720 - app.routers.compare - WARNING - 生成高亮PDF失败: PDF.__init__() takes 1 positional argument but 3 were given
2025-09-04 10:52:47,720 - app.routers.compare - INFO - 最终metadata内容: {'algorithm_params': {'similarity_threshold_high': 0.9, 'similarity_threshold_medium': 0.7, 'min_block_length': 3}, 'display_mode': 'html', 'comparison_time': datetime.datetime(2025, 9, 4, 10, 52, 47, 720822)}
2025-09-04 10:52:47,720 - app.routers.compare - INFO - 文件比较完成，整体相似度: 1.160
2025-09-04 10:52:47,721 - app.routers.compare - ERROR - 文件比较失败: 1 validation error for CompareResponse
comparison -> overall_similarity
  ensure this value is less than or equal to 1 (type=value_error.number.not_le; limit_value=1)
INFO:     172.19.0.2:36466 - "POST /api/compare/files HTTP/1.0" 500 Internal Server Error
## Todo
(1)可以检索下网络有没有其他方法转成PDF
(2)如果没有，就直接用文本块显示（PDF以外的文件就用文本块显示，但是最好还是用一个markdown，就是Markitdown提取出来的效果，同时Markdown要正确的显示,只是标注颜色的地方要标注上）