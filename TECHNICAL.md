# A7R6 创意外观逆向 —— 结果说明

对索尼 Imaging Edge Edit（IEDT）4.1.01.06121（Windows x64）做静态逆向 + 数据解析，为索尼 A7R VI（ILCE-7RM6）生成 12 种「创意外观」（Creative Look）的 Adobe Camera Raw / Lightroom 配置。

生成方式与 [751K/sony-a7m5-looks](https://github.com/751K/sony-a7m5-looks) 同源，全部由外观链直接求值，不经过任何经验拟合。

---

## 1. 数据来源

### 1.1 外观参数（来自 ARW）

创意外观的参数不写死在程序里，而是**由相机写入每张 ARW 的加密 SR2 数据**。使用 dcraw 同款解密算法解析 `SR2SubIFD`：

- `0x74c0`：外观 IFD 偏移列表；
- 每个 IFD 的 `0x7770`：外观名；
- 关键标签：
  - `0x780f`（276 字节）：LinearMatrix16 构建数据（色相节点、矩阵组、二次项）；
  - `0x7805` / `0x7806`：MainGamma 的 X / Y 节点（14 位域，X 以 128 为步长）；
  - `0x780c` / `0x780d` / `0x780e`：YGamma 拐点、斜率与增益表；
  - `0x7842`–`0x7846`：YCC 分象限的剪切/增益参数；
  - `0x7801`：亮度系数，`0x74c5`：Sepia 色调。

A7R6 的 ARW 内共 12 组：`Standard / Vivid / Neutral / Portrait / FL / VV2 / IN / SH / BW / Sepia / FL2 / FL3`。

### 1.2 常数表（来自 Edit.exe）

程序内两张全局表，按数值特征在 `Edit.exe`（PE32+，ImageBase `0x140000000`）中定位：

| 表 | 内容 | 文件偏移 | VA |
|---|---|---|---|
| atan | `float32[512]`，色相角 0–128（1/8 圈） | `0x46E598` | `0x14046F798` |
| contrast family | `int32[37][1025]`，对比度曲线族，第 18 行为恒等曲线 | `0x48C200` | `0x14048D400` |

对比度曲线族的定位依据：第 18 行严格等于 `min(64·i, 65535)`（i = 0…1024），全文件唯一命中。

### 1.3 目标软件的输入编码 E

ACR 交给配置文件的不是线性相机 RGB，而是经其内部编码后的值。E 采用参考项目在合成色卡上标定的模型（`acr_encoding.json`）：

- 中间调线性，`x ≈ l / 6422`；
- 高光肩部压缩，暗部轻微趾部；
- 色相保持：最大/最小通道走同一条 1D 曲线，中间通道保持比例。

配置表最终写入 `f ∘ E⁻¹`，ACR 先施加 E 再查表，复合后得到外观链输出。

---

## 2. 外观链结构

逐像素阶段，顺序固定：

```
相机线性 RGB (0..16383)
  1. LinearMatrix16   色相索引 1024×18 表；3×3 矩阵 + 二次项 + 死区
  2. MainGamma        逐通道 LUT（由 0x7805/0x7806 节点插值），可选叠加对比度曲线族
  3. RGB2YCC          BT.601 亮度/色差（Y = (109R+366G+37B)/512）
  4. YCC 分象限处理    剪切/增益（色相、饱和度）
  5. ChromaSuppress   极暗/极亮降色度
  6. AreaComp         中性附近微调
  7. YGamma           亮度曲线（含褪色 Fade 的暗部抬升）
  8. YCC2RGB          逆 BT.601
  9. Effect           仅 BW / Sepia：单色化 + 棕褐着色
```

另含解码器阶段的 SCCS（亮而饱和的颜色向亮度收拢），参考实现生成配置时默认包含，本项目同样包含。

不纳入配置的部分：去马赛克、降噪、锐化、DRO、镜头校正、周边光量——它们依赖邻域或空间位置，不是逐像素映射。

---

## 3. 生成的配置文件

### 3.1 底座：`SonyA7R6 Linear Base.dcp`

| 字段 | 取值 | 作用 |
|---|---|---|
| UniqueCameraModel | Sony ILCE-7RM6 | 限制机型 |
| ColorMatrix1/2 | 取自 Adobe Standard A7R6 | 白平衡行为与 Adobe 一致 |
| ForwardMatrix1/2 | 线性 ProPhoto → XYZ D50 | 使 ACR 工作空间 = 白平衡后的相机 RGB |
| ProfileToneCurve | `(0,0) (1,1)` | 不叠加 Adobe 影调 |
| DefaultBlackRender | none | 不做黑场渲染 |

### 3.2 外观：`A7R6 <代号>.xmp`

- `crs:PresetType="Look"`，`crs:CameraProfile="SonyA7R6 Linear Base"`；
- `crs:RGBTable` + `crs:Table_<MD5>`：ACR 原生 3D 表（base85 + zlib 私有编码）；
- 表规格：**64³**，ProPhoto 原色，gamma 1.8，u16 差值编码（与恒等表相减）；
- 表值 = `f_look(E⁻¹(v))` 转 ProPhoto gamma 1.8。

> 注意：这不是早些时候被 ACR 静默忽略的 `crs:LookTable` 写法——`LookTable` 只接受 DNG 的 hue/sat CSV 格式；RGBTable 才是 ACR 执行 3D LUT 的通道。

---

## 4. 精度验证

同一批 ARW，分别用本配置（LR 导出 JPEG）与 IEDT（16bit TIFF）导出，几何对齐后 8 倍降采样比较（sRGB / D50，500px 长边）：

| 场景 | ΔE76 | ΔE00 | 备注 |
|---|---|---|---|
| DSC00697（湖景） | 0.98 | 0.75 | 参与黑位标定 |
| DSC00737（林地） | 0.98 | 0.79 | 参与白平衡折中标定 |
| DSC00642（纪实） | 1.15 | 1.00 | **留出验证，未参与标定** |

在外观链之外，生成时还烘焙了一组**共享校准**（`calib.json`）：

- 黑位/增益：R ×0.9986 / G ×0.9963 / B ×0.9987，偏移 −0.011 左右 —— 修正 ACR 与 IEDT 的黑位与整体亮度差；
- 白平衡折中：R ×1.002 / G ×0.994 / B ×0.990 —— 修正两家对 "As Shot" 白平衡解释的差异。

这两项与具体外观无关，因此 12 张表共用同一组系数。校准后 ΔL 已归零（±0.2），残差主要是色度，且集中在绿调密集场景（中间调 Δa 约 −0.2），来自两家去马赛克与色度处理差异，配置文件无法进一步修正。

其余 10 种外观走完全相同的代码与参数来源，但**尚无 IEDT 成片对照**（与参考项目的处境一致），仅通过结构校验：
- BW 表三通道差值恒为 0（严格单色）；
- Sepia 中灰 R>G>B 且偏色量 0.11（棕褐）；
- 其余外观在灰轴上中性、通道最大差约 0.6（高饱和色域正常）。

---

## 5. 安装

1. 退出 Photoshop / Lightroom；
2. 复制 `SonyA7R6 Linear Base.dcp` → `%APPDATA%\Adobe\CameraRaw\CameraProfiles\`（用户级目录，不存在请新建；勿用 `C:\ProgramData\...` 系统级路径——需管理员权限且部分环境不扫描）
3. 复制 `A7R6 *.xmp` → `%APPDATA%\Adobe\CameraRaw\Settings\`
4. 重启，配置文件浏览器出现 **Sony A7R6** 组，选择 `A7R6 ST` 等即可。

注意：本组配置只对 ILCE-7RM6 的 RAW 显示（其他机型看不到属正常）；仅支持 Lightroom Classic / Photoshop ACR（云版 Lightroom 桌面版不读本地配置）；需要 LR Classic 9.3+ / ACR 12.3+。

使用时：白平衡保持原照；配置文件自带完整影调，无需再套其它预设。

---

## 6. 已知局限

- **DRO / 大光比**：空间自适应处理，不在逐像素链内，配置不包含；
- **锐化 / 降噪 / 清晰度**：同属空间处理，各软件自行实现，非配置文件职责；
- **褪色默认值**：按相机默认（FL2/FL3 = 1、IN = 3、SH = 6）生成；ACR 侧不能再调 Fade；
- **机型绑定**：参数取自 A7R6 的 ARW，其他机型请勿直接使用；
- **E 模型**：沿用参考项目在 ACR 上的标定，若 Adobe 更改管线，需重新标定。

---

## 7. 合规说明

- 参考项目 751K/sony-a7m5-looks 为 MIT 许可，本项目的代码改造与其同源；
- 配置文件由用户本机安装的软件读取常数、由用户自己的 RAW 提供参数生成，仓库/交付物不包含索尼的二进制或反编译代码；
- 与 Sony、Adobe 均无关联，相关商标归各自所有者；仅供个人学习研究，禁止商用。
