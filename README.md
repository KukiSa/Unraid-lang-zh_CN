# Unraid 简体中文语言包 · 独立译本

[![校验](https://github.com/KukiSa/Unraid-lang-zh_CN/actions/workflows/ci.yml/badge.svg)](https://github.com/KukiSa/Unraid-lang-zh_CN/actions/workflows/ci.yml)
[![发布](https://github.com/KukiSa/Unraid-lang-zh_CN/actions/workflows/release.yml/badge.svg)](https://github.com/KukiSa/Unraid-lang-zh_CN/releases/latest)

从 [Unraid 官方英文源](https://github.com/unraid/lang-en_US)独立翻译，覆盖 **51 个文件、5,183 条单行记录、633 个多行帮助区块**，未复用现有中文翻译仓库。

专业或易歧义术语采用「阵列 (Array)」「存储池 (Pool)」等中英对照。一般文字使用「」，纯西文括注使用半角括号并与相邻正文留空格；VoIP 保留原文。代码、命令、路径和配置语法保持原样。

## 安装与更新

打开 Unraid **Tools → Language**（工具 → WebGUI → 语言），在用户视图的 XML 地址栏填写：

```text
https://github.com/KukiSa/Unraid-lang-zh_CN/releases/latest/download/lang-zh_CN.xml
```

点击 **Install**，然后前往 **Settings → Display Settings → Language**，选择 **中文 (Chinese)**，即 `zh_CN`，应用并刷新页面。后续使用 Unraid 的语言包更新机制。

固定地址读取最新正式版 XML；XML 内的 ZIP 地址绑定具体版本，避免版本号和文件错配。

### 离线安装及旧版迁移

从 [Releases](https://github.com/KukiSa/Unraid-lang-zh_CN/releases/latest) 下载 `unraid-zh_CN-offline-版本号.zip`，解压到服务器的独立目录，例如 `/boot/unraid-zh-cn-independent/`，以 root 用户执行：

```bash
bash /boot/unraid-zh-cn-independent/install-offline.sh
```

安装时无需联网。脚本检查校验和、备份当前中文包，再调用原生语言管理器。以后联网时仍可检查更新。脚本会输出备份路径和完整恢复命令。

之前使用无更新源的离线版时，建议通过此脚本迁移；它会替换旧缓存 ZIP。仅重复安装 XML 可能复用 Unraid 已缓存的旧 ZIP。

`zh_CN.zip` 也可在 **Developer** 视图上传，手动选择 `zh_CN`。这是临时开发测试方式，重启后可能失效。

本译本与官方中文包使用相同语言代码，再次安装官方包会替换本译本。

## 修改与校验

**直接编辑根目录及插件目录的 `.txt` 文件**。单行条目只改 `=` 右侧；多行帮助只改标签之间的正文。保留英文键、标签、占位符、HTML/PHP、代码和链接目标。请遵循[术语表](docs/GLOSSARY.zh-CN.md)。

需要 Python 3.9+、PHP 8.3+（Zip、SimpleXML）、Node.js 和 Bash：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/build.py
php tests/runtime.php
node --check build/translate.zh_CN.js
node tests/javascript.cjs
bash -n install-offline.sh restore-language.sh
```

校验结果保存在 `build/`，发布附件保存在 `dist/`。构建不下载译文或其他语言包。

## 跟进英文源

每天 **10:23（北京时间）**检查上游，也可在 Actions 手动运行 **Check English upstream**。有待翻译内容时，任务会失败，在摘要和附件中列出差异；不会自动替换已审阅的译文。

```bash
python3 tools/upstream.py           # 只检查
python3 tools/upstream.py --apply   # 工作区干净时显式同步
```

同步按英文键和帮助标签匹配：保留已有译文；新增条目留空并标记 `; TODO`；英文正文变化时保留译文并标记待审阅。全部处理后才能通过校验。英文快照和提交记录位于 `upstream/en_US/`、`source.lock.json`。

## 发布

1. 修改译文并完成校验。
2. 更新 `VERSION`，采用 `YYYY.MM.DD.NN`，例如 `2026.10.30.02`。序号固定两位，适配 Unraid 的字符串版本比较。
3. 更新 `RELEASE-NOTES.md`，执行 `python3 tools/build.py --write-metadata`，将版本和 XML 一起提交到 `main`。
4. 打标签并推送：

   ```bash
   git tag -a v2026.10.30.02 -m 'Release 2026.10.30.02'
   git push origin main v2026.10.30.02
   ```

Actions 会先在 PHP 8.3、8.5 中验证，再创建草稿 Release、上传全部附件，最后发布为最新版。同标签的已有发布不会被自动覆盖。

## 实际边界

已使用官方原样 PHP 解析函数和 ZIP 安装函数，在临时目录验证加载、逐字节解包及缓存清除；也校验了键、标签、UTF-8/LF、占位符和受保护语法。

**未实机验证**页面宽度、插件显示和重启恢复。官方 JavaScript 的 Yes/No 保留键存在归一化问题：105 个唯一键中，103 个查词通过，另外 2 个可能显示英文。该限制明确纳入测试，不通过注入脚本或修改 WebGUI 绕过。

英文源缺少或插件未接入多语言的文案也可能保留英文。

## 来源、署名及许可

本仓库保留官方英文仓库完整 Git 历史，在其上提交独立译文；GitHub 层面为独立仓库。没有合并或读取中文翻译仓库。

- 译文作者：**gpt-6.1-sol <noreply@openai.com>**
- 共同作者及维护者：**iks <i@iks.moe>**
- 英文源及原程序的作者、贡献者和版权记录保留在 Git 历史及 [LICENSE.txt](LICENSE.txt) 中。

采用 **GPL-2.0**，非官方译本，不表示 Unraid 官方背书。另见[翻译说明](docs/TRANSLATION-NOTES.zh-CN.md)、[文件清单](docs/CONTENTS.zh-CN.md)。

语境依据：[共享](https://docs.unraid.net/unraid-os/using-unraid-to/manage-storage/shares/)、[阵列](https://docs.unraid.net/unraid-os/using-unraid-to/manage-storage/array/overview/)、[存储池](https://docs.unraid.net/unraid-os/using-unraid-to/manage-storage/cache-pools/)、[多语言支持](https://docs.unraid.net/unraid-os/using-unraid-to/customize-your-experience/multi-language-support/)及 [Docker IPvlan](https://docs.docker.com/engine/network/drivers/ipvlan/)。
