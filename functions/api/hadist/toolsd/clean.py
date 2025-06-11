import json
import os
import shutil
from pathlib import Path
from datetime import datetime

class HadistCleaner:
    def __init__(self, data_folder="data"):
        self.data_folder = data_folder
        self.backup_folder = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def create_backup(self):
        """Buat backup folder sebelum cleaning"""
        if not os.path.exists(self.data_folder):
            print(f"❌ Folder '{self.data_folder}' tidak ditemukan!")
            return False
            
        try:
            shutil.copytree(self.data_folder, self.backup_folder)
            print(f"✅ Backup dibuat: {self.backup_folder}")
            return True
        except Exception as e:
            print(f"❌ Gagal membuat backup: {e}")
            return False
    
    def analyze_files(self):
        """Analisis kondisi file JSON sebelum cleaning"""
        print("\n🔍 ANALISIS FILE JSON")
        print("=" * 60)
        
        json_files = list(Path(self.data_folder).glob("*.json"))
        
        if not json_files:
            print(f"❌ Tidak ada file JSON di folder '{self.data_folder}'")
            return []
        
        analysis_results = []
        
        for json_file in sorted(json_files):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'hadist' not in data:
                    continue
                
                hadist_list = data['hadist']
                numbers = [item.get('no', 0) for item in hadist_list]
                
                analysis = {
                    'filename': json_file.name,
                    'total_hadist': len(hadist_list),
                    'min_no': min(numbers) if numbers else 0,
                    'max_no': max(numbers) if numbers else 0,
                    'has_duplicates': len(numbers) != len(set(numbers)),
                    'has_missing': False,
                    'has_zero_or_negative': any(n <= 0 for n in numbers),
                    'is_sequential': numbers == list(range(1, len(numbers) + 1)),
                    'collection': data.get('metadata', {}).get('collection', 'Unknown')
                }
                
                # Cek missing numbers
                if numbers:
                    expected_range = set(range(min(numbers), max(numbers) + 1))
                    actual_numbers = set(numbers)
                    analysis['has_missing'] = len(expected_range - actual_numbers) > 0
                
                analysis_results.append(analysis)
                
                # Print status
                status_icons = []
                if analysis['is_sequential']:
                    status_icons.append("✅")
                else:
                    if analysis['has_duplicates']:
                        status_icons.append("🔄")
                    if analysis['has_missing']:
                        status_icons.append("❓")
                    if analysis['has_zero_or_negative']:
                        status_icons.append("⚠️")
                    if not status_icons:
                        status_icons.append("🔧")
                
                status = "".join(status_icons)
                print(f"{status} {json_file.name:<15} | {analysis['total_hadist']:>4} hadist | Range: {analysis['min_no']}-{analysis['max_no']} | {analysis['collection']}")
                
            except Exception as e:
                print(f"❌ {json_file.name:<15} | Error: {e}")
        
        print("\n📊 LEGEND:")
        print("✅ Sudah terurut dengan benar")
        print("🔄 Ada nomor duplikat")
        print("❓ Ada nomor yang hilang")
        print("⚠️ Ada nomor 0 atau negatif")
        print("🔧 Perlu dirapihkan")
        
        return analysis_results
    
    def clean_file(self, filepath):
        """Clean satu file JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'hadist' not in data:
                return False, "No 'hadist' key found"
            
            original_count = len(data['hadist'])
            
            # Urutkan nomor hadist dari 1
            for index, hadist_item in enumerate(data['hadist']):
                hadist_item['no'] = index + 1
            
            # Update metadata
            if 'metadata' in data:
                data['metadata']['total_hadist'] = len(data['hadist'])
            
            # Simpan file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True, f"Cleaned {original_count} hadist"
            
        except Exception as e:
            return False, str(e)
    
    def clean_all_files(self):
        """Clean semua file JSON"""
        print("\n🧹 CLEANING PROCESS")
        print("=" * 60)
        
        json_files = list(Path(self.data_folder).glob("*.json"))
        success_count = 0
        
        for json_file in sorted(json_files):
            success, message = self.clean_file(json_file)
            
            if success:
                print(f"✅ {json_file.name:<15} | {message}")
                success_count += 1
            else:
                print(f"❌ {json_file.name:<15} | Error: {message}")
        
        print(f"\n📊 Berhasil membersihkan {success_count} dari {len(json_files)} file")
        return success_count
    
    def validate_cleaned_files(self):
        """Validasi file setelah cleaning"""
        print("\n✅ VALIDASI HASIL")
        print("=" * 60)
        
        json_files = list(Path(self.data_folder).glob("*.json"))
        all_valid = True
        total_hadist = 0
        
        for json_file in sorted(json_files):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                hadist_count = len(data['hadist'])
                total_hadist += hadist_count
                
                # Cek sequential numbering
                numbers = [item['no'] for item in data['hadist']]
                expected_numbers = list(range(1, hadist_count + 1))
                
                is_valid = numbers == expected_numbers
                all_valid = all_valid and is_valid
                
                status = "✅" if is_valid else "❌"
                collection = data.get('metadata', {}).get('collection', 'Unknown')
                metadata_total = data.get('metadata', {}).get('total_hadist', 'N/A')
                
                print(f"{status} {json_file.name:<15} | {hadist_count:>4} hadist | Metadata: {metadata_total} | {collection}")
                
            except Exception as e:
                print(f"❌ {json_file.name:<15} | Error: {e}")
                all_valid = False
        
        print("=" * 60)
        print(f"📊 Total: {total_hadist} hadist dari {len(json_files)} file")
        
        if all_valid:
            print("🎉 Semua file valid dan siap digunakan!")
        else:
            print("⚠️ Ada file yang masih bermasalah")
        
        return all_valid
    
    def generate_report(self):
        """Generate laporan lengkap"""
        print("\n📋 LAPORAN LENGKAP")
        print("=" * 60)
        
        json_files = list(Path(self.data_folder).glob("*.json"))
        collections = {}
        
        for json_file in sorted(json_files):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                collection = data.get('metadata', {}).get('collection', 'Unknown')
                hadist_count = len(data['hadist'])
                
                if collection not in collections:
                    collections[collection] = []
                
                collections[collection].append({
                    'file': json_file.name,
                    'count': hadist_count
                })
                
            except Exception as e:
                print(f"Error reading {json_file.name}: {e}")
        
        # Print summary by collection
        total_hadist = 0
        for collection, files in collections.items():
            collection_total = sum(f['count'] for f in files)
            total_hadist += collection_total
            print(f"📚 {collection}:")
            for file_info in files:
                print(f"   └── {file_info['file']}: {file_info['count']} hadist")
            print(f"   Total: {collection_total} hadist\n")
        
        print(f"🎯 GRAND TOTAL: {total_hadist} hadist dari {len(json_files)} file")

def main():
    print("🕌 HADIST JSON ADVANCED CLEANER")
    print("=" * 60)
    
    cleaner = HadistCleaner()
    
    # Cek folder data
    if not os.path.exists("data"):
        print("❌ Folder 'data' tidak ditemukan!")
        return
    
    # Analisis file
    analysis_results = cleaner.analyze_files()
    
    if not analysis_results:
        print("❌ Tidak ada file JSON yang valid ditemukan")
        return
    
    # Tanya apakah perlu cleaning
    needs_cleaning = any(not result['is_sequential'] for result in analysis_results)
    
    if not needs_cleaning:
        print("\n🎉 Semua file sudah dalam kondisi baik!")
        cleaner.generate_report()
        return
    
    print(f"\n🔧 Ditemukan {sum(1 for r in analysis_results if not r['is_sequential'])} file yang perlu dibersihkan")
    print("\nScript ini akan:")
    print("1. 💾 Membuat backup folder")
    print("2. 🧹 Mengurutkan nomor hadist dari 1, 2, 3, ...")
    print("3. 📊 Update metadata total_hadist")
    print("4. ✅ Validasi hasil")
    
    confirm = input("\nLanjutkan? (y/n): ").lower().strip()
    
    if confirm not in ['y', 'yes', 'ya']:
        print("❌ Dibatalkan")
        return
    
    # Proses cleaning
    if cleaner.create_backup():
        success_count = cleaner.clean_all_files()
        
        if success_count > 0:
            cleaner.validate_cleaned_files()
            cleaner.generate_report()
            
            print(f"\n🎉 CLEANING SELESAI!")
            print(f"✅ {success_count} file berhasil dibersihkan")
            print(f"💾 Backup tersimpan di: {cleaner.backup_folder}")
            print("\nFile JSON siap untuk digunakan di Cloudflare Pages API!")
        else:
            print("\n❌ Tidak ada file yang berhasil dibersihkan")
    else:
        print("❌ Gagal membuat backup, proses dibatalkan")

if __name__ == "__main__":
    main()