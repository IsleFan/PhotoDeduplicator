import os
import hashlib
from PIL import Image
import imagehash
from collections import defaultdict
import argparse
from pathlib import Path
import json
from datetime import datetime
import sys

class PhotoDuplicateCleaner:
    """智能照片重複檢測與清理工具 - 支援多目錄比對"""

    def __init__(self, folder_paths, hash_size=8, similarity_threshold=5, recursive=True):
        """
        初始化照片清理工具

        Args:
            folder_paths (list): 要掃描的資料夾路徑列表
            hash_size (int): 雜湊大小，越大越精確但速度較慢
            similarity_threshold (int): 相似度閾值，數值越小越嚴格
            recursive (bool): 是否遞迴掃描子目錄
        """
        self.folder_paths = [Path(path) for path in folder_paths]
        self.hash_size = hash_size
        self.similarity_threshold = similarity_threshold
        self.recursive = recursive
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        self.photo_hashes = {}
        self.duplicate_groups = []
        self.folder_stats = {}

    def get_image_info(self, image_path):
        """獲取圖片基本資訊"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                file_size = os.path.getsize(image_path)
                resolution = width * height

                # 確定照片所屬的原始掃描目錄
                source_folder = self.get_source_folder(image_path)

                return {
                    'path': image_path,
                    'width': width,
                    'height': height,
                    'resolution': resolution,
                    'file_size': file_size,
                    'format': img.format,
                    'source_folder': source_folder,
                    'relative_path': image_path.relative_to(source_folder) if source_folder else image_path
                }
        except Exception as e:
            print(f"無法處理圖片 {image_path}: {e}")
            return None

    def get_source_folder(self, image_path):
        """確定圖片所屬的原始掃描目錄"""
        for folder in self.folder_paths:
            try:
                image_path.relative_to(folder)
                return folder
            except ValueError:
                continue
        return None

    def calculate_perceptual_hash(self, image_path):
        """計算感知雜湊值"""
        try:
            with Image.open(image_path) as img:
                # 使用多種雜湊算法提高準確性
                phash = imagehash.phash(img, hash_size=self.hash_size)
                dhash = imagehash.dhash(img, hash_size=self.hash_size)
                whash = imagehash.whash(img, hash_size=self.hash_size)

                return {
                    'phash': phash,
                    'dhash': dhash,
                    'whash': whash
                }
        except Exception as e:
            print(f"無法計算雜湊值 {image_path}: {e}")
            return None

    def scan_photos(self):
        """掃描所有指定資料夾中的照片"""
        print(f"開始掃描 {len(self.folder_paths)} 個資料夾:")
        for folder in self.folder_paths:
            print(f"  - {folder}")

        total_files = 0
        processed_count = 0

        # 初始化各資料夾統計
        for folder in self.folder_paths:
            self.folder_stats[str(folder)] = {
                'total_photos': 0,
                'processed_photos': 0,
                'total_size': 0,
                'exists': folder.exists()
            }

        # 掃描每個資料夾
        for folder_path in self.folder_paths:
            if not folder_path.exists():
                print(f"⚠️  資料夾不存在: {folder_path}")
                continue

            print(f"\n📁 掃描資料夾: {folder_path}")

            # 根據是否遞迴選擇掃描方式
            if self.recursive:
                print(f"   (包含所有子目錄)")
                photo_files = []
                for ext in self.supported_formats:
                    photo_files.extend(folder_path.rglob(f"*{ext}"))
                    photo_files.extend(folder_path.rglob(f"*{ext.upper()}"))
            else:
                print(f"   (僅掃描當前目錄)")
                photo_files = []
                for ext in self.supported_formats:
                    photo_files.extend(folder_path.glob(f"*{ext}"))
                    photo_files.extend(folder_path.glob(f"*{ext.upper()}"))

            folder_file_count = len(photo_files)
            total_files += folder_file_count
            self.folder_stats[str(folder_path)]['total_photos'] = folder_file_count

            print(f"   找到 {folder_file_count} 張照片")

            # 處理該資料夾中的照片
            folder_processed = 0
            for photo_path in photo_files:
                info = self.get_image_info(photo_path)
                if info:
                    hashes = self.calculate_perceptual_hash(photo_path)
                    if hashes:
                        info['hashes'] = hashes
                        self.photo_hashes[str(photo_path)] = info
                        processed_count += 1
                        folder_processed += 1
                        self.folder_stats[str(folder_path)]['total_size'] += info['file_size']

                if processed_count % 50 == 0:
                    print(f"   已處理 {processed_count} 張照片...")

            self.folder_stats[str(folder_path)]['processed_photos'] = folder_processed
            print(f"   ✅ 成功處理 {folder_processed} 張照片")

        print(f"\n📊 掃描總結:")
        print(f"   總共找到: {total_files} 張照片")
        print(f"   成功處理: {processed_count} 張照片")
        self.display_folder_stats()

    def display_folder_stats(self):
        """顯示各資料夾統計資訊"""
        print(f"\n📈 各資料夾統計:")
        print("-" * 80)

        for folder_path, stats in self.folder_stats.items():
            if not stats['exists']:
                print(f"❌ {folder_path}: 資料夾不存在")
                continue

            size_mb = stats['total_size'] / 1024 / 1024
            print(f"📁 {Path(folder_path).name}:")
            print(f"   路徑: {folder_path}")
            print(f"   照片數量: {stats['processed_photos']} 張")
            print(f"   總大小: {size_mb:.2f} MB")
            print()

    def find_duplicates(self):
        """找出重複的照片群組"""
        print("🔍 開始比對重複照片...")

        photo_list = list(self.photo_hashes.values())
        grouped_photos = defaultdict(list)
        processed_pairs = set()

        total_comparisons = len(photo_list) * (len(photo_list) - 1) // 2
        current_comparison = 0

        for i, photo1 in enumerate(photo_list):
            for j, photo2 in enumerate(photo_list[i+1:], i+1):
                current_comparison += 1

                # 顯示進度
                if current_comparison % 1000 == 0:
                    progress = (current_comparison / total_comparisons) * 100
                    print(f"   比對進度: {progress:.1f}% ({current_comparison}/{total_comparisons})")

                pair_key = tuple(sorted([str(photo1['path']), str(photo2['path'])]))
                if pair_key in processed_pairs:
                    continue
                processed_pairs.add(pair_key)

                if self.are_similar(photo1['hashes'], photo2['hashes']):
                    # 使用較小的雜湊值作為群組鍵
                    group_key = min(str(photo1['hashes']['phash']), str(photo2['hashes']['phash']))
                    grouped_photos[group_key].extend([photo1, photo2])

        # 去除重複項目並整理群組
        final_groups = []
        for group in grouped_photos.values():
            # 去除重複的照片項目
            unique_photos = {}
            for photo in group:
                path_key = str(photo['path'])
                if path_key not in unique_photos:
                    unique_photos[path_key] = photo

            if len(unique_photos) > 1:
                final_groups.append(list(unique_photos.values()))

        self.duplicate_groups = final_groups
        print(f"✅ 找到 {len(final_groups)} 個重複照片群組")

        # 統計跨資料夾重複
        self.analyze_cross_folder_duplicates()

    def analyze_cross_folder_duplicates(self):
        """分析跨資料夾重複情況"""
        cross_folder_groups = 0
        same_folder_groups = 0

        for group in self.duplicate_groups:
            source_folders = set(str(photo['source_folder']) for photo in group)
            if len(source_folders) > 1:
                cross_folder_groups += 1
            else:
                same_folder_groups += 1

        print(f"\n📊 重複類型分析:")
        print(f"   跨資料夾重複: {cross_folder_groups} 個群組")
        print(f"   同資料夾重複: {same_folder_groups} 個群組")

    def are_similar(self, hashes1, hashes2):
        """判斷兩張照片是否相似"""
        # 使用多種雜湊算法進行比較，提高準確性
        phash_diff = hashes1['phash'] - hashes2['phash']
        dhash_diff = hashes1['dhash'] - hashes2['dhash']
        whash_diff = hashes1['whash'] - hashes2['whash']

        # 如果任一種雜湊算法認為相似，則判定為相似
        return (phash_diff <= self.similarity_threshold or
                dhash_diff <= self.similarity_threshold or
                whash_diff <= self.similarity_threshold)

    def generate_deletion_list(self):
        """生成待刪除清單，支援多種保留策略"""
        deletion_list = []
        keep_list = []

        for group in self.duplicate_groups:
            # 按解析度排序，解析度相同時按檔案大小排序
            sorted_group = sorted(group, key=lambda x: (x['resolution'], x['file_size']), reverse=True)

            # 保留解析度最高的照片
            keep_photo = sorted_group[0]
            keep_list.append(keep_photo)

            # 其餘加入刪除清單
            for photo in sorted_group[1:]:
                deletion_list.append(photo)

        return deletion_list, keep_list

    def display_deletion_preview(self, deletion_list, keep_list):
        """顯示刪除預覽，包含跨資料夾資訊"""
        print("\n" + "="*100)
        print("重複照片清理預覽")
        print("="*100)

        total_space_saved = 0
        cross_folder_deletions = 0

        for i, group in enumerate(self.duplicate_groups, 1):
            print(f"\n群組 {i} (共 {len(group)} 張重複照片):")
            print("-" * 80)

            # 檢查是否為跨資料夾重複
            source_folders = set(str(photo['source_folder']) for photo in group)
            if len(source_folders) > 1:
                print(f"🔄 跨資料夾重複 (涉及 {len(source_folders)} 個資料夾)")
                cross_folder_deletions += 1
            else:
                print(f"📁 同資料夾重複")

            # 找出這個群組中要保留和刪除的照片
            group_paths = {str(photo['path']) for photo in group}
            group_keep = [p for p in keep_list if str(p['path']) in group_paths]
            group_delete = [p for p in deletion_list if str(p['path']) in group_paths]

            # 顯示保留的照片
            if group_keep:
                keep_photo = group_keep[0]
                folder_name = Path(keep_photo['source_folder']).name if keep_photo['source_folder'] else "未知"
                print(f"✅ 保留: {keep_photo['relative_path']}")
                print(f"   📁 資料夾: {folder_name}")
                print(f"   📐 解析度: {keep_photo['width']}x{keep_photo['height']} ({keep_photo['resolution']:,} 像素)")
                print(f"   💾 檔案大小: {keep_photo['file_size']:,} bytes")

            # 顯示要刪除的照片
            for photo in group_delete:
                folder_name = Path(photo['source_folder']).name if photo['source_folder'] else "未知"
                print(f"❌ 刪除: {photo['relative_path']}")
                print(f"   📁 資料夾: {folder_name}")
                print(f"   📐 解析度: {photo['width']}x{photo['height']} ({photo['resolution']:,} 像素)")
                print(f"   💾 檔案大小: {photo['file_size']:,} bytes")
                total_space_saved += photo['file_size']

        print(f"\n📊 總計:")
        print(f"   將刪除: {len(deletion_list)} 張重複照片")
        print(f"   將保留: {len(keep_list)} 張高解析度照片")
        print(f"   跨資料夾重複群組: {cross_folder_deletions} 個")
        print(f"   預計節省空間: {total_space_saved:,} bytes ({total_space_saved/1024/1024:.2f} MB)")

        # 按資料夾顯示刪除統計
        self.display_deletion_by_folder(deletion_list)

    def display_deletion_by_folder(self, deletion_list):
        """按資料夾顯示刪除統計"""
        folder_deletions = defaultdict(list)

        for photo in deletion_list:
            folder_key = str(photo['source_folder']) if photo['source_folder'] else "未知"
            folder_deletions[folder_key].append(photo)

        print(f"\n📁 各資料夾刪除統計:")
        print("-" * 60)

        for folder_path, photos in folder_deletions.items():
            folder_name = Path(folder_path).name if folder_path != "未知" else "未知"
            total_size = sum(photo['file_size'] for photo in photos)
            print(f"📁 {folder_name}: {len(photos)} 張照片, {total_size/1024/1024:.2f} MB")

    def save_deletion_log(self, deletion_list, log_file="deletion_log.json"):
        """儲存刪除記錄"""
        # 按資料夾分組記錄
        folder_groups = defaultdict(list)
        for photo in deletion_list:
            folder_key = str(photo['source_folder']) if photo['source_folder'] else "unknown"
            folder_groups[folder_key].append({
                'path': str(photo['path']),
                'relative_path': str(photo['relative_path']),
                'resolution': f"{photo['width']}x{photo['height']}",
                'file_size': photo['file_size']
            })

        log_data = {
            'timestamp': datetime.now().isoformat(),
            'scan_folders': [str(folder) for folder in self.folder_paths],
            'recursive_scan': self.recursive,
            'settings': {
                'hash_size': self.hash_size,
                'similarity_threshold': self.similarity_threshold
            },
            'deletion_by_folder': dict(folder_groups),
            'summary': {
                'total_deleted': len(deletion_list),
                'total_space_saved': sum(photo['file_size'] for photo in deletion_list),
                'folders_affected': len(folder_groups)
            }
        }

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        print(f"📝 刪除記錄已儲存至: {log_file}")

    def delete_photos(self, deletion_list):
        """執行照片刪除"""
        print(f"\n🗑️  開始刪除 {len(deletion_list)} 張照片...")

        deleted_count = 0
        failed_deletions = []
        deleted_by_folder = defaultdict(int)

        for photo in deletion_list:
            try:
                os.remove(photo['path'])
                deleted_count += 1
                folder_key = str(photo['source_folder']) if photo['source_folder'] else "unknown"
                deleted_by_folder[folder_key] += 1
                print(f"✅ 已刪除: {photo['relative_path']}")
            except Exception as e:
                failed_deletions.append((photo['path'], str(e)))
                print(f"❌ 刪除失敗: {photo['relative_path']} - {e}")

        print(f"\n📊 刪除完成:")
        print(f"   成功刪除: {deleted_count} 張照片")

        # 顯示各資料夾刪除結果
        for folder_path, count in deleted_by_folder.items():
            folder_name = Path(folder_path).name if folder_path != "unknown" else "未知"
            print(f"   📁 {folder_name}: {count} 張")

        if failed_deletions:
            print(f"   刪除失敗: {len(failed_deletions)} 張照片")
            for path, error in failed_deletions:
                print(f"     {path}: {error}")

    def run(self):
        """執行完整的清理流程"""
        print("🖼️  智能照片重複檢測與清理工具 (多目錄版)")
        print("="*70)

        # 檢查資料夾存在性
        valid_folders = [folder for folder in self.folder_paths if folder.exists()]
        if not valid_folders:
            print("❌ 錯誤: 所有指定的資料夾都不存在")
            return

        if len(valid_folders) < len(self.folder_paths):
            missing_folders = [folder for folder in self.folder_paths if not folder.exists()]
            print(f"⚠️  警告: 以下資料夾不存在，將被跳過:")
            for folder in missing_folders:
                print(f"   - {folder}")

        # 步驟1: 掃描照片
        self.scan_photos()

        if not self.photo_hashes:
            print("❌ 未找到任何可處理的照片")
            return

        # 步驟2: 找出重複項目
        self.find_duplicates()

        if not self.duplicate_groups:
            print("✅ 未發現重複照片")
            return

        # 步驟3: 生成刪除清單
        deletion_list, keep_list = self.generate_deletion_list()

        # 步驟4: 顯示預覽
        self.display_deletion_preview(deletion_list, keep_list)

        # 步驟5: 確認執行
        print(f"\n❓ 是否確定執行刪除操作? (輸入 'yes' 確認, 其他任何輸入取消)")
        confirmation = input("請輸入: ").strip().lower()

        if confirmation == 'yes':
            # 儲存刪除記錄
            self.save_deletion_log(deletion_list)

            # 執行刪除
            self.delete_photos(deletion_list)
            print("\n🎉 清理完成!")
        else:
            print("❌ 操作已取消")


def main():
    parser = argparse.ArgumentParser(
        description='智能照片重複檢測與清理工具 (多目錄版)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  # 掃描單一資料夾
  python photo_cleaner.py ~/Pictures

  # 掃描多個資料夾
  python photo_cleaner.py ~/Pictures ~/Downloads/Photos ~/Desktop/Images

  # 不遞迴掃描子目錄
  python photo_cleaner.py ~/Pictures --no-recursive

  # 自訂參數
  python photo_cleaner.py ~/Pictures ~/Downloads --hash-size 16 --threshold 3
        """
    )

    parser.add_argument('folders', nargs='+', help='要掃描的資料夾路徑 (支援多個)')
    parser.add_argument('--hash-size', type=int, default=8,
                       help='雜湊大小 (預設: 8, 建議範圍: 4-16)')
    parser.add_argument('--threshold', type=int, default=5,
                       help='相似度閾值 (預設: 5, 建議範圍: 3-10)')
    parser.add_argument('--no-recursive', action='store_true',
                       help='不遞迴掃描子目錄 (預設會掃描所有子目錄)')

    args = parser.parse_args()

    cleaner = PhotoDuplicateCleaner(
        folder_paths=args.folders,
        hash_size=args.hash_size,
        similarity_threshold=args.threshold,
        recursive=not args.no_recursive
    )

    cleaner.run()


