import pandas as pd
import json
import os
from PIL import Image
import argparse

def convert_csv_to_coco(csv_file, image_dir, output_json):
    """Konversi CSV ke format COCO JSON."""
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: File CSV tidak ditemukan: {csv_file}")
        return
    except pd.errors.EmptyDataError:
        print(f"Error: File CSV kosong: {csv_file}")
        return
    except pd.errors.ParserError:
        print(f"Error: Gagal memparsing CSV: {csv_file}")
        return

    if df.empty:
      print(f"Error: Dataframe CSV kosong setelah dibaca: {csv_file}")
      return

    coco_data = {
        "images": [],
        "annotations": [],
        "categories": [] # Kategori akan diisi dinamis
    }

    annotation_id = 0
    image_id = 0

    required_columns = ['fname', 'structure', 'h_min', 'w_min', 'h_max', 'w_max']
    if not all(col in df.columns for col in required_columns):
        print(f"Error: CSV harus memiliki kolom: {required_columns}")
        return

    # Buat dictionary untuk menyimpan kategori unik
    categories = {}
    category_id_counter = 0

    image_files = df['fname'].unique()

    for image_file in image_files:
        image_id += 1
        image_path = os.path.join(image_dir, image_file)

        try:
            img = Image.open(image_path)
            width, height = img.size
        except FileNotFoundError:
            print(f"Peringatan: Gambar {image_path} tidak ditemukan. Melewati.")
            continue
        except Exception as e:
            print(f"Peringatan: Gagal memproses gambar {image_path}: {e}. Melewati.")
            continue

        coco_data["images"].append({
            "id": image_id,
            "file_name": image_file,
            "width": width,
            "height": height
        })

        image_df = df[df['fname'] == image_file]

        for index, row in image_df.iterrows():
            annotation_id += 1
            x_min = row['h_min']
            y_min = row['w_min']
            x_max = row['h_max']
            y_max = row['w_max']
            w = x_max - x_min
            h = y_max - y_min
            bbox = [x_min, y_min, w, h]
            
            category_name = row['struct'] # Ambil nama kategori dari kolom "struct"
            if category_name not in categories:
                category_id_counter += 1
                categories[category_name] = category_id_counter
                coco_data["categories"].append({"id": category_id_counter, "name": category_name})

            category_id = categories[category_name]

            coco_data["annotations"].append({
                "id": annotation_id,
                "image_id": image_id,
                "bbox": bbox,
                "category_id": category_id
            })

    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, 'w') as f:
        json.dump(coco_data, f, indent=4)

    print(f"File COCO JSON berhasil dibuat: {output_json}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Konversi CSV ke format COCO JSON.")
    parser.add_argument("csv_file", help="Path ke file CSV.")
    parser.add_argument("image_dir", help="Path ke direktori gambar.")
    parser.add_argument("output_json", help="Path untuk menyimpan file JSON COCO.")
    args = parser.parse_args()

    convert_csv_to_coco(args.csv_file, args.image_dir, args.output_json)
