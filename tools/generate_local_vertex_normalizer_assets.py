from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

OUT = Path('docs/local-vertex-normalizer')
OUT.mkdir(parents=True, exist_ok=True)
REGULAR = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
BASELINE = '기준: 최소실패-지점 / f61166e1b6cf74c3c2d05fb574556634f02293b2'


def f(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REGULAR, size)


def rounded(draw, box, fill, outline, radius=24, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def center(draw, box, text, font, fill=(25, 25, 25), spacing=6):
    x0, y0, x1, y1 = box
    bb = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align='center')
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.multiline_text(((x0 + x1 - tw) / 2, (y0 + y1 - th) / 2), text,
                        font=font, fill=fill, spacing=spacing, align='center')


def arrow(draw, start, end, fill=(60, 60, 60), width=5, head=16):
    draw.line([start, end], fill=fill, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    p1 = (end[0] - head * math.cos(angle - math.pi / 6),
          end[1] - head * math.sin(angle - math.pi / 6))
    p2 = (end[0] - head * math.cos(angle + math.pi / 6),
          end[1] - head * math.sin(angle + math.pi / 6))
    draw.polygon([end, p1, p2], fill=fill)


def footer(draw, width, y):
    draw.text((70, y), BASELINE, font=f(20), fill=(90, 90, 90))


def make_purpose():
    W, H = 1800, 1130
    im = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(im)
    d.text((70, 45), 'LocalVertexNormalizer의 최종 목적', font=f(52, True), fill=(20, 20, 20))
    d.text((72, 115), '좌표를 예쁘게 반올림하는 것이 아니라, 작은 좌표 오차를 제거하면서도 기존 Solid의 표면과 위상을 지키는 것',
           font=f(28), fill=(60, 60, 60))

    boxes = [
        ((80, 240, 450, 520), '입력 Solid\n\n거의 같은 좌표\n미세한 틈\n짧은 삼각형\n중복 경계',
         (247, 247, 247), (100, 100, 100)),
        ((575, 240, 1225, 520), 'Normalizer\n\n정점을 격자에 맞춤\n경계·삼각형을 재구성\n닫힌 껍질인지 검사\n실패하면 원상복구',
         (232, 243, 255), (38, 91, 150)),
        ((1350, 240, 1720, 520), '출력 Solid\n\n격자 좌표\nManifold\n닫힌 표면\n원래 표면과 동등',
         (235, 249, 240), (50, 120, 70)),
    ]
    for box, text, fill, outline in boxes:
        rounded(d, box, fill, outline)
        center(d, box, text, f(31, 'Normalizer' in text))
    arrow(d, (450, 380), (575, 380))
    arrow(d, (1225, 380), (1350, 380))

    guard = (180, 650, 1620, 980)
    rounded(d, guard, (255, 247, 230), (190, 120, 20), radius=30, width=4)
    d.text((230, 690), '반드시 지켜야 하는 세 가지', font=f(36, True), fill=(120, 75, 10))
    rows = [
        ('1', '격자 정렬', '정점이 지정 tolerance의 배수 좌표에 있어야 한다.'),
        ('2', '위상 보존', '면이 사라지거나 새 구멍·교차·겹침이 생기면 안 된다.'),
        ('3', '표면 동등', '삼각형 분할이 달라도 실제 외피와 구멍 경계는 같아야 한다.'),
    ]
    y = 770
    for n, title, desc in rows:
        d.ellipse((240, y - 8, 292, y + 44), fill=(255, 220, 150), outline=(170, 100, 0), width=2)
        center(d, (240, y - 8, 292, y + 44), n, f(25, True))
        d.text((320, y - 5), title, font=f(29, True), fill=(50, 50, 50))
        d.text((540, y - 3), desc, font=f(26), fill=(50, 50, 50))
        y += 70
    footer(d, W, 1085)
    im.save(OUT / '01_normalizer_final_purpose.png', optimize=True)


def make_pipeline():
    W, H = 2000, 1740
    im = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(im)
    d.text((70, 40), 'LocalVertexNormalizer 10단계 파이프라인', font=f(52, True), fill=(20, 20, 20))
    d.text((72, 110), '파란색은 계산 단계, 주황색은 안전 검사, 초록색은 SketchUp 형상 반영 단계',
           font=f(27), fill=(70, 70, 70))
    steps = [
        ('1', '입력 Solid 검증', '작업 가능한 Group인지 확인하고 원본 topology·volume을 기록'),
        ('2', '축 평면 계획', 'X/Y/Z 방향 면 묶음을 찾아 같은 평면이 같은 격자값을 사용하게 함'),
        ('3', '삼각형 스냅샷', 'SketchUp Face를 독립 triangle 기록으로 복사하고 원본 경계를 보존'),
        ('4', '격자 목표 계산', '각 정점을 tolerance 격자에 맞추되 충돌·퇴화 후보를 표시'),
        ('5', '국소 복구', '무너진 삼각형과 짧은 sliver를 제한적으로 고침'),
        ('6', '평면 패치 재삼각화', '영향받은 면 묶음을 외곽선과 구멍 기준으로 다시 삼각분할'),
        ('7', '사전 Hard Gate', '원본 삭제 전에 전체 triangle mesh가 닫히고 교차하지 않는지 검사'),
        ('8', 'SketchUp 재빌드', '검증된 triangle로 실제 Face와 Edge를 다시 생성'),
        ('9', '방향·공면 정리', '면 방향을 통일하고 안전한 내부 공면 edge만 제거'),
        ('10', '최종 Hard Gate', 'Manifold·격자 잔차·표면 동등성을 모두 통과해야 성공'),
    ]
    box_w, box_h = 850, 210
    xs = [100, 1050]
    y0, gap = 210, 75
    for i, (n, title, desc) in enumerate(steps):
        col, row = i % 2, i // 2
        x, y = xs[col], y0 + row * (box_h + gap)
        if n in ('7', '10'):
            fill, outline = (255, 239, 220), (190, 95, 20)
        elif n in ('8', '9'):
            fill, outline = (231, 247, 235), (45, 120, 65)
        else:
            fill, outline = (232, 243, 255), (40, 95, 155)
        rounded(d, (x, y, x + box_w, y + box_h), fill, outline, radius=25, width=4)
        d.ellipse((x + 28, y + 35, x + 105, y + 112), fill='white', outline=outline, width=3)
        center(d, (x + 28, y + 35, x + 105, y + 112), n, f(34, True))
        d.text((x + 135, y + 30), title, font=f(31, True), fill=(30, 30, 30))
        lines = [desc[i:i + 38] for i in range(0, len(desc), 38)]
        d.multiline_text((x + 135, y + 88), '\n'.join(lines), font=f(25), fill=(55, 55, 55), spacing=8)
        if i < 8:
            if col == 0:
                arrow(d, (x + box_w, y + box_h / 2), (xs[1] - 30, y + box_h / 2), width=4, head=13)
            else:
                next_y = y0 + (row + 1) * (box_h + gap)
                arrow(d, (x + box_w / 2, y + box_h), (x + box_w / 2, next_y - 25), width=4, head=13)
    rounded(d, (260, 1560, 1740, 1650), (245, 245, 245), (120, 120, 120), radius=20, width=2)
    center(d, (260, 1560, 1740, 1650), '어느 Hard Gate라도 실패하면 작업 전체를 취소하고 원본 Solid를 유지한다.', f(30, True))
    footer(d, W, 1695)
    im.save(OUT / '02_normalizer_10_stage_pipeline.png', optimize=True)


def make_rollback():
    W, H = 1800, 1280
    im = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(im)
    d.text((70, 45), '왜 실패하면 원상복구하는가', font=f(52, True), fill=(20, 20, 20))
    d.text((72, 115), 'Normalizer는 Solid 전체를 재구성하므로, 검증되지 않은 중간 결과를 남기면 기존 성공 요소까지 망가질 수 있다.',
           font=f(27), fill=(70, 70, 70))
    nodes = [
        ((100, 230, 480, 420), '원본 Solid\n백업 가능한 상태', (245, 245, 245), (90, 90, 90)),
        ((710, 230, 1090, 420), '메모리에서\n새 triangle shell 계산', (232, 243, 255), (40, 95, 155)),
        ((1320, 230, 1700, 420), '사전 Hard Gate\n닫힘·교차·edge 사용 검사', (255, 239, 220), (190, 95, 20)),
        ((1320, 600, 1700, 790), 'SketchUp 재빌드\n면 방향·공면 edge 정리', (231, 247, 235), (45, 120, 65)),
        ((710, 600, 1090, 790), '최종 Hard Gate\nManifold·격자·표면 동등', (255, 239, 220), (190, 95, 20)),
        ((100, 600, 480, 790), '성공 Commit\n새 Solid 확정', (231, 247, 235), (45, 120, 65)),
    ]
    for box, text, fill, outline in nodes:
        rounded(d, box, fill, outline, radius=25, width=4)
        center(d, box, text, f(30, True))
    arrow(d, (480, 325), (710, 325))
    arrow(d, (1090, 325), (1320, 325))
    arrow(d, (1510, 420), (1510, 600))
    arrow(d, (1320, 695), (1090, 695))
    arrow(d, (710, 695), (480, 695))
    rounded(d, (470, 930, 1330, 1130), (255, 232, 232), (175, 45, 45), radius=28, width=4)
    center(d, (470, 930, 1330, 1130), '어느 검사에서든 실패\n\nSketchUp operation abort → 원본 형상 복원\n실패한 중간 geometry는 commit하지 않음',
           f(31, True), fill=(95, 20, 20))
    arrow(d, (1510, 790), (1200, 930), fill=(175, 45, 45), width=5, head=17)
    arrow(d, (900, 790), (900, 930), fill=(175, 45, 45), width=5, head=17)
    arrow(d, (1510, 420), (1220, 930), fill=(175, 45, 45), width=4, head=14)
    d.text((100, 1180), '핵심 원칙: 검사를 약하게 만드는 것이 아니라, 안전한 복구 경로를 넓히되 최종 Hard Gate는 유지한다.',
           font=f(27, True), fill=(45, 45, 45))
    footer(d, W, 1240)
    im.save(OUT / '03_normalizer_safety_and_rollback.png', optimize=True)


make_purpose()
make_pipeline()
make_rollback()
