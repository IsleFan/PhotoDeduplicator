# PhotoDeduplicator

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A powerful Python tool that intelligently identifies duplicate photos across multiple directories, even with different resolutions. Automatically preserves high-resolution photos while safely cleaning up duplicates.

## ✨ Key Features

- 🔍 **Smart Content Comparison**: Uses perceptual hashing to identify identical content at different resolutions
- 🎯 **Multi-Hash Algorithms**: Combines pHash, dHash, and wHash algorithms for improved accuracy
- 📁 **Multi-Directory Support**: Scan multiple folders simultaneously and detect cross-directory duplicates
- 🔄 **Deep Scanning**: Recursively scan all subdirectories or choose directory-only scanning
- 📐 **Intelligent Retention Strategy**: Automatically keeps highest resolution photos, removes lower quality duplicates
- 🛡️ **Safety Mechanisms**: Complete preview before execution, user confirmation required
- 📝 **Detailed Logging**: Automatic deletion log generation for operation tracking
- 🎨 **Multi-Format Support**: Supports JPG, PNG, GIF, BMP, TIFF, WebP and other mainstream formats

## 🚀 Quick Start

### Install Dependencies

```bash
pip install Pillow imagehash
```

### Basic Usage

#### Method 1: Interactive Mode (Recommended for beginners)

```bash
python photo_deduplicator.py
```

The program will guide you through entering folder paths and configuration parameters, supporting multiple folders at once.

#### Method 2: Command Line Mode (Recommended for advanced users)

```bash
# Scan single folder
python photo_deduplicator.py /path/to/your/photos

# Scan multiple folders
python photo_deduplicator.py ~/Pictures ~/Downloads/Photos ~/Desktop/Images

# No recursive subdirectory scanning
python photo_deduplicator.py ~/Pictures --no-recursive

# Custom parameters
python photo_deduplicator.py ~/Pictures ~/Downloads --hash-size 8 --threshold 5
```

## 📋 Usage Examples

### Clean duplicate photos in Downloads folder

```bash
python photo_deduplicator.py ~/Downloads/Photos
```

### High precision mode cleaning (stricter comparison)

```bash
python photo_deduplicator.py ~/Pictures --hash-size 16 --threshold 3
```

### Fast mode cleaning (more lenient comparison)

```bash
python photo_deduplicator.py ~/Pictures --hash-size 4 --threshold 8
```

### Scan multiple photo libraries

```bash
python photo_deduplicator.py ~/Pictures ~/Photos ~/Desktop/Images ~/Downloads
```

## ⚙️ Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `folders` | Required | Folder paths to scan (supports multiple) |
| `--hash-size` | 8 | Hash size, larger values are more precise but slower (recommended range: 4-16) |
| `--threshold` | 5 | Similarity threshold, smaller values are stricter (recommended range: 3-10) |
| `--no-recursive` | False | Don't scan subdirectories recursively |

### Parameter Tuning Recommendations

- **Speed Priority**: `--hash-size 4 --threshold 8`
- **Balanced Mode**: `--hash-size 8 --threshold 5` (default)
- **Precision Priority**: `--hash-size 16 --threshold 3`

## 🔧 How It Works

1. **Scanning Phase**: Recursively scan specified folders to find all supported image formats
2. **Analysis Phase**: Calculate multiple perceptual hash values for each photo
3. **Comparison Phase**: Use hash values to compare and find groups of similar content
4. **Filtering Phase**: Select highest resolution photo to keep in each duplicate group
5. **Preview Phase**: Display detailed deletion list for user confirmation
6. **Execution Phase**: Safely delete duplicate photos and generate operation log

## 📊 Output Example

```
🖼️  Smart Photo Duplicate Detection & Cleanup Tool (Multi-Directory)
======================================================================
Starting scan of 3 folders:
  - /Users/username/Pictures
  - /Users/username/Downloads/Photos
  - /Users/username/Desktop/Images

📁 Scanning folder: /Users/username/Pictures
   (including all subdirectories)
   Found 1250 photos
   ✅ Successfully processed 1250 photos

📊 Scan Summary:
   Total found: 2847 photos
   Successfully processed: 2847 photos

📈 Folder Statistics:
📁 Pictures:
   Path: /Users/username/Pictures
   Photo count: 1250 photos
   Total size: 2847.32 MB

🔍 Starting duplicate photo comparison...
   Comparison progress: 50.0% (125000/250000)
✅ Found 23 duplicate photo groups

📊 Duplicate Type Analysis:
   Cross-directory duplicates: 8 groups
   Same-directory duplicates: 15 groups

====================================================================================================
Duplicate Photo Cleanup Preview
====================================================================================================

Group 1 (3 duplicate photos total):
--------------------------------------------------------------------------------
🔄 Cross-directory duplicate (involves 2 folders)
✅ Keep: IMG_001_4K.jpg
   📁 Folder: Pictures
   📐 Resolution: 3840x2160 (8,294,400 pixels)
   💾 File size: 2,547,832 bytes
❌ Delete: IMG_001_HD.jpg
   📁 Folder: Downloads
   📐 Resolution: 1920x1080 (2,073,600 pixels)
   💾 File size: 1,245,678 bytes
❌ Delete: IMG_001_thumb.jpg
   📁 Folder: Desktop
   📐 Resolution: 640x360 (230,400 pixels)
   💾 File size: 125,431 bytes

📊 Summary:
   Will delete: 45 duplicate photos
   Will keep: 23 high-resolution photos
   Cross-directory duplicate groups: 8
   Estimated space savings: 127,234,567 bytes (121.34 MB)

📁 Deletion Statistics by Folder:
------------------------------------------------------------
📁 Downloads: 28 photos, 67.45 MB
📁 Desktop: 12 photos, 23.21 MB
📁 Pictures: 5 photos, 30.68 MB

❓ Confirm deletion operation? (Enter 'yes' to confirm, any other input cancels)
```

