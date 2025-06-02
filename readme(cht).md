# 智能照片重複檢測與清理工具

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一個強大的Python工具，能夠智能識別多個資料夾中的重複照片，即使在不同解析度下也能準確比對。支援跨目錄比對，自動保留高解析度照片，安全清理重複項目。

## ✨ 主要特色

- 🔍 **智能內容比對**: 使用感知雜湊技術，能識別相同內容但不同解析度的照片
- 🎯 **多重檢測算法**: 結合pHash、dHash、wHash三種算法，提高檢測準確性
- 📁 **多目錄支援**: 支援同時掃描多個資料夾，並能識別跨資料夾的重複照片
- 🔄 **深度掃描**: 遞迴掃描所有子目錄，或選擇僅掃描指定目錄
- 📐 **智能保留策略**: 自動保留解析度最高的照片，刪除低解析度重複項
- 🛡️ **安全機制**: 執行前完整預覽，需用戶確認才執行刪除
- 📝 **詳細記錄**: 自動生成刪除記錄，可追蹤操作歷史
- 🎨 **多格式支援**: 支援JPG、PNG、GIF、BMP、TIFF、WebP等主流格式

## 🚀 快速開始

### 安裝依賴

```bash
pip install Pillow imagehash
```

### 基本使用

#### 方式一：互動模式（推薦新手）

```bash
python photo_cleaner.py
```

程式會引導您輸入資料夾路徑和設定參數，支援一次輸入多個資料夾。

#### 方式二：命令列模式（推薦進階用戶）

```bash
# 掃描單一資料夾
python photo_cleaner.py /path/to/your/photos

# 掃描多個資料夾
python photo_cleaner.py ~/Pictures ~/Downloads/Photos ~/Desktop/Images

# 不遞迴掃描子目錄
python photo_cleaner.py ~/Pictures --no-recursive

# 自訂參數
python photo_cleaner.py ~/Pictures ~/Downloads --hash-size 8 --threshold 5
```

## 📋 使用範例

### 清理下載資料夾的重複照片

```bash
python photo_cleaner.py ~/Downloads/Photos
```

### 高精度模式清理（更嚴格的比對）

```bash
python photo_cleaner.py ~/Pictures --hash-size 16 --threshold 3
```

### 快速模式清理（較寬鬆的比對）

```bash
python photo_cleaner.py ~/Pictures --hash-size 4 --threshold 8
```

## ⚙️ 參數說明

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `folder` | 必須 | 要掃描的資料夾路徑 |
| `--hash-size` | 8 | 雜湊大小，數值越大越精確但速度較慢（建議範圍：4-16） |
| `--threshold` | 5 | 相似度閾值，數值越小比對越嚴格（建議範圍：3-10） |

### 參數調整建議

- **追求速度**: `--hash-size 4 --threshold 8`
- **平衡模式**: `--hash-size 8 --threshold 5`（預設）
- **追求精度**: `--hash-size 16 --threshold 3`

## 🔧 工作原理

1. **掃描階段**: 遞迴掃描指定資料夾，找出所有支援的圖片格式
2. **分析階段**: 為每張照片計算多種感知雜湊值
3. **比對階段**: 使用雜湊值比對找出內容相似的照片群組
4. **篩選階段**: 在每個重複群組中選擇解析度最高的照片保留
5. **預覽階段**: 顯示詳細的刪除清單供用戶確認
6. **執行階段**: 安全刪除重複照片並生成操作記錄

## 📊 輸出範例

```
智能照片重複檢測與清理工具
==================================================
開始掃描資料夾: /Users/username/Pictures
找到 1250 張照片
已處理 10 張照片...
已處理 20 張照片...
...
成功處理 1250 張照片
開始比對重複照片...
找到 15 個重複照片群組

================================================================================
重複照片清理預覽
================================================================================

群組 1 (共 3 張重複照片):
------------------------------------------------------------
✓ 保留: IMG_001_4K.jpg
   解析度: 3840x2160 (8,294,400 像素)
   檔案大小: 2,547,832 bytes
✗ 刪除: IMG_001_HD.jpg
   解析度: 1920x1080 (2,073,600 像素)
   檔案大小: 1,245,678 bytes
✗ 刪除: IMG_001_thumb.jpg
   解析度: 640x360 (230,400 像素)
   檔案大小: 125,431 bytes

總計:
- 將刪除 28 張重複照片
- 將保留 15 張高解析度照片
- 預計節省空間: 45,234,567 bytes (43.15 MB)

是否確定執行刪除操作? (輸入 'yes' 確認, 其他任何輸入取消)
```

## 📁 支援的檔案格式

- `.jpg` / `.jpeg`
- `.png`
- `.gif`
- `.bmp`
- `.tiff`
- `.webp`

## 🛡️ 安全特性

### 多重保護機制

1. **預覽確認**: 執行前顯示完整刪除清單
2. **明確確認**: 必須輸入 'yes' 才執行刪除
3. **操作記錄**: 自動生成 `deletion_log.json` 記錄檔案
4. **錯誤處理**: 妥善處理檔案讀取和刪除錯誤

### 記錄檔案範例

```json
{
  "timestamp": "2024-06-02T14:30:25.123456",
  "deleted_files": [
    {
      "path": "/Users/username/Pictures/IMG_001_HD.jpg",
      "resolution": "1920x1080",
      "file_size": 1245678
    }
  ],
  "total_deleted": 28,
  "total_space_saved": 45234567
}
```

## 🔍 進階使用技巧

### 批次處理多個資料夾

```bash
# 建立批次處理腳本
for folder in ~/Pictures/2023 ~/Pictures/2024 ~/Downloads; do
    python photo_cleaner.py "$folder"
done
```

### 結合其他工具

```bash
# 先備份再清理
rsync -av ~/Pictures/ ~/Pictures_backup/
python photo_cleaner.py ~/Pictures
```

## ⚠️ 注意事項

1. **備份重要**: 建議執行前先備份重要照片
2. **權限確認**: 確保程式有足夠權限讀寫目標資料夾
3. **空間檢查**: 大型資料夾可能需要較長處理時間
4. **記憶體使用**: 處理大量照片時會消耗較多記憶體

## 🐛 常見問題

### Q: 程式處理速度很慢怎麼辦？
A: 可以調整 `--hash-size` 為較小值（如4），或增加 `--threshold` 值以加快處理速度。

### Q: 擔心誤刪重要照片？
A: 程式會在執行前顯示完整預覽，並且只有明確輸入 'yes' 才會執行刪除。建議先備份重要資料。

### Q: 為什麼某些明顯重複的照片沒有被識別？
A: 可能是相似度閾值設定過於嚴格，嘗試增加 `--threshold` 參數值。

### Q: 可以恢復已刪除的照片嗎？
A: 程式會生成 `deletion_log.json` 記錄檔案，但無法直接恢復。建議使用系統資源回收筒或專業恢復工具。

## 🤝 貢獻指南

歡迎提交Issue和Pull Request來幫助改進這個工具！

### 開發環境設置

```bash
git clone <repository-url>
cd photo-duplicate-cleaner
pip install -r requirements.txt
```

### 執行測試

```bash
python -m pytest tests/
```

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 👨‍💻 作者

由專案管理與系統開發專家打造，專注於提供實用且安全的檔案管理工具。

---

**⭐ 如果這個工具對您有幫助，請給個星星支持！**
