# ruff: noqa
"""Работа с DXF файлами."""
from pathlib import Path

import ezdxf
import matplotlib.pyplot as plt

from ezdxf.math import Vec2
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.config import ColorPolicy, Configuration
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend


def get_bounding_box(msp: ezdxf.layouts.Modelspace) -> tuple[Vec2, Vec2]:
    """Получение границы чертежа."""
    min_point = Vec2(float("inf"), float("inf"))
    max_point = Vec2(float("-inf"), float("-inf"))

    for entity in msp:
        if entity.dxftype() == "CIRCLE":  # Обработка окружностей
            center = Vec2(entity.dxf.center)
            radius = entity.dxf.radius
            min_point = Vec2(min(min_point.x, center.x - radius), min(min_point.y, center.y - radius))
            max_point = Vec2(max(max_point.x, center.x + radius), max(max_point.y, center.y + radius))
        elif entity.dxftype() == "LINE":  # Обработка линий
            start = Vec2(entity.dxf.start)
            end = Vec2(entity.dxf.end)
            min_point = Vec2(min(min_point.x, start.x, end.x), min(min_point.y, start.y, end.y))
            max_point = Vec2(max(max_point.x, start.x, end.x), max(max_point.y, start.y, end.y))
        elif entity.dxftype() == "LWPOLYLINE":  # Обработка полилиний
            points = [Vec2(p[0], p[1]) for p in entity.get_points()]
            if points:
                min_point = Vec2(min(min_point.x, *(p.x for p in points)), min(min_point.y, *(p.y for p in points)))
                max_point = Vec2(max(max_point.x, *(p.x for p in points)), max(max_point.y, *(p.y for p in points)))
        elif entity.dxftype() == "ARC":  # Обработка дуг
            center = Vec2(entity.dxf.center)
            radius = entity.dxf.radius
            angle_min = entity.dxf.start_angle
            angle_max = entity.dxf.end_angle
            # Вычисляем крайние точки дуги
            from math import cos, sin, radians
            start_point = Vec2(center.x + radius * cos(radians(angle_min)), center.y + radius * sin(radians(angle_min)))
            end_point = Vec2(center.x + radius * cos(radians(angle_max)), center.y + radius * sin(radians(angle_max)))
            min_point = Vec2(min(min_point.x, start_point.x, end_point.x, center.x - radius),
                             min(min_point.y, start_point.y, end_point.y, center.y - radius))
            max_point = Vec2(max(max_point.x, start_point.x, end_point.x, center.x + radius),
                             max(max_point.y, start_point.y, end_point.y, center.y + radius))
        elif hasattr(entity, "extents"):  # Обработка других объектов с методом extents()
            bbox = entity.extents()
            min_point = Vec2(min(min_point.x, bbox[0].x), min(min_point.y, bbox[0].y))
            max_point = Vec2(max(max_point.x, bbox[1].x), max(max_point.y, bbox[1].y))

        elif entity.dxftype() == "INSERT":  # Обработка блоков (вставок)
            insertion_point = Vec2(entity.dxf.insert)  # Точка вставки блока
            xscale = entity.dxf.xscale if entity.dxf.xscale != 0 else 1  # Масштаб по X
            yscale = entity.dxf.yscale if entity.dxf.yscale != 0 else 1  # Масштаб по Y
            rotation = entity.dxf.rotation  # Поворот блока

            # Получаем определение блока через документ
            block = entity.block()  # Метод block() возвращает определение блока
            if block is not None:
                # Находим минимальные и максимальные координаты блока вручную
                block_min = Vec2(float("inf"), float("inf"))
                block_max = Vec2(float("-inf"), float("-inf"))

                for e in block:  # Перебираем элементы внутри блока
                    if e.dxftype() == "CIRCLE":  # Обработка окружностей
                        center = Vec2(e.dxf.center)
                        radius = e.dxf.radius
                        block_min = Vec2(min(block_min.x, center.x - radius), min(block_min.y, center.y - radius))
                        block_max = Vec2(max(block_max.x, center.x + radius), max(block_max.y, center.y + radius))

                    elif e.dxftype() == "LINE":  # Обработка линий
                        start = Vec2(e.dxf.start)
                        end = Vec2(e.dxf.end)
                        block_min = Vec2(min(block_min.x, start.x, end.x), min(block_min.y, start.y, end.y))
                        block_max = Vec2(max(block_max.x, start.x, end.x), max(block_max.y, start.y, end.y))

                    elif e.dxftype() == "LWPOLYLINE":  # Обработка полилиний
                        points = [Vec2(p[0], p[1]) for p in e.get_points()]
                        if points:
                            block_min = Vec2(min(block_min.x, *(p.x for p in points)),
                                             min(block_min.y, *(p.y for p in points)))
                            block_max = Vec2(max(block_max.x, *(p.x for p in points)),
                                             max(block_max.y, *(p.y for p in points)))

                    elif hasattr(e, "extents"):  # Обработка других объектов с методом extents()
                        bbox = e.extents()
                        block_min = Vec2(min(block_min.x, bbox[0].x), min(block_min.y, bbox[0].y))
                        block_max = Vec2(max(block_max.x, bbox[1].x), max(block_max.y, bbox[1].y))

                if block_min != Vec2(float("inf"), float("inf")) and block_max != Vec2(float("-inf"), float("-inf")):
                    # Применяем преобразования блока к его границам
                    transformed_block_min = insertion_point + Vec2(
                        (block_min.x * xscale),
                        (block_min.y * yscale),
                    ).rotate_deg(rotation)

                    transformed_block_max = insertion_point + Vec2(
                        (block_max.x * xscale),
                        (block_max.y * yscale),
                    ).rotate_deg(rotation)

                    # Обновляем глобальные минимум и максимум
                    min_point = Vec2(min(min_point.x, transformed_block_min.x, transformed_block_max.x),
                                     min(min_point.y, transformed_block_min.y, transformed_block_max.y))
                    max_point = Vec2(max(max_point.x, transformed_block_min.x, transformed_block_max.x),
                                     max(max_point.y, transformed_block_min.y, transformed_block_max.y))

        else:
            print(f"Не известный тип фигуры: {entity.dxftype()}") # noqa
        print(min_point, max_point) # noqa
    return min_point, max_point


