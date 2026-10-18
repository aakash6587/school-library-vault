from PIL import Image

# --- EXISTING SINGLE ENCODERS/DECODERS ---
def encode_image(image_path, secret_text, key, output_path):
    img = Image.open(image_path).convert('RGB')
    encoded = img.copy()
    pixels = encoded.load()
    
    secret_text += "#####"
    binary_secret = ''.join(format(ord(c), '08b') for c in secret_text)
    
    data_idx = 0
    data_len = len(binary_secret)
    
    for y in range(img.height):
        for x in range(img.width):
            if data_idx < data_len:
                r, g, b = pixels[x, y]
                r = (r & ~1) | int(binary_secret[data_idx])
                pixels[x, y] = (r, g, b)
                data_idx += 1
            else:
                break
        if data_idx >= data_len:
            break
            
    encoded.save(output_path, format='PNG')

def decode_image(image_path, key):
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    
    binary_data = ""
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            binary_data += str(r & 1)
            
    all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded_text = ""
    for byte in all_bytes:
        decoded_text += chr(int(byte, 2))
        if decoded_text.endswith("#####"):
            return True, decoded_text[:-5]
            
    return False, "No hidden message found or invalid format."

def encode_image_in_image(cover_path, secret_path, output_path):
    cover = Image.open(cover_path).convert('RGB')
    secret = Image.open(secret_path).convert('RGB')
    secret = secret.resize(cover.size)
    cover_pixels = cover.load()
    secret_pixels = secret.load()
    
    stego = Image.new('RGB', cover.size)
    stego_pixels = stego.load()
    
    for x in range(cover.width):
        for y in range(cover.height):
            cr, cg, cb = cover_pixels[x, y]
            sr, sg, sb = secret_pixels[x, y]
            
            nr = (cr & 0xF0) | (sr >> 4)
            ng = (cg & 0xF0) | (sg >> 4)
            nb = (cb & 0xF0) | (sb >> 4)
            stego_pixels[x, y] = (nr, ng, nb)
            
    stego.save(output_path, format='PNG')

def decode_image_from_image(stego_path, output_path):
    stego = Image.open(stego_path).convert('RGB')
    stego_pixels = stego.load()
    
    secret = Image.new('RGB', stego.size)
    secret_pixels = secret.load()
    
    for x in range(stego.width):
        for y in range(stego.height):
            r, g, b = stego_pixels[x, y]
            sr = (r & 0x0F) << 4
            sg = (g & 0x0F) << 4
            sb = (b & 0x0F) << 4
            secret_pixels[x, y] = (sr, sg, sb)
            
    secret.save(output_path, format='PNG')

# --- DUAL ENCODER & DECODER (TEXT + IMAGE COMBINED) ---
def encode_dual_stego(cover_path, secret_img_path, secret_text, output_path):
    cover = Image.open(cover_path).convert('RGB')
    secret_img = Image.open(secret_img_path).convert('RGB').resize(cover.size)
    
    cover_pixels = cover.load()
    secret_pixels = secret_img.load()
    
    stego = Image.new('RGB', cover.size)
    stego_pixels = stego.load()
    
    secret_text += "#####"
    binary_text = ''.join(format(ord(c), '08b') for c in secret_text)
    data_idx = 0
    data_len = len(binary_text)
    
    for y in range(cover.height):
        for x in range(cover.width):
            cr, cg, cb = cover_pixels[x, y]
            sr, sg, sb = secret_pixels[x, y]
            
            nr = (cr & 0xF0) | ((sr >> 5) << 1)
            ng = (cg & 0xF0) | ((sg >> 5) << 1)
            nb = (cb & 0xF0) | ((sb >> 5) << 1)
            
            if data_idx < data_len:
                nr = (nr & ~1) | int(binary_text[data_idx])
                data_idx += 1
                
            stego_pixels[x, y] = (nr, ng, nb)
            
    stego.save(output_path, format='PNG')

def decode_dual_stego(stego_path, output_img_path):
    stego = Image.open(stego_path).convert('RGB')
    pixels = stego.load()
    
    secret_img = Image.new('RGB', stego.size)
    secret_pixels = secret_img.load()
    
    binary_text = ""
    
    for y in range(stego.height):
        for x in range(stego.width):
            r, g, b = pixels[x, y]
            
            binary_text += str(r & 1)
            
            sr = ((r >> 1) & 0x07) << 5
            sg = ((g >> 1) & 0x07) << 5
            sb = ((b >> 1) & 0x07) << 5
            secret_pixels[x, y] = (sr, sg, sb)
            
    secret_img.save(output_img_path, format='PNG')
    
    all_bytes = [binary_text[i:i+8] for i in range(0, len(binary_text), 8)]
    decoded_text = ""
    for byte in all_bytes:
        decoded_text += chr(int(byte, 2))
        if decoded_text.endswith("#####"):
            return True, decoded_text[:-5]
            
    return False, "No hidden text found."