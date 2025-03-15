import pygame
import sys

def animate_sprites_with_scaling(frames, scale_factor=2, frame_rate=10):
    """
    用 pygame 播放放大后的动画。
    :param frames: 单帧图片路径列表
    :param scale_factor: 放大倍数
    :param frame_rate: 帧率 (帧/秒)
    """
    pygame.init()
    # 假设所有帧尺寸相同，加载第一帧以确定窗口大小
    first_image = pygame.image.load(frames[0])
    frame_width = first_image.get_width() * scale_factor
    frame_height = first_image.get_height() * scale_factor

    screen = pygame.display.set_mode((frame_width, frame_height))
    pygame.display.set_caption("Desktop Pet Animation")

    # 加载并放大所有帧
    images = [
        pygame.transform.scale(pygame.image.load(frame), (frame_width, frame_height))
        for frame in frames
    ]
    clock = pygame.time.Clock()
    running = True
    frame_index = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))  # 背景颜色
        screen.blit(images[frame_index], (0, 0))  # 绘制当前帧
        pygame.display.flip()  # 更新显示

        frame_index = (frame_index + 1) % len(images)  # 循环播放
        clock.tick(frame_rate)  # 控制帧率

    pygame.quit()
    sys.exit()

# 主函数
if __name__ == "__main__":
    # 替换为你的单帧图片路径列表
    frame_paths = [
        "resources/stand/0.png", "resources/stand/1.png",  # 示例路径
        # "frames/frame_0_2.png", "frames/frame_0_3.png"
    ]

    # 动画播放，放大倍数为2
    animate_sprites_with_scaling(frame_paths, scale_factor=30, frame_rate=2)

