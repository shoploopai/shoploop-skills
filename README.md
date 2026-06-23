# Shoploop AI — Codex 视频技能 / Video Skills for Codex

让 Codex 用一句话帮你生成**无水印视频**(文生视频 / 图生视频 / 首尾帧 / 多参考 / 视频参考)。
Make no-watermark videos in Codex with one sentence.

下面任选一种方式安装。On Windows, replace `python3` with `python` or `py -3`.

---

## 最省事:一键安装 / One-liner

在你的项目目录里运行 / Run in your project dir:

**mac / Linux**
```bash
curl -fsSL https://raw.githubusercontent.com/shoploopai/shoploop-skills/main/install.sh | sh
```
**Windows(PowerShell)**
```powershell
irm https://raw.githubusercontent.com/shoploopai/shoploop-skills/main/install.ps1 | iex
```

它会自动用 npx 装好技能、生成 `.env.shoploop`,并写一份 `AGENTS.md` 简报——这样**新的 Codex 一开会话就知道**怎么用本项目出片。装完把 key 填进 `.env.shoploop`,新开一个 Codex 会话即可(用法见第 4 步)。
It auto-installs the skills via npx, scaffolds `.env.shoploop`, and writes an `AGENTS.md` brief so a fresh Codex session immediately knows how to make videos. (Prefer doing it by hand? Copy `AGENTS.example.md` to `AGENTS.md`.)

> 访问 GitHub 不便?用我们给的 **`shoploop-installer.zip`**:解压后 mac 运行 `sh install.sh`、Windows 运行 `install.ps1`,效果一样。

想自己一步步来,看下面的**手动 4 步**(同样有效):

---

## 准备一下 / Before you start

1. 已安装 **Codex CLI**(能在终端运行 `codex`)。
2. 已安装 **Node.js**。终端运行 `node -v` 能看到版本号即可(没有就去 https://nodejs.org 装)。
3. 有一把 **Shoploop key**(形如 `sk-...`,由我们提供)。

---

## 第 1 步:安装技能 / Install

在你的项目目录打开终端,运行:

```bash
npx skills add shoploopai/shoploop-skills --all
```

> 想让所有项目都能用,就加 `-g` 全局安装:`npx skills add shoploopai/shoploop-skills --all -g`

你会看到类似 `Installed 2 skills` 和最后一行 `Done!`,技能就装进了 `.agents/skills/`。

## 第 2 步:填入你的 Key / Add your key

在项目根目录建一个文件 `.env.shoploop`,内容:

```bash
SHOPLOOP_KEY=sk-换成你的key
```

(可选,通常不用改)`SHOPLOOP_BASE=https://seedance.shoploopai.com` 和 `SHOPLOOP_MODEL=seedance2.0` 已是默认值。
**不要把这个文件发给别人、也不要提交到 git。**

## 第 3 步:重开 Codex / Restart Codex

关掉当前 Codex,**重新打开一个会话**(新装的技能要新会话才会加载)。
输入 `/skills`,应能看到 `shoploop-video`。看到了就说明装好了。

## 第 4 步:开始出片 / Make a video

直接用中文/英文对 Codex 说你想要什么,例如:

- `帮我做一个 9:16 的产品展示视频,5 秒,电影感,存到 shoploop_outputs/demo.mp4`
- `把这张图片做成会动的视频，缓慢推进镜头`(把图片路径告诉它)
- `Make a 16:9 cinematic sunrise over the ocean, 8 seconds`

Codex 会自动选用 `shoploop-video` 技能(也可以手动打 `$shoploop-video`)。
**生成通常要几分钟**,完成后会给你视频地址 / 下载到的本地文件路径。

---

## 常见问题 / Troubleshooting

- **报 `HTTP 401`** → key 没填对。检查 `.env.shoploop` 在项目根、`SHOPLOOP_KEY` 正确。
- **`/skills` 里看不到技能** → 没重开会话。关掉 Codex 再开一个新会话。
- **`npx` 提示找不到命令** → 先装 Node.js(`node -v` 能用即可)。
- **时长** → 支持 4–15 秒。
- **更新到最新技能** → 运行 `npx skills update`。

需要帮助随时联系我们。
