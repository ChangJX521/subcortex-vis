# Subcortex Mesh Viewer

[English](README_EN.md) | 中文

轻量级工具，用于导入 NIfTI (`.nii/.nii.gz`) 体数据，通过 marching cubes 提取网格并在 PyVista 中可视化。逻辑参考了仓库中的 `subcortex_regional_overlap.ipynb`。

## 依赖
- Python 3.9+
- `pyvista`, `nibabel`, `numpy`, `scipy`
- GUI 额外需要: `PyQt5`, `pyvistaqt`, `matplotlib`

安装示例：
```bash
pip install pyvista nibabel numpy scipy PyQt5 pyvistaqt matplotlib
```

## 项目结构

```
subcortex-vis/
├── subcortex_vis/              # 主 Python 包
│   ├── __init__.py
│   ├── mesh_viz.py             # 核心网格提取与可视化函数
│   └── gui/                    # GUI 子包
│       ├── __init__.py         # 导出 MeshGui, main 等
│       ├── __main__.py         # 支持 python -m subcortex_vis.gui
│       ├── constants.py        # 颜色调色板、colormap 列表、默认参数
│       ├── delegates.py        # Qt 自定义委托（颜色方块显示）
│       ├── renderer.py         # PyVista 渲染逻辑封装
│       ├── main_window.py      # 主窗口 MeshGui 类
│       └── widgets/            # 可复用 UI 组件
│           ├── __init__.py
│           ├── file_loader.py      # 文件加载面板
│           ├── label_list.py       # 标签列表面板
│           ├── colormap_panel.py   # ROI 值与 colormap 面板
│           └── render_params.py    # 渲染参数面板
├── scripts/
│   ├── gui_app.py              # GUI 启动入口
│   └── demo_mesh.py            # 命令行 demo 脚本
├── atlas/                      # 模板文件
├── data/                       # 示例数据
└── Tian2020MSA/                # Tian 子皮层图谱
```

## 快速使用

### 命令行模式
基于现有的 Tian 子皮层模板做一次左视角截图：
```bash
python -m subcortex_vis.mesh_viz \
  --input atlas/Tian_Subcortex_S2_3T.nii.gz \
  --label 1 \
  --sigma 0.8 \
  --smooth-iter 30 \
  --view left \
  --screenshot plots/demo_mesh.png
```

参数说明：
- `--label`：只提取某个标签（默认用掩膜并在 0.5 处取等值面）。如果不传，用 `--threshold` 直接对灰度取等值面。
- `--sigma`：marching cubes 前的高斯平滑。
- `--smooth-iter`/`--smooth-relax`：网格平滑参数。
- `--view`：`iso|left|right|top|front` 预设视角。
- `--screenshot`：提供路径时关闭窗口、离屏渲染并保存截图；不提供则打开交互窗口。

### 作为函数调用
```python
from subcortex_vis.mesh_viz import load_nii_volume, extract_isosurface, visualize_mesh

volume, spacing, origin = load_nii_volume("atlas/Tian_Subcortex_S2_3T.nii.gz")
mask = (volume == 1).astype(float)
mesh = extract_isosurface(mask, spacing, origin, threshold=0.5, sigma=0.8, smooth_iter=30)
visualize_mesh(mesh, view="left", background="white")
```

## GUI 图形界面

支持载入 NIfTI、自动列出非 0 标签、选择/全选多 ROI、自定义颜色、导入 ROI 数值并应用 colormap、调节平滑参数、切换视角、截图保存。

### 启动方式

```bash
# 方式一：通过脚本启动
python scripts/gui_app.py

# 方式二：作为模块启动
python -m subcortex_vis.gui
```

### 界面功能

| 功能区 | 说明 |
|--------|------|
| **文件加载** | 选择 `.nii/.nii.gz` 文件，点击 "Load NIfTI" 自动读取并列出标签 |
| **标签列表** | 多选或全选 ROI，点击 "Set color" 自定义颜色 |
| **ROI 值 & Colormap** | 导入 CSV 文件为每个 ROI 赋值，启用 colormap 自动着色 |
| **渲染参数** | 调整 Sigma、Smooth iter、显示边缘、2D/3D 风格 |
| **视角控制** | left/right/top/front/iso 预设视角 |
| **导出** | Reset view 重置视角，Save screenshot 保存 PNG |

### ROI 值文件格式

支持 CSV 或 TXT 格式，包含两列：标签和数值。自动识别常见列名：

```csv
label,value
1,0.523
2,0.187
3,0.891
...
```

### 代码中使用 GUI 组件

```python
from subcortex_vis.gui import MeshGui, PALETTE, COLORMAPS
from subcortex_vis.gui.renderer import MeshRenderer
from subcortex_vis.gui.widgets import LabelListPanel, ColormapPanel

# 创建主窗口
gui = MeshGui()
gui.show()
```

## 许可证

Tian 图谱许可证见 [Tian2020MSA/license.txt](Tian2020MSA/license.txt)。
