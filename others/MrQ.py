import os
import sys
from PIL import Image
import qrcode
import cv2
from pyzbar.pyzbar import decode

def read_text(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8", errors="replace")

def make_qr(data, version=1, error=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4):
    qr = qrcode.QRCode(version=version, error_correction=error, box_size=box_size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")

def make_color_encoded_qr(r_data, g_data, b_data):
    base_r = make_qr(r_data)
    base_g = make_qr(g_data)
    base_b = make_qr(b_data)
    r1, _, _ = base_r.split()
    _, g1, _ = base_g.split()
    _, _, b1 = base_b.split()
    return Image.merge("RGB", (r1, g1, b1))

def force_size(img, w, h):
    return img.resize((w, h), resample=Image.NEAREST)

def stack_vertical(top_img, bottom_img):
    w = max(top_img.width, bottom_img.width)
    h = top_img.height + bottom_img.height
    out = Image.new("RGB", (w, h), (255, 255, 255))
    out.paste(top_img.convert("RGB"), (0, 0))
    out.paste(bottom_img.convert("RGB"), (0, top_img.height))
    return out

def slice_to_frames(img, tile_w, tile_h):
    frames = []
    for y in range(0, img.height, tile_h):
        for x in range(0, img.width, tile_w):
            frames.append(img.crop((x, y, x + tile_w, y + tile_h)).convert("RGB"))
    return frames

def save_gif_from_frames(frames, path, duration_ms=100):
    frames[0].save(path, save_all=True, append_images=frames[1:], optimize=False, duration=duration_ms, loop=0)

def interlace_two_gifs(gif_a_path, gif_b_path, out_path, duration_ms=100):
    a = Image.open(gif_a_path)
    b = Image.open(gif_b_path)
    frames = []
    n = min(getattr(a, "n_frames", 1), getattr(b, "n_frames", 1))
    for i in range(n):
        a.seek(i)
        b.seek(i)
        frames.append(a.convert("RGB").copy())
        frames.append(b.convert("RGB").copy())
    save_gif_from_frames(frames, out_path, duration_ms)

def split_gif_frames(gif_path, frames_dir, ensure_size=(127,127)):
    os.makedirs(frames_dir, exist_ok=True)
    with Image.open(gif_path) as gif:
        n = getattr(gif, "n_frames", 1)
        for i in range(n):
            gif.seek(i)
            f = gif.convert("RGB")
            if ensure_size:
                f = f.resize(ensure_size, Image.NEAREST) if (f.width != ensure_size[0] or f.height != ensure_size[1]) else f
            fp = os.path.join(frames_dir, f"frame_{i:03d}.png")
            f.save(fp)

def reassemble_qr_even_first(frames_dir, output_image_path, tile=127, cols=10, rows=20):
    w, h = tile * cols, tile * rows
    out = Image.new("RGB", (w, h), (255, 255, 255))
    for i in range(rows):
        for j in range(cols):
            idx = (j + i * cols) * 2 if i < rows // 2 else (j + (i - rows // 2) * cols) * 2 + 1
            fp = os.path.join(frames_dir, f"frame_{idx:03d}.png")
            if os.path.exists(fp):
                img = Image.open(fp).convert("RGB")
                if img.size != (tile, tile):
                    img = img.resize((tile, tile), Image.NEAREST)
                out.paste(img, (j * tile, i * tile))
    out.save(output_image_path)
    return output_image_path

def decode_color_qr(image_path):
    image = cv2.imread(image_path)
    b, g, r = cv2.split(image)
    decoded = {}
    for name, ch in (("red", r), ("green", g), ("blue", b)):
        ch3 = cv2.merge([ch, ch, ch])
        objs = decode(ch3)
        decoded[name] = objs[0].data.decode("utf-8") if objs else None
    return decoded

def generate_pipeline(e_path, n_path, c_path, trad_path=None, out_dir="out", tile=127, cols=10, rows=20, duration_ms=100):
    os.makedirs(out_dir, exist_ok=True)
    e = read_text(e_path)
    n = read_text(n_path)
    c = read_text(c_path)
    encoded = make_color_encoded_qr(e, n, c)
    if trad_path and os.path.exists(trad_path):
        trad_data = read_text(trad_path)
        traditional = make_qr(trad_data)
    else:
        traditional = make_qr(f"padding|{len(e)}|{len(n)}|{len(c)}")
    target_w = tile * cols
    half_h = tile * (rows // 2)
    encoded = force_size(encoded, target_w, half_h)
    traditional = force_size(traditional, target_w, half_h)
    enc_stack = stack_vertical(encoded, traditional)
    enc_png = os.path.join(out_dir, "encoded_top.png")
    enc_stack.save(enc_png)
    enc_gif = os.path.join(out_dir, "encoded_top.gif")
    save_gif_from_frames(slice_to_frames(enc_stack, tile, tile), enc_gif, duration_ms)
    trad_stack = stack_vertical(traditional, encoded)
    trad_png = os.path.join(out_dir, "traditional_top.png")
    trad_stack.save(trad_png)
    trad_gif = os.path.join(out_dir, "traditional_top.gif")
    save_gif_from_frames(slice_to_frames(trad_stack, tile, tile), trad_gif, duration_ms)
    final_interlaced = os.path.join(out_dir, "final_interlaced.gif")
    interlace_two_gifs(enc_gif, trad_gif, final_interlaced, duration_ms)
    print(enc_png)
    print(enc_gif)
    print(trad_png)
    print(trad_gif)
    print(final_interlaced)

def extract_pipeline(gif_path, out_dir="out_extract", tile=127, cols=10, rows=20):
    os.makedirs(out_dir, exist_ok=True)
    frames_dir = os.path.join(out_dir, "frames")
    split_gif_frames(gif_path, frames_dir, ensure_size=(tile, tile))
    reassembled = os.path.join(out_dir, "reassembled_qr.png")
    reassemble_qr_even_first(frames_dir, reassembled, tile, cols, rows)
    data = decode_color_qr(reassembled)
    print(reassembled)
    print(data)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python script.py generate <e_file> <n_file> <c_file> [trad_file] [out_dir]")
        print("  python script.py extract <gif_path> [out_dir]")
        sys.exit(1)
    mode = sys.argv[1].lower()
    if mode == "generate":
        if len(sys.argv) < 5:
            print("Usage: python script.py generate <e_file> <n_file> <c_file> [trad_file] [out_dir]")
            sys.exit(1)
        e_file = sys.argv[2]
        n_file = sys.argv[3]
        c_file = sys.argv[4]
        trad_file = sys.argv[5] if len(sys.argv) > 5 and os.path.isfile(sys.argv[5]) else None
        out_dir = sys.argv[6] if len(sys.argv) > 6 else ("out" if len(sys.argv) <= 5 or trad_file else sys.argv[5])
        generate_pipeline(e_file, n_file, c_file, trad_file, out_dir)
    elif mode == "extract":
        if len(sys.argv) < 3:
            print("Usage: python script.py extract <gif_path> [out_dir]")
            sys.exit(1)
        gif_path = sys.argv[2]
        out_dir = sys.argv[3] if len(sys.argv) > 3 else "out_extract"
        extract_pipeline(gif_path, out_dir)
    else:
        print("Mode must be 'generate' or 'extract'")
        sys.exit(1)