def add_bounding_dimensions(ax: plt.Axes, min_point: Vec2, max_point: Vec2) -> None:
    """Добавление габаритных размеров."""
    width = max_point.x - min_point.x
    height = max_point.y - min_point.y
    axes_offset = 10
    # Добавляем размер по ширине
    ax.annotate(
        f"Ширина: {width:.2f}",
        xy=((min_point.x + max_point.x) / 2, min_point.y),
        xytext=(0, 15),
        textcoords="offset points",
        ha="center",
        fontsize=8,
        color="black",  # Изменён цвет текста на чёрный
    )
    ax.plot([min_point.x - axes_offset, max_point.x - axes_offset],
            [min_point.y - axes_offset, min_point.y - axes_offset], "k--")  # Чёрные пунктирные линии

    # Добавляем размер по высоте
    ax.annotate(
        f"Высота: {height:.2f}",
        xy=(min_point.x, (min_point.y + max_point.y) / 2),
        xytext=(15, 0),
        textcoords="offset points",
        rotation=90,
        va="center",
        fontsize=8,
        color="black",  # Изменён цвет текста на чёрный
    )
    ax.plot([min_point.x - axes_offset, min_point.x - axes_offset],
            [min_point.y - axes_offset, max_point.y - axes_offset], "k--")  # Чёрные пунктирные линии


def dxf_to_image_with_bounding(dxf_file: Path, output_image: str | None = None) -> None:
    """Рендеринг DXF в изображение с белым фоном и чёрными линиями."""
    # Загрузка DXF-файла
    doc = ezdxf.readfile(dxf_file)
    msp = doc.modelspace()  # Получаем пространство модели

    # Создание контекста рендеринга
    fig = plt.figure(facecolor="white")  # Белый фон фигуры
    ax = fig.add_axes([0, 0, 1, 1], facecolor="black")  # Белый фон осей
    ctx = RenderContext(doc)

    # Настройка конфигурации рендеринга
    config = Configuration(lineweight_scaling=3,
        color_policy=ColorPolicy.BLACK)

    # Создание backend'a для Matplotlib
    backend = MatplotlibBackend(ax)
    frontend = Frontend(ctx, backend, config=config)

    # Рисование элементов DXF
    frontend.draw_layout(msp)

    # Получение границ чертежа
    min_point, max_point = get_bounding_box(msp)

    # Добавление габаритных размеров
    add_bounding_dimensions(ax, min_point, max_point)

    # Сохранение изображения
    fig.savefig(output_image, dpi=300, transparent=True, facecolor="white", edgecolor="black")
    plt.close(fig)

if __name__ == "__main__":
    base_path = Path(r"M:\Xranenie\Чертежи на плазму\А КОТЛЫ")
    # file_name = "8СП СТГ2-3.dxf"
    file_name = "4СП 500R.3000.001-01 Обечайка дымогарника (ДЛЯ ГИБКИ).dxf"
    input_dxf = base_path / file_name  # Путь к вашему DXF-файлу
    output_png = "output_with_white_background.png"  # Путь к выходному изображению
    dxf_to_image_with_bounding(input_dxf, output_png)
    print(f"Изображение сохранено как {output_png}")  # noqa
