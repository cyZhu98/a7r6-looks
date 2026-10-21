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

## 未包含的内容

本仓库**不包含**任何 Sony 或 Adobe 的二进制程序、安装包，也不包含从这些程序中提取的常数表数据文件。

`code/edit_binary.py` 在运行时读取的是用户**自行合法安装**的 Imaging Edge Edit 中的常数表；这些数据不随本仓库分发。

## 商标

Sony、Alpha、Imaging Edge、Creative Look，以及本项目涉及的外观代号（ST / VV / NT / PT / FL / IN / SH / BW / SE 等）为 Sony Group Corporation 的商标或产品名称；
Adobe、Lightroom、Camera Raw、DNG 为 Adobe Inc. 的商标。

本项目与上述公司**无任何隶属、授权或背书关系**。所有商标归各自权利人所有。
