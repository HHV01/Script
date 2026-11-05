"""Kiểm tra ảnh cảnh cung cấp thủ công; không kết nối dịch vụ tạo ảnh."""
from PIL import Image
from .common import need

def run(project, force=False):
    scenes = project.load_scenes()
    need(bool(scenes), 'Chưa có phân cảnh để kiểm ảnh.')
    paths = []
    errors = []
    for scene in scenes:
        path = project.image_path(scene)
        try:
            if path is None:
                raise FileNotFoundError()
            with Image.open(path) as image:
                image.verify()
            paths.append(path)
        except (OSError, ValueError, SyntaxError):
            errors.append(scene['id'])
    need(not errors, f'Thiếu hoặc hỏng ảnh cảnh {errors}. Đặt ảnh từng cảnh vào {project.images_dir}, tên canh-001.png (hoặc 001.png), rồi chạy lại collect. Không tự tạo hoặc tải ảnh.')
    for scene, path in zip(scenes, paths):
        scene['image'] = path.name
    project.save_scenes(scenes)
    print(f'[collect] Đọc được đủ {len(scenes)} ảnh cục bộ; chưa duyệt nội dung hình.')