## 📁 Supported File Formats

- `.jpg` / `.jpeg`
- `.png`
- `.gif`
- `.bmp`
- `.tiff`
- `.webp`

## 🛡️ Safety Features

### Multiple Protection Mechanisms

1. **Preview Confirmation**: Display complete deletion list before execution
2. **Explicit Confirmation**: Must enter 'yes' to execute deletion
3. **Operation Logging**: Automatically generate `deletion_log.json` log file
4. **Error Handling**: Properly handle file read and deletion errors

### Log File Example

```json
{
  "timestamp": "2024-06-02T14:30:25.123456",
  "scan_folders": [
    "/Users/username/Pictures",
    "/Users/username/Downloads/Photos"
  ],
  "recursive_scan": true,
  "settings": {
    "hash_size": 8,
    "similarity_threshold": 5
  },
  "deletion_by_folder": {
    "/Users/username/Pictures": [
      {
        "path": "/Users/username/Pictures/IMG_001_HD.jpg",
        "relative_path": "IMG_001_HD.jpg",
        "resolution": "1920x1080",
        "file_size": 1245678
      }
    ]
  },
  "summary": {
    "total_deleted": 45,
    "total_space_saved": 127234567,
    "folders_affected": 3
  }
}
```

## 🔍 Advanced Usage Tips

### Batch Processing Multiple Folder Sets

```bash
# Create batch processing script
for folder_set in "~/Pictures ~/Downloads" "~/Photos/2023 ~/Photos/2024"; do
    python photo_deduplicator.py $folder_set
done
```

### Integration with Other Tools

```bash
# Backup before cleanup
rsync -av ~/Pictures/ ~/Pictures_backup/
python photo_deduplicator.py ~/Pictures

# Check available space before processing
df -h ~/Pictures
python photo_deduplicator.py ~/Pictures
```

### Advanced Configuration

```bash
# High precision mode for professional photos
python photo_deduplicator.py ~/Professional_Photos --hash-size 16 --threshold 2

# Fast cleanup for large archives
python photo_deduplicator.py ~/Archive --hash-size 4 --threshold 8 --no-recursive
```

## ⚠️ Important Notes

1. **Backup Important**: Recommend backing up important photos before execution
2. **Permission Check**: Ensure program has sufficient permissions to read/write target folders
3. **Space Check**: Large folders may require longer processing time
4. **Memory Usage**: Processing large numbers of photos will consume more memory

## 🐛 Troubleshooting

### Q: Program processing is very slow?
A: You can adjust `--hash-size` to a smaller value (like 4), or increase `--threshold` value to speed up processing.

### Q: Worried about accidentally deleting important photos?
A: The program displays a complete preview before execution, and only executes deletion with explicit 'yes' input. Recommend backing up important data first.

### Q: Why aren't some obviously duplicate photos being detected?
A: The similarity threshold might be set too strictly. Try increasing the `--threshold` parameter value.

### Q: Can deleted photos be recovered?
A: The program generates a `deletion_log.json` log file but cannot directly recover photos. Recommend using system recycle bin or professional recovery tools.

### Q: How to handle very large photo collections?
A: For collections with 10,000+ photos, consider:
- Using `--hash-size 4` for faster processing
- Processing folders in batches
- Running during off-peak hours
- Ensuring sufficient RAM (8GB+ recommended)

## 🤝 Contributing

Welcome to submit Issues and Pull Requests to help improve this tool!

### Development Environment Setup

```bash
git clone <repository-url>
cd PhotoDeduplicator
pip install -r requirements.txt
```

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

- Follow PEP 8 coding standards
- Use meaningful variable and function names
- Add appropriate comments and docstrings
- Ensure cross-platform compatibility

## 📈 Performance Benchmarks

| Photo Count | Processing Time | Memory Usage | Recommended Settings |
|-------------|----------------|--------------|---------------------|
| < 1,000     | < 30 seconds   | < 500MB      | Default settings    |
| 1,000-5,000 | 1-5 minutes    | 500MB-2GB    | --hash-size 8       |
| 5,000-10,000| 5-15 minutes   | 2GB-4GB      | --hash-size 6       |
| > 10,000    | 15+ minutes    | 4GB+         | --hash-size 4       |

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Pillow](https://pillow.readthedocs.io/) - Python Imaging Library
- [ImageHash](https://github.com/JohannesBuchner/imagehash) - Perceptual image hashing
- Community contributors and testers

## 👨‍💻 Author

Created by a project management and system development expert, focused on providing practical and safe file management tools.

---

**⭐ If this tool helps you, please give it a star for support!**

## 📞 Support

- 🐛 **Bug Reports**: [Create an Issue](../../issues)
- 💡 **Feature Requests**: [Create an Issue](../../issues)
- 📖 **Documentation**: Check the [Wiki](../../wiki)
- 💬 **Discussions**: [Join Discussions](../../discussions)
