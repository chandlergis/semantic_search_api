#!/bin/bash
# 这个脚本用于清理旧的临时文件

# 设置临时文件目录的路径
TEMP_DIR="$(dirname "$0")/temp_files"

# 查找并删除超过1天（1440分钟）的旧文件
# 使用 -mmin +1440 来查找超过1440分钟（24小时）未修改的文件
find "$TEMP_DIR" -type f -mmin +1440 -name "*_*_highlighted.pdf" -delete

# 打印一条日志，说明清理完成
echo "Temp files cleanup complete. Files older than 24 hours in $TEMP_DIR have been deleted."
