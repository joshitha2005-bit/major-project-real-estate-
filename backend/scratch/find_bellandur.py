import hashlib

def get_image_index(pid, title, num_images):
    h_str = f"{title}_{pid}"
    h = hashlib.md5(h_str.encode('utf-8')).hexdigest()
    idx = (int(h, 16) % num_images) + 1
    print(f"PID: {pid} | Title: {title} | String: '{h_str}' | Hash: {h} | Modulo index: {idx}")
    return idx

get_image_index(12127, "Srure S", 5)
get_image_index(12081, "NiCodCa", 5)
get_image_index(11949, "OriewLa", 5)
