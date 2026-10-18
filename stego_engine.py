from PIL import Image

def text_to_bin(text):
    return ''.join(format(ord(i), '08b') for i in text)

def bin_to_text(binary):
    bytes_list = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join(chr(int(b, 2)) for b in bytes_list)

def encode_image(img_path, message, key, out_path):
    payload = f"{key}::{message}###END###"
    binary = text_to_bin(payload)
    
    img = Image.open(img_path).convert("RGB")
    pixels = img.load()
    w, h = img.size
    
    idx = 0
    total = len(binary)
    
    for y in range(h):
        for x in range(w):
            if idx < total:
                r, g, b = pixels[x, y]
                new_r = (r & ~1) | int(binary[idx])
                pixels[x, y] = (new_r, g, b)
                idx += 1
            else:
                break
        if idx >= total:
            break
            
    img.save(out_path, "PNG")

def decode_image(img_path, input_key):
    img = Image.open(img_path).convert("RGB")
    pixels = img.load()
    w, h = img.size
    
    binary = ""
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            binary += str(r & 1)
            
            if len(binary) % 8 == 0:
                current_text = bin_to_text(binary)
                if "###END###" in current_text:
                    clean_data = current_text.replace("###END###", "")
                    if "::" in clean_data:
                        saved_key, msg = clean_data.split("::", 1)
                        if saved_key == input_key:
                            return True, msg
                        return False, "Invalid Key!"
                    return False, "Corrupted Payload!"
    return False, "No hidden message found."