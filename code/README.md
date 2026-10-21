# A7R6 Looks —— 生成代码（ACR 侧）

本目录只包含**把外观接进 Camera Raw** 这一层：DCP 容器、XMP 表编码、64³ 表组装、以及从 Edit.exe 读常数表的接口。

**索尼外观链本身的实现不在本仓库分发**——它对每个外观只做"参数 → 渲染"这一步，属于上游项目的工作，见 [751K/sony-a7m5-looks](https://github.com/751K/sony-a7m5-looks)（MIT）。

## 目录

| 文件 | 作用 | 来源 |
|---|---|---|
| `acr/acr_a7r6.py` | 主程序：写 DCP、写 XMP、组装 64³ 表 | 本项目（MIT） |
| `acr/dcp.py` | DCP 读写（IIRC TIFF 容器、DNG profile tag） | 751K 原码（MIT） |
| `acr/crs_table.py` | XMP 表编码：base85 + zlib + MD5 指纹 | 751K 原码（MIT） |
| `acr/acr_encoding.py` | ACR 输入编码 E 及其逆 | 751K 原码（MIT） |
| `acr/acr_encoding.json` | E 的实测常数 | 751K 原码（MIT） |
| `acr/calib.json` | 本项目实测的黑位/白平衡标定 | 本项目（MIT） |
| `edit_binary.py` | 从用户本机安装的 Edit.exe 按偏移读常数表 | 751K 的 Windows 改编版（MIT） |
| `README.md` | 本文件 | — |

## 要跑起来：补齐上游

本目录**不能单独运行**——`acr_a7r6.py` 还会 import 外观链模块。补法：

```bash
git clone https://github.com/751K/sony-a7m5-looks.git
cp sony-a7m5-looks/sonylook/*.py  <本目录>/
```

然后：

```bash
python acr/acr_a7r6.py all                 # 全部 12 个外观（默认 64³）
python acr/acr_a7r6.py st --grid 64 --out out
```

> 层级不能动：`acr_a7r6.py` 用 `HERE = acr/`、`ROOT = 本目录/` 铺 `sys.path`，把上游模块放进子目录会 import 失败。

### 运行前提

| 依赖 | 说明 |
|---|---|
| Python 3 + `numpy` | 生成表只需要这两个 |
| 一张 A7R6 的 ARW | 脚本内常量 `ARW = r"D:\索尼\raw\2026年国庆北疆\DSC01352.ARW"`，换成任意一张即可（外观参数从 ARW 的加密 SR2 块读取，该读取器在上游 `sr2.py`） |
| 已安装的 Imaging Edge Edit | 常数表按文件偏移从 `Edit.exe` 读取，默认 `A:\Apps\SonyIE\Edit.exe`，可用环境变量 `SONY_EDIT_BINARY` 覆盖 |
| `acr/calib.json` | 黑位/白平衡标定，**缺了输出会偏**，不可删 |

## 可复现性

用「本目录 + 上游 sonylook/」完整跑过 `acr_a7r6.py st --grid 64`，与 `../profiles/` 的发布件比对：

| 产物 | 结果 |
|---|---|
| `A7R6 ST.xmp` | **逐字节一致**（SHA-256 `640210ab…`，表载荷 MD5 `D4A8C2763EB556F66392233F15FE663F`） |
| `SonyA7R6 Linear Base.dcp` | **逐字节一致**（536 字节） |

也就是说：代码 + `calib.json` + 一张 ARW + 对应版本 Edit.exe = 发布件本身。

## 实现要点

### 1. 外观 XMP 的结构

```
crs:PresetType="Look"
crs:CameraModelRestriction="Sony ILCE-7RM6"      ← 机型隔离
crs:CameraProfile="SonyA7R6 Linear Base"         ← 按名字引用底座 DCP
crs:RGBTable="<32 位 MD5>"
crs:Table_<MD5>="<base85 载荷>"                   ← 表体在这里，占文件 99.9%
crs:Name / crs:Group = "A7R6 ST" / "Sony A7R6"
crs:Version="13.0"  crs:ProcessVersion="11.0"
```

### 2. 表载荷编码（`crs_table.py`）

```
base85(Adobe 字母表，小端 4 字节→5 字符)  ∘  [u32 原长][zlib 流]
MD5 取「解压后数据」的大写十六进制 —— 即 crs:RGBTable 里的那个名字
```

### 3. RGBTable 二进制（`table_bytes()`）

```
u32 1, u32 1, u32 3, u32 n          ← 16 字节头（n = 网格边长）
n³ × (R,G,B) uint16                 ← 存「值 − 恒等值」，按 mod 65536 回绕
u32 原色=2(ProPhoto), u32 gamma=2(γ1.8), u32 gamut=0
f64 最小强度=0.0, f64 最大强度=1.0
```

节点顺序 R 最慢、B 最快；恒等值 = `round(i·65535/(n−1))`。

### 4. 底座 DCP（`write_base()`）

12 个 tag，全部内联、无外部引用：

| tag | 来源 |
|---|---|
| `ColorMatrix1/2`、`CalibrationIlluminant1/2` | 读官方 `Sony ILCE-7RM6 Adobe Standard.dcp` 后固化 |
| `ForwardMatrix1/2` | **固定为线性 ProPhoto → XYZ D50**（工作空间 = 白平衡后的相机 RGB） |
| `ProfileToneCurve` | 恒等 `[0,0,1,1]` |
| `DefaultBlackRender` | 1（不做暗部渲染） |
| `ProfileName` / `UniqueCameraModel` / `ProfileCopyright` / `ProfileEmbedPolicy` | 命名与元信息 |

**不含** `ProfileHueSatMap`、`ProfileLookTable`、`RGBTables(0xCD3F)`——底座不带任何风格，也因此不受 Adobe「忽略 DCP 内嵌 RGBTables」缺陷影响。

## 许可

- `code/**` 采用 **MIT**（全文见仓库根 `LICENSE`）；
- `profiles/**` 与文档采用 **CC BY-NC 4.0**，禁止商业使用；
- 上游代码为 751K 的 MIT 实现，版权与来源见仓库根 [`THIRD-PARTY.md`](../THIRD-PARTY.md)；
- 本仓库不包含 Sony / Adobe 的任何二进制或数据文件；`Edit.exe` 由用户在本地自行安装。
