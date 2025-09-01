#!/usr/bin/env python3

import requests
import json

# 测试API端点
def test_highlighted_download():
    # 首先获取已上传的文件列表
    try:
        response = requests.get("http://localhost:9000/api/compare/files")
        if response.status_code == 200:
            files = response.json()
            print("已上传的文件:")
            for file_id, file_info in files.items():
                print(f"  {file_id}: {file_info['filename']}")
                
                # 查找高亮版本
                if file_info['filename'].startswith('highlighted_'):
                    print(f"  -> 高亮版本: {file_id}")
                    
                    # 尝试下载高亮文件
                    download_url = f"http://localhost:9000/api/compare/download/{file_id}"
                    download_response = requests.get(download_url)
                    
                    if download_response.status_code == 200:
                        with open(f"/tmp/{file_info['filename']}", "wb") as f:
                            f.write(download_response.content)
                        print(f"  -> 已下载到: /tmp/{file_info['filename']}")
                    else:
                        print(f"  -> 下载失败: {download_response.status_code}")
        else:
            print(f"获取文件列表失败: {response.status_code}")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_highlighted_download()