if __name__ == "__main__":
    # 如果直接執行腳本，使用互動模式
    if len(sys.argv) == 1:
        print("🖼️  智能照片重複檢測與清理工具 (多目錄版)")
        print("="*70)

        # 輸入多個資料夾路徑
        print("📁 請輸入要掃描的資料夾路徑 (可輸入多個，用空格分隔):")
        folder_input = input("資料夾路徑: ").strip()

        if not folder_input:
            print("❌ 未輸入資料夾路徑")
            exit(1)

        # 解析多個路徑
        folder_paths = [path.strip().strip('"\'') for path in folder_input.split()]

        # 詢問是否遞迴掃描
        recursive_input = input("是否掃描子目錄? (y/N): ").strip().lower()
        recursive = recursive_input in ['y', 'yes', '是']

        # 詢問進階設定
        print("\n⚙️  進階設定 (直接按 Enter 使用預設值):")
        hash_size_input = input("雜湊大小 (預設 8): ").strip()
        threshold_input = input("相似度閾值 (預設 5): ").strip()

        hash_size = int(hash_size_input) if hash_size_input.isdigit() else 8
        threshold = int(threshold_input) if threshold_input.isdigit() else 5

        print(f"\n🚀 開始處理 {len(folder_paths)} 個資料夾...")

        cleaner = PhotoDuplicateCleaner(
            folder_paths=folder_paths,
            hash_size=hash_size,
            similarity_threshold=threshold,
            recursive=recursive
        )

        cleaner.run()
    else:
        main()
