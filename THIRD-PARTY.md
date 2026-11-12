# 第三方代码与商标声明

## 751K/sony-a7m5-looks（MIT）

`code/acr/` 下以下文件**逐字节**来自上游仓库，仅新增了版权头注释：

| 本仓库 | 上游路径 |
|---|---|
| `code/acr/crs_table.py` | `camera_raw/crs_table.py` |
| `code/acr/dcp.py` | `camera_raw/dcp.py` |
| `code/acr/acr_encoding.py` | `camera_raw/acr_encoding.py` |
| `code/acr/acr_encoding.json` | `camera_raw/acr_encoding.json` |

`code/edit_binary.py` 是上游 `sonylook/edit_binary.py` 的 Windows 改编版。

上游版权与许可：

```
Copyright (c) 2026 sony-a7m5-looks contributors
Licensed under the MIT License
https://github.com/751K/sony-a7m5-looks/blob/main/LICENSE
```

## Classic Chrome 外观参考

`profiles/A7R6 Fuji Classic Chrome.xmp` 改编自 Aaron Buchler（abpy）的 PROVIA 和 Classic Chrome sRGB LUT。源表来自其 Fujifilm Camera Matching 重建，锁定在提交 `b5a1f16abfb2759b337c83d69d9dc49470e7e518`。 [源项目与许可声明](https://github.com/abpy/FujifilmCameraProfiles/tree/b5a1f16abfb2759b337c83d69d9dc49470e7e518)

本项目对 PROVIA 求三维逆变换，将 Classic Chrome 相对 PROVIA 的色彩和影调变化应用到 Sony ST，并转换为 Adobe XMP 色表格式。该 XMP 按 **CC BY-NC-SA 4.0** 提供，署名须保留 Aaron Buchler（abpy）及其项目来源。 [许可全文](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode)

## 未包含的内容

本仓库**不包含**任何 Sony 或 Adobe 的二进制程序、安装包，也不包含从这些程序中提取的常数表数据文件。

`code/edit_binary.py` 在运行时读取的是用户**自行合法安装**的 Imaging Edge Edit 中的常数表；这些数据不随本仓库分发。

## 商标

Sony、Alpha、Imaging Edge、Creative Look，以及本项目涉及的外观代号（ST / VV / NT / PT / FL / IN / SH / BW / SE 等）为 Sony Group Corporation 的商标或产品名称；
Adobe、Lightroom、Camera Raw、DNG 为 Adobe Inc. 的商标。

本项目与上述公司**无任何隶属、授权或背书关系**。所有商标归各自权利人所有。
